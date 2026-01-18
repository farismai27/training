# Anthropic Computer Use - Reference Implementation UI

**The EXACT interface from the lesson** - interact with Claude through a web UI and watch it control a virtual desktop in real-time!

---

## 🎯 What You Get

The reference implementation provides a **split-screen web interface**:

```
┌─────────────────────────────────────────────────────────────┐
│                    http://localhost:8080                     │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│    LEFT SIDE             │         RIGHT SIDE               │
│    Chat Interface        │     Virtual Desktop              │
│                          │                                  │
│  ┌────────────────────┐  │   ┌──────────────────────────┐  │
│  │ Type your message  │  │   │  [Browser Window]        │  │
│  │ to Claude here:    │  │   │                          │  │
│  │                    │  │   │  See Claude navigate,    │  │
│  │ "Test this login   │  │   │  type, click in          │  │
│  │  form at           │  │   │  real-time!              │  │
│  │  localhost:3000"   │  │   │                          │  │
│  │                    │  │   │  [Mouse cursor moves]    │  │
│  │  [Send]            │  │   │  [Claude types text]     │  │
│  └────────────────────┘  │   │  [Clicks buttons]        │  │
│                          │   └──────────────────────────┘  │
│  Claude's response:      │                                  │
│  "I'll test that form    │   Desktop resolution:            │
│   for you..."            │   1920x1080                      │
│                          │                                  │
│  [Action log showing     │   [Screenshot updates            │
│   what Claude is doing]  │    in real-time]                │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1: Using Launch Script (Easiest)

**Windows:**
```cmd
cd C:\Users\farismai2\coding\computer-use
set ANTHROPIC_API_KEY=your-key-here
launch-reference-ui.bat
```

**Mac/Linux:**
```bash
cd computer-use
export ANTHROPIC_API_KEY='your-key-here'
./launch-reference-ui.sh
```

**Then open**: http://localhost:8080

### Option 2: Using Docker Compose

```bash
cd computer-use
export ANTHROPIC_API_KEY='your-key-here'
docker-compose -f docker-compose-reference.yml up
```

**Then open**: http://localhost:8080

### Option 3: Manual Docker Command

```bash
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 8080:8080 -p 6080:6080 -p 5900:5900 -p 8501:8501 \
    -it ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
```

**Then open**: http://localhost:8080

---

## 🖥️ The Interface

### Left Side: Chat with Claude

This is where you interact with the agent:

**Input Field:**
- Type your instructions for Claude
- Can be simple: "Open Google"
- Or complex: "Test this entire form with 10 test cases"

**Chat History:**
- See your messages
- See Claude's responses
- Watch Claude explain what it's doing

**Action Log:**
- Real-time updates of Claude's actions
- "Moving mouse to (x, y)"
- "Clicking button"
- "Typing text: hello"
- "Taking screenshot"

### Right Side: Virtual Desktop

This is what Claude sees and controls:

**Browser Window:**
- Full Firefox browser
- Claude can navigate to any URL
- Claude can interact with any webpage
- You see everything Claude does

**Desktop Environment:**
- Full Linux desktop (Ubuntu)
- Claude can open applications
- Claude can use terminal
- Claude can manage files

**Real-Time Updates:**
- Screen refreshes as Claude works
- See mouse cursor move
- See text being typed
- See clicks happening

**Resolution:**
- Default: 1920x1080
- Configurable via environment variables

---

## 📝 Example Usage

### Example 1: Test a Login Form

**You type (left side):**
```
Test the login form at http://localhost:3000/login

Tests:
1. Try empty fields → verify error messages
2. Try invalid email → verify error
3. Try valid credentials → verify redirect
4. Screenshot each step
```

**Claude does (right side):**
```
1. Opens browser
2. Navigates to localhost:3000/login
3. Clicks email field
4. Types nothing
5. Clicks password field
6. Types nothing
7. Clicks "Login" button
8. Takes screenshot → sees error message ✅
9. Refreshes page
10. Types invalid email
11. Clicks "Login"
12. Takes screenshot → sees error ✅
... (continues for all tests)
```

**You see:**
- Left: Claude's narration of what it's doing
- Right: The actual browser with Claude working
- Real-time: Every mouse movement, every click, every keystroke

### Example 2: Web Scraping

**You type:**
```
Go to https://news.ycombinator.com
Extract the top 10 story titles
Save them to a text file
```

**Claude does:**
- Opens browser (you see it)
- Navigates to site (you watch)
- Scrolls through stories (you see cursor move)
- Reads each title (highlights elements)
- Opens text editor (you see desktop)
- Types the titles (you see text appear)
- Saves file (you see dialog)

### Example 3: QA Testing (Lesson Example)

**You type:**
```
Test the @mention component at http://localhost:8000

Test Cases:
1. Verify autocomplete appears when typing @
2. Verify Enter inserts mention
3. Verify Backspace with multiple mentions
4. Document any bugs found
```

**Claude does:**
- Navigates to site
- Types @ (you see it)
- Verifies dropdown appears
- Types @john (you watch)
- Presses Enter
- Adds another mention
- Presses Backspace
- **Sees bug!** Autocomplete in wrong position
- Takes screenshot of bug
- Documents findings

---

## 🎮 Interactive Features

### What You Can Do

**Send Commands:**
- Type anything in the chat
- Claude responds with actions
- Watch it happen in real-time

**Interrupt/Redirect:**
- Type new messages anytime
- Claude will adjust its approach
- You can course-correct mid-task

**Take Over:**
- Container allows VNC access
- You can control the desktop too
- Test alongside Claude

**Save Work:**
- Files saved in container
- Volume-mapped to your computer
- Persist between sessions

### What Claude Can Do

**Navigation:**
- Open URLs in browser
- Switch between tabs
- Use back/forward buttons
- Scroll pages

**Interaction:**
- Click any element
- Type in any field
- Fill forms
- Submit data

**Analysis:**
- Read text on screen
- Verify elements exist
- Check for errors
- Validate behavior

**Documentation:**
- Take screenshots
- Record findings
- Generate reports
- Save results

---

## 🔧 Configuration

### Environment Variables

Set before launching:

```bash
# Required
export ANTHROPIC_API_KEY='your-key'

# Optional
export WIDTH=1920          # Desktop width
export HEIGHT=1080         # Desktop height
```

### Ports

The container exposes multiple ports:

| Port | Purpose | Access |
|------|---------|--------|
| 8080 | **Main Web UI** | http://localhost:8080 |
| 6080 | noVNC (browser VNC) | http://localhost:6080 |
| 5900 | VNC server | VNC client → localhost:5900 |
| 8501 | Streamlit server | (internal) |

**Primary Access**: http://localhost:8080 (use this!)

### Storage

Files are persisted in:
```bash
~/.anthropic/         # On your computer
/home/computeruse/.anthropic/  # In container
```

---

## 🎯 Use Cases

### 1. QA Testing (Lesson Example)

Perfect for testing web applications:
- Test forms with multiple scenarios
- Verify error messages
- Check navigation flows
- Document bugs automatically

**Advantages:**
- See exactly what Claude sees
- Verify each step visually
- Catch UI bugs easily
- Screenshot evidence

### 2. Web Scraping

Extract data from websites:
- Navigate complex sites
- Handle JavaScript interactions
- Click through pagination
- Save extracted data

**Advantages:**
- Handle dynamic content
- Work with authenticated sites
- Debug scraping logic
- Visual verification

### 3. Integration Testing

Test complete user workflows:
- Multi-step processes
- Cross-application workflows
- End-to-end scenarios
- Real browser testing

**Advantages:**
- Test like real user
- Catch integration issues
- Visual regression testing
- Full workflow coverage

### 4. Documentation

Generate documentation automatically:
- Screenshot each step
- Record workflows
- Create tutorials
- Build knowledge base

**Advantages:**
- Always up-to-date screenshots
- Consistent documentation
- Automated updates
- Visual guides

### 5. Exploratory Testing

Let Claude explore your app:
- Find edge cases
- Discover bugs
- Test combinations
- Fuzzing UI

**Advantages:**
- AI-driven exploration
- Finds unexpected issues
- Thorough coverage
- Creative testing

---

## 🆚 Comparison: Reference UI vs Custom Client

| Feature | Reference UI | Custom Client |
|---------|-------------|---------------|
| **Interface** | ✅ Web browser | ❌ Command line |
| **Visual Feedback** | ✅ Real-time | ❌ No visual |
| **See Claude Work** | ✅ Yes! | ❌ No |
| **Split Screen** | ✅ Chat + Desktop | ❌ Text only |
| **Isolation** | ✅ Docker | ⚠️ Your computer |
| **Safety** | ✅ Contained | ⚠️ Direct access |
| **Setup** | ✅ One command | ⚠️ Manual config |
| **Demo Experience** | ✅ Exact match | ⚠️ Similar |
| **Learning** | ✅ Visual | ⚠️ Abstract |
| **Debugging** | ✅ Easy (see it) | ⚠️ Harder |

**Recommendation**: Use Reference UI for:
- Learning Computer Use
- Demo/presentation
- Visual verification
- Safe testing

Use Custom Client for:
- Production automation
- Scripting tasks
- CI/CD integration
- Custom workflows

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8080
# Windows:
netstat -ano | findstr :8080
taskkill /PID <pid> /F

# Mac/Linux:
lsof -ti:8080 | xargs kill -9
```

### Container Won't Start

```bash
# Remove old container
docker rm -f computer-use-demo

# Clear Docker cache
docker system prune -a

# Try again
./launch-reference-ui.sh
```

### Can't Access UI

1. **Check container is running:**
   ```bash
   docker ps | grep computer-use
   ```

2. **Check logs:**
   ```bash
   docker logs computer-use-demo
   ```

3. **Verify ports:**
   ```bash
   curl http://localhost:8080
   ```

4. **Restart container:**
   ```bash
   docker restart computer-use-demo
   ```

### Slow Performance

1. **Increase Docker resources:**
   - Docker Desktop → Settings → Resources
   - CPU: 4+ cores recommended
   - Memory: 8GB+ recommended

2. **Lower resolution:**
   ```bash
   export WIDTH=1280
   export HEIGHT=720
   ```

3. **Close other applications**

### API Key Issues

```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY  # Mac/Linux
echo %ANTHROPIC_API_KEY%  # Windows

# Test API key works
curl https://api.anthropic.com/v1/messages \
  -H "anthropic-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

---

## 📚 Advanced Features

### Custom Desktop Applications

Install additional software in container:

```bash
# Connect to running container
docker exec -it computer-use-demo bash

# Install software (as computeruse user)
sudo apt-get update
sudo apt-get install your-package
```

### VNC Access

Direct VNC connection for manual control:

```bash
# Use VNC client
# Connect to: localhost:5900
# Password: (usually none or 'vncpassword')

# Or use browser VNC:
# http://localhost:6080
```

### Persistent Storage

Mount additional volumes:

```yaml
volumes:
  - ~/.anthropic:/home/computeruse/.anthropic
  - ./my-data:/home/computeruse/data  # Add your own
  - ./screenshots:/home/computeruse/screenshots
```

### Custom Network

Access local services:

```yaml
network_mode: "host"  # Use host networking
```

Then Claude can access:
- localhost:3000 → Your test app
- localhost:8000 → Your @mention demo
- Any other local service

---

## 🎓 Learning Path

### Beginner (5 minutes)

1. ✅ Launch the UI
2. ✅ Type "Open Google"
3. ✅ Watch Claude navigate
4. ✅ Try "Search for Claude AI"

### Intermediate (15 minutes)

1. ✅ Test your @mention component
2. ✅ Ask Claude to fill a form
3. ✅ Have Claude take screenshots
4. ✅ Review action log

### Advanced (30 minutes)

1. ✅ Multi-step QA testing
2. ✅ Web scraping task
3. ✅ Integration test scenario
4. ✅ Custom test suite

### Expert (1 hour)

1. ✅ Connect to local apps
2. ✅ Custom desktop applications
3. ✅ Automated screenshot generation
4. ✅ CI/CD integration

---

## 🎉 What Makes This Special

### It's the Real Deal!

- ✅ **Official Anthropic implementation**
- ✅ **Same as the lesson demo**
- ✅ **Production-grade code**
- ✅ **Maintained by Anthropic**

### Visual Learning

- ✅ **See Claude think** (action log)
- ✅ **See Claude work** (desktop view)
- ✅ **Understand decisions** (narration)
- ✅ **Verify results** (screenshots)

### Safe Experimentation

- ✅ **Isolated environment** (Docker)
- ✅ **Can't harm your computer**
- ✅ **Easy to reset** (restart container)
- ✅ **Reproducible** (same every time)

### Professional Tool

- ✅ **Used by Anthropic team**
- ✅ **Actively maintained**
- ✅ **Well documented**
- ✅ **Community supported**

---

## 📖 Resources

### Official Links

- **GitHub Repo**: https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo
- **Anthropic Docs**: https://docs.anthropic.com/en/docs/build-with-claude/computer-use
- **API Reference**: https://docs.anthropic.com/en/api/computer-use

### Your Repository

- **Custom Client**: `scripts/computer_use_client.py`
- **Test App**: `test-app/index.html`
- **QA Scripts**: `scripts/qa_test_mention_component.py`

### Community

- **Anthropic Discord**: Support and examples
- **GitHub Issues**: Report bugs, request features
- **Examples**: Check the quickstarts repo

---

## ✅ Summary

**You now have BOTH implementations:**

1. **Custom Python Client**
   - For scripting and automation
   - Direct computer control
   - Production use

2. **Reference UI** ← NEW!
   - For learning and demo
   - Visual feedback
   - Safe testing
   - Exact lesson experience

**Get started now:**

```bash
cd computer-use
export ANTHROPIC_API_KEY='your-key'
./launch-reference-ui.sh

# Then open: http://localhost:8080
# Type: "Navigate to google.com"
# Watch Claude work!
```

**This is the interface from the lesson** - split screen, chat on left, desktop on right, watch Claude control the computer in real-time! 🎉

---

*Built by Anthropic | Official Reference Implementation*
