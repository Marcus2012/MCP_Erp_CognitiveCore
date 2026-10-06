from typing import Any, Dict, List, Optional, Union
from odoo_client import get_odoo_client

class AnalyticsService:
    """Provides executive KPIs, analytics, and generic safe query interface."""

    @staticmethod
    def get_dashboard_summary() -> Dict[str, Any]:
        """
        Calculates an executive summary and KPIs across all core ERP modules:
        CRM, Sales, Invoicing, Inventory, Projects, and Contacts.
        """
        client = get_odoo_client()
        summary: Dict[str, Any] = {}

        # 1. CRM Pipeline
        try:
            leads = client.search_read(
                "crm.lead",
                domain=[("type", "=", "opportunity"), ("probability", "<", 100)],
                fields=["expected_revenue", "probability"]
            )
            total_pipeline_val = sum(l.get("expected_revenue", 0.0) or 0.0 for l in leads)
            summary["crm"] = {
                "active_opportunities_count": len(leads),
                "total_pipeline_expected_revenue": round(total_pipeline_val, 2)
            }
        except Exception as e:
            summary["crm"] = {"error": str(e)}

        # 2. Sales Orders
        try:
            confirmed_orders = client.search_read(
                "sale.order",
                domain=[("state", "in", ["sale", "done"])],
                fields=["amount_total"]
            )
            quotations = client.search_read(
                "sale.order",
                domain=[("state", "in", ["draft", "sent"])],
                fields=["amount_total"]
            )
            summary["sales"] = {
                "confirmed_orders_count": len(confirmed_orders),
                "confirmed_sales_total": round(sum(o.get("amount_total", 0.0) for o in confirmed_orders), 2),
                "open_quotations_count": len(quotations),
                "quotations_total": round(sum(q.get("amount_total", 0.0) for q in quotations), 2)
            }
        except Exception as e:
            summary["sales"] = {"error": str(e)}

        # 3. Invoicing & Receivables
        try:
            unpaid_invoices = client.search_read(
                "account.move",
                domain=[("move_type", "=", "out_invoice"), ("state", "=", "posted"), ("payment_state", "in", ["not_paid", "partial"])],
                fields=["amount_residual", "amount_total"]
            )
            summary["invoicing"] = {
                "open_customer_invoices_count": len(unpaid_invoices),
                "total_receivable_amount": round(sum(inv.get("amount_residual", 0.0) for inv in unpaid_invoices), 2)
            }
        except Exception as e:
            summary["invoicing"] = {"error": str(e)}

        # 4. Projects & Tasks
        try:
            projects_count = client.search_count("project.project", [("active", "=", True)])
            open_tasks = client.search_count("project.task", [("is_closed", "=", False)])
            summary["projects"] = {
                "active_projects_count": projects_count,
                "open_tasks_count": open_tasks
            }
        except Exception as e:
            summary["projects"] = {"error": str(e)}

        # 5. Contacts Catalog
        try:
            contacts_count = client.search_count("res.partner", [])
            products_count = client.search_count("product.product", [("sale_ok", "=", True)])
            summary["catalog"] = {
                "total_contacts": contacts_count,
                "total_active_products": products_count
            }
        except Exception as e:
            summary["catalog"] = {"error": str(e)}

        return summary

    @staticmethod
    def generic_query(
        model: str,
        method: str = "search_read",
        domain: Optional[List[Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
        order: Optional[str] = None
    ) -> Any:
        """
        Generic search/read fallback query for any Odoo model.
        Useful when AI needs to inspect custom or non-standard models.
        """
        # Block any dangerous methods
        if method in ["unlink", "delete", "drop", "write_raw"]:
            raise PermissionError("Operaciones de eliminación no están permitidas por seguridad.")

        client = get_odoo_client()
        domain = domain or []
        
        if method == "search_read":
            kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
            if fields:
                kwargs["fields"] = fields
            if order:
                kwargs["order"] = order
            return client.execute_kw(model, "search_read", [domain], kwargs)
        elif method == "fields_get":
            return client.fields_get(model, allfields=fields)
        elif method == "search_count":
            return client.search_count(model, domain)
        else:
            raise ValueError(f"Method '{method}' is not allowed in safe generic query.")

    @staticmethod
    def create_record(model: str, values: Dict[str, Any]) -> Dict[str, Any]:
        """Generic Create: Create a record in any Odoo model."""
        client = get_odoo_client()
        new_id = client.create(model, values)
        record = client.read(model, new_id)
        return {"id": new_id, "model": model, "status": "created", "record": record[0] if record else {}}

    @staticmethod
    def read_record(model: str, record_id: int, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generic Read: Read fields of any specific record by model and ID."""
        client = get_odoo_client()
        records = client.read(model, record_id, fields=fields)
        if not records:
            raise ValueError(f"Record {model} with ID {record_id} not found.")
        return records[0]

    @staticmethod
    def update_record(model: str, record_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Generic Update: Update fields of a record in any Odoo model."""
        client = get_odoo_client()
        client.write(model, record_id, values)
        record = client.read(model, record_id)
        return {"id": record_id, "model": model, "status": "updated", "record": record[0] if record else {}}

