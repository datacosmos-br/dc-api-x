#!/usr/bin/env python3
"""
Example of schema extraction and dynamic model generation with DCApiX.

This example demonstrates how to extract API schemas and generate dynamic
models from those schemas using DCApiX.
"""

import sys
from pathlib import Path
from typing import Any

from dc_api_x import ApiClient, BaseModel, SchemaDefinition, SchemaManager
from dc_api_x.utils.formatting import format_json


class SchemaNotFoundError(ValueError):
    """Exception raised when a schema cannot be found."""

    def __init__(self, schema_name: str):
        super().__init__(f"Schema not found: {schema_name}")


class ModelCreationError(ValueError):
    """Exception raised when a model cannot be created from a schema."""

    def __init__(self, schema_name: str):
        super().__init__(f"Failed to create model for schema: {schema_name}")


class SchemaExtractionExample:
    """Example of schema extraction and dynamic model generation."""

    def __init__(
        self,
        api_url: str = "https://api.example.com",
        schema_dir: str = "./schemas",
        *,
        offline_mode: bool = False,
    ):
        """
        Initialize schema extraction example.

        Args:
            api_url: API base URL
            schema_dir: Directory for schema storage
            offline_mode: Whether to operate in offline mode (using only cached schemas)
        """
        self.api_url = api_url
        self.schema_dir = Path(schema_dir)
        self.offline_mode = offline_mode

        # Create schema directory if it doesn't exist
        self.schema_dir.mkdir(parents=True, exist_ok=True)

        if not offline_mode:
            # Create API client
            self.client = ApiClient(
                url=api_url,
                username="demo",  # Placeholder
                password="demo",  # Placeholder - noqa: S106
            )

            # Disable authentication for demo
            self.client.session.auth = None

            # Create schema manager
            self.schema_manager = SchemaManager(
                client=self.client,
                cache_dir=self.schema_dir,
            )
        else:
            # Offline mode - no client, only cached schemas
            self.client = None
            self.schema_manager = SchemaManager(
                cache_dir=self.schema_dir,
                offline_mode=True,
            )

    def create_sample_schemas(self):
        """
        Create sample schemas for demonstration purposes.

        This method creates sample schemas for User, Product, and Order entities.
        In a real application, these would be extracted from the API.
        """
        print("Creating sample schemas...")

        # User schema
        user_schema = SchemaDefinition(
            name="User",
            description="User entity",
            fields={
                "id": {
                    "type": "integer",
                    "description": "User ID",
                },
                "username": {
                    "type": "string",
                    "description": "Username",
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email address",
                },
                "firstName": {
                    "type": "string",
                    "description": "First name",
                },
                "lastName": {
                    "type": "string",
                    "description": "Last name",
                },
                "createdAt": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Creation date",
                },
            },
            required_fields=["id", "username", "email"],
        )

        # Product schema
        product_schema = SchemaDefinition(
            name="Product",
            description="Product entity",
            fields={
                "id": {
                    "type": "integer",
                    "description": "Product ID",
                },
                "name": {
                    "type": "string",
                    "description": "Product name",
                },
                "description": {
                    "type": "string",
                    "description": "Product description",
                },
                "price": {
                    "type": "number",
                    "format": "float",
                    "description": "Product price",
                },
                "category": {
                    "type": "string",
                    "description": "Product category",
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": "Product tags",
                },
                "inStock": {
                    "type": "boolean",
                    "description": "Whether the product is in stock",
                },
            },
            required_fields=["id", "name", "price"],
        )

        # Order schema
        order_schema = SchemaDefinition(
            name="Order",
            description="Order entity",
            fields={
                "id": {
                    "type": "integer",
                    "description": "Order ID",
                },
                "userId": {
                    "type": "integer",
                    "description": "User ID",
                },
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "productId": {
                                "type": "integer",
                                "description": "Product ID",
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "Product quantity",
                            },
                            "price": {
                                "type": "number",
                                "description": "Product price at time of order",
                            },
                        },
                        "required": ["productId", "quantity"],
                    },
                    "description": "Ordered products",
                },
                "totalAmount": {
                    "type": "number",
                    "description": "Total order amount",
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "pending",
                        "processing",
                        "shipped",
                        "delivered",
                        "cancelled",
                    ],
                    "description": "Order status",
                },
                "createdAt": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Creation date",
                },
            },
            required_fields=["id", "userId", "products", "totalAmount", "status"],
        )

        # Save schemas to files
        user_path = user_schema.save(self.schema_dir)
        product_path = product_schema.save(self.schema_dir)
        order_path = order_schema.save(self.schema_dir)

        print(f"✅ Created schema for User: {user_path}")
        print(f"✅ Created schema for Product: {product_path}")
        print(f"✅ Created schema for Order: {order_path}")

        # Register schemas with schema manager
        self.schema_manager.schemas["User"] = user_schema
        self.schema_manager.schemas["Product"] = product_schema
        self.schema_manager.schemas["Order"] = order_schema

    def list_available_schemas(self):
        """list available schemas in the schema directory."""
        print("\n=== Available Schemas ===")

        # Find all schema files
        schema_files = list(self.schema_dir.glob("*.schema.json"))

        if not schema_files:
            print("No schemas found in the schema directory.")
            return

        for file_path in sorted(schema_files):
            name = file_path.stem
            if name.endswith(".schema"):
                name = name[:-7]
            print(f"  • {name}")

    def load_schema(self, name: str):
        """
        Load a schema by name.

        Args:
            name: Schema name

        Returns:
            SchemaDefinition: Schema definition
        """
        schema = self.schema_manager.get_schema(name)
        if not schema:
            raise SchemaNotFoundError(name)
        return schema

    def display_schema(self, name: str):
        """
        Display a schema by name.

        Args:
            name: Schema name
        """
        print(f"\n=== Schema for {name} ===")

        schema = self.load_schema(name)
        schema_json = schema.to_json_schema()

        # Format JSON with indentation
        formatted_json = format_json(schema_json, indent=2)
        print(formatted_json)

    def create_model(self, schema_name: str):
        """
        Create a model from a schema.

        Args:
            schema_name: Schema name

        Returns:
            type[BaseModel]: Model class
        """
        model = self.schema_manager.get_model(schema_name)
        if not model:
            raise ModelCreationError(schema_name)
        return model

    def demonstrate_model_usage(
        self,
        model_class: type[BaseModel],
        sample_data: dict[str, Any],
    ):
        """
        Demonstrate usage of dynamically generated model.

        Args:
            model_class: Model class
            sample_data: Sample data to create model instance
        """
        print("\n=== Model Usage Demonstration ===")
        print(f"Model class: {model_class.__name__}")
        print("Sample data:")
        print(format_json(sample_data, indent=2))

        # Create model instance from sample data
        model = model_class.model_validate(sample_data)
        print("\nModel instance created:")
        model_dict = model.to_dict()
        print(format_json(model_dict, indent=2))

        # Demonstrate field access
        print("\nAccessing model fields:")
        for field in list(model_dict.keys())[:3]:  # Show first 3 fields
            print(f"  • {field}: {getattr(model, field)}")


def main():
    """Run the example."""
    # Create schema extraction example
    example = SchemaExtractionExample(
        api_url="https://api.example.com",
        schema_dir="./example_schemas",
        offline_mode=True,  # Use offline mode for this example
    )

    # Create sample schemas
    example.create_sample_schemas()

    # list available schemas
    example.list_available_schemas()

    # Display a schema
    example.display_schema("User")

    # Create models from schemas
    user_model = example.create_model("User")
    product_model = example.create_model("Product")
    order_model = example.create_model("Order")

    # Sample data
    sample_user = {
        "id": 1,
        "username": "johndoe",
        "email": "john.doe@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "createdAt": "2023-01-15T08:30:00Z",
    }

    sample_product = {
        "id": 101,
        "name": "Smartphone X",
        "description": "Latest smartphone with advanced features",
        "price": 799.99,
        "category": "Electronics",
        "tags": ["smartphone", "electronics", "gadget"],
        "inStock": True,
    }

    sample_order = {
        "id": 1001,
        "userId": 1,
        "products": [
            {
                "productId": 101,
                "quantity": 1,
                "price": 799.99,
            },
            {
                "productId": 102,
                "quantity": 2,
                "price": 29.99,
            },
        ],
        "totalAmount": 859.97,
        "status": "processing",
        "createdAt": "2023-01-16T14:45:00Z",
    }

    # Demonstrate model usage
    example.demonstrate_model_usage(user_model, sample_user)
    example.demonstrate_model_usage(product_model, sample_product)
    example.demonstrate_model_usage(order_model, sample_order)

    print("\n✅ Schema extraction and model generation example completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
