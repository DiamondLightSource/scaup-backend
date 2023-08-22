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


@dataclass
class DB:
    pool: int = 10
    overflow: int = 20


class Config:
    auth: Auth
    ispyb_api: str
    db: DB

    @staticmethod
    def set():
        try:
            with open(os.environ.get("CONFIG_PATH") or "config.json", "r") as fp:
                conf = json.load(fp)
                Config.auth = Auth(**conf["auth"])
                Config.db = DB(**conf["db"])
                Config.ispyb_api = conf["ispyb_api"]

        except (FileNotFoundError, TypeError) as exc:
            raise ConfigurationError(str(exc).replace(".__init__()", "")) from exc
        except KeyError as exc:
            msg = str(exc)
            if msg.isupper():
                raise ConfigurationError(f"Environment variable {str(exc)} is missing")
            else:
                raise ConfigurationError(
                    f"Key {str(exc)} missing from configuration file"
                )
