"""
WebSocket adapter for DCApiX.

This module defines the WebSocketAdapter abstract class for WebSocket communications.
"""

import abc
from collections.abc import Callable
from typing import Any, Optional, Union

from .protocol import ProtocolAdapter


class WebSocketAdapter(ProtocolAdapter):
    """Base interface for WebSocket adapters."""

    @abc.abstractmethod
    def connect_websocket(self, url: str, **kwargs: Any) -> None:
        """
        Connect to a WebSocket endpoint.

        Args:
            url: WebSocket URL
            **kwargs: Additional connection parameters
        """

    @abc.abstractmethod
    def disconnect_websocket(self) -> None:
        """
        Disconnect from the WebSocket endpoint.
        """

    @abc.abstractmethod
    def send(self, data: Union[str, bytes, dict[str, Any]]) -> None:
        """
        Send data through the WebSocket connection.

        Args:
            data: Data to send (string, bytes, or JSON-serializable dict)
        """

    @abc.abstractmethod
    def receive(self, timeout: Optional[float] = None) -> Optional[Union[str, bytes]]:
        """
        Receive data from the WebSocket connection.

        Args:
            timeout: Maximum time to wait in seconds (None for no timeout)

        Returns:
            Received data or None if no data received within timeout
        """

    @abc.abstractmethod
    def on_message(self, callback: Callable[[Union[str, bytes]], None]) -> None:
        """
        Register a callback for incoming messages.

        Args:
            callback: Function that will be called with received data
        """

    @abc.abstractmethod
    def on_error(self, callback: Callable[[Exception], None]) -> None:
        """
        Register a callback for connection errors.

        Args:
            callback: Function that will be called with the exception
        """

    @abc.abstractmethod
    def on_close(self, callback: Callable[[], None]) -> None:
        """
        Register a callback for when the connection is closed.

        Args:
            callback: Function that will be called when connection closes
        """
