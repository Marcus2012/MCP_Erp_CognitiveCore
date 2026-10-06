import asyncio
import server

async def main():
    tools = await server.mcp.list_tools()
    print(f"\n==========================================")
    print(f"Cognitive ERP Odoo 20 MCP Server")
    print(f"Total Tools Registered: {len(tools)}")
    print(f"==========================================")
    for t in tools:
        desc = t.description.strip().split("\n")[0] if t.description else "No description"
        print(f" • {t.name:<30} -> {desc}")

    print("\n--- Testing tool call: erp_dashboard_kpis ---")
    kpis = server.erp_dashboard_kpis()
    print("KPIs Result:")
    print(kpis)

    print("\n--- Testing tool call: crm_list_leads ---")
    leads = server.crm_list_leads(limit=3)
    print("CRM Leads Result:")
    print(leads)

    print("\n--- Testing tool call: inventory_search_products ---")
    products = server.inventory_search_products(limit=3)
    print("Products Result:")
    print(products)

if __name__ == "__main__":
    asyncio.run(main())
