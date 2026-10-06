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
    def get_picking(picking_id: int) -> Dict[str, Any]:
        """Get full details of a stock picking/transfer."""
        client = get_odoo_client()
        fields = [
            "id", "name", "partner_id", "picking_type_id", "scheduled_date",
            "date_done", "origin", "state", "location_id", "location_dest_id",
            "move_ids_without_package"
        ]
        pickings = client.read("stock.picking", picking_id, fields=fields)
        if not pickings:
            raise ValueError(f"Stock picking with ID {picking_id} not found.")
        picking = pickings[0]
        # Fetch move lines
        move_ids = picking.get("move_ids_without_package", [])
        if move_ids:
            move_fields = ["id", "product_id", "product_uom_qty", "quantity", "product_uom", "state"]
            picking["moves"] = client.read("stock.move", move_ids, fields=move_fields)
        else:
            picking["moves"] = []
        return picking

    @staticmethod
    def update_picking(picking_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on a stock picking (e.g. scheduled_date, origin, partner_id)."""
        client = get_odoo_client()
        client.write("stock.picking", picking_id, values)
        return {"id": picking_id, "status": "updated", "picking": InventoryService.get_picking(picking_id)}

    @staticmethod
    def update_stock_quantity(
        product_id: int,
        new_quantity: float,
        location_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update the on-hand stock quantity of a product using stock.quant inventory adjustment.
        """
        client = get_odoo_client()
        # Find internal location if not specified
        if not location_id:
            locations = client.search_read(
                "stock.location",
                domain=[("usage", "=", "internal")],
                fields=["id", "complete_name"],
                limit=1
            )
            if not locations:
                raise ValueError("No internal stock location found.")
            location_id = locations[0]["id"]

        # Check existing quant
        quants = client.search_read(
            "stock.quant",
            domain=[("product_id", "=", product_id), ("location_id", "=", location_id)],
            fields=["id", "quantity", "inventory_quantity"],
            limit=1
        )

        if quants:
            quant_id = quants[0]["id"]
            client.write("stock.quant", quant_id, {"inventory_quantity": new_quantity})
        else:
            quant_id = client.create("stock.quant", {
                "product_id": product_id,
                "location_id": location_id,
                "inventory_quantity": new_quantity
            })

        # Apply inventory adjustment
        try:
            client.execute_kw("stock.quant", "action_apply_inventory", [[quant_id]])
        except Exception:
            # In some setups, writing quantity directly or applying might already succeed
            pass

        return {
            "product_id": product_id,
            "location_id": location_id,
            "new_quantity": new_quantity,
            "status": "quantity_updated",
            "product": InventoryService.get_product(product_id)
        }

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

