"""
Configuration management for DCApiX.

This module provides configuration management classes for the API client,
including loading configuration from environment variables, files, and cloud
secret management services.
"""

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Optional,
    Union,
)

from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

try:
    # Optional dependencies for cloud secret management
    from pydantic_settings import (
        AWSSecretsManagerSettingsSource,
        AzureKeyVaultSettingsSource,
    )

    CLOUD_SECRETS_AVAILABLE = True
except ImportError:
    CLOUD_SECRETS_AVAILABLE = False

# Import constants from the constants module
from .constants import (
    CONFIG_DEFAULT_ENV_FILE,
    CONFIG_ENV_PREFIX,
    CONFIG_PASSWORD_KEY,
    CONFIG_REQUIRED_KEYS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_TIMEOUT,
    URL_EMPTY_ERROR,
    URL_FORMAT_ERROR,
)
from .exceptions import ConfigError, ConfigurationError


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
        return all(key in self.config for key in CONFIG_REQUIRED_KEYS)

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
    timeout: int = Field(DEFAULT_TIMEOUT, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

    # Authentication
    username: str = Field(description="API username")
    password: SecretStr = Field(description="API password")

    # Client behavior
    max_retries: int = Field(
        DEFAULT_MAX_RETRIES,
        description="Maximum number of retry attempts",
    )
    retry_backoff: float = Field(
        DEFAULT_RETRY_BACKOFF,
        description="Exponential backoff factor for retries",
    )
    debug: bool = Field(False, description="Enable debug mode")

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
            raise ValueError("max_retries must be a non-negative integer")

        if self.retry_backoff <= 0:
            raise ValueError("retry_backoff must be a positive number")

        if self.timeout <= 0:
            raise ValueError("timeout must be a positive integer")

        return self

    def model_dump_custom(self, exclude_secrets: bool = True) -> dict[str, Any]:
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
            raise ValueError(f"Unsupported file format: {path.suffix}")

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
            raise FileNotFoundError(f"Configuration file {str(path)} not found")

        # Load based on file extension
        if path.suffix.lower() == ".json":
            config_data = cls._load_json_config(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

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
            raise ConfigError(f"Profile file .env.{profile_name} not found")

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
            Config instance loaded from the profile

        Raises:
            ConfigError: If profile file not found
            ConfigurationError: If configuration is invalid (missing required fields)
        """
        # Check if profile env file exists
        env_file = f"{CONFIG_DEFAULT_ENV_FILE}.{profile_name}"
        env_path = Path(env_file)

        if env_path.exists():
            # Load environment variables from the profile file
            if not load_dotenv(dotenv_path=env_path, override=True):
                raise ConfigError(f"Could not load profile from {env_file}")
        else:
            raise ConfigError(f"Profile file {env_file} not found")

        # Check if required environment variables are present
        missing_vars = []
        for key in CONFIG_REQUIRED_KEYS:
            env_key = f"{CONFIG_ENV_PREFIX}{key.upper()}"
            if env_key not in os.environ:
                missing_vars.append(env_key)

        if missing_vars:
            raise ConfigurationError(
                f"Missing required configuration variables: {', '.join(missing_vars)}",
            )

        # Create configuration from environment variables
        try:
            config = cls(_env_file=env_file)
            config.environment = profile_name
            return config
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load profile {profile_name}: {str(e)}",
            ) from e
        else:
            raise ConfigError(f"Failed to load profile {profile_name}")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
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
            settings_cls: The Settings class
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
            raise ImportError(
                "AWS Secrets Manager integration requires additional dependencies. "
                "Install with: pip install pydantic-settings[aws]",
            )

        class AWSConfig(cls):
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls: type[BaseSettings],
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
            ) -> tuple[PydanticBaseSettingsSource, ...]:
                aws_settings = AWSSecretsManagerSettingsSource(
                    settings_cls,
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
            raise ConfigError(
                f"Failed to load AWS Secrets Manager config: {str(e)}",
            ) from e

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
            raise ImportError(
                "Azure Key Vault integration requires additional dependencies. "
                "Install with: pip install pydantic-settings[azure]",
            )

        class AzureConfig(cls):
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls: type[BaseSettings],
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
            ) -> tuple[PydanticBaseSettingsSource, ...]:
                az_key_vault_settings = AzureKeyVaultSettingsSource(
                    settings_cls,
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
            raise ConfigError(f"Failed to load Azure Key Vault config: {str(e)}") from e

    def model_reload(self) -> None:
        """
        Reload configuration from sources.

        This method reloads configuration from environment variables and files,
        useful when environment variables have changed at runtime.
        """
        # Create new instance with same env file then copy attributes
        new_config = Config(_env_file=self.__class__.model_config.get("env_file"))

        for field_name in self.model_fields:
            if hasattr(new_config, field_name):
                setattr(self, field_name, getattr(new_config, field_name))

    @classmethod
    def from_config(cls, config: "Config") -> "Config":
        """
        Create a new configuration from an existing one.

        This is useful for creating a new configuration with some modified values.

        Args:
            config: Existing configuration

        Returns:
            New configuration object
        """
        return cls(**config.model_dump(exclude_none=True))


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
        raise ConfigError(f"Failed to load configuration: {str(e)}") from e


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
