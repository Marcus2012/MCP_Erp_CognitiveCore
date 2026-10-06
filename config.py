import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    """Odoo Connection and MCP Configuration."""
    ODOO_URL: str = os.getenv("ODOO_URL") or os.getenv("domain") or "https://erp.cognitivecore.pe"
    ODOO_DB: str = os.getenv("ODOO_DB") or os.getenv("db") or "erp_cognitivecore"
    ODOO_EMAIL: str = os.getenv("ODOO_EMAIL") or os.getenv("email_mcp") or "datadriven111@gmail.com"
    ODOO_API_KEY: str = os.getenv("ODOO_API_KEY") or os.getenv("api_key") or ""
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD") or os.getenv("password_mcp") or ""
    
    # Server metadata
    SERVER_NAME: str = "Cognitive ERP MCP"
    SERVER_VERSION: str = "1.0.0"
    
    @classmethod
    def get_credential(cls) -> str:
        """Returns API key if present, otherwise password."""
        return cls.ODOO_API_KEY if cls.ODOO_API_KEY else cls.ODOO_PASSWORD

    @classmethod
    def validate(cls) -> bool:
        """Checks if minimal required settings are present."""
        if not cls.ODOO_URL or not cls.ODOO_DB or not cls.ODOO_EMAIL or not cls.get_credential():
            return False
        return True
