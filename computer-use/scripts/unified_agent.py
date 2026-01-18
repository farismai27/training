#!/usr/bin/env python3
"""
Unified Multi-Purpose Agent

Combines all agent capabilities into one comprehensive system:
- QA Testing & Automation (Computer Use)
- Production Error Monitoring & Auto-Fix
- Document Conversion
- Test Report Generation
- Issue Tracking & Management

This agent can work autonomously or interactively.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from anthropic import Anthropic
import base64
from io import BytesIO

# Try to import optional dependencies
try:
    from PIL import Image
    import pyautogui
    COMPUTER_USE_AVAILABLE = True
except ImportError:
    COMPUTER_USE_AVAILABLE = False
    print("⚠️  Computer Use features unavailable (install pillow and pyautogui)")

try:
    import pdfplumber
    from docx import Document as DocxDocument
    DOCUMENT_CONVERSION_AVAILABLE = True
except ImportError:
    DOCUMENT_CONVERSION_AVAILABLE = False
    print("⚠️  Document conversion unavailable (install pdfplumber and python-docx)")


class UnifiedAgent:
    """
    Unified AI Agent with multiple capabilities:
    - Computer control and automation
    - QA testing
    - Error monitoring and fixing
    - Document processing
    """

    def __init__(self, api_key: str = None, project_root: Path = None):
        """Initialize the unified agent."""
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=self.api_key)
        self.project_root = project_root or Path.cwd()
        self.conversation_history = []
        self.results_dir = self.project_root / "results"
        self.results_dir.mkdir(exist_ok=True)

        # Enable PyAutoGUI fail-safe if available
        if COMPUTER_USE_AVAILABLE:
            pyautogui.FAILSAFE = True

        print("✅ Unified Agent initialized")
        print(f"   Project root: {self.project_root}")
        print(f"   Computer Use: {'Enabled' if COMPUTER_USE_AVAILABLE else 'Disabled'}")
        print(f"   Document Conversion: {'Enabled' if DOCUMENT_CONVERSION_AVAILABLE else 'Disabled'}")

    # ========================================================================
    # COMPUTER USE CAPABILITIES
    # ========================================================================

    def take_screenshot(self) -> str:
        """Take a screenshot and return as base64."""
        if not COMPUTER_USE_AVAILABLE:
            raise RuntimeError("Computer Use not available")

        screenshot = pyautogui.screenshot()
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def execute_computer_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute computer control actions (mouse, keyboard, etc.)."""
        if not COMPUTER_USE_AVAILABLE:
            return {'success': False, 'error': 'Computer Use not available'}

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

            elif action_type == 'type':
                text = action.get('text', '')
                pyautogui.write(text, interval=0.05)
                return {'success': True, 'action': 'type', 'text': text}

            elif action_type == 'key':
                key = action.get('key')
                pyautogui.press(key)
                return {'success': True, 'action': 'key', 'key': key}

            elif action_type == 'screenshot':
                screenshot = self.take_screenshot()
                return {'success': True, 'action': 'screenshot', 'image': screenshot}

            elif action_type == 'wait':
                duration = action.get('duration', 1.0)
                time.sleep(duration)
                return {'success': True, 'action': 'wait', 'duration': duration}

            else:
                return {'success': False, 'error': f'Unknown action: {action_type}'}

        except Exception as e:
            return {'success': False, 'error': str(e), 'action': action_type}

    # ========================================================================
    # DOCUMENT CONVERSION CAPABILITIES
    # ========================================================================

    def convert_pdf_to_markdown(self, pdf_path: Path) -> str:
        """Convert PDF to Markdown."""
        if not DOCUMENT_CONVERSION_AVAILABLE:
            raise RuntimeError("Document conversion not available")

        markdown = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    markdown += f"\n\n# Page {page_num}\n\n{text}"
        return markdown.strip()

    def convert_docx_to_markdown(self, docx_path: Path) -> str:
        """Convert DOCX to Markdown."""
        if not DOCUMENT_CONVERSION_AVAILABLE:
            raise RuntimeError("Document conversion not available")

        doc = DocxDocument(docx_path)
        markdown = ""

        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                # Detect headings
                if para.style.name.startswith('Heading'):
                    level = int(para.style.name[-1]) if para.style.name[-1].isdigit() else 1
                    markdown += f"\n\n{'#' * level} {text}\n\n"
                else:
                    markdown += f"{text}\n\n"

        return markdown.strip()

    def convert_document(self, file_path: Path) -> str:
        """Convert PDF or DOCX to Markdown."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()
        if suffix == '.pdf':
            return self.convert_pdf_to_markdown(file_path)
        elif suffix == '.docx':
            return self.convert_docx_to_markdown(file_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

    # ========================================================================
    # ERROR MONITORING & AUTO-FIX CAPABILITIES
    # ========================================================================

    def load_error_logs(self) -> List[Dict[str, Any]]:
        """Load and parse error logs from the logs directory."""
        logs_dir = self.project_root / "logs"
        errors = []

        if not logs_dir.exists():
            return errors

        for log_file in logs_dir.glob("*.log"):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

                for i, line in enumerate(lines):
                    # Look for common error patterns
                    if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                        errors.append({
                            'file': str(log_file),
                            'line_num': i + 1,
                            'content': line.strip(),
                            'context': lines[max(0, i-2):min(len(lines), i+3)]
                        })

        return errors

    def analyze_error_with_claude(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to analyze an error and suggest fixes."""
        prompt = f"""Analyze this error and provide a fix:

Error: {error['content']}
File: {error['file']}
Line: {error['line_num']}

Context:
{''.join(error.get('context', []))}

Provide:
1. Root cause analysis
2. Suggested fix with code
3. Prevention strategy

Format as JSON:
{{
    "root_cause": "...",
    "fix": {{
        "description": "...",
        "code": "...",
        "file": "..."
    }},
    "prevention": "..."
}}
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        # Try to extract JSON
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {'raw_response': response_text}

    # ========================================================================
    # QA TESTING CAPABILITIES
    # ========================================================================

    def run_qa_test(self, test_prompt: str, max_iterations: int = 30) -> List[str]:
        """
        Run automated QA tests using Computer Use.

        Args:
            test_prompt: Test instructions for Claude
            max_iterations: Maximum number of interaction loops

        Returns:
            List of responses from Claude during testing
        """
        if not COMPUTER_USE_AVAILABLE:
            raise RuntimeError("Computer Use required for QA testing")

        print("\n" + "="*70)
        print("🤖 Starting QA Test Automation")
        print("="*70)

        responses = []

        # Build initial message with screenshot
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": self.take_screenshot()
                }
            },
            {
                "type": "text",
                "text": test_prompt
            }
        ]

        self.conversation_history.append({
            "role": "user",
            "content": content
        })

        # Interact with Claude
        for iteration in range(max_iterations):
            print(f"\n📍 Iteration {iteration + 1}/{max_iterations}")

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=self.conversation_history,
                tools=[{
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": 1920,
                    "display_height_px": 1080,
                    "display_number": 1
                }]
            )

            # Process response
            assistant_message = {"role": "assistant", "content": []}
            response_text = ""
            tool_used = False

            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                    assistant_message["content"].append({
                        "type": "text",
                        "text": block.text
                    })
                    print(f"💬 Claude: {block.text[:200]}...")

                elif block.type == "tool_use":
                    tool_used = True
                    action_result = self.execute_computer_action(block.input)

                    assistant_message["content"].append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

                    # Add tool result
                    self.conversation_history.append(assistant_message)

                    # Take new screenshot after action
                    new_screenshot = self.take_screenshot()

                    self.conversation_history.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(action_result)
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": new_screenshot
                                }
                            }
                        ]
                    })

                    print(f"   🔧 Action: {block.input.get('type')} - {action_result.get('success')}")

            if response_text:
                responses.append(response_text)

            # Check for completion
            if not tool_used and any(phrase in response_text.lower() for phrase in [
                'test complete', 'testing complete', 'all tests', 'report:'
            ]):
                print("\n✅ Testing complete!")
                break

            if not tool_used:
                # No more actions, continue
                self.conversation_history.append(assistant_message)
                self.conversation_history.append({
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": "Continue with the next test step."
                    }]
                })

            time.sleep(0.5)

        return responses

    # ========================================================================
    # UNIFIED TASK EXECUTION
    # ========================================================================

    def execute_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task based on type.

        Task types:
        - 'qa_test': Run automated QA testing
        - 'monitor_errors': Check for and fix production errors
        - 'convert_document': Convert PDF/DOCX to Markdown
        - 'generate_report': Generate comprehensive report
        """
        print(f"\n🚀 Executing task: {task_type}")
        print(f"   Parameters: {kwargs}")

        result = {'task': task_type, 'timestamp': datetime.now().isoformat()}

        try:
            if task_type == 'qa_test':
                test_url = kwargs.get('url', 'http://localhost:8000')
                test_cases = kwargs.get('test_cases', [])

                test_prompt = self._build_qa_prompt(test_url, test_cases)
                responses = self.run_qa_test(test_prompt)

                result['success'] = True
                result['responses'] = responses
                result['report_path'] = self._save_qa_report(responses)

            elif task_type == 'monitor_errors':
                errors = self.load_error_logs()
                fixes = []

                for error in errors[:kwargs.get('max_errors', 5)]:
                    fix = self.analyze_error_with_claude(error)
                    fixes.append({'error': error, 'fix': fix})

                result['success'] = True
                result['errors_found'] = len(errors)
                result['fixes_generated'] = len(fixes)
                result['fixes'] = fixes
                result['report_path'] = self._save_error_report(errors, fixes)

            elif task_type == 'convert_document':
                file_path = Path(kwargs['file_path'])
                markdown = self.convert_document(file_path)
                output_path = self.results_dir / f"{file_path.stem}.md"

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)

                result['success'] = True
                result['input_file'] = str(file_path)
                result['output_file'] = str(output_path)
                result['preview'] = markdown[:500]

            elif task_type == 'generate_report':
                report = self._generate_comprehensive_report()
                report_path = self.results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

                with open(report_path, 'w') as f:
                    f.write(report)

                result['success'] = True
                result['report_path'] = str(report_path)

            else:
                result['success'] = False
                result['error'] = f'Unknown task type: {task_type}'

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            import traceback
            result['traceback'] = traceback.format_exc()

        return result

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _build_qa_prompt(self, url: str, test_cases: List[str]) -> str:
        """Build a comprehensive QA test prompt."""
        prompt = f"""You are performing automated QA testing.

**Target URL:** {url}

**Testing Process:**
1. Navigate to the URL in a browser
2. Execute each test case systematically
3. Document results with screenshots
4. Generate detailed test report

**Test Cases:**
"""

        for i, test_case in enumerate(test_cases, 1):
            prompt += f"\n**Test {i}:** {test_case}"

        prompt += """

**Output Format:**
After completing all tests, provide:

## QA Test Report

### Summary
- Total Tests: X
- Passed: X
- Failed: X

### Detailed Results
[For each test: PASS/FAIL with details and screenshots]

### Bugs Found
[List any bugs with steps to reproduce]

### Recommendations
[Improvements and next steps]

Begin testing now.
"""
        return prompt

    def _save_qa_report(self, responses: List[str]) -> str:
        """Save QA test report to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.results_dir / f"qa_report_{timestamp}.txt"

        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("QA Test Report\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("="*70 + "\n\n")

            for i, response in enumerate(responses, 1):
                f.write(f"\n--- Response {i} ---\n")
                f.write(response)
                f.write("\n")

        return str(report_path)

    def _save_error_report(self, errors: List[Dict], fixes: List[Dict]) -> str:
        """Save error monitoring report to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.results_dir / f"error_report_{timestamp}.md"

        with open(report_path, 'w') as f:
            f.write("# Error Monitoring Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Errors Found:** {len(errors)}\n")
            f.write(f"**Fixes Generated:** {len(fixes)}\n\n")

            f.write("## Errors\n\n")
            for i, error in enumerate(errors, 1):
                f.write(f"### Error {i}\n")
                f.write(f"- **File:** {error['file']}\n")
                f.write(f"- **Line:** {error['line_num']}\n")
                f.write(f"- **Content:** {error['content']}\n\n")

            f.write("## Fixes\n\n")
            for i, fix_data in enumerate(fixes, 1):
                fix = fix_data.get('fix', {})
                f.write(f"### Fix {i}\n")
                f.write(f"- **Root Cause:** {fix.get('root_cause', 'N/A')}\n")
                f.write(f"- **Fix:** {fix.get('fix', {}).get('description', 'N/A')}\n")
                f.write(f"- **Prevention:** {fix.get('prevention', 'N/A')}\n\n")

        return str(report_path)

    def _generate_comprehensive_report(self) -> str:
        """Generate comprehensive system report."""
        report = f"""# System Report

**Generated:** {datetime.now().isoformat()}
**Project:** {self.project_root}

## Agent Capabilities

- Computer Use: {'✅ Enabled' if COMPUTER_USE_AVAILABLE else '❌ Disabled'}
- Document Conversion: {'✅ Enabled' if DOCUMENT_CONVERSION_AVAILABLE else '❌ Disabled'}
- Error Monitoring: ✅ Enabled
- QA Testing: {'✅ Enabled' if COMPUTER_USE_AVAILABLE else '❌ Disabled'}

## Recent Activity

"""

        # List recent reports
        recent_reports = sorted(self.results_dir.glob("*_report_*.txt"), reverse=True)[:5]
        report += "### Recent Reports\n\n"
        for report_file in recent_reports:
            report += f"- {report_file.name}\n"

        return report


def main():
    """Main CLI interface for the unified agent."""
    import argparse

    parser = argparse.ArgumentParser(description='Unified Multi-Purpose Agent')
    parser.add_argument('task', choices=['qa_test', 'monitor_errors', 'convert_document', 'report'],
                        help='Task to execute')
    parser.add_argument('--url', default='http://localhost:8000',
                        help='URL for QA testing')
    parser.add_argument('--file', help='File path for document conversion')
    parser.add_argument('--max-errors', type=int, default=5,
                        help='Maximum errors to analyze')

    args = parser.parse_args()

    # Initialize agent
    agent = UnifiedAgent()

    # Execute task
    if args.task == 'qa_test':
        # Default test cases for @mention component
        test_cases = [
            "Type '@' and verify autocomplete appears",
            "Press Enter to select mention and verify it's inserted",
            "Insert two mentions and press Backspace - verify autocomplete position",
            "Press Escape to close autocomplete",
            "Use arrow keys to navigate autocomplete options"
        ]

        result = agent.execute_task('qa_test', url=args.url, test_cases=test_cases)

    elif args.task == 'monitor_errors':
        result = agent.execute_task('monitor_errors', max_errors=args.max_errors)

    elif args.task == 'convert_document':
        if not args.file:
            print("❌ Error: --file required for document conversion")
            sys.exit(1)
        result = agent.execute_task('convert_document', file_path=args.file)

    elif args.task == 'report':
        result = agent.execute_task('generate_report')

    # Print result
    print("\n" + "="*70)
    print("🎉 Task Complete!")
    print("="*70)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
