"""
Adapter interfaces for DCApiX.

This module contains base interfaces for different technology protocols
that can be implemented by external packages.
"""

from .async_adapters import (
    AsyncAdapter,
    AsyncAdapterMixin,
    AsyncDatabaseAdapterImpl,
    AsyncDatabaseTransactionImpl,
    AsyncHttpAdapter,
    async_transaction,
)
from .cache import CacheAdapter
from .database import DatabaseAdapter, DatabaseTransaction
from .directory import DirectoryAdapter
from .filesystem import FileSystemAdapter
from .graphql import GraphQLAdapter
from .http import HttpAdapter
from .implementations import (
    DatabaseTransactionImpl,
    DirectoryAdapterImpl,
    GenericDatabaseAdapter,
    RequestsHttpAdapter,
)
from .message_queue import MessageQueueAdapter
from .protocol import AsyncDatabaseAdapter, AsyncDatabaseTransaction, ProtocolAdapter
from .websocket import WebSocketAdapter

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
    "AsyncAdapterMixin",
    "AsyncHttpAdapter",
    "AsyncDatabaseAdapter",
    "AsyncDatabaseTransaction",
    "AsyncDatabaseAdapterImpl",
    "AsyncDatabaseTransactionImpl",
    "async_transaction",
    # Implementation classes
    "RequestsHttpAdapter",
    "GenericDatabaseAdapter",
    "DatabaseTransactionImpl",
    "DirectoryAdapterImpl",
]
