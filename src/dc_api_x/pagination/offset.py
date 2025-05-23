"""
Offset-based pagination strategy for DCApiX.

This module provides a paginator for APIs that use offset/limit parameters
for pagination.
"""

from collections.abc import Iterator
from typing import Any

from pydantic import BaseModel

from dc_api_x.exceptions import ApiError
from dc_api_x.pagination.base import BasePaginator


class OffsetPaginator(BasePaginator):
    """
    Paginator for APIs that use offset/limit parameters.

    This is a common pagination strategy used by many APIs,
    where the client specifies an offset and limit for each page.
    """

    def paginate(self) -> Iterator[dict[str, Any] | BaseModel]:
        """
        Paginate through API results using offset/limit.

        This method handles pagination by updating the offset parameter
        for each subsequent request.

        Yields:
            Each item in the paginated response

        Raises:
            ApiError: If the API request fails
        """
        offset = 0
        page_count = 0

        # Set initial limit parameter
        self.params[self.config.limit_param] = self.config.page_size

        while True:
            # Set offset for the current page
            self.params[self.config.offset_param] = offset

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

            # Check if we've reached the end
            if len(items) < self.config.page_size:
                break

            # Move to next page
            offset += len(items)
