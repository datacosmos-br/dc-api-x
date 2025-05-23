"""
Provider interfaces for DCApiX.

This module contains base interfaces for different provider types
that can be implemented by external packages.
"""

from .config import ConfigProvider
from .data import BatchDataProvider, DataProvider
from .facade import ProviderManager, create_data_provider, create_schema_provider
from .pagination import PaginationProvider
from .protocol import Provider
from .schema import SchemaProvider
from .transform import TransformProvider

__all__ = [
    # Interfaces
    "Provider",
    "DataProvider",
    "BatchDataProvider",
    "SchemaProvider",
    "TransformProvider",
    "ConfigProvider",
    "PaginationProvider",
    # Facade & Factory
    "ProviderManager",
    "create_data_provider",
    "create_schema_provider",
]
