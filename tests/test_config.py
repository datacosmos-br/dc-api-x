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
from dc_api_x.utils.exceptions import ConfigError
from tests.constants import (
    BACKOFF_FACTOR,
    CUSTOM_TIMEOUT,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    TEST_API_URL,
    TEST_CONFIG_PATH,
    TEST_PASSWORD,
    TEST_USERNAME,
)


class TestConfig:
    """Test suite for the Config class."""

    def test_init_with_parameters(self) -> None:
        """Test initialization with parameters."""
        config = Config(
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,  # SecretStr is applied automatically
            timeout=DEFAULT_TIMEOUT,
            verify_ssl=True,
            max_retries=MAX_RETRIES,
            retry_backoff=BACKOFF_FACTOR,
            debug=True,
        )

        assert config.url == TEST_API_URL
        assert config.username == TEST_USERNAME
        assert isinstance(config.password, SecretStr)
        assert config.password.get_secret_value() == TEST_PASSWORD
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.verify_ssl is True
        assert config.max_retries == MAX_RETRIES
        assert config.retry_backoff == BACKOFF_FACTOR
        assert config.debug is True

    def test_init_with_defaults(self) -> None:
        """Test initialization with defaults."""
        config = Config(
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
        )

        assert config.url == TEST_API_URL
        assert config.username == TEST_USERNAME
        assert isinstance(config.password, SecretStr)
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.verify_ssl is True
        assert config.max_retries == MAX_RETRIES
        assert config.retry_backoff == BACKOFF_FACTOR
        assert config.debug is False

    def test_validates_url(self) -> None:
        """Test URL validation."""
        # Test with valid URLs
        config = Config(
            url=f"{TEST_API_URL}/",
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
        )
        assert config.url == TEST_API_URL  # Trailing slash removed

        # Test with invalid URLs
        with pytest.raises(ValueError, match="must start with http:// or https://"):
            Config(
                url="invalid-url",
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
            )

        with pytest.raises(ValueError, match="empty"):
            Config(
                url="",
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
            )

    def test_validates_config(self) -> None:
        """Test cross-field validation."""
        # Test with valid data
        config = Config(
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            timeout=DEFAULT_TIMEOUT,
            max_retries=MAX_RETRIES,
            retry_backoff=BACKOFF_FACTOR,
        )
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.max_retries == MAX_RETRIES
        assert config.retry_backoff == BACKOFF_FACTOR

        # Test with invalid max_retries
        with pytest.raises(
            ValueError,
            match="max_retries must be a non-negative integer",
        ):
            Config(
                url=TEST_API_URL,
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
                max_retries=-1,
            )

        # Test with invalid retry_backoff
        with pytest.raises(ValueError, match="retry_backoff must be a positive number"):
            Config(
                url=TEST_API_URL,
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
                retry_backoff=0,
            )

        # Test with invalid timeout
        with pytest.raises(ValueError, match="timeout must be a positive integer"):
            Config(
                url=TEST_API_URL,
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
                timeout=0,
            )

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        config = Config(
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            timeout=CUSTOM_TIMEOUT,
            debug=True,
        )

        config_dict: dict[str, Any] = config.to_dict()
        assert config_dict["url"] == TEST_API_URL
        assert config_dict["username"] == TEST_USERNAME
        assert config_dict["password"] == TEST_PASSWORD  # Plain text in dict
        assert config_dict["timeout"] == CUSTOM_TIMEOUT
        assert config_dict["debug"] is True

    def test_model_dump_custom(self) -> None:
        """Test custom model_dump method."""
        config = Config(
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            timeout=CUSTOM_TIMEOUT,
            debug=True,
        )

        # With exclude_secrets=True (default)
        config_dict = config.model_dump_custom()
        assert config_dict["url"] == TEST_API_URL
        assert config_dict["username"] == TEST_USERNAME
        assert "password" in config_dict  # Password is included but masked
        assert config_dict["timeout"] == CUSTOM_TIMEOUT
        assert config_dict["debug"] is True

        # With exclude_secrets=False
        config_dict = config.model_dump_custom(exclude_secrets=False)
        assert config_dict["url"] == TEST_API_URL
        assert config_dict["username"] == TEST_USERNAME
        assert config_dict["password"] == TEST_PASSWORD  # Password is revealed
        assert config_dict["timeout"] == CUSTOM_TIMEOUT
        assert config_dict["debug"] is True

    def test_save_load_json(self) -> None:
        """Test saving and loading config as JSON."""
        config = Config(
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
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

            # Check all fields were loaded correctly
            assert loaded_config.url == TEST_API_URL
            assert loaded_config.username == TEST_USERNAME
            assert loaded_config.password.get_secret_value() == TEST_PASSWORD
            assert loaded_config.timeout == CUSTOM_TIMEOUT
            assert loaded_config.verify_ssl is False
            assert loaded_config.debug is True
        finally:
            # Clean up the temp file
            Path(temp_path).unlink()

    def test_save_invalid_format(self) -> None:
        """Test saving with an invalid format."""
        config = Config(
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
        )
        with pytest.raises(ValueError, match="Unsupported format"):
            config.save("config.txt")

    def test_from_file_not_found(self) -> None:
        """Test loading from a non-existent file."""
        with pytest.raises(ConfigError, match="not found"):
            Config.from_file("nonexistent_config.json")

    def test_from_profile(self) -> None:
        """Test loading from a profile."""
        # Create a temporary config file for testing
        config_content = f"""
        [default]
        url = {TEST_API_URL}
        username = {TEST_USERNAME}
        password = {TEST_PASSWORD}
        timeout = {CUSTOM_TIMEOUT}
        verify_ssl = False
        debug = True
        """
        with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp_file:
            temp_file.write(config_content.encode("utf-8"))
            temp_path = temp_file.name

        try:
            # Mock the config file path
            with patch("dc_api_x.config.CONFIG_PATH", temp_path):
                config = Config.from_profile("default")
                assert config.url == TEST_API_URL
                assert config.username == TEST_USERNAME
                assert config.password.get_secret_value() == TEST_PASSWORD
                assert config.timeout == CUSTOM_TIMEOUT
                assert config.verify_ssl is False
                assert config.debug is True
        finally:
            # Clean up the temp file
            Path(temp_path).unlink()

    def test_from_profile_not_found(self) -> None:
        """Test loading from a non-existent profile."""
        # Create a temporary config file for testing
        config_content = """
        [default]
        url = https://api.example.com
        """
        with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp_file:
            temp_file.write(config_content.encode("utf-8"))
            temp_path = temp_file.name

        try:
            # Mock the config file path
            with (
                patch("dc_api_x.config.CONFIG_PATH", temp_path),
                pytest.raises(ConfigError, match="not found"),
            ):
                Config.from_profile("nonexistent")
        finally:
            # Clean up the temp file
            Path(temp_path).unlink()

    def test_from_profile_missing_vars(self) -> None:
        """Test loading from a profile with missing variables."""
        # Create a temporary config file for testing
        config_content = """
        [default]
        url = https://api.example.com
        # Missing username and password
        """
        with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp_file:
            temp_file.write(config_content.encode("utf-8"))
            temp_path = temp_file.name

        try:
            # Mock the config file path
            with (
                patch("dc_api_x.config.CONFIG_PATH", temp_path),
                pytest.raises(ConfigError, match="missing"),
            ):
                Config.from_profile("default")
        finally:
            # Clean up the temp file
            Path(temp_path).unlink()

    def test_model_reload(self) -> None:
        """Test model reload method."""
        # Mock the storage adapter
        mock_adapter = {
            "save": lambda _data, _format: None,
            "load": lambda _path: {
                "url": TEST_API_URL,
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
                "timeout": CUSTOM_TIMEOUT,
                "debug": True,
            },
        }

        # Create a config with a mock storage adapter
        config = Config(
            url="https://old-api.example.com",
            username="old-user",
            password="old-pass",
            timeout=30,
            debug=False,
        )

        # Reload the config
        with patch("dc_api_x.config.CONFIG_STORAGE_ADAPTERS", {"json": mock_adapter}):
            config.reload(TEST_CONFIG_PATH)

            # Check all fields were reloaded correctly
            assert config.url == TEST_API_URL
            assert config.username == TEST_USERNAME
            assert config.password.get_secret_value() == TEST_PASSWORD
            assert config.timeout == CUSTOM_TIMEOUT
            assert config.debug is True

    def test_load_config_from_env(self) -> None:
        """Test loading config from environment variables."""
        # Mock environment variables
        mock_env = {
            "DC_API_URL": TEST_API_URL,
            "DC_API_USERNAME": TEST_USERNAME,
            "DC_API_PASSWORD": TEST_PASSWORD,
            "DC_API_TIMEOUT": str(CUSTOM_TIMEOUT),
            "DC_API_VERIFY_SSL": "False",
            "DC_API_DEBUG": "True",
        }

        with patch.dict(os.environ, mock_env, clear=True):
            config = load_config_from_env()
            assert config.url == TEST_API_URL
            assert config.username == TEST_USERNAME
            assert config.password.get_secret_value() == TEST_PASSWORD
            assert config.timeout == CUSTOM_TIMEOUT
            assert config.verify_ssl is False
            assert config.debug is True

    def test_load_config_from_env_failure(self) -> None:
        """Test failure when loading config from environment variables."""
        # Mock environment variables with missing required values
        mock_env = {
            "DC_API_URL": TEST_API_URL,
            # Missing username and password
        }

        with (
            patch.dict(os.environ, mock_env, clear=True),
            pytest.raises(ConfigError, match="Missing required"),
        ):
            load_config_from_env()


class TestConfigProfile:
    """Test suite for the ConfigProfile class."""

    def test_init(self) -> None:
        """Test initialization."""
        profile = ConfigProfile(
            name="test",
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            timeout=CUSTOM_TIMEOUT,
            verify_ssl=False,
            debug=True,
        )

        assert profile.name == "test"
        assert profile.url == TEST_API_URL
        assert profile.username == TEST_USERNAME
        assert profile.password == TEST_PASSWORD
        assert profile.timeout == CUSTOM_TIMEOUT
        assert profile.verify_ssl is False
        assert profile.debug is True

    def test_is_valid(self) -> None:
        """Test validity check."""
        # Valid profile with all required fields
        profile = ConfigProfile(
            name="test",
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
        )
        assert profile.is_valid() is True

        # Invalid profile missing URL
        profile = ConfigProfile(
            name="test",
            url="",
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
        )
        assert profile.is_valid() is False

        # Invalid profile missing username
        profile = ConfigProfile(
            name="test",
            url=TEST_API_URL,
            username="",
            password=TEST_PASSWORD,
        )
        assert profile.is_valid() is False

        # Invalid profile missing password
        profile = ConfigProfile(
            name="test",
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password="",
        )
        assert profile.is_valid() is False

    def test_repr(self) -> None:
        """Test string representation."""
        profile = ConfigProfile(
            name="test",
            url=TEST_API_URL,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            timeout=CUSTOM_TIMEOUT,
            verify_ssl=False,
            debug=True,
        )

        repr_str = repr(profile)
        assert "test" in repr_str
        assert TEST_API_URL in repr_str
        assert TEST_USERNAME in repr_str
        assert "******" in repr_str  # Password should be masked


def test_list_available_profiles() -> None:
    """Test listing available profiles."""
    # Create a temporary config file for testing
    config_content = """
    [default]
    url = https://api.example.com
    username = user1
    password = pass1

    [test]
    url = https://test.example.com
    username = user2
    password = pass2
    """
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp_file:
        temp_file.write(config_content.encode("utf-8"))
        temp_path = temp_file.name

    try:
        # Mock the config file path
        with patch("dc_api_x.config.CONFIG_PATH", temp_path):
            profiles = list_available_profiles()
            assert len(profiles) == 2
            assert "default" in [p.name for p in profiles]
            assert "test" in [p.name for p in profiles]
    finally:
        # Clean up the temp file
        Path(temp_path).unlink()
