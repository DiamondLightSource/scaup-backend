import json
import os
from dataclasses import dataclass
from typing import Literal


class ConfigurationError(Exception):
    pass


@dataclass
class Auth:
    endpoint: str = "https://localhost/auth"
    type: Literal["dummy", "micro"] = "micro"
    cookie_key: str = "cookie_key"
    cors: bool = False


@dataclass
class DB:
    pool: int = 10
    overflow: int = 20


@dataclass
class ShippingService:
    url: str = "https://localtest.diamond.ac.uk/"
    secret: str = "no-secret"
    callback_url: str = "https://localhost/api"


def _read_config():
    with open(os.environ.get("CONFIG_PATH") or "config.json", "r") as fp:
        conf = json.load(fp)

    return conf


class Config:
    auth: Auth
    ispyb_api: str
    frontend_url: str
    db: DB
    shipping_service: ShippingService

    @staticmethod
    def set():
        try:
            conf = _read_config()
            Config.auth = Auth(**conf["auth"])
            Config.db = DB(**conf["db"])
            Config.ispyb_api = conf["ispyb_api"]
            Config.frontend_url = conf["frontend_url"]
            Config.shipping_service = ShippingService(**conf["shipping_service"])

            Config.shipping_service.secret = os.environ.get(
                "SHIPPING_SERVICE_SECRET", "no-secret"
            )

        except TypeError as exc:
            raise ConfigurationError(str(exc).replace(".__init__()", "")) from exc
        except KeyError as exc:
            msg = str(exc)
            if msg.isupper():
                raise ConfigurationError(f"Environment variable {str(exc)} is missing")
            else:
                raise ConfigurationError(
                    f"Key {str(exc)} missing from configuration file"
                )
