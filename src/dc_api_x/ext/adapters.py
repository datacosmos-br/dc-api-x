"""
Adapter interfaces for DCApiX.

This module defines adapter interfaces for different technology protocols
that can be implemented by external packages.

This is a facade that re-exports all adapters from the adapters subdirectory.
"""

from .adapters.async_adapters import (
    AsyncAdapter,
    AsyncDatabaseAdapter,
    AsyncDatabaseTransaction,
    AsyncHttpAdapter,
)
from .adapters.cache import CacheAdapter
from .adapters.database import DatabaseAdapter, DatabaseTransaction
from .adapters.directory import DirectoryAdapter
from .adapters.filesystem import FileSystemAdapter
from .adapters.graphql import GraphQLAdapter
from .adapters.http import HttpAdapter
from .adapters.message_queue import MessageQueueAdapter
from .adapters.protocol import ProtocolAdapter
from .adapters.websocket import WebSocketAdapter

__all__ = [
    "ProtocolAdapter",
    "HttpAdapter",
    "DatabaseAdapter",
    "DatabaseTransaction",
    "DirectoryAdapter",
    "MessageQueueAdapter",
    "CacheAdapter",
    "FileSystemAdapter",
    "GraphQLAdapter",
    "WebSocketAdapter",
    "AsyncAdapter",
    "AsyncHttpAdapter",
    "AsyncDatabaseAdapter",
    "AsyncDatabaseTransaction",
]
