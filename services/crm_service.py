from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class CRMService:
    """Manages CRM Leads, Opportunities, and Sales Pipelines."""

    @staticmethod
    def list_stages() -> List[Dict[str, Any]]:
        """List all pipeline stages in Odoo CRM."""
        client = get_odoo_client()
        return client.search_read(
            "crm.stage",
            domain=[],
            fields=["id", "name", "sequence", "is_won", "fold"],
            order="sequence asc"
        )

    @staticmethod
    def list_leads(
        search_term: Optional[str] = None,
        stage_name: Optional[str] = None,
        is_won: Optional[bool] = None,
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List CRM leads and opportunities."""
        client = get_odoo_client()
        domain: List[Any] = []

        if search_term:
            domain.append("|")
            domain.append(("name", "ilike", search_term))
            domain.append(("partner_name", "ilike", search_term))

        if stage_name:
            domain.append(("stage_id.name", "ilike", stage_name))

        if is_won is True:
            domain.append(("probability", "=", 100))
        elif is_won is False:
            domain.append(("probability", "<", 100))

        if user_id:
            domain.append(("user_id", "=", user_id))

        fields = [
            "id", "name", "partner_id", "partner_name", "email_from", 
            "phone", "expected_revenue", "probability", "stage_id", 
            "user_id", "create_date", "type"
        ]
        return client.search_read("crm.lead", domain=domain, fields=fields, limit=limit, order="id desc")

    @staticmethod
    def get_lead(lead_id: int) -> Dict[str, Any]:
        """Get full details of a specific CRM opportunity/lead."""
        client = get_odoo_client()
        fields = [
            "id", "name", "partner_id", "partner_name", "email_from", "phone",
            "expected_revenue", "probability", "stage_id", "user_id",
            "description", "date_deadline", "priority", "tag_ids",
            "activity_ids", "create_date", "write_date", "type"
        ]
        leads = client.read("crm.lead", lead_id, fields=fields)
        if not leads:
            raise ValueError(f"CRM Lead with ID {lead_id} not found.")
        return leads[0]

    @staticmethod
    def create_lead(
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
    ) -> Dict[str, Any]:
        """Create a new CRM lead or opportunity."""
        client = get_odoo_client()
        values: Dict[str, Any] = {
            "name": name,
            "expected_revenue": expected_revenue,
            "type": "opportunity" if is_opportunity else "lead",
            "priority": priority,
        }
        if partner_id:
            values["partner_id"] = partner_id
        if partner_name:
            values["partner_name"] = partner_name
        if email_from:
            values["email_from"] = email_from
        if phone:
            values["phone"] = phone
        if probability is not None:
            values["probability"] = probability
        if description:
            values["description"] = description

        new_id = client.create("crm.lead", values)
        return {"id": new_id, "status": "created", "lead": CRMService.get_lead(new_id)}

    @staticmethod
    def update_lead(lead_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on a CRM lead/opportunity."""
        client = get_odoo_client()
        client.write("crm.lead", lead_id, values)
        return {"id": lead_id, "status": "updated", "lead": CRMService.get_lead(lead_id)}

    @staticmethod
    def mark_lead_won(lead_id: int) -> Dict[str, Any]:
        """Mark a CRM opportunity as Won."""
        client = get_odoo_client()
        client.execute_kw("crm.lead", "action_set_won", [[lead_id]])
        return {"id": lead_id, "status": "won", "lead": CRMService.get_lead(lead_id)}

    @staticmethod
    def mark_lead_lost(lead_id: int, lost_reason_id: Optional[int] = None) -> Dict[str, Any]:
        """Mark a CRM opportunity as Lost."""
        client = get_odoo_client()
        if lost_reason_id:
            client.write("crm.lead", lead_id, {"lost_reason_id": lost_reason_id, "active": False})
        else:
            client.execute_kw("crm.lead", "action_set_lost", [[lead_id]])
        return {"id": lead_id, "status": "lost", "lead": CRMService.get_lead(lead_id)}
