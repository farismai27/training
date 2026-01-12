# OneSuite Platform User Stories

This document contains 51 user stories across 8 sections for the OneSuite platform, organized by user journey.

## Access & Onboarding

Epic Links: OAI-176 Authentication & Multi-tenancy Foundation, OAI-504 Onboarding Framework

### US-001: Quick Account Creation
- **As a:** new user
- **I want to:** create an account quickly
- **So that:** I can start using the platform without friction

**Acceptance Criteria:**
- When I sign up with email, I can start immediately
- When I make a typo in my password, the error is clear upon retry

### US-002: Session Persistence
- **As a:** returning user
- **I want to:** stay logged in
- **So that:** I don't have to re-authenticate every session

**Acceptance Criteria:**
- When I logged in yesterday and return today, I'm still authenticated
- When I've been idle, if I return within timeout, my session is still valid
- When I click logout, my session ends securely

### US-003: SSO Authentication (Publicis Employees)
- **As a:** Publicis employee
- **I want to:** log in with corporate credentials
- **So that:** I don't need to remember another password

**Acceptance Criteria:**
- On login page, when I click "Login with Lion", I'm redirected to Publicis SSO
- When I authenticate successfully and am redirected back, I'm logged into OneSuite
- When authentication fails, I see a clear error message upon redirect

### US-004: Client-Scoped Access
- **As a:** manager
- **I want to:** only see my assigned clients
- **So that:** I can focus on my work without distraction

**Acceptance Criteria:**
- When I log in managing Client A and B, I only see those clients
- Project list must show only projects associated with selected client
- Projects belonging to other clients must not appear regardless of permissions

### US-005: [Future] Super Admin - View All Clients
- **As a:** Super Admin
- **I want to:** see all clients
- **So that:** I can manage the platform globally

**Acceptance Criteria:**
- When I log in as super admin, I see all clients
- When I need to help a specific client and navigate to them, I have full access
- When I access admin settings, I can assign client permissions

### US-006: [Future] Super Admin - Create New Client
- **As a:** Super Admin
- **I want to:** create a new client
- **So that:** the client has an isolated environment for their data and users

**Acceptance Criteria:**
- When I create new client details, an isolated client is created
- When a client is created, it has a unique identifier following naming conventions
- When I need to assign admins to a client, I can immediately assign them

### US-007: [Future] Super Admin - Assign Users to Clients
- **As a:** Super Admin
- **I want to:** assign users to clients with specific roles
- **So that:** they have appropriate access levels

**Acceptance Criteria:**
- When I assign a user with a role, they can access only that client
- When assigned as Admin, upon login they have admin permissions for that client
- When assigned as User, upon login they have standard permissions only

### US-008: [Future] Super Admin - Upload Client Documents
- **As a:** Super Admin
- **I want to:** upload client onboarding documents (KPIs, taxonomy, competitors)
- **So that:** the AI agent has client-specific context

**Acceptance Criteria:**
- When I upload documents, the system validates required fields
- When documents are uploaded successfully and user asks about KPIs, agent references client-specific targets
- When invalid data is uploaded and validation fails, I see clear error messages

### US-009: [Future] Super Admin - Connect Client Platforms
- **As a:** Super Admin
- **I want to:** connect client platform accounts (Google Ads, Meta, Amazon, etc.)
- **So that:** performance data can be ingested

**Acceptance Criteria:**
- When I initiate connection with client platform credentials, I can authorize via OAuth
- When a platform is connected and authorization completes, data ingestion begins automatically
- When a connection fails, I see the specific error and can retry

### US-010: [Future] Super Admin - View Onboarding Status
- **As a:** Super Admin
- **I want to:** see onboarding completion status
- **So that:** I know when a client is ready for users

**Acceptance Criteria:**
- When client is being set up and I view status, I see which steps are complete vs incomplete
- When all required steps are done, it shows "Ready"
- When required steps are missing, it shows "Incomplete" with specific items needed

## Workspace Management

Epic Links: OAI-177 General UI/UX, OAI-178 Client_id & Project Management, OAI-1145 UI Chat Interface

### US-011: Create Project Workspace
- **As a:** user
- **I want to:** create a project workspace
- **So that:** I can organize my conversations by client or campaign

**Acceptance Criteria:**
- When I click "New Project", I see a creation form
- Form includes: Name (required, max 500 chars), Description (optional, max 500 chars), Color Picker
- When entering project name, system must:
  - Reject empty or whitespace-only values
  - Enforce maximum 500 characters
  - Display dynamic character counter
  - Prevent submission if project name already exists for my user with clear error
- When I fill in details and submit, project appears in my projects page
- When project is created and I open it, I can start conversations scoped to it
- When I manage multiple clients and create separate projects, conversations stay organized by client

### US-012: Edit/Rename Projects
- **As a:** user
- **I want to:** edit or rename my projects
- **So that:** I can keep them organized as work evolves

**Acceptance Criteria:**
- When project exists and I access its menu, I can edit name, description, or color
- When I make changes and save, updates are reflected immediately

### US-013: Delete Projects
- **As a:** user
- **I want to:** delete projects I no longer need
- **So that:** my workspace stays clean

**Acceptance Criteria:**
- When I want to remove a project and select delete, I see a confirmation dialog
- When I confirm deletion, the project and all its content is removed

## Conversation Experience

Epic Links: OAI-177 General UI/UX, OAI-1145 UI Chat Interface, OAI-802 Chat Interface & Streaming, OAI-805 MCP Tool Calling, OAI-804 Agent Core Runtime, OAI-893 Core Orchestration, OAI-894 Master & Tailored Config Management, OAI-907 Agent Tools

### US-014: Ask Questions in Plain English
- **As a:** marketer
- **I want to:** ask questions in plain English
- **So that:** I can get insights without writing SQL or switching between tools

**Acceptance Criteria:**
- When I type a question and submit it, I receive a relevant answer
- When I ask about campaign performance, response includes specific metrics
- When waiting for response, I see immediate feedback

### US-015: Answers Informed by Brand KB
- **As a:** marketer
- **I want to:** get answers informed by the Brand KB
- **So that:** responses include client-specific context and best practices

**Acceptance Criteria:**
- When I ask about best practices, agent responds citing Brand KB documentation
- When there's a client protocol and it's relevant, agent follows it
- When I need to verify, I can ask for sources and links are provided

### US-016: Channel-Specific Answers
- **As a:** marketer
- **I want to:** get relevant answers for my specific channel
- **So that:** I don't have to filter through irrelevant information

**Acceptance Criteria:**
- When I work on Google Ads and ask a question, answers are search-specific
- When I switch to Social work and select that context, answers adapt
- When platform-specific terminology is used, agent understands it

### US-017: Continue Previous Conversations
- **As a:** returning user
- **I want to:** continue where I left off
- **So that:** I don't have to re-explain my situation

**Acceptance Criteria:**
- When I had a conversation yesterday and return today, I can see it
- When I reference earlier context ("like we discussed"), agent understands
- When I want to start fresh and create new chat, previous context doesn't interfere

### US-018: Remember Conversation Context
- **As a:** user
- **I want to:** have the agent remember conversation context
- **So that:** I don't repeat information within a session

**Acceptance Criteria:**
- When I prefer concise answers and state it once, future responses are concise
- When I work on specific account and mention it, subsequent questions assume that context

### US-019: Dark Mode Support
- **As a:** user working late
- **I want to:** use dark mode
- **So that:** the screen doesn't strain my eyes

**Acceptance Criteria:**
- When I toggle dark mode, UI switches
- When I switched to dark mode and return later, it's still dark

### US-020: Start New Chat Sessions
- **As a:** user
- **I want to:** start a new chat
- **So that:** I can have a fresh conversation with the AI agent

**Acceptance Criteria:**
- When I'm in a project and click "New Chat", new session is created
- When chat is created and I refresh page, conversation persists
- When I start typing and send message, agent responds

### US-021: Delete Chat Sessions
- **As a:** user
- **I want to:** delete chats I no longer need
- **So that:** my workspace stays organized

**Acceptance Criteria:**
- When I want to delete a chat and select delete, I see confirmation dialog
- When I'm in active chat and try to delete, I'm told to switch first
- When I confirm deletion, chat and its content are removed

### US-022: Attach Files to Messages
- **As a:** user
- **I want to:** attach files to my messages
- **So that:** the AI can reference my documents

**Acceptance Criteria:**
- When I drag files to chat, they upload with progress indicators
- When attaching files, system accepts: Documents (.pdf, .docx, .txt, .md up to 50MB), Data (.csv, .xlsx, .jsonl up to 50MB), Images (.png, .jpg, .jpeg, .gif)
- When I have several files, I can upload up to 5 files per message
- When upload completes, image files show thumbnail preview, document/data files show file icon + filename
- When files are uploaded and I send message, AI can reference their content
- When upload fails, I see clear error and can retry

### US-023: Real-Time Response Streaming
- **As a:** user
- **I want to:** see responses stream in real-time
- **So that:** I know the AI is working and can read as it types

**Acceptance Criteria:**
- When AI responds, I see text appear incrementally
- When streaming is in progress and I want to stop, I can cancel response
- When streaming completes, response is fully formatted

### US-024: See Tools Being Used
- **As a:** user
- **I want to:** see what tools the AI is using
- **So that:** I understand how it's getting information

**Acceptance Criteria:**
- When AI uses a tool and it runs, I see which tool is executing
- When tool returns results, I can see what it found
- When tool fails, I see a clear error message

### US-025: Agent Selection
- **As a:** user
- **I want to:** select which agent to chat with
- **So that:** I get specialized help for my channel

**Acceptance Criteria:**
- When starting new chat from homepage or project, agent selection dropdown available in both locations
- When I see agent selector, I can choose from available agents
- When I select an agent, the selected agent persists for entire session until explicitly changed
- When I select an agent, chat session uses that agent's specialized knowledge
- When in project and chatting, agent has access to project documents
- When in active chat and switch to different agent, new context is created and previous context not carried over
- When starting chat from homepage and agent selected: Project Knowledge Base cannot be loaded, no project documents/artifacts loaded, agent loads only system default context (system prompt and toolset)

### US-026: [Future] Rename Chat Sessions
- **As a:** user
- **I want to:** rename existing chats
- **So that:** I can better organize my conversations

**Acceptance Criteria:**
- When chat exists and I access its menu, I can rename it
- When I make changes and save, updates are reflected immediately

## Agent Capabilities

Epic Links: OAI-804 Agent Core Runtime, OAI-907 Agent Tools, OAI-893 Core Orchestration, OAI-894 Master & Tailored Config Management, OAI-805 MCP Tool Calling, OAI-1104 KB - Capability-Specific Content, OAI-1115 Search - KB & Agent Memory, OAI-176 Authentication & Multi-tenancy Foundation, OAI-510 Agentic Tools, OAI-524 Agent Query Tool Capability, OAI-1096 Search - Query System Methods, OAI-183 Data Lakehouse Databricks, OAI-1088 Search Bronze to Gold Pipeline, OAI-1427 Custom Ingestion - Search Data, OAI-1745 Search Google Ads Bronze Ingestion, OAI-1746 Search GSC Bronze Ingestion, OAI-1747 Search SA360 Bronze Ingestion, OAI-1760 Search Google Ads Silver Normalization, OAI-1806 Search SA360 Silver Normalization, OAI-1807 Search GSC Silver Normalization

### US-027: [Future] Reasoning Mode
- **As a:** user
- **I want to:** enable reasoning mode for complex questions
- **So that:** I get more thorough step-by-step analysis

**Acceptance Criteria:**
- When I have a complex question and enable reasoning mode, agent shows thinking process
- When reasoning is enabled and agent responds, I see step-by-step reasoning before answer
- When reasoning takes longer and is enabled, I understand the trade-off for better quality

### US-028: Agent Searches Brand KB
- **As a:** user
- **I want to:** have the agent search the Brand KB
- **So that:** responses include client-specific documentation and best practices

**Acceptance Criteria:**
- When Brand KB documents exist and I ask about client processes, agent searches and cites relevant docs
- When metadata filtering available and I ask channel-specific questions, results filtered by channel
- When agent finds KB content and responds, citations link to source documents

### US-029: Automatic Tool Usage
- **As a:** user
- **I want to:** have the agent use the right tools automatically
- **So that:** I get accurate calculations and data without specifying tools

**Acceptance Criteria:**
- When I ask a calculation question, agent responds using the calculator tool

---

**Total User Stories:** 51 across 8 sections
**Status:** Core functionality implemented, future features marked with [Future]
**Last Updated:** January 12, 2026
