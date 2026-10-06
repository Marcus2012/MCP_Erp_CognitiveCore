"""
Tool Registry for Cognitive ERP (Odoo 20).
Defines schemas, metadata, and callable functions for both MCP and FastAPI Agent.
Provides full CRU (Create, Read, Update - NO Delete) capabilities across all ERP modules.
"""

from typing import Any, Callable, Dict, List
from services.crm_service import CRMService
from services.sales_service import SalesService
from services.invoicing_service import InvoicingService
from services.inventory_service import InventoryService
from services.contacts_service import ContactsService
from services.projects_service import ProjectsService
from services.hr_service import HRService
from services.activities_calendar_service import ActivitiesCalendarService
from services.analytics_service import AnalyticsService
from services.theme_service import ThemeService

TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    # --- Analytics, KPIs & Generic ORM CRU ---
    {
        "name": "erp_dashboard_kpis",
        "category": "Analytics",
        "description": "Obtener KPIs y resumen ejecutivo en tiempo real del ERP (pipeline CRM, cotizaciones, ventas confirmadas, cuentas por cobrar, tareas activas).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "func": lambda args: AnalyticsService.get_dashboard_summary()
    },
    {
        "name": "odoo_generic_query",
        "category": "Analytics",
        "description": "Ejecutar una consulta ORM flexible de lectura en cualquier modelo de Odoo (search_read, fields_get, search_count).",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Nombre técnico del modelo Odoo (ej. 'res.partner', 'crm.lead')"},
                "method": {"type": "string", "enum": ["search_read", "fields_get", "search_count"], "default": "search_read"},
                "domain": {"type": "array", "description": "Dominio de filtro Odoo (ej. [['is_company', '=', true]])"},
                "fields": {"type": "array", "items": {"type": "string"}, "description": "Lista de campos a leer"},
                "limit": {"type": "integer", "default": 20},
                "offset": {"type": "integer", "default": 0},
                "order": {"type": "string", "description": "Ordenamiento (ej. 'id desc')"}
            },
            "required": ["model"]
        },
        "func": lambda args: AnalyticsService.generic_query(
            model=args.get("model"),
            method=args.get("method", "search_read"),
            domain=args.get("domain", []),
            fields=args.get("fields"),
            limit=args.get("limit", 20),
            offset=args.get("offset", 0),
            order=args.get("order")
        )
    },
    {
        "name": "odoo_create_record",
        "category": "Analytics",
        "description": "Crear un registro genérico en cualquier modelo de Odoo (Create).",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Nombre técnico del modelo Odoo (ej. 'res.partner', 'project.project')"},
                "values": {"type": "object", "description": "Diccionario de campos y valores a insertar"}
            },
            "required": ["model", "values"]
        },
        "func": lambda args: AnalyticsService.create_record(
            model=args["model"],
            values=args["values"]
        )
    },
    {
        "name": "odoo_read_record",
        "category": "Analytics",
        "description": "Leer los datos de un registro específico en cualquier modelo de Odoo por su ID (Read).",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Nombre técnico del modelo Odoo"},
                "record_id": {"type": "integer", "description": "ID del registro a leer"},
                "fields": {"type": "array", "items": {"type": "string"}, "description": "Lista opcional de campos específicos a leer"}
            },
            "required": ["model", "record_id"]
        },
        "func": lambda args: AnalyticsService.read_record(
            model=args["model"],
            record_id=args["record_id"],
            fields=args.get("fields")
        )
    },
    {
        "name": "odoo_update_record",
        "category": "Analytics",
        "description": "Actualizar campos de un registro específico en cualquier modelo de Odoo (Update).",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Nombre técnico del modelo Odoo"},
                "record_id": {"type": "integer", "description": "ID del registro a actualizar"},
                "values": {"type": "object", "description": "Diccionario de campos y nuevos valores a actualizar"}
            },
            "required": ["model", "record_id", "values"]
        },
        "func": lambda args: AnalyticsService.update_record(
            model=args["model"],
            record_id=args["record_id"],
            values=args["values"]
        )
    },

    # --- CRM & Pipeline ---
    {
        "name": "crm_list_stages",
        "category": "CRM",
        "description": "Listar todas las etapas configuradas en el embudo comercial CRM.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "func": lambda args: CRMService.list_stages()
    },
    {
        "name": "crm_list_leads",
        "category": "CRM",
        "description": "Buscar y listar oportunidades o prospectos del CRM por nombre de cliente, etapa, estado o vendedor.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {"type": "string", "description": "Término de búsqueda (nombre del lead o cliente)"},
                "stage_name": {"type": "string", "description": "Filtrar por nombre de etapa (ej. 'New', 'Won')"},
                "is_won": {"type": "boolean", "description": "True para oportunidades ganadas, False para abiertas"},
                "user_id": {"type": "integer", "description": "ID del vendedor asignado"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": []
        },
        "func": lambda args: CRMService.list_leads(
            search_term=args.get("search_term"),
            stage_name=args.get("stage_name"),
            is_won=args.get("is_won"),
            user_id=args.get("user_id"),
            limit=args.get("limit", 20)
        )
    },
    {
        "name": "crm_get_lead",
        "category": "CRM",
        "description": "Obtener los datos detallados de una oportunidad/prospecto específico por su ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer", "description": "ID de la oportunidad CRM"}
            },
            "required": ["lead_id"]
        },
        "func": lambda args: CRMService.get_lead(lead_id=args["lead_id"])
    },
    {
        "name": "crm_create_lead",
        "category": "CRM",
        "description": "Crear una nueva oportunidad comercial o lead en el CRM.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Título o asunto de la oportunidad (ej. 'Implementación ERP')"},
                "partner_id": {"type": "integer", "description": "ID del cliente existente en Odoo"},
                "partner_name": {"type": "string", "description": "Nombre de la empresa/cliente si aún no existe"},
                "email_from": {"type": "string", "description": "Correo electrónico de contacto"},
                "phone": {"type": "string", "description": "Teléfono de contacto"},
                "expected_revenue": {"type": "number", "description": "Monto o ingreso estimado (ej. 10000.0)"},
                "probability": {"type": "number", "description": "Probabilidad estimada de 0 a 100"},
                "description": {"type": "string", "description": "Notas internas o requerimientos del cliente"},
                "priority": {"type": "string", "enum": ["0", "1", "2", "3"], "default": "1"}
            },
            "required": ["name"]
        },
        "func": lambda args: CRMService.create_lead(
            name=args["name"],
            partner_id=args.get("partner_id"),
            partner_name=args.get("partner_name"),
            email_from=args.get("email_from"),
            phone=args.get("phone"),
            expected_revenue=args.get("expected_revenue", 0.0),
            probability=args.get("probability"),
            description=args.get("description"),
            priority=args.get("priority", "1")
        )
    },
    {
        "name": "crm_update_lead",
        "category": "CRM",
        "description": "Actualizar campos de una oportunidad CRM (etapa, monto esperado, probabilidad, notas, cliente).",
        "parameters": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer", "description": "ID de la oportunidad a actualizar"},
                "name": {"type": "string", "description": "Nuevo nombre o título de la oportunidad"},
                "stage_id": {"type": "integer", "description": "Nuevo ID de etapa"},
                "expected_revenue": {"type": "number", "description": "Nuevo monto estimado"},
                "probability": {"type": "number", "description": "Nueva probabilidad (0-100)"},
                "description": {"type": "string", "description": "Notas o descripción adicional"},
                "partner_id": {"type": "integer", "description": "ID del cliente vinculado"},
                "phone": {"type": "string", "description": "Teléfono"},
                "email_from": {"type": "string", "description": "Correo"}
            },
            "required": ["lead_id"]
        },
        "func": lambda args: CRMService.update_lead(
            lead_id=args["lead_id"],
            values={k: v for k, v in args.items() if k != "lead_id" and v is not None}
        )
    },
    {
        "name": "crm_mark_won",
        "category": "CRM",
        "description": "Marcar una oportunidad CRM como Ganada (100% de probabilidad).",
        "parameters": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer", "description": "ID de la oportunidad CRM"}
            },
            "required": ["lead_id"]
        },
        "func": lambda args: CRMService.mark_lead_won(lead_id=args["lead_id"])
    },
    {
        "name": "crm_mark_lost",
        "category": "CRM",
        "description": "Marcar una oportunidad CRM como Perdida.",
        "parameters": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer", "description": "ID de la oportunidad CRM"},
                "lost_reason_id": {"type": "integer", "description": "ID del motivo de pérdida"}
            },
            "required": ["lead_id"]
        },
        "func": lambda args: CRMService.mark_lead_lost(
            lead_id=args["lead_id"],
            lost_reason_id=args.get("lost_reason_id")
        )
    },

    # --- Sales & Quotations ---
    {
        "name": "sales_list_orders",
        "category": "Ventas",
        "description": "Listar cotizaciones y pedidos de venta por cliente o estado (draft, sent, sale, cancel).",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {"type": "string", "description": "Número de orden o nombre de cliente"},
                "partner_id": {"type": "integer", "description": "ID del cliente"},
                "state": {"type": "string", "enum": ["draft", "sent", "sale", "cancel"], "description": "Estado del pedido"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": []
        },
        "func": lambda args: SalesService.list_orders(
            search_term=args.get("search_term"),
            partner_id=args.get("partner_id"),
            state=args.get("state"),
            limit=args.get("limit", 20)
        )
    },
    {
        "name": "sales_get_order",
        "category": "Ventas",
        "description": "Obtener los datos completos de una cotización/orden de venta con sus líneas de producto y totales.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "ID de la orden de venta"}
            },
            "required": ["order_id"]
        },
        "func": lambda args: SalesService.get_order(order_id=args["order_id"])
    },
    {
        "name": "sales_create_quotation",
        "category": "Ventas",
        "description": "Crear un nuevo presupuesto/cotización de venta con líneas de productos.",
        "parameters": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "integer", "description": "ID del cliente"},
                "order_lines": {
                    "type": "array",
                    "description": "Lista de líneas: [{'product_id': 1, 'qty': 2, 'price_unit': 1250.0, 'description': 'Opcional'}]",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer"},
                            "qty": {"type": "number", "default": 1.0},
                            "price_unit": {"type": "number"},
                            "description": {"type": "string"}
                        },
                        "required": ["product_id"]
                    }
                },
                "payment_term_id": {"type": "integer", "description": "ID del término de pago"},
                "note": {"type": "string", "description": "Términos y condiciones o nota"}
            },
            "required": ["partner_id", "order_lines"]
        },
        "func": lambda args: SalesService.create_quotation(
            partner_id=args["partner_id"],
            order_lines=args["order_lines"],
            payment_term_id=args.get("payment_term_id"),
            note=args.get("note")
        )
    },
    {
        "name": "sales_update_order",
        "category": "Ventas",
        "description": "Actualizar campos principales de una orden de venta o cotización (cliente, notas, términos de pago, fecha de validez).",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "ID de la orden de venta"},
                "partner_id": {"type": "integer", "description": "ID del cliente"},
                "payment_term_id": {"type": "integer", "description": "ID del plazo de pago"},
                "note": {"type": "string", "description": "Notas o términos"},
                "validity_date": {"type": "string", "description": "Fecha de validez de la oferta (YYYY-MM-DD)"}
            },
            "required": ["order_id"]
        },
        "func": lambda args: SalesService.update_order(
            order_id=args["order_id"],
            values={k: v for k, v in args.items() if k != "order_id" and v is not None}
        )
    },
    {
        "name": "sales_add_order_line",
        "category": "Ventas",
        "description": "Agregar una nueva línea de producto a una orden de venta o cotización existente.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "ID de la orden de venta"},
                "product_id": {"type": "integer", "description": "ID del producto a agregar"},
                "qty": {"type": "number", "description": "Cantidad", "default": 1.0},
                "price_unit": {"type": "number", "description": "Precio unitario personalizado (opcional)"},
                "description": {"type": "string", "description": "Descripción personalizada de la línea (opcional)"}
            },
            "required": ["order_id", "product_id"]
        },
        "func": lambda args: SalesService.add_order_line(
            order_id=args["order_id"],
            product_id=args["product_id"],
            qty=args.get("qty", 1.0),
            price_unit=args.get("price_unit"),
            description=args.get("description")
        )
    },
    {
        "name": "sales_update_order_line",
        "category": "Ventas",
        "description": "Actualizar una línea existente dentro de una orden de venta (cantidad, precio unitario, descripción).",
        "parameters": {
            "type": "object",
            "properties": {
                "line_id": {"type": "integer", "description": "ID de la línea de orden de venta"},
                "product_uom_qty": {"type": "number", "description": "Nueva cantidad"},
                "price_unit": {"type": "number", "description": "Nuevo precio unitario"},
                "name": {"type": "string", "description": "Nueva descripción"}
            },
            "required": ["line_id"]
        },
        "func": lambda args: SalesService.update_order_line(
            line_id=args["line_id"],
            values={k: v for k, v in args.items() if k != "line_id" and v is not None}
        )
    },
    {
        "name": "sales_confirm_order",
        "category": "Ventas",
        "description": "Confirmar una cotización en borrador para convertirla en Orden de Venta en firme.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "ID de la cotización a confirmar"}
            },
            "required": ["order_id"]
        },
        "func": lambda args: SalesService.confirm_order(order_id=args["order_id"])
    },
    {
        "name": "sales_cancel_order",
        "category": "Ventas",
        "description": "Cancelar una cotización u orden de venta.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "ID de la orden a cancelar"}
            },
            "required": ["order_id"]
        },
        "func": lambda args: SalesService.cancel_order(order_id=args["order_id"])
    },

    # --- Invoicing & Billing ---
    {
        "name": "invoices_list",
        "category": "Facturación",
        "description": "Listar facturas de clientes (out_invoice) o facturas de proveedores (in_invoice) con saldos pendientes.",
        "parameters": {
            "type": "object",
            "properties": {
                "move_type": {"type": "string", "enum": ["out_invoice", "in_invoice", "out_refund", "in_refund"], "default": "out_invoice"},
                "state": {"type": "string", "enum": ["draft", "posted", "cancel"]},
                "payment_state": {"type": "string", "enum": ["not_paid", "in_payment", "paid", "reversed"]},
                "partner_id": {"type": "integer", "description": "ID del cliente/proveedor"},
                "search_term": {"type": "string", "description": "Número de factura o nombre de cliente"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": []
        },
        "func": lambda args: InvoicingService.list_invoices(
            move_type=args.get("move_type", "out_invoice"),
            state=args.get("state"),
            payment_state=args.get("payment_state"),
            partner_id=args.get("partner_id"),
            search_term=args.get("search_term"),
            limit=args.get("limit", 20)
        )
    },
    {
        "name": "invoices_get",
        "category": "Facturación",
        "description": "Obtener los datos completos de una factura con sus líneas y saldo pendiente de cobro.",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "ID de la factura"}
            },
            "required": ["invoice_id"]
        },
        "func": lambda args: InvoicingService.get_invoice(invoice_id=args["invoice_id"])
    },
    {
        "name": "invoices_create",
        "category": "Facturación",
        "description": "Crear una factura borrador de cliente o proveedor con líneas de producto.",
        "parameters": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "integer", "description": "ID del cliente o proveedor"},
                "invoice_lines": {
                    "type": "array",
                    "description": "Líneas de factura: [{'product_id': 1, 'quantity': 1, 'price_unit': 1250.0, 'name': 'Descripción'}]",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer"},
                            "quantity": {"type": "number", "default": 1.0},
                            "price_unit": {"type": "number"},
                            "name": {"type": "string"}
                        }
                    }
                },
                "move_type": {"type": "string", "enum": ["out_invoice", "in_invoice"], "default": "out_invoice"},
                "invoice_date": {"type": "string", "description": "Fecha de emisión (YYYY-MM-DD)"},
                "invoice_date_due": {"type": "string", "description": "Fecha de vencimiento (YYYY-MM-DD)"},
                "ref": {"type": "string", "description": "Referencia o número de factura físico"}
            },
            "required": ["partner_id", "invoice_lines"]
        },
        "func": lambda args: InvoicingService.create_invoice(
            partner_id=args["partner_id"],
            invoice_lines=args["invoice_lines"],
            move_type=args.get("move_type", "out_invoice"),
            invoice_date=args.get("invoice_date"),
            invoice_date_due=args.get("invoice_date_due"),
            ref=args.get("ref")
        )
    },
    {
        "name": "invoices_update_invoice",
        "category": "Facturación",
        "description": "Actualizar datos de una factura en borrador (fecha de emisión, vencimiento, referencia, cliente, notas).",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "ID de la factura"},
                "partner_id": {"type": "integer", "description": "ID del cliente/proveedor"},
                "invoice_date": {"type": "string", "description": "Fecha de emisión (YYYY-MM-DD)"},
                "invoice_date_due": {"type": "string", "description": "Fecha de vencimiento (YYYY-MM-DD)"},
                "ref": {"type": "string", "description": "Referencia física"},
                "narration": {"type": "string", "description": "Términos o notas"}
            },
            "required": ["invoice_id"]
        },
        "func": lambda args: InvoicingService.update_invoice(
            invoice_id=args["invoice_id"],
            values={k: v for k, v in args.items() if k != "invoice_id" and v is not None}
        )
    },
    {
        "name": "invoices_add_line",
        "category": "Facturación",
        "description": "Agregar una nueva línea a una factura en borrador.",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "ID de la factura"},
                "name": {"type": "string", "description": "Descripción del concepto o servicio"},
                "price_unit": {"type": "number", "description": "Precio unitario"},
                "quantity": {"type": "number", "description": "Cantidad", "default": 1.0},
                "product_id": {"type": "integer", "description": "ID del producto (opcional)"}
            },
            "required": ["invoice_id", "name", "price_unit"]
        },
        "func": lambda args: InvoicingService.add_invoice_line(
            invoice_id=args["invoice_id"],
            name=args["name"],
            price_unit=args["price_unit"],
            quantity=args.get("quantity", 1.0),
            product_id=args.get("product_id")
        )
    },
    {
        "name": "invoices_post",
        "category": "Facturación",
        "description": "Validar y Publicar una factura en borrador (asigna numeración oficial en el ERP).",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "ID de la factura"}
            },
            "required": ["invoice_id"]
        },
        "func": lambda args: InvoicingService.post_invoice(invoice_id=args["invoice_id"])
    },
    {
        "name": "invoices_register_payment",
        "category": "Facturación",
        "description": "Registrar el pago o cobro de una factura publicada.",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "ID de la factura"},
                "amount": {"type": "number", "description": "Monto pagado (si se omite, se paga el saldo total)"},
                "payment_date": {"type": "string", "description": "Fecha de pago (YYYY-MM-DD)"}
            },
            "required": ["invoice_id"]
        },
        "func": lambda args: InvoicingService.register_payment(
            invoice_id=args["invoice_id"],
            amount=args.get("amount"),
            payment_date=args.get("payment_date")
        )
    },

    # --- Inventory & Products ---
    {
        "name": "inventory_search_products",
        "category": "Inventario",
        "description": "Buscar productos y servicios del catálogo por nombre, código SKU o código de barras.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto de búsqueda (nombre, SKU o código)"},
                "product_type": {"type": "string", "enum": ["service", "consu", "product"], "description": "Tipo de producto"},
                "limit": {"type": "integer", "default": 25}
            },
            "required": []
        },
        "func": lambda args: InventoryService.search_products(
            query=args.get("query"),
            product_type=args.get("product_type"),
            limit=args.get("limit", 25)
        )
    },
    {
        "name": "inventory_get_product",
        "category": "Inventario",
        "description": "Obtener la ficha completa del producto: precio de venta, costo, stock disponible y categoría.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "ID del producto"}
            },
            "required": ["product_id"]
        },
        "func": lambda args: InventoryService.get_product(product_id=args["product_id"])
    },
    {
        "name": "inventory_create_product",
        "category": "Inventario",
        "description": "Crear un nuevo producto o servicio en el catálogo de Odoo.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre del producto/servicio"},
                "list_price": {"type": "number", "description": "Precio de venta al público"},
                "default_code": {"type": "string", "description": "Código interno o SKU"},
                "standard_price": {"type": "number", "description": "Costo unitario"},
                "product_type": {"type": "string", "enum": ["service", "consu", "product"], "default": "service"},
                "description": {"type": "string", "description": "Descripción para cotizaciones y ventas"}
            },
            "required": ["name", "list_price"]
        },
        "func": lambda args: InventoryService.create_product(
            name=args["name"],
            list_price=args["list_price"],
            default_code=args.get("default_code"),
            standard_price=args.get("standard_price"),
            product_type=args.get("product_type", "service"),
            description=args.get("description")
        )
    },
    {
        "name": "inventory_update_product",
        "category": "Inventario",
        "description": "Actualizar precios, SKU o descripción de un producto existente.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "ID del producto"},
                "name": {"type": "string", "description": "Nuevo nombre del producto"},
                "list_price": {"type": "number", "description": "Nuevo precio de venta"},
                "standard_price": {"type": "number", "description": "Nuevo costo"},
                "default_code": {"type": "string", "description": "Nuevo código SKU"},
                "barcode": {"type": "string", "description": "Código de barras"},
                "description_sale": {"type": "string", "description": "Nueva descripción"}
            },
            "required": ["product_id"]
        },
        "func": lambda args: InventoryService.update_product(
            product_id=args["product_id"],
            values={k: v for k, v in args.items() if k != "product_id" and v is not None}
        )
    },
    {
        "name": "inventory_update_stock_quantity",
        "category": "Inventario",
        "description": "Ajustar o actualizar la cantidad de stock disponible (on-hand) de un producto.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "ID del producto a ajustar stock"},
                "new_quantity": {"type": "number", "description": "Nueva cantidad física real de inventario"},
                "location_id": {"type": "integer", "description": "ID de la ubicación de inventario (opcional)"}
            },
            "required": ["product_id", "new_quantity"]
        },
        "func": lambda args: InventoryService.update_stock_quantity(
            product_id=args["product_id"],
            new_quantity=args["new_quantity"],
            location_id=args.get("location_id")
        )
    },
    {
        "name": "inventory_list_pickings",
        "category": "Inventario",
        "description": "Listar transferencias de inventario, despachos a clientes o recepciones de proveedores.",
        "parameters": {
            "type": "object",
            "properties": {
                "picking_type": {"type": "string", "enum": ["outgoing", "incoming", "internal"]},
                "state": {"type": "string", "enum": ["draft", "waiting", "confirmed", "assigned", "done", "cancel"]},
                "partner_id": {"type": "integer", "description": "ID del cliente/proveedor"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": []
        },
        "func": lambda args: InventoryService.list_pickings(
            picking_type=args.get("picking_type"),
            state=args.get("state"),
            partner_id=args.get("partner_id"),
            limit=args.get("limit", 20)
        )
    },
    {
        "name": "inventory_get_picking",
        "category": "Inventario",
        "description": "Obtener los datos detallados de una transferencia o guía de remisión/despacho con sus movimientos.",
        "parameters": {
            "type": "object",
            "properties": {
                "picking_id": {"type": "integer", "description": "ID de la transferencia de stock"}
            },
            "required": ["picking_id"]
        },
        "func": lambda args: InventoryService.get_picking(picking_id=args["picking_id"])
    },
    {
        "name": "inventory_update_picking",
        "category": "Inventario",
        "description": "Actualizar campos de una transferencia de inventario (fecha programada, origen, cliente).",
        "parameters": {
            "type": "object",
            "properties": {
                "picking_id": {"type": "integer", "description": "ID de la transferencia"},
                "scheduled_date": {"type": "string", "description": "Fecha programada (YYYY-MM-DD HH:MM:SS)"},
                "origin": {"type": "string", "description": "Documento origen"},
                "partner_id": {"type": "integer", "description": "ID del cliente o proveedor"}
            },
            "required": ["picking_id"]
        },
        "func": lambda args: InventoryService.update_picking(
            picking_id=args["picking_id"],
            values={k: v for k, v in args.items() if k != "picking_id" and v is not None}
        )
    },

    # --- Contacts & Partners ---
    {
        "name": "contacts_search",
        "category": "Contactos",
        "description": "Buscar clientes, proveedores o personas por nombre, RUC, DNI, correo o teléfono.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Nombre, RUC, DNI, teléfono o email"},
                "is_company": {"type": "boolean", "description": "True para empresas, False para personas"},
                "is_customer": {"type": "boolean", "description": "True para clientes"},
                "is_supplier": {"type": "boolean", "description": "True para proveedores"},
                "limit": {"type": "integer", "default": 25}
            },
            "required": []
        },
        "func": lambda args: ContactsService.search_contacts(
            query=args.get("query"),
            is_company=args.get("is_company"),
            is_customer=args.get("is_customer"),
            is_supplier=args.get("is_supplier"),
            limit=args.get("limit", 25)
        )
    },
    {
        "name": "contacts_get",
        "category": "Contactos",
        "description": "Obtener los datos detallados de un contacto/cliente con su historial comercial y balance.",
        "parameters": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "integer", "description": "ID del contacto"}
            },
            "required": ["partner_id"]
        },
        "func": lambda args: ContactsService.get_contact(partner_id=args["partner_id"])
    },
    {
        "name": "contacts_create",
        "category": "Contactos",
        "description": "Crear un nuevo contacto, cliente o empresa con número de RUC o DNI y dirección.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Razón social o nombre completo"},
                "email": {"type": "string", "description": "Correo electrónico"},
                "phone": {"type": "string", "description": "Teléfono o celular"},
                "vat": {"type": "string", "description": "Número de documento fiscal (RUC / DNI)"},
                "is_company": {"type": "boolean", "default": False},
                "street": {"type": "string", "description": "Dirección"},
                "city": {"type": "string", "description": "Ciudad / Distrito"},
                "is_customer": {"type": "boolean", "default": True},
                "is_supplier": {"type": "boolean", "default": False},
                "comment": {"type": "string", "description": "Notas internas"}
            },
            "required": ["name"]
        },
        "func": lambda args: ContactsService.create_contact(
            name=args["name"],
            email=args.get("email"),
            phone=args.get("phone"),
            vat=args.get("vat"),
            is_company=args.get("is_company", False),
            street=args.get("street"),
            city=args.get("city"),
            is_customer=args.get("is_customer", True),
            is_supplier=args.get("is_supplier", False),
            comment=args.get("comment")
        )
    },
    {
        "name": "contacts_update",
        "category": "Contactos",
        "description": "Actualizar datos de un contacto existente (nombre, teléfono, correo, RUC, dirección, notas).",
        "parameters": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "integer", "description": "ID del contacto"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "vat": {"type": "string"},
                "street": {"type": "string"},
                "city": {"type": "string"},
                "comment": {"type": "string"}
            },
            "required": ["partner_id"]
        },
        "func": lambda args: ContactsService.update_contact(
            partner_id=args["partner_id"],
            values={k: v for k, v in args.items() if k != "partner_id" and v is not None}
        )
    },

    # --- Projects & Tasks ---
    {
        "name": "projects_list",
        "category": "Proyectos",
        "description": "Listar proyectos activos con conteo de tareas.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {"type": "string", "description": "Nombre del proyecto"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": []
        },
        "func": lambda args: ProjectsService.list_projects(
            search_term=args.get("search_term"),
            limit=args.get("limit", 20)
        )
    },
    {
        "name": "projects_get_project",
        "category": "Proyectos",
        "description": "Obtener detalles completos de un proyecto específico.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "ID del proyecto"}
            },
            "required": ["project_id"]
        },
        "func": lambda args: ProjectsService.get_project(project_id=args["project_id"])
    },
    {
        "name": "projects_create_project",
        "category": "Proyectos",
        "description": "Crear un nuevo proyecto en Odoo.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre del proyecto"},
                "partner_id": {"type": "integer", "description": "ID del cliente vinculado (opcional)"},
                "user_id": {"type": "integer", "description": "ID del gerente o responsable del proyecto (opcional)"},
                "description": {"type": "string", "description": "Descripción o alcance del proyecto"},
                "date_start": {"type": "string", "description": "Fecha de inicio (YYYY-MM-DD)"},
                "date": {"type": "string", "description": "Fecha de finalización (YYYY-MM-DD)"}
            },
            "required": ["name"]
        },
        "func": lambda args: ProjectsService.create_project(
            name=args["name"],
            partner_id=args.get("partner_id"),
            user_id=args.get("user_id"),
            description=args.get("description"),
            date_start=args.get("date_start"),
            date=args.get("date")
        )
    },
    {
        "name": "projects_update_project",
        "category": "Proyectos",
        "description": "Actualizar campos de un proyecto existente (nombre, responsable, fechas, descripción).",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "ID del proyecto"},
                "name": {"type": "string"},
                "partner_id": {"type": "integer"},
                "user_id": {"type": "integer"},
                "description": {"type": "string"},
                "date_start": {"type": "string"},
                "date": {"type": "string"}
            },
            "required": ["project_id"]
        },
        "func": lambda args: ProjectsService.update_project(
            project_id=args["project_id"],
            values={k: v for k, v in args.items() if k != "project_id" and v is not None}
        )
    },
    {
        "name": "projects_list_tasks",
        "category": "Proyectos",
        "description": "Listar tareas por proyecto, responsable o estado de cierre.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "ID del proyecto"},
                "search_term": {"type": "string", "description": "Nombre de la tarea"},
                "user_id": {"type": "integer", "description": "ID del usuario asignado"},
                "is_closed": {"type": "boolean", "description": "True para tareas finalizadas, False para abiertas"},
                "limit": {"type": "integer", "default": 25}
            },
            "required": []
        },
        "func": lambda args: ProjectsService.list_tasks(
            project_id=args.get("project_id"),
            search_term=args.get("search_term"),
            user_id=args.get("user_id"),
            is_closed=args.get("is_closed"),
            limit=args.get("limit", 25)
        )
    },
    {
        "name": "projects_get_task",
        "category": "Proyectos",
        "description": "Obtener los datos detallados de una tarea con su descripción completa.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID de la tarea"}
            },
            "required": ["task_id"]
        },
        "func": lambda args: ProjectsService.get_task(task_id=args["task_id"])
    },
    {
        "name": "projects_create_task",
        "category": "Proyectos",
        "description": "Crear una nueva tarea en un proyecto o to-do personal.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Título de la tarea"},
                "project_id": {"type": "integer", "description": "ID del proyecto (opcional)"},
                "user_ids": {"type": "array", "items": {"type": "integer"}, "description": "IDs de los usuarios asignados"},
                "description": {"type": "string", "description": "Descripción o requerimientos de la tarea"},
                "date_deadline": {"type": "string", "description": "Fecha límite (YYYY-MM-DD)"},
                "priority": {"type": "string", "enum": ["0", "1"], "default": "0"}
            },
            "required": ["name"]
        },
        "func": lambda args: ProjectsService.create_task(
            name=args["name"],
            project_id=args.get("project_id"),
            user_ids=args.get("user_ids"),
            description=args.get("description"),
            date_deadline=args.get("date_deadline"),
            priority=args.get("priority", "0")
        )
    },
    {
        "name": "projects_update_task",
        "category": "Proyectos",
        "description": "Actualizar propiedades de una tarea (etapa, fecha límite, prioridad, asignados o descripción).",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID de la tarea"},
                "name": {"type": "string"},
                "stage_id": {"type": "integer"},
                "description": {"type": "string"},
                "date_deadline": {"type": "string"},
                "priority": {"type": "string", "enum": ["0", "1"]}
            },
            "required": ["task_id"]
        },
        "func": lambda args: ProjectsService.update_task(
            task_id=args["task_id"],
            values={k: v for k, v in args.items() if k != "task_id" and v is not None}
        )
    },

    # --- HR & Employees ---
    {
        "name": "hr_list_employees",
        "category": "Recursos Humanos",
        "description": "Listar colaboradores con su departamento, cargo, correo y teléfono laboral.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {"type": "string", "description": "Nombre o correo del colaborador"},
                "department_id": {"type": "integer", "description": "ID del departamento"},
                "limit": {"type": "integer", "default": 25}
            },
            "required": []
        },
        "func": lambda args: HRService.list_employees(
            search_term=args.get("search_term"),
            department_id=args.get("department_id"),
            limit=args.get("limit", 25)
        )
    },
    {
        "name": "hr_get_employee",
        "category": "Recursos Humanos",
        "description": "Obtener la ficha completa de un colaborador.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer", "description": "ID del empleado"}
            },
            "required": ["employee_id"]
        },
        "func": lambda args: HRService.get_employee(employee_id=args["employee_id"])
    },
    {
        "name": "hr_create_employee",
        "category": "Recursos Humanos",
        "description": "Crear un nuevo empleado / colaborador en Odoo.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre completo del colaborador"},
                "job_title": {"type": "string", "description": "Puesto o cargo"},
                "work_email": {"type": "string", "description": "Correo corporativo"},
                "work_phone": {"type": "string", "description": "Teléfono corporativo"},
                "mobile_phone": {"type": "string", "description": "Celular"},
                "department_id": {"type": "integer", "description": "ID del departamento"},
                "parent_id": {"type": "integer", "description": "ID del gerente o supervisor directo"}
            },
            "required": ["name"]
        },
        "func": lambda args: HRService.create_employee(
            name=args["name"],
            job_title=args.get("job_title"),
            work_email=args.get("work_email"),
            work_phone=args.get("work_phone"),
            mobile_phone=args.get("mobile_phone"),
            department_id=args.get("department_id"),
            parent_id=args.get("parent_id")
        )
    },
    {
        "name": "hr_update_employee",
        "category": "Recursos Humanos",
        "description": "Actualizar campos de un empleado (cargo, departamento, supervisor, teléfonos, correo).",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer", "description": "ID del empleado"},
                "name": {"type": "string"},
                "job_title": {"type": "string"},
                "work_email": {"type": "string"},
                "work_phone": {"type": "string"},
                "mobile_phone": {"type": "string"},
                "department_id": {"type": "integer"},
                "parent_id": {"type": "integer"}
            },
            "required": ["employee_id"]
        },
        "func": lambda args: HRService.update_employee(
            employee_id=args["employee_id"],
            values={k: v for k, v in args.items() if k != "employee_id" and v is not None}
        )
    },
    {
        "name": "hr_list_departments",
        "category": "Recursos Humanos",
        "description": "Listar los departamentos de la empresa con conteo de empleados.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "func": lambda args: HRService.list_departments()
    },
    {
        "name": "hr_get_department",
        "category": "Recursos Humanos",
        "description": "Obtener los datos de un departamento específico.",
        "parameters": {
            "type": "object",
            "properties": {
                "department_id": {"type": "integer", "description": "ID del departamento"}
            },
            "required": ["department_id"]
        },
        "func": lambda args: HRService.get_department(department_id=args["department_id"])
    },
    {
        "name": "hr_create_department",
        "category": "Recursos Humanos",
        "description": "Crear un nuevo departamento en la empresa.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre del departamento"},
                "manager_id": {"type": "integer", "description": "ID del empleado gerente (opcional)"},
                "parent_id": {"type": "integer", "description": "ID del departamento padre (opcional)"}
            },
            "required": ["name"]
        },
        "func": lambda args: HRService.create_department(
            name=args["name"],
            manager_id=args.get("manager_id"),
            parent_id=args.get("parent_id")
        )
    },
    {
        "name": "hr_update_department",
        "category": "Recursos Humanos",
        "description": "Actualizar campos de un departamento.",
        "parameters": {
            "type": "object",
            "properties": {
                "department_id": {"type": "integer", "description": "ID del departamento"},
                "name": {"type": "string"},
                "manager_id": {"type": "integer"},
                "parent_id": {"type": "integer"}
            },
            "required": ["department_id"]
        },
        "func": lambda args: HRService.update_department(
            department_id=args["department_id"],
            values={k: v for k, v in args.items() if k != "department_id" and v is not None}
        )
    },

    # --- Activities & Calendar ---
    {
        "name": "activities_list",
        "category": "Agenda",
        "description": "Listar actividades programadas (llamadas, reuniones, correos, to-dos) en cualquier modelo de Odoo.",
        "parameters": {
            "type": "object",
            "properties": {
                "res_model": {"type": "string", "description": "Modelo (ej. 'crm.lead', 'sale.order', 'res.partner')"},
                "res_id": {"type": "integer", "description": "ID del registro vinculado"},
                "user_id": {"type": "integer", "description": "ID del usuario responsable"},
                "limit": {"type": "integer", "default": 25}
            },
            "required": []
        },
        "func": lambda args: ActivitiesCalendarService.list_activities(
            res_model=args.get("res_model"),
            res_id=args.get("res_id"),
            user_id=args.get("user_id"),
            limit=args.get("limit", 25)
        )
    },
    {
        "name": "activities_create",
        "category": "Agenda",
        "description": "Programar una nueva actividad (llamada, correo, tarea) vinculada a un registro de Odoo.",
        "parameters": {
            "type": "object",
            "properties": {
                "res_model": {"type": "string", "description": "Modelo técnico (ej. 'crm.lead', 'res.partner')"},
                "res_id": {"type": "integer", "description": "ID del registro a vincular"},
                "summary": {"type": "string", "description": "Título o resumen de la actividad"},
                "date_deadline": {"type": "string", "description": "Fecha límite (YYYY-MM-DD)"},
                "note": {"type": "string", "description": "Detalles o notas"},
                "activity_type_id": {"type": "integer", "description": "ID del tipo de actividad"}
            },
            "required": ["res_model", "res_id", "summary", "date_deadline"]
        },
        "func": lambda args: ActivitiesCalendarService.create_activity(
            res_model=args["res_model"],
            res_id=args["res_id"],
            summary=args["summary"],
            date_deadline=args["date_deadline"],
            note=args.get("note"),
            activity_type_id=args.get("activity_type_id")
        )
    },
    {
        "name": "activities_update",
        "category": "Agenda",
        "description": "Actualizar campos de una actividad programada (resumen, fecha límite, notas).",
        "parameters": {
            "type": "object",
            "properties": {
                "activity_id": {"type": "integer", "description": "ID de la actividad"},
                "summary": {"type": "string", "description": "Nuevo resumen"},
                "date_deadline": {"type": "string", "description": "Nueva fecha límite (YYYY-MM-DD)"},
                "note": {"type": "string", "description": "Nuevas notas"},
                "user_id": {"type": "integer", "description": "ID del nuevo usuario asignado"}
            },
            "required": ["activity_id"]
        },
        "func": lambda args: ActivitiesCalendarService.update_activity(
            activity_id=args["activity_id"],
            values={k: v for k, v in args.items() if k != "activity_id" and v is not None}
        )
    },
    {
        "name": "activities_mark_done",
        "category": "Agenda",
        "description": "Marcar una actividad como completada y opcionalmente registrar feedback.",
        "parameters": {
            "type": "object",
            "properties": {
                "activity_id": {"type": "integer", "description": "ID de la actividad"},
                "feedback": {"type": "string", "description": "Comentario de lo ocurrido o resultado"}
            },
            "required": ["activity_id"]
        },
        "func": lambda args: ActivitiesCalendarService.mark_activity_done(
            activity_id=args["activity_id"],
            feedback=args.get("feedback")
        )
    },
    {
        "name": "calendar_list_meetings",
        "category": "Agenda",
        "description": "Listar reuniones y eventos agendados en el calendario de Odoo.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Desde fecha (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Hasta fecha (YYYY-MM-DD)"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": []
        },
        "func": lambda args: ActivitiesCalendarService.list_calendar_events(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            limit=args.get("limit", 20)
        )
    },
    {
        "name": "calendar_get_meeting",
        "category": "Agenda",
        "description": "Obtener los datos detallados de una reunión o evento del calendario.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "integer", "description": "ID del evento de calendario"}
            },
            "required": ["event_id"]
        },
        "func": lambda args: ActivitiesCalendarService.get_calendar_event(event_id=args["event_id"])
    },
    {
        "name": "calendar_create_meeting",
        "category": "Agenda",
        "description": "Crear una nueva reunión en el calendario de Odoo con fecha y participantes.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Título de la reunión"},
                "start": {"type": "string", "description": "Inicio (YYYY-MM-DD HH:MM:SS)"},
                "stop": {"type": "string", "description": "Fin (YYYY-MM-DD HH:MM:SS)"},
                "partner_ids": {"type": "array", "items": {"type": "integer"}, "description": "IDs de los contactos asistentes"},
                "description": {"type": "string", "description": "Agenda o descripción"},
                "location": {"type": "string", "description": "Lugar o enlace de reunión (Meet, Zoom)"}
            },
            "required": ["name", "start", "stop"]
        },
        "func": lambda args: ActivitiesCalendarService.create_calendar_event(
            name=args["name"],
            start=args["start"],
            stop=args["stop"],
            partner_ids=args.get("partner_ids"),
            description=args.get("description"),
            location=args.get("location")
        )
    },
    {
        "name": "calendar_update_meeting",
        "category": "Agenda",
        "description": "Actualizar una reunión en el calendario (título, fechas de inicio/fin, ubicación, asistentes o descripción).",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "integer", "description": "ID del evento de calendario"},
                "name": {"type": "string", "description": "Nuevo título"},
                "start": {"type": "string", "description": "Nuevo inicio (YYYY-MM-DD HH:MM:SS)"},
                "stop": {"type": "string", "description": "Nuevo fin (YYYY-MM-DD HH:MM:SS)"},
                "partner_ids": {"type": "array", "items": {"type": "integer"}, "description": "Lista de IDs de asistentes"},
                "description": {"type": "string", "description": "Nueva descripción"},
                "location": {"type": "string", "description": "Nueva ubicación o link"}
            },
            "required": ["event_id"]
        },
        "func": lambda args: ActivitiesCalendarService.update_calendar_event(
            event_id=args["event_id"],
            values={k: v for k, v in args.items() if k != "event_id" and v is not None}
        )
    },

    # --- Theme & Branding ---
    {
        "name": "theme_get_branding",
        "category": "Tema & Branding",
        "description": "Consultar los colores corporativos actuales (primario, secundario), tipografía y configuración de marca del ERP.",
        "parameters": {
            "type": "object",
            "properties": {
                "company_id": {"type": "integer", "default": 1}
            },
            "required": []
        },
        "func": lambda args: ThemeService.get_branding(company_id=args.get("company_id", 1))
    },
    {
        "name": "theme_update_branding",
        "category": "Tema & Branding",
        "description": "Actualizar colores corporativos (primario, secundario), tipografía o razón social de la empresa en Odoo.",
        "parameters": {
            "type": "object",
            "properties": {
                "company_id": {"type": "integer", "default": 1},
                "primary_color": {"type": "string", "description": "Color primario en formato Hex (ej. '#0EA5E9' o '#427293')"},
                "secondary_color": {"type": "string", "description": "Color secundario en formato Hex (ej. '#092D53')"},
                "font": {"type": "string", "description": "Tipografía (ej. 'Lato', 'Roboto', 'Inter', 'Montserrat')"},
                "name": {"type": "string", "description": "Nombre o razón social de la empresa"}
            },
            "required": []
        },
        "func": lambda args: ThemeService.update_branding(
            company_id=args.get("company_id", 1),
            primary_color=args.get("primary_color"),
            secondary_color=args.get("secondary_color"),
            font=args.get("font"),
            name=args.get("name")
        )
    },
    {
        "name": "theme_set_navbar_theme",
        "category": "Tema & Branding",
        "description": "Personalizar y aplicar un tema visual para la barra superior (navbar) del administrador de Odoo 20 con degradados y acentos.",
        "parameters": {
            "type": "object",
            "properties": {
                "navbar_bg_start": {"type": "string", "description": "Color inicial del degradado del navbar (ej. '#092D53')", "default": "#092D53"},
                "navbar_bg_end": {"type": "string", "description": "Color final del degradado del navbar (ej. '#1E3A8A')", "default": "#1E3A8A"},
                "navbar_text_color": {"type": "string", "description": "Color de texto y menús (ej. '#FFFFFF')", "default": "#FFFFFF"},
                "primary_accent": {"type": "string", "description": "Color de acento y botones principales (ej. '#0EA5E9')", "default": "#0EA5E9"}
            },
            "required": []
        },
        "func": lambda args: ThemeService.set_navbar_theme(
            navbar_bg_start=args.get("navbar_bg_start", "#092D53"),
            navbar_bg_end=args.get("navbar_bg_end", "#1E3A8A"),
            navbar_text_color=args.get("navbar_text_color", "#FFFFFF"),
            primary_accent=args.get("primary_accent", "#0EA5E9")
        )
    },
    {
        "name": "theme_remove_custom_css",
        "category": "Tema & Branding",
        "description": "Desactivar el tema visual personalizado y restaurar los estilos estándar de Odoo 20.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "func": lambda args: ThemeService.remove_custom_css()
    },
    {
        "name": "theme_list_fonts",
        "category": "Tema & Branding",
        "description": "Listar tipografías corporativas recomendadas para Odoo.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "func": lambda args: ThemeService.list_available_fonts()
    }
]

# Quick lookup map by tool name
TOOLS_BY_NAME: Dict[str, Dict[str, Any]] = {t["name"]: t for t in TOOLS_DEFINITIONS}

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Executes a registered tool by name with provided arguments."""
    tool = TOOLS_BY_NAME.get(tool_name)
    if not tool:
        raise ValueError(f"Tool '{tool_name}' is not registered.")
    return tool["func"](arguments)

def get_openai_tools_schema() -> List[Dict[str, Any]]:
    """Returns OpenAI/Gemini compatible tools format."""
    schemas = []
    for t in TOOLS_DEFINITIONS:
        schemas.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"]
            }
        })
    return schemas
