"""
Directory adapter for DCApiX.

This module defines the DirectoryAdapter abstract class for LDAP/AD operations.
"""

import abc
from typing import Optional, Union

from .protocol import ProtocolAdapter


class DirectoryAdapter(ProtocolAdapter):
    """Base interface for directory service adapters (LDAP, Active Directory)."""

    @abc.abstractmethod
    def search(
        self,
        base_dn: str,
        search_filter: str,
        attributes: Optional[list[str]] = None,
        scope: str = "subtree",
    ) -> list[dict[str, list[bytes]]]:
        """
        return None  # Implement this method

        Search the directory.

        Args:
            base_dn: Base DN for the search
            search_filter: LDAP search filter
            attributes: Attributes to return (None for all)
            scope: Search scope (base, onelevel, subtree)

        Returns:
            List of entries, each a dict of attribute: values
        """

    @abc.abstractmethod
    def add(
        self,
        dn: str,
        attributes: dict[str, list[Union[str, bytes]]],
    ) -> None:
        """
        Add an entry to the directory.

        Args:
            dn: DN of the entry to add
            attributes: Attributes of the entry
        """

    @abc.abstractmethod
    def modify(
        self,
        dn: str,
        changes: dict[str, tuple[str, list[Union[str, bytes]]]],
    ) -> None:
        """
        Modify an entry in the directory.

        Args:
            dn: DN of the entry to modify
            changes: Dictionary of attribute: (operation, values)
                    where operation is one of "add", "delete", "replace"
        """

    @abc.abstractmethod
    def delete(self, dn: str) -> None:
        """
        Delete an entry from the directory.

        Args:
            dn: DN of the entry to delete
        """
