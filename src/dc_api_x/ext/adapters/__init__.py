"""
Adapter interfaces for DCApiX.

This module contains base interfaces for different technology protocols
that can be implemented by external packages.
"""

from .async_adapters import (
    AsyncAdapter,
    AsyncDatabaseAdapter,
    AsyncDatabaseTransaction,
    AsyncHttpAdapter,
)
from .cache import CacheAdapter
from .database import DatabaseAdapter, DatabaseTransaction
from .directory import DirectoryAdapter
from .filesystem import FileSystemAdapter
from .graphql import GraphQLAdapter
from .http import HttpAdapter
from .message_queue import MessageQueueAdapter
from .protocol import ProtocolAdapter
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
    "AsyncHttpAdapter",
    "AsyncDatabaseAdapter",
    "AsyncDatabaseTransaction",
]
