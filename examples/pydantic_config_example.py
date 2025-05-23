#!/usr/bin/env python3
"""
Example of using DCApiX configuration with Pydantic Settings.

This example demonstrates different ways to load and manage configuration
using Pydantic Settings in DCApiX.
"""

import os
import tempfile
from pathlib import Path

import dc_api_x as apix


def main():
    """Run the configuration example."""
    print("DCApiX Configuration Examples")
    print("============================\n")

    # Example 1: Direct initialization
    print("Example 1: Direct initialization")
    print("--------------------------------")
    config = apix.Configonfig(
        url="https://api.example.com",
        username="user123",
        password="pass123",  # noqa: S106
        timeout=30,
        debug=True,
    )
    print(f"URL: {config.url}")
    print(f"Username: {config.username}")
    print(f"Password: {'*' * len(config.password.get_secret_value())}")
    print(f"Timeout: {config.timeout}")
    print(f"Debug: {config.debug}")

    # Example 2: Loading from environment variables
    print("\nExample 2: Loading from environment variables")
    print("-------------------------------------------")
    # Set environment variables
    os.environ["API_URL"] = "https://api.fromenv.com"
    os.environ["API_USERNAME"] = "envuser"
    os.environ["API_PASSWORD"] = "envpass"  # noqa: S105
    os.environ["API_DEBUG"] = "true"

    # Load from environment
    env_config = apix.Config()
    print(f"URL: {env_config.url}")
    print(f"Username: {env_config.username}")
    print(f"Password: {'*' * len(env_config.password.get_secret_value())}")
    print(f"Timeout: {env_config.timeout} (default)")
    print(f"Debug: {env_config.debug}")

    # Example 3: Saving and loading from a file
    print("\nExample 3: Saving and loading from a file")
    print("----------------------------------------")
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Save configuration to file
        config.save(temp_path)
        print(f"Configuration saved to: {temp_path}")

        # Load configuration from file
        loaded_config = apix.Config.from_file(temp_path)
        print(f"Loaded URL: {loaded_config.url}")
        print(f"Loaded Username: {loaded_config.username}")
        print(f"Loaded Debug: {loaded_config.debug}")
    finally:
        # Clean up
        Path(temp_path).unlink()

    # Example 4: Configuration profiles
    print("\nExample 4: Configuration profiles")
    print("--------------------------------")
    # Create a .env.dev file (for demonstration)
    with Path(".env.dev").open("w") as f:
        f.write("API_URL=https://dev-api.example.com\n")
        f.write("API_USERNAME=dev-user\n")
        f.write("API_PASSWORD=dev-pass\n")

    try:
        # List available profiles
        profiles = apix.list_available_profiles()
        print(f"Available profiles: {profiles}")

        # Load profile if it exists
        if "dev" in profiles:
            dev_config = apix.Config.from_profile("dev")
            print(f"Dev URL: {dev_config.url}")
            print(f"Dev Username: {dev_config.username}")
            print(f"Dev Password: {'*' * len(dev_config.password.get_secret_value())}")
    finally:
        # Clean up
        Path(".env.dev").unlink()

    # Example 5: Custom configuration
    print("\nExample 5: Reloading configuration")
    print("--------------------------------")

    # Original environment values
    print("Original configuration:")
    config = apix.Config()
    print(f"URL: {config.url}")

    # Change environment variables
    os.environ["API_URL"] = "https://updated-api.example.com"

    # Reload configuration
    print("After environment change (before reload):")
    print(f"URL: {config.url}")

    # Reload configuration
    config.model_reload()
    print("After reload:")
    print(f"URL: {config.url}")


if __name__ == "__main__":
    main()
