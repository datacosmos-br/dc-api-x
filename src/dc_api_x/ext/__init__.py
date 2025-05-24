"""
Extension interfaces for DCApiX.

This module re-exports the extension interfaces for adapters, auth, hooks, and providers.
"""

# Re-export public APIs from ext.adapters
from .adapters import (
    AsyncAdapter,
    AsyncAdapterMixin,
    AsyncDatabaseAdapter,
    AsyncDatabaseAdapterImpl,
    AsyncDatabaseTransaction,
    AsyncDatabaseTransactionImpl,
    AsyncHttpAdapter,
    CacheAdapter,
    DatabaseAdapter,
    DatabaseTransaction,
    DatabaseTransactionImpl,
    DirectoryAdapter,
    DirectoryAdapterImpl,
    FileSystemAdapter,
    GenericDatabaseAdapter,
    GraphQLAdapter,
    HttpAdapter,
    MessageQueueAdapter,
    ProtocolAdapter,
    RequestsHttpAdapter,
    WebSocketAdapter,
    async_transaction,
)

# Re-export public APIs from ext.auth
from .auth import AuthProvider, BasicAuthProvider, LdapAuthProvider, TokenAuthProvider

# Re-export public APIs from ext.hooks
from .hooks import (
    ApiResponseHook,
    AuthHook,
    ErrorHook,
    HeadersHook,
    HookManager,
    LoggingHook,
    RequestHook,
    ResponseHook,
    create_auth_hook,
    create_headers_hook,
    create_logging_hook,
)

# Re-export public APIs from ext.providers
from .providers import (
    BatchDataProvider,
    ConfigProvider,
    DataProvider,
    PaginationProvider,
    Provider,
    ProviderManager,
    SchemaProvider,
    TransformProvider,
    create_data_provider,
    create_schema_provider,
)

__all__ = [
    # Adapters
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
    # Adapter implementations
    "RequestsHttpAdapter",
    "GenericDatabaseAdapter",
    "DatabaseTransactionImpl",
    "DirectoryAdapterImpl",
    # Auth providers
    "AuthProvider",
    "BasicAuthProvider",
    "TokenAuthProvider",
    "LdapAuthProvider",
    # Hooks
    "RequestHook",
    "ResponseHook",
    "ApiResponseHook",
    "ErrorHook",
    "LoggingHook",
    "HeadersHook",
    "AuthHook",
    "HookManager",
    "create_auth_hook",
    "create_headers_hook",
    "create_logging_hook",
    # Providers
    "Provider",
    "DataProvider",
    "BatchDataProvider",
    "SchemaProvider",
    "TransformProvider",
    "ConfigProvider",
    "PaginationProvider",
    "ProviderManager",
    "create_data_provider",
    "create_schema_provider",
]
