"""
Tests for the Config module.
"""

import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from dc_api_x.config import (
    Config,
    ConfigProfile,
    list_available_profiles,
    load_config_from_env,
)
from dc_api_x.exceptions import ConfigError
from tests.constants import CUSTOM_TIMEOUT, DEFAULT_TIMEOUT, MAX_RETRIES


class TestConfig:
    """Test suite for the Config class."""

    def test_init_with_parameters(self) -> None:
        """Test initialization with parameters."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",  # SecretStr is applied automatically
            timeout=30,
            verify_ssl=True,
            max_retries=5,
            retry_backoff=1.0,
            debug=True,
        )

        assert config.url == "https://api.example.com"
        assert config.username == "testuser"
        assert isinstance(config.password, SecretStr)
        assert config.password.get_secret_value() == "testpass"
        assert config.timeout == 30
        assert config.verify_ssl is True
        assert config.max_retries == 5
        assert config.retry_backoff == 1.0
        assert config.debug is True

    def test_init_with_defaults(self) -> None:
        """Test initialization with defaults."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        assert config.url == "https://api.example.com"
        assert config.username == "testuser"
        assert isinstance(config.password, SecretStr)
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.verify_ssl is True
        assert config.max_retries == MAX_RETRIES
        assert config.retry_backoff == 0.5
        assert config.debug is False

    def test_validates_url(self) -> None:
        """Test URL validation."""
        # Test with valid URLs
        config = Config(
            url="https://api.example.com/",
            username="testuser",
            password="testpass",
        )
        assert config.url == "https://api.example.com"  # Trailing slash removed

        # Test with invalid URLs
        with pytest.raises(ValueError, match="must start with http:// or https://"):
            Config(
                url="invalid-url",
                username="testuser",
                password="testpass",
            )

        with pytest.raises(ValueError, match="empty"):
            Config(
                url="",
                username="testuser",
                password="testpass",
            )

    def test_validates_config(self) -> None:
        """Test cross-field validation."""
        # Test with valid data
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
            timeout=30,
            max_retries=3,
            retry_backoff=0.5,
        )
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_backoff == 0.5

        # Test with invalid max_retries
        with pytest.raises(
            ValueError,
            match="max_retries must be a non-negative integer",
        ):
            Config(
                url="https://api.example.com",
                username="testuser",
                password="testpass",
                max_retries=-1,
            )

        # Test with invalid retry_backoff
        with pytest.raises(ValueError, match="retry_backoff must be a positive number"):
            Config(
                url="https://api.example.com",
                username="testuser",
                password="testpass",
                retry_backoff=0,
            )

        # Test with invalid timeout
        with pytest.raises(ValueError, match="timeout must be a positive integer"):
            Config(
                url="https://api.example.com",
                username="testuser",
                password="testpass",
                timeout=0,
            )

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
            timeout=CUSTOM_TIMEOUT,
            debug=True,
        )

        config_dict: dict[str, Any] = config.to_dict()
        assert config_dict["url"] == "https://api.example.com"
        assert config_dict["username"] == "testuser"
        assert config_dict["password"] == "testpass"  # Plain text in dict
        assert config_dict["timeout"] == CUSTOM_TIMEOUT
        assert config_dict["debug"] is True

    def test_model_dump_custom(self) -> None:
        """Test custom model_dump method."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
            timeout=CUSTOM_TIMEOUT,
            debug=True,
        )

        # With exclude_secrets=True (default)
        config_dict: dict[str, Any] = config.model_dump_custom()
        assert config_dict["url"] == "https://api.example.com"
        assert config_dict["username"] == "testuser"
        assert "password" in config_dict  # Password is included but masked
        assert config_dict["timeout"] == CUSTOM_TIMEOUT
        assert config_dict["debug"] is True

        # With exclude_secrets=False
        config_dict: dict[str, Any] = config.model_dump_custom(exclude_secrets=False)
        assert config_dict["url"] == "https://api.example.com"
        assert config_dict["username"] == "testuser"
        assert config_dict["password"] == "testpass"  # Password is revealed
        assert config_dict["timeout"] == CUSTOM_TIMEOUT
        assert config_dict["debug"] is True

    def test_save_load_json(self) -> None:
        """Test saving and loading config as JSON."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
            timeout=CUSTOM_TIMEOUT,
            verify_ssl=False,
            debug=True,
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Save configuration to temp file
            config.save(temp_path)

            # Load configuration from temp file
            loaded_config = Config.from_file(temp_path)

            # Verify loaded configuration
            assert loaded_config.url == "https://api.example.com"
            assert loaded_config.username == "testuser"
            assert isinstance(loaded_config.password, SecretStr)
            assert loaded_config.password.get_secret_value() == "testpass"
            assert loaded_config.timeout == CUSTOM_TIMEOUT
            assert loaded_config.verify_ssl is False
            assert loaded_config.debug is True
        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_save_invalid_format(self) -> None:
        """Test saving with invalid format."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Attempt to save with invalid format
            with pytest.raises(ValueError, match="Unsupported file format"):
                config.save(temp_path)
        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_from_file_not_found(self) -> None:
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            Config.from_file("nonexistent.json")

    def test_from_profile(self) -> None:
        """Test loading from profile."""
        # Create a patch for the settings config dict
        orig_config = Config.model_config.copy()
        temp_secrets_dir = tempfile.mkdtemp()

        try:
            # Update model_config with a temporary directory
            Config.model_config["secrets_dir"] = temp_secrets_dir

            # Test using the prepared .env.test file
            with (
                patch("pathlib.Path.exists", return_value=True),
                patch("dc_api_x.config.load_dotenv", return_value=True),
                patch.dict(
                    "os.environ",
                    {
                        "API_URL": "https://test-api.example.com",
                        "API_USERNAME": "testuser",
                        "API_PASSWORD": "testpass",
                        "API_TIMEOUT": "45",
                        "API_DEBUG": "true",
                    },
                ),
            ):
                config = Config.from_profile("test")

                # Verify loaded configuration
                assert config.url == "https://test-api.example.com"
                assert config.username == "testuser"
                assert isinstance(config.password, SecretStr)
                assert config.password.get_secret_value() == "testpass"
                assert config.timeout == 45
                assert config.debug is True
        finally:
            # Restore original model_config
            Config.model_config = orig_config
            # Clean up temp directory
            import shutil

            shutil.rmtree(temp_secrets_dir, ignore_errors=True)

    def test_from_profile_not_found(self) -> None:
        """Test loading from non-existent profile."""
        with (
            patch("pathlib.Path.exists", return_value=False),
            pytest.raises(
                ConfigError,
                match="Profile file .env.nonexistent not found",
            ),
        ):
            Config.from_profile("nonexistent")

    def test_from_profile_missing_vars(self) -> None:
        """Test loading from profile with missing variables."""
        # Create a temporary env file with missing required variables
        with tempfile.NamedTemporaryFile(prefix=".env.", delete=False) as temp_file:
            temp_file.write(b"API_DEBUG=true\n")
            temp_path = temp_file.name

        # Create a patch for the settings config dict
        orig_config = Config.model_config.copy()
        temp_secrets_dir = tempfile.mkdtemp()

        try:
            # Update model_config with a temporary directory
            Config.model_config["secrets_dir"] = temp_secrets_dir

            # Mock the file existence check
            with (
                patch("pathlib.Path.exists", return_value=True),
                patch("dc_api_x.config.load_dotenv", return_value=True),
                pytest.raises(
                    ConfigError,
                    match="Missing required configuration variables",
                ),
            ):
                Config.from_profile(temp_path.split(".")[-1])
        finally:
            # Clean up
            Path(temp_path).unlink()
            # Restore original model_config
            Config.model_config = orig_config
            # Clean up temp directory
            import shutil

            shutil.rmtree(temp_secrets_dir, ignore_errors=True)

    def test_model_reload(self) -> None:
        """Test reloading configuration from sources."""
        # Initial configuration
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password="testpass",
        )

        # Mock the environment variables
        new_env = {
            "API_URL": "https://updated-api.example.com",
            "API_USERNAME": "updateduser",
            "API_PASSWORD": "updatedpass",
        }

        # Apply new environment and reload
        with patch.dict(os.environ, new_env, clear=True):
            config.model_reload()

            # Verify updated configuration
            assert config.url == "https://updated-api.example.com"
            assert config.username == "updateduser"
            assert config.password.get_secret_value() == "updatedpass"

    def test_load_config_from_env(self) -> None:
        """Test loading configuration from environment variables."""
        # Mock environment variables
        with patch.dict(
            "os.environ",
            {
                "API_URL": "https://env-api.example.com",
                "API_USERNAME": "envuser",
                "API_PASSWORD": "envpass",
                "API_TIMEOUT": "45",
                "API_DEBUG": "true",
            },
        ):
            # Load configuration from environment
            config = load_config_from_env()

            # Verify loaded configuration
            assert config.url == "https://env-api.example.com"
            assert config.username == "envuser"
            assert config.password.get_secret_value() == "envpass"
            assert config.timeout == 45
            assert config.debug is True

    def test_load_config_from_env_failure(self) -> None:
        """Test failure to load configuration from environment variables."""
        # Mock environment with missing required variables
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(
                ConfigError,
                match="Failed to load configuration",
            ),
        ):
            load_config_from_env()


class TestConfigProfile:
    """Test suite for the ConfigProfile class."""

    def test_init(self) -> None:
        """Test initialization of ConfigProfile."""
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.example.com",
                "username": "testuser",
                "password": "testpass",
            },
        )

        assert profile.name == "test"
        assert profile.config["url"] == "https://api.example.com"
        assert profile.config["username"] == "testuser"
        assert profile.config["password"] == "testpass"

    def test_is_valid(self) -> None:
        """Test validation of ConfigProfile."""
        # Valid profile
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.example.com",
                "username": "testuser",
                "password": "testpass",
            },
        )
        assert profile.is_valid is True

        # Invalid profile (missing required keys)
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.example.com",
            },
        )
        assert profile.is_valid is False

    def test_repr(self) -> None:
        """Test string representation of ConfigProfile."""
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.example.com",
                "username": "testuser",
                "password": "testpass",
            },
        )

        repr_str = repr(profile)
        assert "test" in repr_str
        assert "https://api.example.com" in repr_str
        assert "testuser" in repr_str
        assert "testpass" not in repr_str  # Password should be masked
        assert "****" in repr_str  # Password should be masked


def test_list_available_profiles() -> None:
    """Test listing available profiles."""
    # Mock glob to return test files
    with patch(
        "pathlib.Path.glob",
        return_value=[
            Path(".env.dev"),
            Path(".env.prod"),
            Path(".env.test"),
        ],
    ):
        profiles = list_available_profiles()
        assert sorted(profiles) == sorted(["dev", "prod", "test"])
