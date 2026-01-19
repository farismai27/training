#!/usr/bin/env python3
"""
OneSuite PM Hero - Enhanced with Jira & GitHub Integration
Product-Engineering Alignment + Progress Tracking

Purpose:
- Validate product-engineering alignment
- Track progress across Jira and GitHub
- Report completion rates and blockers
"""

import streamlit as st
import os
import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic, AnthropicError
import requests
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Jira Integration
class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (email, api_token)
        self.headers = {"Accept": "application/json"}

    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """Get Jira issue details"""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            response = requests.get(url, headers=self.headers, auth=self.auth)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None

    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search Jira issues with JQL"""
        try:
            url = f"{self.base_url}/rest/api/3/search"
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,assignee,created,updated,priority,labels,issuetype"
            }
            response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
            if response.status_code == 200:
                return response.json().get('issues', [])
            return []
        except Exception as e:
            return []

# GitHub Integration
class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_repo(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository details"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None

    def get_pull_requests(self, owner: str, repo: str, state: str = "all") -> List[Dict]:
        """Get pull requests"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            params = {"state": state, "per_page": 100}
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []

    def get_commits(self, owner: str, repo: str, since: Optional[str] = None) -> List[Dict]:
        """Get recent commits"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/commits"
            params = {"per_page": 100}
            if since:
                params["since"] = since
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            return []

    def search_issues(self, query: str) -> List[Dict]:
        """Search GitHub issues"""
        try:
            url = "https://api.github.com/search/issues"
            params = {"q": query, "per_page": 100}
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get('items', [])
            return []
        except Exception as e:
            return []

# Progress Analyzer
class ProgressAnalyzer:
    @staticmethod
    def calculate_completion_rate(total: int, completed: int) -> float:
        """Calculate completion percentage"""
        if total == 0:
            return 0.0
        return (completed / total) * 100

    @staticmethod
    def analyze_jira_progress(issues: List[Dict]) -> Dict:
        """Analyze Jira issues progress"""
        if not issues:
            return {"total": 0, "completed": 0, "in_progress": 0, "todo": 0, "blocked": 0}

        total = len(issues)
        completed = 0
        in_progress = 0
        todo = 0
        blocked = 0

        for issue in issues:
            status = issue.get('fields', {}).get('status', {}).get('name', '').lower()

            if 'done' in status or 'closed' in status or 'resolved' in status:
                completed += 1
            elif 'progress' in status or 'review' in status:
                in_progress += 1
            elif 'blocked' in status:
                blocked += 1
            else:
                todo += 1

        completion_rate = ProgressAnalyzer.calculate_completion_rate(total, completed)

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "todo": todo,
            "blocked": blocked,
            "completion_rate": completion_rate
        }

    @staticmethod
    def analyze_github_progress(prs: List[Dict], commits: List[Dict]) -> Dict:
        """Analyze GitHub progress"""
        total_prs = len(prs)
        merged_prs = sum(1 for pr in prs if pr.get('merged_at'))
        open_prs = sum(1 for pr in prs if pr.get('state') == 'open')
        closed_prs = sum(1 for pr in prs if pr.get('state') == 'closed' and not pr.get('merged_at'))

        pr_merge_rate = ProgressAnalyzer.calculate_completion_rate(total_prs, merged_prs)

        return {
            "total_prs": total_prs,
            "merged_prs": merged_prs,
            "open_prs": open_prs,
            "closed_prs": closed_prs,
            "total_commits": len(commits),
            "pr_merge_rate": pr_merge_rate
        }

# Enhanced PM Hero System Prompt with Progress Tracking
PM_HERO_SYSTEM_PROMPT = """
<identity>
You are the **OneSuite PM Hero** - a specialized AI agent focused on ensuring product-engineering alignment AND tracking actual progress for OneSuite development.

Your dual mission:
1. **Validate Alignment**: Ensure requirements are clear, feasible, and consistent
2. **Track Progress**: Monitor Jira and GitHub to report on actual completion and blockers
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

**Part 1: Alignment Validation**
1. Validate Requirements - Check completeness and clarity
2. Assess Engineering Feasibility - Evaluate technical complexity
3. Check Cross-Channel Alignment - Verify consistency across channels
4. Map Dependencies - Identify technical, data, team dependencies
5. Assess Risks - Technical, timeline, resource, business risks
6. Score Alignment - 0-100 score with breakdown

**Part 2: Progress Tracking (NEW)**
7. Monitor Jira Progress - Track ticket status and completion
8. Analyze GitHub Activity - PRs, commits, merge rates
9. Compare Plan vs Reality - Are we on track?
10. Identify Blockers - What's preventing progress?
11. Report Completion Rates - Overall progress percentage
12. Provide Velocity Insights - How fast are we moving?
</your_role>

<output_format_alignment>
For requirement validation:

## 📊 Alignment Score: X/100

### ✅ Strengths
- [What's good]

### ⚠️ Gaps & Issues
- [What's missing]

### 🔧 Feasibility Assessment
**Complexity**: [Low/Medium/High/Very High]
**Effort Estimate**: [S/M/L/XL]

### 🌐 Cross-Channel Impact
| Channel | Impact | Notes |
|---------|--------|-------|
| Search | H/M/L | [Notes] |
| Social | H/M/L | [Notes] |
| Programmatic | H/M/L | [Notes] |
| Commerce | H/M/L | [Notes] |

### 🔗 Dependencies
- Technical, Data, Teams

### ⚠️ Risks
| Risk | Likelihood | Impact | Mitigation |

### 💡 Recommendations
</output_format_alignment>

<output_format_progress>
For progress tracking:

## 📈 Progress Report

### 🎯 Overall Completion
**Completion Rate**: X%
**Status**: [On Track / At Risk / Blocked]

### 📋 Jira Progress
- **Total Tickets**: X
- **Completed**: X (X%)
- **In Progress**: X
- **Todo**: X
- **Blocked**: X

### 💻 GitHub Activity
- **Total PRs**: X
- **Merged**: X (X%)
- **Open**: X
- **Commits (Last 30 days)**: X

### 🚧 Blockers
- [List of blocking issues]

### 📊 Velocity Insights
- **Avg Time to Merge**: X days
- **Active Contributors**: X
- **Commit Frequency**: X/week

### 🎯 Recommendations
1. [Action items based on progress]
</output_format_progress>

<commands>
User can ask you to:
- "Check alignment for [requirement]" - Validate a requirement
- "Track progress for [project/epic]" - Get progress report
- "Compare Jira ticket [KEY] with GitHub" - Cross-check status
- "Show blockers" - List all blockers
- "What's the completion rate?" - Overall progress
- "Analyze velocity" - Team performance metrics
</commands>

<communication_style>
- **Data-driven** - Use actual numbers from Jira/GitHub
- **Actionable** - Focus on what to do next
- **Honest** - Call out problems clearly
- **Constructive** - Always provide solutions
- **PM-friendly** - Speak in product management terms
</communication_style>

<scoring_rubric>
Alignment Score (0-100):
1. Requirement Clarity (20 pts)
2. Technical Feasibility (20 pts)
3. Cross-Channel Consistency (20 pts)
4. Completeness (20 pts)
5. Execution Readiness (20 pts)
</scoring_rubric>
"""

# Page config
st.set_page_config(
    page_title="OneSuite PM Hero - Alignment & Progress Tracking",
    page_icon="🦸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [Previous CSS remains the same - keeping it for brevity]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    .main { background-color: #0d0d0d; padding: 0; }
    .block-container { padding: 2rem 2rem; max-width: 56rem; margin: 0 auto; }
    [data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #2d2d2d; }
    [data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1rem; }

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

    .new-chat-btn {
        background: #10b981 !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-bottom: 1rem !important;
    }

    .sidebar-menu-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        margin: 0.25rem 0;
        color: #9ca3af;
        border-radius: 0.5rem;
        font-size: 0.9rem;
    }

    .sidebar-menu-item:hover { background: #2d2d2d; color: #ffffff; }
    .sidebar-menu-item.active { background: #2d2d2d; color: #10b981; }

    .welcome-message { text-align: center; margin: 6rem 0 3rem 0; }
    .welcome-title { font-size: 2.5rem; font-weight: 700; color: #ffffff; margin-bottom: 1rem; }
    .welcome-subtitle { color: #9ca3af; font-size: 1.25rem; margin-bottom: 0.5rem; }
    .hero-icon { font-size: 4rem; margin-bottom: 1rem; }

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

    [data-testid="stChatMessageAvatarUser"] { display: none !important; }

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

    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; font-weight: 600; }
    a { color: #10b981 !important; }
    ul, ol, li { color: #e5e7eb; }

    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th { background-color: #2d2d2d !important; color: #10b981 !important; padding: 0.75rem; border: 1px solid #404040 !important; }
    td { background-color: #1a1a1a !important; color: #e5e7eb !important; padding: 0.75rem; border: 1px solid #2d2d2d !important; }

    code { background-color: #2d2d2d !important; color: #10b981 !important; padding: 0.125rem 0.375rem; border-radius: 0.25rem; }
    pre { background-color: #1a1a1a !important; border: 1px solid #2d2d2d !important; border-radius: 0.5rem !important; padding: 1rem !important; }
    pre code { background-color: transparent !important; color: #e5e7eb !important; padding: 0 !important; }

    .stButton > button {
        background-color: #10b981 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 500 !important;
    }

    .stTextInput input, .stSelectbox > div > div {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 0.5rem !important;
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

    .sidebar-section-title {
        color: #9ca3af;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1.5rem 0 0.75rem 0;
        padding: 0 0.75rem;
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
    if 'jira_client' not in st.session_state:
        st.session_state.jira_client = None
    if 'github_client' not in st.session_state:
        st.session_state.github_client = None

init_session_state()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">🦸</div>
        <div>
            <div style="font-weight: 600; font-size: 0.9rem;">PM Hero</div>
            <div style="color: #6b7280; font-size: 0.75rem;">Alignment + Progress</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("+ New Analysis", key="new_chat"):
        st.session_state.messages = []
        st.session_state.show_welcome = True
        st.session_state.total_tokens = {'input': 0, 'output': 0}
        st.rerun()

    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-menu-item active">
        <span>✅</span>
        <span>Alignment Check</span>
    </div>
    <div class="sidebar-menu-item">
        <span>📈</span>
        <span>Progress Tracking</span>
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

    # API Keys Section
    st.markdown('<div class="sidebar-section-title">🔑 API Keys</div>', unsafe_allow_html=True)

    # Anthropic API Key
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get('ANTHROPIC_API_KEY', ''),
        help="Your Anthropic API key",
        key="anthropic_key"
    )

    if api_key_input:
        os.environ['ANTHROPIC_API_KEY'] = api_key_input
        st.session_state.anthropic_client = Anthropic(api_key=api_key_input)
        st.markdown('<div class="status-badge">✓ Anthropic Connected</div>', unsafe_allow_html=True)

    # Jira Configuration
    with st.expander("⚙️ Jira Configuration"):
        jira_url = st.text_input("Jira URL", value=os.environ.get('JIRA_URL', ''), help="e.g., https://yourcompany.atlassian.net")
        jira_email = st.text_input("Jira Email", value=os.environ.get('JIRA_EMAIL', ''))
        jira_token = st.text_input("Jira API Token", type="password", value=os.environ.get('JIRA_API_TOKEN', ''))

        if jira_url and jira_email and jira_token:
            st.session_state.jira_client = JiraClient(jira_url, jira_email, jira_token)
            st.success("✓ Jira Connected")

    # GitHub Configuration
    with st.expander("⚙️ GitHub Configuration"):
        github_token = st.text_input("GitHub Token", type="password", value=os.environ.get('GITHUB_TOKEN', ''))

        if github_token:
            st.session_state.github_client = GitHubClient(github_token)
            st.success("✓ GitHub Connected")

    st.divider()

    # Model Settings
    st.markdown('<div class="sidebar-section-title">⚙️ Model Settings</div>', unsafe_allow_html=True)

    model = st.selectbox(
        "Model",
        ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-opus-4-20250514"],
        index=0
    )

    max_tokens = st.slider("Max Tokens", 1000, 8192, 6000, 500)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
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

# Main content
if st.session_state.show_welcome and len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-message">
        <div class="hero-icon">🦸</div>
        <div class="welcome-title">
            OneSuite PM Hero
        </div>
        <div class="welcome-subtitle">
            Product-Engineering Alignment + Progress Tracking
        </div>
        <div style="color: #6b7280; font-size: 1rem; margin-top: 1rem;">
            Validate requirements • Track Jira & GitHub • Report completion rates
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if "metadata" in message and "usage" in message["metadata"]:
                usage = message["metadata"]["usage"]
                st.markdown(f"""
                <div style="background: #1a1a1a; border: 1px solid #2d2d2d; border-radius: 0.5rem; padding: 0.5rem 0.875rem; font-size: 0.8125rem; color: #9ca3af; margin-top: 0.5rem; display: inline-flex; gap: 1rem;">
                    <span><span style="font-weight: 600; color: #10b981;">In:</span> {usage.get('input_tokens', 0):,}</span>
                    <span><span style="font-weight: 600; color: #10b981;">Out:</span> {usage.get('output_tokens', 0):,}</span>
                    <span><span style="font-weight: 600; color: #10b981;">Time:</span> {message["metadata"].get('duration', 0):.2f}s</span>
                </div>
                """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask: 'Check alignment for...' or 'Track progress for...' or 'Show blockers'")

if user_input:
    st.session_state.show_welcome = False

    # Check if user is requesting progress tracking
    context_data = ""

    if any(keyword in user_input.lower() for keyword in ['track', 'progress', 'jira', 'github', 'completion', 'blockers']):
        # Extract Jira keys or GitHub repos from input
        jira_keys = re.findall(r'\b[A-Z]+-\d+\b', user_input)
        github_repos = re.findall(r'[\w-]+/[\w-]+', user_input)

        if st.session_state.jira_client and jira_keys:
            context_data += "\n\n### Jira Data:\n"
            for key in jira_keys:
                issue = st.session_state.jira_client.get_issue(key)
                if issue:
                    context_data += f"\n**{key}**: {issue.get('fields', {}).get('summary', 'N/A')}\n"
                    context_data += f"Status: {issue.get('fields', {}).get('status', {}).get('name', 'N/A')}\n"
                    context_data += f"Priority: {issue.get('fields', {}).get('priority', {}).get('name', 'N/A')}\n"

        if st.session_state.github_client and github_repos:
            context_data += "\n\n### GitHub Data:\n"
            for repo in github_repos:
                owner, repo_name = repo.split('/')
                prs = st.session_state.github_client.get_pull_requests(owner, repo_name)
                commits = st.session_state.github_client.get_commits(owner, repo_name)

                progress = ProgressAnalyzer.analyze_github_progress(prs, commits)
                context_data += f"\n**{repo}**:\n"
                context_data += f"Total PRs: {progress['total_prs']}, Merged: {progress['merged_prs']} ({progress['pr_merge_rate']:.1f}%)\n"
                context_data += f"Commits (30 days): {progress['total_commits']}\n"

    # Add context data to user message if available
    full_message = user_input
    if context_data:
        full_message += context_data

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

                # Add context data to last user message
                if context_data and api_messages:
                    api_messages[-1]["content"] = full_message

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
                <div style="background: #1a1a1a; border: 1px solid #2d2d2d; border-radius: 0.5rem; padding: 0.5rem 0.875rem; font-size: 0.8125rem; color: #9ca3af; margin-top: 0.5rem; display: inline-flex; gap: 1rem;">
                    <span><span style="font-weight: 600; color: #10b981;">In:</span> {usage['input_tokens']:,}</span>
                    <span><span style="font-weight: 600; color: #10b981;">Out:</span> {usage['output_tokens']:,}</span>
                    <span><span style="font-weight: 600; color: #10b981;">Time:</span> {duration:.2f}s</span>
                </div>
                """, unsafe_allow_html=True)

                st.rerun()

            except AnthropicError as e:
                st.error(f"❌ API Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.error("⚠️ Please configure your Anthropic API key in the sidebar")
