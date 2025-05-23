"""
Pagination utilities for DCApiX.

This module provides utilities for handling paginated API responses.
"""

from collections.abc import Generator
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel

from dc_api_x.client import ApiClient

# Define a generic type for models
T = TypeVar("T", bound=BaseModel)

# Error message constants
PAGINATION_FAILED = "Pagination failed: {}"
MISSING_DATA_KEY = "Response does not contain '{}' key"
NOT_A_LIST_ERROR = "Response data is not a list"


@dataclass
class PaginationConfig:
    """Configuration for paginating API results."""

    page_param: str = "page"
    page_size_param: str = "per_page"
    page_size: int = 100
    max_pages: int | None = None
    data_key: str | None = None
    params: dict[str, Any] | None = None


def paginate(  # noqa: PLR0912
    client: ApiClient,
    endpoint: str,
    model_class: type[BaseModel] | None = None,
    config: PaginationConfig | None = None,
) -> Generator[dict[str, Any] | BaseModel, None, None]:
    """
    Paginate through API results.

    This function handles pagination by making multiple requests and
    yielding each item in the response.

    Args:
        client: API client
        endpoint: API endpoint
        model_class: Optional model class for response items
        config: Pagination configuration

    Yields:
        Each item in the paginated response
    """
    # Use default config if none provided
    cfg = config or PaginationConfig()

    # Initialize parameters
    query_params = cfg.params.copy() if cfg.params else {}
    query_params[cfg.page_size_param] = cfg.page_size
    page = 1

    while True:
        # Set current page
        query_params[cfg.page_param] = page

        # Make request
        response = client.get(endpoint, params=query_params)

        # Check for errors
        if not response.success:
            error_message = str(response.error) if response.error else "Unknown error"
            raise RuntimeError(PAGINATION_FAILED.format(error_message))

        # Extract data
        response_data = response.data or {}

        if cfg.data_key:
            # Data is nested under a key
            if not isinstance(response_data, dict) or cfg.data_key not in response_data:
                raise ValueError(MISSING_DATA_KEY.format(cfg.data_key))
            items = response_data[cfg.data_key]
        else:
            # Data is directly in response
            items = response_data

        # Ensure items is a list
        if not isinstance(items, list):
            raise TypeError(NOT_A_LIST_ERROR)

        # No more items, we're done
        if not items:
            break

        # Yield each item
        for item in items:
            if model_class:
                # Try to use model_validate if available (Pydantic v2)
                try:
                    if hasattr(model_class, "model_validate"):
                        yield model_class.model_validate(item)
                    else:
                        # Fallback for older pydantic versions or model constructor
                        yield model_class(**item)
                except (ValueError, TypeError) as e:
                    # If instantiation fails, return the raw item as fallback
                    print(f"Warning: Failed to instantiate model: {e}")
                    yield item
            else:
                # Yield raw item
                yield item

        # Check if we've reached max pages
        if cfg.max_pages and page >= cfg.max_pages:
            break

        # Check if we've reached the last page
        if len(items) < cfg.page_size:
            break

        # Move to next page
        page += 1
