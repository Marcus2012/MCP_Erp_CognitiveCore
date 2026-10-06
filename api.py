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

# --- Direct Domain Endpoints (Convenience CRU) ---

@app.get("/api/dashboard")
def get_dashboard():
    """Get executive dashboard KPIs."""
    return execute_tool("erp_dashboard_kpis", {})

# CRM
@app.get("/api/crm/leads")
def get_crm_leads(limit: int = 20, search: Optional[str] = None):
    return execute_tool("crm_list_leads", {"limit": limit, "search_term": search})

@app.get("/api/crm/leads/{lead_id}")
def get_crm_lead(lead_id: int):
    return execute_tool("crm_get_lead", {"lead_id": lead_id})

@app.post("/api/crm/leads")
def create_crm_lead(payload: Dict[str, Any] = Body(...)):
    return execute_tool("crm_create_lead", payload)

@app.put("/api/crm/leads/{lead_id}")
def update_crm_lead(lead_id: int, payload: Dict[str, Any] = Body(...)):
    payload["lead_id"] = lead_id
    return execute_tool("crm_update_lead", payload)

# Sales
@app.get("/api/sales/orders")
def get_sales_orders(limit: int = 20, search: Optional[str] = None):
    return execute_tool("sales_list_orders", {"limit": limit, "search_term": search})

@app.get("/api/sales/orders/{order_id}")
def get_sales_order(order_id: int):
    return execute_tool("sales_get_order", {"order_id": order_id})

@app.post("/api/sales/orders")
def create_sales_order(payload: Dict[str, Any] = Body(...)):
    return execute_tool("sales_create_quotation", payload)

@app.put("/api/sales/orders/{order_id}")
def update_sales_order(order_id: int, payload: Dict[str, Any] = Body(...)):
    payload["order_id"] = order_id
    return execute_tool("sales_update_order", payload)

@app.post("/api/sales/orders/{order_id}/lines")
def add_sales_order_line(order_id: int, payload: Dict[str, Any] = Body(...)):
    payload["order_id"] = order_id
    return execute_tool("sales_add_order_line", payload)

# Invoicing
@app.get("/api/invoices")
def get_invoices(limit: int = 20, search: Optional[str] = None):
    return execute_tool("invoices_list", {"limit": limit, "search_term": search})

@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: int):
    return execute_tool("invoices_get", {"invoice_id": invoice_id})

@app.post("/api/invoices")
def create_invoice(payload: Dict[str, Any] = Body(...)):
    return execute_tool("invoices_create", payload)

@app.put("/api/invoices/{invoice_id}")
def update_invoice(invoice_id: int, payload: Dict[str, Any] = Body(...)):
    payload["invoice_id"] = invoice_id
    return execute_tool("invoices_update_invoice", payload)

@app.post("/api/invoices/{invoice_id}/lines")
def add_invoice_line(invoice_id: int, payload: Dict[str, Any] = Body(...)):
    payload["invoice_id"] = invoice_id
    return execute_tool("invoices_add_line", payload)

# Inventory
@app.get("/api/inventory/products")
def get_inventory_products(limit: int = 25, query: Optional[str] = None):
    return execute_tool("inventory_search_products", {"limit": limit, "query": query})

@app.get("/api/inventory/products/{product_id}")
def get_inventory_product(product_id: int):
    return execute_tool("inventory_get_product", {"product_id": product_id})

@app.post("/api/inventory/products")
def create_inventory_product(payload: Dict[str, Any] = Body(...)):
    return execute_tool("inventory_create_product", payload)

@app.put("/api/inventory/products/{product_id}")
def update_inventory_product(product_id: int, payload: Dict[str, Any] = Body(...)):
    payload["product_id"] = product_id
    return execute_tool("inventory_update_product", payload)

@app.post("/api/inventory/stock-adjust")
def update_stock_quantity(payload: Dict[str, Any] = Body(...)):
    return execute_tool("inventory_update_stock_quantity", payload)

# Contacts
@app.get("/api/contacts")
def get_contacts(limit: int = 25, query: Optional[str] = None):
    return execute_tool("contacts_search", {"limit": limit, "query": query})

@app.get("/api/contacts/{partner_id}")
def get_contact(partner_id: int):
    return execute_tool("contacts_get", {"partner_id": partner_id})

@app.post("/api/contacts")
def create_contact(payload: Dict[str, Any] = Body(...)):
    return execute_tool("contacts_create", payload)

@app.put("/api/contacts/{partner_id}")
def update_contact(partner_id: int, payload: Dict[str, Any] = Body(...)):
    payload["partner_id"] = partner_id
    return execute_tool("contacts_update", payload)

# Projects & Tasks
@app.get("/api/projects")
def get_projects(limit: int = 20, search: Optional[str] = None):
    return execute_tool("projects_list", {"limit": limit, "search_term": search})

@app.get("/api/projects/{project_id}")
def get_project(project_id: int):
    return execute_tool("projects_get_project", {"project_id": project_id})

@app.post("/api/projects")
def create_project(payload: Dict[str, Any] = Body(...)):
    return execute_tool("projects_create_project", payload)

@app.put("/api/projects/{project_id}")
def update_project(project_id: int, payload: Dict[str, Any] = Body(...)):
    payload["project_id"] = project_id
    return execute_tool("projects_update_project", payload)

@app.get("/api/projects/tasks")
def get_project_tasks(limit: int = 25, search: Optional[str] = None):
    return execute_tool("projects_list_tasks", {"limit": limit, "search_term": search})

@app.get("/api/projects/tasks/{task_id}")
def get_project_task(task_id: int):
    return execute_tool("projects_get_task", {"task_id": task_id})

@app.post("/api/projects/tasks")
def create_project_task(payload: Dict[str, Any] = Body(...)):
    return execute_tool("projects_create_task", payload)

@app.put("/api/projects/tasks/{task_id}")
def update_project_task(task_id: int, payload: Dict[str, Any] = Body(...)):
    payload["task_id"] = task_id
    return execute_tool("projects_update_task", payload)

# HR & Employees
@app.get("/api/hr/employees")
def get_hr_employees(limit: int = 25, search: Optional[str] = None):
    return execute_tool("hr_list_employees", {"limit": limit, "search_term": search})

@app.get("/api/hr/employees/{employee_id}")
def get_hr_employee(employee_id: int):
    return execute_tool("hr_get_employee", {"employee_id": employee_id})

@app.post("/api/hr/employees")
def create_hr_employee(payload: Dict[str, Any] = Body(...)):
    return execute_tool("hr_create_employee", payload)

@app.put("/api/hr/employees/{employee_id}")
def update_hr_employee(employee_id: int, payload: Dict[str, Any] = Body(...)):
    payload["employee_id"] = employee_id
    return execute_tool("hr_update_employee", payload)

@app.get("/api/hr/departments")
def get_hr_departments():
    return execute_tool("hr_list_departments", {})

@app.post("/api/hr/departments")
def create_hr_department(payload: Dict[str, Any] = Body(...)):
    return execute_tool("hr_create_department", payload)

@app.put("/api/hr/departments/{department_id}")
def update_hr_department(department_id: int, payload: Dict[str, Any] = Body(...)):
    payload["department_id"] = department_id
    return execute_tool("hr_update_department", payload)

# Calendar & Activities
@app.get("/api/calendar/meetings")
def get_calendar_meetings(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 20):
    return execute_tool("calendar_list_meetings", {"start_date": start_date, "end_date": end_date, "limit": limit})

@app.post("/api/calendar/meetings")
def create_calendar_meeting(payload: Dict[str, Any] = Body(...)):
    return execute_tool("calendar_create_meeting", payload)

@app.put("/api/calendar/meetings/{event_id}")
def update_calendar_meeting(event_id: int, payload: Dict[str, Any] = Body(...)):
    payload["event_id"] = event_id
    return execute_tool("calendar_update_meeting", payload)

@app.get("/api/activities")
def get_activities(res_model: Optional[str] = None, res_id: Optional[int] = None, limit: int = 25):
    return execute_tool("activities_list", {"res_model": res_model, "res_id": res_id, "limit": limit})

@app.post("/api/activities")
def create_activity(payload: Dict[str, Any] = Body(...)):
    return execute_tool("activities_create", payload)

@app.put("/api/activities/{activity_id}")
def update_activity(activity_id: int, payload: Dict[str, Any] = Body(...)):
    payload["activity_id"] = activity_id
    return execute_tool("activities_update", payload)

# Generic ORM CRU
@app.post("/api/odoo/record")
def odoo_create_record_endpoint(payload: Dict[str, Any] = Body(...)):
    return execute_tool("odoo_create_record", payload)

@app.get("/api/odoo/record/{model}/{record_id}")
def odoo_read_record_endpoint(model: str, record_id: int):
    return execute_tool("odoo_read_record", {"model": model, "record_id": record_id})

@app.put("/api/odoo/record/{model}/{record_id}")
def odoo_update_record_endpoint(model: str, record_id: int, payload: Dict[str, Any] = Body(...)):
    return execute_tool("odoo_update_record", {"model": model, "record_id": record_id, "values": payload})

# Theme
@app.get("/api/theme")
def get_theme_branding():
    """Get current Odoo backend branding, colors, and typography."""
    return execute_tool("theme_get_branding", {})

@app.post("/api/theme/navbar")
def set_navbar_theme(payload: Dict[str, Any] = Body(...)):
    """Set custom navbar colors and primary accent."""
    return execute_tool("theme_set_navbar_theme", payload)

# --- Main Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting FastAPI Gateway on http://0.0.0.0:8000 (Odoo DB: {Config.ODOO_DB})...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

