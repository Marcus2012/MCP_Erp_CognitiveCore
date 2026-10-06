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
    def create_employee(
        name: str,
        job_title: Optional[str] = None,
        work_email: Optional[str] = None,
        work_phone: Optional[str] = None,
        mobile_phone: Optional[str] = None,
        department_id: Optional[int] = None,
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new employee record."""
        client = get_odoo_client()
        values: Dict[str, Any] = {"name": name}
        if job_title:
            values["job_title"] = job_title
        if work_email:
            values["work_email"] = work_email
        if work_phone:
            values["work_phone"] = work_phone
        if mobile_phone:
            values["mobile_phone"] = mobile_phone
        if department_id:
            values["department_id"] = department_id
        if parent_id:
            values["parent_id"] = parent_id

        new_id = client.create("hr.employee", values)
        return {"id": new_id, "status": "created", "employee": HRService.get_employee(new_id)}

    @staticmethod
    def update_employee(employee_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on an employee (e.g. job_title, department_id, work_email, phone)."""
        client = get_odoo_client()
        client.write("hr.employee", employee_id, values)
        return {"id": employee_id, "status": "updated", "employee": HRService.get_employee(employee_id)}

    @staticmethod
    def list_departments() -> List[Dict[str, Any]]:
        """List company departments."""
        client = get_odoo_client()
        return client.search_read("hr.department", domain=[], fields=["id", "name", "manager_id", "total_employee", "parent_id"])

    @staticmethod
    def get_department(department_id: int) -> Dict[str, Any]:
        """Get details of a specific department."""
        client = get_odoo_client()
        departments = client.read("hr.department", department_id, fields=["id", "name", "manager_id", "total_employee", "parent_id", "company_id"])
        if not departments:
            raise ValueError(f"Department with ID {department_id} not found.")
        return departments[0]

    @staticmethod
    def create_department(
        name: str,
        manager_id: Optional[int] = None,
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new department."""
        client = get_odoo_client()
        values: Dict[str, Any] = {"name": name}
        if manager_id:
            values["manager_id"] = manager_id
        if parent_id:
            values["parent_id"] = parent_id

        new_id = client.create("hr.department", values)
        return {"id": new_id, "status": "created", "department": HRService.get_department(new_id)}

    @staticmethod
    def update_department(department_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on a department."""
        client = get_odoo_client()
        client.write("hr.department", department_id, values)
        return {"id": department_id, "status": "updated", "department": HRService.get_department(department_id)}

