"""
Base pagination classes for DCApiX.

This module provides the base classes that all pagination strategies use.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from pydantic import BaseModel

# Use string literals for types to avoid circular imports
if TYPE_CHECKING:
    from dc_api_x.client import ApiClient
    from dc_api_x.models import ApiResponse

# Type variable for entity models
T = TypeVar("T", bound=BaseModel)

# Error message constants
DATA_KEY_ERROR_MSG = "Response does not contain the expected data key"
DATA_TYPE_ERROR_MSG = "Response data is not a list"


@dataclass
class PaginationConfig:
    """Configuration for pagination strategies."""

    # Common configuration options
    page_size: int = 100
    max_pages: Optional[int] = None
    data_key: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)

    # Page number pagination
    page_param: str = "page"
    page_size_param: str = "per_page"

    # Offset pagination
    offset_param: str = "offset"
    limit_param: str = "limit"

    # Cursor pagination
    cursor_param: str = "cursor"
    has_more_key: str = "has_more"
    next_cursor_key: str = "next_cursor"

    # Header-based pagination
    link_header: str = "Link"
    count_header: str = "X-Total-Count"


class BasePaginator(Generic[T], ABC):
    """
    Base class for all pagination strategies.

    This abstract class defines the API that all paginators must implement.
    """

    def __init__(
        self,
        client: "ApiClient",
        endpoint: str,
        model_class: Optional[type[BaseModel]] = None,
        config: Optional[PaginationConfig] = None,
    ):
        """
        Initialize a paginator.

        Args:
            client: The API client to use for requests
            endpoint: The API endpoint to paginate
            model_class: Optional model class for response items
            config: Pagination configuration
        """
        self.client = client
        self.endpoint = endpoint
        self.model_class = model_class
        self.config = config or PaginationConfig()
        self.params = self.config.params.copy() if self.config.params else {}

    @abstractmethod
    def paginate(self) -> Iterator[dict[str, Any] | BaseModel]:
        """
        Paginate through API results.

        This method handles pagination by making multiple requests and
        yielding each item in the response.

        Yields:
            Each item in the paginated response
        """

    def _extract_data(self, response: "ApiResponse") -> list[dict[str, Any]]:
        """
        Extract data from a response.

        This extracts the data list from a response, handling
        nested data if needed.

        Args:
            response: API response

        Returns:
            List of items from the response

        Raises:
            ValueError: If the response doesn't contain the expected data
            TypeError: If the data is not a list
        """
        # Extract data
        response_data = response.data or {}

        if self.config.data_key:
            # Data is nested under a key
            if (
                not isinstance(response_data, dict)
                or self.config.data_key not in response_data
            ):
                missing_key = self.config.data_key
                error_msg = f"Missing key '{missing_key}'. {DATA_KEY_ERROR_MSG}"
                raise ValueError(error_msg)
            items = response_data[self.config.data_key]
        else:
            # Data is directly in response
            items = response_data

        # Ensure items is a list
        if not isinstance(items, list):
            raise TypeError(DATA_TYPE_ERROR_MSG)

        return items

    def _to_model(self, item: dict[str, Any]) -> BaseModel | dict[str, Any]:
        """
        Convert an item to a model instance.

        This attempts to convert an item to a model instance,
        falling back to the raw item if conversion fails.

        Args:
            item: The item data

        Returns:
            Model instance or raw item
        """
        if not self.model_class:
            return item

        # Try to use model_validate if available (Pydantic v2)
        try:
            if hasattr(self.model_class, "model_validate"):
                return self.model_class.model_validate(item)
            # Fallback for older pydantic versions or model constructor
            return self.model_class(**item)
        except (ValueError, TypeError) as e:
            # If instantiation fails, return the raw item as fallback
            # Log a warning but continue with the raw item
            print(f"Warning: Failed to instantiate model: {e}")
            return item
