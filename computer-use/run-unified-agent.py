#!/usr/bin/env python3
"""
Unified Agent Runner

Interactive interface for running the unified multi-purpose agent.
Combines QA testing, error monitoring, and document conversion.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from unified_agent import UnifiedAgent


def print_banner():
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🤖 UNIFIED MULTI-PURPOSE AGENT 🤖               ║
║                                                              ║
║  Autonomous AI Agent with Multiple Capabilities:            ║
║  • QA Testing & Automation                                   ║
║  • Production Error Monitoring                               ║
║  • Automatic Bug Fixing                                      ║
║  • Document Conversion (PDF/DOCX → Markdown)                 ║
║  • Computer Control & Automation                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def print_menu():
    """Print main menu."""
    print("\n" + "="*60)
    print("MAIN MENU")
    print("="*60)
    print("\n1. 🧪 Run QA Tests")
    print("   Test @mention component or custom URL")
    print("\n2. 🐛 Monitor & Fix Errors")
    print("   Analyze production logs and generate fixes")
    print("\n3. 📄 Convert Document")
    print("   Convert PDF or DOCX to Markdown")
    print("\n4. 📊 Generate Report")
    print("   Comprehensive system and activity report")
    print("\n5. 🎯 Run All Tasks (Full Automation)")
    print("   Execute all capabilities in sequence")
    print("\n6. ❌ Exit")
    print("\n" + "="*60)


def run_qa_tests(agent: UnifiedAgent):
    """Run QA testing workflow."""
    print("\n" + "="*60)
    print("🧪 QA TESTING WORKFLOW")
    print("="*60)

    # Get URL
    print("\n📍 Enter URL to test (or press Enter for default):")
    url = input("   URL [http://localhost:8000]: ").strip()
    if not url:
        url = "http://localhost:8000"

    # Ask about test type
    print("\n🎯 Select test type:")
    print("   1. @Mention Component (default test cases)")
    print("   2. Custom test cases")

    choice = input("\n   Choice [1]: ").strip()

    if choice == "2":
        print("\n📝 Enter test cases (one per line, empty line to finish):")
        test_cases = []
        while True:
            case = input("   ").strip()
            if not case:
                break
            test_cases.append(case)
    else:
        # Default @mention test cases
        test_cases = [
            "Type '@' in the text area and verify autocomplete dropdown appears with user suggestions",
            "Type '@john' and verify autocomplete filters to show matching users",
            "Press Enter to select the first option and verify mention is inserted as a pill",
            "Insert two mentions by typing '@', selecting one, then typing '@' again and selecting another",
            "After inserting two mentions, press Backspace after the second mention and check if autocomplete position is correct (BUG: should appear near cursor, not top-left)",
            "Press Escape while autocomplete is open and verify it closes properly",
            "Use Arrow Down and Arrow Up keys to navigate through autocomplete options",
            "Take screenshots of any visual bugs or positioning issues"
        ]

    print("\n⚠️  IMPORTANT: Make sure the test server is running!")
    print(f"   If testing {url}, start the server first:")
    print("   python computer-use/test-app/server.py")

    print("\n🚀 Ready to start testing?")
    input("   Press Enter when ready...")

    # Execute
    result = agent.execute_task('qa_test', url=url, test_cases=test_cases)

    if result.get('success'):
        print(f"\n✅ QA Testing Complete!")
        print(f"   Report saved: {result.get('report_path')}")
        print(f"\n   Total responses: {len(result.get('responses', []))}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


def run_error_monitoring(agent: UnifiedAgent):
    """Run error monitoring workflow."""
    print("\n" + "="*60)
    print("🐛 ERROR MONITORING WORKFLOW")
    print("="*60)

    print("\n🔍 Scanning for errors in logs directory...")

    # Ask for max errors
    print("\n📊 How many errors should I analyze?")
    max_errors = input("   Max errors [5]: ").strip()
    max_errors = int(max_errors) if max_errors.isdigit() else 5

    print(f"\n⚙️  Analyzing up to {max_errors} errors...")

    # Execute
    result = agent.execute_task('monitor_errors', max_errors=max_errors)

    if result.get('success'):
        print(f"\n✅ Error Monitoring Complete!")
        print(f"   Errors found: {result.get('errors_found', 0)}")
        print(f"   Fixes generated: {result.get('fixes_generated', 0)}")
        print(f"   Report saved: {result.get('report_path')}")

        # Show summary of fixes
        fixes = result.get('fixes', [])
        if fixes:
            print("\n🔧 Fixes Generated:")
            for i, fix_data in enumerate(fixes[:3], 1):
                fix = fix_data.get('fix', {})
                print(f"\n   Fix {i}:")
                print(f"   Root Cause: {fix.get('root_cause', 'N/A')[:80]}...")
                print(f"   Prevention: {fix.get('prevention', 'N/A')[:80]}...")
    else:
        print(f"\n❌ Error: {result.get('error')}")


def run_document_conversion(agent: UnifiedAgent):
    """Run document conversion workflow."""
    print("\n" + "="*60)
    print("📄 DOCUMENT CONVERSION WORKFLOW")
    print("="*60)

    print("\n📁 Enter path to document (PDF or DOCX):")
    file_path = input("   File path: ").strip()

    if not file_path:
        print("❌ No file specified")
        return

    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    print(f"\n⚙️  Converting {file_path.name}...")

    # Execute
    result = agent.execute_task('convert_document', file_path=str(file_path))

    if result.get('success'):
        print(f"\n✅ Conversion Complete!")
        print(f"   Input: {result.get('input_file')}")
        print(f"   Output: {result.get('output_file')}")
        print(f"\n   Preview:")
        print("   " + "-"*56)
        print("   " + result.get('preview', '')[:200].replace('\n', '\n   '))
        print("   " + "-"*56)
    else:
        print(f"\n❌ Error: {result.get('error')}")


def generate_report(agent: UnifiedAgent):
    """Generate comprehensive report."""
    print("\n" + "="*60)
    print("📊 GENERATING COMPREHENSIVE REPORT")
    print("="*60)

    result = agent.execute_task('generate_report')

    if result.get('success'):
        print(f"\n✅ Report Generated!")
        print(f"   Saved to: {result.get('report_path')}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


def run_all_tasks(agent: UnifiedAgent):
    """Run all tasks in sequence."""
    print("\n" + "="*60)
    print("🎯 FULL AUTOMATION MODE")
    print("="*60)
    print("\nThis will run:")
    print("   1. QA Tests (default @mention tests)")
    print("   2. Error Monitoring (analyze up to 5 errors)")
    print("   3. Generate comprehensive report")

    print("\n⚠️  Make sure:")
    print("   • Test server is running (http://localhost:8000)")
    print("   • Logs directory has recent logs")

    confirm = input("\n   Continue? [y/N]: ").strip().lower()

    if confirm != 'y':
        print("   Cancelled.")
        return

    results = []

    # 1. QA Tests
    print("\n" + "="*60)
    print("STEP 1: QA Testing")
    print("="*60)

    test_cases = [
        "Type '@' and verify autocomplete appears",
        "Press Enter to select mention and verify insertion",
        "Test backspace with multiple mentions (check positioning bug)",
        "Test Escape key to close autocomplete",
        "Test arrow key navigation"
    ]

    result = agent.execute_task('qa_test', url='http://localhost:8000', test_cases=test_cases)
    results.append(('QA Tests', result))

    if result.get('success'):
        print(f"✅ QA Tests complete - Report: {result.get('report_path')}")
    else:
        print(f"❌ QA Tests failed: {result.get('error')}")

    # 2. Error Monitoring
    print("\n" + "="*60)
    print("STEP 2: Error Monitoring")
    print("="*60)

    result = agent.execute_task('monitor_errors', max_errors=5)
    results.append(('Error Monitoring', result))

    if result.get('success'):
        print(f"✅ Error monitoring complete - Found {result.get('errors_found')} errors")
    else:
        print(f"❌ Error monitoring failed: {result.get('error')}")

    # 3. Generate Report
    print("\n" + "="*60)
    print("STEP 3: Generate Report")
    print("="*60)

    result = agent.execute_task('generate_report')
    results.append(('Report Generation', result))

    if result.get('success'):
        print(f"✅ Report generated - {result.get('report_path')}")
    else:
        print(f"❌ Report generation failed: {result.get('error')}")

    # Summary
    print("\n" + "="*60)
    print("🎉 FULL AUTOMATION COMPLETE")
    print("="*60)

    for task_name, result in results:
        status = "✅ Success" if result.get('success') else "❌ Failed"
        print(f"   {task_name}: {status}")

    print("\n   All reports saved to: results/ directory")


def main():
    """Main interactive interface."""
    print_banner()

    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nTo run this agent:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'")
        print("   python run-unified-agent.py")
        sys.exit(1)

    # Initialize agent
    print("🔧 Initializing agent...")
    try:
        agent = UnifiedAgent()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        sys.exit(1)

    # Main loop
    while True:
        print_menu()
        choice = input("Select option [1-6]: ").strip()

        if choice == '1':
            run_qa_tests(agent)
        elif choice == '2':
            run_error_monitoring(agent)
        elif choice == '3':
            run_document_conversion(agent)
        elif choice == '4':
            generate_report(agent)
        elif choice == '5':
            run_all_tasks(agent)
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-6.")

        input("\n   Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
