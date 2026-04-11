"""MaxKB MCP Server — all MaxKB API endpoints exposed as MCP tools."""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from maxkb_mcp.client import MaxKBClient

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "MaxKB MCP Server",
    instructions="Exposes all MaxKB API endpoints as MCP tools for managing agents, knowledge bases, models, tools, chat, users, and more.",
)

_client: MaxKBClient | None = None
_workspace: str = "default"


def _get_client() -> MaxKBClient:
    global _client
    if _client is None:
        base_url = os.environ.get("MAXKB_URL", "https://maxkb.garzaos.cloud")
        username = os.environ.get("MAXKB_USERNAME", "admin")
        password = os.environ.get("MAXKB_PASSWORD", "")
        if not password:
            raise RuntimeError(
                "MAXKB_PASSWORD environment variable is required. "
                "Set MAXKB_URL, MAXKB_USERNAME, and MAXKB_PASSWORD."
            )
        _client = MaxKBClient(base_url, username, password)
    return _client


def _ws(workspace: str | None = None) -> str:
    return workspace or _workspace


# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION (AGENT) TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_applications(workspace: str | None = None) -> str:
    """List all agents/applications in the workspace."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/application")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_application(application_id: str, workspace: str | None = None) -> str:
    """Get details of a specific agent/application by ID."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/application/{application_id}")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_application(
    name: str,
    desc: str = "",
    app_type: str = "SIMPLE",
    model_id: str = "",
    workspace: str | None = None,
) -> str:
    """Create a new agent/application.

    Args:
        name: Agent name (max 64 chars)
        desc: Description (max 256 chars)
        app_type: SIMPLE or WORK_FLOW
        model_id: LLM model ID to use
    """
    c = _get_client()
    payload: dict[str, Any] = {
        "name": name,
        "desc": desc,
        "type": app_type,
        "folder_id": "default",
    }
    if model_id:
        payload["model_id"] = model_id
    r = await c.post(f"workspace/{_ws(workspace)}/application", json=payload)
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def update_application(
    application_id: str,
    name: str | None = None,
    desc: str | None = None,
    model_id: str | None = None,
    prologue: str | None = None,
    system_prompt: str | None = None,
    mcp_servers: str | None = None,
    mcp_enable: bool | None = None,
    workspace: str | None = None,
) -> str:
    """Update an agent/application configuration.

    Args:
        application_id: Application UUID
        name: New name
        desc: New description
        model_id: New LLM model ID
        prologue: Welcome message shown to users
        system_prompt: System prompt for the agent
        mcp_servers: JSON string of MCP server config (for SIMPLE agents)
        mcp_enable: Enable/disable MCP tools
    """
    c = _get_client()
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if desc is not None:
        payload["desc"] = desc
    if model_id is not None:
        payload["model_id"] = model_id
    if prologue is not None:
        payload["prologue"] = prologue
    if system_prompt is not None:
        payload["system"] = system_prompt
    if mcp_servers is not None:
        payload["mcp_servers"] = mcp_servers
    if mcp_enable is not None:
        payload["mcp_enable"] = mcp_enable
        payload["mcp_output_enable"] = mcp_enable
    r = await c.put(
        f"workspace/{_ws(workspace)}/application/{application_id}", json=payload
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def delete_application(
    application_id: str, workspace: str | None = None
) -> str:
    """Delete an agent/application."""
    c = _get_client()
    r = await c.delete(
        f"workspace/{_ws(workspace)}/application/{application_id}"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def publish_application(
    application_id: str, workspace: str | None = None
) -> str:
    """Publish an agent so it becomes accessible via API and chat URL."""
    c = _get_client()
    r = await c.put(
        f"workspace/{_ws(workspace)}/application/{application_id}/publish",
        json={},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def unpublish_application(
    application_id: str, workspace: str | None = None
) -> str:
    """Unpublish an agent (remove public access)."""
    c = _get_client()
    r = await c.put(
        f"workspace/{_ws(workspace)}/application/{application_id}/un_publish",
        json={},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_application_access_token(
    application_id: str, workspace: str | None = None
) -> str:
    """Get the public access token for an agent's chat URL."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/access_token"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_application_api_key(
    application_id: str, workspace: str | None = None
) -> str:
    """Create a new API key for an agent. Returns the newly created key with its secret.

    Note: MaxKB's API key endpoint always creates a new key on POST.
    There is no separate list endpoint — use get_application to see existing keys.
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/application/{application_id}/application_key",
        json={},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_application_stats(
    application_id: str,
    start_time: str = "",
    end_time: str = "",
    workspace: str | None = None,
) -> str:
    """Get usage statistics for an agent (message count, token usage, etc.).

    Args:
        application_id: Application UUID
        start_time: Start date (YYYY-MM-DD). Defaults to 30 days ago.
        end_time: End date (YYYY-MM-DD). Defaults to today.
    """
    import datetime

    if not end_time:
        end_time = datetime.date.today().isoformat()
    if not start_time:
        start_time = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/application_stats",
        params={"start_time": start_time, "end_time": end_time},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_application_token_usage(
    application_id: str, workspace: str | None = None
) -> str:
    """Get token usage details for an agent."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/application_token_usage"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_application_top_questions(
    application_id: str, workspace: str | None = None
) -> str:
    """Get the top/most-asked questions for an agent."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/top_questions"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def list_application_mcp_tools(
    application_id: str, workspace: str | None = None
) -> str:
    """List all MCP tools available to an agent."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/mcp_tools"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_application_model(
    application_id: str, workspace: str | None = None
) -> str:
    """Get the LLM model configuration for an agent."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/model"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# CHAT TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def chat_completions(
    application_id: str,
    api_key: str,
    message: str,
) -> str:
    """Send a chat message to an agent using the OpenAI-compatible API.

    Args:
        application_id: The agent's UUID
        api_key: The agent's API key (e.g. agent-xxxx)
        message: The user message to send
    """
    c = _get_client()
    url = f"{c.base_url}/chat/api/{application_id}/chat/completions"
    resp = await c._http.post(
        url,
        json={
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        },
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=120,
    )
    resp.raise_for_status()
    return json.dumps(resp.json(), indent=2, ensure_ascii=False)


@mcp.tool()
async def list_chat_sessions(
    application_id: str, workspace: str | None = None
) -> str:
    """List chat sessions/conversations for an agent."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/chat"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_chat_messages(
    application_id: str,
    chat_id: str,
    workspace: str | None = None,
) -> str:
    """Get all messages in a specific chat session.

    Args:
        application_id: The agent's UUID
        chat_id: The chat session UUID
    """
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/chat/{chat_id}/chat_record"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_knowledge_bases(workspace: str | None = None) -> str:
    """List all knowledge bases in the workspace."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/knowledge")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_knowledge_base(
    knowledge_id: str, workspace: str | None = None
) -> str:
    """Get details of a specific knowledge base."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_knowledge_base(
    name: str,
    desc: str = "",
    workspace: str | None = None,
) -> str:
    """Create a new knowledge base.

    Args:
        name: Knowledge base name
        desc: Description
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/knowledge",
        json={"name": name, "desc": desc},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def update_knowledge_base(
    knowledge_id: str,
    name: str | None = None,
    desc: str | None = None,
    workspace: str | None = None,
) -> str:
    """Update a knowledge base."""
    c = _get_client()
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if desc is not None:
        payload["desc"] = desc
    r = await c.put(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}", json=payload
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def delete_knowledge_base(
    knowledge_id: str, workspace: str | None = None
) -> str:
    """Delete a knowledge base and all its documents."""
    c = _get_client()
    r = await c.delete(f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def knowledge_hit_test(
    knowledge_id: str,
    query: str,
    top_n: int = 5,
    similarity: float = 0.6,
    workspace: str | None = None,
) -> str:
    """Test knowledge retrieval by searching for relevant paragraphs.

    Args:
        knowledge_id: Knowledge base UUID
        query: Search query text
        top_n: Number of results to return
        similarity: Minimum similarity threshold (0-1)
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/hit_test",
        json={
            "query_text": query,
            "top_number": top_n,
            "similarity": similarity,
        },
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def sync_knowledge_embedding(
    knowledge_id: str, workspace: str | None = None
) -> str:
    """Re-sync/re-embed all documents in a knowledge base."""
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/embedding",
        json={},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def export_knowledge_base(
    knowledge_id: str, workspace: str | None = None
) -> str:
    """Export a knowledge base (returns download info)."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/export"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENT TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_documents(
    knowledge_id: str, workspace: str | None = None
) -> str:
    """List all documents in a knowledge base."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_document(
    knowledge_id: str, document_id: str, workspace: str | None = None
) -> str:
    """Get details of a specific document."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document/{document_id}"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_text_document(
    knowledge_id: str,
    name: str,
    content: str,
    workspace: str | None = None,
) -> str:
    """Create a new text document in a knowledge base.

    Args:
        knowledge_id: Knowledge base UUID
        name: Document title
        content: Text content of the document
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document",
        json={
            "name": name,
            "paragraphs": [{"content": content, "title": name}],
            "type": "TEXT",
        },
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_web_document(
    knowledge_id: str,
    url: str,
    workspace: str | None = None,
) -> str:
    """Create a document by importing from a web URL.

    Args:
        knowledge_id: Knowledge base UUID
        url: Web URL to scrape and import
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document",
        json={"url": url, "type": "WEB"},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def delete_document(
    knowledge_id: str, document_id: str, workspace: str | None = None
) -> str:
    """Delete a document from a knowledge base."""
    c = _get_client()
    r = await c.delete(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document/{document_id}"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# PARAGRAPH TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_paragraphs(
    knowledge_id: str, document_id: str, workspace: str | None = None
) -> str:
    """List all paragraphs/chunks in a document."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document/{document_id}/paragraph"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_paragraph(
    knowledge_id: str,
    document_id: str,
    content: str,
    title: str = "",
    workspace: str | None = None,
) -> str:
    """Add a paragraph/chunk to a document.

    Args:
        knowledge_id: Knowledge base UUID
        document_id: Document UUID
        content: Paragraph text content
        title: Optional title for the paragraph
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document/{document_id}/paragraph",
        json={"content": content, "title": title},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def update_paragraph(
    knowledge_id: str,
    document_id: str,
    paragraph_id: str,
    content: str | None = None,
    title: str | None = None,
    workspace: str | None = None,
) -> str:
    """Update a paragraph's content or title."""
    c = _get_client()
    payload: dict[str, Any] = {}
    if content is not None:
        payload["content"] = content
    if title is not None:
        payload["title"] = title
    r = await c.put(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document/{document_id}/paragraph/{paragraph_id}",
        json=payload,
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def delete_paragraph(
    knowledge_id: str,
    document_id: str,
    paragraph_id: str,
    workspace: str | None = None,
) -> str:
    """Delete a paragraph from a document."""
    c = _get_client()
    r = await c.delete(
        f"workspace/{_ws(workspace)}/knowledge/{knowledge_id}/document/{document_id}/paragraph/{paragraph_id}"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# MODEL TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_models(workspace: str | None = None) -> str:
    """List all configured LLM models."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/model")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_model(model_id: str, workspace: str | None = None) -> str:
    """Get details of a specific LLM model configuration."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/model/{model_id}")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def list_model_providers() -> str:
    """List all available LLM model providers (OpenAI, Anthropic, Google, etc.)."""
    c = _get_client()
    r = await c.get("provider")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_model(
    provider: str,
    name: str,
    model_type: str,
    model_name: str,
    credential: dict,
    workspace: str | None = None,
) -> str:
    """Create/configure a new LLM model.

    Args:
        provider: Provider name (e.g. 'model_openai_provider', 'model_anthropic_provider')
        name: Display name for this model config
        model_type: Type (e.g. 'LLM', 'EMBEDDING', 'STT', 'TTS')
        model_name: Model identifier (e.g. 'claude-sonnet-4-20250514')
        credential: Provider credentials dict (e.g. {"api_key": "sk-..."})
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/model",
        json={
            "provider": provider,
            "name": name,
            "model_type": model_type,
            "model_name": model_name,
            "credential": credential,
        },
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def delete_model(model_id: str, workspace: str | None = None) -> str:
    """Delete a model configuration."""
    c = _get_client()
    r = await c.delete(f"workspace/{_ws(workspace)}/model/{model_id}")
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# TOOL MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_tools(
    folder_id: str = "default", workspace: str | None = None
) -> str:
    """List all registered tools (MCP servers, HTTP tools, etc.).

    Args:
        folder_id: Folder to list tools from (default = root)
    """
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/tool",
        params={"folder_id": folder_id},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_tool(tool_id: str, workspace: str | None = None) -> str:
    """Get details of a specific tool."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/tool/{tool_id}")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_tool(
    name: str,
    desc: str = "",
    tool_type: str = "MCP",
    config: dict | None = None,
    workspace: str | None = None,
) -> str:
    """Create a new tool (MCP server, HTTP tool, etc.).

    Args:
        name: Tool name
        desc: Description
        tool_type: Tool type (MCP, HTTP, etc.)
        config: Tool configuration dict
    """
    c = _get_client()
    payload: dict[str, Any] = {
        "name": name,
        "desc": desc,
        "tool_type": tool_type,
    }
    if config:
        payload["config"] = config
    r = await c.post(f"workspace/{_ws(workspace)}/tool", json=payload)
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def delete_tool(tool_id: str, workspace: str | None = None) -> str:
    """Delete a tool."""
    c = _get_client()
    r = await c.delete(f"workspace/{_ws(workspace)}/tool/{tool_id}")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def publish_tool(tool_id: str, workspace: str | None = None) -> str:
    """Publish a tool to make it available."""
    c = _get_client()
    r = await c.put(
        f"workspace/{_ws(workspace)}/tool/{tool_id}/publish", json={}
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def debug_tool(
    tool_id: str,
    input_data: dict | None = None,
    workspace: str | None = None,
) -> str:
    """Debug/test a tool with sample input.

    Args:
        tool_id: Tool UUID
        input_data: Input parameters for the tool
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/tool/{tool_id}/debug",
        json=input_data or {},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# USER & WORKSPACE TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_user_profile() -> str:
    """Get the current logged-in user's profile."""
    c = _get_client()
    r = await c.get("user/profile")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def list_workspace_users(workspace: str | None = None) -> str:
    """List all users in the workspace."""
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/user_list")
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# FOLDER TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_folders(
    folder_type: str = "APPLICATION", workspace: str | None = None
) -> str:
    """List folders for organizing resources.

    Args:
        folder_type: Type of folder (APPLICATION, KNOWLEDGE, etc.)
    """
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/{folder_type}/folder")
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def create_folder(
    name: str,
    folder_type: str = "APPLICATION",
    parent_id: str = "default",
    workspace: str | None = None,
) -> str:
    """Create a new folder.

    Args:
        name: Folder name
        folder_type: Type (APPLICATION, KNOWLEDGE, etc.)
        parent_id: Parent folder ID (default = root)
    """
    c = _get_client()
    r = await c.post(
        f"workspace/{_ws(workspace)}/{folder_type}/folder",
        json={"name": name, "parent_id": parent_id},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
async def delete_folder(
    folder_id: str,
    folder_type: str = "APPLICATION",
    workspace: str | None = None,
) -> str:
    """Delete a folder."""
    c = _get_client()
    r = await c.delete(
        f"workspace/{_ws(workspace)}/{folder_type}/folder/{folder_id}"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM MANAGEMENT TOOLS
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# WORKFLOW TOOLS (for Advanced Agents)
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_application_workflow(
    application_id: str, workspace: str | None = None
) -> str:
    """Get the workflow definition for an advanced (WORK_FLOW) agent.

    Returns the nodes and edges that define the workflow graph.
    """
    c = _get_client()
    r = await c.get(f"workspace/{_ws(workspace)}/application/{application_id}")
    data = r.get("data", {})
    wf = data.get("work_flow", {})
    if isinstance(wf, str):
        wf = json.loads(wf)
    return json.dumps(
        {"code": 200, "data": wf}, indent=2, ensure_ascii=False
    )


@mcp.tool()
async def update_application_workflow(
    application_id: str,
    workflow_json: str,
    workspace: str | None = None,
) -> str:
    """Update the workflow for an advanced agent.

    Args:
        application_id: Application UUID
        workflow_json: Full workflow JSON string with nodes and edges
    """
    c = _get_client()
    wf = json.loads(workflow_json)
    r = await c.put(
        f"workspace/{_ws(workspace)}/application/{application_id}",
        json={"work_flow": wf},
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# IMPORT / EXPORT TOOLS
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def export_application(
    application_id: str, workspace: str | None = None
) -> str:
    """Export an agent configuration (for backup or import to another instance)."""
    c = _get_client()
    r = await c.get(
        f"workspace/{_ws(workspace)}/application/{application_id}/export"
    )
    return json.dumps(r, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════════════


def main():
    """Run the MaxKB MCP server."""
    from dotenv import load_dotenv

    load_dotenv()
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))

    # Configure allowed hosts for external access (DNS rebinding protection)
    allowed_hosts_str = os.environ.get("MCP_ALLOWED_HOSTS", "")
    if allowed_hosts_str:
        allowed_hosts = [h.strip() for h in allowed_hosts_str.split(",") if h.strip()]
    else:
        allowed_hosts = []

    mcp.settings.host = host
    mcp.settings.port = port

    if transport in ("sse", "streamable-http") and allowed_hosts:
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=allowed_hosts,
        )
    elif transport in ("sse", "streamable-http"):
        # Disable DNS rebinding protection when no allowed hosts specified
        # (for development or when behind a reverse proxy like Traefik)
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        )

    if transport == "sse":
        mcp.run(transport="sse")
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
