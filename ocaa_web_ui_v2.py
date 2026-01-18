#!/usr/bin/env python3
"""
OCAA Web UI v2 - Enhanced with AI SDK Patterns
Following Vercel AI SDK best practices for AI chat interfaces

Features:
- Streaming responses with real-time display
- Tool use visualization
- Message artifacts
- Token usage tracking
- Loading states
- Error boundaries
- Conversation management
"""

import streamlit as st
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic, AnthropicError
from typing import List, Dict, Any, Optional

# Try to import Computer Use dependencies
try:
    from PIL import Image
    import pyautogui
    COMPUTER_USE_AVAILABLE = True
except ImportError:
    COMPUTER_USE_AVAILABLE = False

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# OCAA System Prompt
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
1. **Product Strategy** - User stories, roadmaps, multi-channel analysis
2. **QA Testing** - Automated UI/UX testing with screenshots
3. **Error Monitoring** - Log analysis, root cause, auto-fix generation
4. **Workflow Design** - Evaluator-Optimizer, RAG pipelines, automation
</capabilities>

<communication_style>
Professional, structured, and results-oriented. Use markdown formatting for clarity.
</communication_style>
"""

# Page config
st.set_page_config(
    page_title="OCAA v2 - OneSuite Core Architect Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with AI SDK patterns
st.markdown("""
<style>
    /* Main container */
    .main {
        background: #f8fafc;
    }

    /* Header */
    .ocaa-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .ocaa-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.25rem;
        font-weight: 700;
    }

    .ocaa-header p {
        color: #e0e7ff;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    .status-connected {
        background: #10b981;
        color: white;
    }

    .status-disconnected {
        background: #ef4444;
        color: white;
    }

    .status-partial {
        background: #f59e0b;
        color: white;
    }

    /* Message container */
    .message-container {
        margin: 1rem 0;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Tool use display */
    .tool-call {
        background: #f3f4f6;
        border-left: 4px solid #6366f1;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.9rem;
    }

    .tool-call-header {
        font-weight: 600;
        color: #6366f1;
        margin-bottom: 0.5rem;
    }

    .tool-result {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }

    /* Artifacts */
    .artifact {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }

    .artifact-header {
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Token usage */
    .token-usage {
        display: flex;
        gap: 1rem;
        padding: 0.75rem;
        background: #fef3c7;
        border-radius: 8px;
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }

    .token-usage-item {
        display: flex;
        gap: 0.25rem;
    }

    .token-usage-label {
        font-weight: 600;
        color: #92400e;
    }

    .token-usage-value {
        color: #78350f;
    }

    /* Loading animation */
    .loading-dots {
        display: inline-flex;
        gap: 0.25rem;
    }

    .loading-dots span {
        width: 0.5rem;
        height: 0.5rem;
        background: #3b82f6;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }

    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }

    /* Quick action button */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I am the **OneSuite Core Architect Agent (OCAA)**, your unified AI agent for:\n\n- 🎯 Product Strategy & User Stories\n- 🧪 QA Automation & Testing\n- 🐛 Error Monitoring & Fixes\n- 🔄 Workflow Design & Execution\n\nHow can I help you today?",
            "timestamp": datetime.now().isoformat()
        })

    if 'anthropic_client' not in st.session_state:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        st.session_state.anthropic_client = Anthropic(api_key=api_key) if api_key else None

    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = {'input': 0, 'output': 0}

    if 'streaming' not in st.session_state:
        st.session_state.streaming = False

init_session_state()

# Header
st.markdown("""
<div class="ocaa-header">
    <h1>🤖 OCAA v2</h1>
    <p>OneSuite Core Architect Agent • Enhanced with AI SDK Patterns</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get('ANTHROPIC_API_KEY', ''),
        help="Your Anthropic API key"
    )

    if api_key_input:
        os.environ['ANTHROPIC_API_KEY'] = api_key_input
        st.session_state.anthropic_client = Anthropic(api_key=api_key_input)
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ Please enter your API key")

    st.divider()

    # Status
    st.header("📊 System Status")

    # API status
    if st.session_state.anthropic_client:
        st.markdown('<div class="status-badge status-connected">🟢 API Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-disconnected">🔴 API Disconnected</div>', unsafe_allow_html=True)

    # Computer Use status
    if COMPUTER_USE_AVAILABLE:
        st.markdown('<div class="status-badge status-connected">🟢 Computer Use Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-partial">🟡 Computer Use Unavailable</div>', unsafe_allow_html=True)

    # Token usage
    if st.session_state.total_tokens['input'] > 0 or st.session_state.total_tokens['output'] > 0:
        st.markdown("### 📈 Token Usage")
        st.metric("Input Tokens", f"{st.session_state.total_tokens['input']:,}")
        st.metric("Output Tokens", f"{st.session_state.total_tokens['output']:,}")
        total = st.session_state.total_tokens['input'] + st.session_state.total_tokens['output']
        st.metric("Total", f"{total:,}")

    st.divider()

    # Quick Actions
    st.header("🎯 Quick Actions")

    quick_actions = {
        "📝 Product Roadmap": "Generate a comprehensive product roadmap for OneSuite Core Q2 2026, including MVP, V1, and Scale phases with multi-channel impact analysis.",
        "✍️ User Story": "Write a user story for implementing advanced search filtering in OneSuite with cross-channel consistency. Include acceptance criteria and channel impact analysis.",
        "🧪 QA Test": "I need to test the @mention component at http://localhost:8000. Run automated QA tests including typing '@', autocomplete validation, and mention insertion.",
        "🐛 Error Analysis": "Analyze this production error and provide a fix: TypeError: Cannot read property 'id' of undefined at getUserData (user-service.js:45)",
        "🔄 Workflow Demo": "Demonstrate the Evaluator-Optimizer workflow pattern by writing a product requirement document with iterative quality improvement.",
    }

    for label, prompt in quick_actions.items():
        if st.button(label, key=f"qa_{label}"):
            st.session_state.quick_action = prompt

    st.divider()

    # Settings
    st.header("🔧 Settings")

    model = st.selectbox(
        "Model",
        [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-opus-4-20250514"
        ],
        index=0,
        help="Claude model to use"
    )

    max_tokens = st.slider(
        "Max Response Tokens",
        min_value=500,
        max_value=8192,
        value=4096,
        step=256,
        help="Maximum tokens for responses"
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.1,
        help="Randomness in responses (0 = deterministic, 1 = creative)"
    )

    stream_responses = st.checkbox(
        "Stream Responses",
        value=True,
        help="Show responses as they're generated"
    )

    st.divider()

    # Conversation Management
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.total_tokens = {'input': 0, 'output': 0}
            st.rerun()

    with col2:
        if st.button("💾 Export", use_container_width=True):
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages,
                "total_tokens": st.session_state.total_tokens
            }
            st.download_button(
                label="Download",
                data=json.dumps(export_data, indent=2),
                file_name=f"ocaa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    st.divider()

    # Info
    with st.expander("ℹ️ About"):
        st.markdown("""
        **OCAA v2.0** - Enhanced with AI SDK Patterns

        **New Features:**
        - ✨ Streaming responses
        - 🛠️ Tool use visualization
        - 📦 Message artifacts
        - 📊 Token tracking
        - ⚡ Better error handling

        **Channels:** Search, Social, Programmatic, Commerce

        **Model:** Claude Sonnet 4
        """)

# Main chat area
st.header("💬 Conversation")

# Display messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show metadata if available
        if "metadata" in message:
            metadata = message["metadata"]

            # Token usage for this message
            if "usage" in metadata:
                usage = metadata["usage"]
                st.markdown(f"""
                <div class="token-usage">
                    <div class="token-usage-item">
                        <span class="token-usage-label">In:</span>
                        <span class="token-usage-value">{usage.get('input_tokens', 0):,}</span>
                    </div>
                    <div class="token-usage-item">
                        <span class="token-usage-label">Out:</span>
                        <span class="token-usage-value">{usage.get('output_tokens', 0):,}</span>
                    </div>
                    <div class="token-usage-item">
                        <span class="token-usage-label">Time:</span>
                        <span class="token-usage-value">{metadata.get('duration', 0):.2f}s</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Handle quick actions
if 'quick_action' in st.session_state:
    user_input = st.session_state.quick_action
    del st.session_state.quick_action
    st.rerun()
else:
    user_input = st.chat_input("Ask OCAA anything about OneSuite, or request QA testing, error analysis, or workflows...")

# Process user input
if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant response
    if st.session_state.anthropic_client:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            start_time = time.time()

            try:
                # Build API messages
                api_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] in ["user", "assistant"]:
                        api_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

                # Stream or regular response
                if stream_responses:
                    # Streaming response
                    with st.session_state.anthropic_client.messages.stream(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=OCAA_SYSTEM_PROMPT,
                        messages=api_messages
                    ) as stream:
                        for text in stream.text_stream:
                            full_response += text
                            message_placeholder.markdown(full_response + "▌")

                        message_placeholder.markdown(full_response)

                        # Get final message for usage stats
                        final_message = stream.get_final_message()
                        usage = {
                            'input_tokens': final_message.usage.input_tokens,
                            'output_tokens': final_message.usage.output_tokens
                        }
                else:
                    # Regular response
                    response = st.session_state.anthropic_client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=OCAA_SYSTEM_PROMPT,
                        messages=api_messages
                    )

                    full_response = response.content[0].text
                    message_placeholder.markdown(full_response)

                    usage = {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens
                    }

                # Calculate duration
                duration = time.time() - start_time

                # Update total tokens
                st.session_state.total_tokens['input'] += usage['input_tokens']
                st.session_state.total_tokens['output'] += usage['output_tokens']

                # Add assistant message with metadata
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "usage": usage,
                        "duration": duration,
                        "model": model
                    }
                })

                # Show token usage
                st.markdown(f"""
                <div class="token-usage">
                    <div class="token-usage-item">
                        <span class="token-usage-label">In:</span>
                        <span class="token-usage-value">{usage['input_tokens']:,}</span>
                    </div>
                    <div class="token-usage-item">
                        <span class="token-usage-label">Out:</span>
                        <span class="token-usage-value">{usage['output_tokens']:,}</span>
                    </div>
                    <div class="token-usage-item">
                        <span class="token-usage-label">Time:</span>
                        <span class="token-usage-value">{duration:.2f}s</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.rerun()

            except AnthropicError as e:
                st.error(f"❌ Anthropic API Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.error("⚠️ Please configure your API key in the sidebar")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.875rem; padding: 1rem;">
    <strong>OCAA v2.0</strong> | Enhanced with AI SDK Patterns |
    Powered by Claude Sonnet 4 |
    <a href="https://github.com/farismai27/training" target="_blank">Documentation</a>
</div>
""", unsafe_allow_html=True)
