from typing import Any, Dict, List, Optional
from odoo_client import get_odoo_client

class ActivitiesCalendarService:
    """Manages ERP Next Actions, Activities (mail.activity), and Calendar Events (calendar.event)."""

    @staticmethod
    def list_activities(
        res_model: Optional[str] = None,
        res_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """List scheduled activities / next actions."""
        client = get_odoo_client()
        domain: List[Any] = []

        if res_model:
            domain.append(("res_model", "=", res_model))
        if res_id:
            domain.append(("res_id", "=", res_id))
        if user_id:
            domain.append(("user_id", "=", user_id))

        fields = [
            "id", "res_model", "res_id", "res_name", "activity_type_id",
            "summary", "note", "date_deadline", "user_id", "state"
        ]
        return client.search_read("mail.activity", domain=domain, fields=fields, limit=limit, order="date_deadline asc")

    @staticmethod
    def create_activity(
        res_model: str,
        res_id: int,
        summary: str,
        date_deadline: str,
        note: Optional[str] = None,
        activity_type_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Schedule an activity on any ERP record (e.g. Lead, Customer, Order).
        date_deadline format: 'YYYY-MM-DD'
        """
        client = get_odoo_client()
        
        # Resolve default activity type if not provided (e.g., Call or Todo)
        if not activity_type_id:
            types = client.search_read("mail.activity.type", domain=[], fields=["id", "name"], limit=1)
            activity_type_id = types[0]["id"] if types else 1

        values: Dict[str, Any] = {
            "res_model": res_model,
            "res_id": res_id,
            "summary": summary,
            "date_deadline": date_deadline,
            "activity_type_id": activity_type_id,
        }
        if note:
            values["note"] = note
        if user_id:
            values["user_id"] = user_id

        new_id = client.create("mail.activity", values)
        return {"id": new_id, "status": "created", "summary": summary, "date_deadline": date_deadline}

    @staticmethod
    def mark_activity_done(activity_id: int, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Mark an activity as completed with optional feedback."""
        client = get_odoo_client()
        client.execute_kw(
            "mail.activity",
            "action_feedback",
            [[activity_id]],
            {"feedback": feedback}
        )
        return {"id": activity_id, "status": "completed"}

    @staticmethod
    def update_activity(activity_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on a scheduled activity (e.g. summary, date_deadline, note, user_id)."""
        client = get_odoo_client()
        client.write("mail.activity", activity_id, values)
        activities = client.read("mail.activity", activity_id, fields=["id", "res_model", "res_id", "summary", "note", "date_deadline", "user_id", "state"])
        return {"id": activity_id, "status": "updated", "activity": activities[0] if activities else {}}

    @staticmethod
    def list_calendar_events(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List calendar events and meetings."""
        client = get_odoo_client()
        domain: List[Any] = []

        if start_date:
            domain.append(("start", ">=", start_date))
        if end_date:
            domain.append(("stop", "<=", end_date))

        fields = ["id", "name", "start", "stop", "partner_ids", "user_id", "location", "description", "allday"]
        return client.search_read("calendar.event", domain=domain, fields=fields, limit=limit, order="start asc")

    @staticmethod
    def get_calendar_event(event_id: int) -> Dict[str, Any]:
        """Get details of a specific calendar meeting or event."""
        client = get_odoo_client()
        fields = ["id", "name", "start", "stop", "partner_ids", "user_id", "location", "description", "allday", "duration", "alarm_ids"]
        events = client.read("calendar.event", event_id, fields=fields)
        if not events:
            raise ValueError(f"Calendar event with ID {event_id} not found.")
        return events[0]

    @staticmethod
    def create_calendar_event(
        name: str,
        start: str,
        stop: str,
        partner_ids: Optional[List[int]] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        allday: bool = False
    ) -> Dict[str, Any]:
        """
        Schedule a new calendar meeting/event.
        start / stop format: 'YYYY-MM-DD HH:MM:SS'
        """
        client = get_odoo_client()
        values: Dict[str, Any] = {
            "name": name,
            "start": start,
            "stop": stop,
            "allday": allday,
        }
        if partner_ids:
            values["partner_ids"] = [(6, 0, partner_ids)]
        if description:
            values["description"] = description
        if location:
            values["location"] = location

        new_id = client.create("calendar.event", values)
        return {"id": new_id, "status": "created", "event": ActivitiesCalendarService.get_calendar_event(new_id)}

    @staticmethod
    def update_calendar_event(event_id: int, values: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on a calendar meeting/event (e.g. name, start, stop, location, description, partner_ids)."""
        client = get_odoo_client()
        formatted_vals = dict(values)
        if "partner_ids" in formatted_vals and isinstance(formatted_vals["partner_ids"], list):
            formatted_vals["partner_ids"] = [(6, 0, formatted_vals["partner_ids"])]

        client.write("calendar.event", event_id, formatted_vals)
        return {"id": event_id, "status": "updated", "event": ActivitiesCalendarService.get_calendar_event(event_id)}

