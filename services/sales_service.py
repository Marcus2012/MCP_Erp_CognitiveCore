from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class SalesService:
    """Manages Sales Orders, Quotations, and Order Lines."""

    @staticmethod
    def list_orders(
        search_term: Optional[str] = None,
        partner_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List sales orders and quotations.
        States: 'draft' (Quotation), 'sent' (Quotation Sent), 'sale' (Sales Order), 'cancel' (Cancelled).
        """
        client = get_odoo_client()
        domain: List[Any] = []

        if search_term:
            domain.append("|")
            domain.append(("name", "ilike", search_term))
            domain.append(("partner_id.name", "ilike", search_term))

        if partner_id:
            domain.append(("partner_id", "=", partner_id))

        if state:
            domain.append(("state", "=", state))

        fields = [
            "id", "name", "partner_id", "date_order", "amount_untaxed",
            "amount_tax", "amount_total", "state", "invoice_status",
            "user_id", "validity_date"
        ]
        return client.search_read("sale.order", domain=domain, fields=fields, limit=limit, order="id desc")

    @staticmethod
    def get_order(order_id: int) -> Dict[str, Any]:
        """Get full details of a sales order including lines."""
        client = get_odoo_client()
        fields = [
            "id", "name", "partner_id", "partner_invoice_id", "partner_shipping_id",
            "date_order", "validity_date", "payment_term_id", "amount_untaxed",
            "amount_tax", "amount_total", "state", "invoice_status",
            "order_line", "user_id", "note", "origin"
        ]
        orders = client.read("sale.order", order_id, fields=fields)
        if not orders:
            raise ValueError(f"Sale order with ID {order_id} not found.")

        order = orders[0]
        # Fetch line items details
        line_ids = order.get("order_line", [])
        if line_ids:
            line_fields = [
                "id", "product_id", "name", "product_uom_qty", "qty_delivered",
                "qty_invoiced", "price_unit", "tax_id", "price_subtotal", "price_total"
            ]
            order["lines"] = client.read("sale.order.line", line_ids, fields=line_fields)
        else:
            order["lines"] = []

        return order

    @staticmethod
    def create_quotation(
        partner_id: int,
        order_lines: List[Dict[str, Any]],
        payment_term_id: Optional[int] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new quotation.
        order_lines format: [{'product_id': 1, 'qty': 2, 'price_unit': 1250.0, 'description': 'Optional note'}]
        """
        client = get_odoo_client()
        formatted_lines = []

        for line in order_lines:
            product_id = line.get("product_id")
            qty = float(line.get("qty", 1.0))
            price_unit = line.get("price_unit")
            name = line.get("description")

            line_vals: Dict[str, Any] = {
                "product_id": product_id,
                "product_uom_qty": qty,
            }
            if price_unit is not None:
                line_vals["price_unit"] = float(price_unit)
            if name:
                line_vals["name"] = name

            formatted_lines.append((0, 0, line_vals))

        values: Dict[str, Any] = {
            "partner_id": partner_id,
            "order_line": formatted_lines,
        }
        if payment_term_id:
            values["payment_term_id"] = payment_term_id
        if note:
            values["note"] = note

        new_order_id = client.create("sale.order", values)
        return {"id": new_order_id, "status": "created", "order": SalesService.get_order(new_order_id)}

    @staticmethod
    def confirm_order(order_id: int) -> Dict[str, Any]:
        """Confirm quotation into a confirmed Sales Order."""
        client = get_odoo_client()
        client.execute_kw("sale.order", "action_confirm", [[order_id]])
        return {"id": order_id, "status": "confirmed", "order": SalesService.get_order(order_id)}

    @staticmethod
    def cancel_order(order_id: int) -> Dict[str, Any]:
        """Cancel a sales order or quotation."""
        client = get_odoo_client()
        client.execute_kw("sale.order", "action_cancel", [[order_id]])
        return {"id": order_id, "status": "cancelled", "order": SalesService.get_order(order_id)}
