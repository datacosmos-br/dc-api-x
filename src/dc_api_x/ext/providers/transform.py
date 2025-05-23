"""
Transform provider interface for DCApiX.

This module defines the TransformProvider abstract class for
data transformation operations.
"""

import abc
from typing import Any, Generic, TypeVar

from .protocol import Provider

T = TypeVar("T")
V = TypeVar("V")


class TransformProvider(Provider, Generic[T, V]):
    """
    Base interface for transform providers.

    Transform providers convert data between different formats or schemas.
    """

    @abc.abstractmethod
    def transform(self, data: T, **kwargs: Any) -> V:
        """
        Transform data from one format to another.

        Args:
            data: Input data
            **kwargs: Transform parameters

        Returns:
            Transformed data
        """

    @abc.abstractmethod
    def batch_transform(self, items: list[T], **kwargs: Any) -> list[V]:
        """
        Transform multiple items.

        Args:
            items: Input items
            **kwargs: Transform parameters

        Returns:
            Transformed items
        """

    def can_transform(self, _source_type: str, _target_type: str) -> bool:
        """
        Check if this provider can transform between the given types.

        Args:
            _source_type: Source data type
            _target_type: Target data type

        Returns:
            True if the provider can transform between these types
        """
        return False

    def get_supported_transforms(self) -> list[tuple[str, str]]:
        """
        Get a list of supported transformations.

        Returns:
            List of (source_type, target_type) tuples
        """
        return []
