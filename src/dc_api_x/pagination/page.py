"""
Page-based pagination strategy for DCApiX.

This module provides a paginator for APIs that use page/per_page parameters
for pagination.
"""

from collections.abc import Iterator
from typing import Any, Optional

from pydantic import BaseModel

from dc_api_x.exceptions import ApiError
from dc_api_x.pagination.base import BasePaginator


class PagePaginator(BasePaginator[BaseModel]):
    """
    Paginator for APIs that use page/per_page parameters.

    This is a common pagination strategy used by many APIs,
    where the client specifies a page number and page size.
    """

    def paginate(self) -> Optional[Iterator[dict[str, Any] | BaseModel]]:
        """
        Paginate through API results using page/per_page.

        This method handles pagination by incrementing the page parameter
        for each subsequent request.

        Yields:
            Each item in the paginated response

        Raises:
            ApiError: If the API request fails
        """
        page = 1

        # Set initial page size parameter
        self.params[self.config.page_size_param] = self.config.page_size

        while True:
            # Set page for the current request
            self.params[self.config.page_param] = page

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

            # Check if we've reached max pages
            if self.config.max_pages and page >= self.config.max_pages:
                break

            # Check if we've reached the end
            if len(items) < self.config.page_size:
                break

            # Move to next page
            page += 1
