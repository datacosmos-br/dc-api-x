"""
Tests for the models module.
"""

import json
from typing import Any

from dc_api_x.models import ApiResponse, BaseModel
from tests.constants import (
    HTTP_NOT_FOUND,
    HTTP_OK,
    ORDER_TOTAL,
    PRODUCT_PRICE,
    TEST_ORDER_ID,
    TEST_PERSON_AGE,
    TEST_PRODUCT_ID,
)


class TestBaseModel:
    """Test suite for the BaseModel class."""

    def test_model_creation(self) -> None:
        """Test model creation."""

        # Define a model class
        class User(BaseModel):
            id: int
            name: str
            email: str

        # Create model instance
        user = User(id=1, name="John Doe", email="john@example.com")

        # Verify fields
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_get_field(self) -> None:
        """Test getting fields with case-insensitive lookup."""

        # Define a model class
        class Product(BaseModel):
            id: int
            product_name: str
            price: float

        # Create model instance
        product = Product(
            id=TEST_PRODUCT_ID,
            product_name="Smartphone",
            price=PRODUCT_PRICE,
        )

        # Test exact match
        assert product.get("id") == TEST_PRODUCT_ID
        assert product.get("product_name") == "Smartphone"
        assert product.get("price") == PRODUCT_PRICE

        # Test case-insensitive match
        assert product.get("Product_Name") == "Smartphone"
        assert product.get("PRICE") == PRODUCT_PRICE

        # Test default value for missing field
        assert product.get("description") is None
        assert product.get("category", "Electronics") == "Electronics"

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""

        # Define a model class
        class Order(BaseModel):
            id: int
            customer_id: int
            total: float
            items: list

        # Create model instance
        order = Order(
            id=TEST_ORDER_ID,
            customer_id=1,
            total=ORDER_TOTAL,
            items=[{"product_id": TEST_PRODUCT_ID, "quantity": 1}],
        )

        # Convert to dictionary
        order_dict = {}
        order_dict[str, Any] = order.to_dict()

        # Verify dictionary
        assert order_dict["id"] == TEST_ORDER_ID
        assert order_dict["customer_id"] == 1
        assert order_dict["total"] == ORDER_TOTAL
        assert order_dict["items"] == [{"product_id": TEST_PRODUCT_ID, "quantity": 1}]

    def test_to_json(self) -> None:
        """Test conversion to JSON."""

        # Define a model class
        class Address(BaseModel):
            street: str
            city: str
            zip_code: str

        # Create model instance
        address = Address(street="123 Main St", city="New York", zip_code="10001")

        # Convert to JSON
        json_str = address.to_json()

        # Parse JSON
        data = json.loads(json_str)

        # Verify JSON
        assert data["street"] == "123 Main St"
        assert data["city"] == "New York"
        assert data["zip_code"] == "10001"

    def test_model_validate(self) -> None:
        """Test creation from dictionary."""

        # Define a model class
        class Person(BaseModel):
            id: int
            name: str
            age: int

        # Create from dictionary
        data = {"id": 1, "name": "Jane Smith", "age": TEST_PERSON_AGE}
        person = Person.model_validate(data)

        # Verify fields
        assert person.id == 1
        assert person.name == "Jane Smith"
        assert person.age == TEST_PERSON_AGE


class TestApiResponse:
    """Test suite for the ApiResponse class."""

    def test_success_response(self) -> None:
        """Test creating a successful response."""
        # Create success response
        response = ApiResponse(
            success=True,
            data={"id": 1, "name": "John"},
            status_code=HTTP_OK,
        )

        # Verify response
        assert response.success is True
        assert response.status_code == HTTP_OK
        assert response.data == {"id": 1, "name": "John"}
        assert response.error is None

    def test_error_response(self) -> None:
        """Test creating an error response."""
        # Create error response
        response = ApiResponse(
            success=False,
            error="Not found",
            status_code=HTTP_NOT_FOUND,
            data=None,
        )

        # Verify response
        assert response.success is False
        assert response.status_code == HTTP_NOT_FOUND
        assert response.data is None
        assert response.error.detail == "Not found"

    def test_bool_representation(self) -> None:
        """Test boolean representation of response."""
        # Create success response
        success_response = ApiResponse(success=True, data={}, status_code=HTTP_OK)

        # Create error response
        error_response = ApiResponse(
            success=False,
            error="Error",
            status_code=HTTP_NOT_FOUND,
        )

        # Verify boolean representations
        assert bool(success_response) is True
        assert bool(error_response) is False
