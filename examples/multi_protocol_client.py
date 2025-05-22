#!/usr/bin/env python3
"""
Multi-protocol client example.

This example demonstrates how to use the DCApiX client with different
protocol adapters.
"""

import logging
import os

from dc_api_x import ApiClient
from dc_api_x.ext.auth import BasicAuthProvider
from dc_api_x.utils import (
    DirectoryAdapterImpl,
    GenericDatabaseAdapter,
    RequestsHttpAdapter,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_http_client() -> None:
    """
    Example of using the HTTP adapter.
    """
    logger.info("=== HTTP Client Example ===")

    # Create an authentication provider
    auth_provider = BasicAuthProvider(
        username="username",
        password="password",
    )

    # Create an HTTP adapter
    adapter = RequestsHttpAdapter(
        timeout=30,
        verify_ssl=True,
        auth_provider=auth_provider,
    )

    # Create the client with the HTTP adapter
    client = ApiClient(
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

    # Create a database adapter for SQLite
    adapter = GenericDatabaseAdapter(
        connection_string="example.db",
        driver="sqlite3",
    )

    # Create the client with the database adapter
    client = ApiClient(
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
            "INSERT INTO test (name) VALUES (?)", {"name": "Transaction Test"},
        )
        transaction.commit()


def example_ldap_client() -> None:
    """
    Example of using the LDAP adapter.
    """
    logger.info("=== LDAP Client Example ===")

    # Create an authentication provider
    auth_provider = BasicAuthProvider(
        username="cn=admin,dc=example,dc=com",
        password="admin_password",
    )

    # Create an LDAP adapter
    adapter = DirectoryAdapterImpl(
        url="ldap://ldap.example.com",
        base_dn="dc=example,dc=com",
        auth_provider=auth_provider,
    )

    # Create the client with the LDAP adapter
    client = ApiClient(
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

    try:
        example_http_client()
    except Exception as e:
        logger.exception("HTTP example failed: %s", e)

    try:
        example_database_client()
    except Exception as e:
        logger.exception("Database example failed: %s", e)

    try:
        # Skip LDAP example by default as it requires an LDAP server
        if os.environ.get("RUN_LDAP_EXAMPLE") == "1":
            example_ldap_client()
    except Exception as e:
        logger.exception("LDAP example failed: %s", e)


if __name__ == "__main__":
    main()
