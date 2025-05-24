# Changelog

All notable changes to the DCApiX project will be documented in this file.

## Navigation

* [README](README.md)
* [License](LICENSE)
* [Security Policy](SECURITY.md)
* [Documentation](docs/01-overview.md)

---

## [Unreleased] - 2025-05-24

### Fixed

* Improved dependency management in Makefile - marlon-costa-dc
  * Fixed `update` target issues with commented lines in package lists
  * Implemented robust error handling with color-coded messages
  * Separated dependency groups (dev and docs) using `--group` flag

### Added

* New utility scripts - marlon-costa-dc
  * `mk_update_deps.py`: Automated dependency management from pyproject.toml
  * `mk_monkeytype_runner.py`: Enhanced type annotation with batch processing
* Documentation reorganization - marlon-costa-dc
  * Restructured all documentation files for better organization and navigation
  * Improved cross-linking between related documentation topics
  * Enhanced documentation map in README and overview

### Changed

* Internationalization improvements - marlon-costa-dc
  * Translated MonkeyType documentation to English
  * Improved formatting and code examples
  * Enhanced error messages with better visibility

## [0.2.0] - 2025-05-23

### Features

* Enhanced testing infrastructure - marlon-costa-dc
  * Added MonkeyType integration for runtime type collection
  * Implemented global pytest configuration with fixtures and logging
  * Added coverage reporting options and Makefile targets

### Bug Fixes

* Comprehensive linting and type fixes - marlon-costa-dc
  * Fixed API client issues (import errors, type annotations, parameter handling)
  * Resolved code duplication in AsyncDatabase classes
  * Addressed exception handling patterns throughout the codebase
  * Fixed shadowing of built-in names (renamed TimeoutError to ApiTimeoutError)

* Code quality improvements - marlon-costa-dc
  * Replaced global state with class-based management
  * Refactored methods with excessive parameters using dataclasses
  * Corrected Pydantic model usage in schema generation
  * Fixed protocol class implementations for better type safety

### Documentation

* Documentation overhaul - marlon-costa-dc
  * Updated README with clearer development tool instructions
  * Enhanced MonkeyType guide with Pydantic integration examples
  * Improved SECURITY documentation with structured reporting procedures
  * Standardized all project files to English
  * Added GitHub configuration documentation for contributors

### CI/CD

* GitHub Actions modernization - marlon-costa-dc
  * Upgraded GitHub Action dependencies to latest versions
  * Enhanced security reporting with GitHub Advanced Security
  * Consolidated security scanning workflows
  * Implemented comprehensive CodeQL configuration
  * Updated team structure in CODEOWNERS

## [0.1.0] - 2025-05-23

### Features

* Initial release with multi-protocol support - marlon-costa-dc
  * Implemented base client for HTTP, database, and LDAP protocols
  * Created extensible plugin architecture with lifecycle management
  * Integrated Pydantic for validation and configuration
  * Implemented CLI interface with Typer and Click

### Documentation

* Initial documentation - marlon-costa-dc
  * Created comprehensive README with installation and usage instructions
  * Added API documentation and examples for all supported protocols

### CI/CD

* Initial CI/CD setup - marlon-costa-dc
  * Configured GitHub Actions for testing, linting, and releases
  * Set up security scanning with CodeQL
  * Implemented Dependabot for automated dependency management

---

This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
