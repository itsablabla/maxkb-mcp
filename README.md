# MaxKB MCP Server

An MCP (Model Context Protocol) server that exposes **all MaxKB API endpoints** as tools, enabling any MCP-compatible agent to programmatically manage a MaxKB instance — agents, knowledge bases, models, tools, chat, users, and more.

## Features

- **45+ MCP tools** covering the full MaxKB Admin API surface
- **Automatic authentication** — logs in and refreshes tokens automatically
- **Multiple transports** — stdio, SSE, and streamable-http
- **Docker-ready** — includes Dockerfile for easy deployment

## Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| **Applications** | 15 | CRUD agents, publish/unpublish, API keys, stats, MCP tools, model config |
| **Chat** | 3 | Send messages (OpenAI-compatible), list sessions, get history |
| **Knowledge Bases** | 7 | CRUD knowledge bases, hit test, embedding sync, export |
| **Documents** | 5 | Create text/web documents, list, get, delete |
| **Paragraphs** | 4 | CRUD paragraph chunks within documents |
| **Models** | 5 | List/configure LLM models, providers, model types |
| **Tools** | 6 | Manage MCP servers and HTTP tools, publish, debug |
| **Users** | 2 | User profile, workspace user list |
| **Folders** | 3 | Organize resources into folders |
| **System** | 2 | System settings and version info |
| **Workflows** | 2 | Get/update advanced agent workflow definitions |
| **Import/Export** | 1 | Export agent configurations |

## Quick Start

### 1. Install

```bash
pip install .
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your MaxKB URL and credentials
```

Required environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MAXKB_URL` | MaxKB instance URL | `https://maxkb.garzaos.cloud` |
| `MAXKB_USERNAME` | Admin username | `admin` |
| `MAXKB_PASSWORD` | Admin password | **(required)** |
| `MCP_TRANSPORT` | Transport type: `stdio`, `sse`, `streamable-http` | `stdio` |
| `MCP_HOST` | Host to bind (for SSE/HTTP) | `0.0.0.0` |
| `MCP_PORT` | Port to bind (for SSE/HTTP) | `8000` |

### 3. Run

**stdio mode** (for local MCP clients like Claude Desktop):
```bash
MAXKB_PASSWORD=xxx maxkb-mcp
```

**SSE mode** (for remote MCP clients):
```bash
MCP_TRANSPORT=sse MAXKB_PASSWORD=xxx maxkb-mcp
```

**Docker**:
```bash
docker build -t maxkb-mcp .
docker run -p 8000:8000 \
  -e MAXKB_URL=https://maxkb.garzaos.cloud \
  -e MAXKB_USERNAME=admin \
  -e MAXKB_PASSWORD=xxx \
  -e MCP_TRANSPORT=sse \
  maxkb-mcp
```

## MCP Client Configuration

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "maxkb": {
      "command": "maxkb-mcp",
      "env": {
        "MAXKB_URL": "https://maxkb.garzaos.cloud",
        "MAXKB_USERNAME": "admin",
        "MAXKB_PASSWORD": "your-password"
      }
    }
  }
}
```

### MaxKB (as an MCP tool inside MaxKB itself)

```json
{
  "maxkb-admin": {
    "url": "https://your-host:8000/sse",
    "transport": "sse"
  }
}
```

## Available Tools

### Application Management
- `list_applications` — List all agents
- `get_application` — Get agent details
- `create_application` — Create new agent (SIMPLE or WORK_FLOW)
- `update_application` — Update agent config (name, model, MCP servers, etc.)
- `delete_application` — Delete an agent
- `publish_application` — Publish agent for public access
- `unpublish_application` — Remove public access
- `get_application_access_token` — Get public chat URL token
- `list_application_api_keys` — List API keys
- `create_application_api_key` — Create new API key
- `get_application_stats` — Usage statistics
- `get_application_token_usage` — Token consumption
- `get_application_top_questions` — Most-asked questions
- `list_application_mcp_tools` — List MCP tools available to agent
- `get_application_model` — Get model configuration

### Chat
- `chat_completions` — Send a message (OpenAI-compatible format)
- `list_chat_sessions` — List conversation sessions
- `get_chat_messages` — Get messages in a session

### Knowledge Bases
- `list_knowledge_bases` — List all knowledge bases
- `get_knowledge_base` — Get KB details
- `create_knowledge_base` — Create new KB
- `update_knowledge_base` — Update KB
- `delete_knowledge_base` — Delete KB
- `knowledge_hit_test` — Test retrieval with a query
- `sync_knowledge_embedding` — Re-embed documents
- `export_knowledge_base` — Export KB

### Documents
- `list_documents` — List documents in a KB
- `get_document` — Get document details
- `create_text_document` — Create text document
- `create_web_document` — Import from URL
- `delete_document` — Delete document

### Paragraphs
- `list_paragraphs` — List chunks in a document
- `create_paragraph` — Add a chunk
- `update_paragraph` — Update chunk content
- `delete_paragraph` — Delete a chunk

### Models
- `list_models` — List configured models
- `get_model` — Get model details
- `create_model` — Configure a new model
- `delete_model` — Remove a model
- `list_model_providers` — Available providers
- `list_model_types` — Available model types

### Tools
- `list_tools` — List all tools/MCP servers
- `get_tool` — Get tool details
- `create_tool` — Register a new tool
- `delete_tool` — Remove a tool
- `publish_tool` — Publish a tool
- `debug_tool` — Test a tool

### Workflows
- `get_application_workflow` — Get workflow graph
- `update_application_workflow` — Update workflow

### Users & System
- `get_user_profile` — Current user info
- `list_workspace_users` — Workspace members
- `list_folders` / `create_folder` / `delete_folder` — Folder management
- `get_system_setting` / `get_system_version` — System info
- `export_application` — Export agent config

## License

MIT
