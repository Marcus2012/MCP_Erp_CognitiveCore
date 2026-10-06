# 🧠 Cognitive ERP MCP (Odoo 20 Community)

Servidor **Model Context Protocol (MCP)** de alto rendimiento para interactuar con **Odoo 20.0 Community** desde cualquier cliente de Inteligencia Artificial (Claude Desktop, Cursor, Antigravity, VSCode MCP, Open-WebUI o Agentes Autónomos).

Permite convertir tu Odoo Community en un sistema con **IA conversacional ejecutiva y operativa**, similar al chat IA de la versión Enterprise.

---

## 🚀 Capacidades y Servicios Disponibles (41 Herramientas MCP)

### 1. 📊 Analítica y Dashboard Ejecutivo
- `erp_dashboard_kpis`: Resumen ejecutivo en tiempo real (monto del pipeline de ventas, cotizaciones abiertas, ventas confirmadas, cuentas por cobrar/facturas pendientes, proyectos y tareas).
- `odoo_generic_query`: Ejecución de consultas ORM flexibles (`search_read`, `fields_get`, `search_count`) para inspeccionar cualquier modelo estándar o personalizado de Odoo.

### 2. 💼 CRM y Pipeline de Oportunidades (`crm.lead`)
- `crm_list_stages`: Listado de etapas del embudo comercial.
- `crm_list_leads`: Búsqueda de oportunidades por cliente, etapa, monto esperado o responsable.
- `crm_get_lead`: Ficha detallada de una oportunidad comercial con notas e historial.
- `crm_create_lead`: Creación de nuevos prospectos u oportunidades comerciales.
- `crm_update_lead`: Actualización de estado, probabilidad e ingresos esperados.
- `crm_mark_won`: Cerrar oportunidad como **Ganada** (100% de probabilidad).
- `crm_mark_lost`: Marcar oportunidad como **Perdida** con motivo.

### 3. 💰 Ventas y Cotizaciones (`sale.order`, `sale.order.line`)
- `sales_list_orders`: Consulta de cotizaciones y órdenes de venta por estado (`draft`, `sent`, `sale`, `cancel`).
- `sales_get_order`: Desglose completo de la orden con productos, cantidades, precios unitarios, impuestos y totales.
- `sales_create_quotation`: Creación de presupuestos con múltiples líneas de productos y términos de pago.
- `sales_confirm_order`: Confirmación de cotización a **Pedido de Venta en Firme**.
- `sales_cancel_order`: Cancelación de cotizaciones y pedidos.

### 4. 🧾 Facturación y Cobranzas (`account.move`, `account.payment`)
- `invoices_list`: Listado de facturas de clientes (`out_invoice`) y facturas de proveedores (`in_invoice`).
- `invoices_get`: Detalle de factura con saldos pendientes (`amount_residual`) y asientos asociados.
- `invoices_create`: Generación de facturas borrador con líneas de producto y fechas de vencimiento.
- `invoices_post`: Validación y publicación de facturas (asignación de correlativo oficial).
- `invoices_register_payment`: Registro de cobros y pagos directamente en Odoo.

### 5. 📦 Inventario y Catálogo de Productos (`product.product`, `stock.picking`)
- `inventory_search_products`: Búsqueda de productos, servicios y consumibles por nombre, SKU o código de barras.
- `inventory_get_product`: Ficha técnica del producto, precio de venta, costo y existencias (`qty_available`, `virtual_available`).
- `inventory_create_product`: Registro de nuevos productos o servicios en el catálogo.
- `inventory_update_product`: Modificación de precios de venta, costos y descripciones.
- `inventory_list_pickings`: Consulta de transferencias, despachos (`outgoing`) y recepciones (`incoming`).

### 6. 👥 Contactos, Clientes y Proveedores (`res.partner`)
- `contacts_search`: Búsqueda de empresas y personas naturales por RUC, DNI, nombre, teléfono o correo.
- `contacts_get`: Ficha completa de cliente/proveedor con historial comercial y balance financiero.
- `contacts_create`: Alta de nuevos clientes o proveedores con datos fiscales y dirección.
- `contacts_update`: Actualización de datos de contacto.

### 7. 📋 Proyectos y Tareas (`project.project`, `project.task`)
- `projects_list`: Listado de proyectos activos y métricas de avance.
- `projects_list_tasks`: Consulta de tareas por proyecto, responsable, prioridad o fecha límite.
- `projects_get_task`: Ficha de tarea con descripción detallada y estado.
- `projects_create_task`: Creación de nuevas tareas o to-dos.
- `projects_update_task`: Cambio de etapa, prioridad o reasignación de tareas.

### 8. 👔 Recursos Humanos (`hr.employee`, `hr.department`)
- `hr_list_employees`: Directorio de colaboradores con cargo, departamento, correo y teléfono.
- `hr_get_employee`: Ficha completa del empleado y jerarquía.
- `hr_list_departments`: Listado de departamentos de la organización.

### 9. ⏰ Actividades y Calendario (`mail.activity`, `calendar.event`)
- `activities_list`: Consulta de llamadas, reuniones y acciones pendientes en el ERP.
- `activities_create`: Programación de actividades de seguimiento vinculadas a cualquier registro (Lead, Cliente, Factura, Pedido).
- `activities_mark_done`: Marcar actividades como completadas con retroalimentación.
- `calendar_list_meetings`: Agenda de reuniones y eventos del calendario.
- `calendar_create_meeting`: Agendamiento de reuniones con participantes.

---

## ⚙️ Configuración del Entorno (.env)

Crea o edita el archivo `.env` en la raíz del proyecto:

```env
ODOO_URL=https://erp.cognitivecore.pe/
ODOO_DB=erp_cognitivecore
ODOO_EMAIL=datadriven111@gmail.com
ODOO_API_KEY=491e1eec3cfedd93a8561f2b9cd822b870bbda89
ODOO_PASSWORD=Temp11$2026
```

---

## 📦 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

---

## 🔌 Cómo Conectar a tu Cliente IA (Claude Desktop, Cursor, Antigravity)

### 1. Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "cognitive-erp": {
      "command": "python",
      "args": [
        "C:\\Users\\Kevin\\Documents\\Cognitive Core\\MCP_Erp_CognitiveCore\\server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### 2. Cursor / VS Code MCP
Añade a tu configuración MCP:
```json
{
  "name": "Cognitive ERP Odoo 20",
  "command": "python",
  "args": ["server.py"]
}
```

---

## 🧪 Pruebas y Modo Interactivo

Puedes probar el servidor y el cliente interactivo localmente:

```bash
# 1. Probar registro de herramientas y conexión en vivo
python test_server.py

# 2. Iniciar el Copilot interactivo en terminal
python demo_cli.py
```

---

## 💡 Ejemplos de Consultas en el Chat IA

- *"¿Cuál es el estado de nuestro pipeline comercial y cuánto tenemos por cobrar?"*
- *"Crea una oportunidad para el cliente COGNITIVE CORE por un valor estimado de S/ 15,000 para el servicio de ERP."*
- *"Genera una cotización para Willy Hinostroza con 2 unidades del servicio ERP CognitiveCore."*
- *"Muéstrame los productos que tenemos registrados en catálogo y sus precios."*
- *"¿Qué tareas o actividades pendientes tengo programadas para esta semana?"*
- *"Agenda una reunión en el calendario para mañana a las 10:00 AM con el equipo comercial."*
