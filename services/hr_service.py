from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class HRService:
    """Manages Human Resources, Employees, and Departments."""

    @staticmethod
    def list_employees(
        search_term: Optional[str] = None,
        department_id: Optional[int] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """List employees in the organization."""
        client = get_odoo_client()
        domain: List[Any] = []

        if search_term:
            domain.append("|")
            domain.append(("name", "ilike", search_term))
            domain.append(("work_email", "ilike", search_term))

        if department_id:
            domain.append(("department_id", "=", department_id))

        fields = ["id", "name", "job_title", "department_id", "work_email", "work_phone", "parent_id"]
        return client.search_read("hr.employee", domain=domain, fields=fields, limit=limit, order="name asc")

    @staticmethod
    def get_employee(employee_id: int) -> Dict[str, Any]:
        """Get full details of an employee."""
        client = get_odoo_client()
        fields = [
            "id", "name", "job_title", "department_id", "work_email",
            "work_phone", "mobile_phone", "parent_id", "coach_id"
        ]
        employees = client.read("hr.employee", employee_id, fields=fields)
        if not employees:
            raise ValueError(f"Employee with ID {employee_id} not found.")
        return employees[0]

    @staticmethod
    def list_departments() -> List[Dict[str, Any]]:
        """List company departments."""
        client = get_odoo_client()
        return client.search_read("hr.department", domain=[], fields=["id", "name", "manager_id", "total_employee"])
