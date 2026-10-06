import json
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from config import Config
from services.crm_service import CRMService
from services.sales_service import SalesService
from services.invoicing_service import InvoicingService
from services.inventory_service import InventoryService
from services.contacts_service import ContactsService
from services.projects_service import ProjectsService
from services.hr_service import HRService
from services.activities_calendar_service import ActivitiesCalendarService
from services.analytics_service import AnalyticsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("CognitiveERP.MCPServer")

# Initialize FastMCP Server
mcp = FastMCP("Cognitive ERP Odoo 20")

# ==========================================
# 📊 EXECUTIVE KPIS & ANALYTICS
# ==========================================

@mcp.tool()
def erp_dashboard_kpis() -> str:
    """
    Get high-level executive dashboard and KPIs of Odoo ERP:
    Active CRM opportunities pipeline value, confirmed sales totals, open quotations,
    unpaid invoices / receivables, active projects, open tasks, and catalog totals.
    """
    result = AnalyticsService.get_dashboard_summary()
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def odoo_generic_query(
    model: str,
    method: str = "search_read",
    domain: Optional[List[Any]] = None,
    fields: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0,
    order: Optional[str] = None
) -> str:
    """
    Execute a flexible read query on any Odoo model.
    Supported methods: 'search_read', 'fields_get', 'search_count'.
    Useful to inspect custom models or specific fields.
    """
    result = AnalyticsService.generic_query(
        model=model,
        method=method,
        domain=domain,
        fields=fields,
        limit=limit,
        offset=offset,
        order=order
    )
    return json.dumps(result, indent=2, ensure_ascii=False)

# ==========================================
# 💼 CRM & PIPELINE
# ==========================================

@mcp.tool()
def crm_list_stages() -> str:
    """List all pipeline stages in Odoo CRM with stage IDs and names."""
    stages = CRMService.list_stages()
    return json.dumps(stages, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_list_leads(
    search_term: Optional[str] = None,
    stage_name: Optional[str] = None,
    is_won: Optional[bool] = None,
    user_id: Optional[int] = None,
    limit: int = 20
) -> str:
    """
    Search and list CRM leads and opportunities.
    Allows filtering by lead title/client name, pipeline stage, won status, or salesperson.
    """
    leads = CRMService.list_leads(
        search_term=search_term,
        stage_name=stage_name,
        is_won=is_won,
        user_id=user_id,
        limit=limit
    )
    return json.dumps(leads, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_get_lead(lead_id: int) -> str:
    """Get full details of a specific CRM opportunity/lead by its ID."""
    lead = CRMService.get_lead(lead_id)
    return json.dumps(lead, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_create_lead(
    name: str,
    partner_id: Optional[int] = None,
    partner_name: Optional[str] = None,
    email_from: Optional[str] = None,
    phone: Optional[str] = None,
    expected_revenue: float = 0.0,
    probability: Optional[float] = None,
    description: Optional[str] = None,
    priority: str = "1",
    is_opportunity: bool = True
) -> str:
    """
    Create a new CRM lead or opportunity.
    Priority values: '0' (Normal), '1' (Low), '2' (High), '3' (Very High).
    """
    res = CRMService.create_lead(
        name=name,
        partner_id=partner_id,
        partner_name=partner_name,
        email_from=email_from,
        phone=phone,
        expected_revenue=expected_revenue,
        probability=probability,
        description=description,
        priority=priority,
        is_opportunity=is_opportunity
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_update_lead(
    lead_id: int,
    stage_id: Optional[int] = None,
    expected_revenue: Optional[float] = None,
    probability: Optional[float] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None
) -> str:
    """Update fields of an existing CRM lead/opportunity."""
    values: Dict[str, Any] = {}
    if stage_id is not None:
        values["stage_id"] = stage_id
    if expected_revenue is not None:
        values["expected_revenue"] = expected_revenue
    if probability is not None:
        values["probability"] = probability
    if description is not None:
        values["description"] = description
    if priority is not None:
        values["priority"] = priority

    res = CRMService.update_lead(lead_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_mark_won(lead_id: int) -> str:
    """Mark a CRM opportunity as Won (100% probability, stage won)."""
    res = CRMService.mark_lead_won(lead_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_mark_lost(lead_id: int, lost_reason_id: Optional[int] = None) -> str:
    """Mark a CRM opportunity as Lost."""
    res = CRMService.mark_lead_lost(lead_id, lost_reason_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 💰 SALES & QUOTATIONS
# ==========================================

@mcp.tool()
def sales_list_orders(
    search_term: Optional[str] = None,
    partner_id: Optional[int] = None,
    state: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    List sales orders and quotations.
    state options: 'draft' (Quotation), 'sent' (Quotation Sent), 'sale' (Sales Order), 'cancel' (Cancelled).
    """
    orders = SalesService.list_orders(
        search_term=search_term,
        partner_id=partner_id,
        state=state,
        limit=limit
    )
    return json.dumps(orders, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_get_order(order_id: int) -> str:
    """Get complete details of a sales order/quotation including line items, products, and prices."""
    order = SalesService.get_order(order_id)
    return json.dumps(order, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_create_quotation(
    partner_id: int,
    order_lines: List[Dict[str, Any]],
    payment_term_id: Optional[int] = None,
    note: Optional[str] = None
) -> str:
    """
    Create a new sales quotation in Odoo.
    order_lines should be a list of objects with:
      - 'product_id' (int, required)
      - 'qty' (float, default 1.0)
      - 'price_unit' (float, optional: if omitted, Odoo uses standard list price)
      - 'description' (str, optional line description)
    Example: [{"product_id": 1, "qty": 2, "price_unit": 1250.0}]
    """
    res = SalesService.create_quotation(
        partner_id=partner_id,
        order_lines=order_lines,
        payment_term_id=payment_term_id,
        note=note
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_confirm_order(order_id: int) -> str:
    """Confirm a draft quotation into an active Sales Order (creates delivery/invoice hooks)."""
    res = SalesService.confirm_order(order_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_cancel_order(order_id: int) -> str:
    """Cancel a quotation or sales order."""
    res = SalesService.cancel_order(order_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 🧾 INVOICING & BILLING
# ==========================================

@mcp.tool()
def invoices_list(
    move_type: str = "out_invoice",
    state: Optional[str] = None,
    payment_state: Optional[str] = None,
    partner_id: Optional[int] = None,
    search_term: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    List customer invoices or vendor bills.
    move_type: 'out_invoice' (Customer Invoice), 'in_invoice' (Vendor Bill), 'out_refund' (Credit Note).
    state: 'draft', 'posted', 'cancel'.
    payment_state: 'not_paid', 'in_payment', 'paid', 'reversed'.
    """
    invoices = InvoicingService.list_invoices(
        move_type=move_type,
        state=state,
        payment_state=payment_state,
        partner_id=partner_id,
        search_term=search_term,
        limit=limit
    )
    return json.dumps(invoices, indent=2, ensure_ascii=False)

@mcp.tool()
def invoices_get(invoice_id: int) -> str:
    """Get complete details of an invoice or bill including line items and balance."""
    invoice = InvoicingService.get_invoice(invoice_id)
    return json.dumps(invoice, indent=2, ensure_ascii=False)

@mcp.tool()
def invoices_create(
    partner_id: int,
    invoice_lines: List[Dict[str, Any]],
    move_type: str = "out_invoice",
    invoice_date: Optional[str] = None,
    invoice_date_due: Optional[str] = None,
    ref: Optional[str] = None
) -> str:
    """
    Create a new draft invoice or vendor bill.
    invoice_lines format: [{"product_id": 1, "quantity": 1, "price_unit": 1250.0, "name": "Service description"}]
    """
    res = InvoicingService.create_invoice(
        partner_id=partner_id,
        invoice_lines=invoice_lines,
        move_type=move_type,
        invoice_date=invoice_date,
        invoice_date_due=invoice_date_due,
        ref=ref
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def invoices_post(invoice_id: int) -> str:
    """Validate and Post a draft invoice (generates invoice number and journal entries)."""
    res = InvoicingService.post_invoice(invoice_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def invoices_register_payment(
    invoice_id: int,
    amount: Optional[float] = None,
    payment_date: Optional[str] = None
) -> str:
    """Register payment for an open invoice."""
    res = InvoicingService.register_payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_date=payment_date
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 📦 INVENTORY & PRODUCTS
# ==========================================

@mcp.tool()
def inventory_search_products(
    query: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = 25
) -> str:
    """
    Search products and services in the catalog by name, code/SKU, or barcode.
    product_type: 'service', 'consu' (Consumable), 'product' (Storable).
    """
    products = InventoryService.search_products(
        query=query,
        product_type=product_type,
        limit=limit
    )
    return json.dumps(products, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_get_product(product_id: int) -> str:
    """Get full product specifications, sales price, cost, and on-hand inventory."""
    product = InventoryService.get_product(product_id)
    return json.dumps(product, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_create_product(
    name: str,
    list_price: float,
    default_code: Optional[str] = None,
    standard_price: Optional[float] = None,
    product_type: str = "service",
    description: Optional[str] = None
) -> str:
    """
    Create a new product or service in Odoo.
    product_type: 'service', 'consu' (Consumable), 'product' (Storable).
    """
    res = InventoryService.create_product(
        name=name,
        list_price=list_price,
        default_code=default_code,
        standard_price=standard_price,
        product_type=product_type,
        description=description
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_update_product(
    product_id: int,
    list_price: Optional[float] = None,
    standard_price: Optional[float] = None,
    description: Optional[str] = None
) -> str:
    """Update sales price, cost price, or description of a product."""
    values: Dict[str, Any] = {}
    if list_price is not None:
        values["list_price"] = list_price
    if standard_price is not None:
        values["standard_price"] = standard_price
    if description is not None:
        values["description_sale"] = description

    res = InventoryService.update_product(product_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_list_pickings(
    picking_type: Optional[str] = None,
    state: Optional[str] = None,
    partner_id: Optional[int] = None,
    limit: int = 20
) -> str:
    """
    List stock picking transfers (Deliveries, Receipts, Internal Transfers).
    picking_type: 'outgoing' (Delivery), 'incoming' (Receipt), 'internal'.
    state: 'draft', 'waiting', 'confirmed', 'assigned' (Ready), 'done', 'cancel'.
    """
    pickings = InventoryService.list_pickings(
        picking_type=picking_type,
        state=state,
        partner_id=partner_id,
        limit=limit
    )
    return json.dumps(pickings, indent=2, ensure_ascii=False)

# ==========================================
# 👥 CONTACTS & PARTNERS
# ==========================================

@mcp.tool()
def contacts_search(
    query: Optional[str] = None,
    is_company: Optional[bool] = None,
    is_customer: Optional[bool] = None,
    is_supplier: Optional[bool] = None,
    limit: int = 25
) -> str:
    """Search customers, suppliers, and contacts by name, email, phone, or Tax ID (RUC / DNI)."""
    contacts = ContactsService.search_contacts(
        query=query,
        is_company=is_company,
        is_customer=is_customer,
        is_supplier=is_supplier,
        limit=limit
    )
    return json.dumps(contacts, indent=2, ensure_ascii=False)

@mcp.tool()
def contacts_get(partner_id: int) -> str:
    """Get complete contact card with address, commercial company, and transaction history."""
    contact = ContactsService.get_contact(partner_id)
    return json.dumps(contact, indent=2, ensure_ascii=False)

@mcp.tool()
def contacts_create(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    vat: Optional[str] = None,
    is_company: bool = False,
    street: Optional[str] = None,
    city: Optional[str] = None,
    is_customer: bool = True,
    is_supplier: bool = False,
    comment: Optional[str] = None
) -> str:
    """Create a new contact, customer, or vendor with RUC/DNI and contact information."""
    res = ContactsService.create_contact(
        name=name,
        email=email,
        phone=phone,
        vat=vat,
        is_company=is_company,
        street=street,
        city=city,
        is_customer=is_customer,
        is_supplier=is_supplier,
        comment=comment
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def contacts_update(
    partner_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    vat: Optional[str] = None,
    street: Optional[str] = None,
    city: Optional[str] = None
) -> str:
    """Update contact information."""
    values: Dict[str, Any] = {}
    if name is not None:
        values["name"] = name
    if email is not None:
        values["email"] = email
    if phone is not None:
        values["phone"] = phone
    if vat is not None:
        values["vat"] = vat
    if street is not None:
        values["street"] = street
    if city is not None:
        values["city"] = city

    res = ContactsService.update_contact(partner_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 📋 PROJECTS & TASKS
# ==========================================

@mcp.tool()
def projects_list(search_term: Optional[str] = None, limit: int = 20) -> str:
    """List active projects and total task counts."""
    projects = ProjectsService.list_projects(search_term=search_term, limit=limit)
    return json.dumps(projects, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_list_tasks(
    project_id: Optional[int] = None,
    search_term: Optional[str] = None,
    user_id: Optional[int] = None,
    is_closed: Optional[bool] = None,
    limit: int = 25
) -> str:
    """List project tasks or to-dos filtered by project, assignee, or status."""
    tasks = ProjectsService.list_tasks(
        project_id=project_id,
        search_term=search_term,
        user_id=user_id,
        is_closed=is_closed,
        limit=limit
    )
    return json.dumps(tasks, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_get_task(task_id: int) -> str:
    """Get full details and description of a task."""
    task = ProjectsService.get_task(task_id)
    return json.dumps(task, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_create_task(
    name: str,
    project_id: Optional[int] = None,
    user_ids: Optional[List[int]] = None,
    description: Optional[str] = None,
    date_deadline: Optional[str] = None,
    priority: str = "0"
) -> str:
    """
    Create a new task or to-do.
    priority: '0' (Normal), '1' (Important).
    date_deadline: 'YYYY-MM-DD'.
    """
    res = ProjectsService.create_task(
        name=name,
        project_id=project_id,
        user_ids=user_ids,
        description=description,
        date_deadline=date_deadline,
        priority=priority
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_update_task(
    task_id: int,
    name: Optional[str] = None,
    stage_id: Optional[int] = None,
    description: Optional[str] = None,
    date_deadline: Optional[str] = None,
    priority: Optional[str] = None
) -> str:
    """Update task details or move to another stage."""
    values: Dict[str, Any] = {}
    if name is not None:
        values["name"] = name
    if stage_id is not None:
        values["stage_id"] = stage_id
    if description is not None:
        values["description"] = description
    if date_deadline is not None:
        values["date_deadline"] = date_deadline
    if priority is not None:
        values["priority"] = priority

    res = ProjectsService.update_task(task_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 👔 HUMAN RESOURCES (HR)
# ==========================================

@mcp.tool()
def hr_list_employees(
    search_term: Optional[str] = None,
    department_id: Optional[int] = None,
    limit: int = 25
) -> str:
    """List company employees with department, job title, email, and phone."""
    employees = HRService.list_employees(
        search_term=search_term,
        department_id=department_id,
        limit=limit
    )
    return json.dumps(employees, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_get_employee(employee_id: int) -> str:
    """Get detailed profile of an employee."""
    employee = HRService.get_employee(employee_id)
    return json.dumps(employee, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_list_departments() -> str:
    """List departments in the organization."""
    departments = HRService.list_departments()
    return json.dumps(departments, indent=2, ensure_ascii=False)

# ==========================================
# ⏰ ACTIVITIES & CALENDAR
# ==========================================

@mcp.tool()
def activities_list(
    res_model: Optional[str] = None,
    res_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: int = 25
) -> str:
    """
    List scheduled activities / next actions across ERP records.
    res_model: e.g. 'crm.lead', 'sale.order', 'res.partner', 'account.move'.
    """
    activities = ActivitiesCalendarService.list_activities(
        res_model=res_model,
        res_id=res_id,
        user_id=user_id,
        limit=limit
    )
    return json.dumps(activities, indent=2, ensure_ascii=False)

@mcp.tool()
def activities_create(
    res_model: str,
    res_id: int,
    summary: str,
    date_deadline: str,
    note: Optional[str] = None,
    user_id: Optional[int] = None
) -> str:
    """
    Schedule a new activity (call, todo, email) on any ERP record.
    date_deadline format: 'YYYY-MM-DD'.
    """
    res = ActivitiesCalendarService.create_activity(
        res_model=res_model,
        res_id=res_id,
        summary=summary,
        date_deadline=date_deadline,
        note=note,
        user_id=user_id
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def activities_mark_done(activity_id: int, feedback: Optional[str] = None) -> str:
    """Mark a scheduled activity as completed with optional feedback."""
    res = ActivitiesCalendarService.mark_activity_done(activity_id, feedback=feedback)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def calendar_list_meetings(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20
) -> str:
    """List calendar events and meetings."""
    events = ActivitiesCalendarService.list_calendar_events(
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return json.dumps(events, indent=2, ensure_ascii=False)

@mcp.tool()
def calendar_create_meeting(
    name: str,
    start: str,
    stop: str,
    partner_ids: Optional[List[int]] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    allday: bool = False
) -> str:
    """
    Create a new meeting/event in the Odoo calendar.
    start / stop format: 'YYYY-MM-DD HH:MM:SS'.
    """
    res = ActivitiesCalendarService.create_calendar_event(
        name=name,
        start=start,
        stop=stop,
        partner_ids=partner_ids,
        description=description,
        location=location,
        allday=allday
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 🚀 MAIN ENTRYPOINT
# ==========================================

if __name__ == "__main__":
    if not Config.validate():
        logger.error("Missing required configuration variables in .env")
        sys.exit(1)

    logger.info(f"Starting {Config.SERVER_NAME} for {Config.ODOO_URL} (DB: {Config.ODOO_DB})...")
    mcp.run()
