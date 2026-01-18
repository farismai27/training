# Claude Computer Use

**Automate QA testing, web scraping, and UI workflows with AI that can see and control your computer!**

## 🎯 What is Computer Use?

Claude's Computer Use feature allows Claude to:
- 👀 **See your screen** via screenshots
- 🖱️ **Control your mouse** (click, drag, move)
- ⌨️ **Type on keyboard** (text, shortcuts, keys)
- 🌐 **Navigate applications** (browsers, desktop apps)
- 🤖 **Automate workflows** (testing, data entry, research)

It's like having Claude operate your computer through a virtual desktop!

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key
- Linux/Mac (Windows requires WSL)

### 1. Set Up API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### 2. Run Quick Start

```bash
cd computer-use
./quick-start.sh
```

This will:
- ✅ Install dependencies
- ✅ Start test server
- ✅ Open test app in browser
- ✅ Prepare for testing

### 3. Run Automated QA Tests

```bash
cd scripts
python3 qa_test_mention_component.py
```

Watch Claude automatically test the @mention component and generate a report!

## 📁 Project Structure

```
computer-use/
├── docker/
│   ├── Dockerfile                        # Container for isolated testing
│   └── requirements-computer-use.txt     # Python dependencies
├── scripts/
│   ├── computer_use_client.py            # Main Computer Use client
│   └── qa_test_mention_component.py      # Automated QA example
├── test-app/
│   ├── index.html                        # @Mention test component
│   └── server.py                         # Simple HTTP server
├── results/                              # Test reports (generated)
├── docker-compose.yml                    # Docker orchestration
└── quick-start.sh                        # Quick setup script
```

## 🎓 The Lesson Example

### The Problem

You have a web component with an @mention feature that has bugs:
- Works fine initially
- But with 2+ mentions, pressing Backspace → autocomplete appears in wrong location (top-left instead of under cursor)
- Manually testing all edge cases takes 30-60 minutes 😫

### The Solution

Use Claude Computer Use to automate QA testing:

```python
from computer_use_client import ComputerUseClient

client = ComputerUseClient()

# Give Claude the testing task
task = """
Test the @mention component at http://localhost:8000

Test Cases:
1. Verify autocomplete appears when typing @
2. Verify Enter inserts mention
3. Verify Backspace with multiple mentions (check position!)
4. Verify Escape closes autocomplete
5. Verify arrow keys navigate

Generate a QA report with results.
"""

# Claude automatically:
# - Opens browser
# - Navigates to site
# - Runs each test
# - Documents results
# - Reports: Test 1 ✅, Test 2 ✅, Test 3 ❌ (bug found!)

responses = client.run_task(task)
```

### Result

- **Manual testing**: 30-60 minutes
- **Computer Use**: 2-3 minutes
- **Savings**: ~90% faster! ⚡

## 💡 How It Works

### Architecture

```
Your Prompt ("Test this component...")
    ↓
Claude API receives task
    ↓
Takes screenshot of screen
    ↓
Analyzes what's visible (OCR, element detection)
    ↓
Decides next action (click here at x,y, type this text)
    ↓
Executes action via Computer Use tools
    ↓
Takes new screenshot
    ↓
Evaluates result
    ↓
Repeat until task complete
    ↓
Returns report
```

### Key Technologies

1. **Screenshot Analysis**: Claude "sees" your screen
2. **Computer Tools API**: mouse_move, click, type, key, scroll
3. **Action Planning**: Claude decides optimal sequence
4. **Feedback Loop**: Verifies actions worked
5. **Error Recovery**: Handles failures gracefully

## 🎯 Real-World Use Cases

### 1. **Automated QA Testing** (Lesson Example)

Test UI components automatically:

```python
task = """
Test the login form at http://localhost:3000/login

Tests:
1. Submit with empty fields → show errors
2. Submit with invalid email → show error
3. Submit with valid credentials → redirect to dashboard
4. Test "Remember me" checkbox
5. Test "Forgot password" link

Generate report.
"""

client.run_task(task)
```

### 2. **Web Scraping**

Extract data from complex websites:

```python
task = """
Navigate to https://example.com/products
1. Scroll through all pages
2. Extract product names, prices, ratings
3. Save to CSV file
"""

client.run_task(task)
```

### 3. **Data Entry Automation**

Fill forms across multiple systems:

```python
task = """
1. Open CRM at https://crm.company.com
2. Click "Add Contact"
3. Fill in: Name, Email, Phone, Company
4. Click Save
5. Repeat for 10 contacts from contacts.csv
"""

client.run_task(task)
```

### 4. **Integration Testing**

Test multi-step user workflows:

```python
task = """
Test e-commerce checkout flow:
1. Add 3 items to cart
2. Proceed to checkout
3. Fill shipping information
4. Select payment method
5. Review order
6. Confirm (don't actually submit)
7. Screenshot each step
8. Report any issues
"""

client.run_task(task)
```

### 5. **Documentation Screenshots**

Generate documentation automatically:

```python
task = """
Create tutorial screenshots for our app:
1. Go to dashboard
2. Click "New Project" → screenshot
3. Fill project form → screenshot
4. Click "Settings" → screenshot
5. Configure options → screenshot
Save all screenshots with descriptive names
"""

client.run_task(task)
```

## 🎮 Interactive Demo

### Test the @Mention Component

1. **Start the test server:**
   ```bash
   cd test-app
   python3 server.py
   ```

2. **Open in browser:**
   ```
   http://localhost:8000
   ```

3. **Manual testing:**
   - Type `@` → Autocomplete appears ✅
   - Press Enter → Mention inserted ✅
   - Type `@john @jane` then Backspace → Bug! Autocomplete in wrong spot ❌

4. **Automated testing:**
   ```bash
   cd scripts
   python3 qa_test_mention_component.py
   ```

Watch Claude find the bugs automatically!

## 📊 Computer Use API

### Available Actions

#### Mouse Actions

```python
# Move mouse
{'type': 'mouse_move', 'x': 100, 'y': 200}

# Click
{'type': 'click', 'x': 100, 'y': 200, 'button': 'left'}

# Double click
{'type': 'double_click', 'x': 100, 'y': 200}

# Scroll
{'type': 'scroll', 'amount': -3}  # Negative = up, Positive = down
```

#### Keyboard Actions

```python
# Type text
{'type': 'type', 'text': 'Hello, world!'}

# Press key
{'type': 'key', 'key': 'Enter'}
{'type': 'key', 'key': 'Escape'}
{'type': 'key', 'key': 'Backspace'}

# Hotkey combination
{'type': 'hotkey', 'keys': ['ctrl', 'c']}
{'type': 'hotkey', 'keys': ['cmd', 'v']}
```

#### Utility Actions

```python
# Take screenshot
{'type': 'screenshot'}

# Wait
{'type': 'wait', 'duration': 2.0}
```

## 🔧 Custom Tasks

### Create Your Own Tests

```python
from computer_use_client import ComputerUseClient

client = ComputerUseClient()

# Test your MCP server
task = """
Test the MCP document conversion tool:
1. Open http://localhost:3000/demo
2. Click "Upload Document"
3. Select a PDF file
4. Click "Convert to Markdown"
5. Verify markdown output appears
6. Download result
7. Check file is valid markdown
"""

responses = client.run_task(task, max_iterations=20)
```

### Browser Automation

```python
task = """
Research and compile information:
1. Go to Google
2. Search for "Python asyncio tutorial"
3. Open top 5 results
4. For each: extract main points
5. Compile summary in results.txt
"""

client.run_task(task)
```

### Desktop Application Testing

```python
task = """
Test VS Code:
1. Open VS Code
2. Create new file
3. Type "Hello, world!"
4. Save as hello.py
5. Run with Python
6. Verify output
7. Screenshot result
"""

client.run_task(task)
```

## 🐳 Docker Setup (Advanced)

For isolated, reproducible testing environment:

### Build and Run

```bash
# Build image
docker-compose build

# Start container
docker-compose up

# Access via VNC
# Open browser: http://localhost:6080
```

### Benefits

- ✅ Isolated from main system
- ✅ Reproducible environment
- ✅ Safe for testing
- ✅ Easy to reset

### Configuration

Edit `docker-compose.yml`:

```yaml
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  - DISPLAY=:99
  - RESOLUTION=1920x1080x24
```

## 🔐 Safety & Best Practices

### Safety Features

1. **PyAutoGUI Fail-Safe**: Move mouse to corner → abort
2. **Docker Isolation**: Test in container, not main system
3. **Action Confirmation**: Claude explains each action
4. **Error Recovery**: Handles failures gracefully

### Best Practices

#### DO ✅

- Test in isolated environments (Docker, VM)
- Start with simple tasks
- Use clear, specific instructions
- Review actions before running
- Set reasonable iteration limits
- Keep API key secure

#### DON'T ❌

- Run on production systems without testing
- Give access to sensitive data
- Use vague task descriptions
- Run indefinitely (set max_iterations)
- Share API keys
- Execute untrusted code

### Task Description Tips

**Good Task Description:**
```python
task = """
Test login form:
1. Navigate to http://localhost:3000/login
2. Enter email: test@example.com
3. Enter password: testpass123
4. Click "Login" button
5. Verify redirect to /dashboard
6. Screenshot result
"""
```

**Bad Task Description:**
```python
task = "Test the login"  # Too vague!
```

## 📈 Performance Optimization

### Reduce API Calls

```python
# Instead of many small screenshots
task = "Take a screenshot, then perform all 10 tests"

# Better than
task = "Take screenshot, test 1. Take screenshot, test 2..."
```

### Use Specific Coordinates

```python
# More efficient
task = "Click the Submit button at approximately (800, 400)"

# Less efficient
task = "Find and click the Submit button somewhere on the page"
```

### Batch Similar Actions

```python
# Efficient
task = "Fill all form fields: name, email, phone, then submit"

# Inefficient
task = "Fill name. Take screenshot. Fill email. Take screenshot..."
```

## 🎓 Learning Path

### Beginner

1. ✅ Run quick-start.sh
2. ✅ Test the @mention component manually
3. ✅ Run automated QA test script
4. ✅ Review generated report

### Intermediate

1. ✅ Modify QA test to add more test cases
2. ✅ Create test for your own web app
3. ✅ Build custom Computer Use tasks
4. ✅ Integrate with CI/CD

### Advanced

1. ✅ Set up Docker environment
2. ✅ Build multi-step automation workflows
3. ✅ Create reusable test suites
4. ✅ Implement screenshot diffing
5. ✅ Build visual regression testing

## 🛠️ Troubleshooting

### "Module not found: pyautogui"

```bash
pip install pyautogui pillow
```

### "Permission denied" on Linux

```bash
# Install X11 dependencies
sudo apt-get install python3-tk python3-dev
```

### "API key not set"

```bash
export ANTHROPIC_API_KEY='your-key'
# Or add to ~/.bashrc for persistence
```

### Actions not working

1. Check screen resolution matches Claude's expectations
2. Verify coordinates are correct
3. Add small delays between actions (`wait` action)
4. Check PyAutoGUI fail-safe isn't triggered

### Browser not opening

```bash
# Install browser
# Chrome/Chromium recommended
sudo apt-get install chromium-browser
```

## 📚 Resources

- **Anthropic Computer Use Docs**: https://docs.anthropic.com/computer-use
- **PyAutoGUI Docs**: https://pyautogui.readthedocs.io
- **Playwright Docs**: https://playwright.dev/python
- **Selenium Docs**: https://selenium-python.readthedocs.io

## 🎯 For Your MCP Server Project

Apply Computer Use to test your project:

### Test Document Conversion

```python
task = """
Test document_path_to_markdown tool:
1. Start MCP server
2. Call tool with test PDF
3. Verify markdown output
4. Test with Word doc
5. Test error cases (missing file, wrong format)
6. Generate test report
"""
```

### Test All MCP Tools

```python
task = """
Comprehensive MCP server test:
1. Start server: python start_document_server.py
2. List all tools
3. Test each tool with valid inputs
4. Test each tool with invalid inputs
5. Verify error messages
6. Check performance
7. Generate full QA report
"""
```

### Integration Testing

```python
task = """
Test full workflow:
1. Start MCP server
2. Connect via Claude Code
3. Upload test PDF
4. Convert to markdown
5. Verify output quality
6. Test with multiple files
7. Screenshot results
"""
```

## 🎉 Success Stories

### Before Computer Use

- **QA Testing**: 2 hours manual testing per release
- **Web Scraping**: Complex JavaScript sites required custom code
- **Data Entry**: Repetitive, error-prone manual work
- **Screenshots**: Manually capture, crop, name each one

### After Computer Use

- **QA Testing**: 5 minutes automated, comprehensive coverage
- **Web Scraping**: Natural language task → automated extraction
- **Data Entry**: Describe once, run repeatedly, error-free
- **Screenshots**: "Generate tutorial screenshots" → done!

**Time Savings**: ~85-95% on repetitive computer tasks! 🚀

## 🎊 Summary

You now have:

✅ **Computer Use client** - Control your computer with Claude
✅ **Test application** - @Mention component with intentional bugs
✅ **QA automation** - Automated testing scripts
✅ **Docker setup** - Isolated testing environment
✅ **Documentation** - Complete guides and examples

**Next Steps:**

1. Run `./quick-start.sh` to test it out
2. Watch Claude automatically test the component
3. Create your own Computer Use tasks
4. Apply to your MCP server testing

**Welcome to the future of QA automation!** 🤖

---

*Powered by Claude Sonnet 4 and Anthropic's Computer Use API*
