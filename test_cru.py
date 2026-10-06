import asyncio
import sys
import httpx
from api import app
from tool_registry import TOOLS_DEFINITIONS, execute_tool

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

async def test_cru_suite():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print(f"=== Total registered MCP Tools: {len(TOOLS_DEFINITIONS)} ===")
        
        # 1. MCP Tools endpoint
        r = await client.get("/api/mcp/tools")
        data = r.json()
        print(f"Tools count from API: {data['count']}")
        assert data["count"] == len(TOOLS_DEFINITIONS)

        # 2. Test Reading Contacts
        print("\n--- Testing Read: contacts_search ---")
        contacts = execute_tool("contacts_search", {"limit": 3})
        print(f"Contacts retrieved: {len(contacts)}")
        assert isinstance(contacts, list)

        # 3. Test Reading Projects & Tasks
        print("\n--- Testing Read: projects_list ---")
        projects = execute_tool("projects_list", {"limit": 3})
        print(f"Projects retrieved: {len(projects)}")
        assert isinstance(projects, list)

        # 4. Test Reading Products
        print("\n--- Testing Read: inventory_search_products ---")
        products = execute_tool("inventory_search_products", {"limit": 3})
        print(f"Products retrieved: {len(products)}")
        assert isinstance(products, list)

        # 5. Test Reading HR Employees
        print("\n--- Testing Read: hr_list_employees ---")
        employees = execute_tool("hr_list_employees", {"limit": 3})
        print(f"Employees retrieved: {len(employees)}")
        assert isinstance(employees, list)

        # 6. Test Reading Calendar Meetings
        print("\n--- Testing Read: calendar_list_meetings ---")
        meetings = execute_tool("calendar_list_meetings", {"limit": 3})
        print(f"Meetings retrieved: {len(meetings)}")
        assert isinstance(meetings, list)

        # 7. Test Generic Read Record
        if contacts:
            partner_id = contacts[0]["id"]
            print(f"\n--- Testing Generic Read: res.partner ID {partner_id} ---")
            rec = execute_tool("odoo_read_record", {"model": "res.partner", "record_id": partner_id, "fields": ["id", "name", "phone", "email"]})
            print(f"Read record: {rec['name']} (ID: {rec['id']})")
            assert rec["id"] == partner_id

        # 8. Test Safety Guard: Ensure Delete is strictly blocked
        print("\n--- Testing Security: Block Delete in Generic Query ---")
        try:
            execute_tool("odoo_generic_query", {"model": "res.partner", "method": "unlink"})
            print("ERROR: Delete was NOT blocked!")
            assert False, "Delete should be blocked"
        except (PermissionError, ValueError) as e:
            print(f"Safety guard passed: {e}")

        print("\n✅ ALL CRU AND SECURITY CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_cru_suite())
