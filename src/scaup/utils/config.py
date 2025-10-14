import json
import os
from dataclasses import dataclass, field
from typing import Literal


class ConfigurationError(Exception):
    pass


@dataclass
class IspybApi:
    url: str
    jwt: str


@dataclass
class Auth:
    jwt_public: str
    jwt_private: str
    endpoint: str = "https://localhost/auth"
    type: Literal["dummy", "micro"] = "micro"
    cookie_key: str = "cookie_key"
    cors: bool = False
    read_all_perms: list[str] = field(default_factory=lambda: ["super_admin"])


@dataclass
class DB:
    pool: int = 10
    overflow: int = 20


@dataclass
class ShippingService:
    frontend_url: str = "https://localtest.diamond.ac.uk/"
    backend_url: str = "https://localtest.diamond.ac.uk/"
    secret: str = "no-secret"
    callback_url: str = "https://localhost/api"


@dataclass
class Alerts:
    smtp_server: str
    smtp_port: str
    local_contacts: dict[str, str]
    contact_email: str | None = None


def _read_config():
    with open(os.environ.get("CONFIG_PATH") or "config.json", "r") as fp:
        conf = json.load(fp)

    return conf


class Config:
    auth: Auth
    frontend_url: str
    db: DB
    shipping_service: ShippingService
    ispyb_api: IspybApi
    alerts: Alerts

    @staticmethod
    def set():
        try:
            conf = _read_config()
            Config.auth = Auth(
                **conf["auth"],
                jwt_public=os.environ.get("SCAUP_PUBLIC_KEY"),
                jwt_private=os.environ.get("SCAUP_PRIVATE_KEY"),
            )
            Config.db = DB(**conf["db"])
            Config.ispyb_api = IspybApi(url=conf["ispyb_api"], jwt=os.environ.get("SCAUP_EXPEYE_TOKEN"))
            Config.frontend_url = conf["frontend_url"]
            Config.shipping_service = ShippingService(**conf["shipping_service"])
            Config.alerts = Alerts(**conf["alerts"])

        except TypeError as exc:
            raise ConfigurationError(str(exc).replace(".__init__()", "")) from exc
        except KeyError as exc:
            msg = str(exc)
            if msg.isupper():
                raise ConfigurationError(f"Environment variable {str(exc)} is missing")
            else:
                raise ConfigurationError(f"Key {str(exc)} missing from configuration file")
