# Pydantic Guide for DCApiX

## Introduction

DCApiX leverages [Pydantic V2.11](https://docs.pydantic.dev/2.11/) for robust data validation, serialization, and configuration management. This guide provides a comprehensive overview of Pydantic usage within DCApiX, serving as a central reference for developers.

## Core Pydantic V2.11 Features in DCApiX

### Models and Validation

DCApiX uses Pydantic's data models to validate, serialize, and document data structures:

- [BaseModel](https://docs.pydantic.dev/2.11/api/base_model/) - Core model class for data validation
- [RootModel](https://docs.pydantic.dev/2.11/api/root_model/) - Root container for collections
- [Dataclasses](https://docs.pydantic.dev/2.11/api/dataclasses/) - Integration with Python dataclasses
- [TypeAdapter](https://docs.pydantic.dev/2.11/api/type_adapter/) - Validate and serialize arbitrary types
- [validate_call](https://docs.pydantic.dev/2.11/api/validate_call/) - Decorator for function argument validation

### Model Configuration

Custom behaviors can be configured through:

- [Field Aliases](https://docs.pydantic.dev/2.11/api/aliases/) - Rename fields for serialization/deserialization
- [Model Config](https://docs.pydantic.dev/2.11/api/config/) - Configure model behavior

### Validation and Serialization

Fine-grained control over validation and serialization:

- [JSON Schema](https://docs.pydantic.dev/2.11/api/json_schema/) - Generate JSON Schema
- [Error Handling](https://docs.pydantic.dev/2.11/api/errors/) - Customizable error handling
- [Functional Validators](https://docs.pydantic.dev/2.11/api/functional_validators/) - Custom validation logic
- [Functional Serializers](https://docs.pydantic.dev/2.11/api/functional_serializers/) - Custom serialization

### Types and Type Handling

DCApiX utilizes Pydantic's extensive type system:

- [Standard Library Types](https://docs.pydantic.dev/2.11/api/standard_library_types/) - Support for Python's built-in types
- [Custom Types](https://docs.pydantic.dev/2.11/api/types/) - Special types for common use cases
- [Network Types](https://docs.pydantic.dev/2.11/api/networks/) - Email, URL, etc.
- [Annotated Handlers](https://docs.pydantic.dev/2.11/api/annotated_handlers/) - Field metadata for validation

### Extended Type Support

For specialized use cases, DCApiX provides access to additional types:

- [Color Types](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_color/)
- [Country Types](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_country/)
- [Payment Card Types](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_payment/)
- [Phone Number Types](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_phone_numbers/)
- [Banking Routing Numbers](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_routing_numbers/)
- [Geographic Coordinates](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_coordinate/)
- [MAC Addresses](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_mac_address/)
- [ISBN Numbers](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_isbn/)
- [Pendulum DateTime](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_pendulum_dt/)
- [Currency Codes](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_currency_code/)
- [Language Codes](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_language_code/)
- [Script Codes](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_script_code/)
- [Semantic Versions](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_semantic_version/)
- [Timezone Names](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_timezone_name/)
- [ULID](https://docs.pydantic.dev/2.11/api/pydantic_extra_types_ulid/)

### Error Handling

Comprehensive error handling capabilities:

- [Error Overview](https://docs.pydantic.dev/2.11/errors/errors/)
- [Validation Errors](https://docs.pydantic.dev/2.11/errors/validation_errors/)
- [Usage Errors](https://docs.pydantic.dev/2.11/errors/usage_errors/)

### Integration and Developer Tools

DCApiX takes advantage of Pydantic's ecosystem:

- [Devtools](https://docs.pydantic.dev/2.11/integrations/devtools/) - Development utilities
- [Rich Integration](https://docs.pydantic.dev/2.11/integrations/rich/) - Pretty printing
- [Linting Support](https://docs.pydantic.dev/2.11/integrations/linting/) - Code quality tools
- [Documentation Support](https://docs.pydantic.dev/2.11/integrations/documentation/) - API docs generation

### Common Use Cases

Examples of Pydantic usage patterns:

- [File Handling](https://docs.pydantic.dev/2.11/examples/files/)
- [HTTP Requests](https://docs.pydantic.dev/2.11/examples/requests/)
- [Queue Processing](https://docs.pydantic.dev/2.11/examples/queues/)
- [ORM Integration](https://docs.pydantic.dev/2.11/examples/orms/)
- [Custom Validators](https://docs.pydantic.dev/2.11/examples/custom_validators/)

### Advanced Topics

For those seeking deeper understanding:

- [Architecture](https://docs.pydantic.dev/2.11/internals/architecture/)
- [Annotation Resolution](https://docs.pydantic.dev/2.11/internals/resolving_annotations/)
- [Core Implementation](https://docs.pydantic.dev/2.11/api/pydantic_core/)
- [Schema Implementation](https://docs.pydantic.dev/2.11/api/pydantic_core_schema/)
- [Experimental Features](https://docs.pydantic.dev/2.11/api/experimental/)

## Pydantic V2.11 Settings in DCApiX

DCApiX uses [Pydantic Settings](https://docs.pydantic.dev/2.11/concepts/pydantic_settings/) for configuration management. This section details how to use this powerful feature for loading settings from various sources.

### Configuration Sources

Pydantic Settings supports loading configuration from:

- Environment variables
- `.env` files
- Secret files
- Configuration files (JSON, TOML, YAML)
- CLI arguments
- Profiles for multiple environments
- Cloud secret management services (AWS, Azure, GCP)

### Basic Usage

#### Loading Configuration

The simplest way to configure DCApiX is through environment variables:

```python
from dc_api_x.config import Config

# This will load configuration from environment variables
config = Config()

# Access configuration values
print(f"API URL: {config.url}")
print(f"Username: {config.username}")
# Access password securely
print(f"Password: {'*' * len(config.password.get_secret_value())}")
print(f"Timeout: {config.timeout}")
```

#### Environment Variables

DCApiX expects environment variables to be prefixed with `API_`. The following environment variables are supported:

| Environment Variable | Description               | Type    | Default |
|----------------------|---------------------------|---------|---------|
| `API_URL`            | API base URL              | string  | -       |
| `API_USERNAME`       | API username              | string  | -       |
| `API_PASSWORD`       | API password              | string  | -       |
| `API_TIMEOUT`        | Request timeout in seconds| integer | 30      |
| `API_VERIFY_SSL`     | Verify SSL certificates   | boolean | True    |
| `API_MAX_RETRIES`    | Maximum retry attempts    | integer | 3       |
| `API_RETRY_BACKOFF`  | Retry backoff factor      | float   | 0.5     |
| `API_DEBUG`          | Enable debug mode         | boolean | False   |
| `API_ENVIRONMENT`    | Environment name          | string  | None    |

#### Direct Initialization

You can also initialize configuration directly:

```python
from dc_api_x.config import Config

# Create configuration with direct values
config = Config(
    url="https://api.example.com",
    username="user123",
    password="pass123",  # Will be automatically converted to SecretStr
    timeout=30,
    verify_ssl=True,
    debug=True
)
```

### Configuration Profiles

Profiles allow you to maintain different configurations for different environments (development, staging, production).

#### Creating Profiles

Create a file named `.env.{profile_name}` in your project directory:

`.env.dev`:

```bash
API_URL=https://dev-api.example.com
API_USERNAME=dev-user
API_PASSWORD=dev-pass
API_TIMEOUT=45
API_DEBUG=true
```

`.env.prod`:

```bash
API_URL=https://api.example.com
API_USERNAME=prod-user
API_PASSWORD=prod-pass
API_TIMEOUT=30
API_DEBUG=false
```

#### Loading Profiles

```python
from dc_api_x.config import Config, list_available_profiles

# List available profiles
profiles = list_available_profiles()
print(f"Available profiles: {profiles}")  # ['dev', 'prod']

# Load a specific profile
dev_config = Config.from_profile("dev")
print(f"Dev API URL: {dev_config.url}")  # https://dev-api.example.com
```

### Working with Aliases

Pydantic Settings allows renaming environment variables using aliases. This is useful when your environment variables follow a different naming convention than your code:

```python
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings

class MyConfig(BaseSettings):
    # Uses MY_API_KEY environment variable
    api_key: str = Field(validation_alias='MY_API_KEY')
    
    # Can use either SERVICE_REDIS_DSN or REDIS_URL
    redis_url: str = Field(
        validation_alias=AliasChoices('SERVICE_REDIS_DSN', 'REDIS_URL')
    )
```

### File-Based Configuration

#### Saving Configuration to a File

```python
from dc_api_x.config import Config

config = Config(
    url="https://api.example.com",
    username="user123",
    password="pass123"
)

# Save to JSON
config.save("config.json")
```

#### Loading Configuration from a File

```python
from dc_api_x.config import Config

# Load from JSON
config = Config.from_file("config.json")
```

### Secret Management

#### Using Secret Files

Pydantic Settings supports loading secrets from files, which is a common practice for container environments like Docker or Kubernetes.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/run/secrets')
    
    # Will be loaded from a file named 'database_password' in /run/secrets
    database_password: str
```

You can also use multiple secret directories:

```python
class Settings(BaseSettings):
    # Files in '/run/secrets' take priority over '/var/run'
    model_config = SettingsConfigDict(
        secrets_dir=('/var/run', '/run/secrets')
    )
    
    database_password: str
```

#### Using Cloud Secret Management Services

##### AWS Secrets Manager

```python
import os
from pydantic import BaseModel
from pydantic_settings import (
    AWSSecretsManagerSettingsSource,
    BaseSettings,
    PydanticBaseSettingsSource,
)

class Database(BaseModel):
    username: str
    password: str

class Settings(BaseSettings):
    database: Database
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        aws_settings = AWSSecretsManagerSettingsSource(
            settings_cls,
            os.environ['AWS_SECRETS_MANAGER_SECRET_ID'],
        )
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            aws_settings,
        )
```

##### Azure Key Vault

```python
import os
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel
from pydantic_settings import (
    AzureKeyVaultSettingsSource, 
    BaseSettings,
    PydanticBaseSettingsSource
)

class Settings(BaseSettings):
    api_key: str
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        az_key_vault_settings = AzureKeyVaultSettingsSource(
            settings_cls,
            os.environ['AZURE_KEY_VAULT_URL'],
            DefaultAzureCredential(),
        )
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            az_key_vault_settings,
        )
```

### Nested Models and Complex Types

Pydantic Settings supports nested models, which is useful for organizing related settings:

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    
class ApiSettings(BaseModel):
    url: str
    timeout: int = 30
    
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__"
    )
    
    database: DatabaseSettings
    api: ApiSettings
    debug: bool = False
```

With the above configuration, you can set environment variables like:

```bash
APP_DATABASE__HOST=db.example.com
APP_DATABASE__PORT=5432
APP_DATABASE__USERNAME=dbuser
APP_DATABASE__PASSWORD=dbpass
APP_API__URL=https://api.example.com
APP_API__TIMEOUT=60
APP_DEBUG=true
```

### Advanced Features

#### Configuration Reloading

You can reload configuration from sources (environment variables, .env files) at runtime:

```python
import os
from dc_api_x.config import Config

# Initial configuration
config = Config()
print(f"URL: {config.url}")

# Change environment variable
os.environ["API_URL"] = "https://updated-api.example.com"

# Reload configuration
config.model_reload()
print(f"Updated URL: {config.url}")  # https://updated-api.example.com
```

#### Converting to Dictionary

Convert configuration to a dictionary, useful for serialization:

```python
from dc_api_x.config import Config

config = Config(
    url="https://api.example.com",
    username="user123",
    password="pass123"
)

# Convert to dictionary
config_dict = config.to_dict()
print(config_dict)
```

#### Customizing Settings Sources Priority

You can customize the order of settings sources (initialize parameters, environment variables, .env files, secret files) by overriding the `settings_customise_sources` method:

```python
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

class CustomConfig(Config):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Change the priority order of sources
        return (
            env_settings,           # Environment variables first
            dotenv_settings,        # .env files second
            init_settings,          # Constructor parameters third
            file_secret_settings,   # Secret files last
        )
```

#### Creating Custom Settings Sources

You can create custom settings sources to load configuration from any source:

```python
import json
from pathlib import Path
from typing import Any
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

class JsonConfigSettingsSource(PydanticBaseSettingsSource):
    """Load settings from a JSON file."""
    
    def __init__(self, settings_cls: type[BaseSettings], json_file: Path) -> None:
        super().__init__(settings_cls)
        self.json_file = json_file
    
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        with self.json_file.open() as f:
            config_data = json.load(f)
        
        field_value = config_data.get(field_name)
        return field_value, field_name, False
    
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value
    
    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        
        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value
        
        return d
```

### Command Line Support

Pydantic Settings provides integrated CLI support:

```python
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)
    
    url: str
    username: str
    password: str
    debug: bool = False

# Example usage:
# python my_script.py --url=https://api.example.com --username=user --password=pass --debug

settings = Settings()
print(settings.model_dump())
```

### Integration with ApiClient

The configuration can be directly used with the ApiClient:

```python
import dc_api_x as apix
from dc_api_x.config import Config

# Load configuration from environment or .env file
config = Config()

# Create client with the configuration
client = apix.ApiClient(
    url=config.url,
    username=config.username,
    password=config.password.get_secret_value(),
    timeout=config.timeout,
    verify_ssl=config.verify_ssl,
    debug=config.debug
)

# Or using the from_config method
client = apix.ApiClient.from_config(config)
```

### Validation and Default Values

Unlike regular Pydantic models, BaseSettings fields' default values are validated by default. You can disable this by setting `validate_default=False`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)
    
    # Default won't be validated
    port: int = "8080"  # Would normally fail validation

print(Settings().port)  # '8080' as a string, not validated to be an int
```

## Best Practices

1. **Environment-Specific Profiles**: Create separate profiles for development, testing, staging, and production environments.

2. **Secrets Management**: Store passwords and API keys in environment variables rather than checked-in .env files, or use a secrets management service.

3. **Config Files for CI/CD**: Use configuration files for settings that need to be version-controlled or passed between systems.

4. **Security**: Never commit .env files or JSON files with secrets to version control. Add these files to .gitignore.

5. **Validation**: Use the built-in Pydantic validation to ensure configuration values are correct before using them.

6. **Explicit Types**: Always provide type annotations for all settings fields to ensure proper validation.

7. **Default Values**: Provide sensible defaults for optional settings to make your application more resilient.

8. **Documentation**: Document all available settings and their purpose.

9. **Type Hints**: Use proper typing for all models to leverage Pydantic's validation capabilities fully.

10. **Field Validation**: Implement field validators for complex validation logic that can't be expressed through type annotations.

11. **Error Handling**: Always handle validation errors appropriately in your application.

12. **Model Reuse**: Create reusable model components that can be shared across different parts of your application.

## Type Annotations with MonkeyType

DCApiX uses [MonkeyType](https://github.com/Instagram/MonkeyType) to enhance Pydantic models and other code with accurate type annotations. This section explains how to use MonkeyType to collect runtime type information and apply it to your codebase.

### Introduction to MonkeyType

MonkeyType is a runtime type collection tool developed by Instagram that automatically generates type annotations by observing the types of arguments and return values during program execution. It helps:

1. Discover types in existing untyped code
2. Generate field types for Pydantic models based on actual usage
3. Improve mypy coverage with minimal effort
4. Find type inconsistencies in the code

### Installation and Setup

MonkeyType is configured as a development dependency for the project:

```bash
# Ensure MonkeyType is installed
poetry install --with dev
# or
make install-dev
```

### Type Collection Workflow

The basic workflow for adding types with MonkeyType consists of:

1. **Collection**: Run tests with MonkeyType to collect runtime type information
2. **Discovery**: List modules that have collected type information
3. **Application**: Apply collected types to specific modules
4. **Refinement**: Manually review and refine the types if necessary
5. **Verification**: Verify type consistency with mypy

### Using MonkeyType in DCApiX

DCApiX includes several Makefile targets that simplify MonkeyType usage:

```bash
# Run all tests with MonkeyType to collect type information
make monkeytype-run

# Run a specific test with MonkeyType
make monkeytype-run TEST_PATH=tests/unit/test_config.py

# List modules with collected type information
make monkeytype-list

# Apply types to a specific module
make monkeytype-apply MODULE=dc_api_x.config

# Apply types to all modules at once
make monkeytype-apply-all

# Generate a stub file with collected types
make monkeytype-stub MODULE=dc_api_x.models

# Verify types with mypy
make monkeytype-mypy MODULE=dc_api_x.config

# Run complete MonkeyType cycle (collect, list, apply, verify)
make monkeytype-cycle
```

> **Note**: Even if some tests fail, MonkeyType can still collect types from the tests that executed successfully.

### Advanced Usage with Standalone Script

For more specific use cases, you can use the script `scripts/mk_monkeytype_runner.py` directly:

```bash
# Run all tests with MonkeyType
python scripts/mk_monkeytype_runner.py run

# Run a specific test
python scripts/mk_monkeytype_runner.py run --test-path tests/unit/test_config.py

# List modules with type information
python scripts/mk_monkeytype_runner.py list

# Apply types to a module
python scripts/mk_monkeytype_runner.py apply --module dc_api_x.config

# Apply types to all modules
python scripts/mk_monkeytype_runner.py apply --apply-all

# Generate stub for a module
python scripts/mk_monkeytype_runner.py stub --module dc_api_x.models
```

### Converting MonkeyType Annotations to Pydantic Models

MonkeyType generates standard Python type annotations that need to be converted to Pydantic field definitions. Here are examples of the conversion process:

#### Basic Example

**Original class without types:**

```python
class Config:
    def __init__(self, api_url, timeout=None):
        self.api_url = api_url
        self.timeout = timeout or 30
```

**After applying MonkeyType:**

```python
class Config:
    def __init__(self, api_url: str, timeout: Optional[int] = None) -> None:
        self.api_url = api_url
        self.timeout = timeout or 30
```

**Converted to Pydantic model:**

```python
class Config(BaseModel):
    api_url: str
    timeout: Optional[int] = 30
```

#### Example with Collections

**Original class:**

```python
class MyModel:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value or {}
```

**After MonkeyType:**

```python
class MyModel:
    def __init__(self, name: str, value: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.value = value or {}
```

**Converted to Pydantic:**

```python
class MyModel(BaseModel):
    name: str
    value: Dict[str, Any] = Field(default_factory=dict)
```

### Recommended Workflow for DCApiX Projects

For effective type annotation in DCApiX projects, follow this workflow:

1. **Identify Target Module**: Determine which module needs type annotations
2. **Run Targeted Tests**: Execute tests that exercise the target module with MonkeyType

   ```bash
   make monkeytype-run TEST_PATH=tests/unit/test_target_module.py
   ```

3. **Verify Collection**: Check if type information was collected

   ```bash
   make monkeytype-list
   ```

4. **Apply Types**: Apply the collected types to the module

   ```bash
   make monkeytype-apply MODULE=dc_api_x.target_module
   ```

5. **Manual Review**: Review and refine the applied types, especially for:
   - Pydantic models
   - Complex generic types
   - Return types in abstract methods
   - Parameters with default values
   - Union types

6. **Verify with mypy**: Check type consistency using mypy

   ```bash
   make monkeytype-mypy MODULE=dc_api_x.target_module
   ```

7. **Iterate**: Repeat the process for other modules or if additional type coverage is needed

### Solving Common Problems

#### Parameterized Generics with isinstance()

When using MonkeyType-generated types, you might encounter errors with parameterized generics in `isinstance()` checks:

```python
# Before - causes error
if isinstance(data, list[Any]):
    # code...

# After - correct usage
if isinstance(data, list):
    # code...
```

#### Missing Attributes

If you see errors like `'ClientConfig' object has no attribute 'auth_provider'`, this indicates a mismatch between your code and tests. Either update the tests to match the current code structure or add the missing attributes to your classes.

#### Incomplete Types

If MonkeyType generates `Any` or incomplete types, it usually means your tests aren't exercising all code paths. Improve test coverage to get more accurate type information.

### Limitations of MonkeyType

When using MonkeyType with Pydantic, be aware of these limitations:

- **Test Coverage Dependency**: MonkeyType only detects types used during test execution
- **Complex Type Refinement**: Generic types, unions, and other complex types often need manual refinement
- **Pydantic-Specific Features**: Features like Field, validator, and model_config must be added manually
- **Uncalled Code**: Types for functions or methods never called in tests won't be collected
- **Type Variety**: Tests must exercise code paths with different types to detect unions correctly
- **Failed Tests**: Failed tests won't contribute type information

### The py.typed File

The empty `py.typed` file in the `dc_api_x` package indicates that the package supports type annotations. This file is necessary for mypy and other type checking tools to recognize and process the package's type annotations.

## Complete Example

Here's a comprehensive example showing the various ways to use Pydantic Settings:

```python
import os
from pathlib import Path
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dc_api_x.config import Config, list_available_profiles

# 1. Define a nested model for database settings
class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: SecretStr

# 2. Define the main settings class
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_nested_delimiter="__",
        secrets_dir="/run/secrets",
        case_sensitive=False
    )
    
    # API settings
    api_url: str = Field(..., description="API base URL")
    api_timeout: int = Field(30, description="API timeout in seconds")
    
    # Database settings
    database: DatabaseSettings
    
    # Application settings
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")

# 3. Create .env.dev file for development profile
with open(".env.dev", "w") as f:
    f.write("APP_API_URL=https://dev-api.example.com\n")
    f.write("APP_API_TIMEOUT=45\n")
    f.write("APP_DATABASE__HOST=dev-db.example.com\n")
    f.write("APP_DATABASE__USERNAME=dev-user\n")
    f.write("APP_DATABASE__PASSWORD=dev-pass\n")
    f.write("APP_DEBUG=true\n")
    f.write("APP_LOG_LEVEL=DEBUG\n")

# 4. Set environment variables for production
os.environ["APP_API_URL"] = "https://api.example.com"
os.environ["APP_DATABASE__HOST"] = "db.example.com"
os.environ["APP_DATABASE__USERNAME"] = "prod-user"
os.environ["APP_DATABASE__PASSWORD"] = "prod-pass"

# 5. List available profiles
profiles = list_available_profiles()
print(f"Available profiles: {profiles}")  # ['dev']

# 6. Load settings from environment variables
env_settings = AppSettings()
print(f"Production API URL: {env_settings.api_url}")  # https://api.example.com

# 7. Load settings from development profile
dev_settings = AppSettings(_env_file=".env.dev")
print(f"Development API URL: {dev_settings.api_url}")  # https://dev-api.example.com

# 8. Save settings to file
dev_settings.model_dump_json(indent=2, path="config.json")

# 9. Load settings from file
with open("config.json") as f:
    config_json = f.read()
file_settings = AppSettings.model_validate_json(config_json)

# Clean up
Path(".env.dev").unlink()
Path("config.json").unlink()
```

## See Also

- [Pydantic Documentation](https://docs.pydantic.dev/2.11/)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/2.11/concepts/pydantic_settings/)
- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/2.11/migration/)
- [MonkeyType Documentation](https://github.com/Instagram/MonkeyType)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Environment Variables Best Practices](https://12factor.net/config)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
