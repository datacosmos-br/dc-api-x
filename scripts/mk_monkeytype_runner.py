#!/usr/bin/env python3
"""
MonkeyType Runner for DC-API-X

Script to collect runtime type information during test execution,
apply these type annotations to modules, and generate stubs for integration with mypy and pydantic.

Usage:
    python monkeytype_runner.py run [--test-path <test_path>]
    python monkeytype_runner.py list
    python monkeytype_runner.py apply --module <module_path>
    python monkeytype_runner.py apply --all
    python monkeytype_runner.py stub --module <module_path>

Examples:
    # Run all project tests with MonkeyType
    python monkeytype_runner.py run

    # Run a specific test with MonkeyType
    python monkeytype_runner.py run --test-path tests/test_config.py

    # List modules with collected type information
    python monkeytype_runner.py list

    # Apply types to the config module
    python monkeytype_runner.py apply --module dc_api_x.config

    # Apply types to all modules with collected information
    python monkeytype_runner.py apply --all

    # Generate stub for the models module
    python monkeytype_runner.py stub --module dc_api_x.models
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class MonkeyTypeRunner:
    """Runner for MonkeyType in the DC-API-X project."""

    def __init__(self) -> None:
        """Initialize the runner with project paths."""
        # Find the project root
        self.project_root = self._find_project_root()

        # Important paths
        self.venv_dir = Path(
            os.environ.get("VIRTUAL_ENV", self.project_root.parent / ".venv"),
        )
        self.python_exe = self.venv_dir / "bin" / "python"
        self.monkeytype_exe = self.venv_dir / "bin" / "monkeytype"

        # Directory for MonkeyType database
        self.db_dir = self.project_root / ".monkeytype"
        self.db_dir.mkdir(exist_ok=True)

        # SQLite database file
        self.db_file = self.db_dir / "dc_api_x.sqlite"
        self.db_file_absolute = str(self.db_file.absolute())

        # Configure environment to use the database
        os.environ["MONKEYTYPE_DB"] = f"sqlite:///{self.db_file_absolute}"

        # Source code folder
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"

        # Check if directories exist
        if not self.src_dir.exists():
            raise FileNotFoundError(
                f"Source code directory not found: {self.src_dir}",
            )
        if not self.tests_dir.exists():
            raise FileNotFoundError(
                f"Tests directory not found: {self.tests_dir}",
            )

    def _find_project_root(self) -> Path:
        """Find the root of the DC-API-X project."""
        # Get current directory
        current_dir = Path.cwd()

        # Navigate through parent directories looking for pyproject.toml
        dir_to_check = current_dir
        while dir_to_check != dir_to_check.parent:  # Until reaching system root
            if (dir_to_check / "pyproject.toml").exists():
                # Check if it's the dc-api-x project
                with open(dir_to_check / "pyproject.toml") as f:
                    content = f.read()
                    if 'name = "dc-api-x"' in content:
                        return dir_to_check
            dir_to_check = dir_to_check.parent

        # If not found, try current directory or script directory
        script_dir = Path(__file__).parent
        for check_dir in [current_dir, script_dir.parent]:
            if (check_dir / "pyproject.toml").exists():
                with open(check_dir / "pyproject.toml") as f:
                    content = f.read()
                    if 'name = "dc-api-x"' in content:
                        return check_dir

        # If still not found, assume we're in the dc-api-x directory
        return Path("dc-api-x").absolute()

    def run_tests_with_monkeytype(self, test_path: Optional[str] = None) -> int:
        """
        Run tests with MonkeyType instrumentation to collect types.

        Args:
            test_path: Path to the specific test to run (optional)

        Returns:
            Return code of the command
        """
        # Change to the project root directory
        os.chdir(self.project_root)

        # Build the monkeytype run -m pytest command
        cmd = [
            "monkeytype",
            "run",
            "-m",
            "pytest",
        ]

        # Add the test path, if specified
        if test_path:
            test_path_full = self.project_root / test_path
            if not test_path_full.exists():
                print(f"Error: Test path {test_path_full} not found")
                return 1
            cmd.append(str(test_path))

        print("Running tests with MonkeyType in DC-API-X")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(
                "\nMonkeyType successfully collected types during test execution.",
            )

            # List available modules
            print("\nModules with collected type information:")
            subprocess.run(["monkeytype", "list-modules"], check=False)

            print("\nTo apply collected types to a specific module:")
            print(f"  python {Path(__file__).name} apply --module <module_path>")

            print("\nTo apply collected types to all modules at once:")
            print(f"  python {Path(__file__).name} apply --all")

            # Suggestion to apply types to the configuration module
            print("\nExample of applying types:")
            print(f"  python {Path(__file__).name} apply --module dc_api_x.config")
        else:
            print(
                "\nSome tests failed, but types may have been collected anyway.",
            )
            print("Check available modules with:")
            print(f"  python {Path(__file__).name} list")

        return result.returncode

    def list_modules(self) -> int:
        """
        List modules with collected type information.

        Returns:
            Return code of the command
        """
        # Check if the database exists (optional, MonkeyType already does this)
        # if not self.db_file.exists():
        #    print(f"Error: Database file not found: {self.db_file}")
        #    print(f"Run tests first: python {Path(__file__).name} run")
        #    return 1

        # Use the monkeytype list-modules command directly
        cmd = ["monkeytype", "list-modules"]

        print("Listing modules with collected type information:")
        result = subprocess.run(cmd, check=False)

        # If listing was successful, display instructions for the user
        if result.returncode == 0:
            print("\nTo apply types to a specific module:")
            print(f"  python {Path(__file__).name} apply --module <module_name>")

            print("\nTo apply types to all modules at once:")
            print(f"  python {Path(__file__).name} apply --all")

            print("\nExample:")
            print(f"  python {Path(__file__).name} apply --module dc_api_x.config")

        return result.returncode

    def apply_types(self, module_path: str = None, apply_all: bool = False) -> int:
        """
        Apply collected types to a module or all available modules.

        Args:
            module_path: Path of the module to apply types to (optional if apply_all=True)
            apply_all: If True, apply types to all available modules

        Returns:
            Return code of the command
        """
        if apply_all:
            # List all modules with type information
            cmd_list = ["monkeytype", "list-modules"]
            print("Listing modules with type information...")
            result = subprocess.run(
                cmd_list,
                check=False,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print("Error listing modules with type information")
                return result.returncode

            # Extract modules from output
            modules = [
                m.strip() for m in result.stdout.strip().split("\n") if m.strip()
            ]

            # Filter only dc_api_x modules
            dc_modules = [m for m in modules if m.startswith("dc_api_x.")]

            if not dc_modules:
                print("No dc_api_x modules found with type information")
                return 0

            print(f"Found {len(dc_modules)} modules to apply types to:")
            for m in dc_modules:
                print(f"  - {m}")

            # Apply types to each module
            success_count = 0
            failed_modules = []

            for module in dc_modules:
                print(f"\n{'='*40}")
                print(f"Applying types to module {module}...")
                result = self.apply_types(module)

                if result == 0:
                    success_count += 1
                else:
                    failed_modules.append(module)

            # Summary
            print(f"\n{'='*60}")
            print(
                f"Summary: Type application completed for {success_count}/{len(dc_modules)} modules",
            )

            if failed_modules:
                print("Failed to apply types to the following modules:")
                for m in failed_modules:
                    print(f"  - {m}")
                return 1

            return 0

        # Apply types to a single module
        if not module_path:
            print("Error: Module path not specified")
            return 1

        # Check if the module exists (for safety)
        module_parts = module_path.split(".")
        if module_parts[0] == "dc_api_x":
            # Fix the path to point to the module inside src/dc_api_x/
            module_file = self.src_dir / "dc_api_x" / "/".join(module_parts[1:])
            module_file = module_file.with_suffix(".py")
            if not module_file.exists():
                print(f"Error: Module file not found: {module_file}")
                return 1

        # Apply types using the monkeytype apply command directly
        cmd = [
            "monkeytype",
            "apply",
            module_path,
        ]

        print(f"Applying types to module {module_path}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(f"\nTypes successfully applied to module {module_path}")
            print(
                "Don't forget to check the changes and run mypy to validate the types.",
            )
            print("\nTo check type compliance:")
            print(
                f"  cd {self.project_root} && python -m mypy src/{module_path.replace('.', '/')}.py",
            )

            # Guide for Pydantic models
            if "models" in module_path or "schema" in module_path:
                print("\nTip for Pydantic integration:")
                print(
                    "  For model classes, you can convert type annotations to Pydantic fields:",
                )
                print("  Instead of:")
                print("    def __init__(self, name: str, age: Optional[int] = None):")
                print("  Use:")
                print("    class User(BaseModel):")
                print("        name: str")
                print("        age: Optional[int] = None")

        return result.returncode

    def generate_stub(self, module_path: str) -> int:
        """
        Generate stub with collected types.

        Args:
            module_path: Path of the module to generate the stub for

        Returns:
            Return code of the command
        """
        # Check if the module exists (for safety)
        module_parts = module_path.split(".")
        if module_parts[0] == "dc_api_x":
            # Fix the path to point to the module inside src/dc_api_x/
            module_file = self.src_dir / "dc_api_x" / "/".join(module_parts[1:])
            module_file = module_file.with_suffix(".py")
            if not module_file.exists():
                print(f"Error: Module file not found: {module_file}")
                return 1

        # Generate the stub using the monkeytype stub command directly
        cmd = [
            "monkeytype",
            "stub",
            module_path,
        ]

        print(f"Generating type stub for module {module_path}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(f"\nType stub successfully generated for {module_path}")
            print(
                "Review the generated stub and apply it manually to your code if needed.",
            )

            # Tips for Pydantic integration
            if "models" in module_path or "schema" in module_path:
                print("\nTip for Pydantic integration:")
                print(
                    "  For model classes, convert type annotations to Pydantic fields:",
                )
                print("  Example:")
                print("    # Stub generated by MonkeyType")
                print("    class User:")
                print("        name: str")
                print("        email: str")
                print("        age: Optional[int]")
                print("    ")
                print("    # Converted to Pydantic")
                print("    class User(BaseModel):")
                print("        name: str")
                print("        email: EmailStr  # With additional validation")
                print("        age: Optional[int] = None")

        return result.returncode


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DC-API-X MonkeyType Runner - Tool for collecting and applying types.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run tests with MonkeyType tracing",
    )
    run_parser.add_argument(
        "--test-path",
        help="Specific test path within the project",
    )

    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="List modules with collected types",
    )

    # apply command
    apply_parser = subparsers.add_parser(
        "apply",
        help="Apply collected types to a module",
    )
    apply_module_group = apply_parser.add_mutually_exclusive_group(required=True)
    apply_module_group.add_argument(
        "--module",
        help="Path of the module to apply types to",
    )
    apply_module_group.add_argument(
        "--all",
        action="store_true",
        help="Apply types to all available modules",
    )

    # stub command
    stub_parser = subparsers.add_parser(
        "stub",
        help="Generate module stub with collected types",
    )
    stub_parser.add_argument(
        "--module",
        required=True,
        help="Path of the module to generate the stub for",
    )

    return parser.parse_args()


def main() -> int:
    """Main runner function."""
    args = parse_args()

    try:
        runner = MonkeyTypeRunner()

        if args.command == "run":
            return runner.run_tests_with_monkeytype(args.test_path)
        if args.command == "list":
            return runner.list_modules()
        if args.command == "apply":
            if args.all:
                return runner.apply_types(apply_all=True)
            return runner.apply_types(args.module)
        if args.command == "stub":
            return runner.generate_stub(args.module)
        print(f"Unknown command: {args.command}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
