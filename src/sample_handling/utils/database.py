import contextlib
import contextvars
from typing import Generator, Generic, Optional, TypeVar

import sqlalchemy.orm
from fastapi import HTTPException, status
from ispyb.models import Base
from pydantic import BaseModel
from sqlalchemy import Select, func, literal_column, select

from .session import _inner_session as innersession

_inner_session = contextvars.ContextVar("_inner_session", default=None)


class InnerDatabase:
    @classmethod
    def set_session(cls, session):
        _inner_session.set(session)

    @property
    def session(cls) -> sqlalchemy.orm.Session:
        try:
            current_session = _inner_session.get()
            if current_session is None:
                raise AttributeError
            return current_session
        except (AttributeError, LookupError):
            raise Exception(
                "Can't get session. Please call IspybDatabase.set_session()"
            )


inner_db = InnerDatabase()


@contextlib.contextmanager
def get_session() -> Generator[sqlalchemy.orm.Session, None, None]:
    inner_db_session = innersession()
    try:
        InnerDatabase.set_session(inner_db_session)
        yield inner_db_session
    except Exception:
        inner_db_session.rollback()
        raise
    finally:
        InnerDatabase.set_session(None)
        inner_db_session.close()


T = TypeVar("T")


class Paged(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


def fast_count(query: Select) -> int:
    return inner_db.session.execute(
        query.with_only_columns(func.count(literal_column("1"))).order_by(None)
    ).scalar_one()


def paginate(
    query: Select,
    items: int,
    page: int,
    slow_count=True,
    precounted_total: Optional[int] = None,
):
    """Paginate a query before querying ISPyB"""
    if precounted_total is not None:
        total = precounted_total
    elif slow_count:
        total = inner_db.session.execute(
            select(func.count(literal_column("1"))).select_from(query.subquery())
        ).scalar_one()
    else:
        total = fast_count(query)

    if not total:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No items found",
        )

    if page < 0:
        page = (total // items) + page

    data = inner_db.session.execute(query.limit(items).offset((page) * items)).all()

    return Paged(items=data, total=total, limit=items, page=page)


def unravel(model: Base):
    return [c for c in model.__table__.columns]
