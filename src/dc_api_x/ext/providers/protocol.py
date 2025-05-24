"""
Base provider protocol for DCApiX.

This module defines the base Provider abstract class that all
specific providers must inherit from.
"""

import abc
from typing import Any, TypeVar

T = TypeVar("T")


class Provider(abc.ABC):
    """
    Base interface for all providers.

    Providers are components that supply external data, schemas,
    or services in a standardized format.
    """

    @abc.abstractmethod
    def initialize(self) -> None:
        """
        return None  # Implement this method

        Initialize the provider.

        This method is called when the provider is first used
        and should establish any necessary connections or load
        any required resources.
        """

    @abc.abstractmethod
    def shutdown(self) -> None:
        """
        Shut down the provider.

        This method is called when the provider is no longer needed
        and should clean up any resources.
        """

    def set_option(self, name: str, value: Any) -> None:
        """
        Set a provider option.

        Args:
            name: Option name
            value: Option value
        """
        raise NotImplementedError(f"Option {name} not supported by this provider")
