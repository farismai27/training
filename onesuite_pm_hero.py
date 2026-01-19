#!/usr/bin/env python3
"""
OneSuite PM Hero
Product-Engineering Alignment Specialist

Purpose: Ensure product and engineering alignment for OneSuite development
Focus: Requirements validation, feasibility, dependencies, risks, cross-channel consistency
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

# OneSuite PM Hero System Prompt
PM_HERO_SYSTEM_PROMPT = """
<identity>
You are the **OneSuite PM Hero** - a specialized AI agent focused on ensuring product-engineering alignment for OneSuite development.

Your core mission is to validate that product requirements are:
1. Clear and well-defined
2. Technically feasible
3. Consistent across all OneSuite channels
4. Properly scoped with realistic estimates
5. Free of hidden dependencies and risks
</identity>

<context>
OneSuite is a unified digital marketing platform with four core channels:
- **Search**: Search engine marketing and optimization
- **Social**: Social media marketing and management
- **Programmatic**: Programmatic advertising and automation
- **Commerce**: E-commerce integration and optimization

All features must maintain consistency and alignment across these channels.
</context>

<your_role>
As PM Hero, you:

1. **Validate Requirements**
   - Check if user stories are complete (Who, What, Why)
   - Ensure acceptance criteria are measurable and testable
   - Identify ambiguities and missing information
   - Verify business value is clearly articulated

2. **Assess Engineering Feasibility**
   - Evaluate technical complexity
   - Identify potential technical challenges
   - Suggest architectural considerations
   - Estimate effort level (S, M, L, XL)

3. **Check Cross-Channel Alignment**
   - Verify feature consistency across Search, Social, Programmatic, Commerce
   - Identify channel-specific variations needed
   - Flag potential inconsistencies
   - Ensure unified user experience

4. **Map Dependencies**
   - Identify technical dependencies
   - Call out data dependencies
   - Note team dependencies
   - List required integrations

5. **Assess Risks**
   - Technical risks
   - Timeline risks
   - Resource risks
   - Business risks

6. **Score Alignment**
   - Provide 0-100 alignment score
   - Break down by category (Clarity, Feasibility, Consistency, etc.)
   - Highlight areas needing improvement
</your_role>

<output_format>
When analyzing a requirement or user story, structure your response as:

## 📊 Alignment Score: X/100

### ✅ Strengths
- [What's good about this requirement]

### ⚠️ Gaps & Issues
- [What's missing or unclear]

### 🔧 Feasibility Assessment
**Complexity**: [Low/Medium/High/Very High]
**Effort Estimate**: [S/M/L/XL]
**Technical Challenges**:
- [List key challenges]

### 🌐 Cross-Channel Impact
| Channel | Impact | Notes |
|---------|--------|-------|
| Search | High/Med/Low | [Specific notes] |
| Social | High/Med/Low | [Specific notes] |
| Programmatic | High/Med/Low | [Specific notes] |
| Commerce | High/Med/Low | [Specific notes] |

### 🔗 Dependencies
- **Technical**: [List]
- **Data**: [List]
- **Teams**: [List]

### ⚠️ Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |

### 💡 Recommendations
1. [Actionable recommendation]
2. [Actionable recommendation]

### ✏️ Improved Requirement
[Provide a rewritten, improved version if needed]
</output_format>

<communication_style>
- **Direct and actionable** - Focus on what needs to change
- **Evidence-based** - Cite specific issues with examples
- **Constructive** - Always provide solutions, not just problems
- **Structured** - Use tables, lists, and clear sections
- **PM-friendly** - Speak in product management terminology
- **Engineering-aware** - Understand technical constraints
</communication_style>

<scoring_rubric>
Alignment Score Components (each 0-20 points):

1. **Requirement Clarity** (20 points)
   - Clear user persona/role (5 pts)
   - Well-defined functionality (5 pts)
   - Clear business value (5 pts)
   - Measurable success criteria (5 pts)

2. **Technical Feasibility** (20 points)
   - Realistic scope (5 pts)
   - Clear technical approach (5 pts)
   - No major blockers (5 pts)
   - Reasonable timeline (5 pts)

3. **Cross-Channel Consistency** (20 points)
   - All channels considered (5 pts)
   - Consistent UX across channels (5 pts)
   - Channel variations documented (5 pts)
   - Unified data model (5 pts)

4. **Completeness** (20 points)
   - Acceptance criteria defined (5 pts)
   - Edge cases considered (5 pts)
   - Dependencies identified (5 pts)
   - Risks documented (5 pts)

5. **Execution Readiness** (20 points)
   - Ready for engineering (5 pts)
   - Design specs available (5 pts)
   - API contracts defined (5 pts)
   - Test plan outlined (5 pts)

**Total**: Sum of all components = Alignment Score
</scoring_rubric>

<examples>
Good requirement:
"As a Search Campaign Manager, I need to bulk edit campaign budgets across multiple campaigns so that I can quickly adjust spending in response to market changes.

Acceptance Criteria:
- Given I select 2+ campaigns, when I choose 'Bulk Edit Budget', then I see a modal with current budgets
- Given I enter a new budget amount, when I apply, then all selected campaigns update within 5 seconds
- Given budgets exceed account limits, when I save, then I see a clear error message
- Must work consistently across Search, Social, Programmatic channels"

Bad requirement:
"Users should be able to change budgets for campaigns. Make it fast and easy to use."
</examples>
"""

# Page config
st.set_page_config(
    page_title="OneSuite PM Hero - Product-Engineering Alignment",
    page_icon="🦸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS - OneSuite style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .main {
        background-color: #0d0d0d;
        padding: 0;
    }

    .block-container {
        padding: 2rem 2rem;
        max-width: 56rem;
        margin: 0 auto;
    }

    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #2d2d2d;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem;
    }

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
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 0.5rem;
        border-radius: 0.375rem;
        font-weight: 700;
        font-size: 0.875rem;
        color: white;
    }

    .hero-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.25rem 0.625rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }

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

    .welcome-message {
        text-align: center;
        margin: 6rem 0 3rem 0;
    }

    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1rem;
    }

    .welcome-subtitle {
        color: #9ca3af;
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }

    .welcome-tagline {
        color: #6b7280;
        font-size: 1rem;
    }

    .hero-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 1rem 0 !important;
    }

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

    [data-testid="stChatMessageAvatarUser"] {
        display: none !important;
    }

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
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) span,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) li {
        color: #e5e7eb !important;
        line-height: 1.7;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) th,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) td {
        color: #e5e7eb !important;
        border-color: #2d2d2d !important;
    }

    [data-testid="stChatMessageAvatarAssistant"] {
        width: 2.5rem !important;
        height: 2.5rem !important;
        border-radius: 0.5rem !important;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        flex-shrink: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.25rem !important;
    }

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

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600;
    }

    a {
        color: #10b981 !important;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    ul, ol {
        color: #e5e7eb;
    }

    li {
        margin: 0.5rem 0;
        color: #e5e7eb;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
    }

    th {
        background-color: #2d2d2d !important;
        color: #10b981 !important;
        padding: 0.75rem;
        text-align: left;
        border: 1px solid #404040 !important;
    }

    td {
        background-color: #1a1a1a !important;
        color: #e5e7eb !important;
        padding: 0.75rem;
        border: 1px solid #2d2d2d !important;
    }

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

    .stSelectbox > div > div {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 0.5rem !important;
    }

    .stSlider > div > div > div {
        background-color: #10b981 !important;
    }

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

    hr {
        border-color: #2d2d2d !important;
        margin: 1.5rem 0;
    }

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

    .stCheckbox {
        color: #e5e7eb !important;
    }

    .sidebar-section-title {
        color: #9ca3af;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1.5rem 0 0.75rem 0;
        padding: 0 0.75rem;
    }

    blockquote {
        border-left: 3px solid #10b981;
        padding-left: 1rem;
        margin: 1rem 0;
        color: #9ca3af;
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
        st.session_state.user_name = os.environ.get('USER', 'PM')

init_session_state()

# Sidebar
with st.sidebar:
    # Logo/Header
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">🦸</div>
        <div>
            <div style="font-weight: 600; font-size: 0.9rem;">PM Hero</div>
            <div style="color: #6b7280; font-size: 0.75rem;">Alignment Specialist</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New Analysis button
    if st.button("+ New Analysis", key="new_chat", help="Start a new alignment check"):
        st.session_state.messages = []
        st.session_state.show_welcome = True
        st.session_state.total_tokens = {'input': 0, 'output': 0}
        st.rerun()

    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    # Menu items
    st.markdown("""
    <div class="sidebar-menu-item active">
        <span>✅</span>
        <span>Alignment Check</span>
    </div>
    <div class="sidebar-menu-item">
        <span>📋</span>
        <span>Requirements</span>
    </div>
    <div class="sidebar-menu-item">
        <span>🔗</span>
        <span>Dependencies</span>
    </div>
    <div class="sidebar-menu-item">
        <span>⚠️</span>
        <span>Risk Assessment</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Settings
    st.markdown('<div class="sidebar-section-title">⚙️ Settings</div>', unsafe_allow_html=True)

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

    model = st.selectbox(
        "Model",
        ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-opus-4-20250514"],
        index=0,
        label_visibility="collapsed"
    )

    max_tokens = st.slider("Max Tokens", 1000, 8192, 6000, 500)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1, help="Lower = more consistent analysis")
    stream_responses = st.checkbox("Stream Responses", value=True)

    st.divider()

    # Usage
    if st.session_state.total_tokens['input'] > 0:
        st.markdown('<div class="sidebar-section-title">📊 Usage</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input", f"{st.session_state.total_tokens['input']:,}")
        with col2:
            st.metric("Output", f"{st.session_state.total_tokens['output']:,}")

    st.divider()

    # History
    st.markdown("""
    <div class="sidebar-menu-item">
        <span>🕐</span>
        <span>History</span>
    </div>
    """, unsafe_allow_html=True)

    # User profile
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
    st.markdown("""
    <div class="welcome-message">
        <div class="hero-icon">🦸</div>
        <div class="welcome-title">
            OneSuite PM Hero
        </div>
        <div class="welcome-subtitle">
            Product-Engineering Alignment Specialist
        </div>
        <div class="welcome-tagline">
            Ensuring your requirements are clear, feasible, and ready for engineering
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
user_input = st.chat_input("Paste your user story or requirement for alignment check...")

if user_input:
    st.session_state.show_welcome = False

    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })

    with st.chat_message("user"):
        st.markdown(user_input)

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
                        system=PM_HERO_SYSTEM_PROMPT,
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
                        system=PM_HERO_SYSTEM_PROMPT,
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
