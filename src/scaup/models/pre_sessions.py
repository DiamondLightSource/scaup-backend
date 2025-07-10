from typing import Any, Optional

from pydantic import BaseModel


class BasePreSession(BaseModel):
    details: Optional[dict[str, Any]] = None


class PreSessionIn(BasePreSession):
    pass


class PreSessionOptional(BasePreSession):
    pass


class PreSessionOut(BasePreSession):
    isLocked: bool = False
