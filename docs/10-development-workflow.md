# Development Workflow

> *"Great software is always built by great teams following consistent processes."*
> This guide provides an overview of the development workflow for DCApiX,
> outlining processes, tools, and expectations for contributors.

---

## Navigation

| ⬅️ Previous | Current | Next ➡️ |
|-------------|---------|----------|
| [06 - Roadmap](06-roadmap.md) | **10 - Development Workflow** | [11 - Development: Contributing](11-development-contributing.md) |

---

## 1. Development Environment Setup

### 1.1 Prerequisites

Before starting development with DCApiX, ensure you have:

* Python 3.10 or higher
* Git
* pip and virtualenv or another environment manager
* A code editor with Python support (VS Code, PyCharm, etc.)

### 1.2 Initial Setup

```bash
# Clone the repository
git clone https://github.com/datacosmos/dc-api-x.git
cd dc-api-x

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[all,dev]"

# Install pre-commit hooks
pre-commit install
```

---

## 2. Development Workflow

The DCApiX development workflow follows these steps:

### 2.1 Branch Creation

```bash
# Ensure you're on the main branch with latest changes
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2.2 Development Process

1. **Make your changes** following the code style guidelines
2. **Write tests** for your changes (see [23 - Tech: Testing](23-tech-testing.md))
3. **Run linting and tests** locally before pushing
4. **Create small, focused commits** with clear messages

### 2.3 Code Quality Checks

DCApiX maintains high code quality standards through automated checks:

```bash
# Run automated formatting
make format

# Run linting checks
make lint

# Fix common linting issues automatically
make lint-fix

# Run tests with coverage
make test

# Run all checks
make check
```

See [12 - Development: Code Quality](12-development-code-quality.md) for detailed information on code quality tools.

---

## 3. Pull Request Process

### 3.1 Preparing Your Pull Request

Before submitting a pull request:

1. **Ensure your branch is up-to-date** with the main branch
2. **Run all checks** locally to verify your changes
3. **Update documentation** to reflect your changes
4. **Update CHANGELOG.md** following the Keep a Changelog format

### 3.2 Pull Request Submission

When submitting a pull request:

1. **Fill out the PR template** completely
2. **Link related issues** in the PR description
3. **Wait for CI checks** to complete before requesting review
4. **Address review comments** promptly

### 3.3 Review and Approval

Pull requests require:

* At least one keeper reviewer approval
* At least one domain reviewer approval
* All CI checks passing
* No unresolved conversations

---

## 4. Release Process

DCApiX follows semantic versioning (SemVer) for releases:

* **Major version** (X.0.0): Incompatible API changes
* **Minor version** (0.X.0): Backwards-compatible functionality
* **Patch version** (0.0.X): Backwards-compatible bug fixes

The release process involves:

1. **Version bump** in pyproject.toml
2. **CHANGELOG.md update** with all changes since the last release
3. **Git tag** with the version number
4. **Package publishing** to PyPI

---

## 5. Continuous Integration

DCApiX uses GitHub Actions for continuous integration:

* **Linting**: Code style and quality checks
* **Testing**: Unit, integration, and functional tests
* **Coverage**: Code coverage reporting
* **Documentation**: Documentation building and publishing
* **Security**: Security vulnerability scanning

---

## Related Documentation

* [11 - Development: Contributing](11-development-contributing.md) - Contribution guidelines
* [12 - Development: Code Quality](12-development-code-quality.md) - Code quality standards
* [13 - Development: Plugin System](13-development-plugin-system.md) - Plugin development
* [20 - Tech: Overview](20-tech-overview.md) - Technology stack overview
* [23 - Tech: Testing](23-tech-testing.md) - Testing guidelines
