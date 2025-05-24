"""
Cursor-based pagination strategy for DCApiX.

This module provides a paginator for APIs that use cursors for pagination,
such as those that return a "next_cursor" and "has_more" flag.
"""

from collections.abc import Iterator
from typing import Any, Optional

from pydantic import BaseModel

from dc_api_x.pagination.base import BasePaginator
from dc_api_x.utils.exceptions import ApiError


class CursorPaginator(BasePaginator[BaseModel]):
    """
    Paginator for APIs that use cursor-based pagination.

    This strategy works with APIs that return a next cursor token
    and a has_more flag to indicate if there are more pages.
    """

    def paginate(self) -> Optional[Iterator[dict[str, Any] | BaseModel]]:
        """
        Paginate through API results using cursor tokens.

        This method handles pagination by extracting the next cursor
        from each response and using it in the subsequent request.

        Yields:
            Each item in the paginated response

        Raises:
            ApiError: If the API request fails
        """
        page_count = 0
        cursor = None

        # Set initial page size if supported
        if hasattr(self.config, "page_size_param") and self.config.page_size_param:
            self.params[self.config.page_size_param] = self.config.page_size

        while True:
            # Set cursor for the current request (if not the first page)
            if cursor is not None:
                self.params[self.config.cursor_param] = cursor
            elif self.config.cursor_param in self.params:
                # Remove cursor param for first request if it was in params
                del self.params[self.config.cursor_param]

            # Make request
            response = self.client.get(self.endpoint, params=self.params)

            # Check for errors
            if not response.success:
                error_message = (
                    str(response.error) if response.error else "Unknown error"
                )
                error_msg = f"Pagination failed: {error_message}"
                raise ApiError(error_msg)

            # Extract data
            items = self._extract_data(response)

            # No more items, we're done
            if not items:
                break

            # Yield each item
            for item in items:
                yield self._to_model(item)

            # Update page count
            page_count += 1

            # Check if we've reached max pages
            if self.config.max_pages and page_count >= self.config.max_pages:
                break

            # Get next cursor and has_more flag
            response_data = response.data or {}
            has_more = False
            cursor = None

            if isinstance(response_data, dict[str, Any]):
                # Check if there are more pages
                if self.config.has_more_key in response_data:
                    has_more = bool(response_data[self.config.has_more_key])

                # Get next cursor
                if self.config.next_cursor_key in response_data:
                    cursor = response_data[self.config.next_cursor_key]

            # If no more pages or no cursor, we're done
            if not has_more or cursor is None:
                break
