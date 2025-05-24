#!/usr/bin/env python3
"""
Example of using DCApiX configuration with Pydantic Settings.

This script demonstrates how to use the Config class to configure the
ApiClient, load different profiles, and work with secure credentials.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import dc_api_x as apix
from dc_api_x.config import Config, list_available_profiles


def print_section(title: str) -> None:
    """Print a section title."""
    print(f"\n{title}")
    print("=" * len(title))


def example_basic_config() -> Config:
    """Example: Basic configuration with DCApiX."""
    print_section("Basic Configuration")

    # Create a config with direct values
    config = Config(
        url="https://api.example.com",
        username="user123",
        password="pass123",  # noqa: S106
        timeout=30,
        verify_ssl=True,
        debug=True,
    )

    # Create an API client using the config
    client = apix.ApiClient.from_config(config)

    # Print client details
    print(f"Client URL: {client.url}")
    print(f"Client Auth: {client.auth}")
    print(f"Client Timeout: {client.timeout}s")
    print(f"Client Verify SSL: {client.verify_ssl}")
    print(f"Client Debug Mode: {client.debug}")

    return config


def example_environment_vars() -> Config:
    """Example: Load configuration from environment variables."""
    print_section("Environment Variables Configuration")

    # Set environment variables
    os.environ["API_URL"] = "https://env-api.example.com"
    os.environ["API_USERNAME"] = "env-user"
    os.environ["API_PASSWORD"] = "env-pass"  # noqa: S105
    os.environ["API_TIMEOUT"] = "45"
    os.environ["API_MAX_RETRIES"] = "3"
    os.environ["API_DEBUG"] = "true"

    # Load configuration from environment variables
    config = Config()

    # Print configuration details
    print(f"Config URL: {config.url}")
    print(f"Config Username: {config.username}")
    print(f"Config Password: {'*' * len(config.password.get_secret_value())}")
    print(f"Config Timeout: {config.timeout}s")
    print(f"Config Max Retries: {config.max_retries}")
    print(f"Config Debug Mode: {config.debug}")

    return config


def example_dotenv_file() -> Config:
    """Example: Load configuration from a .env file."""
    print_section("Dotenv File Configuration")

    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        env_path = temp_file.name
        temp_file.write("API_URL=https://dotenv-api.example.com\n")
        temp_file.write("API_USERNAME=dotenv-user\n")
        temp_file.write("API_PASSWORD=dotenv-pass\n")
        temp_file.write("API_TIMEOUT=60\n")
        temp_file.write("API_DEBUG=false\n")

    # Save the original env file location
    original_env_file = apix.CONFIG_DEFAULT_ENV_FILE

    try:
        # Set the env file location to our temporary file
        apix.CONFIG_DEFAULT_ENV_FILE = env_path

        # Clear any existing environment variables
        for key in list(os.environ.keys()):
            if key.startswith("API_"):
                del os.environ[key]

        # Load configuration from the .env file
        config = Config()

        # Print configuration details
        print(f"Config URL: {config.url}")
        print(f"Config Username: {config.username}")
        print(f"Config Password: {'*' * len(config.password.get_secret_value())}")
        print(f"Config Timeout: {config.timeout}s")
        print(f"Config Debug Mode: {config.debug}")

        return config
    finally:
        # Clean up
        Path(env_path).unlink()
        apix.CONFIG_DEFAULT_ENV_FILE = original_env_file


def example_profiles() -> tuple[Config, Config]:
    """Example: Work with configuration profiles."""
    print_section("Configuration Profiles")

    # Create temporary profile env files
    dev_path = create_profile_env(
        "dev",
        {
            "URL": "https://dev-api.example.com",
            "USERNAME": "dev-user",
            "PASSWORD": "dev-pass",
            "TIMEOUT": "45",
            "DEBUG": "true",
        },
    )

    prod_path = create_profile_env(
        "prod",
        {
            "URL": "https://prod-api.example.com",
            "USERNAME": "prod-user",
            "PASSWORD": "prod-pass",
            "TIMEOUT": "30",
            "DEBUG": "false",
        },
    )

    try:
        # Override Path.glob to return our temporary files
        original_glob = Path.glob

        def mock_glob(self, pattern) -> None:
            if pattern == f"{apix.CONFIG_DEFAULT_ENV_FILE}.*":
                return [Path(dev_path), Path(prod_path)]
            return original_glob(self, pattern)

        Path.glob = mock_glob

        # List available profiles
        profiles = list_available_profiles()
        print(f"Available profiles: {profiles}")

        # Use mock to simulate profile loading
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

            # Load the development profile
            dev_config = Config.from_profile("dev")
            print("\nDevelopment Profile:")
            print(f"  URL: {dev_config.url}")
            print(f"  Username: {dev_config.username}")
            print(f"  Debug: {dev_config.debug}")

            # Load the production profile
            prod_config = Config.from_profile("prod")
            print("\nProduction Profile:")
            print(f"  URL: {prod_config.url}")
            print(f"  Username: {prod_config.username}")
            print(f"  Debug: {prod_config.debug}")

            return dev_config, prod_config
    finally:
        # Clean up
        Path(dev_path).unlink()
        Path(prod_path).unlink()
        Path.glob = original_glob


def example_save_load() -> Config:
    """Example: Save and load configuration to/from file."""
    print_section("Save and Load Configuration")

    # Create a configuration
    config = Config(
        url="https://api.example.com",
        username="file-user",
        password="file-pass",  # noqa: S106
        timeout=30,
        max_retries=5,
        debug=True,
    )

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Save configuration to file
        config.save(temp_path)
        print(f"Configuration saved to: {temp_path}")

        # Load configuration from file
        loaded_config = Config.from_file(temp_path)

        # Verify loaded configuration
        print("\nLoaded configuration:")
        print(f"  URL: {loaded_config.url}")
        print(f"  Username: {loaded_config.username}")
        print(f"  Password: {'*' * len(loaded_config.password.get_secret_value())}")
        print(f"  Timeout: {loaded_config.timeout}")
        print(f"  Max Retries: {loaded_config.max_retries}")
        print(f"  Debug: {loaded_config.debug}")

        return loaded_config
    finally:
        # Clean up
        Path(temp_path).unlink()


def example_client_from_config() -> apix.ApiClient:
    """Example: Create an API client from configuration."""
    print_section("Create API Client from Configuration")

    # Create a configuration
    config = Config(
        url="https://api.example.com",
        username="client-user",
        password="client-pass",  # noqa: S106
        timeout=30,
        verify_ssl=True,
        max_retries=3,
        debug=True,
    )

    # Create an API client from the configuration
    client = apix.ApiClient.from_config(config)

    # Print client details
    print("Created API client with the following configuration:")
    print(f"  Base URL: {client.url}")
    print(f"  Authentication: Basic Auth (username: {config.username})")
    print(f"  Timeout: {client.timeout}s")
    print(f"  Verify SSL: {client.verify_ssl}")
    print(f"  Debug Mode: {client.debug}")

    return client


def example_convert_to_dict() -> dict[str, Any]:
    """Example: Convert configuration to dictionary."""
    print_section("Convert Configuration to Dictionary")

    # Create a configuration
    config = Config(
        url="https://api.example.com",
        username="dict-user",
        password="dict-pass",  # noqa: S106
        timeout=30,
        verify_ssl=True,
        max_retries=3,
        debug=True,
        environment="testing",
    )

    # Convert to dictionary
    config_dict[str, Any] = config.model_dump(exclude_none=True)

    # Print dictionary representation
    print("Configuration as dictionary:")
    for key, value in config_dict.items():
        if key == "password":
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")

    return config_dict


def example_model_reload() -> None:
    """Example: Reload configuration after changing env vars."""
    print_section("Configuration Model Reload")

    # Setup initial environment
    os.environ["API_URL"] = "https://initial.example.com"
    os.environ["API_USERNAME"] = "initial-user"

    # Create configuration
    config = Config()
    print(f"Initial URL: {config.url}")
    print(f"Initial Username: {config.username}")

    # Change environment variables
    os.environ["API_URL"] = "https://updated.example.com"
    os.environ["API_USERNAME"] = "updated-user"

    # Reload configuration
    config.model_reload()
    print(f"After reload - URL: {config.url}")
    print(f"After reload - Username: {config.username}")


def create_profile_env(profile_name: str, values: dict[str, Any]) -> str:
    """Create a temporary .env file for a profile.

    Args:
        profile_name: Name of the profile
        values: Dictionary of values to write to the file

    Returns:
        Path to the created file
    """
    with tempfile.NamedTemporaryFile(
        mode="w+",
        delete=False,
        prefix=f".env.{profile_name}",
    ) as f:
        for key, value in values.items():
            f.write(f"API_{key}={value}\n")
        return f.name


def main() -> None:
    """Run the DC-APIx configuration examples."""
    print("DC-APIx Configuration Examples")
    print("==============================")

    try:
        # Run the examples
        example_basic_config()
        example_environment_vars()
        example_dotenv_file()
        example_profiles()
        example_save_load()
        example_client_from_config()
        example_convert_to_dict()
        example_model_reload()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up environment variables
        for key in list(os.environ.keys()):
            if key.startswith("API_"):
                del os.environ[key]


if __name__ == "__main__":
    main()
