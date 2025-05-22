"""
File system adapter for DCApiX.

This module defines the FileSystemAdapter abstract class for file system operations.
"""

import abc
from typing import Union

from .protocol import ProtocolAdapter


class FileSystemAdapter(ProtocolAdapter):
    """Base interface for file system adapters."""

    @abc.abstractmethod
    def read_file(self, path: str) -> bytes:
        """
        Read a file from the file system.

        Args:
            path: Path to the file

        Returns:
            File contents as bytes
        """

    @abc.abstractmethod
    def write_file(self, path: str, contents: Union[str, bytes]) -> None:
        """
        Write contents to a file.

        Args:
            path: Path to the file
            contents: Contents to write
        """

    @abc.abstractmethod
    def delete_file(self, path: str) -> None:
        """
        Delete a file.

        Args:
            path: Path to the file
        """

    @abc.abstractmethod
    def list_directory(self, path: str) -> list[str]:
        """
        List contents of a directory.

        Args:
            path: Path to the directory

        Returns:
            List of file/directory names
        """

    @abc.abstractmethod
    def create_directory(self, path: str) -> None:
        """
        Create a directory.

        Args:
            path: Path to the directory
        """

    @abc.abstractmethod
    def delete_directory(self, path: str, *, recursive: bool = False) -> None:
        """
        Delete a directory.

        Args:
            path: Path to the directory
            recursive: Whether to delete recursively
        """

    @abc.abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a file or directory exists.

        Args:
            path: Path to check

        Returns:
            True if exists, False otherwise
        """

    @abc.abstractmethod
    def is_file(self, path: str) -> bool:
        """
        Check if path points to a file.

        Args:
            path: Path to check

        Returns:
            True if path is a file, False otherwise
        """

    @abc.abstractmethod
    def is_directory(self, path: str) -> bool:
        """
        Check if path points to a directory.

        Args:
            path: Path to check

        Returns:
            True if path is a directory, False otherwise
        """
