import importlib

from expeye_utils.auth import CookieOrHTTPBearer

from ..utils.config import Config
from .template import GenericPermissions

auth_type = Config.auth.type.lower()
auth_scheme = CookieOrHTTPBearer(cookie_key=Config.auth.cookie_key)

_Permissions = importlib.import_module("sample_handling.auth." + auth_type).Permissions

assert issubclass(_Permissions, GenericPermissions)

Permissions: GenericPermissions = _Permissions
