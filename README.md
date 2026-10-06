# 🧠 Cognitive ERP MCP & API Gateway (Odoo 20 Community)

Backend unificado con **FastAPI** y servidor **Model Context Protocol (MCP)** de alto rendimiento para interactuar con **Odoo 20.0 Community** desde:
- 🌐 **Frontend Web / React / Next.js**: Conexión vía REST y Streaming SSE (`MCP_Erp_CognitiveCoreFrontend`).
- 🤖 **Clientes Desktop / IDEs**: Conexión MCP directa por `stdio` (Cursor, Claude Desktop, Antigravity).

---

## 🚀 Capacidades y Servicios Disponibles (41 Herramientas MCP)

| Módulo | Herramientas Principales |
| :--- | :--- |
| **📊 Ejecutivo & Analítica** | `erp_dashboard_kpis`, `odoo_generic_query` |
| **💼 CRM & Pipeline** | `crm_list_leads`, `crm_get_lead`, `crm_create_lead`, `crm_update_lead`, `crm_mark_won`, `crm_mark_lost`, `crm_list_stages` |
| **💰 Ventas & Cotizaciones** | `sales_list_orders`, `sales_get_order`, `sales_create_quotation`, `sales_confirm_order`, `sales_cancel_order` |
| **🧾 Facturación & Cobranzas** | `invoices_list`, `invoices_get`, `invoices_create`, `invoices_post`, `invoices_register_payment` |
| **📦 Catálogo & Inventario** | `inventory_search_products`, `inventory_get_product`, `inventory_create_product`, `inventory_update_product`, `inventory_list_pickings` |
| **👥 Contactos & Clientes** | `contacts_search`, `contacts_get`, `contacts_create`, `contacts_update` |
| **📋 Proyectos & Tareas** | `projects_list`, `projects_list_tasks`, `projects_get_task`, `projects_create_task`, `projects_update_task` |
| **👔 Recursos Humanos** | `hr_list_employees`, `hr_get_employee`, `hr_list_departments` |
| **⏰ Agenda & Actividades** | `activities_list`, `activities_create`, `activities_mark_done`, `calendar_list_meetings`, `calendar_create_meeting` |

---

## ⚙️ Configuración del Entorno (.env)

Crea o edita el archivo `.env` en la raíz del proyecto:

```env
# Conexión Odoo 20
ODOO_URL=https://erp.cognitivecore.pe/
ODOO_DB=erp_cognitivecore
ODOO_EMAIL=datadriven111@gmail.com
ODOO_API_KEY=491e1eec3cfedd93a8561f2b9cd822b870bbda89
ODOO_PASSWORD=Temp11$2026

# Opcional: Para agentes LLM autónomos (OpenAI / GPT-4o)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

---

## 📦 Instalación y Ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar el Servidor FastAPI (para Web Frontend y API)
uvicorn api:app --reload --port 8000
```

Documentación interactiva Swagger disponible en: `http://localhost:8000/docs`

---

## 🌐 Endpoints Principales de FastAPI

- `GET /api/health` -> Estado de conexión con Odoo y versión.
- `GET /api/dashboard` -> Resumen ejecutivo y KPIs del ERP.
- `GET /api/mcp/tools` -> Catálogo completo de las 41 herramientas MCP con sus esquemas JSON (usado por `McpInspector.tsx`).
- `POST /api/mcp/tools/{tool_name}/execute` -> Ejecución directa de cualquier herramienta MCP.
- `POST /api/chat` -> Chat con el asistente inteligente Odoo (respuesta completa).
- `POST /api/chat/stream` -> Chat con streaming Server-Sent Events (SSE) palabra por palabra.

---

## 🔌 Conectar como Servidor MCP de Escritorio (Claude Desktop / Cursor)

Añade a tu configuración MCP:
```json
{
  "mcpServers": {
    "cognitive-erp": {
      "command": "python",
      "args": [
        "c:\\Users\\Kevin\\Documents\\Cognitive Core\\MCP_Erp_CognitiveCore\\server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

---

## 🧪 Pruebas en Terminal

```bash
# Probar endpoints de FastAPI
python test_api.py

# Probar servidor FastMCP
python test_server.py

# Probar Copilot en consola interactiva
python demo_cli.py
```
