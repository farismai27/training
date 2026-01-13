#!/usr/bin/env python3
"""
OCAA Unified Extension - Computer Use, Error Monitoring & Workflows

This file contains all the additional capabilities to be merged into demo.py:
- Computer Use (screenshot, mouse, keyboard)
- Error Monitoring & Auto-Fix
- QA Testing Workflows
- Evaluator-Optimizer Patterns

To integrate: Copy sections into demo.py at the marked locations
"""

# ===========================================================================
# SECTION 1: ADD TO IMPORTS (After line 22 in demo.py)
# ===========================================================================

import base64
from io import BytesIO
import re
from typing import Optional

# Try to import Computer Use dependencies
try:
    from PIL import Image
    import pyautogui
    COMPUTER_USE_AVAILABLE = True
    pyautogui.FAILSAFE = True  # Enable fail-safe
except ImportError:
    COMPUTER_USE_AVAILABLE = False
    print("⚠️  Computer Use unavailable (pip install pillow pyautogui)")

try:
    import pdfplumber
    from docx import Document as DocxDocument
    DOCUMENT_CONVERSION_AVAILABLE = True
except ImportError:
    DOCUMENT_CONVERSION_AVAILABLE = False

# ===========================================================================
# SECTION 2: COMPUTER USE TOOL SCHEMAS (Add after line 400 with other schemas)
# ===========================================================================

# Computer Use tool schemas
computer_screenshot_schema = ToolParam(
    name="take_screenshot",
    description=(
        "Take a screenshot of the current screen and return as base64 image. "
        "Use this to see the current state of the screen during QA testing or "
        "when you need to analyze UI elements visually."
    ),
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

computer_action_schema = ToolParam(
    name="execute_computer_action",
    description=(
        "Execute mouse/keyboard actions on the computer for automation. "
        "Supports: mouse_move, click, type (text input), key (press key), wait. "
        "Use for QA testing, UI automation, and interactive workflows."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "action_type": {
                "type": "string",
                "enum": ["mouse_move", "click", "type", "key", "wait"],
                "description": "Type of action to perform"
            },
            "x": {
                "type": "number",
                "description": "X coordinate for mouse actions"
            },
            "y": {
                "type": "number",
                "description": "Y coordinate for mouse actions"
            },
            "text": {
                "type": "string",
                "description": "Text to type (for 'type' action)"
            },
            "key": {
                "type": "string",
                "description": "Key to press (for 'key' action): enter, escape, backspace, etc."
            },
            "button": {
                "type": "string",
                "enum": ["left", "right", "middle"],
                "description": "Mouse button (for 'click' action, default: left)"
            },
            "duration": {
                "type": "number",
                "description": "Duration in seconds (for 'wait' action)"
            }
        },
        "required": ["action_type"]
    }
)

error_analysis_schema = ToolParam(
    name="analyze_production_error",
    description=(
        "Analyze a production error and generate a fix with root cause analysis. "
        "Provide error content and optional context. Returns fix code, explanation, "
        "and prevention strategy."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "error_content": {
                "type": "string",
                "description": "The error message or stack trace"
            },
            "file_path": {
                "type": "string",
                "description": "Optional file path where error occurred"
            },
            "context": {
                "type": "string",
                "description": "Optional surrounding code or context"
            }
        },
        "required": ["error_content"]
    }
)

qa_workflow_schema = ToolParam(
    name="run_qa_workflow",
    description=(
        "Run automated QA testing workflow on a URL. Tests UI components, "
        "generates screenshots, executes test cases, and produces a report. "
        "Provide URL and optional test cases array."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to test (e.g., http://localhost:8000)"
            },
            "test_cases": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional array of test case descriptions"
            },
            "max_iterations": {
                "type": "number",
                "description": "Max testing iterations (default: 30)"
            }
        },
        "required": ["url"]
    }
)

# ===========================================================================
# SECTION 3: COMPUTER USE FUNCTIONS (Add after line 760 before execute_tool)
# ===========================================================================

def tool_take_screenshot():
    """Take screenshot and return base64 encoded image."""
    if not COMPUTER_USE_AVAILABLE:
        raise RuntimeError("Computer Use not available. Install: pip install pillow pyautogui")

    try:
        screenshot = pyautogui.screenshot()
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return {
            "success": True,
            "image_base64": img_str,
            "format": "PNG",
            "note": "Screenshot captured successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def tool_execute_computer_action(action_type, x=None, y=None, text=None, key=None, button="left", duration=1.0):
    """Execute computer actions (mouse, keyboard)."""
    if not COMPUTER_USE_AVAILABLE:
        raise RuntimeError("Computer Use not available. Install: pip install pillow pyautogui")

    try:
        if action_type == "mouse_move":
            if x is None or y is None:
                raise ValueError("x and y coordinates required for mouse_move")
            pyautogui.moveTo(x, y, duration=0.2)
            return {"success": True, "action": "mouse_move", "x": x, "y": y}

        elif action_type == "click":
            if x is None or y is None:
                raise ValueError("x and y coordinates required for click")
            pyautogui.click(x, y, button=button)
            return {"success": True, "action": "click", "x": x, "y": y, "button": button}

        elif action_type == "type":
            if not text:
                raise ValueError("text required for type action")
            pyautogui.write(text, interval=0.05)
            return {"success": True, "action": "type", "text": text}

        elif action_type == "key":
            if not key:
                raise ValueError("key required for key action")
            pyautogui.press(key)
            return {"success": True, "action": "key", "key": key}

        elif action_type == "wait":
            time.sleep(duration)
            return {"success": True, "action": "wait", "duration": duration}

        else:
            raise ValueError(f"Unknown action_type: {action_type}")

    except Exception as e:
        return {"success": False, "error": str(e), "action": action_type}

def tool_analyze_production_error(error_content, file_path=None, context=None):
    """Analyze production error and generate fix."""
    prompt = f"""Analyze this production error and provide a fix:

Error: {error_content}
File: {file_path or 'Unknown'}
Context:
{context or 'No additional context'}

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

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        # Try to extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            fix_data = json.loads(json_match.group())
            return {
                "success": True,
                "analysis": fix_data
            }
        else:
            return {
                "success": True,
                "raw_response": response_text
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def tool_run_qa_workflow(url, test_cases=None, max_iterations=30):
    """Run automated QA testing workflow."""
    if not COMPUTER_USE_AVAILABLE:
        raise RuntimeError("Computer Use required for QA workflows")

    # Default test cases if none provided
    if not test_cases:
        test_cases = [
            "Navigate to the URL and verify page loads",
            "Interact with main UI elements",
            "Test form inputs and buttons",
            "Verify expected functionality",
            "Report any bugs or issues found"
        ]

    # Build QA prompt
    qa_prompt = f"""You are performing automated QA testing.

**Target URL:** {url}

**Test Cases:**
"""
    for i, tc in enumerate(test_cases, 1):
        qa_prompt += f"\n{i}. {tc}"

    qa_prompt += """

**Process:**
1. Take screenshot to see current state
2. Navigate to URL if needed
3. Execute each test case systematically
4. Take screenshots of any issues
5. Generate report with PASS/FAIL for each test

**Report Format:**
## QA Test Report

### Summary
- Total Tests: X
- Passed: X
- Failed: X

### Test Results
[For each test: PASS/FAIL with details]

### Bugs Found
[List any bugs with reproduction steps]

Begin testing now.
"""

    # Run QA workflow with Computer Use
    conversation = []
    responses = []

    print(f"\n🧪 Starting QA Workflow for {url}")
    print(f"   Max iterations: {max_iterations}")
    print(f"   Test cases: {len(test_cases)}")

    # Initial screenshot
    screenshot_result = tool_take_screenshot()

    conversation.append({
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": screenshot_result.get("image_base64", "")
                }
            },
            {
                "type": "text",
                "text": qa_prompt
            }
        ]
    })

    for iteration in range(max_iterations):
        print(f"\n   Iteration {iteration + 1}/{max_iterations}")

        try:
            # Call Claude with Computer Use support (using beta API)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=conversation,
                tools=[{
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": 1920,
                    "display_height_px": 1080
                }]
            )

            # Process response
            response_text = ""
            tool_used = False

            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                    responses.append(block.text)
                    print(f"   Claude: {block.text[:100]}...")

                elif block.type == "tool_use":
                    tool_used = True
                    # Execute computer action
                    action_result = tool_execute_computer_action(**block.input)
                    print(f"   Action: {block.input.get('type')} - {action_result.get('success')}")

            # Check for completion
            if not tool_used and any(phrase in response_text.lower() for phrase in
                                    ['test complete', 'testing complete', 'report:']):
                print("\n   ✅ Testing complete!")
                break

            # Continue conversation
            time.sleep(0.5)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            break

    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f"results/qa_report_{timestamp}.txt"

    os.makedirs("results", exist_ok=True)
    with open(report_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write(f"QA Test Report: {url}\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("="*70 + "\n\n")
        for i, resp in enumerate(responses, 1):
            f.write(f"\n--- Response {i} ---\n{resp}\n")

    return {
        "success": True,
        "url": url,
        "test_cases": test_cases,
        "iterations": iteration + 1,
        "responses": len(responses),
        "report_path": report_path
    }

# ===========================================================================
# SECTION 4: WORKFLOW PATTERNS (Add after QA functions)
# ===========================================================================

def evaluator_optimizer_workflow(task, producer_prompt, grader_prompt, max_iterations=5):
    """
    Evaluator-Optimizer pattern from the lesson.

    Components:
    - PRODUCER: Generates output
    - GRADER: Evaluates output quality
    - FEEDBACK LOOP: Iterates until grader accepts
    """
    print("\n" + "="*70)
    print("🔄 EVALUATOR-OPTIMIZER WORKFLOW")
    print("="*70)
    print(f"Task: {task}")
    print(f"Max iterations: {max_iterations}\n")

    for iteration in range(max_iterations):
        print(f"\n📍 Iteration {iteration + 1}/{max_iterations}")

        # PRODUCER: Generate output
        print("   📝 Producer: Generating output...")
        producer_response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": producer_prompt}]
        )
        produced_content = producer_response.content[0].text
        print(f"   Output length: {len(produced_content)} chars")

        # GRADER: Evaluate output
        print("   ✅ Grader: Evaluating quality...")
        grader_response = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"{grader_prompt}\n\nOutput to grade:\n{produced_content}"
            }]
        )
        grade = grader_response.content[0].text

        # Check if grader accepts
        if "PASS" in grade.upper() or "ACCEPT" in grade.upper() or "APPROVED" in grade.upper():
            print(f"   🎉 Grader ACCEPTED output!")
            print(f"\n{'='*70}")
            print("WORKFLOW COMPLETE - OUTPUT ACCEPTED")
            print(f"{'='*70}\n")
            return {
                'success': True,
                'output': produced_content,
                'iterations': iteration + 1,
                'final_grade': grade
            }

        # Feedback loop: Extract improvement suggestions
        print(f"   ⚠️  Grader REJECTED. Providing feedback...")
        print(f"   Feedback: {grade[:100]}...")

        # Update producer prompt with feedback
        producer_prompt = f"""{task}

Previous attempt:
{produced_content}

Grader feedback:
{grade}

Please improve based on this feedback."""

    print(f"\n{'='*70}")
    print("WORKFLOW ENDED - MAX ITERATIONS REACHED")
    print(f"{'='*70}\n")

    return {
        'success': False,
        'output': produced_content,
        'iterations': max_iterations,
        'reason': 'Max iterations reached without acceptance'
    }

def load_and_analyze_errors():
    """Load error logs and analyze them."""
    logs_dir = Path("logs")
    errors = []

    if not logs_dir.exists():
        return {"errors_found": 0, "errors": [], "message": "No logs directory found"}

    for log_file in logs_dir.glob("*.log"):
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                    errors.append({
                        'file': str(log_file),
                        'line_num': i + 1,
                        'content': line.strip(),
                        'context': ''.join(lines[max(0, i-2):min(len(lines), i+3)])
                    })

    return {
        "errors_found": len(errors),
        "errors": errors[:10],  # Limit to first 10
        "message": f"Found {len(errors)} errors in logs"
    }

# ===========================================================================
# SECTION 5: UPDATE system_prompt (Replace existing, around line 2038)
# ===========================================================================

UPDATED_SYSTEM_PROMPT = """
<identity>
You are the OneSuite Core Architect Agent (OCAA) - a unified multi-capability AI agent.

Your roles:
1. **Product Manager** - Product strategy and documentation for OneSuite Core
2. **QA Automation Specialist** - Automated testing using Computer Use
3. **Production Monitor** - Error analysis and automated bug fixing
4. **Workflow Architect** - Design and execute complex multi-step workflows

When asked who you are, introduce yourself clearly:
"I am the OneSuite Core Architect Agent (OCAA), a unified AI agent specializing in
product strategy, QA automation, error monitoring, and workflow execution for the
OneSuite Core platform."
</identity>

<task>
PRIMARY: Define clear, actionable product user stories with acceptance criteria.
SECONDARY: Execute automated QA tests, monitor production errors, and design workflows.
TERTIARY: Maintain consistency across all OneSuite channels (Search, Social, Programmatic, Commerce).
</task>

<capabilities>
1. **Product Strategy**
   - User story development with acceptance criteria
   - Product roadmap creation aligned with OneSuite vision
   - Multi-channel impact analysis (Search, Social, Programmatic, Commerce)
   - Requirement documentation and specification

2. **QA Testing & Automation (Computer Use)**
   - Automated UI/UX testing with screenshot analysis
   - Mouse and keyboard automation for test execution
   - Test case execution and validation
   - Detailed test report generation with PASS/FAIL results
   - Bug documentation with reproduction steps

3. **Production Error Monitoring**
   - Production log analysis and error detection
   - Root cause analysis for errors and exceptions
   - Automated fix generation with code suggestions
   - Prevention strategy recommendations
   - Fix validation and testing

4. **Workflow Design & Execution**
   - Evaluator-Optimizer patterns (Producer → Grader → Feedback)
   - RAG pipelines (Retrieval → Re-ranking → Generation)
   - Multi-step automation workflows
   - Iterative refinement processes
   - Quality validation loops

5. **Document Management (via MCP)**
   - PDF/DOCX to Markdown conversion
   - Document storage and retrieval
   - Content analysis and summarization
</capabilities>

<tools_available>
**Product Strategy Tools:**
- get_current_datetime: Get current date/time for planning
- set_reminder: Schedule tasks and reminders
- get_confluence_page: Retrieve Confluence documentation
- calculate_product_metrics: Analyze product performance

**Document Management Tools (MCP):**
- document_path_to_markdown: Convert documents to Markdown
- list_documents: List available documents
- read_document: Read document contents
- update_document: Update document contents

**Computer Use Tools:**
- take_screenshot: Capture current screen state
- execute_computer_action: Perform mouse/keyboard actions
  - Actions: click, type, key_press, mouse_move, wait

**Error Monitoring Tools:**
- analyze_production_error: Analyze errors and generate fixes
- load_error_logs: Scan and parse production logs

**Workflow Tools:**
- run_qa_workflow: Execute complete QA testing workflow
- evaluator_optimizer: Run iterative refinement workflows
</tools_available>

<instructions>
YOUR THINKING PROCESS (Follow these steps for every request):

**For Product Strategy Tasks:**
1. ANALYZE THE SCOPE - Identify affected channels (Search, Social, Programmatic, Commerce)
2. IDENTIFY STAKEHOLDERS - Determine who is impacted and their needs
3. ASSESS CURRENT STATE - What exists today? What are the gaps?
4. BRAINSTORM SOLUTIONS - Generate multiple approaches, evaluate trade-offs
5. STRUCTURE LOGICALLY - Organize findings into clear, hierarchical sections
6. VALIDATE CONSISTENCY - Ensure alignment across all affected channels

**For QA Testing Tasks:**
1. UNDERSTAND REQUIREMENTS - What needs to be tested?
2. TAKE SCREENSHOT - See current state of application
3. EXECUTE TESTS - Use computer actions to interact and validate
4. DOCUMENT RESULTS - Record PASS/FAIL with screenshots
5. REPORT BUGS - Provide clear reproduction steps for failures

**For Error Monitoring Tasks:**
1. LOAD LOGS - Scan production logs for errors
2. ANALYZE ROOT CAUSE - Understand why the error occurred
3. GENERATE FIX - Provide code-level solution
4. EXPLAIN PREVENTION - How to avoid this in future
5. VALIDATE FIX - Ensure solution addresses root cause

**For Workflow Tasks:**
1. DESIGN WORKFLOW - Break down into Producer → Grader → Feedback
2. EXECUTE PRODUCER - Generate initial output
3. RUN GRADER - Evaluate quality against criteria
4. PROVIDE FEEDBACK - If rejected, explain improvements needed
5. ITERATE - Repeat until output meets quality standards
</instructions>

<response_format>
**For Product Strategy:**
- Context: Current situation and background
- Problem: What needs to be solved and why
- Solution: Proposed approach with rationale
- Acceptance Criteria: Measurable, specific requirements
- Channel Impact: Effects on Search, Social, Programmatic, Commerce
- Dependencies: Related features, teams, or systems
- Assumptions & Constraints: What we're assuming and what limits apply

**For QA Testing:**
- Test Summary: Total tests, passed, failed
- Detailed Results: PASS/FAIL for each test with evidence
- Bugs Found: Clear description with reproduction steps
- Screenshots: Visual evidence of issues
- Recommendations: Suggested fixes and improvements

**For Error Analysis:**
- Error Summary: What error occurred and where
- Root Cause: Why the error happened
- Proposed Fix: Code-level solution with explanation
- Prevention: How to avoid this error in future
- Validation: How to verify the fix works

**For Workflows:**
- Workflow Type: Which pattern (Evaluator-Optimizer, RAG, etc.)
- Steps Executed: What happened in each iteration
- Results: Final output and quality assessment
- Iterations: How many cycles were needed
- Lessons: What was learned from the process
</response_format>

<constraints>
- Focus primarily on OneSuite Core product strategy for product tasks
- Use Computer Use tools responsibly - always confirm before destructive actions
- Analyze errors thoroughly before suggesting fixes
- Document all assumptions and constraints clearly
- Keep responses comprehensive but concise
- Include cross-channel impact analysis where relevant
- Be specific and measurable - avoid vague language
</constraints>

<communication_style>
Professional, structured, and results-oriented. Always maintain clarity and completeness.
For technical tasks, be precise and detailed. For strategy tasks, be comprehensive and considerate
of multi-channel impacts.
</communication_style>
"""

# ===========================================================================
# SECTION 6: ADD TO execute_tool() FUNCTION (around line 860)
# ===========================================================================

# Add these cases to the execute_tool() function:

# elif tool_name == "take_screenshot":
#     try:
#         result = tool_take_screenshot()
#         return json.dumps(result)
#     except Exception as e:
#         return json.dumps({"error": str(e)})

# elif tool_name == "execute_computer_action":
#     try:
#         result = tool_execute_computer_action(
#             tool_input.get("action_type"),
#             x=tool_input.get("x"),
#             y=tool_input.get("y"),
#             text=tool_input.get("text"),
#             key=tool_input.get("key"),
#             button=tool_input.get("button", "left"),
#             duration=tool_input.get("duration", 1.0)
#         )
#         return json.dumps(result)
#     except Exception as e:
#         return json.dumps({"error": str(e)})

# elif tool_name == "analyze_production_error":
#     try:
#         result = tool_analyze_production_error(
#             tool_input.get("error_content", ""),
#             file_path=tool_input.get("file_path"),
#             context=tool_input.get("context")
#         )
#         return json.dumps(result)
#     except Exception as e:
#         return json.dumps({"error": str(e)})

# elif tool_name == "run_qa_workflow":
#     try:
#         result = tool_run_qa_workflow(
#             tool_input.get("url", ""),
#            test_cases=tool_input.get("test_cases"),
#             max_iterations=tool_input.get("max_iterations", 30)
#         )
#         return json.dumps(result)
#     except Exception as e:
#         return json.dumps({"error": str(e)})

# ===========================================================================
# SECTION 7: ADD TO main() FUNCTION (around line 3400)
# ===========================================================================

# Add these commands to the print statements in main():

"""
print("\n  --- QA & TESTING ---")
print("  '/qa-test <url>' - Run automated QA tests on URL")
print("  '/test-mention' - Test @mention component (http://localhost:8000)")

print("\n  --- ERROR MONITORING ---")
print("  '/monitor-errors' - Analyze production error logs")
print("  '/analyze-error' - Analyze specific error interactively")

print("\n  --- WORKFLOWS ---")
print("  '/workflow-demo' - Demo Evaluator-Optimizer pattern")
print("  '/full-automation' - Run all capabilities in sequence")

print(f"\n  Computer Use: {'✅ Enabled' if COMPUTER_USE_AVAILABLE else '❌ Disabled'}")
print(f"  Document Conversion: {'✅ Enabled' if DOCUMENT_CONVERSION_AVAILABLE else '❌ Disabled'}")
"""

# Add these command handlers in the main() loop (around line 3450):

"""
elif user_input.startswith("/qa-test"):
    parts = user_input.split(maxsplit=1)
    url = parts[1] if len(parts) > 1 else "http://localhost:8000"

    print(f"\n🧪 Running QA tests on: {url}")
    result = tool_run_qa_workflow(url)

    if result.get("success"):
        print(f"\n✅ QA Testing Complete!")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Responses: {result['responses']}")
        print(f"   Report: {result['report_path']}")
    else:
        print(f"\n❌ QA Testing failed: {result.get('error')}")

elif user_input == "/test-mention":
    print("\n🧪 Testing @mention component...")
    print("   Make sure test server is running: python computer-use/test-app/server.py")

    test_cases = [
        "Type '@' and verify autocomplete appears",
        "Press Enter to insert mention",
        "Test backspace with multiple mentions (check positioning bug)",
        "Press Escape to close autocomplete",
        "Test arrow key navigation"
    ]

    result = tool_run_qa_workflow("http://localhost:8000", test_cases=test_cases)

    if result.get("success"):
        print(f"\n✅ @Mention Testing Complete!")
        print(f"   Report: {result['report_path']}")

elif user_input == "/monitor-errors":
    print("\n🐛 Monitoring production errors...")

    errors_data = load_and_analyze_errors()
    print(f"\n{'='*70}")
    print(f"ERRORS FOUND: {errors_data['errors_found']}")
    print(f"{'='*70}\n")

    if errors_data['errors_found'] > 0:
        for i, error in enumerate(errors_data['errors'][:5], 1):
            print(f"\n{i}. Error in {error['file']}:{error['line_num']}")
            print(f"   {error['content']}")

            # Analyze first 3 errors
            if i <= 3:
                print(f"   Analyzing...")
                analysis = tool_analyze_production_error(
                    error['content'],
                    file_path=error['file'],
                    context=error['context']
                )

                if analysis.get('success') and 'analysis' in analysis:
                    fix = analysis['analysis']
                    print(f"   Root Cause: {fix.get('root_cause', 'N/A')[:80]}...")
                    print(f"   Fix: {fix.get('fix', {}).get('description', 'N/A')[:80]}...")
    else:
        print("✅ No errors found in logs directory")

elif user_input == "/analyze-error":
    print("\n🔍 Interactive Error Analysis")
    print("   Paste error message (end with empty line):\n")

    error_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        error_lines.append(line)

    if error_lines:
        error_content = '\n'.join(error_lines)
        print("\n   Analyzing...")

        analysis = tool_analyze_production_error(error_content)

        if analysis.get('success'):
            if 'analysis' in analysis:
                fix = analysis['analysis']
                print(f"\n{'='*70}")
                print("ERROR ANALYSIS REPORT")
                print(f"{'='*70}\n")
                print(f"Root Cause:\n{fix.get('root_cause', 'N/A')}\n")
                print(f"Proposed Fix:\n{fix.get('fix', {}).get('description', 'N/A')}\n")
                print(f"Code:\n{fix.get('fix', {}).get('code', 'N/A')}\n")
                print(f"Prevention:\n{fix.get('prevention', 'N/A')}\n")
            else:
                print(f"\n{analysis.get('raw_response', 'No analysis available')}")

elif user_input == "/workflow-demo":
    print("\n🔄 Evaluator-Optimizer Workflow Demo")
    print("   Demonstrating Producer → Grader → Feedback loop\n")

    task = "Write a concise product roadmap for Q2 2026"

    producer_prompt = """Write a concise 3-month product roadmap for OneSuite Core Q2 2026.
Include: MVP phase, V1 features, and Scale phase.
Keep it under 200 words."""

    grader_prompt = """Evaluate this product roadmap:

Criteria:
- Clear phases (MVP, V1, Scale)
- Under 200 words
- Specific and actionable
- Includes timelines

Respond with:
- PASS if meets all criteria
- FAIL if missing requirements (explain what's missing)"""

    result = evaluator_optimizer_workflow(task, producer_prompt, grader_prompt, max_iterations=3)

    if result['success']:
        print(f"\n✅ Workflow succeeded in {result['iterations']} iterations")
        print(f"\nFinal Output:\n{result['output']}")
    else:
        print(f"\n⚠️  Workflow ended: {result['reason']}")

elif user_input == "/full-automation":
    print("\n" + "="*70)
    print("🎯 FULL AUTOMATION MODE - ALL CAPABILITIES")
    print("="*70)
    print("\nThis will run:")
    print("  1. QA Tests (on http://localhost:8000)")
    print("  2. Error Monitoring (analyze logs)")
    print("  3. Workflow Demo (Evaluator-Optimizer)")
    print("  4. Generate Summary Report")

    confirm = input("\nContinue? [y/N]: ")
    if confirm.lower() == 'y':
        results = {}

        # 1. QA Tests
        print("\n" + "="*70)
        print("STEP 1: QA TESTING")
        print("="*70)
        try:
            qa_result = tool_run_qa_workflow("http://localhost:8000")
            results['qa'] = qa_result
            print(f"✅ QA Complete - {qa_result.get('report_path')}")
        except Exception as e:
            print(f"❌ QA Failed: {e}")
            results['qa'] = {'error': str(e)}

        # 2. Error Monitoring
        print("\n" + "="*70)
        print("STEP 2: ERROR MONITORING")
        print("="*70)
        try:
            errors = load_and_analyze_errors()
            results['errors'] = errors
            print(f"✅ Found {errors['errors_found']} errors")
        except Exception as e:
            print(f"❌ Error Monitoring Failed: {e}")
            results['errors'] = {'error': str(e)}

        # 3. Workflow Demo
        print("\n" + "="*70)
        print("STEP 3: WORKFLOW DEMO")
        print("="*70)
        try:
            workflow_result = evaluator_optimizer_workflow(
                "Write a user story",
                "Write a user story for OneSuite search filtering",
                "Grade: PASS if has As a/I want to/So that format, FAIL otherwise",
                max_iterations=2
            )
            results['workflow'] = workflow_result
            print(f"✅ Workflow Complete - {workflow_result['success']}")
        except Exception as e:
            print(f"❌ Workflow Failed: {e}")
            results['workflow'] = {'error': str(e)}

        # 4. Summary
        print("\n" + "="*70)
        print("🎉 FULL AUTOMATION COMPLETE")
        print("="*70)
        print(f"\nQA Tests: {'✅' if results.get('qa', {}).get('success') else '❌'}")
        print(f"Error Monitoring: ✅ ({results.get('errors', {}).get('errors_found', 0)} errors)")
        print(f"Workflow Demo: {'✅' if results.get('workflow', {}).get('success') else '❌'}")
"""

print("\n" + "="*70)
print("✅ OCAA UNIFIED EXTENSION - INTEGRATION GUIDE")
print("="*70)
print("""
This file contains all components to merge into demo.py:

1. ✅ Computer Use capabilities (screenshot, mouse, keyboard)
2. ✅ Error monitoring and analysis
3. ✅ QA testing workflows
4. ✅ Evaluator-Optimizer patterns
5. ✅ Updated system prompt with all capabilities
6. ✅ New commands: /qa-test, /monitor-errors, /workflow-demo, /full-automation

TO INTEGRATE:
Copy each SECTION into demo.py at the marked locations.

OR: Run the automated merge script (coming next!)
""")
