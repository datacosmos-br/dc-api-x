"""
Tests for validation utilities.
"""

import uuid

import pytest

from dc_api_x.utils.validation import (
    validate_callable,
    validate_date,
    validate_dict,
    validate_email,
    validate_enum_field,
    validate_list,
    validate_min_max,
    validate_not_empty,
    validate_one_of,
    validate_required_fields,
    validate_type,
    validate_url,
    validate_uuid,
)

# Import utilities from tests package
from tests import (
    requires_logfire,
    test_context,
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestValidateUrl:
    """Test suite for validate_url function."""

    def test_valid_url(self) -> None:
        """Test with valid URLs."""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "http://localhost:8000",
            "https://api.example.com/v1/resource",
            "https://example.com:8080/path?query=value#fragment",
        ]
        for url in valid_urls:
            is_valid, error = validate_url(url)
            assert is_valid is True
            assert error is None

    @requires_logfire
    def test_invalid_url(self, logfire_testing) -> None:
        """Test with invalid URLs."""
        invalid_urls = [
            "example.com",  # Missing protocol
            "ftp://example.com",  # Unsupported protocol
            "http://",  # Missing domain
            "http://.com",  # Invalid domain
            "https://*invalid.com",  # Invalid characters
        ]

        with test_context(test_case="invalid_urls", url_count=len(invalid_urls)):
            for url in invalid_urls:
                is_valid, error = validate_url(url)
                assert is_valid is False
                assert error == "Invalid URL format"

        # Verify that validation errors were logged
        url_validation_logs = logfire_testing.find_logs(level="WARNING", field="url")

        assert len(url_validation_logs) == len(
            invalid_urls,
        ), "Not all URL validation errors were logged"

        # Check that the values were logged correctly
        for url in invalid_urls:
            log = logfire_testing.find_log(field="url", value=url)
            assert log is not None, f"URL '{url}' was not found in the logs"


class TestValidateEmail:
    """Test suite for validate_email function."""

    def test_valid_email(self) -> None:
        """Test with valid email addresses."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com",
            "user123@example.co.uk",
        ]
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is True
            assert error is None

    @requires_logfire
    def test_invalid_email(self, logfire_testing) -> None:
        """Test with invalid email addresses."""
        invalid_emails = [
            "user",  # Missing @ and domain
            "user@",  # Missing domain
            "@example.com",  # Missing username
            "user@example",  # Incomplete domain
            "user@.com",  # Missing domain name
            "user@example.",  # Incomplete TLD
            "user@exam ple.com",  # Space in domain
        ]

        with test_context(test_case="invalid_emails", email_count=len(invalid_emails)):
            for email in invalid_emails:
                is_valid, error = validate_email(email)
                assert is_valid is False
                assert error == "Invalid email format"

        # Verify that validation errors were logged
        email_validation_logs = logfire_testing.find_logs(
            level="WARNING",
            field="email",
        )

        assert len(email_validation_logs) == len(
            invalid_emails,
        ), "Not all email validation errors were logged"

        # Check that the values were logged correctly
        for email in invalid_emails:
            log = logfire_testing.find_log(field="email", value=email)
            assert log is not None, f"Email '{email}' was not found in the logs"


class TestValidateUuid:
    """Test suite for validate_uuid function."""

    def test_valid_uuid(self) -> None:
        """Test with valid UUID strings."""
        # Generate some valid UUIDs
        valid_uuids = [
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            "123e4567-e89b-12d3-a456-426614174000",
        ]
        for uuid_str in valid_uuids:
            is_valid, error = validate_uuid(uuid_str)
            assert is_valid is True
            assert error is None

    @requires_logfire
    def test_invalid_uuid(self, logfire_testing) -> None:
        """Test with invalid UUID strings."""
        invalid_uuids = [
            "not-a-uuid",
            "123456",
            "123e4567-e89b-12d3-a456",  # Incomplete
            "123e4567-e89b-12d3-a456-42661417400Z",  # Invalid character
        ]

        with test_context(test_case="invalid_uuids", uuid_count=len(invalid_uuids)):
            for uuid_str in invalid_uuids:
                is_valid, error = validate_uuid(uuid_str)
                assert is_valid is False
                assert error == "Invalid UUID format"

        # Verify that validation errors were logged
        uuid_validation_logs = logfire_testing.find_logs(level="WARNING", field="uuid")

        assert len(uuid_validation_logs) == len(
            invalid_uuids,
        ), "Not all UUID validation errors were logged"


class TestValidateDate:
    """Test suite for validate_date function."""

    def test_valid_date_default_format(self) -> None:
        """Test with valid date in default format."""
        is_valid, error = validate_date("2023-01-15")
        assert is_valid is True
        assert error is None

    def test_valid_date_custom_format(self) -> None:
        """Test with valid date in custom format."""
        is_valid, error = validate_date("15/01/2023", format_str="%d/%m/%Y")
        assert is_valid is True
        assert error is None

    def test_invalid_date_default_format(self) -> None:
        """Test with invalid date in default format."""
        is_valid, error = validate_date("2023/01/15")
        assert is_valid is False
        assert "Invalid date format" in error

    def test_invalid_date_custom_format(self) -> None:
        """Test with invalid date in custom format."""
        is_valid, error = validate_date("15-01-2023", format_str="%d/%m/%Y")
        assert is_valid is False
        assert "Invalid date format" in error

    def test_invalid_date_value(self) -> None:
        """Test with invalid date value."""
        is_valid, error = validate_date("2023-13-45")  # No month 13, no day 45
        assert is_valid is False
        assert "Invalid date format" in error


class TestValidateRequiredFields:
    """Test suite for validate_required_fields function."""

    def test_all_fields_present(self) -> None:
        """Test with all required fields present."""
        data = {"name": "John", "email": "john@example.com", "age": 30}
        required_fields = ["name", "email", "age"]
        is_valid, error = validate_required_fields(data, required_fields)
        assert is_valid is True
        assert error is None

    @requires_logfire
    def test_missing_fields(self, logfire_testing) -> None:
        """Test with missing required fields."""
        data = {"name": "John", "age": 30}
        required_fields = ["name", "email", "age"]

        with test_context(
            test_case="missing_fields",
            data=data,
            required_fields=required_fields,
        ):
            is_valid, error = validate_required_fields(data, required_fields)
            assert is_valid is False
            assert "Missing required fields: email" in error

        # Verify that validation errors were logged
        required_field_log = logfire_testing.find_log(
            level="WARNING",
            message=lambda msg: "Required fields missing" in msg,
        )

        assert (
            required_field_log is not None
        ), "Required field validation error was not logged"

        # Verify the log contains the missing fields
        assert hasattr(
            required_field_log,
            "missing_fields",
        ), "Log entry missing the missing_fields field"
        assert (
            "email" in required_field_log.missing_fields
        ), "Log entry doesn't contain the missing field 'email'"


class TestValidateEnumField:
    """Test suite for validate_enum_field function."""

    def test_valid_enum_value(self) -> None:
        """Test with valid enum value."""
        valid_values = ["apple", "banana", "cherry"]
        is_valid, error = validate_enum_field("banana", valid_values)
        assert is_valid is True
        assert error is None

    def test_invalid_enum_value(self) -> None:
        """Test with invalid enum value."""
        valid_values = ["apple", "banana", "cherry"]
        is_valid, error = validate_enum_field("orange", valid_values)
        assert is_valid is False
        assert "Invalid value: orange" in error
        assert "apple" in error
        assert "banana" in error
        assert "cherry" in error


class TestValidateMinMax:
    """Test suite for validate_min_max function."""

    def test_value_within_range(self) -> None:
        """Test with value within range."""
        is_valid, error = validate_min_max(5, min_value=1, max_value=10)
        assert is_valid is True
        assert error is None

    def test_value_at_boundaries(self) -> None:
        """Test with value at boundaries."""
        # At minimum
        is_valid, error = validate_min_max(1, min_value=1, max_value=10)
        assert is_valid is True
        assert error is None

        # At maximum
        is_valid, error = validate_min_max(10, min_value=1, max_value=10)
        assert is_valid is True
        assert error is None

    @requires_logfire
    def test_value_below_minimum(self, logfire_testing) -> None:
        """Test with value below minimum."""
        with test_context(
            test_case="below_minimum",
            value=0,
            min_value=1,
            max_value=10,
        ):
            is_valid, error = validate_min_max(0, min_value=1, max_value=10)
            assert is_valid is False
            assert "Value 0 is less than the minimum 1" in error

        # Verify that validation errors were logged
        min_max_log = logfire_testing.find_log(
            level="WARNING",
            field="numeric_value",
            value=0,
        )

        assert min_max_log is not None, "Min/max validation error was not logged"

        # Verify the log contains error details
        assert (
            "less than" in min_max_log.error
        ), "Log entry doesn't indicate 'less than' error"

    def test_value_above_maximum(self) -> None:
        """Test with value above maximum."""
        is_valid, error = validate_min_max(11, min_value=1, max_value=10)
        assert is_valid is False
        assert "Value 11 is greater than the maximum 10" in error

    def test_only_min_value(self) -> None:
        """Test with only minimum value specified."""
        is_valid, error = validate_min_max(5, min_value=1)
        assert is_valid is True
        assert error is None

        is_valid, error = validate_min_max(0, min_value=1)
        assert is_valid is False
        assert "Value 0 is less than the minimum 1" in error

    def test_only_max_value(self) -> None:
        """Test with only maximum value specified."""
        is_valid, error = validate_min_max(5, max_value=10)
        assert is_valid is True
        assert error is None

        is_valid, error = validate_min_max(11, max_value=10)
        assert is_valid is False
        assert "Value 11 is greater than the maximum 10" in error


class TestValidateNotEmpty:
    """Test suite for validate_not_empty function."""

    def test_non_empty_string(self) -> None:
        """Test with non-empty string."""
        # Should not raise exception
        validate_not_empty("test", "field")

    def test_empty_string(self) -> None:
        """Test with empty string."""
        with pytest.raises(ValueError, match="test_field cannot be empty") as exc_info:
            validate_not_empty("", "test_field")
        assert "test_field cannot be empty" in str(exc_info.value)


class TestValidateType:
    """Test suite for validate_type function."""

    def test_correct_type(self) -> None:
        """Test with correct type."""
        result = validate_type(
            value="test",
            expected_type=str,
            field_name="field",
        )
        assert result == "test"

        result = validate_type(
            value=123,
            expected_type=int,
            field_name="field",
        )
        assert result == 123

        result = validate_type(
            value=123.45,
            expected_type=float,
            field_name="field",
        )
        assert result == 123.45

        result = validate_type(
            value=True,
            expected_type=bool,
            field_name="field",
        )
        assert result is True

    def test_incorrect_type(self) -> None:
        """Test with incorrect type."""
        with pytest.raises(TypeError) as exc_info:
            validate_type(
                value="123",
                expected_type=int,
                field_name="test_field",
            )
        assert "test_field must be of type" in str(exc_info.value)
        assert "int" in str(exc_info.value)

        with pytest.raises(TypeError) as exc_info:
            validate_type(
                value=123,
                expected_type=str,
                field_name="test_field",
            )
        assert "test_field must be of type" in str(exc_info.value)
        assert "str" in str(exc_info.value)


class TestValidateDict:
    """Test suite for validate_dict function."""

    def test_valid_dict(self) -> None:
        """Test with valid dictionary."""
        data = {"name": "John", "email": "john@example.com", "age": 30}
        required_keys = ["name", "email"]
        result = validate_dict(
            data=data,
            required_keys=required_keys,
            field_name="user_data",
        )
        assert result == data

    def test_missing_required_keys(self) -> None:
        """Test with missing required keys."""
        data = {"name": "John"}
        required_keys = ["name", "email"]
        with pytest.raises(
            ValueError,
            match="user_data is missing required keys",
        ) as exc_info:
            validate_dict(
                data=data,
                required_keys=required_keys,
                field_name="user_data",
            )
        assert "user_data is missing required keys" in str(exc_info.value)
        assert "email" in str(exc_info.value)

    def test_not_a_dict(self) -> None:
        """Test with non-dictionary value."""
        with pytest.raises(TypeError) as exc_info:
            validate_dict(
                data="not a dict",
                required_keys=["key"],
                field_name="test_field",
            )
        assert "test_field must be of type" in str(exc_info.value)
        assert "dict" in str(exc_info.value)


class TestValidateList:
    """Test suite for validate_list function."""

    def test_valid_list(self) -> None:
        """Test with valid list."""
        data = [1, 2, 3]
        result = validate_list(
            data=data,
            min_length=1,
            field_name="numbers",
        )
        assert result == data

    def test_empty_list_when_items_required(self) -> None:
        """Test with empty list when items are required."""
        with pytest.raises(
            ValueError,
            match="test_list must have at least 1 item",
        ) as exc_info:
            validate_list(
                data=[],
                min_length=1,
                field_name="test_list",
            )
        assert "test_list must have at least 1 item" in str(exc_info.value)

    def test_not_a_list(self) -> None:
        """Test with non-list value."""
        with pytest.raises(TypeError) as exc_info:
            validate_list(
                data="not a list",
                min_length=1,
                field_name="test_field",
            )
        assert "test_field must be of type" in str(exc_info.value)
        assert "list" in str(exc_info.value)


class TestValidateOneOf:
    """Test suite for validate_one_of function."""

    def test_valid_value(self) -> None:
        """Test with valid value."""
        valid_values = ["apple", "banana", "cherry"]
        result = validate_one_of(
            value="banana",
            valid_values=valid_values,
            field_name="fruit",
        )
        assert result == "banana"

    @requires_logfire
    def test_invalid_value(self, logfire_testing) -> None:
        """Test with invalid value."""
        valid_values = ["apple", "banana", "cherry"]

        with test_context(
            test_case="invalid_enum",
            value="orange",
            valid_values=valid_values,
            field="fruit",
        ):
            with pytest.raises(ValueError, match="fruit must be one of") as exc_info:
                validate_one_of(
                    value="orange",
                    valid_values=valid_values,
                    field_name="fruit",
                )
            assert "fruit must be one of" in str(exc_info.value)

        # Verify that validation errors were logged
        enum_log = logfire_testing.find_log(
            level="WARNING",
            field="fruit",
            value="orange",
        )

        assert enum_log is not None, "Enum validation error was not logged"


class TestValidateCallable:
    """Test suite for validate_callable function."""

    def test_valid_callable(self) -> None:
        """Test with valid callable."""

        def test_func() -> None:
            pass

        result = validate_callable(
            callable=test_func,
            field_name="callback",
        )
        assert result == test_func

    def test_invalid_callable(self) -> None:
        """Test with non-callable value."""
        with pytest.raises(TypeError) as exc_info:
            validate_callable(
                callable="not a function",
                field_name="callback",
            )
        assert "callback must be callable" in str(exc_info.value)
