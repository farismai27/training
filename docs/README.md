# OCAA Documentation
Complete documentation for the OneSuite Core Architect Agent (OCAA) multi-agent system.

## Quick Links
- **New to the project?** Start with [Getting Started](./01-getting-started/setup-guide.md)
- **Need to build a feature?** Check [Architecture](./02-architecture/overview.md) and [Features](./03-features/overview.md)
- **Writing code?** See [Development Guidelines](./04-development/coding-standards.md)
- **Running agents?** Read [Agent System](./03-features/agents/unified-agent.md)

## Documentation Structure

### 01. Getting Started
Onboarding guide for new developers - setup, overview, and common workflows.

- [Setup Guide](./01-getting-started/setup-guide.md) - Environment setup and dependencies
- [Project Overview](./01-getting-started/project-overview.md) - Architecture & tech stack
- [Quick Start](./01-getting-started/quick-start.md) - Run your first agent
- [Common Tasks](./01-getting-started/common-tasks.md) - Frequent development workflows

### 02. Architecture
Core architectural patterns and system design.

- [System Overview](./02-architecture/overview.md) - Multi-agent architecture
- [Folder Structure](./02-architecture/folder-structure.md) - Source code organization
- [Agent System](./02-architecture/agent-system.md) - Agent design patterns
- [Data Flow](./02-architecture/data-flow.md) - API → Agent → Response patterns
- [Error Handling](./02-architecture/error-handling.md) - Error patterns and logging

### 03. Features
Feature-specific implementation guides.

#### Agents
- [Agents Overview](./03-features/agents/overview.md) - Complete agent system guide
- [Unified Agent](./03-features/agents/unified-agent.md) - All-in-one OCAA agent
- [RAG Agent](./03-features/agents/rag-agent.md) - RAG & hybrid retrieval
- [Computer Use Agent](./03-features/agents/computer-use.md) - QA automation
- [Production Monitor](./03-features/agents/production-monitor.md) - Error monitoring

#### Web UI
- [Web UI Overview](./03-features/web-ui/overview.md) - Streamlit interface guide
- [Chat System](./03-features/web-ui/chat-system.md) - Chat implementation
- [Quick Actions](./03-features/web-ui/quick-actions.md) - Pre-built prompts

#### RAG System
- [RAG Overview](./03-features/rag/overview.md) - Retrieval-augmented generation
- [Hybrid Retrieval](./03-features/rag/hybrid-retrieval.md) - Semantic + Lexical search
- [Re-ranking](./03-features/rag/reranking.md) - Claude-powered re-ranking
- [Document Server](./03-features/rag/document-server.md) - MCP server integration

#### Other Features
- [Workflows](./03-features/workflows.md) - Evaluator-Optimizer patterns
- [Computer Use](./03-features/computer-use.md) - Browser automation
- [Document Processing](./03-features/documents.md) - PDF, DOCX, MD conversion

### 04. Development
Development workflows, standards, and best practices.

- [Coding Standards](./04-development/coding-standards.md) - Code style and conventions
- [Git Workflow](./04-development/git-workflow.md) - Branching, commits, and PRs
- [Testing](./04-development/testing.md) - Testing strategy and patterns
- [Logging](./04-development/logging.md) - Production logging patterns

### 05. API Integration
Claude API and MCP integration patterns.

- [Claude API](./05-api/claude-api.md) - Messages API patterns
- [MCP Protocol](./05-api/mcp-protocol.md) - Model Context Protocol
- [Streaming](./05-api/streaming.md) - SSE and streaming responses
- [Tool Use](./05-api/tool-use.md) - Function calling patterns

### 06. Deployment
Deployment and production setup.

- [Local Deployment](./06-deployment/local.md) - Running locally
- [Production Setup](./06-deployment/production.md) - Production configuration
- [Environment Variables](./06-deployment/environment.md) - Configuration management
- [Monitoring](./06-deployment/monitoring.md) - Production monitoring

### 07. Workflows
Parallel development and automation workflows.

- [Git Worktrees](./07-workflows/worktrees.md) - Parallel development
- [Auto-Fix System](./07-workflows/auto-fix.md) - Automated bug fixing
- [CI/CD Pipeline](./07-workflows/cicd.md) - GitHub Actions

### 08. Reference
Quick reference guides and API documentation.

- [Commands Reference](./08-reference/commands.md) - All available commands
- [System Prompts](./08-reference/system-prompts.md) - Agent system prompts
- [Error Codes](./08-reference/error-codes.md) - Error reference
- [FAQ](./08-reference/faq.md) - Frequently asked questions

## Contributing to Documentation
Documentation is critical to project success. When contributing:

- ✅ **Keep docs in sync with code** - Update docs when changing implementation
- ✅ **Write for humans** - Be concise, clear, and scannable
- ✅ **Use examples** - Show practical patterns, not just theory
- ✅ **Link rather than duplicate** - Reference existing docs and official resources
- ✅ **Follow the structure** - Place new docs in the appropriate section

See [Coding Standards](./04-development/coding-standards.md) for documentation writing guidelines.

## External Resources
- [Anthropic Documentation](https://docs.anthropic.com)
- [Claude API Reference](https://docs.anthropic.com/en/api/messages)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Python Testing with Pytest](https://docs.pytest.org)

## Need Help?
- **For quick setup**: See [Getting Started](./01-getting-started/setup-guide.md)
- **For architecture questions**: See [Architecture Overview](./02-architecture/overview.md)
- **For feature guides**: See [Features](./03-features/overview.md)
- **For API patterns**: See [API Integration](./05-api/claude-api.md)

---

**Version:** 1.0.0
**Last Updated:** 2026-01-18
**Maintainer:** OCAA Team
