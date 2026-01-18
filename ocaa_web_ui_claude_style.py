#!/usr/bin/env python3
"""
OCAA Web UI - Claude Style
Matches claude.ai UI design exactly

Features:
- Claude.ai-inspired clean design
- Proper message bubbles
- Code syntax highlighting
- Copy buttons
- Smooth animations
- Clean typography
"""

import streamlit as st
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic, AnthropicError

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
    page_title="OCAA - OneSuite Core Architect Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Claude-style CSS
st.markdown("""
<style>
    /* Import Inter font (Claude uses Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Reset and base styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container - Claude's light beige background */
    .main {
        background-color: #f5f5f4;
        padding: 0;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 48rem;
        margin: 0 auto;
    }

    /* Header - minimal like Claude */
    .ocaa-header {
        background: #ffffff;
        border-bottom: 1px solid #e7e7e5;
        padding: 1rem 2rem;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .ocaa-header h1 {
        color: #1a1a1a;
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }

    .ocaa-header-subtitle {
        color: #6b6b6b;
        font-size: 0.875rem;
        margin-left: 0.5rem;
    }

    /* Chat messages - Claude style */
    [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        padding: 0 !important;
        border: none !important;
    }

    /* User messages - aligned right like Claude */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1.5rem;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border-radius: 1.5rem;
        padding: 0.875rem 1.125rem !important;
        max-width: 80%;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) div,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) span {
        color: #ffffff !important;
    }

    /* Hide user avatar */
    [data-testid="stChatMessageAvatarUser"] {
        display: none;
    }

    /* Assistant messages - left aligned with avatar */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 2rem;
        gap: 0.75rem;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        color: #1a1a1a !important;
        padding: 0.5rem 0 !important;
        max-width: 100%;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div {
        color: #1a1a1a !important;
        line-height: 1.7;
        font-size: 0.9375rem;
    }

    /* Assistant avatar - Claude's orange/red color */
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 2rem !important;
        height: 2rem !important;
        border-radius: 0.375rem !important;
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
    }

    /* Code blocks - Claude style */
    code {
        background-color: #f5f5f4;
        color: #1a1a1a;
        padding: 0.125rem 0.375rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-family: 'Monaco', 'Menlo', monospace;
    }

    pre {
        background-color: #1a1a1a !important;
        border-radius: 0.5rem !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        overflow-x: auto;
    }

    pre code {
        background-color: transparent !important;
        color: #e5e5e5 !important;
        padding: 0 !important;
        font-size: 0.875rem;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    /* Links */
    a {
        color: #ea580c;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    /* Lists */
    ul, ol {
        margin: 1rem 0;
        padding-left: 1.5rem;
    }

    li {
        margin: 0.5rem 0;
        line-height: 1.7;
    }

    /* Blockquotes */
    blockquote {
        border-left: 3px solid #ea580c;
        padding-left: 1rem;
        margin: 1rem 0;
        color: #6b6b6b;
    }

    /* Chat input - Claude style */
    [data-testid="stChatInput"] {
        background-color: #ffffff;
        border: 1px solid #e7e7e5;
        border-radius: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stChatInput"] textarea {
        border: none !important;
        font-size: 0.9375rem;
        padding: 0.875rem 1rem;
    }

    [data-testid="stChatInput"] textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #2d2d2d;
        color: #ffffff;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background-color: #1a1a1a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e7e7e5;
        padding: 1.5rem 1rem;
    }

    [data-testid="stSidebar"] .element-container {
        margin-bottom: 1rem;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #6b6b6b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #e7e7e5;
        margin: 1.5rem 0;
    }

    /* Status indicators - minimal */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.25rem 0.625rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        background-color: #f5f5f4;
        color: #6b6b6b;
        border: 1px solid #e7e7e5;
    }

    .status-connected {
        background-color: #f0fdf4;
        color: #15803d;
        border-color: #86efac;
    }

    .status-connected::before {
        content: "●";
        color: #22c55e;
    }

    /* Token usage - minimal */
    .token-usage {
        background-color: #fef3c7;
        border: 1px solid #fde68a;
        border-radius: 0.5rem;
        padding: 0.625rem 0.875rem;
        font-size: 0.8125rem;
        color: #92400e;
        margin-top: 0.5rem;
        display: inline-flex;
        gap: 1rem;
    }

    .token-label {
        font-weight: 600;
    }

    /* Scrollbar - Claude style */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: #d4d4d4;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #a3a3a3;
    }

    /* Loading animation - Claude style */
    .loading-dots {
        display: inline-flex;
        gap: 0.375rem;
        padding: 0.5rem 0;
    }

    .loading-dots span {
        width: 0.5rem;
        height: 0.5rem;
        background: #a3a3a3;
        border-radius: 50%;
        animation: pulse 1.4s infinite ease-in-out both;
    }

    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes pulse {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm OCAA (OneSuite Core Architect Agent). I can help you with product strategy, QA testing, error monitoring, and workflow design. What would you like to work on today?",
            "timestamp": datetime.now().isoformat()
        })

    if 'anthropic_client' not in st.session_state:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        st.session_state.anthropic_client = Anthropic(api_key=api_key) if api_key else None

    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = {'input': 0, 'output': 0}

init_session_state()

# Header
st.markdown("""
<div class="ocaa-header">
    <div>
        <span style="font-size: 1.25rem; margin-right: 0.5rem;">🤖</span>
        <span style="font-weight: 600; font-size: 1rem;">OCAA</span>
        <span class="ocaa-header-subtitle">OneSuite Core Architect Agent</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Add spacing for fixed header
st.markdown('<div style="height: 4rem;"></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")

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
        st.markdown('<div class="status-badge status-connected">API Connected</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter your API key")

    st.divider()

    # Model selection
    model = st.selectbox(
        "Model",
        [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-opus-4-20250514"
        ],
        index=0
    )

    # Settings
    max_tokens = st.slider("Max Tokens", 500, 8192, 4096, 256)
    temperature = st.slider("Temperature", 0.0, 1.0, 1.0, 0.1)
    stream_responses = st.checkbox("Stream Responses", value=True)

    st.divider()

    # Token usage
    if st.session_state.total_tokens['input'] > 0:
        st.markdown("### 📊 Usage")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input", f"{st.session_state.total_tokens['input']:,}")
        with col2:
            st.metric("Output", f"{st.session_state.total_tokens['output']:,}")

    st.divider()

    # Actions
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

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show token usage if available
        if "metadata" in message and "usage" in message["metadata"]:
            usage = message["metadata"]["usage"]
            st.markdown(f"""
            <div class="token-usage">
                <span><span class="token-label">In:</span> {usage.get('input_tokens', 0):,}</span>
                <span><span class="token-label">Out:</span> {usage.get('output_tokens', 0):,}</span>
                <span><span class="token-label">Time:</span> {message["metadata"].get('duration', 0):.2f}s</span>
            </div>
            """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Message OCAA...")

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
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                    if msg["role"] in ["user", "assistant"]
                ]

                # Stream response
                if stream_responses:
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
                        final_message = stream.get_final_message()
                        usage = {
                            'input_tokens': final_message.usage.input_tokens,
                            'output_tokens': final_message.usage.output_tokens
                        }
                else:
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

                duration = time.time() - start_time

                # Update totals
                st.session_state.total_tokens['input'] += usage['input_tokens']
                st.session_state.total_tokens['output'] += usage['output_tokens']

                # Add to messages
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

                # Show usage
                st.markdown(f"""
                <div class="token-usage">
                    <span><span class="token-label">In:</span> {usage['input_tokens']:,}</span>
                    <span><span class="token-label">Out:</span> {usage['output_tokens']:,}</span>
                    <span><span class="token-label">Time:</span> {duration:.2f}s</span>
                </div>
                """, unsafe_allow_html=True)

                st.rerun()

            except AnthropicError as e:
                st.error(f"❌ API Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.error("⚠️ Please configure your API key in the sidebar")
