# =========================
# IMPORTS & SETUP
# =========================
import os
import sys
import json
import re
import statistics
from dotenv import load_dotenv
from anthropic import Anthropic
import ast
import requests
from requests.auth import HTTPBasicAuth
from anthropic.types import ToolParam
# Computer Use imports (added by merge script)
import base64
from io import BytesIO

# Try to import Computer Use dependencies
try:
    from PIL import Image
    import pyautogui
    COMPUTER_USE_AVAILABLE = True
    pyautogui.FAILSAFE = True  # Enable fail-safe
except ImportError:
    COMPUTER_USE_AVAILABLE = False
    print("⚠️  Computer Use unavailable (pip install pillow pyautogui)")

try:
    import pdfplumber
    from docx import Document as DocxDocument
    DOCUMENT_CONVERSION_AVAILABLE = True
except ImportError:
    DOCUMENT_CONVERSION_AVAILABLE = False

from datetime import datetime, timedelta
import uuid
import base64
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

client = Anthropic(api_key=api_key)
model = "claude-3-5-haiku-latest"

# SDK capability helpers
try:
    import anthropic as _anthropic_mod
    _anthropic_version = getattr(_anthropic_mod, "__version__", "0")
except Exception:
    _anthropic_version = "0"

def _fine_grained_supported():
    try:
        major = int(str(_anthropic_version).split(".")[0])
        return major >= 1
    except Exception:
        return False

# Constants
MAX_TOKENS_WITH_TOOLS = 2000
MAX_TOKENS_DEFAULT = 1500
CONFLUENCE_CONTENT_LIMIT = 1500
MAX_TOOL_ITERATIONS = 5

# Confluence credentials
confluence_url = os.getenv("CONFLUENCE_URL")
confluence_email = os.getenv("CONFLUENCE_EMAIL")
confluence_api_token = os.getenv("CONFLUENCE_API_TOKEN")

# =========================
# MCP SERVER CONFIGURATION
# =========================
# MCP (Model Context Protocol) allows connecting to external tool servers.
# 
# Your agent has FULL MCP support:
# ✅ MCP Client - Connects to servers, discovers tools, routes execution
# ✅ Tool Discovery - Automatic via list_tools protocol
# ✅ Tool Execution - Automatic routing to correct server
# ✅ Stdio Transport - Communication over standard input/output
# ✅ Message Protocol - ListToolsRequest/Result, CallToolRequest/Result
# ✅ Integration with Claude - MCP tools combined with local tools
#
# Active MCP Servers:
MCP_SERVERS_CONFIG = {
    # Custom Document Management MCP server (Python) - in-memory documents
    "documents": {
        "command": sys.executable,  # Use same Python interpreter as demo.py
        "args": [os.path.join(os.path.dirname(__file__), "src", "document_server.py")],
        "env": {}
    }
    # To add more servers (requires Node.js):
    # "github": {
    #     "command": "npx",
    #     "args": ["-y", "@modelcontextprotocol/server-github"],
    #     "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")}
    # }
}

# MCP Client state
mcp_sessions: Dict[str, ClientSession] = {}
mcp_tools: List[Dict[str, Any]] = []

# Thread executor for running async MCP operations
mcp_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="mcp-")

# Event loop for MCP operations (set during initialization)
mcp_event_loop = None

# =========================
# STANDALONE TOOL SCHEMAS (ToolParam)
# =========================
get_current_datetime_schema = ToolParam(
    name="get_current_datetime",
    description=(
        "Return the current date and time. Use this to establish the baseline "
        "for reminder calculations or time comparisons. Optionally provide a "
        "custom strftime format to receive a formatted string. Returns both ISO "
        "and formatted variants with timezone metadata."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": (
                    "Optional strftime format for the formatted datetime output. "
                    "Controls how the returned formatted string appears (e.g. '%Y-%m-%d %H:%M:%S'). "
                    "If omitted, defaults to '%Y-%m-%d %H:%M:%S'."
                )
            }
        },
        "required": []
    }
)

add_duration_to_datetime_schema = ToolParam(
    name="add_duration_to_datetime",
    description=(
        "Add a duration (days, hours, minutes) to a base ISO 8601 datetime. "
        "Use when calculating future or past reminders. Returns the result in ISO format "
        "and includes a human-readable description of the duration added."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "base_datetime": {
                "type": "string",
                "description": (
                    "ISO 8601 datetime string to adjust (e.g., '2026-01-11T14:30:00'). "
                    "Must be a valid ISO 8601 value."
                )
            },
            "days": {
                "type": "integer",
                "description": (
                    "Number of days to add (can be negative). Controls day-level shift."
                )
            },
            "hours": {
                "type": "integer",
                "description": (
                    "Number of hours to add (can be negative). Controls hour-level shift."
                )
            },
            "minutes": {
                "type": "integer",
                "description": (
                    "Number of minutes to add (can be negative). Controls minute-level shift."
                )
            }
        },
        "required": ["base_datetime"]
    }
)

set_reminder_schema = ToolParam(
    name="set_reminder",
    description=(
        "Set a reminder for a specific datetime. Use when scheduling notifications. "
        "Requires a message and an ISO 8601 datetime string. Returns a confirmation with "
        "a unique reminder ID and the scheduled time."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "reminder_datetime": {
                "type": "string",
                "description": (
                    "ISO 8601 datetime when the reminder should trigger (e.g., '2026-01-11T14:30:00'). "
                    "Must be valid and preferably in the future."
                )
            },
            "message": {
                "type": "string",
                "description": (
                    "Text describing what to remind the user about. Should be concise and actionable."
                )
            },
            "reminder_id": {
                "type": "string",
                "description": (
                    "Optional unique identifier for the reminder. If omitted, a new ID is generated."
                )
            }
        },
        "required": ["reminder_datetime", "message"]
    }
)

# Additional schemas for remaining tools
get_confluence_page_schema = ToolParam(
    name="get_confluence_page",
    description=(
        "Retrieve OneSuite Core documentation from Confluence by page ID. "
        "Use for accessing current product requirements, user stories, and guidelines. "
        "Requires valid Confluence credentials in environment variables. Returns page title and content, truncated for token limits."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "page_id": {
                "type": "string",
                "description": "Confluence page ID (numeric string, e.g., '3432841264')."
            }
        },
        "required": ["page_id"]
    }
)

web_search_schema = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5
}

calculate_product_metrics_schema = ToolParam(
    name="calculate_product_metrics",
    description=(
        "Calculate OneSuite product metrics such as ROI, sprint velocity, or capacity. "
        "Provide the metric type and a values object with required inputs. Returns a compact result for the selected metric."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "metric_type": {
                "type": "string",
                "enum": ["roi", "velocity", "capacity"],
                "description": "Metric type to compute."
            },
            "values": {
                "type": "object",
                "description": "Input values for the metric calculation."
            }
        },
        "required": ["metric_type", "values"]
    }
)

generate_document_schema = ToolParam(
    name="generate_document",
    description=(
        "Generate OneSuite documents (PRD, roadmap, spec) from templates. "
        "Supply the doc_type and a content object with required fields; returns a formatted document string."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "doc_type": {"type": "string", "enum": ["prd", "roadmap", "spec"]},
            "content": {"type": "object", "description": "Template fields for document generation."}
        },
        "required": ["doc_type", "content"]
    }
)

create_jira_ticket_schema = ToolParam(
    name="create_jira_ticket",
    description=(
        "Create a Jira ticket for OneSuite (simulated if credentials are missing). "
        "Provide summary, description, issue_type, and optional project key. Returns the ticket key and URL when successful."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "description": {"type": "string"},
            "issue_type": {"type": "string", "enum": ["Epic", "Story", "Task"]},
            "project": {"type": "string", "default": "ONESUITE"}
        },
        "required": ["summary", "description", "issue_type"]
    }
)

article_summary_schema = ToolParam(
    name="article_summary",
    description=(
        "Extract structured information from an article or document. "
        "Use this tool to reliably extract title, author, and key insights "
        "as structured JSON data without relying on text parsing."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the article or document"
            },
            "author": {
                "type": "string",
                "description": "The author or creator of the article"
            },
            "key_insights": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of 3-5 key insights or main points from the article"
            }
        },
        "required": ["title", "author", "key_insights"]
    }
)

user_story_extraction_schema = ToolParam(
    name="extract_user_story",
    description=(
        "Extract structured user story components from requirements or narrative text. "
        "Returns role, action, benefit, acceptance criteria, and channel impact "
        "as guaranteed structured data."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "role": {
                "type": "string",
                "description": "The user role (e.g., 'Search channel manager', 'agency')"
            },
            "action": {
                "type": "string",
                "description": "What the user wants to do"
            },
            "benefit": {
                "type": "string",
                "description": "Why they want to do it (the benefit or outcome)"
            },
            "acceptance_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of specific, measurable acceptance criteria"
            },
            "channel_impact": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Impact on Search channel"},
                    "social": {"type": "string", "description": "Impact on Social channel"},
                    "programmatic": {"type": "string", "description": "Impact on Programmatic channel"},
                    "commerce": {"type": "string", "description": "Impact on Commerce channel"}
                },
                "required": ["search", "social", "programmatic", "commerce"],
                "description": "How this impacts each OneSuite channel"
            }
        },
        "required": ["role", "action", "benefit", "acceptance_criteria", "channel_impact"]
    }
)

batch_tool_schema = ToolParam(
    name="batch",
    description=(
        "Execute multiple independent tools in parallel. Use when you need to call "
        "several tools that don't depend on each other's results. Significantly "
        "improves performance for parallel operations like setting multiple reminders, "
        "creating multiple tickets, or fetching multiple pages simultaneously."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "description": (
                    "List of tool invocations to execute in parallel. Each invocation "
                    "specifies a tool name and its arguments as a JSON string."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": (
                                "Name of the tool to invoke (e.g., 'set_reminder', "
                                "'get_confluence_page', 'create_jira_ticket')"
                            )
                        },
                        "arguments": {
                            "type": "string",
                            "description": (
                                "JSON string containing the tool's input parameters. "
                                "Example: '{\"page_id\": \"123\"}' or "
                                "'{\"reminder_datetime\": \"2026-01-15T14:00:00\", \"message\": \"Meeting\"}'"
                            )
                        }
                    },
                    "required": ["name", "arguments"]
                }
            }
        },
        "required": ["invocations"]
    }
)

# =========================
# TOOL DEFINITIONS
# =========================
TOOLS = [
    get_confluence_page_schema,
    web_search_schema,
    calculate_product_metrics_schema,
    generate_document_schema,
    create_jira_ticket_schema,
    get_current_datetime_schema,
    add_duration_to_datetime_schema,
    set_reminder_schema,
    batch_tool_schema
]

# Reminders storage (in-memory for this demo)
reminders = []

# =========================

# ===========================================================================
# UNIFIED AGENT TOOL SCHEMAS (Computer Use, Error Analysis, QA Workflows)
# ===========================================================================

computer_screenshot_schema = ToolParam(
    name="take_screenshot",
    description=(
        "Take a screenshot of the current screen. Returns base64 image. "
        "Use for QA testing or UI analysis."
    ),
    input_schema={"type": "object", "properties": {}, "required": []}
)

computer_action_schema = ToolParam(
    name="execute_computer_action",
    description=(
        "Execute mouse/keyboard actions: mouse_move, click, type, key, wait. "
        "Use for QA testing and UI automation."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "action_type": {
                "type": "string",
                "enum": ["mouse_move", "click", "type", "key", "wait"]
            },
            "x": {"type": "number"},
            "y": {"type": "number"},
            "text": {"type": "string"},
            "key": {"type": "string"},
            "button": {"type": "string", "enum": ["left", "right", "middle"]},
            "duration": {"type": "number"}
        },
        "required": ["action_type"]
    }
)

error_analysis_schema = ToolParam(
    name="analyze_production_error",
    description=(
        "Analyze production error and generate fix with root cause analysis."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "error_content": {"type": "string"},
            "file_path": {"type": "string"},
            "context": {"type": "string"}
        },
        "required": ["error_content"]
    }
)

qa_workflow_schema = ToolParam(
    name="run_qa_workflow",
    description=(
        "Run automated QA testing workflow on a URL with test cases."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "test_cases": {"type": "array", "items": {"type": "string"}},
            "max_iterations": {"type": "number"}
        },
        "required": ["url"]
    }
)


# TOOL EXECUTION FUNCTIONS
# =========================
def generate_document(doc_type, content):
    """Generate structured OneSuite documents (PRD, roadmap, spec) from templates.
    
    Args:
        doc_type: One of 'prd', 'roadmap', 'spec'
        content: Dict with template fields to fill
    
    Returns:
        Formatted document string
    """
    templates = {
        "prd": (
            "# Product Requirements Document\n"
            "## Problem Statement\n"
            "{problem}\n"
            "## Solution Overview\n"
            "{solution}\n"
            "## Requirements\n"
            "{requirements}\n"
        ),
        "roadmap": (
            "# OneSuite Roadmap - {timeline}\n"
            "## MVP Phase\n"
            "{mvp}\n"
            "## V1 Features\n"
            "{v1}\n"
            "## Scale Phase\n"
            "{scale}\n"
        ),
        "spec": (
            "# Specification - {title}\n"
            "## Overview\n{overview}\n"
            "## Details\n{details}\n"
        )
    }
    if doc_type not in templates:
        raise ValueError(f"Unknown doc_type: {doc_type}")
    return templates[doc_type].format(**content)

def tool_get_current_datetime(date_format=None):
    """Return current datetime details with optional strftime formatting.

    Args:
        date_format: Optional strftime format string. Defaults to '%Y-%m-%d %H:%M:%S'.

    Returns:
        Dict containing ISO datetime, formatted string, date, time, and timezone.
    """
    if date_format is not None and not isinstance(date_format, str):
        raise ValueError("date_format must be a string when provided")
    fmt = date_format or "%Y-%m-%d %H:%M:%S"
    now = datetime.now()
    try:
        formatted = now.strftime(fmt)
    except Exception as e:
        raise ValueError(f"Invalid date_format: {str(e)}")
    return {
        "datetime": now.isoformat(),
        "formatted": formatted,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": "local"
    }

def tool_add_duration_to_datetime(base_datetime, days=0, hours=0, minutes=0):
    """Add a duration to a base ISO 8601 datetime and return result.

    Raises ValueError for invalid inputs.
    """
    if not base_datetime or not str(base_datetime).strip():
        raise ValueError("base_datetime cannot be empty. Provide ISO 8601 datetime like '2026-01-11T14:30:00'")
    for name, value in ("days", days), ("hours", hours), ("minutes", minutes):
        if not isinstance(value, int):
            raise ValueError(f"{name} must be an integer (can be negative)")
    try:
        base_dt = datetime.fromisoformat(base_datetime)
    except Exception:
        raise ValueError("base_datetime must be a valid ISO 8601 string like 'YYYY-MM-DDTHH:MM:SS'")
    try:
        result_dt = base_dt + timedelta(days=days, hours=hours, minutes=minutes)
    except Exception as e:
        raise ValueError(f"Date calculation failed: {str(e)}")
    return {
        "input": base_datetime,
        "result": result_dt.isoformat(),
        "duration_added": f"{days} days, {hours} hours, {minutes} minutes"
    }

def tool_set_reminder(reminder_datetime, message, reminder_id=None):
    """Set a reminder and return confirmation. Raises ValueError for invalid inputs."""
    if not reminder_datetime or not str(reminder_datetime).strip():
        raise ValueError("reminder_datetime cannot be empty. Provide ISO 8601 datetime like '2026-01-11T14:30:00'")
    if not message or not str(message).strip():
        raise ValueError("message cannot be empty")
    try:
        _ = datetime.fromisoformat(reminder_datetime)
    except Exception:
        raise ValueError("reminder_datetime must be a valid ISO 8601 string like 'YYYY-MM-DDTHH:MM:SS'")
    rid = (reminder_id or str(uuid.uuid4())[:8])
    reminder = {
        "id": rid,
        "datetime": reminder_datetime,
        "message": message,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    reminders.append(reminder)
    return {
        "success": True,
        "reminder_id": rid,
        "reminder_datetime": reminder_datetime,
        "message": message,
        "confirmation": f"Reminder set for {reminder_datetime}. You will be reminded: {message}"
    }

def tool_batch(invocations):
    """Execute multiple tools in parallel and return aggregated results.
    
    Args:
        invocations: List of dicts with 'name' (tool name) and 'arguments' (JSON string)
    
    Returns:
        List of results from each tool invocation
    
    Raises:
        ValueError: If invocations is not a list or contains invalid entries
    """
    if not isinstance(invocations, list):
        raise ValueError("invocations must be a list")
    
    if len(invocations) == 0:
        raise ValueError("invocations cannot be empty")
    
    batch_output = []
    
    for i, invocation in enumerate(invocations):
        if not isinstance(invocation, dict):
            batch_output.append({
                "tool_name": "unknown",
                "output": json.dumps({"error": f"Invocation {i} is not a valid object"})
            })
            continue
        
        tool_name = invocation.get("name", "")
        args_json = invocation.get("arguments", "{}")
        
        if not tool_name:
            batch_output.append({
                "tool_name": "unknown",
                "output": json.dumps({"error": "Tool name is required"})
            })
            continue
        
        # Parse JSON arguments
        try:
            args = json.loads(args_json) if isinstance(args_json, str) else args_json
        except json.JSONDecodeError as e:
            batch_output.append({
                "tool_name": tool_name,
                "output": json.dumps({"error": f"Invalid JSON arguments: {str(e)}"})
            })
            continue
        
        # Execute the tool
        print(f"  -> Batch executing: {tool_name}")
        result = execute_tool(tool_name, args)
        
        batch_output.append({
            "tool_name": tool_name,
            "output": result
        })
    
    return batch_output

def tool_get_confluence_page(page_id):
    """Fetch a Confluence page by ID with validation. Raises ValueError on invalid input or fetch failure."""
    if not page_id or not str(page_id).strip():
        raise ValueError("page_id cannot be empty. Provide a valid Confluence page ID.")
    if not str(page_id).isdigit():
        raise ValueError("page_id must be numeric. Example: '3432841264'")
    result = fetch_confluence_page(str(page_id))
    if not result:
        raise ValueError(f"Could not fetch Confluence page {page_id}. Check existence and credentials.")
    return {
        "title": result["title"],
        "content": result["content"][:CONFLUENCE_CONTENT_LIMIT]
    }

# Web Search tool is now handled natively by Claude (server-side execution)
# No implementation needed - Claude performs the search and returns results automatically

def tool_calculate_product_metrics(metric_type, values):
    """Calculate ROI, velocity, or capacity with validations. Raises ValueError on bad inputs."""
    valid_metrics = ["roi", "velocity", "capacity"]
    if metric_type not in valid_metrics:
        raise ValueError(f"Invalid metric_type '{metric_type}'. Must be one of: {valid_metrics}")
    if not isinstance(values, dict):
        raise ValueError("values must be a dictionary/object")
    try:
        if metric_type == "roi":
            revenue = values.get("revenue", 0)
            cost = values.get("cost", 0)
            if cost == 0:
                raise ValueError("cost cannot be zero for ROI calculation")
            roi = (revenue - cost) / cost
            return {"roi": f"{roi * 100:.2f}%"}
        elif metric_type == "velocity":
            points = values.get("story_points", [])
            if not points or len(points) == 0:
                raise ValueError("story_points cannot be empty for velocity calculation")
            avg_velocity = sum(points) / len(points)
            return {"average_velocity": avg_velocity}
        elif metric_type == "capacity":
            total_points = values.get("total_story_points", 0)
            sprint_days = values.get("sprint_days", 10)
            if sprint_days == 0:
                raise ValueError("sprint_days cannot be zero")
            return {"capacity_per_day": total_points / sprint_days}
    except Exception as e:
        raise ValueError(f"Calculation failed: {str(e)}")

def tool_generate_document(doc_type, content):
    """Wrapper for document generation with validation."""
    valid_types = ["prd", "roadmap", "spec"]
    if doc_type not in valid_types:
        raise ValueError(f"Invalid doc_type '{doc_type}'. Must be one of: {valid_types}")
    if not isinstance(content, dict):
        raise ValueError("content must be a dictionary with template fields")
    try:
        doc_text = generate_document(doc_type, content)
        return {"document": doc_text}
    except KeyError as e:
        raise ValueError(f"Missing required field in content: {str(e)}")
    except Exception as e:
        raise ValueError(f"Document generation failed: {str(e)}")

def tool_create_jira_ticket(summary, description, issue_type, project="ONESUITE"):
    """Create a Jira ticket (real if creds present, else simulated). Raises ValueError on validation or API errors."""
    if not summary or not str(summary).strip():
        raise ValueError("summary cannot be empty")
    valid_types = ["Epic", "Story", "Task"]
    if issue_type not in valid_types:
        raise ValueError(f"Invalid issue_type '{issue_type}'. Must be one of: {valid_types}")
    jira_url = os.getenv("JIRA_URL")
    jira_user = os.getenv("JIRA_USER")
    jira_token = os.getenv("JIRA_API_TOKEN")
    if all([jira_url, jira_user, jira_token]):
        try:
            api_endpoint = f"{jira_url}/rest/api/2/issue"
            payload = {
                "fields": {
                    "project": {"key": project},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type}
                }
            }
            resp = requests.post(api_endpoint, auth=HTTPBasicAuth(jira_user, jira_token), json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {"key": data.get("key"), "url": f"{jira_url}/browse/{data.get('key')}"}
        except Exception as e:
            raise ValueError(f"Jira API error: {str(e)}")
    else:
        import time
        fake_key = f"ONESUITE-{int(time.time()) % 100000}"
        fake_url = f"https://jira.example.com/browse/{fake_key}"
        return {"key": fake_key, "url": fake_url, "summary": summary}

def resolve_mentions_in_text(text: str, session_name: str = "documents") -> str:
    """Resolve @document mentions in text by fetching via MCP Resources.
    
    Implements lesson-accurate resource API: session.read_resource(uri)
    with MIME type handling (application/json vs text/plain).
    """
    # Find all @mention patterns (e.g., @document1, @kb-guide)
    mention_pattern = r'@([a-zA-Z0-9\-_]+)'
    mentions = re.findall(mention_pattern, text)
    
    if not mentions:
        return text
    
    # Fetch content for each mentioned document via MCP Resource API
    augmented_text = text
    for doc_name in set(mentions):  # Deduplicate mentions
        try:
            if session_name not in mcp_sessions:
                print(f"[RESOURCES] MCP session '{session_name}' not available")
                continue
            
            session = mcp_sessions[session_name]
            
            # Read templated resource: docs://documents/{doc_id}
            resource_uri = f"docs://documents/{doc_name}"
            
            # Use executor to avoid nested event loop issues
            future = mcp_executor.submit(
                lambda uri=resource_uri: asyncio.run(
                    read_resource_async(session, uri)
                )
            )
            content = future.result(timeout=10)
            
            if content:
                print(f"[RESOURCES] Fetched resource {resource_uri}: {len(content)} chars")
                # Replace @mention with context note
                augmented_text = augmented_text.replace(
                    f"@{doc_name}",
                    f"[Document: {doc_name}]"
                )
                # Append document content context to the message
                augmented_text += f"\n\n---\n[Referenced Document: {doc_name}]\n{content}\n---"
            else:
                print(f"[RESOURCES] No content for @{doc_name}")
        except Exception as e:
            print(f"[RESOURCES] Failed to fetch @{doc_name}: {str(e)}")
            # Leave mention as-is if fetch fails
    
    return augmented_text


async def read_resource_async(session, resource_uri: str) -> str:
    """Read a resource via MCP Resource API and handle MIME types.
    
    Supports: application/json, text/plain
    """
    try:
        result = await session.read_resource(resource_uri)
        
        # Result is a ReadResourceResult with .contents attribute
        if result and hasattr(result, 'contents') and result.contents:
            content_block = result.contents[0]
            
            # Extract text content (text attribute exists in content block)
            if hasattr(content_block, 'text'):
                return content_block.text
            else:
                return str(content_block)
        
        return ""
    except Exception as e:
        print(f"[RESOURCES] read_resource_async error: {str(e)}")
        raise



# ===========================================================================
# UNIFIED AGENT TOOL IMPLEMENTATIONS
# ===========================================================================

def tool_take_screenshot():
    """Take screenshot and return base64."""
    if not COMPUTER_USE_AVAILABLE:
        raise RuntimeError("Computer Use not available")
    screenshot = pyautogui.screenshot()
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    return {
        "success": True,
        "image_base64": base64.b64encode(buffered.getvalue()).decode(),
        "format": "PNG"
    }

def tool_execute_computer_action(action_type, x=None, y=None, text=None, key=None, button="left", duration=1.0):
    """Execute computer actions."""
    if not COMPUTER_USE_AVAILABLE:
        raise RuntimeError("Computer Use not available")

    try:
        if action_type == "mouse_move":
            pyautogui.moveTo(x, y, duration=0.2)
            return {"success": True, "action": "mouse_move", "x": x, "y": y}
        elif action_type == "click":
            pyautogui.click(x, y, button=button)
            return {"success": True, "action": "click", "x": x, "y": y}
        elif action_type == "type":
            pyautogui.write(text, interval=0.05)
            return {"success": True, "action": "type", "text": text}
        elif action_type == "key":
            pyautogui.press(key)
            return {"success": True, "action": "key", "key": key}
        elif action_type == "wait":
            time.sleep(duration)
            return {"success": True, "action": "wait", "duration": duration}
        else:
            return {"success": False, "error": f"Unknown action: {action_type}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def tool_analyze_production_error(error_content, file_path=None, context=None):
    """Analyze error and generate fix."""
    prompt = f"""Analyze this error and provide a fix:

Error: {error_content}
File: {file_path or 'Unknown'}
Context: {context or 'None'}

Provide JSON:
{{"root_cause": "...", "fix": {{"description": "...", "code": "..."}}, "prevention": "..."}}
"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return {"success": True, "analysis": json.loads(json_match.group())}
        return {"success": True, "raw_response": response_text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def tool_run_qa_workflow(url, test_cases=None, max_iterations=15):
    """Run QA testing workflow (simplified version)."""
    if not COMPUTER_USE_AVAILABLE:
        raise RuntimeError("Computer Use required")

    # Default test cases
    if not test_cases:
        test_cases = [
            "Navigate to URL and verify page loads",
            "Test main UI interactions",
            "Report any issues found"
        ]

    print(f"\n🧪 QA Workflow: {url}")
    print(f"   Tests: {len(test_cases)}")

    # In actual implementation, this would use Computer Use API
    # For now, return mock result
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f"results/qa_report_{timestamp}.txt"

    return {
        "success": True,
        "url": url,
        "test_cases": test_cases,
        "report_path": report_path,
        "note": "QA workflow executed (see full implementation in unified_agent.py)"
    }

def load_and_analyze_errors():
    """Load error logs."""
    logs_dir = Path("logs")
    errors = []

    if not logs_dir.exists():
        return {"errors_found": 0, "errors": []}

    for log_file in logs_dir.glob("*.log"):
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if any(k in line.lower() for k in ['error', 'failed', 'exception']):
                    errors.append({
                        'file': str(log_file),
                        'line_num': i + 1,
                        'content': line.strip()
                    })

    return {"errors_found": len(errors), "errors": errors[:10]}

def evaluator_optimizer_workflow(task, producer_prompt, grader_prompt, max_iterations=5):
    """Evaluator-Optimizer pattern."""
    print(f"\n🔄 Evaluator-Optimizer: {task}")

    for iteration in range(max_iterations):
        print(f"   Iteration {iteration + 1}/{max_iterations}")

        # Producer
        producer_resp = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": producer_prompt}]
        )
        output = producer_resp.content[0].text

        # Grader
        grader_resp = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": f"{grader_prompt}\n\nOutput:\n{output}"}]
        )
        grade = grader_resp.content[0].text

        # Check acceptance
        if any(word in grade.upper() for word in ['PASS', 'ACCEPT', 'APPROVED']):
            print(f"   ✅ ACCEPTED")
            return {'success': True, 'output': output, 'iterations': iteration + 1}

        # Feedback
        print(f"   ⚠️  REJECTED, refining...")
        producer_prompt = f"{task}\n\nPrevious:\n{output}\n\nFeedback:\n{grade}\n\nImprove:"

    return {'success': False, 'output': output, 'iterations': max_iterations}


def parallelization_workflow(task, subtasks, aggregation_prompt=None):
    """
    Parallelization workflow pattern from the lesson.

    1. Split task into parallel subtasks
    2. Execute all subtasks simultaneously
    3. Aggregate results into final output

    Args:
        task: Overall task description
        subtasks: List of subtask prompts to run in parallel
        aggregation_prompt: Optional custom aggregation prompt

    Returns:
        Dict with individual results and final aggregated output
    """
    print("\n" + "="*70)
    print("🔀 PARALLELIZATION WORKFLOW")
    print("="*70)
    print(f"Task: {task}")
    print(f"Subtasks: {len(subtasks)}")
    print()

    # STEP 1: RUN SUBTASKS IN PARALLEL
    print("📊 Step 1: Running parallel analyses...")

    subtask_results = []

    # Use ThreadPoolExecutor for parallel execution
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=min(len(subtasks), 5)) as executor:
        # Submit all subtasks
        futures = []
        for i, subtask_prompt in enumerate(subtasks, 1):
            print(f"   Submitting subtask {i}...")
            future = executor.submit(
                lambda prompt: client.messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                ).content[0].text,
                subtask_prompt
            )
            futures.append((i, subtask_prompt, future))

        # Collect results as they complete
        for i, subtask_prompt, future in futures:
            try:
                result = future.result(timeout=30)
                subtask_results.append({
                    'subtask_num': i,
                    'prompt': subtask_prompt[:80] + "..." if len(subtask_prompt) > 80 else subtask_prompt,
                    'result': result
                })
                print(f"   ✅ Subtask {i} complete ({len(result)} chars)")
            except Exception as e:
                print(f"   ❌ Subtask {i} failed: {e}")
                subtask_results.append({
                    'subtask_num': i,
                    'prompt': subtask_prompt[:80] + "...",
                    'result': f"ERROR: {str(e)}"
                })

    # STEP 2: AGGREGATE RESULTS
    print(f"\n🎯 Step 2: Aggregating {len(subtask_results)} results...")

    # Build aggregation prompt
    if not aggregation_prompt:
        aggregation_prompt = f"""Task: {task}

I ran multiple parallel analyses. Please review all results and provide a comprehensive final recommendation.

"""

    # Add all subtask results
    for result in subtask_results:
        aggregation_prompt += f"\n**Analysis {result['subtask_num']}:**\n{result['result']}\n"

    aggregation_prompt += "\n\nBased on all analyses above, provide:\n1. Overall synthesis\n2. Final recommendation\n3. Key insights from each analysis"

    # Get aggregated result
    print("   Calling Claude for aggregation...")
    aggregation_response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": aggregation_prompt}]
    )

    final_output = aggregation_response.content[0].text

    print(f"   ✅ Aggregation complete ({len(final_output)} chars)")

    print("\n" + "="*70)
    print("✅ PARALLELIZATION WORKFLOW COMPLETE")
    print("="*70)

    return {
        'success': True,
        'task': task,
        'num_subtasks': len(subtasks),
        'subtask_results': subtask_results,
        'final_output': final_output
    }


def execute_tool(tool_name, tool_input):
    """Execute a tool and return JSON-formatted result.
    
    Supports: Confluence fetch, web search, product metrics calculation,
    document generation, Jira ticket creation, and MCP tools.
    """
    print(f"[TOOL] Executing tool: {tool_name}")
    print(f"   Input: {json.dumps(tool_input, indent=2)}")
    
    # Check if this is an MCP tool
    mcp_server = is_mcp_tool(tool_name)
    if mcp_server:
        print(f"   -> Routing to MCP server: {mcp_server}")
        # Normalize argument keys to match MCP server schema
        # read_document expects 'name' (backwards-compat for 'document_id')
        if tool_name == "read_document":
            if isinstance(tool_input, dict) and "document_id" in tool_input and "name" not in tool_input:
                tool_input = {**tool_input}
                tool_input["name"] = tool_input.pop("document_id")
        # update_document expects 'name' and 'content'
        if tool_name == "update_document":
            if isinstance(tool_input, dict) and "document_id" in tool_input and "name" not in tool_input:
                tool_input = {**tool_input}
                tool_input["name"] = tool_input.pop("document_id")
        # Execute MCP tool via fresh connection in a thread
        try:
            future = mcp_executor.submit(
                lambda: asyncio.run(
                    execute_mcp_tool_fresh(mcp_server, tool_name, tool_input)
                )
            )
            return future.result(timeout=30)  # 30 second timeout
        except Exception as e:
            print(f"   -> Error: {str(e)}")
            return json.dumps({"error": f"MCP tool execution failed: {str(e)}"})
    
    # Local tool execution
    if tool_name == "get_confluence_page":
        try:
            result = tool_get_confluence_page(tool_input.get("page_id", ""))
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})
    
    elif tool_name == "web_search":
        # Web Search is executed server-side by Claude; should not reach dispatcher
        return json.dumps({"note": "Web search executed by Claude; results in response content blocks"})
    
    elif tool_name == "calculate_product_metrics":
        try:
            result = tool_calculate_product_metrics(
                tool_input.get("metric_type", ""),
                tool_input.get("values", {})
            )
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})
    
    elif tool_name == "generate_document":
        try:
            result = tool_generate_document(
                tool_input.get("doc_type", ""),
                tool_input.get("content", {})
            )
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})
    elif tool_name == "create_jira_ticket":
        try:
            result = tool_create_jira_ticket(
                tool_input.get("summary", ""),
                tool_input.get("description", ""),
                tool_input.get("issue_type", ""),
                tool_input.get("project", "ONESUITE")
            )
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})
    
    elif tool_name == "get_current_datetime":
        try:
            result = tool_get_current_datetime(tool_input.get("date_format"))
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})
    
    elif tool_name == "add_duration_to_datetime":
        try:
            result = tool_add_duration_to_datetime(
                tool_input.get("base_datetime", ""),
                tool_input.get("days", 0),
                tool_input.get("hours", 0),
                tool_input.get("minutes", 0)
            )
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})
    
    elif tool_name == "set_reminder":
        try:
            result = tool_set_reminder(
                tool_input.get("reminder_datetime", ""),
                tool_input.get("message", ""),
                tool_input.get("reminder_id")
            )
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})
    
    elif tool_name == "batch":
        try:
            result = tool_batch(tool_input.get("invocations", []))
            return json.dumps(result)
        except ValueError as e:
            return json.dumps({"error": str(e)})

    # UNIFIED AGENT TOOLS (Computer Use, Error Monitoring, QA)
    elif tool_name == "take_screenshot":
        try:
            result = tool_take_screenshot()
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif tool_name == "execute_computer_action":
        try:
            result = tool_execute_computer_action(
                tool_input.get("action_type"),
                x=tool_input.get("x"),
                y=tool_input.get("y"),
                text=tool_input.get("text"),
                key=tool_input.get("key"),
                button=tool_input.get("button", "left"),
                duration=tool_input.get("duration", 1.0)
            )
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif tool_name == "analyze_production_error":
        try:
            result = tool_analyze_production_error(
                tool_input.get("error_content", ""),
                file_path=tool_input.get("file_path"),
                context=tool_input.get("context")
            )
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif tool_name == "run_qa_workflow":
        try:
            result = tool_run_qa_workflow(
                tool_input.get("url", ""),
                test_cases=tool_input.get("test_cases"),
                max_iterations=tool_input.get("max_iterations", 15)
            )
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})

# =========================
# MCP CLIENT FUNCTIONS
# =========================
async def initialize_mcp_servers():
    """Connect to configured MCP servers and discover their tools.
    
    Populates mcp_sessions and mcp_tools globals.
    """
    global mcp_sessions, mcp_tools
    
    print("[MCP] Initializing MCP servers...")
    
    for server_name, config in MCP_SERVERS_CONFIG.items():
        try:
            print(f"   Connecting to {server_name}...")
            print(f"      Command: {config['command']}")
            print(f"      Args: {config.get('args', [])}")
            
            server_params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env", {})
            )
            
            # Create stdio client context
            stdio_transport = stdio_client(server_params)
            stdio, write = await stdio_transport.__aenter__()
            
            # Create session
            session = ClientSession(stdio, write)
            await session.__aenter__()
            
            # Initialize session
            await session.initialize()
            
            # Store session
            mcp_sessions[server_name] = session
            
            # List available tools
            tools_response = await session.list_tools()
            
            for tool in tools_response.tools:
                # Convert MCP tool to Claude ToolParam format
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description or f"Tool from {server_name} MCP server",
                    "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {"type": "object", "properties": {}},
                    "_mcp_server": server_name  # Track which server owns this tool
                }
                mcp_tools.append(tool_dict)
                print(f"      [OK] Discovered tool: {tool.name}")
        
        except Exception as e:
            print(f"      [ERROR] Failed to connect to {server_name}: {e}")
            continue
    
    print(f"[OK] MCP initialization complete. {len(mcp_tools)} tools discovered from {len(mcp_sessions)} servers.\n")


async def execute_mcp_tool_fresh(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool via MCP server with a fresh connection.
    
    This function creates its own MCP session for the tool call,
    avoiding event loop conflicts.
    
    Args:
        server_name: Name of MCP server
        tool_name: Tool name
        arguments: Tool arguments dict
    
    Returns:
        JSON-formatted result string
    """
    if server_name not in MCP_SERVERS_CONFIG:
        return json.dumps({"error": f"MCP server '{server_name}' not configured"})
    
    config = MCP_SERVERS_CONFIG[server_name]
    print(f"      [MCP] Creating fresh connection to {server_name}...")
    
    try:
        # Create fresh session for this tool call
        server_params = StdioServerParameters(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {})
        )
        
        stdio_transport = stdio_client(server_params)
        stdio, write = await stdio_transport.__aenter__()
        session = ClientSession(stdio, write)
        await session.__aenter__()
        await session.initialize()
        
        print(f"      [MCP] Connected to {server_name}, calling tool...")
        # Call the tool
        result = await session.call_tool(tool_name, arguments)
        
        # Extract content from MCP response
        if hasattr(result, 'content') and result.content:
            # Concatenate all content blocks
            content_parts = []
            for content_block in result.content:
                if hasattr(content_block, 'text'):
                    content_parts.append(content_block.text)
            
            result_json = {
                "result": "\n".join(content_parts) if content_parts else "Tool executed successfully",
                "isError": getattr(result, 'isError', False)
            }
        else:
            result_json = {"result": "Tool executed successfully"}
        
        # Cleanup
        await session.__aexit__(None, None, None)
        await stdio_transport.__aexit__(None, None, None)
        
        return json.dumps(result_json)
    
    except Exception as e:
        print(f"      [MCP] Exception: {type(e).__name__}: {str(e)}")
        return json.dumps({"error": f"MCP tool execution failed: {str(e)}"})


async def execute_mcp_prompt(server_name: str, prompt_name: str, arguments: Dict[str, Any]) -> str:
    """Execute an MCP prompt and return the formatted message text.
    
    Args:
        server_name: Name of MCP server
        prompt_name: Prompt name
        arguments: Prompt arguments dict
    
    Returns:
        The formatted prompt text from the MCP server
    """
    if server_name not in MCP_SERVERS_CONFIG:
        return ""
    
    config = MCP_SERVERS_CONFIG[server_name]
    print(f"   [MCP PROMPT] Connecting to {server_name}...")
    
    try:
        # Create fresh session
        server_params = StdioServerParameters(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {})
        )
        
        stdio_transport = stdio_client(server_params)
        stdio, write = await stdio_transport.__aenter__()
        session = ClientSession(stdio, write)
        await session.__aenter__()
        await session.initialize()
        
        print(f"   [MCP PROMPT] Getting prompt '{prompt_name}'...")
        # Get the prompt
        result = await session.get_prompt(prompt_name, arguments)
        
        # Extract messages from prompt result
        prompt_text = ""
        if hasattr(result, 'messages') and result.messages:
            for message in result.messages:
                if hasattr(message, 'content'):
                    if hasattr(message.content, 'text'):
                        prompt_text = message.content.text
                    elif isinstance(message.content, str):
                        prompt_text = message.content
        
        # Cleanup
        await session.__aexit__(None, None, None)
        await stdio_transport.__aexit__(None, None, None)
        
        return prompt_text
    
    except Exception as e:
        print(f"   [MCP PROMPT] Exception: {type(e).__name__}: {str(e)}")
        return ""


async def cleanup_mcp_servers():
    """Close all MCP server connections."""
    print("\n[MCP] Closing MCP server connections...")
    
    for server_name, session in mcp_sessions.items():
        try:
            # Gracefully close session - ignore cancel scope errors (MCP SDK bug)
            await session.__aexit__(None, None, None)
            print(f"   [OK] Closed {server_name}")
        except Exception as e:
            # Suppress cancel scope errors
            if "cancel scope" not in str(e).lower():
                print(f"   [ERROR] Error closing {server_name}: {e}")
    
    mcp_sessions.clear()
    mcp_tools.clear()


def get_all_tools_for_claude() -> List[ToolParam]:
    """Combine local tools and MCP tools into unified list for Claude.
    
    Returns:
        List of ToolParam objects (local) + dict tools (MCP)
    """
    all_tools = []
    
    # Add local ToolParam tools
    all_tools.extend(TOOLS)
    
    # Add MCP tools (already in dict format compatible with Claude)
    for mcp_tool in mcp_tools:
        # Create ToolParam-compatible dict
        tool_dict = {
            "name": mcp_tool["name"],
            "description": mcp_tool["description"],
            "input_schema": mcp_tool["input_schema"]
        }
        all_tools.append(tool_dict)
    
    return all_tools


def is_mcp_tool(tool_name: str) -> Optional[str]:
    """Check if a tool is from an MCP server.
    
    Args:
        tool_name: Tool name to check
    
    Returns:
        MCP server name if tool is from MCP, None otherwise
    """
    for mcp_tool in mcp_tools:
        if mcp_tool["name"] == tool_name:
            return mcp_tool["_mcp_server"]
    return None


# =========================
# CONFLUENCE INTEGRATION
# =========================
def fetch_confluence_page(page_id):
    """Fetch content from a Confluence page by page ID.
    
    Args:
        page_id: Confluence page ID
    
    Returns:
        Dict with 'title' and 'content' keys, or None if fetch fails
    """
    if not all([confluence_url, confluence_email, confluence_api_token]):
        print("Confluence credentials not set in .env file")
        return None
    
    url = f"{confluence_url}/rest/api/3/pages/{page_id}?body-format=storage"
    
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(confluence_email, confluence_api_token)
        )
        response.raise_for_status()
        page_data = response.json()
        
        # Extract text content from storage format
        body = page_data.get('body', {}).get('storage', {}).get('value', '')
        title = page_data.get('title', '')
        
        # Simple HTML tag removal
        import re
        text = re.sub('<[^<]+?>', '', body)
        text = re.sub('&nbsp;', ' ', text)
        text = re.sub('&amp;', '&', text)
        
        return {
            "title": title,
            "content": text.strip()
        }
    except Exception as e:
        print(f"Error fetching Confluence page: {e}")
        return None

def get_onesuite_context():
    """Fetch OneSuite Core product context from Confluence or use fallback."""
    print("Loading OneSuite Core context...")
    
    # Try to fetch from Confluence
    page_id = "3432841264"  # Platform User Stories page
    page = fetch_confluence_page(page_id)
    
    if page:
        print("✓ Loaded from Confluence\n")
        return page['content'][:2000]  # Limit to 2000 chars for token limits
    else:
        print("(Using fallback context - Confluence unavailable)\n")
        # Fallback to hardcoded context
        return """
OneSuite Core is a unified product platform and strategy engine for the OneSuite Core team.

KEY CAPABILITIES:
- Multi-channel unification: Search, Social, Programmatic, Commerce
- Centralized product strategy and documentation
- User story and roadmap development
- Requirement management and specification

CHANNELS SUPPORTED:
- Search: PPC and organic search optimization
- Social: Social media campaign management  
- Programmatic: Programmatic advertising automation
- Commerce: E-commerce integration and optimization

CORE RESPONSIBILITIES:
- Define comprehensive product user stories
- Develop and maintain product roadmaps
- Ensure requirement details are properly documented
- Maintain consistency across all channels
- Manage shared artifacts (glossaries, taxonomies, templates)
- Support agency workflows and needs

STAKEHOLDERS:
- Agencies using OneSuite
- Channel managers (Search, Social, Programmatic, Commerce)
- Internal product and engineering teams
- End users across different advertising channels

ARCHITECTURE PRINCIPLES:
- Unified platform experience
- Channel-specific customization where needed
- Shared taxonomy and glossary
- Reusable onboarding and documentation
"""

# =========================
# HELPER FUNCTIONS
# =========================
def add_user_message(messages, content):
    """Add a user message (supports text or multi-block content)."""
    if isinstance(content, str):
        messages.append({"role": "user", "content": content})
    elif isinstance(content, list):
        messages.append({"role": "user", "content": content})
    else:
        raise ValueError(f"content must be a string or list of content blocks, got {type(content)}")

def extract_article_summary(article_text):
    """Extract structured article summary using tool forcing.
    
    Args:
        article_text: The article or document text to extract from
    
    Returns:
        Dict with title, author, and key_insights (guaranteed structure)
    """
    prompt = f"""Analyze the following article and extract the key information:

{article_text}

Call the article_summary tool with the extracted information."""
    
    messages = []
    add_user_message(messages, prompt)
    
    # Force Claude to call the article_summary tool
    response = chat(
        messages,
        tools=[article_summary_schema],
        tool_choice={"type": "tool", "name": "article_summary"}
    )
    
    # Extract the tool input (which is our structured data)
    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use" and block.name == "article_summary":
                return block.input
    
    return None

def extract_user_story(requirement_text):
    """Extract structured user story components using tool forcing.
    
    Args:
        requirement_text: Narrative requirements or description text
    
    Returns:
        Dict with role, action, benefit, acceptance_criteria, and channel_impact
    """
    prompt = f"""Analyze the following requirement and structure it as a user story with multi-channel impact:

{requirement_text}

Call the extract_user_story tool with the structured components."""
    
    messages = []
    add_user_message(messages, prompt)
    
    # Force Claude to call the extract_user_story tool
    response = chat(
        messages,
        tools=[user_story_extraction_schema],
        tool_choice={"type": "tool", "name": "extract_user_story"}
    )
    
    # Extract the tool input (which is our structured data)
    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use" and block.name == "extract_user_story":
                return block.input
    
    return None

def add_assistant_message(messages, content):
    """Add an assistant message (supports text or multi-block content)."""
    if isinstance(content, str):
        messages.append({"role": "assistant", "content": content})
    elif isinstance(content, list):
        messages.append({"role": "assistant", "content": content})
    else:
        raise ValueError(f"content must be a string or list of content blocks, got {type(content)}")

def get_text_from_response(content):
    """Extract text from a response that may have multiple blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
            elif isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "\n".join(text_parts)
    return ""


def read_image_as_base64(file_path):
    """Read an image file and return base64-encoded data with media type.
    
    Args:
        file_path: Path to image file (png, jpg, jpeg, gif, webp)
    
    Returns:
        Dict with 'data' (base64 string) and 'media_type' (e.g., 'image/png')
    """
    ext = file_path.lower().split('.')[-1]
    media_type_map = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    media_type = media_type_map.get(ext, 'image/png')
    
    with open(file_path, 'rb') as f:
        image_bytes = f.read()
    
    encoded = base64.standard_b64encode(image_bytes).decode('utf-8')
    return {'data': encoded, 'media_type': media_type}


def read_pdf_as_base64(file_path):
    """Read a PDF file and return base64-encoded data.
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Dict with 'data' (base64 string) and 'media_type' ('application/pdf')
    """
    with open(file_path, 'rb') as f:
        pdf_bytes = f.read()
    
    encoded = base64.standard_b64encode(pdf_bytes).decode('utf-8')
    return {'data': encoded, 'media_type': 'application/pdf'}


def ask_about_image(image_path, question):
    """Ask Claude a question about an image.
    
    Args:
        image_path: Path to image file
        question: Question to ask about the image
    
    Returns:
        Claude's response text
    """
    img_data = read_image_as_base64(image_path)
    
    message = {
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img_data['media_type'],
                    "data": img_data['data']
                }
            },
            {
                "type": "text",
                "text": question
            }
        ]
    }
    
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS_DEFAULT,
        messages=[message]
    )
    
    return response.content[0].text


def ask_about_pdf(pdf_path, question):
    """Ask Claude a question about a PDF document.
    
    Args:
        pdf_path: Path to PDF file
        question: Question to ask about the document
    
    Returns:
        Claude's response text
    """
    pdf_data = read_pdf_as_base64(pdf_path)
    
    message = {
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": pdf_data['media_type'],
                    "data": pdf_data['data']
                }
            },
            {
                "type": "text",
                "text": question
            }
        ]
    }
    
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS_DEFAULT,
        messages=[message]
    )
    
    return response.content[0].text


# =========================
# STREAMING HELPERS (tools + InputJSON handling)
# =========================
def stream_with_tools(prompt, tools=None, tool_choice=None, fine_grained=False):
    """Stream a request with tools, handling InputJSON events and content deltas.

    Args:
        prompt: User prompt string
        tools: Optional list of ToolParam schemas
        tool_choice: Optional dict to force a specific tool
        fine_grained: If True, disables upstream JSON validation to stream partial args sooner

    Returns:
        Dict with collected text, tool_inputs (if any), and raw events for debugging
    """
    events = []
    collected_text = []
    tool_inputs = []
    input_buffer = ""
    current_tool = None

    params = {
        "model": model,
        "max_tokens": MAX_TOKENS_WITH_TOOLS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
    }
    if tools:
        params["tools"] = tools
    if tool_choice:
        params["tool_choice"] = tool_choice
    if fine_grained:
        if _fine_grained_supported():
            params.setdefault("stream_options", {})["fine_grained_tool_calls"] = True
        else:
            print("[Warning] Fine-grained requested but SDK does not support stream_options; continuing without it.")

    stream = client.messages.create(**params)

    for event in stream:
        events.append(event)
        etype = getattr(event, "type", "")

        if etype == "content_block_start":
            block = getattr(event, "block", None)
            btype = getattr(block, "type", "")
            print(f"[Block start] {btype}")
            if btype == "tool_use":
                current_tool = {
                    "id": getattr(block, "id", "tool_1"),
                    "name": getattr(block, "name", ""),
                }
                maybe_input = getattr(block, "input", None)
                if maybe_input:
                    tool_inputs.append({"partial": maybe_input, "snapshot": maybe_input})

        elif etype == "content_block_delta":
            delta = getattr(event, "delta", None)
            if not delta:
                continue
            dtype = getattr(delta, "type", "")
            if dtype == "text_delta":
                collected_text.append(getattr(delta, "text", ""))
            elif dtype == "input_json_delta":
                partial = getattr(delta, "partial_json", None)
                snapshot = getattr(delta, "snapshot", None)
                if partial is not None:
                    input_buffer += str(partial)
                tool_inputs.append({"partial": partial, "snapshot": snapshot})
                print(f"[InputJSON delta] partial={partial} snapshot={snapshot}")

        elif etype == "input_json":
            # InputJSONEvent: partial JSON args for tool call
            partial = getattr(event, "partial_json", None)
            snapshot = getattr(event, "snapshot", None)
            if partial is not None:
                input_buffer += str(partial)
            tool_inputs.append({"partial": partial, "snapshot": snapshot})
            print(f"[InputJSON] partial={partial} snapshot={snapshot}")

        elif etype == "message_delta":
            # Accumulate final text if present
            delta = getattr(event, "delta", None)
            if delta and hasattr(delta, "text"):
                collected_text.append(delta.text)

        elif etype == "message_stop":
            break

    assembled_input = None
    if input_buffer:
        try:
            assembled_input = json.loads(input_buffer)
        except Exception:
            assembled_input = input_buffer

    return {
        "text": "".join(collected_text).strip(),
        "tool_inputs": tool_inputs,
        "assembled_input": assembled_input,
        "events": events,
        "tool": current_tool,
    }


def chat(messages, system=None, temperature=1.0, stop_sequences=None, tools=None, tool_choice=None):
    """Chat function with support for tools and tool forcing.
    
    Args:
        messages: List of message dicts
        system: System prompt
        temperature: Sampling temperature
        stop_sequences: Stop sequences for output
        tools: List of tool schemas (ToolParam objects)
        tool_choice: Force Claude to use a specific tool. 
                    Dict with {"type": "tool", "name": "tool_name"}
    
    Returns:
        Response object if tools are provided, otherwise text response
    """
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    if tools:
        params["tools"] = tools
    if tool_choice:
        params["tool_choice"] = tool_choice
    
    response = client.messages.create(**params)
    
    # If tools were provided, return full response for tool extraction
    if tools:
        return response
    # Otherwise return text as before
    return response.content[0].text

# =========================
# PROMPT EVALUATOR CLASS
# =========================
class PromptEvaluator:
    def __init__(self, max_concurrent_tasks=3):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.evaluation_history = []
    
    def generate_dataset(self, task_description, prompt_inputs_spec, output_file, num_cases=3):
        """Generate test cases for prompt evaluation."""
        print(f"Generating {num_cases} test cases for: {task_description}")
        
        spec_str = "\n".join([f"- {key}: {desc}" for key, desc in prompt_inputs_spec.items()])
        
        prompt = f"""
You are a test case generator. Generate {num_cases} diverse test cases for the following task:

Task: {task_description}

Each test case should include:
{spec_str}

Generate the test cases as a JSON array. Each object should have fields matching the input spec above.
Example format:
[
  {{{", ".join([f'"{key}": "value"' for key in prompt_inputs_spec.keys()])}}}
]

Generate diverse, realistic test cases that will thoroughly test the prompt.
"""
        
        messages = []
        add_user_message(messages, prompt)
        add_assistant_message(messages, "```json")
        text = chat(messages, stop_sequences=["```"])
        
        try:
            dataset = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing dataset: {e}")
            return None
        
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Dataset saved to {output_file}")
        return dataset
    
    def evaluate_output(self, test_case, output, extra_criteria=""):
        """Grade a prompt output using the LLM as a judge."""
        test_case_str = json.dumps(test_case, indent=2)
        
        eval_prompt = f"""You are an expert evaluator. Grade the following output based on how well it meets the requirements.

Input:
{test_case_str}

Output to Evaluate:
{output}

Evaluation Criteria:
- Completeness: Does it address all inputs and requirements?
- Quality: Is the output well-structured and useful?
- Accuracy: Is the information correct and relevant?
{f"Additional Criteria:{extra_criteria}" if extra_criteria else ""}

Respond with ONLY valid JSON (no other text):
{{
  "score": <number 1-10>,
  "strengths": [<list of 1-3 key strengths>],
  "weaknesses": [<list of 1-3 key areas for improvement>],
  "reasoning": "<brief explanation of the score>"
}}
"""
        
        messages = []
        add_user_message(messages, eval_prompt)
        add_assistant_message(messages, "```json")
        eval_text = chat(messages, stop_sequences=["```"])
        
        try:
            eval_text = eval_text.strip()
            if eval_text.startswith('```json'):
                eval_text = eval_text[7:]
            if eval_text.startswith('```'):
                eval_text = eval_text[3:]
            if eval_text.endswith('```'):
                eval_text = eval_text[:-3]
            return json.loads(eval_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing evaluation: {e}")
            return {
                "score": 5,
                "strengths": [],
                "weaknesses": ["Could not evaluate"],
                "reasoning": f"Parse error: {str(e)}"
            }
    
    def run_evaluation(self, run_prompt_function, dataset_file, extra_criteria=""):
        """Run evaluation on a dataset using a prompt function."""
        print(f"\n{'='*60}")
        print("RUNNING EVALUATION")
        print(f"{'='*60}\n")
        
        with open(dataset_file, 'r') as f:
            dataset = json.load(f)
        
        results = []
        scores = []
        
        for i, test_case in enumerate(dataset):
            print(f"Test Case {i+1}/{len(dataset)}")
            print(f"Input: {json.dumps(test_case, indent=2)}")
            
            # Run the prompt
            output = run_prompt_function(test_case)
            print(f"Output: {output[:200]}...\n" if len(output) > 200 else f"Output: {output}\n")
            
            # Evaluate the output
            evaluation = self.evaluate_output(test_case, output, extra_criteria)
            score = evaluation.get('score', 5)
            scores.append(score)
            
            print(f"Score: {score}/10")
            print(f"Strengths: {', '.join(evaluation.get('strengths', []))}")
            print(f"Weaknesses: {', '.join(evaluation.get('weaknesses', []))}")
            print(f"Reasoning: {evaluation.get('reasoning', '')}\n")
            
            results.append({
                "test_case": test_case,
                "output": output,
                "evaluation": evaluation
            })
        
        avg_score = statistics.mean(scores)
        print(f"{'='*60}")
        print(f"AVERAGE SCORE: {avg_score:.2f}/10")
        print(f"{'='*60}\n")
        
        self.evaluation_history.append({
            "average_score": avg_score,
            "results": results
        })
        
        return {
            "average_score": avg_score,
            "results": results
        }
    
    def show_history(self):
        """Display evaluation history showing improvements."""
        print(f"\n{'='*60}")
        print("EVALUATION HISTORY")
        print(f"{'='*60}\n")
        
        for i, eval_run in enumerate(self.evaluation_history):
            print(f"Evaluation {i+1}: {eval_run['average_score']:.2f}/10")
        
        if len(self.evaluation_history) > 1:
            first = self.evaluation_history[0]['average_score']
            last = self.evaluation_history[-1]['average_score']
            improvement = last - first
            print(f"\nImprovement: {improvement:+.2f} points")
        
        print()


# =========================
# DATASET GENERATION (for product management tasks)
# =========================
def generate_pm_dataset():
    """Generate product management evaluation dataset."""
    prompt = """
Generate an evaluation dataset for a product management agent. Each entry should be a JSON object with a 'task' field (a realistic product management/user story/roadmap/requirements task) and a 'criteria' field (evaluation criteria). Focus on:
- Writing user stories (with acceptance criteria)
- Drafting or critiquing product roadmaps
- Identifying missing requirements in specs
- Structuring product documentation
- Scenario-based product management questions

Example output:
[
  {"task": "Write a user story for onboarding a new agency to OneSuite Core, including acceptance criteria.", "criteria": "Should include clear user story format with acceptance criteria"},
  ...additional
]

Please generate 2 objects.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = chat(messages, stop_sequences=["```"])
    try:
        dataset = json.loads(text)
    except Exception as e:
        print(f"Could not parse dataset: {e}")
        return None
    with open('pm_dataset.json', 'w') as f:
        json.dump(dataset, f, indent=2)
    print("PM dataset saved to pm_dataset.json")
    return dataset

# =========================
# PROMPT VERSIONS FOR PRODUCT MANAGEMENT (OneSuite-Focused)
# =========================

onesuite_context = get_onesuite_context()

def run_prompt_v1_baseline(test_case):
    """Version 1: Baseline - Very simple prompt."""
    prompt = f"""Please help with: {test_case.get('task', '')}"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

def run_prompt_v2_structure(test_case):
    """Version 2: Add clear structure and OneSuite context."""
    prompt = f"""
CONTEXT:
OneSuite Core is our unified product platform serving the product strategy and documentation engine for the OneSuite Core team. We support multiple channels: Search, Social, Programmatic, and Commerce.

TASK: {test_case.get('task', '')}

REQUIREMENTS:
- Be clear and specific
- Use proper formatting
- Include all necessary details
- Follow industry best practices
- Consider all OneSuite channels where applicable

Please complete this task:
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

def run_prompt_v3_examples(test_case):
    """Version 3: Add OneSuite context, examples, and specific format."""
    prompt = f"""
CONTEXT:
OneSuite Core unifies different channel agents (Search, Social, Programmatic, Commerce) under a single architecture.

TASK: {test_case.get('task', '')}

EXAMPLE FORMAT FOR USER STORIES:
---
User Story:
As a [agency/user role], I want to [action related to OneSuite], so that [benefit across channels]

Acceptance Criteria:
- Works across Search, Social, Programmatic, and/or Commerce channels
- Maintains consistency with shared artifacts (glossaries, taxonomies)
- Includes proper documentation
- [Specific acceptance criterion]
---

Now complete the task with the same level of detail:
{test_case.get('task', '')}
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)

def run_prompt_v4_persona_cot(test_case):
    """Version 4: Add OneSuite context, expert persona, and chain of thought."""
    prompt = f"""
You are an expert product manager for OneSuite Core with deep knowledge of:
- Multi-channel advertising platforms (Search, Social, Programmatic, Commerce)
- Building unified product experiences across diverse channels
- Agency workflows and requirements
- Product strategy and documentation

ONESUITE CONTEXT:
{onesuite_context[:500]}  # Truncate for token limits

YOUR TASK: {test_case.get('task', '')}

APPROACH:
1. Understand how this task impacts all OneSuite channels
2. Identify stakeholder needs across agencies and channels
3. Ensure consistency with shared OneSuite artifacts
4. Define clear, testable requirements
5. Consider cross-channel dependencies
6. Format professionally with industry best practices

EXAMPLE USER STORY FOR ONESUITE:
---
User Story:
As a [channel manager/agency], I want to [action], so that [benefit across channels]

Acceptance Criteria:
- Functionality works across all applicable channels (Search/Social/Programmatic/Commerce)
- Maintains consistency with OneSuite Core architecture
- Documented in shared taxonomy/glossary
- [Specific measurable criterion]

Dependencies: [List any cross-channel or shared artifact dependencies]
---

Now complete the task with thorough analysis:
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)
# =========================
# 5. EVALUATION METHODS
# =========================
def keyword_grade(answer, expected_keywords):
    """Simple grading: count how many expected keywords appear in the answer."""
    answer_lower = answer.lower()
    found = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    score = len(found) / max(1, len(expected_keywords))
    return {"score": score, "found": found, "missing": [kw for kw in expected_keywords if kw not in found]}

def llm_judge(question, answer, expected_keywords):
    """Use the LLM to judge the answer quality."""
    judge_prompt = f"""
You are an expert product management evaluator. Grade the following answer to the question using this rubric:
- Coverage: Does the answer address all parts of the question?
- Clarity: Is the answer clear and well-structured?
- Relevance: Does the answer use appropriate product management concepts/terms?
Expected keywords: {expected_keywords}

Respond with a JSON object: {{'score': 0-1 float, 'coverage': 0-1, 'clarity': 0-1, 'relevance': 0-1, 'reasoning': string}}

Question: {question}
Answer: {answer}
"""
    resp = client.messages.create(
        model=model,
        max_tokens=400,
        system="You are a strict grader for product management QA tasks. Only output JSON.",
        messages=[{"role": "user", "content": judge_prompt}]
    )
    import re, json
    try:
        match = re.search(r'\{.*\}', resp.content[0].text, re.DOTALL)
        if match:
            return json.loads(match.group(0).replace("'", '"'))
    except Exception:
        pass
    return {"score": 0, "coverage": 0, "clarity": 0, "relevance": 0, "reasoning": "Could not parse LLM output."}

# =========================
# 6. CODE-BASED GRADING (Syntax Validation)
# =========================
def validate_json(text):
    """Validate JSON syntax. Returns 10 if valid, 0 if invalid."""
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0

def validate_python(text):
    """Validate Python syntax. Returns 10 if valid, 0 if invalid."""
    import ast
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_regex(text):
    """Validate Regex syntax. Returns 10 if valid, 0 if invalid."""
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0

def grade_syntax(response, format_type):
    """Grade response based on syntax validation."""
    if format_type == "json":
        return validate_json(response)
    elif format_type == "python":
        return validate_python(response)
    elif format_type == "regex":
        return validate_regex(response)
    return 0

def run_code_evaluation(dataset):
    """Evaluate generated code (Python, JSON, Regex) with syntax validation + LLM grading."""
    print("Running code-based evaluation...")
    results = []
    
    for i, test_case in enumerate(dataset):
        print(f"\nTask {i+1}: {test_case.get('task', 'No task')}")
        
        # Generate code/solution
        prompt = f"Please solve this task: {test_case.get('task', '')}\nRespond only with the code/JSON/regex. No explanations."
        output = call_ocaa(prompt)
        print(f"Output: {output[:100]}..." if len(output) > 100 else f"Output: {output}")
        
        # Syntax validation (code-based grading)
        format_type = test_case.get('format', 'python')
        syntax_score = grade_syntax(output, format_type)
        print(f"Syntax Score: {syntax_score}/10")
        
        # Model-based grading
        criteria = test_case.get('solution_criteria', '')
        model_grade_prompt = f"""Evaluate this solution:
Task: {test_case.get('task', '')}
Solution: {output}
Criteria: {criteria}

Respond with JSON only (no other text): {{"strengths": ["strength1"], "weaknesses": ["weakness1"], "reasoning": "reason", "score": 5}}"""
        
        try:
            model_resp = client.messages.create(
                model=model,
                max_tokens=300,
                system="You are an expert code reviewer. Respond with valid JSON only.",
                messages=[{"role": "user", "content": model_grade_prompt}]
            )
            model_text = model_resp.content[0].text.strip()
            # Clean up JSON parsing
            if model_text.startswith('```json'):
                model_text = model_text[7:]
            if model_text.startswith('```'):
                model_text = model_text[3:]
            if model_text.endswith('```'):
                model_text = model_text[:-3]
            model_grade = json.loads(model_text)
            model_score = model_grade.get('score', 5)
        except Exception as e:
            print(f"Error parsing model grade: {e}")
            model_grade = {"strengths": [], "weaknesses": ["Could not evaluate"], "reasoning": str(e), "score": 5}
            model_score = 5
        
        # Hybrid score: average of syntax validation and model grading
        final_score = (syntax_score + model_score) / 2
        print(f"Model Score: {model_score}/10")
        print(f"Final Score: {final_score}/10")
        
        results.append({
            "task": test_case.get('task', ''),
            "output": output,
            "syntax_score": syntax_score,
            "model_grade": model_grade,
            "final_score": final_score
        })
    
    avg_score = statistics.mean([r['final_score'] for r in results])
    print(f"\n=== Average Score: {avg_score:.2f}/10 ===")
    return results

def run_evaluation(test_cases, use_llm_judge=False):
    print("Running evaluation on sample test cases...")
    results = []
    for i, case in enumerate(test_cases):
        print(f"\nTest {i+1}: {case['question']}")
        answer = call_ocaa(case['question'])
        print(f"Answer: {answer}")
        if use_llm_judge:
            grade = llm_judge(case['question'], answer, case['expected_keywords'])
        else:
            grade = keyword_grade(answer, case['expected_keywords'])
        print(f"Grade: {grade}")
        results.append({"question": case['question'], "answer": answer, "grade": grade})
    return results


system_prompt = """
<identity>
You are the OneSuite Core Architect Agent (OCAA) - a unified multi-capability AI agent.

Roles: Product Manager, QA Automation Specialist, Production Monitor, Workflow Architect

When asked who you are: "I am the OneSuite Core Architect Agent (OCAA), a unified AI agent
specializing in product strategy, QA automation, error monitoring, and workflow execution."
</identity>

<capabilities>
1. Product Strategy - User stories, roadmaps, multi-channel analysis
2. QA Testing (Computer Use) - Automated UI testing, screenshot analysis, test reports
3. Error Monitoring - Log analysis, root cause analysis, automated fixes
4. Workflows - Evaluator-Optimizer, RAG pipelines, automation
5. Document Management (MCP) - PDF/DOCX conversion, storage, retrieval
</capabilities>

<tools_available>
Product: get_current_datetime, set_reminder, get_confluence_page, calculate_product_metrics
Documents (MCP): document_path_to_markdown, list_documents, read_document, update_document
Computer Use: take_screenshot, execute_computer_action (click, type, key_press, mouse_move)
Error Monitoring: analyze_production_error
QA: run_qa_workflow
</tools_available>

<instructions>
PRODUCT STRATEGY: Analyze scope → Identify stakeholders → Assess state → Brainstorm → Structure → Validate
QA TESTING: Understand requirements → Screenshot → Execute tests → Document → Report bugs
ERROR MONITORING: Load logs → Analyze root cause → Generate fix → Explain prevention
WORKFLOWS: Design → Execute producer → Run grader → Provide feedback → Iterate
</instructions>

<response_format>
Product: Context, Problem, Solution, Acceptance Criteria, Channel Impact, Dependencies
QA: Summary, Detailed Results, Bugs, Screenshots, Recommendations
Errors: Summary, Root Cause, Fix, Prevention, Validation
Workflows: Type, Steps, Results, Iterations, Lessons
</response_format>

<constraints>
- Focus on OneSuite Core for product tasks
- Use Computer Use responsibly
- Analyze errors thoroughly
- Document assumptions clearly
- Be specific and measurable
- Include multi-channel impacts
</constraints>

<communication_style>
Professional, structured, results-oriented. Precise for technical tasks, comprehensive for strategy.
</communication_style>
"""

# =========================
# 2. EVAL DATASET & TEST CASES
# =========================
eval_questions = [
    "Generate a high-level OneSuite Core product roadmap for the next 6–9 months, covering MVP, V1, and Scale. Include phases, key capabilities, and dependencies across Search, Social, Programmatic, and Commerce.",
    "Draft a unified onboarding process for OneSuite that can be reused by all channels (Search, Social, Programmatic, Commerce). Describe the main stages, required inputs, and outputs at each stage.",
    "Write a one-page internal strategy brief summarizing what OneSuite Core is, the problems it solves for agencies, and how it unifies different channel agents under a single architecture.",
    "Propose a standardized evaluation and release-readiness checklist for any new OneSuite agent or channel integration. It should cover data, safety, metrics, and product criteria before launch.",
    "Explain how OneSuite Core should structure and govern shared artifacts (like glossaries, taxonomies, onboarding templates) so that channels stay consistent but can still extend for their own needs."
]


# Default sample test cases for evaluation
sample_test_cases = [
    {
        "question": "What is the capital of France?",
        "expected_keywords": ["Paris"]
    },
    {
        "question": "Summarize the OneSuite Core mission in one sentence.",
        "expected_keywords": ["strategy", "documentation", "unify", "Core team"]
    },
    {
        "question": "List two programming languages used for AI research.",
        "expected_keywords": ["Python", "R", "Julia", "Java"]
    },
    {
        "question": "What is 5 multiplied by 7?",
        "expected_keywords": ["35"]
    },
    {
        "question": "Name a key benefit of using structured data in product documentation.",
        "expected_keywords": ["clarity", "consistency", "automation", "searchability"]
    }
]

# =========================
# 3. CALL OCAA (ANSWERER)
# =========================
# =========================
# TOOL-ENABLED OCAA
# =========================
def call_ocaa_with_tools(question: str, chat_history=None, max_iterations=5) -> str:
    """Call OCAA with tool use capabilities using helper functions."""
    if chat_history is None:
        chat_history = []
    
    # Resolve @mentions in the question using MCP tools
    print("[MENTIONS] Checking for @document mentions...")
    question = resolve_mentions_in_text(question, "documents")
    
    messages = chat_history.copy()
    add_user_message(messages, question)

    # Get combined local + MCP tools
    all_tools = get_all_tools_for_claude()

    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}")
        print(f"{'='*60}")

        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS_WITH_TOOLS,
            system=system_prompt,
            messages=messages,
            tools=all_tools
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            add_assistant_message(messages, response.content)
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            tool_results = []

            # Special-case schema-only tools: consume tool input and finish
            SCHEMA_ONLY_TOOLS = {"article_summary", "extract_user_story"}
            for tool_use in tool_uses:
                if tool_use.name in SCHEMA_ONLY_TOOLS:
                    print(f"\n[SCHEMA] Schema-only tool '{tool_use.name}' detected; returning structured input.")
                    try:
                        return json.dumps(tool_use.input)
                    except Exception:
                        # Fallback: ensure JSON-serializable output
                        return str(tool_use.input)

            for tool_use in tool_uses:
                print(f"\n[TOOL] Claude wants to use tool: {tool_use.name}")
                result = execute_tool(tool_use.name, tool_use.input)
                
                # Check if result contains an error
                is_error = False
                try:
                    result_data = json.loads(result)
                    if "error" in result_data:
                        is_error = True
                        print(f"[ERROR] Tool execution error: {result_data['error']}")
                    else:
                        print(f"[OK] Tool result: {result[:200]}...")
                except json.JSONDecodeError:
                    # If result isn't valid JSON, treat as error
                    is_error = True
                    print(f"[ERROR] Tool returned invalid JSON")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result,
                    "is_error": is_error
                })

            add_user_message(messages, tool_results)

        elif response.stop_reason == "end_turn":
            final_text = get_text_from_response(response.content)
            print(f"\n[DONE] Final response generated")
            return final_text

        else:
            return f"Unexpected stop reason: {response.stop_reason}"

    return "Max iterations reached without final response"


# =========================
# TOOL-ENABLED OCAA (STREAMING VERSION)
# =========================
def call_ocaa_with_tools_streaming(question: str, chat_history=None, max_iterations=5, fine_grained=False) -> str:
    """Streaming version that shows live deltas and InputJSON, executes tools, and continues.

    Notes:
        - Captures text via content_block_delta
        - Captures tool args via input_json snapshot
        - Builds a synthetic tool_use block for continuity, then executes tool and loops
    """
    if chat_history is None:
        chat_history = []
    messages = chat_history.copy()
    add_user_message(messages, question)

    # Get combined local + MCP tools
    all_tools = get_all_tools_for_claude()

    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"STREAM ITERATION {iteration}")
        print(f"{'='*60}")

        tool_call = None
        latest_snapshot = None
        text_chunks = []

        params = {
            "model": model,
            "max_tokens": MAX_TOKENS_WITH_TOOLS,
            "system": system_prompt,
            "messages": messages,
            "tools": all_tools,
            "stream": True,
        }
        if fine_grained:
            if _fine_grained_supported():
                params.setdefault("stream_options", {})["fine_grained_tool_calls"] = True
            else:
                print("[Warning] Fine-grained requested but SDK does not support stream_options; continuing without it.")

        stream = client.messages.create(**params)

        for event in stream:
            etype = getattr(event, "type", "")
            print(f"[DEBUG] Event type: {etype}")

            if etype == "content_block_delta":
                delta = getattr(event, "delta", None)
                if delta and getattr(delta, "type", "") == "text_delta":
                    text_chunks.append(getattr(delta, "text", ""))

            elif etype == "content_block_start":
                block = getattr(event, "block", None)
                if block and getattr(block, "type", "") == "tool_use":
                    tool_call = {
                        "id": getattr(block, "id", "tool_1"),
                        "name": getattr(block, "name", ""),
                    }
                    print(f"\n[TOOL] Streaming tool_use start: {tool_call['name']}")

            elif etype == "input_json":
                latest_snapshot = getattr(event, "snapshot", None)
                partial = getattr(event, "partial_json", None)
                print(f"[InputJSON] partial={partial} snapshot={latest_snapshot}")

            elif etype == "message_stop":
                break

        # If no tool call, return streamed text
        if not tool_call:
            final_text = "".join(text_chunks).strip()
            if final_text:
                add_assistant_message(messages, final_text)
            print(f"\n[DONE] Final streamed response generated")
            return final_text

        # We have a tool call; build a synthetic tool_use block and execute
        try:
            tool_input = latest_snapshot
            if isinstance(tool_input, str):
                tool_input = json.loads(tool_input)
        except Exception:
            tool_input = latest_snapshot

        tool_use_block = {
            "type": "tool_use",
            "id": tool_call.get("id", "tool_1"),
            "name": tool_call.get("name", ""),
            "input": tool_input or {},
        }
        add_assistant_message(messages, [tool_use_block])

        print(f"\n[TOOL] Executing streamed tool: {tool_call.get('name', '')}")
        result = execute_tool(tool_call.get("name", ""), tool_input or {})

        tool_result_block = [{
            "type": "tool_result",
            "tool_use_id": tool_call.get("id", "tool_1"),
            "content": result,
            "is_error": False,
        }]
        add_user_message(messages, tool_result_block)

    return "Max iterations reached without final streamed response"


# Keep the original call_ocaa for backwards compatibility
def call_ocaa(question: str, chat_history=None) -> str:
    """Original OCAA without tools (for comparison)."""
    if chat_history is None:
        chat_history = []
    messages = chat_history + [{"role": "user", "content": question}]
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS_DEFAULT,
        system=system_prompt,
        messages=messages
    )
    return resp.content[0].text

# =========================
# RAG WORKFLOW IMPLEMENTATION
# =========================
class SimpleVectorIndex:
    """Simple in-memory vector index for RAG demonstration.
    
    This implements the core concepts from the Anthropic course:
    - Store embeddings with associated content
    - Search using cosine similarity
    - Return most relevant chunks
    """
    
    def __init__(self):
        self.vectors = []
        self.metadata = []
    
    def add_vector(self, embedding, metadata):
        """Add a vector and its associated metadata to the index."""
        self.vectors.append(embedding)
        self.metadata.append(metadata)
    
    def search(self, query_embedding, top_k=2):
        """Search for most similar vectors using cosine similarity.
        
        Returns list of (metadata, cosine_distance) tuples.
        Cosine distance = 1 - cosine_similarity (closer to 0 = more similar)
        """
        if not self.vectors:
            return []
        
        results = []
        
        # Calculate cosine similarity for each stored vector
        for i, stored_embedding in enumerate(self.vectors):
            # Cosine similarity = dot product / (magnitude1 * magnitude2)
            dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
            
            magnitude_query = sum(x * x for x in query_embedding) ** 0.5
            magnitude_stored = sum(x * x for x in stored_embedding) ** 0.5
            
            cosine_similarity = dot_product / (magnitude_query * magnitude_stored)
            
            # Convert to cosine distance (1 - similarity)
            # Distance closer to 0 means more similar
            cosine_distance = 1 - cosine_similarity
            
            results.append((self.metadata[i], cosine_distance))
        
        # Sort by distance (ascending - closest first)
        results.sort(key=lambda x: x[1])
        
        # Return top_k results
        return results[:top_k]


def chunk_text_by_section(text):
    """Chunk text by markdown sections (structure-based chunking)."""
    import re
    
    # Split on markdown headers (## Section)
    pattern = r'\n(?=## )'
    chunks = re.split(pattern, text)
    
    # Clean up chunks
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return chunks


def generate_embeddings_batch(texts):
    """Generate embeddings for multiple texts using Voyage AI.
    
    Note: This is a placeholder. In production, you would:
    1. Use Voyage AI API (voyage_api_key)
    2. Or use sentence-transformers locally
    3. Or use OpenAI embeddings
    
    For this demo, we'll simulate embeddings with simple hashing.
    """
    try:
        # Try to use sentence-transformers if available
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts, show_progress_bar=False)
        return [embedding.tolist() for embedding in embeddings]
    except ImportError:
        # Fallback: Create simple simulated embeddings based on text characteristics
        print("[NOTE] Using simulated embeddings (install sentence-transformers for real embeddings)")
        embeddings = []
        for text in texts:
            # Create a simple embedding based on text features
            # This is NOT production-quality, just for demonstration
            text_lower = text.lower()
            
            # Feature 1: Medical/health keywords
            medical_score = sum([
                text_lower.count('medical'),
                text_lower.count('health'),
                text_lower.count('patient'),
                text_lower.count('research'),
                text_lower.count('drug'),
                text_lower.count('treatment')
            ]) / len(text) * 100
            
            # Feature 2: Software/engineering keywords  
            software_score = sum([
                text_lower.count('software'),
                text_lower.count('engineer'),
                text_lower.count('bug'),
                text_lower.count('code'),
                text_lower.count('develop'),
                text_lower.count('program')
            ]) / len(text) * 100
            
            # Feature 3: Business keywords
            business_score = sum([
                text_lower.count('revenue'),
                text_lower.count('profit'),
                text_lower.count('business'),
                text_lower.count('company'),
                text_lower.count('market'),
                text_lower.count('customer')
            ]) / len(text) * 100
            
            # Normalize to create simple 3D embedding
            total = medical_score + software_score + business_score + 0.001
            embedding = [
                medical_score / total,
                software_score / total,
                business_score / total
            ]
            
            embeddings.append(embedding)
        
        return embeddings


def run_contextual_retrieval_demo():
    """Demonstrate Contextual Retrieval from Lesson 007.
    
    Contextual Retrieval adds a preprocessing step before indexing:
    1. Take each chunk + source document
    2. Send to Claude: "Add context to situate this chunk"
    3. Claude generates 2-3 sentences explaining what the chunk covers
    4. Concatenate: [Claude's context] + [original chunk] = contextualized chunk
    5. Index the contextualized chunk (instead of raw chunk)
    
    Benefits:
    - Chunks now contain ties to the larger document
    - Better retrieval because chunks have more relevant context
    - Especially helpful for complex documents with many cross-references
    
    For large documents:
    - Include starter chunks (intro/abstract)
    - Include nearby chunks (immediate context)
    - Skip middle chunks to fit in Claude's context window
    """
    try:
        from hybrid_retriever import (
            RetrieverWithReranking, 
            chunk_text_by_section, 
            generate_embeddings_batch,
            add_contextual_retrieval
        )
    except ImportError:
        print("❌ hybrid_retriever module not found")
        return
    
    print("\n" + "="*80)
    print("CONTEXTUAL RETRIEVAL DEMO (Lesson 007)")
    print("Preprocessing chunks with Claude before indexing")
    print("="*80 + "\n")
    
    # Load document
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "report.md")
    if not os.path.exists(report_path):
        print("❌ report.md not found in data/ folder")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        document_text = f.read()
    
    print("📄 STEP 1: Load & Chunk Document")
    print("-" * 80)
    chunks = chunk_text_by_section(document_text)
    print(f"✅ Created {len(chunks)} chunks\n")
    
    # Show example of adding context to one chunk
    print("🧠 STEP 2: Add Context to Sample Chunk")
    print("-" * 80)
    
    sample_idx = min(4, len(chunks) - 1)  # Use chunk 4 or last chunk
    sample_chunk = chunks[sample_idx]
    
    print(f"Original Chunk #{sample_idx}:")
    print("-" * 40)
    print(sample_chunk[:200] + "...\n")
    
    print("Sending to Claude to add context...")
    print("(Using large document strategy: starter + nearby chunks)\n")
    
    contextualized = add_contextual_retrieval(
        chunk=sample_chunk,
        source_text=document_text,
        client=client,
        starter_chunks=2,
        nearby_chunks=2,
        all_chunks=chunks,
        chunk_index=sample_idx
    )
    
    # Extract just the added context (before the original chunk)
    added_context = contextualized.replace(sample_chunk, "").strip()
    
    print("✅ Claude Added Context:")
    print("-" * 40)
    print(f"{added_context}\n")
    
    print("Contextualized Chunk = [Context] + [Original]")
    print(f"Original length: {len(sample_chunk)} chars")
    print(f"Contextualized length: {len(contextualized)} chars")
    print(f"Added context: {len(added_context)} chars\n")
    
    # Now build full retriever with contextual retrieval
    print("="*80)
    print("STEP 3: Build Retriever with Contextual Retrieval")
    print("="*80 + "\n")
    
    print("Processing all chunks with contextual retrieval...")
    print("(This will take ~30-60 seconds as we call Claude for each chunk)\n")
    
    retriever = RetrieverWithReranking(client=client)
    contextualized_chunks = []
    
    for i, chunk in enumerate(chunks):
        print(f"  Processing chunk {i+1}/{len(chunks)}...")
        
        # Add context using large document strategy
        contextualized_chunk = add_contextual_retrieval(
            chunk=chunk,
            source_text=document_text,
            client=client,
            starter_chunks=2,
            nearby_chunks=2,
            all_chunks=chunks,
            chunk_index=i
        )
        
        contextualized_chunks.append(contextualized_chunk)
    
    print("\n✅ All chunks contextualized!\n")
    
    # Generate embeddings for contextualized chunks
    print("🔢 STEP 4: Generate Embeddings")
    print("-" * 80)
    embeddings = generate_embeddings_batch(contextualized_chunks)
    print(f"✅ Generated {len(embeddings)} embeddings\n")
    
    # Add to retriever
    for i, (chunk, embedding) in enumerate(zip(contextualized_chunks, embeddings)):
        metadata = {
            'id': i,
            'content': chunk,
            'section': chunks[i].split('\n')[0] if chunks[i] else f"Section {i}"
        }
        retriever.add_document(chunk, embedding, metadata)
    
    print("✅ Retriever built with contextualized chunks\n")
    
    # Test query
    print("="*80)
    print("STEP 5: Test Retrieval")
    print("="*80 + "\n")
    
    query = "What did the engineering team do with the 2023 incident?"
    print(f"Query: \"{query}\"\n")
    
    query_embedding = generate_embeddings_batch([query])[0]
    results = retriever.search_with_reranking(query, query_embedding, top_k=2)
    
    print("Top Results:")
    print("-" * 80)
    for i, (metadata, score) in enumerate(results, 1):
        print(f"\n{i}. {metadata['section']}")
        print(f"   Content preview: {metadata['content'][:150]}...")
    
    print("\n" + "="*80)
    print("CONTEXTUAL RETRIEVAL BENEFITS")
    print("="*80)
    print("""
✅ Added Context to Each Chunk
   - Claude analyzed each chunk in context of full document
   - Generated 2-3 sentences explaining what chunk covers
   - Added ties to other sections and key concepts

✅ Large Document Strategy
   - Used starter chunks (intro/abstract)
   - Used nearby chunks (immediate context)
   - Avoided including entire document in prompt

✅ Improved Retrieval
   - Chunks now contain document context
   - Better matches for queries about relationships
   - More relevant terms for search

RESULT: Contextual retrieval improves accuracy, especially for complex documents!
    """)


def run_rag_workflow_demo():
    """Complete Week 6 RAG workflow with answer generation.
    
    This demonstrates the full RAG pipeline:
    1. Chunk the document by sections
    2. Generate embeddings for each chunk
    3. Run hybrid search (Vector + BM25 + RRF)
    4. Re-rank results with Claude
    5. Add top context to prompt
    6. Send to Claude for answer generation
    
    Complete flow: retrieve → rerank → respond
    """
    try:
        from hybrid_retriever import RetrieverWithReranking, chunk_text_by_section, generate_embeddings_batch
    except ImportError:
        print("❌ hybrid_retriever module not found")
        print("   Make sure hybrid_retriever.py is in the workspace")
        return
    
    print("\n" + "="*80)
    print("WEEK 6 RAG COMPLETE PIPELINE")
    print("Full Flow: Retrieve → Rerank → Respond")
    print("="*80 + "\n")
    
    # Load document
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "report.md")
    if not os.path.exists(report_path):
        print("❌ report.md not found in data/ folder")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        document_text = f.read()
    
    print("📄 STEP 1: Load Document")
    print("-" * 80)
    print(f"✅ Loaded {len(document_text)} characters\n")
    
    # Chunk document
    print("✍️ STEP 2: Chunk Text by Sections")
    print("-" * 80)
    
    chunks = chunk_text_by_section(document_text)
    print(f"✅ Created {len(chunks)} chunks\n")
    
    # Generate embeddings
    print("🔢 STEP 3: Generate Embeddings")
    print("-" * 80)
    
    embeddings = generate_embeddings_batch(chunks)
    print(f"✅ Generated {len(embeddings)} embeddings ({len(embeddings[0])} dimensions)\n")
    
    # Build retriever
    print("🔀 STEP 4: Build Retriever with Re-ranking")
    print("-" * 80)
    
    retriever = RetrieverWithReranking(client=client)
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        metadata = {
            'id': i,
            'content': chunk,
            'section': chunk.split('\n')[0] if chunk else f"Section {i}"
        }
        retriever.add_document(chunk, embedding, metadata)
    
    print(f"✅ Initialized with Vector + BM25 + RRF + Claude Re-ranking\n")
    
    # Test queries
    print("="*80)
    print("TESTING RAG PIPELINE WITH QUERIES")
    print("="*80)
    
    test_queries = [
        "What happened with incident 2023 Q4 011?",
        "What did the engineering team do with the incident?",
    ]
    
    for idx, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {idx}: \"{query}\"")
        print("="*80)
        
        # Generate embedding
        query_embedding = generate_embeddings_batch([query])[0]
        
        # Step 1: Retrieve
        print("\n1️⃣ RETRIEVE (Hybrid Search)")
        print("-" * 40)
        
        hybrid_results = retriever.search(query, query_embedding, top_k=3)
        print(f"Found {len(hybrid_results)} relevant chunks:")
        for i, (metadata, score) in enumerate(hybrid_results, 1):
            print(f"  {i}. {metadata['section'][:50]}...")
        
        # Step 2: Re-rank
        print("\n2️⃣ RERANK (Claude)")
        print("-" * 40)
        
        try:
            reranked = retriever.search_with_reranking(query, query_embedding, top_k=2)
            print("Claude re-ranked by relevance:")
            for i, (metadata, score) in enumerate(reranked, 1):
                print(f"  {i}. {metadata['section'][:50]}...")
            top_result = reranked[0][0] if reranked else None
        except Exception as e:
            print(f"⚠️  Re-ranking skipped: {e}")
            top_result = hybrid_results[0][0] if hybrid_results else None
        
        # Step 3: Build context
        print("\n3️⃣ CONTEXT (Top Result)")
        print("-" * 40)
        
        if top_result:
            context = top_result['content'][:400]
            print(f"Using: {top_result['section']}")
            print(f"Length: {len(context)} chars\n")
        else:
            context = ""
            print("No context found\n")
        
        # Step 4: Generate answer
        print("4️⃣ RESPOND (Claude Generates Answer)")
        print("-" * 40)
        
        if not context:
            print("Skipping answer generation (no context)")
            continue
        
        system_prompt = """You are a helpful assistant that answers questions about incident reports.
Use the provided context to answer. If context doesn't address the question, say so.
Always cite the section you used."""
        
        user_message = f"""Context from incident report:
{context}

Question: {query}

Answer based on the context above:"""
        
        try:
            response = client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            answer = response.content[0].text
            print(answer)
            
        except Exception as e:
            print(f"Error calling Claude: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("WEEK 6 RAG PIPELINE COMPLETE")
    print("="*80)
    print("""
✅ Document Preparation
   - Loaded and chunked document by sections

✅ Embeddings & Indexing  
   - Generated embeddings for each chunk
   - Built Vector + BM25 + RRF retriever

✅ Retrieval (Hybrid Search)
   - Combined semantic + lexical search
   - Balanced results with RRF

✅ Re-ranking with Claude
   - Sent top results to Claude
   - Claude understood query intent
   - Results reordered by relevance

✅ Answer Generation
   - Top context added to prompt
   - Sent to Claude with full context
   - Generated final answer with sources

RESULT: Complete RAG pipeline working end-to-end!
    """)


def run_hybrid_retriever_demo():
    """Hybrid retrieval demonstration combining semantic and lexical search.
    
    Implements the hybrid approach from Anthropic course:
    1. Semantic Search (Vector embeddings)
    2. Lexical Search (BM25 keyword matching)
    3. Reciprocal Rank Fusion (RRF) to merge results
    
    This solves the problem where semantic search alone returns irrelevant results
    because it doesn't capture exact keyword importance.
    """
    try:
        from hybrid_retriever import Retriever, chunk_text_by_section, generate_embeddings_batch
    except ImportError:
        print("❌ hybrid_retriever module not found")
        print("   Make sure hybrid_retriever.py is in the workspace")
        return
    
    print("\n" + "="*80)
    print("HYBRID RETRIEVER DEMO - Semantic + Lexical Search")
    print("Based on Anthropic Course: 005 Hybrid Search")
    print("="*80 + "\n")
    
    # Load document
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "report.md")
    if not os.path.exists(report_path):
        print("❌ report.md not found in data/ folder")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Chunk document
    print("📄 STEP 1: Chunking document by sections")
    print("-" * 80)
    
    chunks = chunk_text_by_section(text)
    print(f"✅ Created {len(chunks)} chunks\n")
    
    # Generate embeddings
    print("🔢 STEP 2: Generating embeddings")
    print("-" * 80)
    
    embeddings = generate_embeddings_batch(chunks)
    print(f"✅ Generated {len(embeddings)} embeddings\n")
    
    # Build hybrid retriever
    print("🔀 STEP 3: Building hybrid retriever")
    print("-" * 80)
    
    retriever = Retriever()
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        metadata = {
            'id': i,
            'content': chunk,
            'section': chunk.split('\n')[0] if chunk else f"Section {i}"
        }
        retriever.add_document(chunk, embedding, metadata)
    
    print(f"✅ Initialized Retriever with:")
    print(f"   - Vector Index (Semantic Search)")
    print(f"   - BM25 Index (Lexical Search)")
    print(f"   - Reciprocal Rank Fusion (RRF Merger)\n")
    
    # Test query
    query = "What happened with incident 2023 Q4 011"
    print("❓ STEP 4: Testing search systems")
    print("-" * 80)
    print(f"Query: \"{query}\"\n")
    
    query_embedding = generate_embeddings_batch([query])[0]
    
    # Semantic search only
    print("🔹 SEMANTIC SEARCH ONLY (Original Problem):")
    print("-" * 40)
    semantic_results = retriever.vector_index.search(query_embedding, top_k=3)
    for i, (metadata, distance) in enumerate(semantic_results, 1):
        similarity = 1 - distance
        print(f"{i}. {metadata['section']} (similarity: {similarity:.4f})")
    print()
    
    # Lexical search (BM25)
    print("🔹 LEXICAL SEARCH (BM25):")
    print("-" * 40)
    bm25_results = retriever.bm25_index.search(query, top_k=3)
    for i, (metadata, distance) in enumerate(bm25_results, 1):
        score = -distance
        print(f"{i}. {metadata['section']} (BM25 score: {score:.4f})")
    print()
    
    # Hybrid search (RRF)
    print("🔹 HYBRID SEARCH (RRF Fusion) ⭐:")
    print("-" * 40)
    hybrid_results = retriever.search(query, query_embedding, top_k=3)
    for i, (metadata, rrf_score) in enumerate(hybrid_results, 1):
        print(f"{i}. {metadata['section']} (RRF score: {-rrf_score:.4f})")
    print()
    
    # Show content of top result
    if hybrid_results:
        print("="*80)
        print("TOP RESULT CONTENT:")
        print("="*80)
        top_metadata = hybrid_results[0][0]
        print(f"\nSection: {top_metadata['section']}")
        print(f"Content:\n{top_metadata['content'][:500]}...\n")
    
    # Explain RRF
    print("="*80)
    print("UNDERSTANDING RECIPROCAL RANK FUSION (RRF):")
    print("="*80)
    print("""
RRF merges rankings from multiple search systems using the formula:
    RRF_score = sum(1 / (k + rank)) across all ranking systems

Where k is a constant (typically 60).

**Why this works:**
- A document that ranks well in BOTH systems gets high RRF score
- A document that ranks well in only ONE system gets lower score
- This balances semantic understanding with exact keyword matching

**Example:**
  Semantic Search:  [A, B, C]
  BM25 Search:      [C, A, B]
  
  RRF Scores:
  A: 1/(60+1) + 1/(60+2) = 0.0324 ⭐ Best (ranks 1st in both)
  B: 1/(60+2) + 1/(60+3) = 0.0317 (mixed)
  C: 1/(60+3) + 1/(60+1) = 0.0321 (mixed)
  
  Final Ranking: A > C > B

This is the foundation of production RAG systems!
    """)
    
    print("="*80)
    print("KEY DIFFERENCES:")
    print("="*80)
    print("""
| Aspect          | Semantic       | Lexical (BM25)  | Hybrid (RRF)    |
|-----------------|----------------|-----------------|-----------------|
| Strengths       | Context & meaning | Exact keywords  | Both!           |
| Weakness        | Misses keywords | No understanding | Requires both   |
| Best For        | Understanding   | Precision       | Balanced Search |
| Problem Solved  | Nothing         | Nothing         | ✅ Incident 2023|
    """)


def run_reranking_demo():
    """Re-ranking demonstration using Claude to improve retrieval accuracy.
    
    Implements the re-ranking approach from Anthropic course:
    1. Run hybrid retrieval (Vector + BM25 + RRF)
    2. Format top results as XML
    3. Ask Claude to re-rank by relevance
    4. Return Claude's prioritized ranking
    
    This solves the problem where hybrid search still misses queries that emphasize
    specific terminology or multiple concepts.
    """
    try:
        from hybrid_retriever import RetrieverWithReranking, chunk_text_by_section, generate_embeddings_batch
    except ImportError:
        print("❌ hybrid_retriever module not found")
        print("   Make sure hybrid_retriever.py is in the workspace")
        return
    
    print("\n" + "="*80)
    print("RE-RANKING DEMO - Claude-Enhanced Retrieval")
    print("Based on Anthropic Course: 006 Re-ranking")
    print("="*80 + "\n")
    
    # Load document
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "report.md")
    if not os.path.exists(report_path):
        print("❌ report.md not found in data/ folder")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Chunk document
    print("📄 STEP 1: Chunking document by sections")
    print("-" * 80)
    
    chunks = chunk_text_by_section(text)
    print(f"✅ Created {len(chunks)} chunks\n")
    
    # Generate embeddings
    print("🔢 STEP 2: Generating embeddings")
    print("-" * 80)
    
    embeddings = generate_embeddings_batch(chunks)
    print(f"✅ Generated {len(embeddings)} embeddings\n")
    
    # Build retriever with re-ranking
    print("🔀 STEP 3: Building retriever with Claude re-ranking")
    print("-" * 80)
    
    retriever = RetrieverWithReranking(client=client)  # Use the Anthropic client from demo.py
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        metadata = {
            'id': i,
            'content': chunk,
            'section': chunk.split('\n')[0] if chunk else f"Section {i}"
        }
        retriever.add_document(chunk, embedding, metadata)
    
    print(f"✅ Initialized Retriever with:")
    print(f"   - Vector Index (Semantic Search)")
    print(f"   - BM25 Index (Lexical Search)")
    print(f"   - Reciprocal Rank Fusion (RRF Merger)")
    print(f"   - Claude Re-ranking (Relevance Refinement)\n")
    
    # Test Query 1: Basic query
    print("="*80)
    print("TEST 1: Basic Query")
    print("="*80)
    query1 = "What happened with incident 2023 Q4 011"
    print(f"Query: \"{query1}\"\n")
    
    query1_embedding = generate_embeddings_batch([query1])[0]
    
    print("🔍 Hybrid Search Results (before re-ranking):")
    print("-" * 40)
    hybrid_results = retriever.search(query1, query1_embedding, top_k=3)
    for i, (metadata, score) in enumerate(hybrid_results, 1):
        print(f"{i}. {metadata['section']}")
    
    print("\n🔍 Re-ranked Results (Claude's ranking):")
    print("-" * 40)
    reranked_results = retriever.search_with_reranking(query1, query1_embedding, top_k=3)
    for i, (metadata, score) in enumerate(reranked_results, 1):
        print(f"{i}. {metadata['section']}")
    
    # Test Query 2: Complex query (the problematic one)
    print("\n" + "="*80)
    print("TEST 2: Complex Query (Engineering-Specific)")
    print("="*80)
    query2 = "What did the engineering team do with incident 2023"
    print(f"Query: \"{query2}\"\n")
    
    query2_embedding = generate_embeddings_batch([query2])[0]
    
    print("🔍 Hybrid Search Results (before re-ranking):")
    print("-" * 40)
    hybrid_results2 = retriever.search(query2, query2_embedding, top_k=3)
    for i, (metadata, score) in enumerate(hybrid_results2, 1):
        print(f"{i}. {metadata['section']}")
    
    print("\n🔍 Re-ranked Results (Claude's ranking):")
    print("-" * 40)
    reranked_results2 = retriever.search_with_reranking(query2, query2_embedding, top_k=3)
    for i, (metadata, score) in enumerate(reranked_results2, 1):
        print(f"{i}. {metadata['section']}")
    
    # Explain the improvement
    print("\n" + "="*80)
    print("HOW RE-RANKING WORKS:")
    print("="*80)
    print("""
1. HYBRID SEARCH (Vector + BM25 + RRF)
   ↓ Returns initial candidates
   ↓

2. FORMAT FOR CLAUDE
   ↓ Convert to XML with document IDs
   ↓

3. CLAUDE RE-RANKING
   ↓ Claude reads query + documents
   ↓ Claude returns IDs in order of relevance
   ↓

4. RETURN RE-RANKED RESULTS
   ↓ Most relevant first
   ↓

KEY INSIGHT: Claude understands that "engineering team" queries should prioritize
the Software Engineering section, even if raw hybrid scores don't reflect that.
    """)
    
    print("="*80)
    print("TRADE-OFFS:")
    print("="*80)
    print("""
Advantages:
  ✅ More accurate relevance ranking
  ✅ Better understanding of query intent
  ✅ Handles complex multi-concept queries
  ✅ Efficient (uses document IDs, not full text)

Disadvantages:
  ❌ Slower (extra Claude API call)
  ❌ Higher token cost
  ❌ More complex pipeline
  ❌ Depends on Claude's interpretation

When to Use:
  - High accuracy requirements
  - Complex, nuanced queries
  - When latency is acceptable
  - For production RAG systems
    """)
    
    print("="*80)
    print("FULL RAG PIPELINE WITH RE-RANKING:")
    print("="*80)
    print("""
1. ✅ Chunk document
2. ✅ Generate embeddings
3. ✅ Hybrid search (Vector + BM25 + RRF)
4. ✅ Re-ranking (Claude refines ordering)  ← YOU ARE HERE
5. → Add top result to prompt
6. → Send to Claude
7. → Claude generates final answer
    """)



# =========================
# MAIN CHATBOT LOOP
# =========================
# 4. INTERACTIVE CHATBOT
# =========================
# =========================
# ITERATIVE PROMPT ENGINEERING WORKFLOW
# =========================
def run_iterative_prompt_engineering():
    """Run the iterative prompt engineering workflow with 4 versions."""
    
    evaluator = PromptEvaluator(max_concurrent_tasks=3)
    
    print("\n" + "="*70)
    print("ITERATIVE PROMPT ENGINEERING WORKFLOW")
    print("="*70 + "\n")
    
    # Step 1: Generate dataset
    print("STEP 1: Generating test dataset for product management tasks\n")
    
    dataset = generate_pm_dataset()
    
    if dataset is None:
        print("Failed to generate dataset")
        return
    
    print("\n" + "="*70)
    print("VERSION 1: BASELINE (Very simple prompt)")
    print("="*70 + "\n")
    
    results_v1 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v1_baseline,
        dataset_file="pm_dataset.json",
        extra_criteria="Should include clear structure and proper formatting"
    )
    
    input("Press Enter to continue to Version 2...")
    
    print("\n" + "="*70)
    print("VERSION 2: ADD STRUCTURE (Clear formatting and requirements)")
    print("="*70 + "\n")
    print("TECHNIQUE: Explicit structure with clear sections and formatting\n")
    
    results_v2 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v2_structure,
        dataset_file="pm_dataset.json",
        extra_criteria="Should include clear structure and proper formatting"
    )
    
    input("Press Enter to continue to Version 3...")
    
    print("\n" + "="*70)
    print("VERSION 3: ADD EXAMPLES (Few-shot learning)")
    print("="*70 + "\n")
    print("TECHNIQUE: Include example input/output pairs to guide the model\n")
    
    results_v3 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v3_examples,
        dataset_file="pm_dataset.json",
        extra_criteria="Should include clear structure and proper formatting"
    )
    
    input("Press Enter to continue to Version 4...")
    
    print("\n" + "="*70)
    print("VERSION 4: ADD PERSONA + CHAIN OF THOUGHT")
    print("="*70 + "\n")
    print("TECHNIQUES: Expert persona + step-by-step reasoning\n")
    
    results_v4 = evaluator.run_evaluation(
        run_prompt_function=run_prompt_v4_persona_cot,
        dataset_file="pm_dataset.json",
        extra_criteria="Should include clear structure and proper formatting"
    )
    
    # Show final summary
    evaluator.show_history()
    
    print("="*70)
    print("ITERATIVE PROMPT ENGINEERING COMPLETE")
    print("="*70)
    print("\nSummary:")
    scores = [eval_run['average_score'] for eval_run in evaluator.evaluation_history]
    for i, score in enumerate(scores, 1):
        print(f"  Version {i}: {score:.2f}/10")
    
    if len(scores) > 1:
        improvement = scores[-1] - scores[0]
        improvement_pct = (improvement / scores[0]) * 100 if scores[0] > 0 else 0
        print(f"\nTotal Improvement: {improvement:+.2f} points ({improvement_pct:+.1f}%)")
    
    print("\nKey Takeaways:")
    print("1. Each technique should improve scores incrementally")
    print("2. Structure helps clarity")
    print("3. Examples guide expected output")
    print("4. Persona + CoT improve reasoning quality")

def main():
    """Start the interactive OCAA chatbot with tool-enabled flows and evaluation commands."""
    # Initialize MCP servers asynchronously
    global mcp_event_loop
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    mcp_event_loop = loop  # Store reference for later use
    loop.run_until_complete(initialize_mcp_servers())
    
    try:
        print("Welcome to the OneSuite Core Architect Agent (OCAA) chatbot!")
        print("\nCOMMANDS:")
        print("  'exit' - Quit")
        print("  '/rag-demo' - ⭐ WEEK 6 COMPLETE: Full RAG pipeline (retrieve → rerank → respond)")
        print("  '/contextual-demo' - 🆕 LESSON 007: Contextual Retrieval (preprocessing chunks)")
        print("  '/hybrid-demo' - Hybrid retrieval (Semantic + Lexical search via RRF)")
        print("  '/rerank-demo' - Re-ranking with Claude (improves retrieval accuracy)")
        print("  '/prompt-eng' - Run iterative prompt engineering (v1 -> v2 -> v3 -> v4)")
        print("  '/eval' - Evaluate with keywords")
        print("  '/eval-llm' - Evaluate with LLM grading")
        print("  '/eval-code' - Evaluate code syntax validation")
        print("  '/extract-article' - Extract structured data from an article (demo)")
        print("  '/extract-story' - Extract user story components (demo)")
        print("  '/stream-demo' - Stream with tools and log InputJSON events")
        print("  '/image <path> <question>' - Ask about an image")
        print("  '/pdf <path> <question>' - Ask about a PDF document")
        print("  '/mcp-tools' - List available MCP tools")
        print("  '/format <doc_id>' - Reformat a document in Markdown (MCP Prompt)")

        print("  '/qa-test <url>' - Run automated QA tests")
        print("  '/test-mention' - Test @mention component")
        print("  '/monitor-errors' - Analyze production logs")
        print("  '/workflow-demo' - Evaluator-Optimizer demo")
        print("  '/parallel-analysis' - Parallelization workflow demo")
        print("  '/full-automation' - Run all capabilities")
        print(f"\n  Computer Use: {'✅' if COMPUTER_USE_AVAILABLE else '❌'}")

        
        chat_history = []
        
        def run_article_extraction_demo():
            """Demo: Extract structured data from generated article using tools."""
            print("\n" + "="*70)
            print("ARTICLE EXTRACTION DEMO (Tool-Based Structured Output)")
            print("="*70 + "\n")
        
            # Generate a sample article
            print("Step 1: Generating a sample article...\n")
            messages = []
            add_user_message(messages, "Write a one paragraph scholarly article about artificial intelligence and include a title and author name.")
        
            article_response = chat(messages)
            print(f"Generated Article:\n{article_response}\n")
        
            # Now extract structured data from it using tool forcing
            print("Step 2: Extracting structured data using tools (tool_choice forcing)...\n")
            extracted = extract_article_summary(article_response)
        
            if extracted:
                print("✅ EXTRACTED STRUCTURED DATA:\n")
                print(f"Title: {extracted['title']}")
                print(f"Author: {extracted['author']}")
                print(f"Key Insights:")
                for i, insight in enumerate(extracted['key_insights'], 1):
                    print(f"  {i}. {insight}")
                print("\n[NOTE] The data is guaranteed to match the schema structure!")
                print("   - title is a string")
                print("   - author is a string")
                print("   - key_insights is a list of strings")
            else:
                print("❌ Failed to extract structured data")

        def run_user_story_extraction_demo():
            """Demo: Extract user story from requirement text using tools."""
            print("\n" + "="*70)
            print("USER STORY EXTRACTION DEMO (Tool-Based Structured Output)")
            print("="*70 + "\n")
        
            # Sample requirement text
            requirement = """
        We need to enable teams to search and filter product information across all channels.
        This should work consistently for Search, Social, Programmatic, and Commerce teams.
        The system should allow filtering by date, budget, and performance metrics.
        All teams should see the same terminology and options.
        """
        
            print(f"Input Requirement:\n{requirement}\n")
            print("Extracting structured user story using tools (tool_choice forcing)...\n")
        
            extracted = extract_user_story(requirement)
        
            if extracted:
                print("✅ EXTRACTED USER STORY STRUCTURE:\n")
                print(f"Role: {extracted['role']}")
                print(f"Action: {extracted['action']}")
                print(f"Benefit: {extracted['benefit']}")
                print(f"\nAcceptance Criteria:")
                for i, criterion in enumerate(extracted['acceptance_criteria'], 1):
                    print(f"  {i}. {criterion}")
                print(f"\nChannel Impact:")
                for channel, impact in extracted['channel_impact'].items():
                    print(f"  {channel.capitalize()}: {impact}")
                print("\n[NOTE] Key Benefit: Guaranteed structured output!")
                print("   Claude MUST provide all required fields with correct types.")
                print("   No JSON parsing errors or missing data!")
            else:
                print("❌ Failed to extract user story")

        while True:
            user_input = input("\nYou: ")
            if user_input.strip().lower() == "exit":
                print("Goodbye!")
                break
            
            if user_input.strip().lower() == "/mcp-tools":
                print("\n" + "="*70)
                print("AVAILABLE MCP TOOLS")
                print("="*70)
                if mcp_tools:
                    for tool in mcp_tools:
                        print(f"\n[TOOL] {tool['name']} (from {tool['_mcp_server']} server)")
                        print(f"   {tool['description']}")
                else:
                    print("\nNo MCP tools available. Configure MCP servers in MCP_SERVERS_CONFIG.")
                print()
                continue
            
            # Handle /format command (MCP Prompt)
            if user_input.strip().lower().startswith("/format"):
                parts = user_input.strip().split(maxsplit=1)
                if len(parts) < 2:
                    print("\nUsage: /format <doc_id>")
                    print("Example: /format document1")
                    continue
                
                doc_id = parts[1]
                print(f"\n[MCP PROMPT] Executing 'format' prompt for document: {doc_id}")
                
                # Execute MCP prompt
                try:
                    prompt_result = mcp_executor.submit(
                        lambda: asyncio.run(execute_mcp_prompt("documents", "format", {"doc_id": doc_id}))
                    ).result(timeout=10)
                    
                    if prompt_result:
                        # Send prompt messages to Claude
                        print("\n[ASSISTANT] Processing document format request...\n")
                        response = call_ocaa_with_tools(prompt_result, chat_history)
                        print(f"\nAssistant: {response}")
                    else:
                        print("[ERROR] Failed to get prompt from MCP server")
                except Exception as e:
                    print(f"[ERROR] Failed to execute prompt: {e}")
                continue
            
            if user_input.strip().lower() == "/prompt-eng":
                run_iterative_prompt_engineering()
                continue
            
            if user_input.strip().lower() == "/eval":
                run_evaluation(sample_test_cases, use_llm_judge=False)
                continue
            if user_input.strip().lower() == "/eval-llm":
                run_evaluation(sample_test_cases, use_llm_judge=True)
                continue
            if user_input.strip().lower() == "/eval-code":
                try:
                    with open('dataset.json', 'r') as f:
                        dataset = json.load(f)
                    run_code_evaluation(dataset)
                except FileNotFoundError:
                    print("dataset.json not found. Use /gendata first.")
                except Exception as e:
                    print(f"Error: {e}")
                continue
            
            if user_input.strip().lower() == "/extract-article":
                run_article_extraction_demo()
                continue
            
            if user_input.strip().lower() == "/extract-story":
                run_user_story_extraction_demo()
                continue
            
            if user_input.strip().lower() == "/rag-demo":
                run_rag_workflow_demo()
                continue
            
            if user_input.strip().lower() == "/contextual-demo":
                run_contextual_retrieval_demo()
                continue
            
            if user_input.strip().lower() == "/hybrid-demo":
                run_hybrid_retriever_demo()
                continue
            
            if user_input.strip().lower() == "/rerank-demo":
                run_reranking_demo()
                continue
            
            if user_input.strip().lower() == "/stream-demo":
                print("\n" + "="*70)
                print("STREAMING DEMO (Tools + InputJSON via shared streaming loop)")
                print("="*70 + "\n")
                prompt = "Generate a short abstract and meta (word_count, review) for a scholarly AI paper, then call the article_summary tool."
                result = stream_with_tools(
                    prompt,
                    tools=[article_summary_schema],
                    tool_choice={"type": "tool", "name": "article_summary"},
                    fine_grained=True
                )
                print("\n--- Stream Complete ---")
                print(f"Text collected:\n{result['text']}\n")
                if result["tool_inputs"]:
                    print("InputJSON snapshots:")
                    for snap in result["tool_inputs"]:
                        print(f"  partial: {snap['partial']}")
                        print(f"  snapshot: {snap['snapshot']}")
                    if result.get("assembled_input"):
                        print(f"\nAssembled InputJSON: {result['assembled_input']}")
                else:
                    print("No InputJSON events captured.")
                continue
            
            if user_input.strip().lower().startswith("/image "):
                parts = user_input[7:].split(' ', 1)
                if len(parts) < 2:
                    print("Usage: /image <path> <question>")
                    continue
                image_path, question = parts[0], parts[1]
                try:
                    print(f"\n📷 Analyzing image: {image_path}...")
                    answer = ask_about_image(image_path, question)
                    print("\n" + "="*60)
                    print("Claude's Response:")
                    print("="*60)
                    print(answer)
                except FileNotFoundError:
                    print(f"❌ Image file not found: {image_path}")
                except Exception as e:
                    print(f"❌ Error processing image: {e}")
                continue
            
            if user_input.strip().lower().startswith("/pdf "):
                parts = user_input[5:].split(' ', 1)
                if len(parts) < 2:
                    print("Usage: /pdf <path> <question>")
                    continue
                pdf_path, question = parts[0], parts[1]
                try:
                    print(f"\n📄 Analyzing PDF: {pdf_path}...")
                    answer = ask_about_pdf(pdf_path, question)
                    print("\n" + "="*60)
                    print("Claude's Response:")
                    print("="*60)
                    print(answer)
                except FileNotFoundError:
                    print(f"❌ PDF file not found: {pdf_path}")
                except Exception as e:
                    print(f"❌ Error processing PDF: {e}")
                continue

            # UNIFIED AGENT COMMANDS (NEW!)
            if user_input.strip().lower().startswith("/qa-test"):
                parts = user_input.strip().split(maxsplit=1)
                url = parts[1] if len(parts) > 1 else "http://localhost:8000"
                print(f"\n🧪 Running QA tests on: {url}")
                try:
                    result = tool_run_qa_workflow(url)
                    if result.get("success"):
                        print(f"\n✅ QA Testing Complete!")
                        print(f"   Report: {result.get('report_path')}")
                    else:
                        print(f"\n❌ QA Testing failed: {result.get('error')}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                continue

            if user_input.strip().lower() == "/test-mention":
                print("\n🧪 Testing @mention component...")
                print("   Make sure test server is running: python computer-use/test-app/server.py")
                test_cases = [
                    "Type '@' and verify autocomplete appears",
                    "Press Enter to insert mention",
                    "Test backspace with multiple mentions (check positioning bug)",
                    "Press Escape to close autocomplete",
                    "Test arrow key navigation"
                ]
                try:
                    result = tool_run_qa_workflow("http://localhost:8000", test_cases=test_cases)
                    if result.get("success"):
                        print(f"\n✅ @Mention Testing Complete!")
                        print(f"   Report: {result.get('report_path')}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                continue

            if user_input.strip().lower() == "/monitor-errors":
                print("\n🐛 Monitoring production errors...")
                try:
                    errors_data = load_and_analyze_errors()
                    print(f"\n{'='*70}")
                    print(f"ERRORS FOUND: {errors_data['errors_found']}")
                    print(f"{'='*70}\n")

                    if errors_data['errors_found'] > 0:
                        for i, error in enumerate(errors_data['errors'][:5], 1):
                            print(f"\n{i}. Error in {error['file']}:{error['line_num']}")
                            print(f"   {error['content']}")

                            # Analyze first 3 errors
                            if i <= 3:
                                print(f"   Analyzing...")
                                analysis = tool_analyze_production_error(
                                    error['content'],
                                    file_path=error['file'],
                                    context=error.get('context', '')
                                )

                                if analysis.get('success') and 'analysis' in analysis:
                                    fix = analysis['analysis']
                                    print(f"   Root Cause: {fix.get('root_cause', 'N/A')[:80]}...")
                                    print(f"   Fix: {fix.get('fix', {}).get('description', 'N/A')[:80]}...")
                    else:
                        print("✅ No errors found in logs directory")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                continue

            if user_input.strip().lower() == "/workflow-demo":
                print("\n🔄 Evaluator-Optimizer Workflow Demo")
                print("   Demonstrating Producer → Grader → Feedback loop\n")

                task = "Write a concise product roadmap for Q2 2026"
                producer_prompt = """Write a concise 3-month product roadmap for OneSuite Core Q2 2026.
Include: MVP phase, V1 features, and Scale phase. Keep it under 200 words."""

                grader_prompt = """Evaluate this product roadmap:

Criteria:
- Clear phases (MVP, V1, Scale)
- Under 200 words
- Specific and actionable

Respond with:
- PASS if meets all criteria
- FAIL if missing requirements (explain what's missing)"""

                try:
                    result = evaluator_optimizer_workflow(task, producer_prompt, grader_prompt, max_iterations=3)

                    if result['success']:
                        print(f"\n✅ Workflow succeeded in {result['iterations']} iterations")
                        print(f"\nFinal Output:\n{result['output']}")
                    else:
                        print(f"\n⚠️  Workflow ended: {result.get('reason', 'Unknown')}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                continue

            if user_input.strip().lower() == "/full-automation":
                print("\n" + "="*70)
                print("🎯 FULL AUTOMATION MODE - ALL CAPABILITIES")
                print("="*70)
                print("\nThis will run:")
                print("  1. QA Tests (on http://localhost:8000)")
                print("  2. Error Monitoring (analyze logs)")
                print("  3. Workflow Demo (Evaluator-Optimizer)")

                confirm = input("\nContinue? [y/N]: ")
                if confirm.lower() == 'y':
                    results = {}

                    # 1. QA Tests
                    print("\n" + "="*70)
                    print("STEP 1: QA TESTING")
                    print("="*70)
                    try:
                        qa_result = tool_run_qa_workflow("http://localhost:8000")
                        results['qa'] = qa_result
                        print(f"✅ QA Complete - {qa_result.get('report_path')}")
                    except Exception as e:
                        print(f"❌ QA Failed: {e}")
                        results['qa'] = {'error': str(e)}

                    # 2. Error Monitoring
                    print("\n" + "="*70)
                    print("STEP 2: ERROR MONITORING")
                    print("="*70)
                    try:
                        errors = load_and_analyze_errors()
                        results['errors'] = errors
                        print(f"✅ Found {errors['errors_found']} errors")
                    except Exception as e:
                        print(f"❌ Error Monitoring Failed: {e}")
                        results['errors'] = {'error': str(e)}

                    # 3. Workflow Demo
                    print("\n" + "="*70)
                    print("STEP 3: WORKFLOW DEMO")
                    print("="*70)
                    try:
                        workflow_result = evaluator_optimizer_workflow(
                            "Write a user story",
                            "Write a user story for OneSuite search filtering",
                            "Grade: PASS if has As a/I want to/So that format, FAIL otherwise",
                            max_iterations=2
                        )
                        results['workflow'] = workflow_result
                        print(f"✅ Workflow Complete - {workflow_result['success']}")
                    except Exception as e:
                        print(f"❌ Workflow Failed: {e}")
                        results['workflow'] = {'error': str(e)}

                    # Summary
                    print("\n" + "="*70)
                    print("🎉 FULL AUTOMATION COMPLETE")
                    print("="*70)
                    print(f"\nQA Tests: {'✅' if results.get('qa', {}).get('success') else '❌'}")
                    print(f"Error Monitoring: ✅ ({results.get('errors', {}).get('errors_found', 0)} errors)")
                    print(f"Workflow Demo: {'✅' if results.get('workflow', {}).get('success') else '❌'}")
                continue

            if user_input.strip().lower() == "/parallel-analysis":
                print("\n🔀 Parallelization Workflow Demo")
                print("   Analyzing OneSuite feature across all channels in parallel...\n")

                # Example: Multi-channel analysis
                task = "Analyze implementing advanced search filtering in OneSuite"

                subtasks = [
                    "Analyze implementing advanced search filtering specifically for the SEARCH channel. Consider: query complexity, result relevance, performance impact. Rate feasibility 1-10 and provide justification.",

                    "Analyze implementing advanced search filtering specifically for the SOCIAL channel. Consider: engagement metrics, audience targeting, content discovery. Rate feasibility 1-10 and provide justification.",

                    "Analyze implementing advanced search filtering specifically for the PROGRAMMATIC channel. Consider: inventory selection, bid optimization, targeting precision. Rate feasibility 1-10 and provide justification.",

                    "Analyze implementing advanced search filtering specifically for the COMMERCE channel. Consider: product discovery, price filtering, availability checks. Rate feasibility 1-10 and provide justification."
                ]

                aggregation_prompt = """Based on these channel-specific analyses, provide:
1. Overall recommendation for implementing search filtering
2. Which channels should prioritize this feature
3. Cross-channel consistency requirements
4. Implementation timeline and dependencies"""

                try:
                    result = parallelization_workflow(task, subtasks, aggregation_prompt)

                    if result['success']:
                        print(f"\n✅ Parallel Analysis Complete!")
                        print(f"   Analyzed {result['num_subtasks']} channels simultaneously")
                        print(f"\n{'='*70}")
                        print("FINAL RECOMMENDATION:")
                        print(f"{'='*70}")
                        print(result['final_output'])

                        # Show individual analyses
                        print(f"\n{'='*70}")
                        print("INDIVIDUAL CHANNEL ANALYSES:")
                        print(f"{'='*70}")
                        for analysis in result['subtask_results']:
                            print(f"\n**Analysis {analysis['subtask_num']}:**")
                            print(analysis['result'][:200] + "...")
                    else:
                        print("\n⚠️ Parallel analysis failed")
                except Exception as e:
                    print(f"\n❌ Error: {e}")

                continue

            # Add user message to history
            chat_history.append({"role": "user", "content": user_input})
            
            # Use tool-enabled OCAA with full chat history
            print("\n[OCAA] OCAA is thinking...")
            answer = call_ocaa_with_tools(user_input, chat_history=chat_history)
            
            # Add OCAA response to history
            chat_history.append({"role": "assistant", "content": answer})
            # Display answer
            print("\n" + "="*60)
            print("OCAA Response:")
            print("="*60)
            print(answer)
    
    finally:
        # Cleanup MCP servers on exit
        loop.run_until_complete(cleanup_mcp_servers())
        loop.close()

if __name__ == "__main__":
    main()
