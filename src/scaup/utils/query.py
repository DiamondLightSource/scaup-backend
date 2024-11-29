from typing import Sequence, Tuple

from sqlalchemy import Select

from ..models.inner_db.tables import Container, Sample, TopLevelContainer
from ..models.shipments import GenericItem, GenericItemData
from .database import inner_db


def filter_fields(item: TopLevelContainer | Container | Sample):
    """Removes children fields from item. Useful for only displaying fields with actual data

    Args:
        item: Original item

    Returns:
        Item with filtered fields
    """
    _unwanted_fields = ["samples", "children"]
    return {key: value for [key, value] in item.__dict__.items() if key not in _unwanted_fields}


def query_result_to_object(
    result: Sequence[TopLevelContainer | Container | Sample],
):
    """Coerces query result into tree of generic item objects

    Args:
        result: Query result

    Returns:
        Tree of generic item objects
    """
    parsed_items: list[GenericItem] = []
    for item in result:
        parsed_item = GenericItem(
            id=item.id,
            name=item.name,
            data=GenericItemData(**filter_fields(item)),
        )
        if not isinstance(item, Sample):
            if isinstance(item, Container) and item.samples:
                parsed_item.children = query_result_to_object(item.samples)
            elif item.children:
                parsed_item.children = query_result_to_object(item.children)

        parsed_items.append(parsed_item)

    return parsed_items


def table_query_to_generic(query: Select[Tuple[Sample]] | Select[Tuple[Container]]):
    """Perform queries and convert result to generic items

    Args:
        query: Original query

    Returns:
        Tree of generic item objects
    """
    results: Sequence[Sample | Container] = inner_db.session.scalars(query).unique().all()

    return query_result_to_object(results)
