from typing import Any, Dict, List, Optional
import base64
from odoo_client import get_odoo_client

class ThemeService:
    """Manages Odoo 20 Backend Branding, Colors, Fonts, and Custom CSS Themes."""

    CUSTOM_VIEW_KEY = "cognitive_core.custom_backend_theme"

    @staticmethod
    def get_branding(company_id: int = 1) -> Dict[str, Any]:
        """Get current company theme, colors, typography, and logo metadata."""
        client = get_odoo_client()
        fields = [
            "id", "name", "primary_color", "secondary_color",
            "email_primary_color", "email_secondary_color",
            "font", "uses_default_logo"
        ]
        companies = client.read("res.company", company_id, fields=fields)
        if not companies:
            raise ValueError(f"Company with ID {company_id} not found.")

        data = companies[0]
        # Check if custom CSS view is currently installed
        custom_views = client.search_read(
            "ir.ui.view",
            domain=[("key", "=", ThemeService.CUSTOM_VIEW_KEY)],
            fields=["id", "name", "active", "arch"],
            limit=1
        )
        data["custom_css_installed"] = len(custom_views) > 0
        data["custom_css_active"] = custom_views[0].get("active", False) if custom_views else False
        return data

    @staticmethod
    def update_branding(
        company_id: int = 1,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        font: Optional[str] = None,
        name: Optional[str] = None,
        logo_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update company branding colors, typography font, name, or logo.
        primary_color / secondary_color format: '#427293' (Hex).
        font options: 'Lato', 'Roboto', 'Open Sans', 'Montserrat', 'Inter', 'Poppins'.
        """
        client = get_odoo_client()
        values: Dict[str, Any] = {}

        if primary_color:
            values["primary_color"] = primary_color
            values["email_primary_color"] = primary_color
        if secondary_color:
            values["secondary_color"] = secondary_color
            values["email_secondary_color"] = secondary_color
        if font:
            values["font"] = font
        if name:
            values["name"] = name
        if logo_base64:
            values["logo"] = logo_base64

        if values:
            client.write("res.company", company_id, values)

        return {
            "status": "updated",
            "company_id": company_id,
            "branding": ThemeService.get_branding(company_id)
        }

    @staticmethod
    def set_navbar_theme(
        navbar_bg_start: str = "#092D53",
        navbar_bg_end: str = "#1E3A8A",
        navbar_text_color: str = "#FFFFFF",
        primary_accent: str = "#0EA5E9"
    ) -> Dict[str, Any]:
        """
        Generate and apply a custom navbar style and theme accents on Odoo 20 backend.
        """
        client = get_odoo_client()
        
        css_rules = f"""
        /* --- Cognitive Core Custom Backend Theme --- */
        
        :root {{
            --Navbar-entry-backgroundColor: rgba(255, 255, 255, 0.12) !important;
            --Navbar-entry-color: {navbar_text_color} !important;
            --o-navbar-bg: {navbar_bg_start} !important;
            --primary: {primary_accent} !important;
        }}

        /* 1. Main Navbar Header */
        .o_main_navbar {{
            --Navbar-entry-backgroundColor: rgba(255, 255, 255, 0.12) !important;
            --Navbar-entry-color: {navbar_text_color} !important;
            background: linear-gradient(135deg, {navbar_bg_start} 0%, {navbar_bg_end} 100%) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.12), 0 2px 4px -1px rgba(0, 0, 0, 0.08) !important;
        }}
        
        /* 2. All Navbar Buttons, Dropdowns & Tabs (Overrides navbar.scss:145) */
        .o_main_navbar .o_nav_entry,
        .o_main_navbar .o_menu_brand,
        .o_main_navbar .o_menu_sections .o_nav_entry,
        .o_main_navbar .o_menu_sections .dropdown-toggle,
        .o_main_navbar .o_menu_sections button,
        .o_main_navbar .o_menu_sections a,
        .o_main_navbar .o_menu_systray .o_nav_entry,
        .o_main_navbar .o_menu_systray .dropdown-toggle,
        .o_main_navbar .o_menu_systray button,
        .o_main_navbar .dropdown-toggle,
        .o_main_navbar button.o-dropdown,
        .o_main_navbar a {{
            background: rgba(255, 255, 255, 0.12) !important;
            background-color: rgba(255, 255, 255, 0.12) !important;
            color: {navbar_text_color} !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 6px !important;
            margin-right: 4px !important;
            font-weight: 500 !important;
        }}

        /* 3. Hover & Active states */
        .o_main_navbar .o_menu_sections .o_nav_entry:hover,
        .o_main_navbar .o_menu_sections .dropdown-toggle:hover,
        .o_main_navbar .o_menu_sections button:hover,
        .o_main_navbar .o_menu_systray .o_nav_entry:hover,
        .o_main_navbar .o_menu_systray .dropdown-toggle:hover,
        .o_main_navbar .o_nav_entry:hover,
        .o_main_navbar .dropdown-toggle:hover {{
            background: rgba(255, 255, 255, 0.25) !important;
            background-color: rgba(255, 255, 255, 0.25) !important;
            color: #FFFFFF !important;
        }}

        .o_main_navbar .o_menu_sections .active,
        .o_main_navbar .o_menu_sections .nav-link.active,
        .o_main_navbar .o_menu_sections .dropdown-toggle.active,
        .o_main_navbar .o_menu_sections .o_nav_entry.active,
        .o_main_navbar .o_menu_sections button[aria-expanded="true"],
        .o_main_navbar .o_menu_sections .dropdown-toggle[aria-expanded="true"] {{
            background: rgba(14, 165, 233, 0.35) !important;
            background-color: rgba(14, 165, 233, 0.35) !important;
            border-color: {primary_accent} !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 8px rgba(14, 165, 233, 0.4) !important;
        }}

        /* 4. User Avatar Icon ('K' Circle) */
        .o_main_navbar .o_user_avatar,
        .o_main_navbar .o_avatar,
        .o_main_navbar .o_user_menu .rounded-circle,
        .o_main_navbar .o_user_menu span.rounded-circle,
        .o_main_navbar span.bg-view-avatar,
        .o_main_navbar div.rounded-circle,
        .o_main_navbar .o_user_menu .o_avatar_badge {{
            background: linear-gradient(135deg, {primary_accent} 0%, #0284C7 100%) !important;
            background-color: {primary_accent} !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            font-weight: bold !important;
        }}

        /* 5. Control Panel & Action Buttons ('Nuevo', 'Guardar', 'Confirmar') */
        .o_control_panel .btn-primary,
        .o_form_button_save,
        .o_list_button_add,
        .btn-primary {{
            background-color: {primary_accent} !important;
            border-color: #0284C7 !important;
            color: #FFFFFF !important;
            font-weight: 500 !important;
            box-shadow: 0 1px 2px rgba(14, 165, 233, 0.3) !important;
        }}
        .o_control_panel .btn-primary:hover,
        .btn-primary:hover {{
            background-color: #0284C7 !important;
            border-color: #0369A1 !important;
        }}

        .o_control_panel .btn-outline-primary,
        .btn-outline-primary,
        .o_control_panel .btn-secondary {{
            color: #0284C7 !important;
            border-color: #BAE6FD !important;
            background-color: #F0F9FF !important;
        }}
        .o_control_panel .btn-outline-primary:hover,
        .btn-outline-primary:hover {{
            background-color: {primary_accent} !important;
            border-color: {primary_accent} !important;
            color: #FFFFFF !important;
        }}

        /* 6. Smart Buttons & Stats ('Documentos', 'Vendido', 'Reglas', 'Entrada') */
        .oe_stat_button,
        .oe_stat_button .o_stat_value,
        .oe_stat_button .o_stat_info,
        .oe_stat_button .o_button_icon,
        .oe_stat_button i,
        .o_stat_text {{
            color: #0369A1 !important;
        }}
        .oe_stat_button:hover {{
            background-color: #F0F9FF !important;
            border-color: #BAE6FD !important;
        }}

        /* 7. Breadcrumbs & Titles */
        .o_control_panel .breadcrumb-item a,
        .o_control_panel .o_breadcrumb .o_back_button,
        .o_control_panel .o_last_breadcrumb_item {{
            color: #0369A1 !important;
        }}

        /* 8. Dropdown menus */
        .dropdown-menu .dropdown-item.active,
        .dropdown-menu .dropdown-item:active {{
            background-color: {primary_accent} !important;
            color: #FFFFFF !important;
        }}
        .dropdown-menu .dropdown-item:hover {{
            background-color: #F0F9FF !important;
            color: #0369A1 !important;
        }}
        """

        # Also update company primary_color for consistency
        ThemeService.update_branding(
            company_id=1,
            primary_color=primary_accent,
            secondary_color=navbar_bg_start
        )

        return ThemeService.inject_custom_css(css_code=css_rules, name="Cognitive Core Navbar Theme")

    @staticmethod
    def inject_custom_css(css_code: str, name: str = "Cognitive Core Backend Theme") -> Dict[str, Any]:
        """Inject custom CSS stylesheet rules into Odoo 20 backend views (web.webclient_bootstrap)."""
        client = get_odoo_client()
        
        clean_css = css_code.replace("&", "&amp;")
        arch_xml = f"""<xpath expr="//t[@t-set='head']" position="inside">
            <style id="cognitive_core_custom_theme">
                {clean_css}
            </style>
        </xpath>"""

        # Find existing custom view or create new one
        existing = client.search_read(
            "ir.ui.view",
            domain=[("key", "=", ThemeService.CUSTOM_VIEW_KEY)],
            fields=["id"]
        )

        if existing:
            view_id = existing[0]["id"]
            client.write("ir.ui.view", view_id, {
                "arch": arch_xml,
                "active": True
            })
            action = "updated"
        else:
            # Find inherit view target (web.webclient_bootstrap, key='web.webclient_bootstrap')
            target_views = client.search_read(
                "ir.ui.view",
                domain=[("key", "=", "web.webclient_bootstrap")],
                fields=["id"],
                limit=1
            )
            inherit_id = target_views[0]["id"] if target_views else 197

            view_values = {
                "name": name,
                "key": ThemeService.CUSTOM_VIEW_KEY,
                "type": "qweb",
                "inherit_id": inherit_id,
                "arch": arch_xml,
                "active": True,
            }

            view_id = client.create("ir.ui.view", view_values)
            action = "created"

        return {
            "status": "success",
            "action": action,
            "view_id": view_id,
            "message": "Custom theme styles successfully applied to Odoo backend."
        }

    @staticmethod
    def remove_custom_css() -> Dict[str, Any]:
        """Disable or remove custom injected theme CSS."""
        client = get_odoo_client()
        existing = client.search_read(
            "ir.ui.view",
            domain=[("key", "=", ThemeService.CUSTOM_VIEW_KEY)],
            fields=["id"]
        )
        if existing:
            client.write("ir.ui.view", existing[0]["id"], {"active": False})
            return {"status": "disabled", "message": "Custom theme styles disabled."}
        return {"status": "not_found", "message": "No custom CSS view found."}

    @staticmethod
    def list_available_fonts() -> List[str]:
        """Returns recommended fonts for Odoo."""
        return ["Lato", "Roboto", "Open Sans", "Montserrat", "Inter", "Poppins", "Helvetica", "Arial"]
