"""
AI Agent Orchestration Engine for Cognitive ERP.
Executes tool calling with LLM (OpenAI / Gemini / Anthropic) with streaming SSE support
and intelligent fallback.
"""

import os
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional
from tool_registry import TOOLS_DEFINITIONS, TOOLS_BY_NAME, execute_tool, get_openai_tools_schema

logger = logging.getLogger("CognitiveERP.AgentEngine")

SYSTEM_PROMPT = """Eres Cognitive ERP AI Copilot, el asistente inteligente y agente autónomo integrado para Odoo 20 Community de COGNITIVE CORE.
Tu objetivo es ayudar al usuario a gestionar, consultar y operar todo el ERP mediante lenguaje natural, similar al chat IA de la versión Enterprise de Odoo.

Tienes acceso a 41 herramientas para operar:
- 📊 Analítica y KPIs ejecutivos (pipeline, ventas, cuentas por cobrar, tareas).
- 💼 CRM: Consultar, crear y actualizar oportunidades, mover etapas, marcar como Ganado o Perdido.
- 💰 Ventas: Listar cotizaciones, crear presupuestos con líneas de producto, confirmar órdenes de venta.
- 🧾 Facturación: Consultar facturas de clientes/proveedores, crear facturas borrador, validar/publicar facturas y registrar cobros.
- 📦 Catálogo e Inventario: Buscar productos, consultar stock disponible, crear productos y revisar despachos.
- 👥 Contactos: Buscar clientes o proveedores por nombre o RUC/DNI, crear contactos con datos fiscales.
- 📋 Proyectos y Tareas: Listar proyectos, crear tareas, asignar responsables y cambiar prioridades.
- 👔 Recursos Humanos: Consultar colaboradores y departamentos.
- ⏰ Agenda y Calendario: Ver y programar actividades (llamadas, reuniones) y eventos en el calendario.

Instrucciones de comportamiento:
1. Responde de manera profesional, clara y concisa en español.
2. Siempre que el usuario solicite consultar, crear, modificar o calcular algo sobre el ERP, utiliza la herramienta correspondiente.
3. Al mostrar datos financieros, formatea los montos claramente con su moneda (ej. S/ 10,000.00).
4. Cuando crees o confirmes cotizaciones, facturas o leads, resume los puntos clave (ID, cliente, total, estado).
5. Si faltan datos obligatorios para una acción (ej. precio o nombre de cliente), pídelos amablemente.
"""

class AgentEngine:
    """Manages AI Chat interactions and tool executions."""

    @staticmethod
    async def chat_completion(
        messages: List[Dict[str, str]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a single or multi-turn agent response with tool execution.
        """
        openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("api_key_openai")
        
        if openai_key:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=openai_key)
                llm_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

                formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
                tools = get_openai_tools_schema()

                response = await client.chat.completions.create(
                    model=llm_model,
                    messages=formatted_messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.2
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                # If the LLM requested tool execution
                executed_tools_info = []
                if tool_calls:
                    formatted_messages.append(response_message)
                    for tc in tool_calls:
                        tool_name = tc.function.name
                        try:
                            tool_args = json.loads(tc.function.arguments)
                        except Exception:
                            tool_args = {}

                        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                        try:
                            tool_result = execute_tool(tool_name, tool_args)
                        except Exception as e:
                            tool_result = {"error": str(e)}

                        executed_tools_info.append({
                            "id": tc.id,
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "result": tool_result
                        })

                        formatted_messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": tool_name,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })

                    # Second call to get final synthesized response
                    second_response = await client.chat.completions.create(
                        model=llm_model,
                        messages=formatted_messages,
                        temperature=0.3
                    )
                    final_text = second_response.choices[0].message.content
                else:
                    final_text = response_message.content

                return {
                    "role": "assistant",
                    "content": final_text,
                    "tool_calls": executed_tools_info
                }

            except Exception as e:
                logger.error(f"OpenAI Execution Error: {e}, falling back to built-in dispatcher")

        # Fallback intelligent parser if no OpenAI API key is provided
        return await AgentEngine._fallback_dispatcher(messages)

    @staticmethod
    async def stream_chat_response(
        messages: List[Dict[str, str]],
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streams response chunks in SSE format for React Frontend.
        Format: data: {"type": "token"|"tool_call"|"done", ...}\n\n
        """
        last_user_message = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        result = await AgentEngine.chat_completion(messages, model=model)

        # Emit tool calls if any
        if result.get("tool_calls"):
            for tc in result["tool_calls"]:
                yield f"data: {json.dumps({'type': 'tool_call', 'data': tc}, ensure_ascii=False)}\n\n"

        # Emit response content in stream tokens
        content = result.get("content", "")
        # Break into words for streaming effect
        words = content.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'type': 'token', 'content': chunk}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'final_message': result}, ensure_ascii=False)}\n\n"

    @staticmethod
    async def _fallback_dispatcher(messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Intelligent rule-based dispatcher when no third-party LLM key is configured.
        Analyzes user query and invokes the corresponding Odoo tools directly.
        """
        last_user_message = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        q = last_user_message.lower()
        tool_calls_info = []

        if any(k in q for k in ["resumen", "kpi", "dashboard", "metricas", "estado general"]):
            tool_name = "erp_dashboard_kpis"
            res = execute_tool(tool_name, {})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {}, "result": res})
            crm = res.get("crm", {})
            sales = res.get("sales", {})
            inv = res.get("invoicing", {})
            proj = res.get("projects", {})
            cat = res.get("catalog", {})

            content = (
                f"### 📊 Resumen Ejecutivo del ERP (Odoo 20)\n\n"
                f"- **💼 Pipeline CRM**: {crm.get('active_opportunities_count', 0)} oportunidades activas por un valor estimado de **S/ {crm.get('total_pipeline_expected_revenue', 0):,.2f}**\n"
                f"- **💰 Ventas**: {sales.get('confirmed_orders_count', 0)} pedidos confirmados (S/ {sales.get('confirmed_sales_total', 0):,.2f}) y {sales.get('open_quotations_count', 0)} cotizaciones abiertas (S/ {sales.get('quotations_total', 0):,.2f})\n"
                f"- **🧾 Cuentas por Cobrar**: {inv.get('open_customer_invoices_count', 0)} facturas pendientes por un total de **S/ {inv.get('total_receivable_amount', 0):,.2f}**\n"
                f"- **📋 Proyectos & Tareas**: {proj.get('active_projects_count', 0)} proyectos activos y {proj.get('open_tasks_count', 0)} tareas pendientes\n"
                f"- **📦 Catálogo**: {cat.get('total_active_products', 0)} productos activos y {cat.get('total_contacts', 0)} contactos registrados."
            )

        elif any(k in q for k in ["crm", "lead", "oportunidad", "pipeline", "embudo"]):
            tool_name = "crm_list_leads"
            res = execute_tool(tool_name, {"limit": 10})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {"limit": 10}, "result": res})
            if res:
                items = "\n".join([
                    f"- **[ID {l['id']}] {l['name']}**: Cliente: *{l.get('partner_id', ['N/A', 'N/A'])[1] if isinstance(l.get('partner_id'), list) else (l.get('partner_name') or 'Sin cliente')}* | Monto: **S/ {l.get('expected_revenue', 0):,.2f}** | Probabilidad: {l.get('probability', 0)}% | Etapa: `{l.get('stage_id', ['N/A', 'N/A'])[1] if isinstance(l.get('stage_id'), list) else 'N/A'}`"
                    for l in res
                ])
                content = f"### 💼 Oportunidades en CRM ({len(res)})\n\n{items}"
            else:
                content = "No se encontraron oportunidades registradas en el CRM."

        elif any(k in q for k in ["producto", "catalogo", "inventario", "precio", "stock"]):
            tool_name = "inventory_search_products"
            res = execute_tool(tool_name, {"limit": 15})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {"limit": 15}, "result": res})
            if res:
                items = "\n".join([
                    f"- **[ID {p['id']}] {p['name']}** (SKU: `{p.get('default_code') or 'S/C'}`): Precio: **S/ {p.get('list_price', 0):,.2f}** | Costo: S/ {p.get('standard_price', 0):,.2f} | Tipo: `{p.get('type')}`"
                    for p in res
                ])
                content = f"### 📦 Catálogo de Productos y Servicios ({len(res)})\n\n{items}"
            else:
                content = "No se encontraron productos en el catálogo."

        elif any(k in q for k in ["contacto", "cliente", "proveedor", "ruc", "dni"]):
            tool_name = "contacts_search"
            res = execute_tool(tool_name, {"limit": 15})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {"limit": 15}, "result": res})
            if res:
                formatted_contacts = []
                for c in res:
                    parts = [f"- **[ID {c['id']}] {c['name']}**"]
                    if c.get('vat'):
                        parts.append(f"RUC/DNI: {c['vat']}")
                    if c.get('phone'):
                        parts.append(f"📱 Tel/Cel: `{c['phone']}`")
                    if c.get('email'):
                        parts.append(f"✉️ Email: {c['email']}")
                    elif not c.get('phone'):
                        parts.append("Sin datos de contacto")
                    formatted_contacts.append(" | ".join(parts))
                
                content = f"### 👥 Directorio de Contactos ({len(res)})\n\n" + "\n".join(formatted_contacts)
            else:
                content = "No se encontraron contactos registrados."

        elif any(k in q for k in ["pedido", "cotizacion", "orden", "presupuesto"]):
            tool_name = "sales_list_orders"
            res = execute_tool(tool_name, {"limit": 10})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {"limit": 10}, "result": res})
            if res:
                items = "\n".join([
                    f"- **[ID {o['id']}] {o['name']}**: Cliente: *{o.get('partner_id', ['N/A', 'N/A'])[1] if isinstance(o.get('partner_id'), list) else 'N/A'}* | Total: **S/ {o.get('amount_total', 0):,.2f}** | Estado: `{o.get('state')}`"
                    for o in res
                ])
                content = f"### 💰 Pedidos y Cotizaciones ({len(res)})\n\n{items}"
            else:
                content = "No hay pedidos o cotizaciones registradas actualmente."

        elif any(k in q for k in ["factura", "cobranza", "cobro", "pago", "invoice"]):
            tool_name = "invoices_list"
            res = execute_tool(tool_name, {"limit": 10})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {"limit": 10}, "result": res})
            if res:
                items = "\n".join([
                    f"- **[ID {inv['id']}] {inv['name']}**: Total: **S/ {inv.get('amount_total', 0):,.2f}** | Saldo: **S/ {inv.get('amount_residual', 0):,.2f}** | Estado: `{inv.get('state')}` | Pago: `{inv.get('payment_state')}`"
                    for inv in res
                ])
                content = f"### 🧾 Facturas ({len(res)})\n\n{items}"
            else:
                content = "No hay facturas registradas."

        elif any(k in q for k in ["proyecto", "tarea", "todo", "task"]):
            tool_name = "projects_list_tasks"
            res = execute_tool(tool_name, {"limit": 10})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {"limit": 10}, "result": res})
            if res:
                items = "\n".join([
                    f"- **[ID {t['id']}] {t['name']}**: Prioridad: {t.get('priority')} | Vencimiento: {t.get('date_deadline') or 'Sin fecha'}"
                    for t in res
                ])
                content = f"### 📋 Tareas y Proyectos ({len(res)})\n\n{items}"
            else:
                content = "No hay tareas registradas."

        elif any(k in q for k in ["empleado", "colaborador", "equipo", "rrhh", "personal"]):
            tool_name = "hr_list_employees"
            res = execute_tool(tool_name, {"limit": 10})
            tool_calls_info.append({"tool_name": tool_name, "arguments": {"limit": 10}, "result": res})
            if res:
                items = "\n".join([
                    f"- **{e['name']}**: Cargo: {e.get('job_title') or 'General'} | Email: {e.get('work_email') or 'N/A'}"
                    for e in res
                ])
                content = f"### 👔 Directorio de Personal ({len(res)})\n\n{items}"
            else:
                content = "No hay colaboradores registrados en RRHH."

        else:
            # General search across CRM, contacts and products
            c_res = execute_tool("contacts_search", {"query": last_user_message, "limit": 3})
            p_res = execute_tool("inventory_search_products", {"query": last_user_message, "limit": 3})
            l_res = execute_tool("crm_list_leads", {"search_term": last_user_message, "limit": 3})
            
            tool_calls_info.append({"tool_name": "contacts_search", "arguments": {"query": last_user_message}, "result": c_res})
            tool_calls_info.append({"tool_name": "inventory_search_products", "arguments": {"query": last_user_message}, "result": p_res})
            tool_calls_info.append({"tool_name": "crm_list_leads", "arguments": {"search_term": last_user_message}, "result": l_res})

            content = (
                f"He procesado tu consulta: *\"{last_user_message}\"*\n\n"
                f"- **Contactos encontrados**: {len(c_res)}\n"
                f"- **Productos encontrados**: {len(p_res)}\n"
                f"- **Oportunidades CRM encontradas**: {len(l_res)}\n\n"
                "¿Deseas que profundice en alguna cotización, cliente o registro en particular?"
            )

        return {
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls_info
        }
