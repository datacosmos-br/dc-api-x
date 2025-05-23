"""
Configuration provider interface for DCApiX.

This module defines the ConfigProvider abstract class for
configuration management.
"""

import abc
from typing import Any

from .protocol import Provider


class ConfigProvider(Provider):
    """
    Base interface for configuration providers.

    Configuration providers supply configuration values from various sources
    and can manage configuration persistence.
    """

    @abc.abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """

    @abc.abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """

    @abc.abstractmethod
    def load(self, source: Any) -> None:
        """
        Load configuration from a source.

        Args:
            source: Configuration source
        """

    @abc.abstractmethod
    def save(self, destination: Any) -> None:
        """
        Save configuration to a destination.

        Args:
            destination: Configuration destination
        """

    def get_section(self, section: str) -> dict[str, Any]:
        """
        Get all configuration values in a section.

        Args:
            section: Section name

        Returns:
            Dictionary of configuration keys and values
        """
        raise NotImplementedError("Section-based configuration not supported")

    def has_key(self, key: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            key: Configuration key

        Returns:
            True if the key exists
        """
        return self.get(key, None) is not None
