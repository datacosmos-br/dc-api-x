"""
Security tests for authentication, authorization, and data protection.

This module demonstrates how to test security-related aspects of the application.
"""

import hashlib
import os
import time
from typing import Any, Optional

import jwt
import pytest

from tests.factories import UserFactory, create_mock_client_with_responses


def hash_password(password: str, salt: Optional[str] = None) -> tuple[Any, ...]:
    """Hash a password using PBKDF2 with SHA-256."""
    import binascii

    if salt is None:
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    else:
        salt = salt.encode("ascii")

    pwdhash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000,
        dklen=128,
    )
    pwdhash = binascii.hexlify(pwdhash)
    (salt + pwdhash).decode("ascii"), salt.decode("ascii")


def verify_password(stored_password: str, provided_password: str, salt: str) -> bool:
    """Verify a password against its hash."""
    # Hash the provided password with the same salt
    new_hash, _ = hash_password(provided_password, salt)
    return new_hash == stored_password


@pytest.mark.security
class TestAuthentication:
    """Test authentication mechanisms and security patterns."""

    def test_password_hashing(self) -> None:
        """Test password hashing and verification."""
        # Arrange
        password = "SecureP@ssw0rd123"

        # Act
        hashed, salt = hash_password(password)

        # Assert
        assert hashed != password  # Password should not be stored in plaintext
        assert len(hashed) > 32  # Hash should be sufficiently long

        # Verify the password can be verified
        assert verify_password(hashed, password, salt) is True

        # Verify incorrect password fails verification
        assert verify_password(hashed, "WrongPassword", salt) is False
        assert verify_password(hashed, password + "1", salt) is False

    def test_jwt_token_security(self) -> None:
        """Test JWT token security."""
        # Arrange
        secret_key = "test-secret-key"
        payload = {
            "sub": "test-user",
            "name": "Test User",
            "role": "admin",
            "exp": int(time.time()) + 3600,  # Expires in 1 hour
        }

        # Act
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        # Assert
        # Verify the token can be decoded with the correct key
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        assert decoded["sub"] == payload["sub"]
        assert decoded["role"] == "admin"

        # Verify the token cannot be decoded with an incorrect key
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong-key", algorithms=["HS256"])

        # Test token expiration
        expired_payload = {
            "sub": "test-user",
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, secret_key, algorithm="HS256")

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, secret_key, algorithms=["HS256"])


@pytest.mark.security
class TestAuthorization:
    """Test authorization controls and access permissions."""

    def test_role_based_access_control(self) -> None:
        """Test role-based access control for different user roles."""
        # Arrange
        # Create users with different roles
        admin = UserFactory.create({"role": "admin"})
        editor = UserFactory.create({"role": "editor"})
        viewer = UserFactory.create({"role": "viewer"})

        # Define permissions to test
        permissions = [
            ("manage_users", [admin]),  # Only admin can manage users
            ("edit_content", [admin, editor]),  # Admin and editor can edit
            ("view_content", [admin, editor, viewer]),  # All can view
        ]

        # Assert - test each permission for each user
        for permission, allowed_users in permissions:
            # Users who should have permission
            for user in allowed_users:
                assert user.has_permission(
                    permission,
                ), f"{user.role} should have {permission} permission"

            # Users who should not have permission
            all_users = [admin, editor, viewer]
            for user in [u for u in all_users if u not in allowed_users]:
                assert not user.has_permission(
                    permission,
                ), f"{user.role} should not have {permission} permission"

    def test_api_authorization(self) -> None:
        """Test API authorization controls."""
        # Arrange - create clients with different auth tokens
        admin_client = create_mock_client_with_responses(
            {
                ("GET", "users"): {"data": [{"id": 1, "name": "User 1"}]},
                ("POST", "users"): {"success": True, "id": 2},
                ("DELETE", "users/1"): {"success": True},
            },
        )
        # Override the auth provider's token
        admin_client.auth_provider.token = "admin-token"

        regular_client = create_mock_client_with_responses(
            {
                ("GET", "users"): {"data": [{"id": 1, "name": "User 1"}]},
                ("POST", "users"): {"error": "Unauthorized", "code": 403},
                ("DELETE", "users/1"): {"error": "Unauthorized", "code": 403},
            },
        )
        # Override the auth provider's token
        regular_client.auth_provider.token = "user-token"

        # Act & Assert
        # Both should be able to read
        admin_response = admin_client.get("users")
        user_response = regular_client.get("users")
        assert "data" in admin_response
        assert "data" in user_response

        # Only admin should be able to create
        admin_create = admin_client.post("users", json={"name": "New User"})
        assert "success" in admin_create
        assert admin_create["success"] is True

        # Regular user should get unauthorized error
        user_create = regular_client.post("users", json={"name": "New User"})
        assert "error" in user_create
        assert user_create["code"] == 403

        # Only admin should be able to delete
        admin_delete = admin_client.delete("users/1")
        assert "success" in admin_delete
        assert admin_delete["success"] is True

        # Regular user should get unauthorized error
        user_delete = regular_client.delete("users/1")
        assert "error" in user_delete
        assert user_delete["code"] == 403


@pytest.mark.security
class TestDataProtection:
    """Test data protection and privacy controls."""

    def test_sensitive_data_masking(self) -> None:
        """Test masking of sensitive data."""
        # Arrange
        user_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "credit_card": "4111-1111-1111-1111",
            "ssn": "123-45-6789",
            "password": "securepassword123",
        }

        # Define masking function
        def mask_sensitive_data(data: dict[str, Any]) -> dict[str, Any]:
            """Mask sensitive fields in user data."""
            masked = data.copy()

            # Mask credit card number except last 4 digits
            if "credit_card" in masked:
                parts = masked["credit_card"].split("-")
                if len(parts) == 4:
                    masked["credit_card"] = f"XXXX-XXXX-XXXX-{parts[3]}"
                else:
                    masked["credit_card"] = "XXXX-XXXX-XXXX-XXXX"

            # Mask SSN except last 4 digits
            if "ssn" in masked:
                parts = masked["ssn"].split("-")
                if len(parts) == 3:
                    masked["ssn"] = f"XXX-XX-{parts[2]}"
                else:
                    masked["ssn"] = "XXX-XX-XXXX"

            # Never include passwords
            if "password" in masked:
                del masked["password"]

            return masked

        # Act
        masked_data = mask_sensitive_data(user_data)

        # Assert
        assert masked_data["id"] == user_data["id"]
        assert masked_data["name"] == user_data["name"]
        assert masked_data["email"] == user_data["email"]
        assert masked_data["credit_card"] == "XXXX-XXXX-XXXX-1111"
        assert masked_data["ssn"] == "XXX-XX-6789"
        assert "password" not in masked_data  # Password should be removed entirely

    def test_secure_api_responses(self) -> None:
        """Test that API responses don't leak sensitive data."""
        # Arrange - create client with responses that might contain sensitive data
        client = create_mock_client_with_responses(
            {
                ("GET", "user/profile"): {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "credit_card": {"last4": "1111", "expiry": "12/25"},
                    # Potentially sensitive fields that shouldn't be exposed
                    "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
                    "internal_notes": "Customer called about billing issue",
                    "system_flags": ["VIP", "CREDIT_HOLD"],
                },
            },
        )

        # Define a function to validate response security
        def validate_response_security(data: dict[str, Any]) -> bool:
            """Check for sensitive data in responses."""
            forbidden_fields = [
                "password",
                "password_hash",
                "salt",
                "secret",
                "internal_notes",
                "system_flags",
            ]

            for field in forbidden_fields:
                if field in data:
                    return False

            # Check nested objects too
            for _key, value in data.items():
                if isinstance(value, dict[str, Any]) and not validate_response_security(
                    value,
                ):
                    return False

            return True

        # Act
        response = client.get("user/profile")

        # Assert
        assert not validate_response_security(
            response,
        ), "Response contains sensitive data"

        # Sanitize the response
        def sanitize_response(data: dict[str, Any]) -> dict[str, Any]:
            """Remove sensitive fields from response."""
            sanitized = data.copy()
            forbidden_fields = [
                "password",
                "password_hash",
                "salt",
                "secret",
                "internal_notes",
                "system_flags",
            ]

            for field in forbidden_fields:
                if field in sanitized:
                    del sanitized[field]

            # Check nested objects too
            for key, value in list(sanitized.items()):
                if isinstance(value, dict[str, Any]):
                    sanitized[key] = sanitize_response(value)

            return sanitized

        # Sanitize the response
        safe_response = sanitize_response(response)

        # Verify sanitized response
        assert validate_response_security(
            safe_response,
        ), "Sanitized response should not contain sensitive data"
        assert "name" in safe_response  # Regular fields should remain
        assert "email" in safe_response
        assert "credit_card" in safe_response
        assert (
            "password_hash" not in safe_response
        )  # Sensitive fields should be removed
        assert "internal_notes" not in safe_response
        assert "system_flags" not in safe_response
