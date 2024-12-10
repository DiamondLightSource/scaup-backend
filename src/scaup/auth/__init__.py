import importlib

from lims_utils.auth import CookieOrHTTPBearer, GenericUser

from ..utils.config import Config
from .template import GenericPermissions

auth_type = Config.auth.type.lower()
auth_scheme = CookieOrHTTPBearer(cookie_key=Config.auth.cookie_key)

_current_auth = importlib.import_module("scaup.auth." + auth_type)

_Permissions = _current_auth.Permissions
_User = _current_auth.User

assert issubclass(_Permissions, GenericPermissions)
assert issubclass(_User, GenericUser)

Permissions: GenericPermissions = _Permissions
User: GenericUser = _User
