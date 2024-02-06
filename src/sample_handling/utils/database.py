from typing import Optional

from fastapi import HTTPException, status
from lims_utils.database import Database
from lims_utils.models import Paged
from sqlalchemy import Select, func, literal_column, select

inner_db = Database()


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
    scalar=True,
):
    """Paginate a query before querying database

    Args:
        query: Original query
        items: Number of items to return per page
        page: Page to access
        slow_count: Count number of total items in a slower, safer manner (useful with GROUP statements)
        precounted_total: Skip count, use this total instead
        scalar: Is query already scalar (use `execute` instead of `scalars` when executing)

    Returns
        Paged representation of query"""

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

    execute_cmd = inner_db.session.execute if scalar else inner_db.session.scalars

    data = execute_cmd(query.limit(items).offset((page) * items)).all()
    return Paged(items=data, total=total, limit=items, page=page)


def unravel(model):
    return list(model.__table__.columns)
