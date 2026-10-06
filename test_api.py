import asyncio
import sys
import httpx
from api import app

# Ensure utf-8 output on windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

async def test_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("--- 1. Testing Root ---")
        r = await client.get("/")
        print("Status:", r.status_code, "Body:", r.json())
        assert r.status_code == 200

        print("\n--- 2. Testing Health Check ---")
        r = await client.get("/api/health")
        print("Status:", r.status_code, "Body:", r.json())
        assert r.status_code == 200
        assert r.json()["status"] == "connected"

        print("\n--- 3. Testing MCP Tools Inspector (/api/mcp/tools) ---")
        r = await client.get("/api/mcp/tools")
        data = r.json()
        print("Status:", r.status_code, "Total Tools Registered:", data["count"])
        assert data["count"] == 41

        print("\n--- 4. Testing Direct Tool Execution (/api/mcp/tools/erp_dashboard_kpis/execute) ---")
        r = await client.post("/api/mcp/tools/erp_dashboard_kpis/execute", json={"arguments": {}})
        print("Status:", r.status_code, "KPIs Output:", r.json()["result"])
        assert r.status_code == 200

        print("\n--- 5. Testing Chat Endpoint (/api/chat) ---")
        r = await client.post("/api/chat", json={
            "messages": [
                {"role": "user", "content": "Muéstrame las oportunidades del CRM y el resumen ejecutivo"}
            ]
        })
        print("Status:", r.status_code)
        print("Chat Assistant Response Excerpt:\n", r.json()["content"][:400] + "...")
        assert r.status_code == 200

        print("\n✅ ALL FASTAPI ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_api())
