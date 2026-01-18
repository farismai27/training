# Quick Start

Get up and running with OCAA in 5 minutes.

## 🚀 Fastest Path to Success

### Step 1: Install (30 seconds)
```bash
pip install streamlit anthropic
```

### Step 2: Set API Key (10 seconds)
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Step 3: Launch (10 seconds)
```bash
streamlit run ocaa_web_ui.py
```

### Step 4: Start Chatting (4 minutes)
Open http://localhost:8501 and try these examples!

---

## Your First Conversations

### Example 1: Product Strategy
**Try this prompt:**
```
Write a user story for implementing real-time notifications
in OneSuite Core. Include acceptance criteria and impact
analysis for all channels (Search, Social, Programmatic, Commerce).
```

**What you'll get:**
- Structured user story format
- Clear acceptance criteria
- Multi-channel impact analysis
- Dependencies and constraints
- Technical considerations

**Expected time:** ~30 seconds

---

### Example 2: RAG Search
**Click:** "Quick Actions" → "Generate Product Roadmap"

OR type:
```
Show me how hybrid search works. Search the knowledge base
for information about OneSuite user stories.
```

**What you'll get:**
- Semantic + lexical search results
- Re-ranked results using Claude
- Relevant excerpts from knowledge base
- Source citations

**Expected time:** ~10 seconds

---

### Example 3: QA Testing
**Try this prompt:**
```
I need to test the @mention component at http://localhost:8000.
Can you help me run automated QA tests?
```

**What you'll get:**
- Automated screenshot capture
- Interaction testing
- Visual validation
- PASS/FAIL report

**Expected time:** ~1 minute

> **Note:** Requires Computer Use dependencies: `pip install pillow pyautogui`

---

### Example 4: Error Analysis
**Try this prompt:**
```
Analyze this error and suggest a fix:

TypeError: Cannot read property 'id' of undefined
  at getUserData (user-service.js:45)
  at async loadUserProfile (profile.js:12)
```

**What you'll get:**
- Root cause analysis
- Code fix with explanation
- Prevention strategy
- Best practices recommendation

**Expected time:** ~20 seconds

---

## Understanding the Interface

### Web UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 OCAA - OneSuite Core Architect Agent                    │
│ Unified AI Agent for Product Strategy, QA, Monitoring...   │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────────────────────────────────┐
│  Sidebar     │  │  Chat Area                               │
│              │  │                                          │
│ ⚙️ Config    │  │  💬 Chat with OCAA                      │
│ • API Key    │  │  ┌─────────────────────────────────┐   │
│              │  │  │ 🤖 OCAA: Hello! I am the...     │   │
│ 📊 Status    │  │  └─────────────────────────────────┘   │
│ • API: ✅    │  │                                          │
│ • Computer: ❌│  │  ┌─────────────────────────────────┐   │
│              │  │  │ 👤 You: Write a user story...   │   │
│ 🎯 Quick     │  │  └─────────────────────────────────┘   │
│   Actions    │  │                                          │
│ • Roadmap    │  │  ┌─────────────────────────────────┐   │
│ • User Story │  │  │ 🤖 OCAA: Here's a user story... │   │
│ • QA Test    │  │  └─────────────────────────────────┘   │
│ • Error Fix  │  │                                          │
│              │  │  ┌──────────────────────────────────┐  │
│ 🔧 Settings  │  │  │ Type your message...             │  │
│ • Max Tokens │  │  └──────────────────────────────────┘  │
│ • Model      │  └──────────────────────────────────────────┘
│              │
│ 🗑️ Clear    │
│ 💾 Export    │
└──────────────┘
```

### Key UI Elements

1. **Chat Area** - Main conversation interface
2. **Sidebar → API Key** - Configure your Anthropic API key
3. **Sidebar → Quick Actions** - Pre-built prompts for common tasks
4. **Sidebar → Settings** - Adjust model and response length
5. **Chat Input** - Type your questions and requests

---

## Quick Actions Explained

The sidebar contains pre-built prompts for common tasks:

### 📝 Generate Product Roadmap
Creates a comprehensive Q2 2026 roadmap with MVP, V1, and Scale phases.

**When to use:** Starting new features, quarterly planning

### ✍️ Write User Story
Generates a user story with acceptance criteria for advanced search.

**When to use:** Feature development, requirements gathering

### 🧪 QA Test @Mention
Runs automated tests on the @mention component.

**When to use:** Component testing, QA validation

**Requires:** Computer Use dependencies

### 🐛 Analyze Error
Analyzes a production error and suggests fixes.

**When to use:** Debugging, error investigation

### 🔄 Workflow Demo
Demonstrates the Evaluator-Optimizer pattern.

**When to use:** Learning workflows, quality improvement

---

## CLI Quick Start (Alternative)

Prefer command-line interfaces?

### Unified Agent
```bash
python src/demo_unified.py
```

**Try these commands:**
```
/hybrid-demo       # RAG search demonstration
/rerank-demo       # Re-ranking demonstration
/qa-test           # QA testing
/workflow-demo     # Evaluator-Optimizer pattern
/full-automation   # Run everything!
```

### Original RAG Agent
```bash
python src/demo.py
```

**Try these commands:**
```
/rag-demo          # Full RAG pipeline
/contextual-demo   # Contextual retrieval
/hybrid-demo       # Hybrid search
/rerank-demo       # Re-ranking
```

---

## Common Workflows

### Workflow 1: Write a Feature Spec
```
1. Open OCAA Web UI
2. Type: "Write a user story for [feature]"
3. Review the generated story
4. Ask: "Add more details to acceptance criteria"
5. Export conversation for documentation
```

### Workflow 2: Test a Component
```
1. Start the component locally (e.g., http://localhost:8000)
2. Click "QA Test @Mention" in Quick Actions
3. Review test results
4. Fix any failures
5. Re-run tests
```

### Workflow 3: Debug an Error
```
1. Copy error message and stack trace
2. Type: "Analyze this error: [paste error]"
3. Review root cause analysis
4. Implement suggested fix
5. Ask: "How can I prevent this in the future?"
```

### Workflow 4: Search Knowledge Base
```
1. Type: "Search for [topic] in the knowledge base"
2. Review hybrid search results
3. Ask follow-up questions about results
4. Export relevant information
```

---

## Tips for Best Results

### ✅ Do's

- **Be specific** - "Write a user story for real-time notifications with WebSocket support"
- **Provide context** - Mention which OneSuite channel (Search, Social, etc.)
- **Ask follow-ups** - "Add more technical details" or "Simplify this explanation"
- **Use Quick Actions** - Fast way to get started with common tasks
- **Review history** - Scroll up to see previous responses

### ❌ Don'ts

- **Don't be vague** - "Write something" → What specifically?
- **Don't skip context** - OCAA works better with domain context
- **Don't ignore errors** - If something fails, paste the error message
- **Don't restart unnecessarily** - Conversation history provides context

---

## Next Steps

You've completed the Quick Start! Here's what to explore next:

### For Product Managers
→ [Product Strategy Features](../03-features/agents/unified-agent.md)
- User story generation
- Roadmap planning
- Acceptance criteria

### For Developers
→ [Architecture Overview](../02-architecture/overview.md)
- System design
- Code patterns
- Integration guides

### For QA Engineers
→ [Computer Use Guide](../03-features/agents/computer-use.md)
- Automated testing
- Visual validation
- Test report generation

### For DevOps
→ [Production Monitoring](../03-features/agents/production-monitor.md)
- Error monitoring
- Auto-fix generation
- Log analysis

---

## Troubleshooting Quick Start Issues

### UI won't load
```bash
# Check if Streamlit is running
ps aux | grep streamlit

# Restart
pkill streamlit
streamlit run ocaa_web_ui.py
```

### API errors
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Test API key
python -c "import anthropic; print(anthropic.Anthropic(api_key='$ANTHROPIC_API_KEY').models.list())"
```

### Chat not responding
1. Check sidebar: API status should be "✅ Connected"
2. Verify API key is entered
3. Check browser console for errors (F12)
4. Restart Streamlit

---

## Resources

- **Full Setup Guide**: [Setup Guide](./setup-guide.md)
- **Project Overview**: [Project Overview](./project-overview.md)
- **Common Tasks**: [Common Tasks](./common-tasks.md)
- **API Reference**: [Claude API](../05-api/claude-api.md)

---

**Time to complete:** 5 minutes
**Prerequisites:** Python, API key
**Next:** [Common Tasks](./common-tasks.md)
