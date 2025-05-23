"""
Pagination module for DCApiX.

This module provides classes for handling different pagination strategies
used by API endpoints.
"""

from collections.abc import Callable, Iterator
from typing import Any, Optional, TypeVar

from .base import BasePaginator, PaginationConfig
from .cursor import CursorPaginator
from .link import LinkHeaderPaginator
from .offset import OffsetPaginator
from .page import PagePaginator

__all__ = [
    "BasePaginator",
    "PaginationConfig",
    "OffsetPaginator",
    "CursorPaginator",
    "LinkHeaderPaginator",
    "PagePaginator",
    "get_paginator",
    "paginate",
]

T = TypeVar("T")


def get_paginator(
    client: Any,
    endpoint: str,
    model_class: Optional[type[T]] = None,
    config: Optional[PaginationConfig] = None,
    strategy: str = "offset",
) -> BasePaginator[T]:
    """
    Get an appropriate paginator based on the strategy.

    Args:
        client: API client
        endpoint: API endpoint
        model_class: Optional model class for response items
        config: Pagination configuration
        strategy: Pagination strategy (offset, page, cursor, link)

    Returns:
        Configured paginator instance

    Raises:
        ValueError: If the strategy is not supported
    """
    if strategy == "offset":
        from .offset import OffsetPaginator

        return OffsetPaginator(client, endpoint, model_class, config)
    if strategy == "page":
        from .page import PagePaginator

        return PagePaginator(client, endpoint, model_class, config)
    if strategy == "cursor":
        from .cursor import CursorPaginator

        return CursorPaginator(client, endpoint, model_class, config)
    if strategy == "link":
        from .link import LinkHeaderPaginator

        return LinkHeaderPaginator(client, endpoint, model_class, config)
    raise ValueError(f"Unsupported pagination strategy: {strategy}")


def paginate(
    client: Any,
    endpoint: str,
    params: Optional[dict[str, Any]] = None,
    model_class: Optional[type[T]] = None,
    config: Optional[PaginationConfig] = None,
    strategy: str = "offset",
    transform_func: Optional[Callable[[Any], T]] = None,
) -> Iterator[T]:
    """
    Paginate through API results.

    Args:
        client: API client
        endpoint: API endpoint
        params: Optional request parameters
        model_class: Optional model class for response items
        config: Pagination configuration
        strategy: Pagination strategy (offset, page, cursor, link)
        transform_func: Optional function to transform each item

    Returns:
        Iterator yielding items from paginated results

    Raises:
        ValueError: If the strategy is not supported
    """
    paginator = get_paginator(client, endpoint, model_class, config, strategy)
    return paginator.paginate(params, transform_func)
