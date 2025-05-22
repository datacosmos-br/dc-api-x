"""
Base protocol adapter for DCApiX.

This module defines the base ProtocolAdapter abstract class that all
specific protocol adapters must inherit from.
"""

import abc
from typing import Any, Optional, Type


class ProtocolAdapter(abc.ABC):
    """
    Base interface for protocol adapters.

    Protocol adapters handle communication with specific technologies
    and abstract away the details of the protocol.
    """

    @abc.abstractmethod
    def connect(self) -> None:
        """
        Establish a connection to the resource.

        This method is called when initializing the adapter and should
        establish any necessary connections.
        """

    @abc.abstractmethod
    def disconnect(self) -> None:
        """
        Close the connection to the resource.

        This method is called when shutting down the adapter and should
        clean up any resources.
        """

    @abc.abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the adapter is connected.

        Returns:
            True if connected, False otherwise
        """

    def __enter__(self) -> "ProtocolAdapter":
        """Enter context manager and connect."""
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """Exit context manager and disconnect."""
        self.disconnect()
