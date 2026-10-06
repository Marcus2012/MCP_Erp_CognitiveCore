"""
Interactive CLI AI Chat for Cognitive ERP (Odoo 20 Community)
Simulates an Enterprise-style AI ERP Copilot connected directly to your ERP MCP tools.
"""

import os
import json
from config import Config
import server

def print_banner():
    print("=" * 65)
    print(" 🤖 COGNITIVE ERP AI COPILOT (Odoo 20 Community)")
    print(f" Connected to: {Config.ODOO_URL} | DB: {Config.ODOO_DB}")
    print("=" * 65)
    print("Comandos disponibles / Ejemplos:")
    print(" 1. 'resumen' o 'kpis'   -> Muestra el resumen ejecutivo del ERP")
    print(" 2. 'crm' o 'leads'      -> Lista oportunidades activas")
    print(" 3. 'productos'          -> Muestra el catálogo de productos")
    print(" 4. 'contactos'          -> Lista clientes y contactos")
    print(" 5. 'pedidos'            -> Lista órdenes de venta / cotizaciones")
    print(" 6. 'facturas'           -> Lista facturas por cobrar / pagar")
    print(" 7. 'proyectos'          -> Muestra proyectos y tareas pendientes")
    print(" 8. 'salir'              -> Finalizar sesión")
    print("=" * 65 + "\n")

def main():
    print_banner()

    while True:
        try:
            query = input("💬 ERP Copilot > ").strip()
            if not query:
                continue

            q = query.lower()
            if q in ["exit", "salir", "quit", "q"]:
                print("¡Hasta pronto!")
                break

            elif any(k in q for k in ["resumen", "kpi", "dashboard", "metricas"]):
                print("\n📊 Consultando KPIs ejecutivos...")
                data = json.loads(server.erp_dashboard_kpis())
                print(json.dumps(data, indent=2, ensure_ascii=False))

            elif any(k in q for k in ["crm", "lead", "oportunidad", "pipeline"]):
                print("\n💼 Consultando CRM y Oportunidades...")
                data = json.loads(server.crm_list_leads(limit=10))
                for lead in data:
                    print(f" • [ID {lead['id']}] {lead['name']} | Cliente: {lead.get('partner_id', ['N/A', 'N/A'])[1] if isinstance(lead.get('partner_id'), list) else 'N/A'} | Esperado: S/ {lead.get('expected_revenue', 0):,.2f} | Etapa: {lead.get('stage_id', ['N/A', 'N/A'])[1] if isinstance(lead.get('stage_id'), list) else 'N/A'}")
                if not data:
                    print("No se encontraron oportunidades.")

            elif any(k in q for k in ["producto", "catalogo", "inventario", "stock"]):
                print("\n📦 Consultando catálogo de productos...")
                data = json.loads(server.inventory_search_products(limit=10))
                for prod in data:
                    print(f" • [ID {prod['id']}] {prod['name']} (SKU: {prod.get('default_code') or 'S/C'}) | Precio: S/ {prod.get('list_price', 0):,.2f} | Tipo: {prod.get('type')}")
                if not data:
                    print("No se encontraron productos.")

            elif any(k in q for k in ["contacto", "cliente", "proveedor", "partner"]):
                print("\n👥 Consultando contactos...")
                data = json.loads(server.contacts_search(limit=10))
                for c in data:
                    vat_str = f" | RUC/DNI: {c['vat']}" if c.get('vat') else ""
                    phone_str = f" | 📱 Tel/Cel: {c['phone']}" if c.get('phone') else ""
                    email_str = f" | ✉️ Email: {c['email']}" if c.get('email') else ""
                    print(f" • [ID {c['id']}] {c['name']}{vat_str}{phone_str}{email_str}")
                if not data:
                    print("No se encontraron contactos.")

            elif any(k in q for k in ["pedido", "cotizacion", "orden", "venta"]):
                print("\n💰 Consultando órdenes de venta...")
                data = json.loads(server.sales_list_orders(limit=10))
                for o in data:
                    print(f" • [ID {o['id']}] {o['name']} | Cliente: {o.get('partner_id', ['N/A', 'N/A'])[1] if isinstance(o.get('partner_id'), list) else 'N/A'} | Total: S/ {o.get('amount_total', 0):,.2f} | Estado: {o.get('state')}")
                if not data:
                    print("No hay pedidos de venta registrados.")

            elif any(k in q for k in ["factura", "cobro", "pago", "invoice"]):
                print("\n🧾 Consultando facturas de clientes...")
                data = json.loads(server.invoices_list(limit=10))
                for inv in data:
                    print(f" • [ID {inv['id']}] {inv['name']} | Total: S/ {inv.get('amount_total', 0):,.2f} | Saldo: S/ {inv.get('amount_residual', 0):,.2f} | Estado: {inv.get('state')}")
                if not data:
                    print("No hay facturas registradas.")

            elif any(k in q for k in ["proyecto", "tarea", "todo", "task"]):
                print("\n📋 Consultando tareas y proyectos...")
                tasks = json.loads(server.projects_list_tasks(limit=10))
                for t in tasks:
                    print(f" • [ID {t['id']}] {t['name']} | Prioridad: {t.get('priority')} | Vencimiento: {t.get('date_deadline') or 'Sin fecha'}")
                if not tasks:
                    print("No hay tareas registradas.")

            else:
                print(f"🔍 Búsqueda general en el ERP para '{query}'...")
                leads = json.loads(server.crm_list_leads(search_term=query, limit=3))
                contacts = json.loads(server.contacts_search(query=query, limit=3))
                products = json.loads(server.inventory_search_products(query=query, limit=3))
                print(f"Resultados encontrados: {len(leads)} leads/CRM, {len(contacts)} contactos, {len(products)} productos.")
                if leads:
                    print(" Leads:", [l['name'] for l in leads])
                if contacts:
                    print(" Contactos:", [c['name'] for c in contacts])
                if products:
                    print(" Productos:", [p['name'] for p in products])

            print()

        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"❌ Error ejecutando acción: {e}\n")

if __name__ == "__main__":
    main()
