"""
Tests for the Config module.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from dc_api_x.config import (
    Config,
    ConfigProfile,
    list_available_profiles,
    load_config_from_env,
)
from tests.constants import CUSTOM_TIMEOUT, DEFAULT_TIMEOUT, MAX_RETRIES


class TestConfig:
    """Test suite for the Config class."""

    def test_init_with_parameters(self):
        """Test initialization with parameters."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password=SecretStr("testpass"),
            timeout=30,
            verify_ssl=True,
            max_retries=5,
            retry_backoff=1.0,
            debug=True,
            environment="test",
        )

        assert config.url == "https://api.example.com"
        assert config.username == "testuser"
        assert config.password.get_secret_value() == "testpass"
        assert config.timeout == 30
        assert config.verify_ssl is True
        assert config.max_retries == 5
        assert config.retry_backoff == 1.0
        assert config.debug is True
        assert config.environment == "test"

    def test_url_validation(self):
        """Test URL validation."""
        # Test with valid URL
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password=SecretStr("testpass"),
        )
        assert config.url == "https://api.example.com"

        # Test with URL having trailing slash
        config = Config(
            url="https://api.example.com/",
            username="testuser",
            password=SecretStr("testpass"),
        )
        assert config.url == "https://api.example.com"

        # Test with invalid URL (no protocol)
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            Config(
                url="api.example.com",
                username="testuser",
                password=SecretStr("testpass"),
            )

        # Test with empty URL
        with pytest.raises(ValueError, match="URL cannot be empty"):
            Config(
                url="",
                username="testuser",
                password=SecretStr("testpass"),
            )

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password=SecretStr("testpass"),
            timeout=30,
        )

        config_dict = config.to_dict()

        assert config_dict["url"] == "https://api.example.com"
        assert config_dict["username"] == "testuser"
        assert config_dict["password"] == "testpass"
        assert config_dict["timeout"] == 30

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password=SecretStr("testpass"),
            timeout=30,
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Save configuration
            config.save(temp_path)

            # Load configuration
            loaded_config = Config.from_file(temp_path)

            # Verify loaded configuration
            assert loaded_config.url == "https://api.example.com"
            assert loaded_config.username == "testuser"
            assert loaded_config.password.get_secret_value() == "testpass"
            assert loaded_config.timeout == DEFAULT_TIMEOUT
        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_save_unsupported_format(self):
        """Test saving to unsupported format."""
        config = Config(
            url="https://api.example.com",
            username="testuser",
            password=SecretStr("testpass"),
        )

        with pytest.raises(ValueError, match="Unsupported file format"):
            config.save("config.txt")

    def test_load_missing_file(self):
        """Test loading from missing file."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            Config.from_file("nonexistent.json")

    def test_load_unsupported_format(self):
        """Test loading from unsupported format."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            Config.from_file("config.txt")

    @patch("dc_api_x.config.load_dotenv")
    @patch("dc_api_x.config.os.path.exists")
    @patch("dc_api_x.config.os.environ")
    def test_from_profile(self, mock_environ, mock_exists, mock_load_dotenv):
        """Test loading from profile."""
        # Mock environment setup
        mock_exists.return_value = True
        mock_environ.get.side_effect = lambda k, default=None: {
            "API_TEST_URL": "https://api.test.com",
            "API_TEST_USERNAME": "testprofile",
            "API_TEST_PASSWORD": "testpass123",
        }.get(k, default)

        # Mock environment variable lookup
        def mock_getitem(key):
            return {
                "API_TEST_URL": "https://api.test.com",
                "API_TEST_USERNAME": "testprofile",
                "API_TEST_PASSWORD": "testpass123",
            }[key]

        mock_environ.__getitem__.side_effect = mock_getitem
        mock_environ.__contains__.side_effect = lambda k: k in [
            "API_TEST_URL",
            "API_TEST_USERNAME",
            "API_TEST_PASSWORD",
        ]

        # Load from profile
        config = Config.from_profile("test")

        # Verify profile was loaded
        assert config.url == "https://api.test.com"
        assert config.username == "testprofile"
        assert config.password.get_secret_value() == "testpass123"

        # Verify dotenv was loaded
        mock_load_dotenv.assert_called_once_with(".env.test")

    @patch("dc_api_x.config.os.path.exists")
    def test_from_profile_missing_file(self, mock_exists):
        """Test loading from missing profile."""
        mock_exists.return_value = False

        with pytest.raises(ValueError, match="Profile environment file not found"):
            Config.from_profile("nonexistent")

    @patch("dc_api_x.config.os.path.exists")
    @patch("dc_api_x.config.os.environ")
    @patch("dc_api_x.config.load_dotenv")
    def test_from_profile_invalid(self, mock_load_dotenv, mock_environ, mock_exists):
        """Test loading from invalid profile."""
        # Mock environment setup
        mock_exists.return_value = True
        mock_environ.get.return_value = None
        mock_environ.__contains__.return_value = False

        with pytest.raises(ValueError, match="Invalid profile configuration"):
            Config.from_profile("invalid")


class TestConfigProfile:
    """Test suite for the ConfigProfile class."""

    def test_init(self):
        """Test initialization."""
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.test.com",
                "username": "testuser",
                "password": "testpass",
            },
        )

        assert profile.name == "test"
        assert profile.config["url"] == "https://api.test.com"
        assert profile.config["username"] == "testuser"
        assert profile.config["password"] == "testpass"

    def test_is_valid(self):
        """Test validation."""
        # Valid profile
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.test.com",
                "username": "testuser",
                "password": "testpass",
            },
        )
        assert profile.is_valid is True

        # Invalid profile (missing password)
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.test.com",
                "username": "testuser",
            },
        )
        assert profile.is_valid is False

        # Invalid profile (missing url)
        profile = ConfigProfile(
            name="test",
            config={
                "username": "testuser",
                "password": "testpass",
            },
        )
        assert profile.is_valid is False

    def test_repr(self):
        """Test string representation."""
        profile = ConfigProfile(
            name="test",
            config={
                "url": "https://api.test.com",
                "username": "testuser",
                "password": "testpass",
            },
        )

        repr_str = repr(profile)

        # Verify password is hidden
        assert "testpass" not in repr_str
        assert "****" in repr_str

        # Verify other fields are included
        assert "test" in repr_str
        assert "https://api.test.com" in repr_str
        assert "testuser" in repr_str


@patch("dc_api_x.config.os.environ")
def test_load_config_from_env(mock_environ):
    """Test loading configuration from environment variables."""
    # Mock environment variables
    mock_environ.get.side_effect = lambda k, default=None: {
        "API_URL": "https://api.env.com",
        "API_USERNAME": "envuser",
        "API_PASSWORD": "envpass",
        "API_TIMEOUT": "45",
        "API_VERIFY_SSL": "False",
        "API_MAX_RETRIES": "2",
        "API_DEBUG": "True",
    }.get(k, default)

    # Load from environment
    config = load_config_from_env()

    # Verify configuration
    assert config.url == "https://api.env.com"
    assert config.username == "envuser"
    assert config.password.get_secret_value() == "envpass"
    assert config.timeout == CUSTOM_TIMEOUT
    assert config.verify_ssl is False
    assert config.max_retries == MAX_RETRIES
    assert config.debug is True


@patch("dc_api_x.config.Path")
def test_list_available_profiles(mock_path):
    """Test listing available profiles."""
    # Mock glob result
    mock_glob = mock_path.return_value.glob
    mock_glob.return_value = [
        Path(".env.dev"),
        Path(".env.test"),
        Path(".env.prod"),
        Path(".env"),  # This should be excluded
    ]

    # list profiles
    profiles = list_available_profiles()

    # Verify profiles
    assert set(profiles) == {"dev", "test", "prod"}
    assert "env" not in profiles  # .env should be excluded
