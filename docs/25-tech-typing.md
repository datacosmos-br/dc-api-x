# Type Systems

> *"Type hints are executable documentation that can't become out of date."*
> This guide explains how DCApiX leverages Python's type system and Pydantic
> to provide robust data validation, serialization, and documentation.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [24 - Tech: Structured Logging](24-tech-structured-logging.md) | **25 - Tech: Typing** | [26 - Tech: CLI](26-tech-cli.md) |

---

## 1. Introduction

DCApiX leverages Python's type system and [Pydantic](https://docs.pydantic.dev/) for robust data validation, serialization, and configuration management. This guide provides a comprehensive overview of typing practices within DCApiX, serving as a central reference for developers.

---

## 2. Modern Python Typing

### 2.1 Core Typing Features

DCApiX uses Python 3.10+ typing features:

```python
# ❌ AVOID: Importing from typing for built-in containers
from typing import Dict, List, Optional, Set, Tuple, Union

def old_style(users: List[Dict[str, str]], active: Optional[bool] = None) -> Tuple[int, Set[str]]:
    pass

# ✅ PREFER: Built-in types as generic containers (PEP 585, Python 3.10+)
def modern_style(users: list[dict[str, str]], active: bool | None = None) -> tuple[int, set[str]]:
    pass
```

### 2.2 Best Practices

* **Use built-in types** directly for generic annotations (Python 3.10+)
* **Prefer `|` union operator** over `Union` (PEP 604)
* **Use `X | None` instead of `Optional[X]`** for nullable types
* **Reserve `typing` imports** for special types without built-in equivalents
* **Use type aliases** to improve readability: `UserDict = dict[str, str]`
* **Include return type annotations** for all functions and methods
* **Use precise collection types** rather than generic sequences
* **Centralize common type definitions** in a dedicated module

### 2.3 Type Definitions Module

DCApiX provides a centralized `type_definitions.py` module for commonly used types:

```python
# Common JSON-related types
JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]

# File and path related types
PathLike = str | Path

# HTTP related types
Headers = dict[str, str]
HttpMethod = str  # GET, POST, PUT, PATCH, DELETE
StatusCode = int

# Entity related types
EntityId = str | int  # Common ID types
FilterDict = dict[str, Any]  # Dictionary for filter parameters
```

Use these type definitions instead of recreating them in each module.

### 2.4 Circular Imports with TYPE_CHECKING

When you need to import types that would create circular imports, use the `TYPE_CHECKING` constant:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import ApiClient
    from .models import ApiResponse

def process_response(response: "ApiResponse") -> dict[str, Any]:
    """Process an API response."""
    return response.data or {}

class Entity:
    def __init__(self, client: "ApiClient") -> None:
        self.client = client
```

With Python 3.10+, string literals for annotations are automatically supported without `from __future__ import annotations`, but we include it for clarity and backward compatibility.

---

## 3. Pydantic Models

### 3.1 Basic Model Usage

DCApiX uses Pydantic models for data validation and serialization:

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    active: bool = True

    class Config:
        frozen = True  # Immutable model
```

### 3.2 Field Customization

```python
class Product(BaseModel):
    id: int
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
```

### 3.3 Model Validation

```python
# Validate data against a model
user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
user = User.model_validate(user_data)

# Access validated fields
print(f"User ID: {user.id}")
print(f"User Name: {user.name}")

# Serialize to dictionary or JSON
user_dict = user.model_dump()
user_json = user.model_dump_json()
```

### 3.4 Custom Validators

```python
from pydantic import BaseModel, field_validator

class SignupRequest(BaseModel):
    username: str
    password: str
    password_confirm: str

    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("Username must contain only letters and numbers")
        return v

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("Passwords do not match")
        return v
```

---

## 4. Settings Management

### 4.1 Configuration with Pydantic Settings

DCApiX uses Pydantic Settings for configuration management:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        extra="ignore"
    )

    url: str
    username: str
    password: str
    timeout: int = 30
    verify_ssl: bool = True
```

### 4.2 Configuration Sources

Settings can be loaded from multiple sources:

* **Environment variables**: `API_URL=https://api.example.com`
* **Environment files**: `.env` or `.env.dev`
* **Direct initialization**: `Settings(url="https://api.example.com")`
* **Configuration profiles**: Using multiple `.env.{profile}` files

### 4.3 Using Settings

```python
from dc_api_x.config import Settings

# Load settings from environment variables
settings = Settings()

# Use settings
client = ApiClient(
    url=settings.url,
    username=settings.username,
    password=settings.password,
    timeout=settings.timeout
)
```

---

## 5. Advanced Type Features

### 5.1 Generic Models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None

class User(BaseModel):
    id: int
    name: str

# Type-safe response
user_response = Response[User](
    success=True,
    data=User(id=1, name="John Doe")
)
```

### 5.2 Discriminated Unions

```python
from pydantic import BaseModel, Field
from typing import Literal

class Dog(BaseModel):
    pet_type: Literal["dog"]
    bark: str
    breed: str

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meow: str
    hunting_skill: int

class Pet(BaseModel):
    __root__: Dog | Cat = Field(..., discriminator="pet_type")

# Type-safe validation
pet = Pet.model_validate({
    "pet_type": "dog",
    "bark": "woof",
    "breed": "Labrador"
})
```

### 5.3 JSON Schema Generation

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: int
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price", gt=0)

# Generate JSON Schema
schema = Product.model_json_schema()
```

### 5.4 Protocol Classes for Structural Typing

DCApiX uses Protocol classes to define interfaces based on structure rather than inheritance:

```python
from typing import Protocol

class ConnectionProtocol(Protocol):
    """Protocol for objects that support connection management."""

    def connect(self) -> bool:
        """Connect to the service."""
        ...

    def disconnect(self) -> bool:
        """Disconnect from the service."""
        ...

    def is_connected(self) -> bool:
        """Check if the connection is active."""
        ...

# Any class with these methods will satisfy this protocol
class MyConnection:
    def connect(self) -> bool:
        print("Connecting")
        return True

    def disconnect(self) -> bool:
        print("Disconnecting")
        return True

    def is_connected(self) -> bool:
        return True

def use_connection(conn: ConnectionProtocol) -> None:
    if not conn.is_connected():
        conn.connect()
    # Do something with the connection
    conn.disconnect()

# This works even though MyConnection doesn't explicitly inherit from ConnectionProtocol
use_connection(MyConnection())
```

Protocol classes enable:

1. **Duck typing with static verification** - "If it walks like a duck and quacks like a duck, it's a duck"
2. **Retroactive conformance** - Existing classes can implement protocols without modification
3. **Composition over inheritance** - Define interfaces without forcing inheritance hierarchies
4. **Testing with mocks** - Easily create mock objects that satisfy protocols

### 5.5 TypeVar and Generic Types in Depth

DCApiX makes extensive use of generic types with TypeVar for increased type safety:

```python
from typing import Generic, TypeVar

# Define a type variable with an upper bound
T = TypeVar('T')  # Unbounded type variable
K = TypeVar('K', bound='BaseModel')  # Bounded type variable

# Generic cache class that can store any type
class Cache(Generic[T]):
    def __init__(self) -> None:
        self.items: dict[str, T] = {}

    def get(self, key: str) -> T | None:
        return self.items.get(key)

    def set(self, key: str, value: T) -> None:
        self.items[key] = value

# Using the generic cache with different types
string_cache = Cache[str]()  # Cache for strings
string_cache.set("name", "John")  # OK
string_cache.set("age", 30)  # Type error: int is not str

# Entity manager with bounded type variable
class EntityManager(Generic[K]):
    def __init__(self, model_class: type[K]) -> None:
        self.model_class = model_class
        self.entities: list[K] = []

    def add(self, entity: K) -> None:
        self.entities.append(entity)

    def create(self, data: dict[str, Any]) -> K:
        return self.model_class(**data)
```

When working with generics:

1. **Type variables** define placeholders for types
2. **Bounds** restrict what types can be used
3. **Generic inheritance** allows specializing base classes
4. **Specialized subclasses** can fix type variables to specific types:

```python
class StringCache(Cache[str]):
    def uppercase_all(self) -> None:
        """Convert all cached strings to uppercase."""
        for key, value in self.items.items():
            self.items[key] = value.upper()
```

---

## 6. Type Discovery with MonkeyType

### 6.1 Introduction to MonkeyType

[MonkeyType](https://github.com/Instagram/MonkeyType) is a runtime type collection tool that automatically generates type annotations by observing the types of arguments and return values during program execution.

### 6.2 Type Collection Workflow

1. **Collection**: Run tests with MonkeyType to collect runtime type information
2. **Discovery**: List modules that have collected type information
3. **Application**: Apply collected types to specific modules
4. **Refinement**: Manually review and refine the types if necessary
5. **Verification**: Verify type consistency with mypy

### 6.3 Basic Usage

DCApiX includes several Makefile targets that simplify MonkeyType usage:

```bash
# Run all tests with MonkeyType to collect type information
make monkeytype-run

# List modules with collected type information
make monkeytype-list

# Apply types to a specific module
make monkeytype-apply MODULE=dc_api_x.config

# Verify types with mypy
make monkeytype-mypy MODULE=dc_api_x.config
```

### 6.4 Converting MonkeyType Annotations to Pydantic

MonkeyType generates standard Python type annotations that need to be converted to Pydantic field definitions:

```python
# Original class without types
class Config:
    def __init__(self, api_url, timeout=None):
        self.api_url = api_url
        self.timeout = timeout or 30

# After applying MonkeyType
class Config:
    def __init__(self, api_url: str, timeout: int | None = None) -> None:
        self.api_url = api_url
        self.timeout = timeout or 30

# Converted to Pydantic model
class Config(BaseModel):
    api_url: str
    timeout: int = 30
```

---

## 7. Type Checking with mypy

### 7.1 Basic Usage

DCApiX uses mypy for static type checking:

```bash
# Check the entire codebase
make mypy

# Check a specific module
make mypy MODULE=dc_api_x.config
```

### 7.2 Configuration

mypy configuration in `mypy.ini`:

```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
strict_optional = True

[pydantic-mypy]
init_forbid_extra = True
init_typed = True
warn_required_dynamic_aliases = True
```

### 7.3 Common Issues and Solutions

* **Missing imports**: Use `typing.TYPE_CHECKING` for circular imports
* **Any types**: Use explicit `Any` when needed, but prefer specific types
* **Overloaded functions**: Use `@overload` for functions with multiple signatures
* **Type narrowing**: Use `isinstance()` and `assert` for type narrowing

---

## 8. Best Practices

1. **Type Everything**: Include type annotations for all function parameters and return values

2. **Use the Most Specific Types**: Prefer specific types over general ones

3. **Validate External Data**: Always validate external data with Pydantic models

4. **Keep Models Focused**: Create specific models for different use cases

5. **Use Field Constraints**: Add validation constraints to fields where appropriate

6. **Document with Types**: Use types as part of your documentation strategy

7. **Test Type Validity**: Include tests that verify type correctness

8. **Consistent Conventions**: Follow consistent naming and structure conventions

9. **Progressive Type Adoption**: Use MonkeyType to gradually add types to legacy code

10. **Regular Type Checking**: Run mypy as part of your CI/CD pipeline

---

## Related Documentation

* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [21 - Tech: Core Libraries](21-tech-core-libraries.md) - Core libraries
* [22 - Tech: Developer Tools](22-tech-developer-tools.md) - Developer tools
* [24 - Tech: Structured Logging](24-tech-structured-logging.md) - Structured logging
* [26 - Tech: CLI](26-tech-cli.md) - CLI implementation with Typer
