#!/usr/bin/env python3
"""
Multi-protocol client example.

This example demonstrates how to use the DCApiX client with different
protocol adapters.
"""

import logging
import os

import dc_api_x as apix

# Enable plugins to access all registered adapters and providers
apix.enable_plugins()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_http_client() -> None:
    """
    Example of using the HTTP adapter.
    """
    logger.info("=== HTTP Client Example ===")

    # Check available HTTP adapters
    http_adapters = [name for name in apix.list_adapters() if "http" in name.lower()]
    logger.info("Available HTTP adapters: %s", http_adapters)

    # Create an authentication provider
    auth_provider = apix.BasicAuthProvider(
        username="username",
        password="password",  # noqa: S106
    )

    # Get HTTP adapter from registry or use the built-in one
    http_adapter_cls = apix.get_adapter("http") or apix.ext.HttpAdapter
    adapter = http_adapter_cls(
        timeout=30,
        verify_ssl=True,
        auth_provider=auth_provider,
    )

    # Create the client with the HTTP adapter
    client = apix.ApiClient(
        url="https://httpbin.org",
        adapter=adapter,
        auth_provider=auth_provider,
    )

    # Make a request
    response = client.get("get", params={"key": "value"})
    logger.info("HTTP Response: %s", response.data)


def example_database_client() -> None:
    """
    Example of using the database adapter.
    """
    logger.info("=== Database Client Example ===")

    # Check available database adapters
    db_adapters = [
        name
        for name in apix.list_adapters()
        if "db" in name.lower() or "database" in name.lower()
    ]
    logger.info("Available database adapters: %s", db_adapters)

    # Get database adapter from registry or use the built-in one
    db_adapter_cls = apix.get_adapter("sqlite_db") or apix.DatabaseAdapter

    # Create a database adapter for SQLite
    adapter = db_adapter_cls(
        connection_string="example.db",
        driver="sqlite3",
    )

    # Create the client with the database adapter
    client = apix.ApiClient(
        url="sqlite://example.db",  # Just for reference, not actually used
        adapter=adapter,
    )

    # Create a table
    client.execute_query(
        """
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """,
    )

    # Insert data
    client.execute_query(
        "INSERT INTO test (name) VALUES (:name)",
        params={"name": "Test Name"},
    )

    # Query data
    result = client.execute_query("SELECT * FROM test")
    logger.info("Database Result: %s", result.data)

    # Using a transaction
    with adapter.begin_transaction() as transaction:
        transaction.execute(
            "INSERT INTO test (name) VALUES (?)",
            {"name": "Transaction Test"},
        )
        transaction.commit()


def example_ldap_client() -> None:
    """
    Example of using the LDAP adapter.
    """
    logger.info("=== LDAP Client Example ===")

    # Check available directory adapters
    dir_adapters = [
        name
        for name in apix.list_adapters()
        if "ldap" in name.lower() or "directory" in name.lower()
    ]
    logger.info("Available directory adapters: %s", dir_adapters)

    # Create an authentication provider
    auth_provider = apix.BasicAuthProvider(
        username="cn=admin,dc=example,dc=com",
        password="admin_password",  # noqa: S106
    )

    # Get directory adapter from registry or use the built-in one
    dir_adapter_cls = apix.get_adapter("ldap") or apix.DirectoryAdapter

    # Create an LDAP adapter
    adapter = dir_adapter_cls(
        url="ldap://ldap.example.com",
        base_dn="dc=example,dc=com",
        auth_provider=auth_provider,
    )

    # Create the client with the LDAP adapter
    client = apix.ApiClient(
        url="ldap://ldap.example.com",  # Just for reference
        adapter=adapter,
        auth_provider=auth_provider,
    )

    # Search the directory
    result = client.search_directory(
        base_dn="ou=users,dc=example,dc=com",
        search_filter="(objectClass=person)",
        attributes=["cn", "mail"],
    )

    logger.info("LDAP Search Result: %s", result.data)


def main() -> None:
    """
    Run all examples.
    """
    logger.info("DCApiX Multi-Protocol Client Examples")

    # Print available plugin components
    logger.info("Available adapters: %s", apix.list_adapters())
    logger.info("Available auth providers: %s", apix.list_auth_providers())
    logger.info("Available schema providers: %s", apix.list_schema_providers())
    logger.info("Available config providers: %s", apix.list_config_providers())
    logger.info("Available data providers: %s", apix.list_data_providers())

    try:
        example_http_client()
    except Exception:
        logger.exception("HTTP example failed")

    try:
        example_database_client()
    except Exception:
        logger.exception("Database example failed")

    try:
        # Skip LDAP example by default as it requires an LDAP server
        if os.environ.get("RUN_LDAP_EXAMPLE") == "1":
            example_ldap_client()
    except Exception:
        logger.exception("LDAP example failed")


if __name__ == "__main__":
    main()
