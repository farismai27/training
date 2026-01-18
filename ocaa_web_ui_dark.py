#!/usr/bin/env python3
"""
OCAA Web UI - Dark Theme (OneSuite Style)
Matches the dark theme UI with sidebar and modern design
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
    initial_sidebar_state="expanded"
)

# Dark theme CSS - matching the screenshot
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Base dark theme */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Main container - dark background */
    .main {
        background-color: #0d0d0d;
        padding: 0;
    }

    .block-container {
        padding: 2rem 2rem;
        max-width: 56rem;
        margin: 0 auto;
    }

    /* Sidebar - dark with slight gradient */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #2d2d2d;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem;
    }

    /* Sidebar header */
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        margin-bottom: 1rem;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .sidebar-logo {
        background: #2d2d2d;
        padding: 0.5rem;
        border-radius: 0.375rem;
        font-weight: 700;
        font-size: 0.875rem;
    }

    /* New Chat button - green like in screenshot */
    .new-chat-btn {
        background: #10b981 !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-bottom: 1rem !important;
        transition: all 0.2s !important;
    }

    .new-chat-btn:hover {
        background: #059669 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }

    /* Sidebar menu items */
    .sidebar-menu-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        margin: 0.25rem 0;
        color: #9ca3af;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.9rem;
    }

    .sidebar-menu-item:hover {
        background: #2d2d2d;
        color: #ffffff;
    }

    .sidebar-menu-item.active {
        background: #2d2d2d;
        color: #10b981;
    }

    /* Welcome message - centered */
    .welcome-message {
        text-align: center;
        margin: 8rem 0 3rem 0;
    }

    .welcome-title {
        font-size: 2rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .welcome-name {
        color: #10b981;
    }

    .welcome-subtitle {
        color: #6b7280;
        font-size: 1.125rem;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 1rem 0 !important;
    }

    /* User messages - right aligned with dark bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        display: flex;
        justify-content: flex-end;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border-radius: 1.25rem !important;
        padding: 0.875rem 1.125rem !important;
        max-width: 70% !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
        color: #ffffff !important;
        margin: 0 !important;
    }

    /* Hide user avatar */
    [data-testid="stChatMessageAvatarUser"] {
        display: none !important;
    }

    /* Assistant messages - left aligned */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        display: flex;
        justify-content: flex-start;
        gap: 0.75rem;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        padding: 0.5rem 0 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) div,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span {
        color: #e5e7eb !important;
        line-height: 1.7;
    }

    /* Assistant avatar - green like in screenshot */
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 2rem !important;
        height: 2rem !important;
        border-radius: 0.5rem !important;
        background: #10b981 !important;
        flex-shrink: 0 !important;
    }

    /* Chat input - large and centered like screenshot */
    [data-testid="stChatInput"] {
        background-color: #1a1a1a !important;
        border: 1px solid #2d2d2d !important;
        border-radius: 1rem !important;
        margin-top: 2rem;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: none !important;
        font-size: 1rem !important;
        padding: 1rem 1.25rem !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
    }

    /* Code blocks */
    code {
        background-color: #2d2d2d !important;
        color: #10b981 !important;
        padding: 0.125rem 0.375rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }

    pre {
        background-color: #1a1a1a !important;
        border: 1px solid #2d2d2d !important;
        border-radius: 0.5rem !important;
        padding: 1rem !important;
        overflow-x: auto;
    }

    pre code {
        background-color: transparent !important;
        color: #e5e7eb !important;
        padding: 0 !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600;
    }

    /* Links */
    a {
        color: #10b981 !important;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    /* Lists */
    ul, ol {
        color: #e5e7eb;
    }

    li {
        margin: 0.5rem 0;
        color: #e5e7eb;
    }

    /* Buttons */
    .stButton > button {
        background-color: #10b981 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background-color: #059669 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }

    /* Text inputs in sidebar */
    .stTextInput input {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 0.5rem !important;
    }

    .stTextInput input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 1px #10b981 !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 0.5rem !important;
    }

    /* Sliders */
    .stSlider > div > div > div {
        background-color: #10b981 !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #10b981 !important;
        font-size: 1.5rem;
        font-weight: 600;
    }

    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Dividers */
    hr {
        border-color: #2d2d2d !important;
        margin: 1.5rem 0;
    }

    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        background-color: #10b981;
        color: #ffffff;
    }

    /* Token usage */
    .token-usage {
        background-color: #1a1a1a;
        border: 1px solid #2d2d2d;
        border-radius: 0.5rem;
        padding: 0.5rem 0.875rem;
        font-size: 0.8125rem;
        color: #9ca3af;
        margin-top: 0.5rem;
        display: inline-flex;
        gap: 1rem;
    }

    .token-label {
        font-weight: 600;
        color: #10b981;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #0d0d0d;
    }

    ::-webkit-scrollbar-thumb {
        background: #2d2d2d;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #404040;
    }

    /* Checkbox */
    .stCheckbox {
        color: #e5e7eb !important;
    }

    /* Sidebar sections */
    .sidebar-section {
        margin: 1.5rem 0;
        padding: 0.75rem;
    }

    .sidebar-section-title {
        color: #9ca3af;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'anthropic_client' not in st.session_state:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        st.session_state.anthropic_client = Anthropic(api_key=api_key) if api_key else None

    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = {'input': 0, 'output': 0}

    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True

    if 'user_name' not in st.session_state:
        st.session_state.user_name = os.environ.get('USER', 'User')

init_session_state()

# Sidebar
with st.sidebar:
    # Logo/Header
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">OS</div>
        <div>
            <div style="font-weight: 600; font-size: 0.9rem;">OneSuite</div>
            <div style="color: #6b7280; font-size: 0.75rem;">Demo Environment</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New Chat button
    if st.button("+ New Chat", key="new_chat", help="Start a new conversation"):
        st.session_state.messages = []
        st.session_state.show_welcome = True
        st.session_state.total_tokens = {'input': 0, 'output': 0}
        st.rerun()

    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    # Menu items
    st.markdown("""
    <div class="sidebar-menu-item">
        <span>📊</span>
        <span>Projects</span>
    </div>
    <div class="sidebar-menu-item">
        <span>📦</span>
        <span>Artifacts</span>
    </div>
    <div class="sidebar-menu-item">
        <span>📚</span>
        <span>Knowledge Base</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Settings section
    st.markdown('<div class="sidebar-section-title">⚙️ Settings</div>', unsafe_allow_html=True)

    # API Key
    api_key_input = st.text_input(
        "API Key",
        type="password",
        value=os.environ.get('ANTHROPIC_API_KEY', ''),
        help="Your Anthropic API key",
        label_visibility="collapsed"
    )

    if api_key_input:
        os.environ['ANTHROPIC_API_KEY'] = api_key_input
        st.session_state.anthropic_client = Anthropic(api_key=api_key_input)
        st.markdown('<div class="status-badge">✓ API Connected</div>', unsafe_allow_html=True)

    # Model selection
    model = st.selectbox(
        "Model",
        ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-opus-4-20250514"],
        index=0,
        label_visibility="collapsed"
    )

    max_tokens = st.slider("Max Tokens", 500, 8192, 4096, 256)
    temperature = st.slider("Temperature", 0.0, 1.0, 1.0, 0.1)
    stream_responses = st.checkbox("Stream Responses", value=True)

    st.divider()

    # Token usage
    if st.session_state.total_tokens['input'] > 0:
        st.markdown('<div class="sidebar-section-title">📊 Usage</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input", f"{st.session_state.total_tokens['input']:,}")
        with col2:
            st.metric("Output", f"{st.session_state.total_tokens['output']:,}")

    st.divider()

    # History section
    st.markdown("""
    <div class="sidebar-menu-item">
        <span>🕐</span>
        <span>History</span>
    </div>
    """, unsafe_allow_html=True)

    # User profile at bottom
    st.markdown(f"""
    <div style="position: fixed; bottom: 1rem; left: 1rem; right: 1rem; padding: 0.75rem; border-top: 1px solid #2d2d2d;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="width: 2rem; height: 2rem; border-radius: 50%; background: linear-gradient(135deg, #10b981 0%, #059669 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.875rem;">
                {st.session_state.user_name[0].upper()}
            </div>
            <div style="color: #e5e7eb; font-size: 0.875rem; font-weight: 500;">
                {st.session_state.user_name}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main content
if st.session_state.show_welcome and len(st.session_state.messages) == 0:
    # Welcome screen
    st.markdown(f"""
    <div class="welcome-message">
        <div class="welcome-title">
            <span class="welcome-name">{st.session_state.user_name}</span> just optimized their way in.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
user_input = st.chat_input("What can we improve today?")

if user_input:
    st.session_state.show_welcome = False

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant response
    if st.session_state.anthropic_client:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            start_time = time.time()

            try:
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                    if msg["role"] in ["user", "assistant"]
                ]

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
                st.session_state.total_tokens['input'] += usage['input_tokens']
                st.session_state.total_tokens['output'] += usage['output_tokens']

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
