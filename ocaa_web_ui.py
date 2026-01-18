#!/usr/bin/env python3
"""
OCAA Web UI - OneSuite Core Architect Agent
Custom Streamlit interface with built-in OCAA system prompt and all capabilities

Features:
- OCAA system prompt built-in (no manual pasting!)
- Computer Use integration
- Product strategy, QA testing, error monitoring
- Conversation history
- Quick action buttons
- OneSuite branding

Usage:
    streamlit run ocaa_web_ui.py
"""

import streamlit as st
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
import base64
from io import BytesIO

# Try to import Computer Use dependencies
try:
    from PIL import Image
    import pyautogui
    COMPUTER_USE_AVAILABLE = True
except ImportError:
    COMPUTER_USE_AVAILABLE = False

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# OCAA System Prompt (Built-in!)
OCAA_SYSTEM_PROMPT = """
<identity>
You are the OneSuite Core Architect Agent (OCAA) - a unified multi-capability AI agent.

Your roles:
1. **Product Manager** - Product strategy and documentation for OneSuite Core
2. **QA Automation Specialist** - Automated testing using Computer Use
3. **Production Monitor** - Error analysis and automated bug fixing
4. **Workflow Architect** - Design and execute complex workflows

When asked who you are, introduce yourself clearly:
"I am the OneSuite Core Architect Agent (OCAA), a unified AI agent specializing in product strategy, QA automation, error monitoring, and workflow execution for the OneSuite Core platform."
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

3. **Production Error Monitoring**
   - Production log analysis and error detection
   - Root cause analysis for errors and exceptions
   - Automated fix generation with code suggestions
   - Prevention strategy recommendations

4. **Workflow Design & Execution**
   - Evaluator-Optimizer patterns (Producer → Grader → Feedback)
   - RAG pipelines (Retrieval → Re-ranking → Generation)
   - Multi-step automation workflows
   - Iterative refinement processes
</capabilities>

<instructions>
YOUR THINKING PROCESS:

**For Product Strategy Tasks:**
1. ANALYZE THE SCOPE - Identify affected channels (Search, Social, Programmatic, Commerce)
2. IDENTIFY STAKEHOLDERS - Determine who is impacted and their needs
3. ASSESS CURRENT STATE - What exists today? What are the gaps?
4. BRAINSTORM SOLUTIONS - Generate multiple approaches, evaluate trade-offs
5. STRUCTURE LOGICALLY - Organize findings into clear sections
6. VALIDATE CONSISTENCY - Ensure alignment across all channels

**For QA Testing Tasks:**
1. UNDERSTAND REQUIREMENTS - What needs to be tested?
2. TAKE SCREENSHOT - See current state of application
3. EXECUTE TESTS - Use computer actions to interact and validate
4. DOCUMENT RESULTS - Record PASS/FAIL with evidence
5. REPORT BUGS - Provide clear reproduction steps

**For Error Monitoring:**
1. ANALYZE ROOT CAUSE - Understand why the error occurred
2. GENERATE FIX - Provide code-level solution
3. EXPLAIN PREVENTION - How to avoid this in future
</instructions>

<response_format>
**For Product Strategy:**
- Context, Problem, Solution, Acceptance Criteria
- Channel Impact: Search, Social, Programmatic, Commerce
- Dependencies, Assumptions & Constraints

**For QA Testing:**
- Test Summary: Total, Passed, Failed
- Detailed Results with evidence
- Bugs Found with reproduction steps

**For Error Analysis:**
- Error Summary, Root Cause
- Proposed Fix with code
- Prevention strategy
</response_format>

<communication_style>
Professional, structured, and results-oriented. Precise for technical tasks, comprehensive for strategy.
</communication_style>
"""

# Page config
st.set_page_config(
    page_title="OCAA - OneSuite Core Architect Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for OneSuite branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        color: #e0e7ff;
        margin: 0.5rem 0 0 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        padding: 0.5rem;
        font-weight: 500;
    }
    .quick-action-btn {
        margin: 0.25rem 0;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .status-enabled {
        background: #10b981;
        color: white;
    }
    .status-disabled {
        background: #6b7280;
        color: white;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #f3f4f6;
        border-left: 4px solid #3b82f6;
    }
    .assistant-message {
        background: #eff6ff;
        border-left: 4px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add initial greeting
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am the OneSuite Core Architect Agent (OCAA), your unified AI agent for product strategy, QA automation, error monitoring, and workflow execution. How can I help you today?"
    })

if 'anthropic_client' not in st.session_state:
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        st.session_state.anthropic_client = Anthropic(api_key=api_key)
    else:
        st.session_state.anthropic_client = None

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 OCAA - OneSuite Core Architect Agent</h1>
    <p>Unified AI Agent for Product Strategy, QA Automation, Error Monitoring & Workflows</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key input
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get('ANTHROPIC_API_KEY', ''),
        help="Enter your Anthropic API key"
    )

    if api_key_input:
        os.environ['ANTHROPIC_API_KEY'] = api_key_input
        st.session_state.anthropic_client = Anthropic(api_key=api_key_input)
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ Please enter your API key")

    st.divider()

    # Status indicators
    st.header("📊 Status")

    computer_use_status = "Enabled" if COMPUTER_USE_AVAILABLE else "Disabled"
    computer_use_class = "status-enabled" if COMPUTER_USE_AVAILABLE else "status-disabled"

    st.markdown(f"""
    <div class="status-badge {computer_use_class}">
        Computer Use: {computer_use_status}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.anthropic_client:
        st.markdown('<div class="status-badge status-enabled">API: Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-disabled">API: Not Connected</div>', unsafe_allow_html=True)

    st.divider()

    # Quick Actions
    st.header("🎯 Quick Actions")

    if st.button("📝 Generate Product Roadmap", key="roadmap_btn"):
        st.session_state.quick_action = "Generate a comprehensive product roadmap for OneSuite Core Q2 2026, including MVP, V1, and Scale phases with multi-channel impact analysis."

    if st.button("✍️ Write User Story", key="story_btn"):
        st.session_state.quick_action = "Write a user story for implementing advanced search filtering in OneSuite with cross-channel consistency. Include acceptance criteria and channel impact analysis."

    if st.button("🧪 QA Test @Mention", key="qa_mention_btn"):
        st.session_state.quick_action = "I need to test the @mention component at http://localhost:8000. Can you help me run automated QA tests? The component should support typing '@', showing autocomplete, inserting mentions with Enter, and handling multiple mentions."

    if st.button("🐛 Analyze Error", key="error_btn"):
        st.session_state.quick_action = "I have a production error: TypeError: Cannot read property 'id' of undefined. Can you analyze the root cause and provide a fix?"

    if st.button("🔄 Workflow Demo", key="workflow_btn"):
        st.session_state.quick_action = "Demonstrate the Evaluator-Optimizer workflow pattern by writing a product requirement document. Show the Producer → Grader → Feedback loop."

    st.divider()

    # Settings
    st.header("🔧 Settings")

    max_tokens = st.slider(
        "Max Response Tokens",
        min_value=500,
        max_value=4096,
        value=2000,
        step=100,
        help="Maximum tokens for OCAA responses"
    )

    model = st.selectbox(
        "Model",
        ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-opus-4-20250514"],
        index=0,
        help="Claude model to use"
    )

    st.divider()

    # Conversation management
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Conversation cleared. How can I help you?"
        }]
        st.session_state.conversation_history = []
        st.rerun()

    if st.button("💾 Export Conversation"):
        # Create export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.messages
        }
        export_json = json.dumps(export_data, indent=2)
        st.download_button(
            label="Download JSON",
            data=export_json,
            file_name=f"ocaa_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    st.divider()

    # Info
    with st.expander("ℹ️ About OCAA"):
        st.markdown("""
        **OneSuite Core Architect Agent (OCAA)**

        A unified AI agent combining:
        - 🎯 Product Strategy & User Stories
        - 🧪 QA Testing & Automation
        - 🐛 Error Monitoring & Fixes
        - 🔄 Workflow Patterns
        - 📄 Document Management
        - 🔍 RAG Pipelines

        **Channels Supported:**
        - Search
        - Social
        - Programmatic
        - Commerce

        **Version:** 1.0.0
        **Model:** Claude Sonnet 4
        """)

# Main chat area
st.header("💬 Chat with OCAA")

# Display messages using Streamlit's native chat components
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle quick actions
if 'quick_action' in st.session_state:
    user_input = st.session_state.quick_action
    del st.session_state.quick_action

    # Add to messages
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Process with OCAA
    if st.session_state.anthropic_client:
        with st.spinner("🤖 OCAA is thinking..."):
            try:
                # Build conversation for API
                api_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] in ["user", "assistant"]:
                        api_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

                # Call Claude with OCAA system prompt
                response = st.session_state.anthropic_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=OCAA_SYSTEM_PROMPT,
                    messages=api_messages
                )

                assistant_message = response.content[0].text

                # Add to conversation
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Please configure your API key in the sidebar")
        st.rerun()

# Chat input
user_input = st.chat_input("Ask OCAA anything about OneSuite, or request QA testing, error analysis, or workflows...")

if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Get OCAA response
    if st.session_state.anthropic_client:
        with st.spinner("🤖 OCAA is thinking..."):
            try:
                # Build conversation for API
                api_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] in ["user", "assistant"]:
                        api_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

                # Call Claude with OCAA system prompt
                response = st.session_state.anthropic_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=OCAA_SYSTEM_PROMPT,
                    messages=api_messages
                )

                assistant_message = response.content[0].text

                # Add to conversation
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                st.rerun()

            except Exception as e:
                st.error(f"Error calling Claude API: {str(e)}")
    else:
        st.error("Please configure your API key in the sidebar")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.875rem; padding: 1rem;">
    <strong>OCAA v1.0</strong> | OneSuite Core Architect Agent |
    Powered by Claude Sonnet 4 |
    <a href="https://github.com/farismai27/training" target="_blank">Documentation</a>
</div>
""", unsafe_allow_html=True)
