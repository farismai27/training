#!/usr/bin/env python3
"""
Claude Computer Use Client

Enables Claude to control a computer via screenshots and actions.
Based on Anthropic's Computer Use reference implementation.
"""

import os
import base64
import json
import time
from io import BytesIO
from typing import Dict, List, Any
from anthropic import Anthropic
from PIL import Image
import pyautogui


class ComputerUseClient:
    """Client for Claude Computer Use functionality."""

    def __init__(self, api_key: str = None):
        """Initialize the Computer Use client."""
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history = []

        # Enable PyAutoGUI fail-safe (move mouse to corner to abort)
        pyautogui.FAILSAFE = True

    def take_screenshot(self) -> str:
        """Take a screenshot and return as base64."""
        screenshot = pyautogui.screenshot()

        # Convert to base64
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return img_str

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a computer action.

        Supported actions:
        - mouse_move: Move mouse to coordinates
        - click: Click at coordinates
        - type: Type text
        - key: Press a key
        - scroll: Scroll in direction
        - screenshot: Take screenshot
        """
        action_type = action.get('type')

        try:
            if action_type == 'mouse_move':
                x, y = action.get('x'), action.get('y')
                pyautogui.moveTo(x, y, duration=0.2)
                return {'success': True, 'action': 'mouse_move', 'x': x, 'y': y}

            elif action_type == 'click':
                x, y = action.get('x'), action.get('y')
                button = action.get('button', 'left')
                pyautogui.click(x, y, button=button)
                return {'success': True, 'action': 'click', 'x': x, 'y': y}

            elif action_type == 'double_click':
                x, y = action.get('x'), action.get('y')
                pyautogui.doubleClick(x, y)
                return {'success': True, 'action': 'double_click', 'x': x, 'y': y}

            elif action_type == 'type':
                text = action.get('text', '')
                pyautogui.write(text, interval=0.05)
                return {'success': True, 'action': 'type', 'text': text}

            elif action_type == 'key':
                key = action.get('key')
                pyautogui.press(key)
                return {'success': True, 'action': 'key', 'key': key}

            elif action_type == 'hotkey':
                keys = action.get('keys', [])
                pyautogui.hotkey(*keys)
                return {'success': True, 'action': 'hotkey', 'keys': keys}

            elif action_type == 'scroll':
                amount = action.get('amount', 0)
                pyautogui.scroll(amount)
                return {'success': True, 'action': 'scroll', 'amount': amount}

            elif action_type == 'screenshot':
                screenshot = self.take_screenshot()
                return {'success': True, 'action': 'screenshot', 'image': screenshot}

            elif action_type == 'wait':
                duration = action.get('duration', 1.0)
                time.sleep(duration)
                return {'success': True, 'action': 'wait', 'duration': duration}

            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'action': action_type}

    def send_message(self, message: str, include_screenshot: bool = True) -> str:
        """
        Send a message to Claude with optional screenshot.

        Args:
            message: The message/instruction for Claude
            include_screenshot: Whether to include current screenshot

        Returns:
            Claude's response text
        """
        # Build message content
        content = []

        if include_screenshot:
            screenshot_b64 = self.take_screenshot()
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": screenshot_b64
                }
            })

        content.append({
            "type": "text",
            "text": message
        })

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": content
        })

        # Get response from Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=self.conversation_history,
            tools=[
                {
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": 1920,
                    "display_height_px": 1080,
                    "display_number": 1
                }
            ]
        )

        # Process response
        assistant_message = {
            "role": "assistant",
            "content": []
        }

        response_text = ""

        for block in response.content:
            if block.type == "text":
                response_text += block.text
                assistant_message["content"].append({
                    "type": "text",
                    "text": block.text
                })

            elif block.type == "tool_use":
                # Execute the computer action
                action_result = self.execute_action(block.input)

                assistant_message["content"].append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

                # Add tool result to conversation
                self.conversation_history.append(assistant_message)
                self.conversation_history.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(action_result)
                    }]
                })

                # Get next response after tool use
                return self.send_message("", include_screenshot=True)

        # Add assistant response to history
        self.conversation_history.append(assistant_message)

        return response_text

    def run_task(self, task: str, max_iterations: int = 20) -> List[str]:
        """
        Run a complete task with Claude Computer Use.

        Args:
            task: The task description
            max_iterations: Maximum number of interaction loops

        Returns:
            List of responses from Claude
        """
        print(f"🤖 Starting task: {task}\n")

        responses = []
        iteration = 0

        # Send initial task
        response = self.send_message(task)
        responses.append(response)
        print(f"Claude: {response}\n")

        # Continue interaction until task complete or max iterations
        while iteration < max_iterations:
            iteration += 1

            # Check if Claude indicates completion
            if any(phrase in response.lower() for phrase in [
                'task complete', 'finished', 'done', 'all tests', 'report:'
            ]):
                print("✅ Task completed!")
                break

            # Small delay between actions
            time.sleep(0.5)

            # Get next action from Claude
            response = self.send_message("Continue with the next step", include_screenshot=True)

            if response:
                responses.append(response)
                print(f"Claude (iteration {iteration}): {response}\n")

        return responses

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def main():
    """Example usage of Computer Use client."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python computer_use_client.py '<task description>'")
        print("\nExample:")
        print("python computer_use_client.py 'Open Chrome and navigate to google.com'")
        sys.exit(1)

    task = sys.argv[1]

    # Initialize client
    client = ComputerUseClient()

    # Run task
    responses = client.run_task(task, max_iterations=10)

    # Print summary
    print("\n" + "="*60)
    print(f"Task: {task}")
    print(f"Total responses: {len(responses)}")
    print("="*60)


if __name__ == "__main__":
    main()
