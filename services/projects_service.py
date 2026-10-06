from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class ProjectsService:
    """Manages Projects and Tasks (project.project and project.task)."""

    @staticmethod
    def list_projects(search_term: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List active projects."""
        client = get_odoo_client()
        domain: List[Any] = []
        if search_term:
            domain.append(("name", "ilike", search_term))

        fields = ["id", "name", "partner_id", "user_id", "task_count", "date_start", "date", "description"]
        return client.search_read("project.project", domain=domain, fields=fields, limit=limit, order="name asc")

    @staticmethod
    def get_project(project_id: int) -> Dict[str, Any]:
        """Get full details of a specific project."""
        client = get_odoo_client()
        fields = ["id", "name", "partner_id", "user_id", "task_count", "date_start", "date", "description", "privacy_visibility", "tag_ids"]
        projects = client.read("project.project", project_id, fields=fields)
        if not projects:
            raise ValueError(f"Project with ID {project_id} not found.")
        return projects[0]

    @staticmethod
    def create_project(
        name: str,
        partner_id: Optional[int] = None,
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        date_start: Optional[str] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new project."""
        client = get_odoo_client()
        values: Dict[str, Any] = {"name": name}
        if partner_id:
            values["partner_id"] = partner_id
        if user_id:
            values["user_id"] = user_id
        if description:
            values["description"] = description
        if date_start:
            values["date_start"] = date_start
        if date:
            values["date"] = date

        new_id = client.create("project.project", values)
        return {"id": new_id, "status": "created", "project": ProjectsService.get_project(new_id)}

    @staticmethod
    def update_project(project_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on a project (name, partner_id, user_id, description, dates)."""
        client = get_odoo_client()
        client.write("project.project", project_id, values)
        return {"id": project_id, "status": "updated", "project": ProjectsService.get_project(project_id)}


    @staticmethod
    def list_tasks(
        project_id: Optional[int] = None,
        search_term: Optional[str] = None,
        user_id: Optional[int] = None,
        is_closed: Optional[bool] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filters."""
        client = get_odoo_client()
        domain: List[Any] = []

        if project_id:
            domain.append(("project_id", "=", project_id))
        if search_term:
            domain.append(("name", "ilike", search_term))
        if user_id:
            domain.append(("user_ids", "in", [user_id]))
        if is_closed is not None:
            domain.append(("is_closed", "=", is_closed))

        fields = [
            "id", "name", "project_id", "user_ids", "stage_id",
            "date_deadline", "priority", "partner_id", "tag_ids"
        ]
        return client.search_read("project.task", domain=domain, fields=fields, limit=limit, order="priority desc, id desc")

    @staticmethod
    def get_task(task_id: int) -> Dict[str, Any]:
        """Get full task details including description."""
        client = get_odoo_client()
        fields = [
            "id", "name", "project_id", "user_ids", "stage_id",
            "date_deadline", "priority", "partner_id", "tag_ids",
            "description", "is_closed"
        ]
        tasks = client.read("project.task", task_id, fields=fields)
        if not tasks:
            raise ValueError(f"Task with ID {task_id} not found.")
        return tasks[0]

    @staticmethod
    def create_task(
        name: str,
        project_id: Optional[int] = None,
        user_ids: Optional[List[int]] = None,
        description: Optional[str] = None,
        date_deadline: Optional[str] = None,
        priority: str = "0"
    ) -> Dict[str, Any]:
        """Create a new project task or todo."""
        client = get_odoo_client()
        values: Dict[str, Any] = {
            "name": name,
            "priority": priority,
        }
        if project_id:
            values["project_id"] = project_id
        if user_ids:
            values["user_ids"] = [(6, 0, user_ids)]
        if description:
            values["description"] = description
        if date_deadline:
            values["date_deadline"] = date_deadline

        new_id = client.create("project.task", values)
        return {"id": new_id, "status": "created", "task": ProjectsService.get_task(new_id)}

    @staticmethod
    def update_task(task_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update task properties or stage."""
        client = get_odoo_client()
        client.write("project.task", task_id, values)
        return {"id": task_id, "status": "updated", "task": ProjectsService.get_task(task_id)}
