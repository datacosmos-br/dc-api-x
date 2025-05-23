"""
Pagination utilities for DCApiX.

This module provides utilities for handling paginated API responses.
"""

from collections.abc import Generator
from typing import Any, Type, TypeVar, cast

from pydantic import BaseModel

from dc_api_x.client import ApiClient

# Define a generic type for models
T = TypeVar("T", bound=BaseModel)

# Error message constants
PAGINATION_FAILED = "Pagination failed: {}"
MISSING_DATA_KEY = "Response does not contain '{}' key"
NOT_A_LIST_ERROR = "Response data is not a list"


def paginate(
    client: ApiClient,
    endpoint: str,
    model_class: Type[BaseModel] | None = None,
    page_param: str = "page",
    page_size_param: str = "per_page",
    page_size: int = 100,
    max_pages: int | None = None,
    data_key: str | None = None,
    params: dict[str, Any] | None = None,
) -> Generator[dict[str, Any] | BaseModel, None, None]:
    """
    Paginate through API results.

    This function handles pagination by making multiple requests and
    yielding each item in the response.

    Args:
        client: API client
        endpoint: API endpoint
        model_class: Optional model class for response items
        page_param: Name of the page parameter
        page_size_param: Name of the page size parameter
        page_size: Number of items per page
        max_pages: Maximum number of pages to retrieve
        data_key: Key for data in response (None if response is array)
        params: Additional query parameters

    Yields:
        Each item in the paginated response
    """
    # Initialize parameters
    query_params = params.copy() if params else {}
    query_params[page_size_param] = page_size
    page = 1

    while True:
        # Set current page
        query_params[page_param] = page

        # Make request
        response = client.get(endpoint, params=query_params)

        # Check for errors
        if not response.success:
            error_message = str(response.error) if response.error else "Unknown error"
            raise RuntimeError(PAGINATION_FAILED.format(error_message))

        # Extract data
        response_data = response.data or {}
        
        if data_key:
            # Data is nested under a key
            if not isinstance(response_data, dict) or data_key not in response_data:
                raise ValueError(MISSING_DATA_KEY.format(data_key))
            items = response_data[data_key]
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
                # Convert to model (handle model_validate and model_construct for different pydantic versions)
                if hasattr(model_class, "model_validate"):
                    yield model_class.model_validate(item)
                else:
                    # Fallback for older pydantic versions
                    yield model_class(**item)
            else:
                # Yield raw item
                yield item

        # Check if we've reached max pages
        if max_pages and page >= max_pages:
            break

        # Check if we've reached the last page
        if len(items) < page_size:
            break

        # Move to next page
        page += 1
