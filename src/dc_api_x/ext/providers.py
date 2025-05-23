"""
Provider interfaces for DCApiX.

This module is deprecated. Please use the dc_api_x.ext.providers package instead.
"""

# Re-export from providers package
from .providers.config import ConfigProvider
from .providers.data import BatchDataProvider, DataProvider
from .providers.facade import (
    ProviderManager,
    create_data_provider,
    create_schema_provider,
)
from .providers.pagination import PaginationProvider
from .providers.protocol import Provider
from .providers.schema import SchemaProvider
from .providers.transform import TransformProvider

__all__ = [
    # Base provider
    "Provider",
    # Data providers
    "DataProvider",
    "BatchDataProvider",
    # Schema provider
    "SchemaProvider",
    # Transform provider
    "TransformProvider",
    # Config provider
    "ConfigProvider",
    # Pagination provider
    "PaginationProvider",
    # Facade & Factory
    "ProviderManager",
    "create_data_provider",
    "create_schema_provider",
]
