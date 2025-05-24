"""
Configuration management module.

This module provides classes and functions for managing configuration settings,
including loading from different sources, validation, and serialization.
"""

import importlib.util
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.main import PydanticBaseSettingsSource

from .utils.constants import (
    AWS_SECRETS_DEPENDENCY_ERROR,
    AWS_SECRETS_LOAD_ERROR,
    AZURE_KEY_VAULT_DEPENDENCY_ERROR,
    AZURE_KEY_VAULT_LOAD_ERROR,
    CONFIG_DEFAULT_ENV_FILE,
    CONFIG_ENV_PREFIX,
    CONFIG_FILE_NOT_FOUND_ERROR,
    CONFIG_PASSWORD_KEY,
    CONFIG_RELOAD_ERROR,
    CONFIG_REQUIRED_KEYS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_TIMEOUT,
    LOAD_CONFIG_ERROR,
    LOAD_PROFILE_FAILED_ERROR,
    MAX_RETRIES_ERROR,
    MISSING_REQUIRED_VARS_ERROR,
    PROFILE_FILE_NOT_FOUND_ERROR,
    RETRY_BACKOFF_ERROR,
    TIMEOUT_ERROR,
    UNSUPPORTED_FORMAT_ERROR,
    URL_EMPTY_ERROR,
    URL_FORMAT_ERROR,
)
from .utils.exceptions import ConfigError

try:
    from pydantic_settings.sources import (
        AWSSecretsManagerSettingsSource,
        AzureKeyVaultSettingsSource,
    )

    CLOUD_SECRETS_AVAILABLE = True
except ImportError:
    CLOUD_SECRETS_AVAILABLE = False

# Check for optional dependencies
YAML_AVAILABLE = importlib.util.find_spec("yaml") is not None
TOML_AVAILABLE = (
    importlib.util.find_spec("tomli") is not None
    and importlib.util.find_spec("tomli_w") is not None
)


def _raise_profile_not_found(profile_name: str) -> None:
    """
    Raise a ConfigError for a profile that wasn't found.

    Args:
        profile_name: Name of the profile that wasn't found

    Raises:
        ConfigError: Always raised with formatted error message
    """
    raise ConfigError(PROFILE_FILE_NOT_FOUND_ERROR.format(profile_name))


def _raise_missing_required_vars(missing_keys: list[str]) -> None:
    """
    Raise a ConfigError for missing required configuration variables.

    Args:
        missing_keys: List of missing keys

    Raises:
        ConfigError: Always raised with formatted error message
    """
    raise ConfigError(MISSING_REQUIRED_VARS_ERROR.format(", ".join(missing_keys)))


@dataclass
class ConfigFormat:
    """Format specifications for configuration files."""

    suffix: str
    read_func: Callable[[Any], Any]
    write_func: Callable[[Any, Any], None]


class DatabaseSettings(BaseModel):
    """
    Database connection settings.

    This model contains settings for connecting to a database, which can
    be configured through environment variables or configuration files.
    """

    host: str = Field("localhost", description="Database host")
    port: int = Field(5432, description="Database port")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[SecretStr] = Field(None, description="Database password")
    name: Optional[str] = Field(None, description="Database name")
    ssl_mode: Optional[str] = Field(
        None,
        description="SSL mode for database connection",
    )


class ConfigProfile:
    """
    Configuration profile.

    A profile represents a named set of configuration values that can be
    loaded from environment variables or files.
    """

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        """
        Initialize with profile name and configuration.

        Args:
            name: Profile name
            config: Configuration dictionary
        """
        self.name = name
        self.config = config

    @property
    def is_valid(self) -> bool:
        """Check if the profile contains the minimum required configuration."""
        return all(
            key in self.config and self.config[key] for key in CONFIG_REQUIRED_KEYS
        )

    def __repr__(self) -> str:
        """Return string representation of the profile."""
        # Hide password in representation
        config_repr = {
            k: "****" if k == CONFIG_PASSWORD_KEY else v for k, v in self.config.items()
        }
        return f"ConfigProfile({self.name}, {config_repr})"


class Config(BaseSettings):
    """
    API client configuration.

    This class provides configuration management for the API client, including
    connection settings, authentication, and client behavior.

    Configuration can be loaded from:
    - Environment variables
    - .env files
    - Configuration files (JSON, TOML, YAML)
    - Secret files
    - Cloud secret management services

    Configuration sources are checked in the following order (by default):
    1. Initialization parameters (highest priority)
    2. Environment variables
    3. .env file
    4. Secret files (lowest priority)

    Example usage:
    ```python
    # Load from environment variables
    config = Config()

    # Load from a specific profile
    dev_config = Config.from_profile("dev")

    # Direct initialization
    config = Config(
        url="https://api.example.com",
        username="user123",
        password="pass123"
    )

    # Save configuration to a file
    config.save("config.json")

    # Load configuration from a file
    config = Config.from_file("config.json")
    ```
    """

    # Connection settings
    url: str = Field(description="API base URL")
    timeout: int = Field(
        default=DEFAULT_TIMEOUT,
        description="Request timeout in seconds",
    )
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    # Authentication
    username: str = Field(description="API username")
    password: SecretStr = Field(description="API password")

    # Client behavior
    max_retries: int = Field(
        default=DEFAULT_MAX_RETRIES,
        description="Maximum number of retry attempts",
    )
    retry_backoff: float = Field(
        default=DEFAULT_RETRY_BACKOFF,
        description="Exponential backoff factor for retries",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # Optional settings
    environment: Optional[str] = Field(
        None,
        description="Environment name (e.g., development, production)",
    )

    # Nested configurations
    database: Optional[DatabaseSettings] = Field(
        None,
        description="Database connection settings",
    )

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX,
        env_file=CONFIG_DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
        case_sensitive=False,
        env_nested_delimiter="__",
        secrets_dir="/run/secrets",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """
        Validate and normalize URL.

        Args:
            v: URL to validate

        Returns:
            Normalized URL

        Raises:
            ValueError: If URL is empty or invalid
        """
        if not v:
            raise ValueError(URL_EMPTY_ERROR)

        # Remove trailing slash
        url = v[:-1] if v.endswith("/") else v

        # Ensure URL starts with http or https
        if not (url.startswith(("http://", "https://"))):
            raise ValueError(URL_FORMAT_ERROR)

        return url

    @model_validator(mode="after")
    def validate_config(self) -> "Config":
        """
        Validate the complete configuration after all fields are set.

        Returns:
            Validated Config instance

        Raises:
            ValueError: If configuration is invalid
        """
        # Add any cross-field validation here
        if self.max_retries < 0:
            raise ValueError(MAX_RETRIES_ERROR)

        if self.retry_backoff <= 0:
            raise ValueError(RETRY_BACKOFF_ERROR)

        if self.timeout <= 0:
            raise ValueError(TIMEOUT_ERROR)

        return self

    def model_dump_custom(self, *, exclude_secrets: bool = True) -> dict[str, Any]:
        """
        Convert configuration to dictionary with custom handling.

        Args:
            exclude_secrets: Whether to exclude sensitive information

        Returns:
            Dictionary representation of the configuration
        """
        result = self.model_dump(exclude_none=True)

        # Handle SecretStr in Pydantic V2
        if not exclude_secrets and CONFIG_PASSWORD_KEY in result:
            if isinstance(result[CONFIG_PASSWORD_KEY], SecretStr):
                result[CONFIG_PASSWORD_KEY] = result[
                    CONFIG_PASSWORD_KEY
                ].get_secret_value()
            elif (
                isinstance(result[CONFIG_PASSWORD_KEY], dict[str, Any])
                and "__secret_value__" in result[CONFIG_PASSWORD_KEY]
            ):
                result[CONFIG_PASSWORD_KEY] = result[CONFIG_PASSWORD_KEY][
                    "__secret_value__"
                ]

        # Handle nested SecretStr fields
        if not exclude_secrets and "database" in result and result["database"]:
            if (
                CONFIG_PASSWORD_KEY in result["database"]
                and result["database"][CONFIG_PASSWORD_KEY]
                and isinstance(result["database"][CONFIG_PASSWORD_KEY], SecretStr)
            ):
                result["database"][CONFIG_PASSWORD_KEY] = result["database"][
                    CONFIG_PASSWORD_KEY
                ].get_secret_value()
            elif (
                isinstance(result["database"][CONFIG_PASSWORD_KEY], dict[str, Any])
                and "__secret_value__" in result["database"][CONFIG_PASSWORD_KEY]
            ):
                result["database"][CONFIG_PASSWORD_KEY] = result["database"][
                    CONFIG_PASSWORD_KEY
                ]["__secret_value__"]

        return result

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration with secrets as plain text
        """
        return self.model_dump_custom(exclude_secrets=False)

    def _save_json(self, file_path: Path) -> None:
        """
        Save configuration as JSON.

        Args:
            file_path: Path to save the JSON file
        """
        with file_path.open("w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def save(self, file_path: Union[str, Path]) -> None:
        """
        Save configuration to a file.

        Args:
            file_path: Path to save the configuration file

        Raises:
            ValueError: If file format is not supported
        """
        path = Path(file_path)

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Determine file format based on extension
        if path.suffix.lower() == ".json":
            self._save_json(path)
        else:
            raise ValueError(UNSUPPORTED_FORMAT_ERROR.format(path.suffix))

    @classmethod
    def _load_json_config(cls, file_path: Path) -> dict[str, Any]:
        """
        Load configuration from JSON file.

        Args:
            file_path: Path to the JSON configuration file

        Returns:
            Dictionary with configuration data
        """
        with file_path.open() as f:
            return json.load(f)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "Config":
        """
        Load configuration from a file.

        Args:
            file_path: Path to the configuration file

        Returns:
            Config: Configuration object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(CONFIG_FILE_NOT_FOUND_ERROR.format(str(path)))

        # Load based on file extension
        if path.suffix.lower() == ".json":
            config_data = cls._load_json_config(path)
        else:
            raise ValueError(UNSUPPORTED_FORMAT_ERROR.format(path.suffix))

        return cls(**config_data)

    @classmethod
    def _load_profile_env_vars(cls, profile_name: str) -> dict[str, Any]:
        """
        Load environment variables from a profile file.

        Args:
            profile_name: Name of the profile to load

        Returns:
            Dictionary of environment variables from the profile

        Raises:
            ConfigError: If profile file not found
        """
        profile_path = cls.get_profile_path(profile_name)

        if not profile_path.exists():
            raise ConfigError(PROFILE_FILE_NOT_FOUND_ERROR.format(profile_name))

        # Load environment variables from profile
        load_dotenv(dotenv_path=profile_path, override=True)

        # Return environment variables with prefix
        return {
            k.replace(CONFIG_ENV_PREFIX, ""): v
            for k, v in os.environ.items()
            if k.startswith(CONFIG_ENV_PREFIX)
        }

    @classmethod
    def get_profile_path(cls, profile_name: str) -> Path:
        """
        Get the path to a profile file.

        Args:
            profile_name: Name of the profile

        Returns:
            Path to the profile file
        """
        return Path(f".env.{profile_name}")

    @classmethod
    def from_profile(cls, profile_name: str) -> "Config":
        """
        Load configuration from a profile.

        Args:
            profile_name: Name of the profile to load

        Returns:
            Config object with profile configuration

        Raises:
            ConfigError: If the profile cannot be loaded
        """
        try:
            # Load configuration from environment variables
            config_vars = {}

            # Load configuration from INI file
            import configparser

            # Define the config path
            config_path = Path(os.environ.get("CONFIG_PATH", "config.ini"))

            if not config_path.exists():
                _raise_profile_not_found(profile_name)

            # Parse the INI file
            parser = configparser.ConfigParser()
            parser.read(config_path)

            # Check if the profile exists
            if profile_name not in parser:
                _raise_profile_not_found(profile_name)

            # Get the profile section
            profile_section = parser[profile_name]

            # Convert the profile section to a dictionary
            for key, value in profile_section.items():
                config_vars[key] = value

            # Validate required keys
            missing_keys = [
                key for key in CONFIG_REQUIRED_KEYS if key not in config_vars
            ]
            if missing_keys:
                _raise_missing_required_vars(missing_keys)

            # Create config object from loaded data
            return cls(**config_vars)

        except ConfigError:
            # Re-raise ConfigError
            raise
        except Exception as e:
            # Wrap other exceptions
            raise ConfigError(
                LOAD_PROFILE_FAILED_ERROR.format(profile_name, str(e)),
            ) from e

    @classmethod
    def settings_customise_sources(
        cls,
        _settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize the sources used for loading settings.

        This method defines the priority order of configuration sources:
        1. Initialization parameters (highest priority)
        2. Environment variables
        3. .env file
        4. Secret files (lowest priority)

        Args:
            _settings_cls: The Settings class (unused)
            init_settings: Settings from initialization
            env_settings: Settings from environment variables
            dotenv_settings: Settings from .env file
            file_secret_settings: Settings from secret files

        Returns:
            Tuple of settings sources in priority order
        """
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    @classmethod
    def with_aws_secrets(
        cls,
        secret_id: str,
        region_name: Optional[str] = None,
    ) -> "Config":
        """
        Load configuration with AWS Secrets Manager integration.

        Args:
            secret_id: AWS Secrets Manager secret ID
            region_name: AWS region name (optional)

        Returns:
            Config object with AWS Secrets Manager integration

        Raises:
            ImportError: If AWS Secrets Manager dependencies are not installed
            ConfigError: If AWS configuration fails
        """
        if not CLOUD_SECRETS_AVAILABLE:
            raise ImportError(AWS_SECRETS_DEPENDENCY_ERROR)

        class AWSConfig(cls):
            @classmethod
            def settings_customise_sources(
                cls,
                _settings_cls: type[BaseSettings],
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
            ) -> tuple[PydanticBaseSettingsSource, ...]:
                aws_settings = AWSSecretsManagerSettingsSource(
                    _settings_cls,
                    secret_id,
                    region_name=region_name,
                )
                return (
                    init_settings,
                    env_settings,
                    dotenv_settings,
                    file_secret_settings,
                    aws_settings,
                )

        try:
            return AWSConfig()
        except Exception as e:
            raise ConfigError(AWS_SECRETS_LOAD_ERROR.format(str(e))) from e

    @classmethod
    def with_azure_key_vault(cls, vault_url: str, credential: Any) -> "Config":
        """
        Load configuration with Azure Key Vault integration.

        Args:
            vault_url: Azure Key Vault URL
            credential: Azure credential object

        Returns:
            Config object with Azure Key Vault integration

        Raises:
            ImportError: If Azure Key Vault dependencies are not installed
            ConfigError: If Azure configuration fails
        """
        if not CLOUD_SECRETS_AVAILABLE:
            raise ImportError(AZURE_KEY_VAULT_DEPENDENCY_ERROR)

        class AzureConfig(cls):
            @classmethod
            def settings_customise_sources(
                cls,
                _settings_cls: type[BaseSettings],
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
            ) -> tuple[PydanticBaseSettingsSource, ...]:
                az_key_vault_settings = AzureKeyVaultSettingsSource(
                    _settings_cls,
                    vault_url,
                    credential,
                )
                return (
                    init_settings,
                    env_settings,
                    dotenv_settings,
                    file_secret_settings,
                    az_key_vault_settings,
                )

        try:
            return AzureConfig()
        except Exception as e:
            raise ConfigError(AZURE_KEY_VAULT_LOAD_ERROR.format(str(e))) from e

    def reload(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        Reload configuration from file.

        Args:
            file_path: Path to configuration file

        Raises:
            ConfigError: If configuration reload fails
        """
        if file_path is None:
            # Create new instance with same env file then copy attributes
            new_config = Config(_env_file=self.__class__.model_config.get("env_file"))

            for field_name in self.model_fields:
                if hasattr(new_config, field_name):
                    setattr(self, field_name, getattr(new_config, field_name))
        else:
            # Load from file
            new_config = self.from_file(file_path)

            for field_name in self.model_fields:
                if hasattr(new_config, field_name):
                    setattr(self, field_name, getattr(new_config, field_name))

    def model_reload(self) -> None:
        """
        Reload configuration from environment variables.

        This method reloads configuration from environment variables and files,
        useful when environment variables have changed at runtime.
        """
        try:
            # Create new instance with same env file then copy attributes
            new_config = Config(_env_file=self.__class__.model_config.get("env_file"))

            for field_name in self.model_fields:
                if hasattr(new_config, field_name):
                    setattr(self, field_name, getattr(new_config, field_name))
        except Exception as e:
            # Wrap any exceptions
            raise ConfigError(CONFIG_RELOAD_ERROR.format(str(e))) from e


def load_config_from_env() -> Config:
    """
    Load configuration from environment variables.

    Returns:
        Config object with environment configuration

    Raises:
        ConfigError: If required configuration is missing
    """
    try:
        return Config()
    except Exception as e:
        raise ConfigError(LOAD_CONFIG_ERROR.format(str(e))) from e


def list_available_profiles() -> list[str]:
    """
    list available configuration profiles.

    Profiles are determined by looking for `.env.{profile_name}` files
    in the current directory.

    Returns:
        list of profile names
    """
    profiles = []
    env_path = Path(CONFIG_DEFAULT_ENV_FILE)
    env_dir = env_path.parent

    # Look for .env.* files
    for file_path in env_dir.glob(f"{env_path.name}.*"):
        # Extract profile name from file name
        profile = file_path.name[len(env_path.name) + 1 :]
        profiles.append(profile)

    return profiles


class CLIConfig(Config):
    """
    Configuration for CLI applications.

    This class extends the base Config class with CLI-specific functionality,
    including automatic parsing of command-line arguments.

    Example usage:
    ```
    # Add this to your CLI script
    config = CLIConfig()

    # Run the script with:
    # python my_script.py --url=https://api.example.com --username=user --password=pass
    ```
    """

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX,
        env_file=CONFIG_DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
        case_sensitive=False,
        env_nested_delimiter="__",
        secrets_dir="/run/secrets",
        cli_parse_args=True,
    )
