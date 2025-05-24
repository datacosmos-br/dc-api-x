#!/usr/bin/env python3
"""
Example of using DCApiX to create a custom REST API client.

This example demonstrates how to create a custom API client for a RESTful API
using DCApiX classes and utilities.
"""

import sys
from typing import Any

import dc_api_x as apix

# Enable plugins to access all registered adapters and providers
apix.enable_plugins()


class Product(apix.BaseModel):
    """Product model."""

    id: int
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: dict[str, Any] | None = None


class User(apix.BaseModel):
    """User model."""

    id: int
    email: str
    username: str
    password: str
    name: dict[str, str] | None = None
    phone: str | None = None


class StoreApiClient(apix.ApiClient):
    """
    Custom Store API client.

    This extends the DCApiX ApiClient with store-specific functionality.
    """

    def __init__(
        self,
        url: str = "https://fakestoreapi.com",
        **kwargs,
    ) -> None:
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
            password="demo",  # Placeholder  # noqa: S106
            **kwargs,
        )

        # Disable authentication for this API
        if self is not None:
            self.session.auth = None
        else:
            # Handle None case appropriately
            pass  # TODO: Implement proper None handling

        # Initialize entity manager
        self.entities = StoreEntityManager(self)

    def get_product_categories(self) -> apix.ApiResponse:
        """Get all product categories."""
        self.get("products/categories")

    def search_products(
        self,
        category: str | None = None,
        limit: int | None = None,
    ) -> apix.ApiResponse:
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


class StoreEntityManager(apix.EntityManager):
    """Entity manager for Store API."""

    def __init__(self, client: StoreApiClient) -> None:
        """Initialize Store entity manager."""
        super().__init__(client)

        # Register built-in entity types
        self._register_entities()

    def _register_entities(self) -> None:
        """Register built-in entity types."""
        self.entities["products"] = self.get_entity("products", Product)
        self.entities["users"] = self.get_entity("users", User)

    def get_product_entity(self) -> apix.Entity:
        """Get products entity."""
        return self.get_entity("products", Product)

    def get_user_entity(self) -> apix.Entity:
        """Get users entity."""
        return self.get_entity("users", User)


class CartEntity(apix.Entity):
    """Shopping cart entity with specialized methods."""

    def add_product(
        self,
        user_id: int,
        product_id: int,
        quantity: int = 1,
    ) -> apix.ApiResponse:
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

    def get_user_cart(self, user_id: int) -> apix.ApiResponse:
        """
        Get user's cart.

        Args:
            user_id: User ID

        Returns:
            ApiResponse: User's cart
        """
        return self.client.get(f"carts/user/{user_id}")


def print_section(title: str) -> None:
    """Print a section title."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def main() -> None:
    """Run the example."""
    # Print available plugins
    print_section("Available Plugin Components")
    print("Adapters:", apix.list_adapters())
    print("Auth Providers:", apix.list_auth_providers())
    print("Schema Providers:", apix.list_schema_providers())

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
    all_products = apix.paginate(
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

    print("Fetching products with pagination (5 items per page):")
    for i, product in enumerate(all_products):
        if i >= max_products:  # Limit to max_products products for this example
            break
        print(f"  • {product.title} - ${product.price}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
assert isinstance(result, None), f"Expected None, got {type(result)}"
return result
