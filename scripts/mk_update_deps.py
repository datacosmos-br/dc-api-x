#!/usr/bin/env python3
"""
Update dependencies script for DC-API-X project.

This script reads the pyproject.toml file and generates Poetry commands
to update dependencies based on the configured groups.

Usage:
    python scripts/update_deps.py

Author: Marlon Costa <marlon.costa@datacosmos.com.br>
Date: 2025-05-24
License: MIT
"""

import subprocess
import sys
import tomli
from pathlib import Path
from typing import Dict, List, Set, Any


def read_pyproject() -> Dict[str, Any]:
    """Read and parse pyproject.toml file."""
    try:
        pyproject_path = Path("pyproject.toml")
        return tomli.loads(pyproject_path.read_text())
    except (FileNotFoundError, tomli.TOMLDecodeError) as e:
        print(f"Error reading pyproject.toml: {e}", file=sys.stderr)
        sys.exit(1)


def get_dependencies_by_group(pyproject: Dict[str, Any]) -> Dict[str, Set[str]]:
    """Extract dependencies by group from pyproject data."""
    dependencies_by_group = {}

    # Get main dependencies
    if "dependencies" in pyproject.get("tool", {}).get("poetry", {}):
        dependencies_by_group["main"] = set(
            dep
            for dep in pyproject["tool"]["poetry"]["dependencies"]
            if dep != "python"
            and not isinstance(pyproject["tool"]["poetry"]["dependencies"][dep], dict)
            or not pyproject["tool"]["poetry"]["dependencies"][dep].get(
                "optional", False
            )
        )

    # Get group dependencies
    if "group" in pyproject.get("tool", {}).get("poetry", {}):
        for group, group_data in pyproject["tool"]["poetry"]["group"].items():
            if "dependencies" in group_data:
                dependencies_by_group[group] = set(group_data["dependencies"].keys())

    return dependencies_by_group


def update_dependencies() -> None:
    """Update dependencies using Poetry based on pyproject.toml."""
    pyproject = read_pyproject()
    dependencies_by_group = get_dependencies_by_group(pyproject)

    # Update Poetry itself
    print("→ Upgrading Poetry")
    subprocess.run(["pip", "install", "--upgrade", "poetry"], check=False)

    # Update dependencies by group
    for group, deps in dependencies_by_group.items():
        if deps:
            if group == "main":
                print(f"→ Updating main dependencies")
                cmd = ["poetry", "add"]
            else:
                print(f"→ Updating {group} dependencies")
                cmd = ["poetry", "add", "--group", group]

            # Add each dependency to the command
            deps_list = list(deps)

            # Execute the command with dependencies
            if deps_list:
                print(f"  Dependencies: {', '.join(deps_list)}")
                try:
                    full_cmd = cmd + deps_list
                    subprocess.run(full_cmd, check=True)
                    print(f"✓ {group} dependencies updated")
                except subprocess.CalledProcessError:
                    print(f"✗ Failed to update {group} dependencies", file=sys.stderr)

    # Update pre-commit hooks
    print("→ Updating pre-commit hooks")
    try:
        subprocess.run(["poetry", "run", "pre-commit", "autoupdate"], check=False)
        subprocess.run(["poetry", "run", "pre-commit", "install"], check=False)
        print("✓ Pre-commit hooks updated")
    except Exception as e:
        print(f"✗ Error updating pre-commit hooks: {e}", file=sys.stderr)

    # Check for outdated packages
    print("→ Checking for outdated packages")
    try:
        subprocess.run(["poetry", "show", "--outdated"], check=False)
    except Exception as e:
        print(f"✗ Error checking outdated packages: {e}", file=sys.stderr)

    print("✓ Dependency and tool update completed")


if __name__ == "__main__":
    update_dependencies()
