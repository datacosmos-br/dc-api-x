"""
Message queue adapter for DCApiX.

This module defines the MessageQueueAdapter abstract class for message queue operations.
"""

import abc
from collections.abc import Callable
from typing import Any, Union

from .protocol import ProtocolAdapter


class MessageQueueAdapter(ProtocolAdapter):
    """Base interface for message queue adapters."""

    @abc.abstractmethod
    def publish(
        self,
        topic: str,
        message: Union[str, bytes, dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Publish a message to a topic.

        Args:
            topic: Topic to publish to
            message: Message to publish
            **kwargs: Additional parameters
        """

    @abc.abstractmethod
    def subscribe(
        self,
        topic: str,
        callback: Callable[[str, Any], None],
        **kwargs: Any,
    ) -> None:
        """
        Subscribe to a topic.

        Args:
            topic: Topic to subscribe to
            callback: Callback function to handle messages
            **kwargs: Additional parameters
        """

    @abc.abstractmethod
    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from a topic.

        Args:
            topic: Topic to unsubscribe from
        """
