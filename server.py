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
from services.theme_service import ThemeService

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
# 📊 EXECUTIVE KPIS & GENERIC ORM CRU
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

@mcp.tool()
def odoo_create_record(model: str, values: Dict[str, Any]) -> str:
    """Create a record in any Odoo model (Generic Create)."""
    result = AnalyticsService.create_record(model=model, values=values)
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def odoo_read_record(model: str, record_id: int, fields: Optional[List[str]] = None) -> str:
    """Read a specific record by model and ID in Odoo (Generic Read)."""
    result = AnalyticsService.read_record(model=model, record_id=record_id, fields=fields)
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def odoo_update_record(model: str, record_id: int, values: Dict[str, Any]) -> str:
    """Update fields on a specific record in any Odoo model (Generic Update)."""
    result = AnalyticsService.update_record(model=model, record_id=record_id, values=values)
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
    priority: str = "1"
) -> str:
    """Create a new CRM lead or opportunity."""
    res = CRMService.create_lead(
        name=name,
        partner_id=partner_id,
        partner_name=partner_name,
        email_from=email_from,
        phone=phone,
        expected_revenue=expected_revenue,
        probability=probability,
        description=description,
        priority=priority
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_update_lead(
    lead_id: int,
    name: Optional[str] = None,
    stage_id: Optional[int] = None,
    expected_revenue: Optional[float] = None,
    probability: Optional[float] = None,
    description: Optional[str] = None,
    partner_id: Optional[int] = None,
    phone: Optional[str] = None,
    email_from: Optional[str] = None
) -> str:
    """Update fields on a CRM lead/opportunity (stage, revenue, probability, notes, contact)."""
    values = {}
    if name is not None: values["name"] = name
    if stage_id is not None: values["stage_id"] = stage_id
    if expected_revenue is not None: values["expected_revenue"] = expected_revenue
    if probability is not None: values["probability"] = probability
    if description is not None: values["description"] = description
    if partner_id is not None: values["partner_id"] = partner_id
    if phone is not None: values["phone"] = phone
    if email_from is not None: values["email_from"] = email_from

    res = CRMService.update_lead(lead_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_mark_won(lead_id: int) -> str:
    """Mark a CRM opportunity as Won (100% probability)."""
    res = CRMService.mark_lead_won(lead_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def crm_mark_lost(lead_id: int, lost_reason_id: Optional[int] = None) -> str:
    """Mark a CRM opportunity as Lost."""
    res = CRMService.mark_lead_lost(lead_id, lost_reason_id=lost_reason_id)
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
    """List sales orders and quotations. State: 'draft', 'sent', 'sale', 'cancel'."""
    orders = SalesService.list_orders(
        search_term=search_term,
        partner_id=partner_id,
        state=state,
        limit=limit
    )
    return json.dumps(orders, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_get_order(order_id: int) -> str:
    """Get full details of a sales order or quotation including line items and totals."""
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
    Create a new quotation in draft state.
    order_lines format: [{'product_id': 1, 'qty': 2, 'price_unit': 1250.0, 'description': 'Optional note'}]
    """
    res = SalesService.create_quotation(
        partner_id=partner_id,
        order_lines=order_lines,
        payment_term_id=payment_term_id,
        note=note
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_update_order(
    order_id: int,
    partner_id: Optional[int] = None,
    payment_term_id: Optional[int] = None,
    note: Optional[str] = None,
    validity_date: Optional[str] = None
) -> str:
    """Update header fields of a sales order or quotation."""
    values = {}
    if partner_id is not None: values["partner_id"] = partner_id
    if payment_term_id is not None: values["payment_term_id"] = payment_term_id
    if note is not None: values["note"] = note
    if validity_date is not None: values["validity_date"] = validity_date

    res = SalesService.update_order(order_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_add_order_line(
    order_id: int,
    product_id: int,
    qty: float = 1.0,
    price_unit: Optional[float] = None,
    description: Optional[str] = None
) -> str:
    """Add a product line to an existing sales order."""
    res = SalesService.add_order_line(
        order_id=order_id,
        product_id=product_id,
        qty=qty,
        price_unit=price_unit,
        description=description
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_update_order_line(
    line_id: int,
    product_uom_qty: Optional[float] = None,
    price_unit: Optional[float] = None,
    name: Optional[str] = None
) -> str:
    """Update quantity, price, or description of a line in a sales order."""
    values = {}
    if product_uom_qty is not None: values["product_uom_qty"] = product_uom_qty
    if price_unit is not None: values["price_unit"] = price_unit
    if name is not None: values["name"] = name

    res = SalesService.update_order_line(line_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_confirm_order(order_id: int) -> str:
    """Confirm a quotation to create a confirmed Sales Order."""
    res = SalesService.confirm_order(order_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def sales_cancel_order(order_id: int) -> str:
    """Cancel a sales order or quotation."""
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
    """List customer invoices or vendor bills. move_type: 'out_invoice', 'in_invoice'."""
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
    """Get full details of an invoice including lines and residual balance."""
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
    """Create a draft invoice or vendor bill."""
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
def invoices_update_invoice(
    invoice_id: int,
    partner_id: Optional[int] = None,
    invoice_date: Optional[str] = None,
    invoice_date_due: Optional[str] = None,
    ref: Optional[str] = None,
    narration: Optional[str] = None
) -> str:
    """Update fields on a draft invoice."""
    values = {}
    if partner_id is not None: values["partner_id"] = partner_id
    if invoice_date is not None: values["invoice_date"] = invoice_date
    if invoice_date_due is not None: values["invoice_date_due"] = invoice_date_due
    if ref is not None: values["ref"] = ref
    if narration is not None: values["narration"] = narration

    res = InvoicingService.update_invoice(invoice_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def invoices_add_line(
    invoice_id: int,
    name: str,
    price_unit: float,
    quantity: float = 1.0,
    product_id: Optional[int] = None
) -> str:
    """Add a new line item to a draft invoice."""
    res = InvoicingService.add_invoice_line(
        invoice_id=invoice_id,
        name=name,
        price_unit=price_unit,
        quantity=quantity,
        product_id=product_id
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def invoices_post(invoice_id: int) -> str:
    """Validate and Post a draft invoice (assigns official invoice number)."""
    res = InvoicingService.post_invoice(invoice_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def invoices_register_payment(
    invoice_id: int,
    amount: Optional[float] = None,
    payment_date: Optional[str] = None
) -> str:
    """Register payment or collection for a posted invoice."""
    res = InvoicingService.register_payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_date=payment_date
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 📦 INVENTORY & CATALOG
# ==========================================

@mcp.tool()
def inventory_search_products(
    query: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = 25
) -> str:
    """Search products and services in the catalog by name, SKU, or barcode."""
    products = InventoryService.search_products(
        query=query,
        product_type=product_type,
        limit=limit
    )
    return json.dumps(products, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_get_product(product_id: int) -> str:
    """Get full details of a specific product: sale price, cost, on-hand qty."""
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
    """Create a new product or service in the catalog."""
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
    name: Optional[str] = None,
    list_price: Optional[float] = None,
    standard_price: Optional[float] = None,
    default_code: Optional[str] = None,
    barcode: Optional[str] = None,
    description_sale: Optional[str] = None
) -> str:
    """Update fields on an existing product (price, cost, SKU, description)."""
    values = {}
    if name is not None: values["name"] = name
    if list_price is not None: values["list_price"] = list_price
    if standard_price is not None: values["standard_price"] = standard_price
    if default_code is not None: values["default_code"] = default_code
    if barcode is not None: values["barcode"] = barcode
    if description_sale is not None: values["description_sale"] = description_sale

    res = InventoryService.update_product(product_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_update_stock_quantity(
    product_id: int,
    new_quantity: float,
    location_id: Optional[int] = None
) -> str:
    """Update on-hand stock quantity of a product via stock.quant."""
    res = InventoryService.update_stock_quantity(
        product_id=product_id,
        new_quantity=new_quantity,
        location_id=location_id
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_list_pickings(
    picking_type: Optional[str] = None,
    state: Optional[str] = None,
    partner_id: Optional[int] = None,
    limit: int = 20
) -> str:
    """List stock transfers (Delivery orders, receipts, internal transfers)."""
    pickings = InventoryService.list_pickings(
        picking_type=picking_type,
        state=state,
        partner_id=partner_id,
        limit=limit
    )
    return json.dumps(pickings, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_get_picking(picking_id: int) -> str:
    """Get full details of a stock picking/transfer with move lines."""
    picking = InventoryService.get_picking(picking_id)
    return json.dumps(picking, indent=2, ensure_ascii=False)

@mcp.tool()
def inventory_update_picking(
    picking_id: int,
    scheduled_date: Optional[str] = None,
    origin: Optional[str] = None,
    partner_id: Optional[int] = None
) -> str:
    """Update fields on a stock picking."""
    values = {}
    if scheduled_date is not None: values["scheduled_date"] = scheduled_date
    if origin is not None: values["origin"] = origin
    if partner_id is not None: values["partner_id"] = partner_id

    res = InventoryService.update_picking(picking_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

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
    """Search customers, suppliers, and contacts by name, email, phone, or VAT/RUC/DNI."""
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
    """Get complete contact card with commercial balance and details."""
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
    """Create a new contact, customer, or supplier."""
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
    city: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """Update fields on a contact/partner."""
    values = {}
    if name is not None: values["name"] = name
    if email is not None: values["email"] = email
    if phone is not None: values["phone"] = phone
    if vat is not None: values["vat"] = vat
    if street is not None: values["street"] = street
    if city is not None: values["city"] = city
    if comment is not None: values["comment"] = comment

    res = ContactsService.update_contact(partner_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 📋 PROJECTS & TASKS
# ==========================================

@mcp.tool()
def projects_list(search_term: Optional[str] = None, limit: int = 20) -> str:
    """List active projects with task counts."""
    projects = ProjectsService.list_projects(search_term=search_term, limit=limit)
    return json.dumps(projects, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_get_project(project_id: int) -> str:
    """Get full details of a specific project."""
    project = ProjectsService.get_project(project_id)
    return json.dumps(project, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_create_project(
    name: str,
    partner_id: Optional[int] = None,
    user_id: Optional[int] = None,
    description: Optional[str] = None,
    date_start: Optional[str] = None,
    date: Optional[str] = None
) -> str:
    """Create a new project in Odoo."""
    res = ProjectsService.create_project(
        name=name,
        partner_id=partner_id,
        user_id=user_id,
        description=description,
        date_start=date_start,
        date=date
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_update_project(
    project_id: int,
    name: Optional[str] = None,
    partner_id: Optional[int] = None,
    user_id: Optional[int] = None,
    description: Optional[str] = None,
    date_start: Optional[str] = None,
    date: Optional[str] = None
) -> str:
    """Update fields on an existing project."""
    values = {}
    if name is not None: values["name"] = name
    if partner_id is not None: values["partner_id"] = partner_id
    if user_id is not None: values["user_id"] = user_id
    if description is not None: values["description"] = description
    if date_start is not None: values["date_start"] = date_start
    if date is not None: values["date"] = date

    res = ProjectsService.update_project(project_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def projects_list_tasks(
    project_id: Optional[int] = None,
    search_term: Optional[str] = None,
    user_id: Optional[int] = None,
    is_closed: Optional[bool] = None,
    limit: int = 25
) -> str:
    """List tasks with optional filters."""
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
    """Get full task details including description."""
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
    """Create a new project task or todo."""
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
    """Update properties of a task."""
    values = {}
    if name is not None: values["name"] = name
    if stage_id is not None: values["stage_id"] = stage_id
    if description is not None: values["description"] = description
    if date_deadline is not None: values["date_deadline"] = date_deadline
    if priority is not None: values["priority"] = priority

    res = ProjectsService.update_task(task_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 👥 HR & EMPLOYEES
# ==========================================

@mcp.tool()
def hr_list_employees(
    search_term: Optional[str] = None,
    department_id: Optional[int] = None,
    limit: int = 25
) -> str:
    """List employees with department, job title, email, and phone."""
    employees = HRService.list_employees(
        search_term=search_term,
        department_id=department_id,
        limit=limit
    )
    return json.dumps(employees, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_get_employee(employee_id: int) -> str:
    """Get full details of an employee."""
    employee = HRService.get_employee(employee_id)
    return json.dumps(employee, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_create_employee(
    name: str,
    job_title: Optional[str] = None,
    work_email: Optional[str] = None,
    work_phone: Optional[str] = None,
    mobile_phone: Optional[str] = None,
    department_id: Optional[int] = None,
    parent_id: Optional[int] = None
) -> str:
    """Create a new employee record."""
    res = HRService.create_employee(
        name=name,
        job_title=job_title,
        work_email=work_email,
        work_phone=work_phone,
        mobile_phone=mobile_phone,
        department_id=department_id,
        parent_id=parent_id
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_update_employee(
    employee_id: int,
    name: Optional[str] = None,
    job_title: Optional[str] = None,
    work_email: Optional[str] = None,
    work_phone: Optional[str] = None,
    mobile_phone: Optional[str] = None,
    department_id: Optional[int] = None,
    parent_id: Optional[int] = None
) -> str:
    """Update fields on an employee."""
    values = {}
    if name is not None: values["name"] = name
    if job_title is not None: values["job_title"] = job_title
    if work_email is not None: values["work_email"] = work_email
    if work_phone is not None: values["work_phone"] = work_phone
    if mobile_phone is not None: values["mobile_phone"] = mobile_phone
    if department_id is not None: values["department_id"] = department_id
    if parent_id is not None: values["parent_id"] = parent_id

    res = HRService.update_employee(employee_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_list_departments() -> str:
    """List company departments with employee counts."""
    departments = HRService.list_departments()
    return json.dumps(departments, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_get_department(department_id: int) -> str:
    """Get full details of a specific department."""
    department = HRService.get_department(department_id)
    return json.dumps(department, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_create_department(
    name: str,
    manager_id: Optional[int] = None,
    parent_id: Optional[int] = None
) -> str:
    """Create a new department."""
    res = HRService.create_department(name=name, manager_id=manager_id, parent_id=parent_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def hr_update_department(
    department_id: int,
    name: Optional[str] = None,
    manager_id: Optional[int] = None,
    parent_id: Optional[int] = None
) -> str:
    """Update fields on a department."""
    values = {}
    if name is not None: values["name"] = name
    if manager_id is not None: values["manager_id"] = manager_id
    if parent_id is not None: values["parent_id"] = parent_id

    res = HRService.update_department(department_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

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
def activities_update(
    activity_id: int,
    summary: Optional[str] = None,
    date_deadline: Optional[str] = None,
    note: Optional[str] = None,
    user_id: Optional[int] = None
) -> str:
    """Update fields on a scheduled activity."""
    values = {}
    if summary is not None: values["summary"] = summary
    if date_deadline is not None: values["date_deadline"] = date_deadline
    if note is not None: values["note"] = note
    if user_id is not None: values["user_id"] = user_id

    res = ActivitiesCalendarService.update_activity(activity_id, values)
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
def calendar_get_meeting(event_id: int) -> str:
    """Get full details of a specific calendar meeting."""
    event = ActivitiesCalendarService.get_calendar_event(event_id)
    return json.dumps(event, indent=2, ensure_ascii=False)

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

@mcp.tool()
def calendar_update_meeting(
    event_id: int,
    name: Optional[str] = None,
    start: Optional[str] = None,
    stop: Optional[str] = None,
    partner_ids: Optional[List[int]] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """Update fields on a calendar meeting/event."""
    values = {}
    if name is not None: values["name"] = name
    if start is not None: values["start"] = start
    if stop is not None: values["stop"] = stop
    if partner_ids is not None: values["partner_ids"] = partner_ids
    if description is not None: values["description"] = description
    if location is not None: values["location"] = location

    res = ActivitiesCalendarService.update_calendar_event(event_id, values)
    return json.dumps(res, indent=2, ensure_ascii=False)

# ==========================================
# 🎨 THEME & BRANDING
# ==========================================

@mcp.tool()
def theme_get_branding(company_id: int = 1) -> str:
    """Get current corporate branding colors (primary, secondary), font, and company info."""
    res = ThemeService.get_branding(company_id=company_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def theme_update_branding(
    company_id: int = 1,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    font: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """Update company branding colors, typography, or company name."""
    res = ThemeService.update_branding(
        company_id=company_id,
        primary_color=primary_color,
        secondary_color=secondary_color,
        font=font,
        name=name
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def theme_set_navbar_theme(
    navbar_bg_start: str = "#092D53",
    navbar_bg_end: str = "#1E3A8A",
    navbar_text_color: str = "#FFFFFF",
    primary_accent: str = "#0EA5E9"
) -> str:
    """Apply custom aesthetic theme to Odoo 20 backend navbar with gradients and accents."""
    res = ThemeService.set_navbar_theme(
        navbar_bg_start=navbar_bg_start,
        navbar_bg_end=navbar_bg_end,
        navbar_text_color=navbar_text_color,
        primary_accent=primary_accent
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def theme_remove_custom_css() -> str:
    """Restore default Odoo 20 theme and remove custom CSS."""
    res = ThemeService.remove_custom_css()
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def theme_list_fonts() -> str:
    """List available recommended fonts for Odoo theme."""
    res = ThemeService.list_available_fonts()
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
