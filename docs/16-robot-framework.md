# Robot Framework Integration for DCApiX

## Introduction

This guide outlines how to leverage [Robot Framework](https://robotframework.org/) within DCApiX as a plugin or supporting component. Rather than using DCApiX from Robot Framework, this approach integrates Robot Framework's powerful keyword-driven testing capabilities directly into DCApiX applications.

## Core Integration Features

### Robot Framework Plugin for DCApiX

The Robot Framework plugin for DCApiX enables:

- **Keyword-Driven Automation**: Write DCApiX logic using Robot Framework's intuitive keyword syntax
- **Declarative Testing**: Create expressive test scenarios that non-technical stakeholders can understand
- **Robot Framework Ecosystem**: Access the rich ecosystem of Robot Framework libraries as DCApiX extensions
- **Data-Driven Capabilities**: Parameterize your DCApiX operations with external data sources
- **Detailed Reports**: Generate comprehensive HTML reports for DCApiX operations

### Integration Components

| Component | Purpose |
|-----------|---------|
| DCApiX Robot Adapter | An adapter that provides DCApiX access to Robot Framework runtime |
| Robot Framework Runner | API for executing Robot Framework tests from DCApiX |
| Keyword Library | Exposes DCApiX functionality as Robot Framework keywords |
| Result Parser | Interprets Robot Framework reports within DCApiX workflows |
| Test Library Builder | Tools for generating custom Robot Framework libraries from DCApiX components |

## Installation

```bash
# Install the DCApiX Robot Framework plugin
pip install dc-api-x[robotframework]
```

## Basic Usage

### Importing Robot Framework Components

```python
import dc_api_x as apix
from dc_api_x.plugins.robot import RobotAdapter, RobotRunner

# Enable plugins to discover Robot Framework adapter
apix.enable_plugins()
robot = apix.get_adapter("robotframework")
```

### Running Robot Framework Tests From DCApiX

```python
# Simple example running a Robot Framework test suite
result = robot.run_test_suite("path/to/test_suite.robot")

# Check test results
if result.passed:
    print(f"All tests passed: {result.stats}")
else:
    print(f"Test failures: {result.failures}")

# Access detailed test data
for test in result.tests:
    print(f"Test: {test.name}, Status: {test.status}, Duration: {test.duration}s")
```

### Executing Robot Keywords Directly

```python
# Create a Robot Framework keyword executor
executor = robot.create_executor()

# Execute keywords directly
executor.run_keyword("Log", "Hello from DCApiX!")
result = executor.run_keyword("Get Current Date")
print(f"Current date: {result}")

# Chain multiple keywords
executor.run_keywords(
    ("Set Variable", "John Doe", "name"),
    ("Log", "${name}"),
    ("Should Be Equal", "${name}", "John Doe")
)
```

## Advanced Features

### Creating Custom Test Libraries from DCApiX Components

```python
from dc_api_x.plugins.robot import LibraryBuilder

# Create a Robot Framework library from DCApiX components
builder = LibraryBuilder("MyDCApiXLibrary")

# Add DCApiX-based keywords to the library
@builder.keyword
def connect_to_oracle_wms(url, username, password):
    """Connect to Oracle WMS using DCApiX."""
    wms = apix.get_adapter("oracle_wms")
    wms.connect(url, username=username, password=password)
    return wms

# Generate the library
library = builder.build()
robot.register_library(library)
```

### Data-Driven Operations with Robot Framework

```python
# Define test data
test_data = [
    {"name": "Test API 1", "url": "https://api1.example.com", "expected_status": 200},
    {"name": "Test API 2", "url": "https://api2.example.com", "expected_status": 200},
    {"name": "Test API 3", "url": "https://api3.example.com", "expected_status": 404}
]

# Run data-driven test with Robot Framework
robot_result = robot.run_test_with_data(
    "templates/api_test_template.robot",
    test_data,
    variables={"timeout": 30, "retry_count": 3}
)

# Process results in DCApiX
success_rate = robot_result.pass_percentage
print(f"API Test Success Rate: {success_rate}%")
```

### Robot Framework as a Domain-Specific Language for DCApiX

You can create domain-specific Robot Framework files that DCApiX executes:

```robotframework
*** Settings ***
Documentation    WMS Order Processing Flow

*** Variables ***
${ORDER_ID}    WO-12345
${WAREHOUSE}    CENTRAL
${TARGET_STATUS}    SHIPPED

*** Tasks ***
Process WMS Order
    Connect To WMS    ${WMS_URL}    ${WMS_USER}    ${WMS_PASSWORD}
    Verify Order Exists    ${ORDER_ID}
    Change Order Status    ${ORDER_ID}    ${TARGET_STATUS}
    ${result}=    Get Order Details    ${ORDER_ID}
    Should Be Equal    ${result.status}    ${TARGET_STATUS}
    Log    Order ${ORDER_ID} successfully processed
```

Execute this in DCApiX:

```python
# Load the task definition
task_file = "wms_order_processing.robot"

# Execute with DCApiX Robot adapter
robot.run_task(
    task_file,
    variables={
        "WMS_URL": config.wms_url,
        "WMS_USER": config.wms_user,
        "WMS_PASSWORD": config.wms_password
    }
)
```

## Implementing the Robot Framework Runner

Below is a complete implementation of the `RobotRunner` class used by the `RobotFrameworkAdapter` to execute Robot Framework test suites:

```python
import os
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from robot import run_cli

@dataclass
class TestResult:
    name: str
    status: str
    message: str = ""
    duration: float = 0.0
    tags: List[str] = field(default_factory=list)
    
@dataclass
class SuiteResult:
    name: str
    passed: bool
    tests: List[TestResult] = field(default_factory=list)
    suites: List['SuiteResult'] = field(default_factory=list)
    message: str = ""
    stats: Dict[str, int] = field(default_factory=dict)
    
    @property
    def failures(self) -> List[TestResult]:
        """Return list of failed tests."""
        return [t for t in self.tests if t.status.upper() != 'PASS']
    
    @property
    def pass_percentage(self) -> float:
        """Calculate the percentage of passed tests."""
        total = len(self.tests)
        if total == 0:
            return 100.0
        passed = len([t for t in self.tests if t.status.upper() == 'PASS'])
        return (passed / total) * 100

class ResultParser:
    """Parses Robot Framework output.xml into structured results."""
    
    def parse(self, output_path: str) -> SuiteResult:
        """Parse Robot Framework output.xml into a SuiteResult object."""
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Robot Framework output file not found: {output_path}")
        
        tree = ET.parse(output_path)
        root = tree.getroot()
        
        # Parse the top-level suite
        suite_elem = root.find("suite")
        if suite_elem is None:
            raise ValueError("No suite element found in output.xml")
        
        # Get statistics
        stat_elem = root.find("statistics/total")
        stats = {}
        if stat_elem is not None:
            for stat in stat_elem.findall("stat"):
                stats[stat.get("name", "").lower()] = int(stat.get("pass", 0))
        
        return self._parse_suite(suite_elem, stats)
    
    def _parse_suite(self, suite_elem: ET.Element, stats: Dict[str, int]) -> SuiteResult:
        """Parse a suite element from output.xml."""
        name = suite_elem.get("name", "Unknown Suite")
        status_elem = suite_elem.find("status")
        status = status_elem.get("status", "FAIL") if status_elem is not None else "FAIL"
        
        # Parse tests in this suite
        tests = []
        for test_elem in suite_elem.findall("test"):
            test_name = test_elem.get("name", "Unknown Test")
            test_status_elem = test_elem.find("status")
            if test_status_elem is None:
                continue
                
            test_status = test_status_elem.get("status", "FAIL")
            test_message = test_status_elem.text or ""
            
            # Calculate duration
            start = test_status_elem.get("starttime", "")
            end = test_status_elem.get("endtime", "")
            duration = 0.0
            if start and end:
                try:
                    from robot.utils import get_elapsed_time
                    duration = get_elapsed_time(start, end)
                except ImportError:
                    # Fallback if Robot utils are not available
                    duration = 0.0
            
            # Get tags
            tags = []
            tags_elem = test_elem.find("tags")
            if tags_elem is not None:
                tags = [tag.text for tag in tags_elem.findall("tag") if tag.text]
                
            tests.append(TestResult(
                name=test_name,
                status=test_status,
                message=test_message,
                duration=duration,
                tags=tags
            ))
        
        # Parse sub-suites recursively
        suites = []
        for subsuite_elem in suite_elem.findall("suite"):
            suites.append(self._parse_suite(subsuite_elem, {}))  # Empty stats for sub-suites
            
        return SuiteResult(
            name=name,
            passed=status == "PASS",
            tests=tests,
            suites=suites,
            stats=stats
        )

class RobotRunner:
    """Runs Robot Framework tests and parses the results."""
    
    def __init__(self, parser: Optional[ResultParser] = None, **options):
        self.options = options
        self.parser = parser or ResultParser()
        
    def run_suite(self, path: str, **kwargs) -> SuiteResult:
        """Run a Robot Framework test suite from a file or directory."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Test suite not found: {path}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.xml")
            
            # Combine base options with kwargs
            options = {**self.options, **kwargs}
            options.setdefault("outputdir", temp_dir)
            options.setdefault("output", "output.xml")
            
            # Convert options to command line arguments
            args = self._build_arguments(path, options)
            
            # Run the tests
            try:
                run_cli(args)
            except SystemExit:
                # Robot Framework always calls sys.exit, we need to catch it
                pass
                
            # Parse results
            return self.parser.parse(output_path)
    
    def run_string(self, content: str, **kwargs) -> SuiteResult:
        """Run Robot Framework tests from a string."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary robot file
            robot_file = os.path.join(temp_dir, "test.robot")
            with open(robot_file, "w", encoding="utf-8") as f:
                f.write(content)
                
            # Run the suite
            return self.run_suite(robot_file, **kwargs)
    
    def run_task(self, path: str, variables: Optional[Dict[str, Any]] = None, **kwargs) -> SuiteResult:
        """Run a Robot Framework task file with variables."""
        kwargs.setdefault("rpa", True)  # Enable RPA mode for tasks
        
        # Convert variables to command line format if provided
        if variables:
            var_args = {}
            for name, value in variables.items():
                var_args[f"variable:{name}"] = str(value)
            kwargs.update(var_args)
            
        return self.run_suite(path, **kwargs)
            
    def _build_arguments(self, path: str, options: Dict[str, Any]) -> List[str]:
        """Convert options dictionary to command line arguments."""
        args = []
        
        # Add all options as command line arguments
        for key, value in options.items():
            if key == "variable":
                # Handle variables specially
                for var_name, var_value in value.items():
                    args.extend(["--variable", f"{var_name}:{var_value}"])
            elif key.startswith("variable:"):
                # Handle directly specified variables
                var_name = key.split(":", 1)[1]
                args.extend(["--variable", f"{var_name}:{value}"])
            elif isinstance(value, bool):
                # Handle boolean flags
                if value:
                    args.append(f"--{key}")
            else:
                # Handle other options
                args.extend([f"--{key}", str(value)])
        
        # Add the path last
        args.append(path)
        
        return args
```

## Real-World Example: WMS Integration

Here's a complete example showing how to use DCApiX with Robot Framework to automate Oracle WMS operations:

### 1. Create a Custom WMS Library

First, create a Robot Framework library that wraps DCApiX's WMS adapter:

```python
from dc_api_x.plugins.robot import LibraryBuilder
import dc_api_x as apix

# Initialize the library builder
builder = LibraryBuilder("OracleWMSLibrary")

# Get the WMS adapter
apix.enable_plugins()
wms_adapter = apix.get_adapter("oracle_wms")

@builder.keyword
def connect_to_wms(url, username, password, warehouse=None):
    """Connect to the Oracle WMS system.
    
    Args:
        url: The WMS server URL
        username: WMS username
        password: WMS password
        warehouse: Optional warehouse code
    """
    wms_adapter.connect(
        url, 
        username=username, 
        password=password,
        warehouse=warehouse
    )
    return True

@builder.keyword
def create_wave(wave_number, carrier_code, orders=None):
    """Create a new wave in WMS.
    
    Args:
        wave_number: The wave identifier
        carrier_code: The carrier code
        orders: Optional list of order numbers to include
    """
    result = wms_adapter.create_wave(
        wave_number=wave_number,
        carrier_code=carrier_code,
        orders=orders or []
    )
    return result

@builder.keyword
def release_orders(order_numbers):
    """Release orders in WMS.
    
    Args:
        order_numbers: List of order numbers to release
    """
    if isinstance(order_numbers, str):
        order_numbers = [order_numbers]
    results = {}
    for order in order_numbers:
        results[order] = wms_adapter.release_order(order)
    return results

@builder.keyword
def get_order_status(order_number):
    """Get the current status of an order.
    
    Args:
        order_number: The order number to check
    """
    order = wms_adapter.get_order(order_number)
    return order.get("status", "UNKNOWN")

@builder.keyword
def verify_order_status(order_number, expected_status, message=None):
    """Verify that an order has the expected status.
    
    Args:
        order_number: The order number to check
        expected_status: The expected status
        message: Optional message for the assertion
    """
    actual_status = get_order_status(order_number)
    if actual_status != expected_status:
        message = message or f"Order {order_number} has status {actual_status}, expected {expected_status}"
        raise AssertionError(message)
    return True

# Generate the library
wms_library = builder.build()
```

### 2. Create a WMS Task for DCApiX

Next, create a Robot Framework task file for WMS operations:

```robotframework
*** Settings ***
Documentation    WMS Order Wave Processing Workflow

*** Variables ***
@{ORDER_NUMBERS}    ORD-12345    ORD-12346    ORD-12347
${WAVE_NUMBER}      WAVE-001
${CARRIER}          FEDEX
${TARGET_STATUS}    RELEASED

*** Tasks ***
Process Order Wave
    Connect To WMS    ${WMS_URL}    ${WMS_USER}    ${WMS_PASSWORD}    ${WMS_WAREHOUSE}
    Log    Creating wave ${WAVE_NUMBER} with carrier ${CARRIER}
    ${wave_result}=    Create Wave    ${WAVE_NUMBER}    ${CARRIER}    ${ORDER_NUMBERS}
    
    # Release the orders
    ${release_results}=    Release Orders    ${ORDER_NUMBERS}
    Log    Release results: ${release_results}
    
    # Verify all orders were released
    FOR    ${order}    IN    @{ORDER_NUMBERS}
        Verify Order Status    ${order}    ${TARGET_STATUS}    Order ${order} was not released correctly
    END
    
    Log    Wave ${WAVE_NUMBER} processing completed successfully
```

### 3. Execute the WMS Task from DCApiX

Finally, execute this task from your DCApiX application:

```python
import dc_api_x as apix
from dc_api_x.plugins.robot import RobotAdapter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Main application function
def process_wms_wave(config, orders):
    """Process a wave of orders in WMS using Robot Framework.
    
    Args:
        config: Application configuration
        orders: List of order numbers to process
    """
    # Enable plugins to discover Robot Framework adapter
    apix.enable_plugins()
    robot = apix.get_adapter("robotframework")
    
    # Register our custom WMS library with the Robot adapter
    from wms_library import wms_library
    robot.register_library(wms_library)
    
    # Set up variables for the task
    variables = {
        "WMS_URL": config.wms_url,
        "WMS_USER": config.wms_user,
        "WMS_PASSWORD": config.wms_password,
        "WMS_WAREHOUSE": config.wms_warehouse,
        "ORDER_NUMBERS": orders,
        "WAVE_NUMBER": f"WAVE-{generate_wave_number()}",
        "CARRIER": config.default_carrier,
        "TARGET_STATUS": "RELEASED"
    }
    
    # Execute the Robot task
    logger.info(f"Starting WMS wave processing for {len(orders)} orders")
    result = robot.run_task(
        "tasks/wms_wave_processing.robot",
        variables=variables,
        log="DEBUG",  # Enable debug logging in Robot Framework
        report=True,  # Generate an HTML report
        outputdir="logs/robot"  # Where to store the logs
    )
    
    # Process the results
    if result.passed:
        logger.info(f"Wave processing completed successfully")
        return {
            "status": "success",
            "wave_id": variables["WAVE_NUMBER"],
            "orders_processed": len(orders)
        }
    else:
        logger.error(f"Wave processing failed: {len(result.failures)} errors")
        for failure in result.failures:
            logger.error(f"Test '{failure.name}' failed: {failure.message}")
            
        return {
            "status": "error",
            "wave_id": variables["WAVE_NUMBER"],
            "errors": [f"{f.name}: {f.message}" for f in result.failures]
        }
        
def generate_wave_number():
    """Generate a unique wave number."""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S")

# Example usage in a DCApiX application
if __name__ == "__main__":
    # Application configuration
    from config import AppConfig
    config = AppConfig()
    
    # Orders to process
    orders_to_process = ["ORD-12345", "ORD-12346", "ORD-12347"]
    
    # Process the orders
    result = process_wms_wave(config, orders_to_process)
    print(f"Wave processing result: {result}")
```

This example demonstrates how DCApiX can leverage Robot Framework for WMS operations, providing:

1. A clean separation between WMS integration details (in the library) and the business process (in the task file)
2. A domain-specific language for WMS operations that business analysts can understand and modify
3. Detailed reporting capabilities for tracking operation success/failure
4. Error handling and logging integration between DCApiX and Robot Framework

The ability to express complex WMS workflows in Robot Framework's keyword-driven syntax while leveraging DCApiX's robust integration capabilities creates a powerful combination for enterprise automation needs.

## Use Cases in DCApiX

### Automated Workflow Testing

Use the Robot Framework plugin to create end-to-end tests for DCApiX workflows:

```python
# Test a complete business process across multiple systems
workflow_test = """
*** Settings ***
Documentation    Test Order to Shipping Workflow

*** Test Cases ***
Order To Shipping Process
    # Create order in ERP
    ${order_id}=    Create Order In ERP    SKU-123    quantity=5
    
    # Verify WMS received order
    Connect To WMS
    ${wms_order}=    Get WMS Order By ERP ID    ${order_id}
    Should Not Be Empty    ${wms_order}
    
    # Process in WMS
    Process WMS Order    ${wms_order.id}
    
    # Verify shipping status in both systems
    ${erp_status}=    Get Order Status In ERP    ${order_id}
    ${wms_status}=    Get Order Status In WMS    ${wms_order.id}
    Should Be Equal    ${erp_status}    SHIPPED
    Should Be Equal    ${wms_status}    SHIPPED
"""

# Run the test using DCApiX Robot adapter
result = robot.run_test_string(workflow_test)
```

### Business Process Automation

Define and execute business processes using Robot Framework's readable syntax:

```python
# Load a business process definition
process = robot.load_process("processes/inventory_reconciliation.robot")

# Execute the process with specific parameters
result = process.run(
    warehouse_id="WH001",
    reconciliation_date="2023-01-15",
    generate_report=True
)

# Process the results in DCApiX
if result.success:
    # Send success notification
    notification_client.send("Inventory reconciliation completed successfully")
else:
    # Handle errors
    error_handler.process(result.errors)
```

### System Integration Testing

Test integrations between multiple systems managed by DCApiX:

```python
# Run integration tests across systems
integration_result = robot.run_test_suite("tests/integration/")

# Generate detailed integration report
report = robot.generate_report(
    integration_result,
    title="System Integration Test Results",
    include_screenshots=True,
    output_dir="reports/integration/"
)

# Email the report to stakeholders
if not integration_result.passed:
    notification.email_report(
        recipients=["team@example.com"],
        subject="Integration Test Failures",
        report_path=report.html_path
    )
```

## Implementing a DCApiX Robot Framework Plugin

### Plugin Structure

```bash
dc-api-x-robotframework/
├── dc_api_x_robotframework/
│   ├── __init__.py
│   ├── robot_adapter.py
│   ├── runner.py
│   ├── keyword_library.py
│   └── result_parser.py
└── pyproject.toml
```

### Adapter Implementation (`robot_adapter.py`)

```python
from dc_api_x.ext.adapters import ProtocolAdapter
from robot import run_cli
from .runner import RobotRunner
from .result_parser import ResultParser

class RobotFrameworkAdapter(ProtocolAdapter):
    """Adapter for using Robot Framework capabilities in DCApiX."""
    
    def __init__(self, **options):
        self.options = options
        self.result_parser = ResultParser()
        
    def create_runner(self, **kwargs):
        """Create a Robot Framework runner with specified options."""
        return RobotRunner(parser=self.result_parser, **{**self.options, **kwargs})
    
    def run_test_suite(self, path, **kwargs):
        """Run a Robot Framework test suite directly."""
        runner = self.create_runner(**kwargs)
        return runner.run_suite(path)
    
    def run_test_string(self, content, **kwargs):
        """Run Robot Framework test content from a string."""
        runner = self.create_runner(**kwargs)
        return runner.run_string(content)
    
    def create_executor(self, **kwargs):
        """Create a Robot Framework keyword executor."""
        from .keyword_executor import KeywordExecutor
        return KeywordExecutor(**kwargs)
```

### Plugin Registration (`__init__.py`)

```python
from dc_api_x import hookspecs

def register_adapters(registry):
    """Register the Robot Framework adapter."""
    from .robot_adapter import RobotFrameworkAdapter
    registry["robotframework"] = RobotFrameworkAdapter
    
def register_hooks(registry):
    """Register Robot Framework related hooks."""
    from .hooks import RobotResultHook
    registry.append(RobotResultHook)
```

### Plugin Configuration (`pyproject.toml`)

```toml
[project]
name = "dc-api-x-robotframework"
version = "0.1.0"
dependencies = [
    "dc-api-x>=0.2.0",
    "robotframework>=6.0.0"
]

[project.optional-dependencies]
selenium = ["robotframework-seleniumlibrary>=6.0.0"]
requests = ["robotframework-requests>=0.9.0"]
database = ["robotframework-databaselibrary>=1.2.0"]

[project.entry-points."dc_api_x.plugins"]
robotframework = "dc_api_x_robotframework"
```

## Best Practices

### When to Use Robot Framework in DCApiX

- **Acceptance Testing**: When you need clear, stakeholder-readable test definitions
- **Cross-System Processes**: For defining workflows that span multiple systems
- **Data-Driven Operations**: When you need to perform the same operations with different data sets
- **Parallel Execution**: When you need to scale out tests across multiple machines
- **Reusing Existing Robot Framework Assets**: When transitioning from Robot Framework tests to DCApiX

### Integration Patterns

1. **Adapter Pattern**: Use the Robot Framework adapter to execute Robot Framework capabilities
2. **Bridge Pattern**: Create bridges between DCApiX components and Robot Framework keywords
3. **Library Pattern**: Build custom Robot Framework libraries around DCApiX functionality
4. **Runner Pattern**: Execute Robot Framework tests as part of DCApiX workflows

### Performance Considerations

- Load Robot Framework only when needed via lazy imports
- Consider using the `pabot` library for parallel execution
- Cache Robot Framework keyword libraries for repeated use
- Use Robot Framework's dryrun mode for validation before execution

## Future Roadmap

The DCApiX Robot Framework integration will expand to include:

- **Visual Testing**: Integration with Robot Framework visual testing libraries
- **RPA Capabilities**: Robotic Process Automation features for business workflows
- **CI/CD Integration**: Streamlined testing within continuous integration pipelines
- **Custom Report Generators**: DCApiX-specific reporting extensions

## See Also

- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [DCApiX Plugin System](05-plugin-system.md)
- [Testing with pytest](14-pytest.md)
- [DCApiX Architecture](03-architecture.md)

-----

<https://robotframework.org/>
<https://docs.robotframework.org/docs>

Robot Framework is open source and supported by Robot Framework Foundation. There is a huge community of contributors around the tool. The software is built with expandability in mind and there are numerous ways to extend it's use cases for various needs.

If you have created or found a library that you think should be listed here, please let us know by submitting a pull request or an issue. You are also welcome to report unmaintained ones that shouldn't be listed anymore.

Libraries
Built-in
Tools
Separately developed external libraries that can be installed based on your needs. Creating your own libraries is a breeze. For instructions, see creating test libraries in Robot Framework User Guide.
Filter by tag

Name

Description

Stars

Tags
SeleniumLibrary 
Web testing library that uses popular Selenium tool internally.
1304 web, selenium
Browser Library 
A modern web testing library powered by Playwright. Aiming for speed, reliability and visibility.
777 web
HTTP RequestsLibrary (Python) 
HTTP level testing using Python Requests internally.
458 http
AppiumLibrary 
Android and iOS testing. Uses Appium internally.
371 mobile
RESTinstance 
Test library for HTTP JSON APIs.
195 http
Database Library (Python) 
Python based library for database testing. Works with any Python interpreter, including Jython.
141 db
SikuliLibrary 
Provides keywords to test UI through Sikulix. This library supports Python 2.x and 3.x.
137 ui
Zoomba Library 
Extends features in many popular tools for GUI, Rest API, Soap API, Mobile, and Windows (WinAppDriver) automation. An ideal all-in-one toolkit for new or existing Robot Framework projects.
136 ui, http
DataDriver Library 
Data-Driven Testing with external 📤 data tables (csv, xls, xlsx, etc.). 🧬 Pairwise Combinatorial Testing support.
117 db
DebugLibrary 
A debug library for RobotFramework, which can be used as an interactive shell(REPL) also.
98 
ImageHorizonLibrary 
Cross-platform, pure Python library for GUI automation based on image recognition.
72 ui, visual
Python Library Core 
Tools to ease creating larger test libraries for Robot Framework using Python.
55 tools
PuppeteerLibrary 
Web testing using Puppeteer tool internally.
53 web, ui
WatchUI 
Visual testing library for visual difference testing as well as image content testing (including PDF documents). Runs on Selenium to generate screenshots, uses PyMuPDF to process PDFs and Tesseract OCR to recognize text.
51 ui
Robotframework-FlaUI 
Robotframework-FlaUI is a keyword based user interface automation testing library for Windows applications like Win32, WinForms, WPF or Store Apps. It's based on the FlaUI user interface automation library.
47 windows, ui
SapGuiLibrary 
Testing the SAPGUI client using the internal SAP Scripting Engine
47 ui, sap
JavalibCore 
Base for implementing larger Java based test libraries for Robot Framework.
42 java
DocTest Library 
Library for Document Testing, offers visual/content comparisons and masks for images, PDFs and more.
38 pdf, visual
Django Library 
Library for Django, a Python web framework.
37 django
ScreenCapLibrary 
Taking screenshots and video recording. Similar functionality as Screenshot standard library, with some additional features.
37 ui
Qweb 
A modern web testing library focusing on making web testing and automation Easy 🎉 and maintainable 🧹 with its high level keyword design.
35 web, ui
AutoItLibrary 
Windows GUI testing library that uses AutoIt freeware tool as a driver.
32 windows, ui
CURFLibrary 
Testing CAN bus with support for ISO-TP and UDS.
32 
ConfluentKafkaLibrary 
Python confluent kafka.
28 
Diff Library 
Diff two files together.
23 
MQTT library 
Testing MQTT brokers and applications.
23 iot
SeleniumLibrary for Java 
Java port of the SeleniumLibrary.
23 java, selenium
ArchiveLibrary 
Handling zip- and tar-archives.
22 zip
HttpRequestLibrary (Java) 
HTTP level testing using Apache HTTP client. Available also at Maven central.
21 http, java
JavaFXLibrary 
Testing JavaFX applications, based on TestFX. Has also remote interface support.
21 java
TestFX Library 
Enables testing Java FX applications using the TestFX framework. Has also remote interface support. Maintained Fork...
19 java
Dependency Library 
Declare dependencies between tests. Ideally tests are independent, but when tests depend on earlier tests, DependencyLibrary makes it easy to explicitly declare these dependencies and have tests that depend on each other do the right thing.
13 
CncLibrary 
Driving a CNC milling machine.
12 rpa
Database Library (Java) 
Java-based library for database testing. Usable with Jython. Available also at Maven central.
12 java
RemoteApplications 
Special test library for launching Java applications on a separate JVM and taking other libraries into use on them.
12 java
SeleniumScreenshots 
Annotating and cropping screenshots taken with SeleniumLibrary.
11 ui, selenium
Plone.app .robotframework 
Provides resources and tools for writing functional Selenium tests for Plone CMS and its add-ons.
11 selenium
OracleDBLibrary 
A database testing library for Robot Framework that utilizes the python-oracledb tool internally.
9 db, oracle, oracledb
Eclipse Library 
Testing Eclipse RCP applications using SWT widgets.
8 
FTP library 
Testing and using FTP server with Robot Framework.
7 ftp
KiCadLibrary 
Interacting with KiCad EDA designs.
7 
AutoRecorder 
Allows automatically recording video for test/suites execution.
6 visual
ListenerLibrary 
Register keywords to run before/after other keywords and suites.
3 
TFTPLibrary 
Interact over Trivial File Transfer Portocol.
3 ftp
DoesIsLibrary 
Autogenerated keywords like Is Something, Does Someting created form assertion keywords like Should Be, Should Not Be, etc
1 
Robotframework-MailClientLibrary 
The Robotframework-MailClientLibrary is a keyword-based mail client library that supports testing of mail protocols, including IMAP, POP3, and SMTP with or without SSL connection.
1 mail, imap, smtp, pop3, ssl
UDS Library 
UDS (Unified Diagnostic Services) keyword library based on udsoncan, doipclient and odxtools. This library is part of the RobotFramework AIO (All In One) OSS project.
N/A embedded, automotive
WADLibrary 
Application testing library that utilizes Win App Driver.
N/A windows
SwingLibrary 
Testing Java applications with Swing GUI.
N/A java, ui
SSHLibrary 
Enables executing commands on remote machines over an SSH connection. Also supports transfering files using SFTP.
N/A ftp, ssh
SoapLibrary 
Designed for those who want to work with webservice automation as if they were using SoapUI, make a request through an XML file, and receive the response in another XML file.
N/A http
RoboSAPiens 
RoboSAPiens is a library for automating the Windows SAP GUI. Its key innovation (compared to SapGuiLibrary) is that UI elements can be selected using the texts in the GUI. No need to use a third-party tool to find some XPath-like selectors. Moreover, RoboSAPiens is under active development.
N/A ui, sap
Robotframework-XmlValidator 
A Robot Framework test library for validating XML files against XSD schemas, and more.
N/A xml, xsd, xmlschema
Robotframework-faker 
Library for Faker, a fake test data generator.
N/A 
RemoteSwingLibrary 
Testing and connecting to a java process and using SwingLibrary, especially Java Web Start applications.
N/A java
Rammbock 
Generic network protocol test library that offers easy way to specify network packets and inspect the results of sent and received packets.
N/A http
Mainframe3270 Library 
Allows the creation of automated test scripts to test IBM Mainframe 3270.
N/A ibm
DoIP Library 
DoIP (Diagnostic over Internet Protocol) keyword library based on doipclient. This library is part of the RobotFramework AIO (All In One) OSS project.

Libraries
Built-in
Tools
Libraries and tools that are bundled with the framework. Libraries provide the actual automation and testing capabilities to Robot Framework by providing keywords.
Filter by tag

Name

Description

Tags
Builtin 
Provides a set of often needed generic keywords. Always automatically available without imports.
library
Collections 
Provides a set of keywords for handling Python lists and dictionaries.
library
DateTime 
Library for date and time conversions.
library
Dialogs 
Provides means for pausing the execution and getting input from users.
library
Libdoc 
Generate keyword documentation for test libraries and resource files.
tool
OperatingSystem 
Enables various operating system related tasks to be performed in the system where Robot Framework is running.
library
Process 
Library for running processes in the system.
library
Rebot 
Generate logs and reports based on XML outputs and for combining multiple outputs together.
tool
Remote 
Special library acting as a proxy between Robot Framework and libraries elsewhere. Actual libraries can be running on different machines and be implemented using any programming language supporting XML-RPC protocol.
library
Screenshot 
Provides keywords to capture screenshots of the desktop.
library
String 
Library for generating, modifying and verifying strings.
library
Telnet 
Makes it possible to connect to Telnet servers and execute commands on the opened connections.
library
Testdoc 
Generate high level HTML documentation based on Robot Framework test cases.
tool
Tidy 
Cleaning up and changing format of Robot Framework test data files.
tool
XML 
Library for generating, modifying and verifying XML files.
library

Supporting tools ease automation: editing, running, building and so on. Most of these tools are developed as separate projects, but some are built into the framework itself.
Filter by tag

Name

Description

Stars

Tags
RIDE 
Standalone Robot Framework test data editor.
915 editor
Pabot 
A parallel executor for Robot Framework tests and tasks.
450 
RCC 
Share your Robot projects with ease. RCC allows you to create, manage, and distribute Python-based self-contained automation packages.
393 
Robot Framework Hub 
Lightweight web server that provides access to the Robot Framework test assets via browser.
168 
Robocop linter 
Static code analysis tool for Robot Framework with use of latest robot API and many built-in rules that can be easily configured or switched off.
163 
Sublime assistant 
A plugin for Sublime Text 2 & 3 by Andriy Hrytskiv.
110 editor
Vim plugin 
Vim plugin for development with Robot Framework.
89 editor
rfswarm 
Testing tool that allows you to use Robot Framework test cases for performance or load testing.
85 
Robot Corder 
Robot Corder generates Robot Framework test script by recording user interactions and scanning the html page in your Chrome browser. It aims to be equivalent of Selenium IDE for RobotFramework browser test automation.
84 
Jenkins plugin 
Plugin to collect and publish Robot Framework execution results in Jenkins.
60 build
Robotmk 
With Robotmk, arbitrary Robot Framework tests can be seamlessly integrated into the Checkmk monitoring tool. In addition to server and network metrics, Checkmk administrators also get worthful insights about on how well business applications are performing from the users point of view ("End-2-End Monitoring"). Robotmk can flexibly monitor and graph the runtimes of tests and keywords, and also alert when related SLAs are violated.
51 
Notepad++ 
Syntax highlighting for Notepad++.
31 editor
Emacs major mode 
Emacs major mode for editing tests.
30 editor
Atom plugin 
Robot Framework plugin for Atom.
26 editor
Sublime plugin 
A plugin for Sublime Text 2 by Mike Gershunovsky.
26 editor
Maven plugin 
Maven plugin for using Robot Framework.
24 build
Oxygen 
Tool for consolidating other test tools' reporting to Robot Framework outputs.
24 
StatusChecker 
A tool for validation that executed Robot Framework test cases have expected statuses and log messages. Mainly targeted for test library developers.
24 
Distbot 
A bot for self distribution of Robot Framework tests into multiple machines/docker and execute in parallel (without need of master node).
21 
Brackets plugin 
Robot Framework plugin for Brackets.
20 editor
RFDoc 
Web based system for storing and searching Robot Framework library and resource file documentations.
14 
Mabot 
Tool for reporting manual tests in format compatible with Robot Framework outputs.
12 
TestDataTable 
Enables you to assign test data variable values from a single set of data to multiple scripts while allowing you to ensure each script has a unique data value.
7 
Ant task 
Ant task for running Robot Framework tests.
3 build
Test Assistant 
Control test processes and RPA tasks with your voice or with a text message sent directly to the assistant through leon-ai's UI..
2 
Xray Test Management 
Test management app for Jira that provides the ability to track coverage based on traditional manual test cases, exploratory testing and automation-related results. For automation, users can track detailed results from test scripts implemented with Robot Framework and link them to the respective requirements.
N/A 
Tesults Listener 
A listener that provides a codeless integration experience for test results reporting from Robot Framework into Tesults.
N/A 
SAGE Framework 
Multi-agent based extension to Robot Framework. Agent based systems make it possible to test distributed systems such as Service Oriented Architecture systems. SAGE Provides a library of Robot Framework keywords for creating and managing SAGE agent networks as well as collecting and reporting results from remote agents.
N/A 
Robot Tools 
Collection of supporting tools that can be used with Robot Framework.
N/A 
RobotFramework AIO (All in One) 
RobotFramework AIO combines test development and execution into a single, integrated environment with VSCodium, Robot Framework, and additional keyword libraries. With just three clicks, a fully pre-configured installation is ready, offering version control to ensure reproducible and predictable test results. This solution simplifies test case development and production testing through seamless integration and continuous updates.
N/A IDTE
Robot Framework Lexer 
Robot Framework syntax highlighting with Pygments. Link is to the lexer project itself, but the lexer is part of Pygments from version 1.6 onwards.
N/A editor
Fixml 
Tool for fixing Robot Framework output files that are broken.
N/A 
DbBot 
Tool for serializing Robot Framework execution results, i.e. output.xml files, into an SQLite database. It serves a good starting point to create your own reporting and analyzing tools.
N/A 
Debugger for Visual Studio Code 
A Visual Studio Code extension that lets you debug robot files with call stack, breakpoints, etc.
N/A editor
Intellisense for Visual Studio Code 
A Visual Studio Code extension that supports Robot Framework development.
N/A editor
Language Server for PyCharm 
PyCharm LSP plugin - syntax highlight, code completion, and other LSP features for PyCharm.
N/A editor
Robot Support for IntelliJ IDEA 
For IntelliJ IDEA-based editors by Valerio Angelini.
N/A editor
Robot Plugin for IntelliJ IDEA 
For IntelliJ IDEA-based editors by JIVE Software.
N/A editor
Gedit 
Syntax highlighting for Gedit.
N/A editor
RobotCode 
RobotFramework support for Visual Studio Code, including features like code completion, navigation, refactoring, usage analysis, debugging, test explorer, test execution and more!
N/A editor, vscode

Rebot 
Generate logs and reports based on XML outputs and for combining multiple outputs together.
tool
Remote 
Special library acting as a proxy between Robot Framework and libraries elsewhere. Actual libraries can be running on different machines and be implemented using any programming language supporting XML-RPC protocol.
library
Screenshot 
Provides keywords to capture screenshots of the desktop.
library
String 
Library for generating, modifying and verifying strings.
library
Telnet 
Makes it possible to connect to Telnet servers and execute commands on the opened connections.
library
Testdoc 
Generate high level HTML documentation based on Robot Framework test cases.
tool
Tidy 
Cleaning up and changing format of Robot Framework test data files.
tool
XML 
Library for generating, modifying and verifying XML files.
library
