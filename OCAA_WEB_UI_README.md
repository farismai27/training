# OCAA Web UI - Quick Start Guide

## 🎉 Custom Web Interface for OneSuite Core Architect Agent

The OCAA Web UI is a beautiful, custom Streamlit interface with the OCAA system prompt **built-in**. No Docker, no pasting context - just launch and chat!

---

## ✨ Features

- ✅ **OCAA System Prompt Built-in** - No manual setup needed!
- ✅ **OneSuite Branding** - Professional UI with branded colors
- ✅ **Quick Action Buttons** - Generate roadmaps, user stories, test apps with one click
- ✅ **Computer Use Ready** - QA testing capabilities integrated
- ✅ **Conversation History** - Full context preserved across the session
- ✅ **Export Conversations** - Download as JSON
- ✅ **Native Windows** - No Docker required
- ✅ **Real-time Status** - See Computer Use and API connection status
- ✅ **Multi-Model Support** - Choose between Sonnet, Opus

---

## 🚀 Quick Start (3 Steps!)

### Step 1: Install Dependencies

```powershell
# On your Windows machine:
cd C:\Users\farismai2\coding\training
git pull origin claude/import-vs-workspace-kobAs

# Install requirements
pip install -r requirements_ocaa_ui.txt
```

### Step 2: Set API Key

```powershell
# Option A: Set in environment (recommended)
$env:ANTHROPIC_API_KEY = "your-api-key-here"

# Option B: Enter in the UI (you'll be prompted)
```

### Step 3: Launch!

```powershell
# Windows
.\launch_ocaa_ui.bat

# Or manually:
streamlit run ocaa_web_ui.py
```

**That's it!** Your browser will open to http://localhost:8501

---

## 🎨 Interface Overview

```
┌──────────────────────────────────────────────────────────┐
│  🤖 OCAA - OneSuite Core Architect Agent                │
│  Unified AI Agent for Product Strategy, QA, Errors...   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [Sidebar]              [Main Chat Area]                │
│                                                          │
│  ⚙️ Configuration        🤖 OCAA: Hello! I am OCAA...  │
│  [API Key Input]                                        │
│                         👤 You: Generate a roadmap      │
│  📊 Status                                              │
│  Computer Use: ✅        🤖 OCAA: Here's your roadmap:  │
│  API: Connected                                         │
│                         [Product strategy response...]  │
│  🎯 Quick Actions                                       │
│  [Generate Roadmap]     [Chat continues...]            │
│  [Write User Story]                                     │
│  [QA Test]              [Type your message...]          │
│  [Analyze Error]                                        │
│  [Workflow Demo]                                        │
│                                                          │
│  🔧 Settings                                            │
│  Max Tokens: [2000]                                     │
│  Model: [Sonnet 4]                                      │
│                                                          │
│  [Clear Conversation]                                   │
│  [Export Conversation]                                  │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Actions Explained

### 📝 Generate Product Roadmap
**What it does:** Asks OCAA to generate a comprehensive Q2 2026 roadmap with MVP, V1, and Scale phases

**Example output:**
```
OCAA: Here's your OneSuite Core Product Roadmap:

**Month 1-2: Foundation & Unification**
- Audit current flows across Search, Social, Programmatic, Commerce
- Create unified agency profile initialization
...

**Channel Impact:**
- Search: Enhanced discovery algorithms
- Social: Unified engagement metrics
...
```

### ✍️ Write User Story
**What it does:** Generates a user story with acceptance criteria and multi-channel impact

**Example output:**
```
OCAA: **User Story:** Implement Advanced Search Filtering

**As a** Search channel manager,
**I want to** enable users to filter results by date range and budget,
**So that** they can refine results with precision.

**Acceptance Criteria:**
- Filter functionality available in all channels
- Uses shared taxonomy from OneSuite glossary
...

**Channel Impact:**
- Search: Enables refinement of organic results
- Social: Allows filtering by engagement metrics
...
```

### 🧪 QA Test @Mention
**What it does:** Prepares OCAA to test the @mention component

**What happens:**
```
OCAA: I'll help you test the @mention component. Based on your description,
I understand it should:
1. Show autocomplete when typing '@'
2. Insert mentions on Enter
3. Handle multiple mentions
4. Respond to Escape key

To execute these tests with Computer Use, I would:
[Detailed test plan...]

Would you like me to proceed with automated testing?
```

### 🐛 Analyze Error
**What it does:** Analyzes a production error and generates a fix

**Example output:**
```
OCAA: **Error Analysis:**

**Root Cause:**
The error "Cannot read property 'id' of undefined" indicates that code
is trying to access the 'id' property on an object that is undefined or null.

**Proposed Fix:**
```javascript
// Before (causes error):
const userId = user.id;

// After (defensive check):
const userId = user?.id || null;
```

**Prevention:**
- Add null checks before property access
- Use optional chaining (?.)
- Validate data at API boundaries
```

### 🔄 Workflow Demo
**What it does:** Demonstrates the Evaluator-Optimizer pattern

**Example output:**
```
OCAA: I'll demonstrate the Evaluator-Optimizer workflow:

**Iteration 1:**
Producer: [Generates initial document]
Grader: "FAIL - Missing Scale phase and under word count"

**Iteration 2:**
Producer: [Generates improved version with feedback]
Grader: "PASS - All criteria met"

**Result:** High-quality output achieved in 2 iterations
[Shows final output]
```

---

## 💬 Chat Examples

### Product Strategy
```
You: Generate a user story for implementing notifications

OCAA: **User Story:** Implement Multi-Channel Notifications

**As a** OneSuite user,
**I want to** receive consistent notifications across all channels,
**So that** I can stay informed regardless of which platform I'm using.

**Acceptance Criteria:**
- Notifications work in Search, Social, Programmatic, Commerce
- Uses shared notification taxonomy
- Real-time delivery within 5 seconds
- User can configure preferences per channel
- History preserved for 90 days

**Channel Impact:**
- Search: Alerts for ranking changes and optimization opportunities
- Social: Engagement notifications and performance updates
- Programmatic: Bid adjustments and budget alerts
- Commerce: Inventory updates and sales notifications
...
```

### Error Analysis
```
You: I'm getting "CORS policy blocked" error when calling our API

OCAA: **Error Analysis:**

**Root Cause:**
CORS (Cross-Origin Resource Sharing) errors occur when your frontend
tries to make requests to an API on a different origin (domain, protocol,
or port) and the server doesn't include proper CORS headers.

**Proposed Fix:**

**Backend (Node.js/Express):**
```javascript
const cors = require('cors');

app.use(cors({
  origin: ['http://localhost:3000', 'https://yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE']
}));
```

**OR for specific endpoints:**
```javascript
app.get('/api/data', (req, res) => {
  res.header('Access-Control-Allow-Origin', 'http://localhost:3000');
  res.header('Access-Control-Allow-Credentials', 'true');
  res.json(data);
});
```

**Prevention:**
- Configure CORS properly in backend during development
- Use environment variables for allowed origins
- Consider using a proxy in development
- Document CORS requirements for frontend team
```

### QA Testing Request
```
You: Can you help me test the login form at http://localhost:3000?

OCAA: I'd be happy to help test your login form! Here's my testing plan:

**Test Cases:**
1. **Valid Login**
   - Enter valid credentials
   - Click login button
   - Verify redirect to dashboard

2. **Invalid Credentials**
   - Enter wrong password
   - Verify error message appears
   - Verify stays on login page

3. **Empty Fields**
   - Try submitting with empty email
   - Try submitting with empty password
   - Verify validation errors

4. **Remember Me**
   - Check "Remember me"
   - Login successfully
   - Close and reopen browser
   - Verify still logged in

5. **Forgot Password Link**
   - Click "Forgot password"
   - Verify redirects to password reset

**With Computer Use enabled, I can:**
- Take screenshots at each step
- Automatically click and type
- Verify UI elements appear/disappear
- Generate detailed test report

Would you like me to proceed with automated testing?
```

---

## ⚙️ Configuration

### API Key Options

**Option 1: Environment Variable (Recommended)**
```powershell
# Windows (permanent)
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"

# Windows (session only)
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# Linux/Mac
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

**Option 2: In the UI**
- Enter in the sidebar "Anthropic API Key" field
- Stored for the session only

### Model Selection

Choose from:
- **Claude Sonnet 4** (Default) - Best balance of speed and quality
- **Claude Opus 4** - Maximum quality for complex tasks
- **Claude 3.5 Sonnet** - Legacy model

### Max Tokens

Adjust based on response length needed:
- **500-1000** - Quick answers
- **2000** (Default) - Standard responses
- **4096** - Long-form content (roadmaps, detailed analysis)

---

## 🔧 Troubleshooting

### Error: "Please configure your API key"

**Solution:** Enter your API key in the sidebar or set environment variable

### Error: "Computer Use not available"

**Cause:** PyAutoGUI not installed

**Solution:**
```powershell
pip install pillow pyautogui
```

### UI doesn't open automatically

**Solution:** Manually open http://localhost:8501 in your browser

### Port 8501 already in use

**Solution:** Kill existing Streamlit process or use different port:
```powershell
streamlit run ocaa_web_ui.py --server.port 8502
```

### Conversation history lost on refresh

**Cause:** Browser refresh clears session state

**Solution:** Use "Export Conversation" button before refreshing

---

## 📊 Comparison: Web UI vs Command Line

| Feature | Command Line (demo_unified.py) | Web UI (ocaa_web_ui.py) |
|---------|-------------------------------|-------------------------|
| **Setup** | Just run Python | Install Streamlit |
| **Interface** | Text-based terminal | Beautiful web UI |
| **System Prompt** | Built-in | Built-in ✅ |
| **Quick Actions** | Commands like `/qa-test` | Buttons in sidebar |
| **Conversation** | Session-based | Persistent in UI |
| **Export** | Manual copy-paste | One-click JSON export |
| **Branding** | Plain text | OneSuite branded |
| **Best For** | Scripting, automation | Interactive use |

**Both are available!** Use whichever fits your workflow.

---

## 🎨 Customization

### Change Colors (OneSuite Branding)

Edit `ocaa_web_ui.py` around line 60:

```python
.main-header {
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    # Change these colors for custom branding
}
```

### Add New Quick Actions

Edit `ocaa_web_ui.py` around line 180:

```python
if st.button("🆕 Your Custom Action", key="custom_btn"):
    st.session_state.quick_action = "Your prompt here..."
```

### Change Initial Greeting

Edit `ocaa_web_ui.py` around line 120:

```python
st.session_state.messages.append({
    "role": "assistant",
    "content": "Your custom greeting..."
})
```

---

## 📈 Performance

- **Startup Time:** < 3 seconds
- **Response Time:** 2-10 seconds (depends on prompt complexity)
- **Memory Usage:** ~200-300 MB
- **Cost:** Same as API calls (~$0.01-0.05 per conversation)

---

## 🚀 Advanced Usage

### Run on Different Port

```powershell
streamlit run ocaa_web_ui.py --server.port 8502
```

### Run on Network (Access from other devices)

```powershell
streamlit run ocaa_web_ui.py --server.address 0.0.0.0
```

### Enable Auto-reload During Development

```powershell
streamlit run ocaa_web_ui.py --server.runOnSave true
```

---

## 📝 Example Workflows

### Morning Standup Workflow
1. Open OCAA Web UI
2. Click "Generate Product Roadmap"
3. Review today's priorities
4. Ask: "What should I focus on today for OneSuite?"
5. Export conversation for team sharing

### Bug Investigation Workflow
1. Click "Analyze Error"
2. Paste error message from logs
3. Get root cause analysis
4. Get proposed fix
5. Ask follow-up questions
6. Export for documentation

### QA Session Workflow
1. Start test server: `python test-app/server.py`
2. Click "QA Test @Mention"
3. OCAA provides test plan
4. Confirm to proceed
5. Watch test execution
6. Review results
7. Export test report

---

## 🎓 Tips & Tricks

### Tip 1: Use Quick Actions for Common Tasks
The sidebar buttons save time for frequent operations

### Tip 2: Ask Follow-up Questions
OCAA remembers conversation context - ask for clarification!

### Tip 3: Export Important Conversations
Use "Export Conversation" for documentation and team sharing

### Tip 4: Adjust Max Tokens for Response Length
Increase for detailed roadmaps, decrease for quick answers

### Tip 5: Refresh to Start Fresh
Clear conversation or refresh browser for new topic

---

## 🎉 Summary

**OCAA Web UI gives you:**

✅ **No Setup Required** - OCAA system prompt built-in
✅ **Beautiful Interface** - OneSuite branded web UI
✅ **Quick Actions** - Common tasks with one click
✅ **Native Windows** - No Docker, just Python
✅ **Full Capabilities** - Product strategy, QA, errors, workflows
✅ **Export & Share** - Download conversations as JSON

**Start chatting in 3 steps:**

```powershell
# 1. Pull code
git pull

# 2. Install
pip install -r requirements_ocaa_ui.txt

# 3. Launch
.\launch_ocaa_ui.bat
```

**Open http://localhost:8501 and start chatting with OCAA!** 🚀

---

## 📞 Support

- **Documentation:** See `UNIFIED_OCAA_GUIDE.md` for complete guide
- **Issues:** Check troubleshooting section above
- **Repository:** https://github.com/farismai27/training

**Happy strategizing with OCAA!** 🎊
