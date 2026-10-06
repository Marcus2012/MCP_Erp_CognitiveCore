import ssl
import logging
import threading
import xmlrpc.client
from typing import Any, Dict, List, Optional, Union
from config import Config

logger = logging.getLogger("CognitiveERP.OdooClient")

class OdooClient:
    """Thread-safe client wrapper for Odoo 20 XML-RPC API."""
    
    _instance: Optional["OdooClient"] = None
    _init_lock = threading.Lock()

    def __init__(self):
        self.url = Config.ODOO_URL.rstrip("/")
        self.db = Config.ODOO_DB
        self.email = Config.ODOO_EMAIL
        self.credential = Config.get_credential()
        self.uid: Optional[int] = None
        self._lock = threading.Lock()
        
        # SSL Context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    @classmethod
    def get_instance(cls) -> "OdooClient":
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = OdooClient()
        return cls._instance

    def _get_common_proxy(self) -> xmlrpc.client.ServerProxy:
        return xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common", 
            context=self.ssl_context,
            allow_none=True
        )

    def _get_object_proxy(self) -> xmlrpc.client.ServerProxy:
        return xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object", 
            context=self.ssl_context,
            allow_none=True
        )

    def authenticate(self, force_refresh: bool = False) -> int:
        """Authenticates with Odoo using API key or Password (thread-safe)."""
        if self.uid and not force_refresh:
            return self.uid

        with self._lock:
            if self.uid and not force_refresh:
                return self.uid

            try:
                common = self._get_common_proxy()
                uid = common.authenticate(self.db, self.email, self.credential, {})
                if not uid:
                    # Try fallback to password if api_key was first and vice-versa
                    alt_cred = Config.ODOO_PASSWORD if self.credential == Config.ODOO_API_KEY else Config.ODOO_API_KEY
                    if alt_cred:
                        uid = common.authenticate(self.db, self.email, alt_cred, {})
                        if uid:
                            self.credential = alt_cred

                if not uid:
                    raise ValueError(
                        f"Authentication failed for user '{self.email}' on database '{self.db}' at '{self.url}'"
                    )

                self.uid = uid
                logger.info(f"Successfully authenticated as UID {self.uid}")
                return self.uid
            except Exception as e:
                logger.error(f"Odoo Auth Error: {str(e)}")
                raise

    def execute_kw(self, model: str, method: str, args: List[Any], kwargs: Optional[Dict[str, Any]] = None) -> Any:
        """Executes any Odoo ORM method via XML-RPC with thread-safety and auto-recovery."""
        if kwargs is None:
            kwargs = {}

        uid = self.authenticate()
        
        with self._lock:
            try:
                models = self._get_object_proxy()
                return models.execute_kw(self.db, uid, self.credential, model, method, args, kwargs)
            except xmlrpc.client.Fault as fault:
                # Check for session expiration or auth faults
                if "AccessDenied" in fault.faultString or "Session expired" in fault.faultString:
                    logger.warning("Session expired, re-authenticating...")
                    self.uid = None
                    uid = self.authenticate(force_refresh=True)
                    models = self._get_object_proxy()
                    return models.execute_kw(self.db, uid, self.credential, model, method, args, kwargs)
                logger.error(f"Odoo XML-RPC Fault [{model}.{method}]: {fault.faultString}")
                raise RuntimeError(f"Odoo Error ({model}.{method}): {fault.faultString}")
            except Exception as e:
                logger.error(f"Odoo Execution Error [{model}.{method}]: {str(e)}")
                raise

    def search_read(
        self,
        model: str,
        domain: Optional[List[Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
        order: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches and reads records from Odoo."""
        domain = domain or []
        kwargs: Dict[str, Any] = {"limit": limit, "offset": offset}
        if fields:
            kwargs["fields"] = fields
        if order:
            kwargs["order"] = order
            
        return self.execute_kw(model, "search_read", [domain], kwargs)

    def search_count(self, model: str, domain: Optional[List[Any]] = None) -> int:
        """Counts records matching domain."""
        domain = domain or []
        return self.execute_kw(model, "search_count", [domain])

    def read(self, model: str, ids: Union[int, List[int]], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Reads specific records by ID."""
        record_ids = [ids] if isinstance(ids, int) else ids
        kwargs = {"fields": fields} if fields else {}
        return self.execute_kw(model, "read", [record_ids], kwargs)

    def create(self, model: str, values: Dict[str, Any]) -> int:
        """Creates a new record and returns its ID."""
        return self.execute_kw(model, "create", [values])

    def write(self, model: str, ids: Union[int, List[int]], values: Dict[str, Any]) -> bool:
        """Updates existing record(s)."""
        record_ids = [ids] if isinstance(ids, int) else ids
        return self.execute_kw(model, "write", [record_ids, values])

    def unlink(self, model: str, ids: Union[int, List[int]]) -> bool:
        """Deletes record(s)."""
        record_ids = [ids] if isinstance(ids, int) else ids
        return self.execute_kw(model, "unlink", [record_ids])

    def fields_get(self, model: str, allfields: Optional[List[str]] = None, attributes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Returns metadata definitions for model fields."""
        kwargs = {}
        if allfields:
            kwargs["allfields"] = allfields
        if attributes:
            kwargs["attributes"] = attributes
        return self.execute_kw(model, "fields_get", [], kwargs)

    def get_server_version(self) -> Dict[str, Any]:
        """Returns Odoo server version details."""
        with self._lock:
            common = self._get_common_proxy()
            return common.version()


# Singleton getter
def get_odoo_client() -> OdooClient:
    return OdooClient.get_instance()
