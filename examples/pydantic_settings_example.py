#!/usr/bin/env python3
"""
Example of using Pydantic Settings in DCApiX.

This script demonstrates various ways to load and manage configuration
using Pydantic Settings, including environment variables, dotenv files,
profiles, and secure handling of sensitive information.
"""

import os
import tempfile
from pathlib import Path
from typing import Annotated, Any, Optional
from unittest import mock

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

import dc_api_x as apix


# Example 1: Basic Config with environment variables
class DatabaseSettings(BaseModel):
    """Database connection settings."""

    host: str = "localhost"
    port: int = 5432
    username: str
    password: SecretStr
    db_name: str = "default"

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate the host value."""
        if not v:
            raise ValueError("Host cannot be empty")
        return v


class AppSettings(BaseSettings):
    """Application settings using Pydantic Settings."""

    # Configure settings sources and behavior
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        secrets_dir="/run/secrets",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    # API settings
    api_url: Annotated[str, Field(description="API base URL")]
    api_timeout: Annotated[int, Field(30, description="Request timeout in seconds")]
    api_key: Annotated[SecretStr, Field(description="API key for authentication")]

    # Database settings
    database: DatabaseSettings

    # Application settings
    debug: Annotated[bool, Field(False, description="Enable debug mode")]
    log_level: Annotated[str, Field("INFO", description="Logging level")]
    temp_dir: Optional[Path] = Field(None, description="Temporary directory")

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v: str) -> str:
        """Validate that the API URL is valid."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("API URL must start with http:// or https://")
        return v.rstrip("/")  # Remove trailing slash if present


def example_1_direct_initialization() -> None:
    """Example 1: Create configuration with direct initialization."""
    print("\nExample 1: Direct Initialization")
    print("--------------------------------")

    # Create settings with direct values
    settings = AppSettings(
        api_url="https://api.example.com",
        api_timeout=30,
        api_key="super-secret-key",
        database=DatabaseSettings(
            host="db.example.com",
            username="dbuser",
            password="dbpass",  # noqa: S106
        ),
        debug=True,
    )

    # Access configuration values
    print(f"API URL: {settings.api_url}")
    print(f"API Timeout: {settings.api_timeout}s")
    print(f"API Key: {'*' * len(settings.api_key.get_secret_value())}")
    print(f"Database Host: {settings.database.host}")
    print(f"Database Username: {settings.database.username}")
    print(
        f"Database Password: {'*' * len(settings.database.password.get_secret_value())}",
    )
    print(f"Debug Mode: {settings.debug}")
    print(f"Log Level: {settings.log_level}")


def example_2_env_variables() -> None:
    """Example 2: Load configuration from environment variables."""
    print("\nExample 2: Environment Variables")
    print("-------------------------------")

    # Set environment variables
    os.environ["APP_API_URL"] = "https://env-api.example.com"
    os.environ["APP_API_KEY"] = "env-secret-key"
    os.environ["APP_DATABASE__HOST"] = "env-db.example.com"
    os.environ["APP_DATABASE__USERNAME"] = "env-dbuser"
    os.environ["APP_DATABASE__PASSWORD"] = "env-dbpass"  # noqa: S105
    os.environ["APP_DEBUG"] = "true"

    # Load from environment variables
    settings = AppSettings()

    # Access configuration values
    print(f"API URL: {settings.api_url}")
    print(f"API Key: {'*' * len(settings.api_key.get_secret_value())}")
    print(f"Database Host: {settings.database.host}")
    print(f"Database Username: {settings.database.username}")
    print(f"Debug Mode: {settings.debug}")


def example_3_dotenv_file() -> None:
    """Example 3: Load configuration from .env file."""
    print("\nExample 3: Dotenv File")
    print("----------------------")

    # Create temporary .env file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, prefix=".env") as f:
        f.write("APP_API_URL=https://dotenv-api.example.com\n")
        f.write("APP_API_KEY=dotenv-secret-key\n")
        f.write("APP_DATABASE__HOST=dotenv-db.example.com\n")
        f.write("APP_DATABASE__USERNAME=dotenv-dbuser\n")
        f.write("APP_DATABASE__PASSWORD=dotenv-dbpass\n")
        f.write("APP_DEBUG=false\n")
        env_path = f.name

    try:
        # Clear environment variables from previous example
        for key in list(os.environ.keys()):
            if key.startswith("APP_"):
                del os.environ[key]

        # Load from .env file
        settings = AppSettings(_env_file=env_path)

        # Access configuration values
        print(f"API URL: {settings.api_url}")
        print(f"API Key: {'*' * len(settings.api_key.get_secret_value())}")
        print(f"Database Host: {settings.database.host}")
        print(f"Database Username: {settings.database.username}")
        print(f"Debug Mode: {settings.debug}")
    finally:
        # Clean up
        Path(env_path).unlink()


def example_4_config_profiles() -> None:
    """Example 4: Use configuration profiles."""
    print("\nExample 4: Configuration Profiles")
    print("--------------------------------")

    # Create temporary .env.dev file
    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, prefix=".env", suffix=".dev",
    ) as f:
        f.write("API_URL=https://dev-api.example.com\n")
        f.write("API_USERNAME=dev-user\n")
        f.write("API_PASSWORD=dev-pass\n")
        f.write("API_TIMEOUT=45\n")
        f.write("API_DEBUG=true\n")
        dev_env_path = f.name

    # Create temporary .env.prod file
    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, prefix=".env", suffix=".prod",
    ) as f:
        f.write("API_URL=https://prod-api.example.com\n")
        f.write("API_USERNAME=prod-user\n")
        f.write("API_PASSWORD=prod-pass\n")
        f.write("API_TIMEOUT=30\n")
        f.write("API_DEBUG=false\n")
        prod_env_path = f.name

    try:
        # Temporarily modify function to work with our temp files
        original_glob = Path.glob

        def mock_glob(self, pattern) -> None:
            if pattern == ".env.*":
                return [Path(dev_env_path), Path(prod_env_path)]
            return original_glob(self, pattern)

        Path.glob = mock_glob

        # List available profiles
        profiles = apix.list_available_profiles()
        print(f"Available profiles: {profiles}")

        # Create patched methods to load our profiles
        with (
            mock.patch("dc_api_x.config.Path.exists", return_value=True),
            mock.patch("dc_api_x.config.load_dotenv"),
            mock.patch(
                "dc_api_x.config.os.environ",
                {
                    "API_DEV_URL": "https://dev-api.example.com",
                    "API_DEV_USERNAME": "dev-user",
                    "API_DEV_PASSWORD": "dev-pass",
                    "API_PROD_URL": "https://prod-api.example.com",
                    "API_PROD_USERNAME": "prod-user",
                    "API_PROD_PASSWORD": "prod-pass",
                },
            ),
        ):

            # Get contents of dev profile
            dev_config = apix.Config.from_profile("dev")
            print(f"Dev Profile - URL: {dev_config.url}")
            print(f"Dev Profile - Username: {dev_config.username}")
            print(
                f"Dev Profile - Password: {'*' * len(dev_config.password.get_secret_value())}",
            )

            # Get contents of prod profile
            prod_config = apix.Config.from_profile("prod")
            print(f"Prod Profile - URL: {prod_config.url}")
            print(f"Prod Profile - Username: {prod_config.username}")
            print(
                f"Prod Profile - Password: {'*' * len(prod_config.password.get_secret_value())}",
            )
    finally:
        # Clean up
        Path(dev_env_path).unlink()
        Path(prod_env_path).unlink()
        Path.glob = original_glob


def example_5_file_operations() -> None:
    """Example 5: Save and load configuration from files."""
    print("\nExample 5: File Operations")
    print("-------------------------")

    # Create configuration
    config = apix.Config(
        url="https://api.example.com",
        username="fileuser",
        password="filepass",  # noqa: S106
        timeout=60,
        debug=True,
    )

    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Save configuration to file
        config.save(temp_path)
        print(f"Configuration saved to {temp_path}")

        # Load configuration from file
        loaded_config = apix.Config.from_file(temp_path)

        # Verify loaded configuration
        print(f"Loaded URL: {loaded_config.url}")
        print(f"Loaded Username: {loaded_config.username}")
        print(
            f"Loaded Password: {'*' * len(loaded_config.password.get_secret_value())}",
        )
        print(f"Loaded Timeout: {loaded_config.timeout}")
        print(f"Loaded Debug: {loaded_config.debug}")
    finally:
        # Clean up
        Path(temp_path).unlink()


def example_6_model_dump() -> None:
    """Example 6: Convert configuration to different formats."""
    print("\nExample 6: Configuration Conversions")
    print("----------------------------------")

    # Create configuration
    settings = AppSettings(
        api_url="https://api.example.com",
        api_timeout=30,
        api_key="conversion-secret-key",
        database=DatabaseSettings(
            host="db.example.com",
            username="dbuser",
            password="dbpass",  # noqa: S106
        ),
        debug=True,
    )

    # Convert to dictionary (excluding None values)
    settings_dict[str, Any] = settings.model_dump(exclude_none=True, exclude_secrets=False)
    print("Dictionary representation:")
    for key, value in settings_dict.items():
        if key == "api_key" or (key == "database" and "password" in value):
            # Mask sensitive values
            if key == "api_key":
                print(f"  {key}: ****")
            else:
                database = value.copy()
                database["password"] = "****"  # noqa: S105
                print(f"  {key}: {database}")
        else:
            print(f"  {key}: {value}")

    # Convert to JSON
    settings_json = settings.model_dump_json(exclude_none=True)
    print(f"\nJSON representation (length: {len(settings_json)} chars)")

    # Convert specific fields only
    api_only = settings.model_dump(include={"api_url", "api_timeout"})
    print("\nAPI fields only:")
    for key, value in api_only.items():
        print(f"  {key}: {value}")


def example_7_config_reload() -> None:
    """Example 7: Reload configuration at runtime."""
    print("\nExample 7: Configuration Reloading")
    print("--------------------------------")

    # Set initial environment variables
    os.environ["API_URL"] = "https://initial-api.example.com"
    os.environ["API_USERNAME"] = "initial-user"
    os.environ["API_PASSWORD"] = "initial-pass"  # noqa: S105

    # Create initial config
    config = apix.Config()
    print("Initial configuration:")
    print(f"  URL: {config.url}")
    print(f"  Username: {config.username}")
    print(f"  Password: {'*' * len(config.password.get_secret_value())}")

    # Change environment variables
    os.environ["API_URL"] = "https://updated-api.example.com"
    os.environ["API_USERNAME"] = "updated-user"
    os.environ["API_PASSWORD"] = "updated-pass"  # noqa: S105

    # Configuration hasn't changed yet
    print("\nBefore reload:")
    print(f"  URL: {config.url}")
    print(f"  Username: {config.username}")
    print(f"  Password: {'*' * len(config.password.get_secret_value())}")

    # Reload configuration
    config.model_reload()

    # Configuration has been updated
    print("\nAfter reload:")
    print(f"  URL: {config.url}")
    print(f"  Username: {config.username}")
    print(f"  Password: {'*' * len(config.password.get_secret_value())}")


def example_8_customizing_sources() -> None:
    """Example 8: Customizing settings sources."""
    print("\nExample 8: Customizing Sources")
    print("----------------------------")

    class CustomSettings(BaseSettings):
        """Settings with custom sources configuration."""

        model_config = SettingsConfigDict(env_prefix="CUSTOM_")

        name: str = "default"
        value: int = 42

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            # Change priority: env vars first, then .env, then init params
            return env_settings, dotenv_settings, init_settings, file_secret_settings

    # Set environment variables
    os.environ["CUSTOM_NAME"] = "from-environment"

    # Create settings with parameters
    settings = CustomSettings(name="from-init")

    # Environment variables take precedence due to customized sources
    print(f"Name value: {settings.name}")  # Should be "from-environment"
    print(f"Value: {settings.value}")


def main() -> None:
    """Run all examples."""
    print("DCApiX Pydantic Settings Examples")
    print("================================")

    try:
        # Run examples
        example_1_direct_initialization()
        example_2_env_variables()
        example_3_dotenv_file()
        example_4_config_profiles()
        example_5_file_operations()
        example_6_model_dump()
        example_7_config_reload()
        example_8_customizing_sources()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up environment variables
        for key in list(os.environ.keys()):
            if key.startswith(("APP_", "API_", "CUSTOM_")):
                del os.environ[key]


if __name__ == "__main__":
    main()
