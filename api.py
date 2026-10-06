"""
FastAPI Backend for Cognitive ERP (Odoo 20).
Provides REST, Chat Streaming (SSE), and MCP Tool Inspection endpoints
for the Web Frontend (MCP_Erp_CognitiveCoreFrontend) and external AI agents.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from config import Config
from odoo_client import get_odoo_client
from tool_registry import TOOLS_DEFINITIONS, TOOLS_BY_NAME, execute_tool
from agent_engine import AgentEngine

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("CognitiveERP.FastAPI")

app = FastAPI(
    title="Cognitive ERP Odoo 20 API & MCP Gateway",
    description="Backend API with AI Agent Orchestration and MCP Tool Execution for Odoo 20 Community.",
    version="1.0.0"
)

# Enable CORS for frontend clients (React / Next.js / Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local and web dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Request Models ---

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="List of previous conversation messages")
    model: Optional[str] = Field(None, description="Optional LLM model name (e.g. gpt-4o-mini)")
    stream: bool = Field(False, description="Whether to stream the response via SSE")

class ToolExecuteRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool function")

# --- System & Health Endpoints ---

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Cognitive ERP Odoo 20 Backend",
        "version": "1.0.0",
        "odoo_url": Config.ODOO_URL,
        "odoo_db": Config.ODOO_DB,
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health_check():
    """Checks live connectivity with Odoo ERP."""
    try:
        client = get_odoo_client()
        uid = client.authenticate()
        version_info = client.get_server_version()
        return {
            "status": "connected",
            "odoo_url": Config.ODOO_URL,
            "database": Config.ODOO_DB,
            "user_email": Config.ODOO_EMAIL,
            "authenticated_uid": uid,
            "server_version": version_info.get("server_version", "20.0")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "disconnected",
                "error": str(e),
                "odoo_url": Config.ODOO_URL,
                "database": Config.ODOO_DB
            }
        )

# --- MCP Tools Inspector Endpoints ---

@app.get("/api/mcp/tools")
def list_mcp_tools():
    """
    Returns all 41 MCP tools with their metadata, categories, and JSON schemas.
    Used by McpInspector.tsx in the frontend.
    """
    tools = []
    for t in TOOLS_DEFINITIONS:
        tools.append({
            "name": t["name"],
            "category": t["category"],
            "description": t["description"],
            "parameters": t["parameters"]
        })
    return {
        "count": len(tools),
        "tools": tools
    }

@app.post("/api/mcp/tools/{tool_name}/execute")
def call_mcp_tool(tool_name: str, payload: ToolExecuteRequest):
    """
    Directly execute any registered MCP tool by name.
    """
    if tool_name not in TOOLS_BY_NAME:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")
    
    try:
        result = execute_tool(tool_name, payload.arguments)
        return {
            "success": True,
            "tool_name": tool_name,
            "arguments": payload.arguments,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing tool '{tool_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- AI Chat & Agent Endpoints ---

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Standard (non-streaming) AI Chat endpoint.
    Processes user message, invokes necessary Odoo ERP tools, and returns the answer.
    """
    messages_dicts = [{"role": m.role, "content": m.content} for m in request.messages]
    result = await AgentEngine.chat_completion(messages_dicts, model=request.model)
    return result

@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Server-Sent Events (SSE) streaming chat endpoint.
    Streams tokens and tool calls in real time to the React frontend.
    """
    messages_dicts = [{"role": m.role, "content": m.content} for m in request.messages]
    generator = AgentEngine.stream_chat_response(messages_dicts, model=request.model)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# --- Direct Domain Endpoints (Convenience) ---

@app.get("/api/dashboard")
def get_dashboard():
    """Get executive dashboard KPIs."""
    return execute_tool("erp_dashboard_kpis", {})

@app.get("/api/crm/leads")
def get_crm_leads(limit: int = 20, search: Optional[str] = None):
    return execute_tool("crm_list_leads", {"limit": limit, "search_term": search})

@app.get("/api/sales/orders")
def get_sales_orders(limit: int = 20, search: Optional[str] = None):
    return execute_tool("sales_list_orders", {"limit": limit, "search_term": search})

@app.get("/api/invoices")
def get_invoices(limit: int = 20, search: Optional[str] = None):
    return execute_tool("invoices_list", {"limit": limit, "search_term": search})

@app.get("/api/inventory/products")
def get_inventory_products(limit: int = 25, query: Optional[str] = None):
    return execute_tool("inventory_search_products", {"limit": limit, "query": query})

@app.get("/api/contacts")
def get_contacts(limit: int = 25, query: Optional[str] = None):
    return execute_tool("contacts_search", {"limit": limit, "query": query})

@app.get("/api/projects/tasks")
def get_project_tasks(limit: int = 25, search: Optional[str] = None):
    return execute_tool("projects_list_tasks", {"limit": limit, "search_term": search})

@app.get("/api/hr/employees")
def get_hr_employees(limit: int = 25, search: Optional[str] = None):
    return execute_tool("hr_list_employees", {"limit": limit, "search_term": search})

# --- Main Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting FastAPI Gateway on http://0.0.0.0:8000 (Odoo DB: {Config.ODOO_DB})...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
