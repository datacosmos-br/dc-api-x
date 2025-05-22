"""
Cache adapter for DCApiX.

This module defines the CacheAdapter abstract class for cache operations.
"""

import abc
from typing import Generic, Optional, TypeVar

from .protocol import ProtocolAdapter

K = TypeVar("K")
V = TypeVar("V")


class CacheAdapter(ProtocolAdapter, Generic[K, V]):
    """Base interface for cache adapters."""

    @abc.abstractmethod
    def get(self, key: K) -> Optional[V]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """

    @abc.abstractmethod
    def set(self, key: K, value: V, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default)
        """

    @abc.abstractmethod
    def delete(self, key: K) -> None:
        """
        Delete a value from the cache.

        Args:
            key: Cache key
        """

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear the entire cache."""
