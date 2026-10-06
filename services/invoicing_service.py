from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class InvoicingService:
    """Manages Invoices, Vendor Bills, and Payments."""

    @staticmethod
    def list_invoices(
        move_type: str = "out_invoice",
        state: Optional[str] = None,
        payment_state: Optional[str] = None,
        partner_id: Optional[int] = None,
        search_term: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List invoices or vendor bills.
        move_type options: 'out_invoice' (Customer Invoice), 'in_invoice' (Vendor Bill),
                           'out_refund' (Customer Credit Note), 'in_refund' (Vendor Credit Note).
        state options: 'draft', 'posted', 'cancel'.
        payment_state options: 'not_paid', 'in_payment', 'paid', 'reversed'.
        """
        client = get_odoo_client()
        domain: List[Any] = [("move_type", "=", move_type)]

        if state:
            domain.append(("state", "=", state))
        if payment_state:
            domain.append(("payment_state", "=", payment_state))
        if partner_id:
            domain.append(("partner_id", "=", partner_id))
        if search_term:
            domain.append("|")
            domain.append(("name", "ilike", search_term))
            domain.append(("partner_id.name", "ilike", search_term))

        fields = [
            "id", "name", "partner_id", "invoice_date", "invoice_date_due",
            "amount_untaxed", "amount_tax", "amount_total", "amount_residual",
            "state", "payment_state", "move_type", "ref"
        ]
        return client.search_read("account.move", domain=domain, fields=fields, limit=limit, order="id desc")

    @staticmethod
    def get_invoice(invoice_id: int) -> Dict[str, Any]:
        """Get complete details of an invoice including lines and totals."""
        client = get_odoo_client()
        fields = [
            "id", "name", "partner_id", "invoice_date", "invoice_date_due",
            "amount_untaxed", "amount_tax", "amount_total", "amount_residual",
            "state", "payment_state", "move_type", "ref", "narration",
            "invoice_line_ids", "currency_id"
        ]
        invoices = client.read("account.move", invoice_id, fields=fields)
        if not invoices:
            raise ValueError(f"Invoice with ID {invoice_id} not found.")

        invoice = invoices[0]
        line_ids = invoice.get("invoice_line_ids", [])
        if line_ids:
            line_fields = [
                "id", "product_id", "name", "quantity", "price_unit",
                "tax_ids", "price_subtotal", "price_total"
            ]
            invoice["lines"] = client.read("account.move.line", line_ids, fields=line_fields)
        else:
            invoice["lines"] = []

        return invoice

    @staticmethod
    def create_invoice(
        partner_id: int,
        invoice_lines: List[Dict[str, Any]],
        move_type: str = "out_invoice",
        invoice_date: Optional[str] = None,
        invoice_date_due: Optional[str] = None,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new draft invoice or vendor bill.
        invoice_lines format: [{'product_id': 1, 'quantity': 2, 'price_unit': 1250.0, 'name': 'Service description'}]
        """
        client = get_odoo_client()
        formatted_lines = []

        for line in invoice_lines:
            product_id = line.get("product_id")
            quantity = float(line.get("quantity", 1.0))
            price_unit = line.get("price_unit")
            name = line.get("name")

            line_vals: Dict[str, Any] = {
                "quantity": quantity,
            }
            if product_id:
                line_vals["product_id"] = product_id
            if price_unit is not None:
                line_vals["price_unit"] = float(price_unit)
            if name:
                line_vals["name"] = name

            formatted_lines.append((0, 0, line_vals))

        values: Dict[str, Any] = {
            "partner_id": partner_id,
            "move_type": move_type,
            "invoice_line_ids": formatted_lines,
        }
        if invoice_date:
            values["invoice_date"] = invoice_date
        if invoice_date_due:
            values["invoice_date_due"] = invoice_date_due
        if ref:
            values["ref"] = ref

        new_invoice_id = client.create("account.move", values)
        return {"id": new_invoice_id, "status": "created", "invoice": InvoicingService.get_invoice(new_invoice_id)}

    @staticmethod
    def update_invoice(invoice_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on an invoice (e.g. invoice_date, invoice_date_due, ref, narration, partner_id)."""
        client = get_odoo_client()
        client.write("account.move", invoice_id, values)
        return {"id": invoice_id, "status": "updated", "invoice": InvoicingService.get_invoice(invoice_id)}

    @staticmethod
    def add_invoice_line(
        invoice_id: int,
        name: str,
        price_unit: float,
        quantity: float = 1.0,
        product_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add a new line item to a draft invoice."""
        client = get_odoo_client()
        line_vals: Dict[str, Any] = {
            "move_id": invoice_id,
            "name": name,
            "quantity": quantity,
            "price_unit": price_unit,
        }
        if product_id:
            line_vals["product_id"] = product_id

        line_id = client.create("account.move.line", line_vals)
        return {"line_id": line_id, "invoice_id": invoice_id, "status": "line_added", "invoice": InvoicingService.get_invoice(invoice_id)}

    @staticmethod
    def post_invoice(invoice_id: int) -> Dict[str, Any]:
        """Validate and Post a draft invoice (makes it officially numbered and posted)."""
        client = get_odoo_client()
        client.execute_kw("account.move", "action_post", [[invoice_id]])
        return {"id": invoice_id, "status": "posted", "invoice": InvoicingService.get_invoice(invoice_id)}


    @staticmethod
    def register_payment(
        invoice_id: int,
        amount: Optional[float] = None,
        payment_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register payment for an invoice using Odoo's payment register wizard."""
        client = get_odoo_client()
        invoice = InvoicingService.get_invoice(invoice_id)
        if invoice["state"] != "posted":
            raise ValueError(f"Invoice must be in 'posted' state to register payment. Current state: {invoice['state']}")

        payment_amount = amount if amount is not None else invoice.get("amount_residual", 0.0)

        wizard_context = {
            "active_model": "account.move",
            "active_ids": [invoice_id],
        }
        wizard_vals: Dict[str, Any] = {
            "amount": payment_amount,
        }
        if payment_date:
            wizard_vals["payment_date"] = payment_date

        wizard_id = client.execute_kw(
            "account.payment.register", 
            "create", 
            [wizard_vals], 
            {"context": wizard_context}
        )
        client.execute_kw(
            "account.payment.register", 
            "action_create_payments", 
            [[wizard_id]], 
            {"context": wizard_context}
        )

        return {"id": invoice_id, "status": "payment_registered", "invoice": InvoicingService.get_invoice(invoice_id)}
