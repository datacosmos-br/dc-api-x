"""
Pagination provider interface for DCApiX.

This module defines the PaginationProvider abstract class for
handling paginated data access.
"""

import abc
from typing import Any, Generic, TypeVar

from .protocol import Provider

T = TypeVar("T")


class PaginationProvider(Provider, Generic[T]):
    """
    Base interface for pagination providers.

    Pagination providers handle paginated data access, providing
    standardized methods for navigating through pages of results.
    """

    @abc.abstractmethod
    def get_page(self, page_number: int, page_size: int, **kwargs: Any) -> list[T]:
        """
        Get a specific page of results.

        Args:
            page_number: Page number (1-based)
            page_size: Number of items per page
            **kwargs: Additional filter parameters

        Returns:
            List of items for the requested page
        """

    @abc.abstractmethod
    def get_total_pages(self, page_size: int, **kwargs: Any) -> int:
        """
        Get the total number of pages available.

        Args:
            page_size: Number of items per page
            **kwargs: Additional filter parameters

        Returns:
            Total number of pages
        """

    @abc.abstractmethod
    def get_total_items(self, **kwargs: Any) -> int:
        """
        Get the total number of items available.

        Args:
            **kwargs: Additional filter parameters

        Returns:
            Total number of items
        """

    def get_next_page_token(self, current_page: int, page_size: int) -> str:
        """
        Get a token that can be used to retrieve the next page.

        This is useful for cursor-based pagination systems.

        Args:
            current_page: Current page number
            page_size: Number of items per page

        Returns:
            Token for the next page
        """
        raise NotImplementedError("Token-based pagination not supported")

    def get_page_by_token(self, token: str, page_size: int) -> list[T]:
        """
        Get a page of results using a pagination token.

        Args:
            token: Pagination token from get_next_page_token
            page_size: Number of items per page

        Returns:
            List of items for the requested page
        """
        raise NotImplementedError("Token-based pagination not supported")
