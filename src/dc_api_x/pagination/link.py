"""
Link header-based pagination strategy for DCApiX.

This module provides a paginator for APIs that use RFC 5988 Link headers
for pagination, like GitHub and many other RESTful APIs.
"""

import re
from collections.abc import Iterator
from typing import Any, Optional

from pydantic import BaseModel

from dc_api_x.pagination.base import BasePaginator
from dc_api_x.utils.exceptions import ApiError


class LinkHeaderPaginator(BasePaginator[BaseModel]):
    """
    Paginator for APIs that use Link headers for pagination.

    This strategy works with APIs that return pagination links in the
    Link header according to RFC 5988, like GitHub's API.
    """

    def paginate(self) -> Optional[Iterator[dict[str, Any] | BaseModel]]:
        """
        Paginate through API results using Link headers.

        This method handles pagination by extracting the next link
        from the Link header and using it for subsequent requests.

        Yields:
            Each item in the paginated response

        Raises:
            ApiError: If the API request fails
        """
        page_count = 0
        url = self.endpoint

        # Set initial page size if supported
        params = self.params.copy()
        if hasattr(self.config, "page_size_param") and self.config.page_size_param:
            params[self.config.page_size_param] = self.config.page_size

        while True:
            # Make request - for first page use our constructed URL,
            # for subsequent pages use the 'next' link directly
            if page_count == 0:
                response = self.client.get(url, params=params)
            else:
                # Use URL directly - don't add params again
                response = self.client.get(url)

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

            # Get the 'next' link from the Link header
            next_link = self._extract_next_link(response.headers)
            if next_link is None:
                # No next link, we're done
                break

            # Update the URL for the next request
            url = next_link

    def _extract_next_link(self, headers: dict[str, str]) -> Optional[str]:
        """
        Extract the 'next' link from the Link header.

        Args:
            headers: Response headers

        Returns:
            URL for the next page, or None if there is no next page
        """
        # Link header may not be present if we're on the last page
        link_header = headers.get(self.config.link_header)
        if not link_header:
            return None

        # Parse the Link header
        # Format: <url>; rel="next", <url>; rel="prev", <url>; rel="last", ...
        links = {}
        for link in link_header.split(","):
            # Extract URL and rel
            match = re.search(r'<(.+)>;\s*rel="(.+)"', link)
            if match:
                url, rel = match.groups()
                links[rel] = url

        # Return the 'next' link
        return links.get("next")
