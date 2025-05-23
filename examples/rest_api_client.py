#!/usr/bin/env python3
"""
Example of using DCApiX to create a custom REST API client.

This example demonstrates how to create a custom API client for a RESTful API
using DCApiX classes and utilities.
"""

import os
import sys
from typing import Any

# Add src directory to path to import dc_api_x
# If the package is installed, you can remove these lines
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


from dc_api_x import ApiClient, ApiResponse, BaseModel, Entity, EntityManager, paginate


class Product(BaseModel):
    """Product model."""

    id: int
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: dict[str, Any] | None = None


class User(BaseModel):
    """User model."""

    id: int
    email: str
    username: str
    password: str
    name: dict[str, str] | None = None
    phone: str | None = None


class StoreApiClient(ApiClient):
    """
    Custom Store API client.

    This extends the DCApiX ApiClient with store-specific functionality.
    """

    def __init__(
        self,
        url: str = "https://fakestoreapi.com",
        **kwargs,
    ):
        """
        Initialize Store API client.

        Args:
            url: Store API URL (default: https://fakestoreapi.com)
            **kwargs: Additional arguments for ApiClient
        """
        # For this demo API, we don't need authentication
        super().__init__(
            url=url,
            username="demo",  # Placeholder
            password="demo",  # Placeholder
            **kwargs,
        )

        # Disable authentication for this API
        self.session.auth = None

        # Initialize entity manager
        self.entities = StoreEntityManager(self)

    def get_product_categories(self) -> ApiResponse:
        """Get all product categories."""
        return self.get("products/categories")

    def search_products(
        self,
        category: str | None = None,
        limit: int | None = None,
    ) -> ApiResponse:
        """
        Search products by category.

        Args:
            category: Product category (optional)
            limit: Maximum number of results (optional)

        Returns:
            ApiResponse: Search results
        """
        params = {}

        if limit is not None:
            params["limit"] = limit

        if category:
            return self.get(f"products/category/{category}", params=params)
        return self.get("products", params=params)


class StoreEntityManager(EntityManager):
    """Entity manager for Store API."""

    def __init__(self, client: StoreApiClient):
        """Initialize Store entity manager."""
        super().__init__(client)

        # Register built-in entity types
        self._register_entities()

    def _register_entities(self):
        """Register built-in entity types."""
        self.entities["products"] = self.get_entity("products", Product)
        self.entities["users"] = self.get_entity("users", User)

    def get_product_entity(self) -> Entity:
        """Get products entity."""
        return self.get_entity("products", Product)

    def get_user_entity(self) -> Entity:
        """Get users entity."""
        return self.get_entity("users", User)


class CartEntity(Entity):
    """Shopping cart entity with specialized methods."""

    def add_product(
        self,
        user_id: int,
        product_id: int,
        quantity: int = 1,
    ) -> ApiResponse:
        """
        Add product to user's cart.

        Args:
            user_id: User ID
            product_id: Product ID
            quantity: Product quantity

        Returns:
            ApiResponse: Updated cart
        """
        data = {
            "userId": user_id,
            "products": [
                {
                    "productId": product_id,
                    "quantity": quantity,
                },
            ],
        }
        return self.client.post("carts", json_data=data)

    def get_user_cart(self, user_id: int) -> ApiResponse:
        """
        Get user's cart.

        Args:
            user_id: User ID

        Returns:
            ApiResponse: User's cart
        """
        return self.client.get(f"carts/user/{user_id}")


def print_section(title: str):
    """Print a section title."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def main():
    """Run the example."""
    # Create Store API client
    client = StoreApiClient()
    print("✅ Store API client initialized")

    # Get product categories
    print_section("Product Categories")
    categories_response = client.get_product_categories()
    if categories_response.success:
        categories = categories_response.data
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")

    # Search for products in a category
    selected_category = "electronics"
    print_section(f"Products in '{selected_category}' Category")
    products_response = client.search_products(category=selected_category)
    if products_response.success:
        products = products_response.data
        for product in products:
            # Convert to Product model
            p = Product.model_validate(product)
            print(f"  • {p.title} - ${p.price}")
            print(f"    {p.description[:100]}...")

    # Using entity API
    print_section("Using Entity API")
    products = client.entities.get_product_entity()

    # Get a specific product
    product_id = 1
    product_response = products.get(product_id)
    if product_response.success:
        product = Product.model_validate(product_response.data)
        print(f"Product: {product.title}")
        print(f"Price: ${product.price}")
        print(f"Category: {product.category}")
        print(f"Description: {product.description[:100]}...")

    # Using pagination
    print_section("Using Pagination")
    all_products = paginate(
        client=client,
        endpoint="products",
        page_param="page",
        page_size_param="limit",
        page_size=5,
        data_key=None,  # This API returns the array directly
        model_class=Product,
    )

    # Define constant for the product limit
    max_products = 10

    print(f"Fetching products with pagination (5 items per page):")
    for i, product in enumerate(all_products):
        if i >= max_products:  # Limit to max_products products for this example
            break
        print(f"  • {product.title} - ${product.price}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
