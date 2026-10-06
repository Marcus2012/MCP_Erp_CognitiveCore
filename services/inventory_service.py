from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class InventoryService:
    """Manages Products, Inventory, Stock Quants, and Transfers/Deliveries."""

    @staticmethod
    def search_products(
        query: Optional[str] = None,
        product_type: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Search products and services in the catalog.
        product_type options: 'consu' (Consumable), 'service' (Service), 'product' / 'goods' (Storable).
        """
        client = get_odoo_client()
        domain: List[Any] = [("sale_ok", "=", True)]

        if query:
            domain.append("|")
            domain.append("|")
            domain.append(("name", "ilike", query))
            domain.append(("default_code", "ilike", query))
            domain.append(("barcode", "ilike", query))

        if product_type:
            domain.append(("type", "=", product_type))

        fields = [
            "id", "name", "default_code", "barcode", "list_price",
            "standard_price", "qty_available", "virtual_available",
            "type", "categ_id", "uom_id"
        ]
        return client.search_read("product.product", domain=domain, fields=fields, limit=limit, order="name asc")

    @staticmethod
    def get_product(product_id: int) -> Dict[str, Any]:
        """Get full details of a specific product."""
        client = get_odoo_client()
        fields = [
            "id", "name", "default_code", "barcode", "list_price",
            "standard_price", "qty_available", "virtual_available",
            "type", "categ_id", "uom_id", "description_sale", "taxes_id"
        ]
        products = client.read("product.product", product_id, fields=fields)
        if not products:
            raise ValueError(f"Product with ID {product_id} not found.")
        return products[0]

    @staticmethod
    def create_product(
        name: str,
        list_price: float,
        default_code: Optional[str] = None,
        standard_price: Optional[float] = None,
        product_type: str = "service",
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new product or service.
        product_type: 'service', 'consu' (Consumable), or 'product' (Storable).
        """
        client = get_odoo_client()
        values: Dict[str, Any] = {
            "name": name,
            "list_price": list_price,
            "type": product_type,
            "sale_ok": True,
            "purchase_ok": True,
        }
        if default_code:
            values["default_code"] = default_code
        if standard_price is not None:
            values["standard_price"] = standard_price
        if description:
            values["description_sale"] = description

        new_product_id = client.create("product.product", values)
        return {"id": new_product_id, "status": "created", "product": InventoryService.get_product(new_product_id)}

    @staticmethod
    def update_product(product_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update product fields (e.g. list_price, standard_price, description)."""
        client = get_odoo_client()
        client.write("product.product", product_id, values)
        return {"id": product_id, "status": "updated", "product": InventoryService.get_product(product_id)}

    @staticmethod
    def list_pickings(
        picking_type: Optional[str] = None,
        state: Optional[str] = None,
        partner_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List stock transfers (Delivery Orders, Receipts, Internal Transfers).
        state options: 'draft', 'waiting', 'confirmed', 'assigned' (Ready), 'done', 'cancel'.
        """
        client = get_odoo_client()
        domain: List[Any] = []

        if picking_type:
            domain.append(("picking_type_id.code", "=", picking_type))
        if state:
            domain.append(("state", "=", state))
        if partner_id:
            domain.append(("partner_id", "=", partner_id))

        fields = [
            "id", "name", "partner_id", "picking_type_id", "scheduled_date",
            "date_done", "origin", "state", "location_id", "location_dest_id"
        ]
        return client.search_read("stock.picking", domain=domain, fields=fields, limit=limit, order="id desc")
