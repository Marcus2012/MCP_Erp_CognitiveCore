from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class ContactsService:
    """Manages Customers, Vendors, and Contacts (res.partner)."""

    @staticmethod
    def search_contacts(
        query: Optional[str] = None,
        is_company: Optional[bool] = None,
        is_customer: Optional[bool] = None,
        is_supplier: Optional[bool] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Search contacts by name, email, phone, or VAT / Tax ID (RUC / DNI)."""
        client = get_odoo_client()
        domain: List[Any] = []

        if query:
            domain.append("|")
            domain.append("|")
            domain.append("|")
            domain.append(("name", "ilike", query))
            domain.append(("email", "ilike", query))
            domain.append(("phone", "ilike", query))
            domain.append(("vat", "ilike", query))

        if is_company is not None:
            domain.append(("is_company", "=", is_company))

        if is_customer is True:
            domain.append(("customer_rank", ">", 0))

        if is_supplier is True:
            domain.append(("supplier_rank", ">", 0))

        fields = [
            "id", "name", "email", "phone", "vat",
            "is_company", "street", "city", "country_id", "commercial_company_name"
        ]
        return client.search_read("res.partner", domain=domain, fields=fields, limit=limit, order="name asc")

    @staticmethod
    def get_contact(partner_id: int) -> Dict[str, Any]:
        """Get complete contact card with commercial details."""
        client = get_odoo_client()
        fields = [
            "id", "name", "email", "phone", "vat", "is_company",
            "street", "street2", "city", "state_id", "country_id",
            "customer_rank", "supplier_rank", "comment", "user_id",
            "total_invoiced", "credit", "debit"
        ]
        contacts = client.read("res.partner", partner_id, fields=fields)
        if not contacts:
            raise ValueError(f"Contact with ID {partner_id} not found.")
        return contacts[0]

    @staticmethod
    def create_contact(
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
    ) -> Dict[str, Any]:
        """Create a new contact, customer, or vendor."""
        client = get_odoo_client()
        values: Dict[str, Any] = {
            "name": name,
            "is_company": is_company,
        }
        if email:
            values["email"] = email
        if phone:
            values["phone"] = phone
        if vat:
            values["vat"] = vat
        if street:
            values["street"] = street
        if city:
            values["city"] = city
        if is_customer:
            values["customer_rank"] = 1
        if is_supplier:
            values["supplier_rank"] = 1
        if comment:
            values["comment"] = comment

        new_id = client.create("res.partner", values)
        return {"id": new_id, "status": "created", "contact": ContactsService.get_contact(new_id)}

    @staticmethod
    def update_contact(partner_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on a contact/partner."""
        client = get_odoo_client()
        client.write("res.partner", partner_id, values)
        return {"id": partner_id, "status": "updated", "contact": ContactsService.get_contact(partner_id)}
