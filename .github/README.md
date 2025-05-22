# GitHub Configuration

This directory contains configuration files for GitHub features used in this repository.

## Structure

- **CODEOWNERS**: Defines ownership rules for repository content
- **PULL_REQUEST_TEMPLATE.md**: Template used when creating new pull requests
- **dependabot.yml**: Configuration for Dependabot automated dependency updates
- **labeler.yml**: Configuration for automatic PR labeling based on file paths

### Directories

- **ISSUE_TEMPLATE/**: Templates used when creating new issues
  - `bug_report.md`: Template for reporting bugs
  - `feature_request.md`: Template for requesting new features
- **workflows/**: GitHub Actions workflow definitions
  - `python-workflow.yml`: Main CI/CD pipeline for linting, testing, and checking dependencies
  - `security-scans.yml`: Comprehensive security scanning tools (CodeQL, Bandit, OSV, Pyre)
  - `stale.yml`: Automatically manages stale issues and pull requests
  - `greetings.yml`: Welcomes first-time contributors
  - `label.yml`: Applies labels to PRs based on the paths of modified files
  - `summary.yml`: Creates AI-generated summaries for new issues
  - `release.yml`: Automates the release process when a version tag is pushed
  - `docs.yml`: Builds and deploys documentation to GitHub Pages

## Workflows

### Python CI/CD (`python-workflow.yml`)

Runs on push to main, PRs to main, and weekly scheduled runs:

1. **Lint**: Checks code style with ruff, black, and type checking with mypy
2. **Test**: Runs pytest with coverage reports across multiple Python versions
3. **Security**: Scans code for security vulnerabilities with bandit
4. **Dependency Review**: Reviews dependencies in PRs for vulnerabilities

### Security Scans (`security-scans.yml`)

Runs on push to main, PRs to main, and weekly:

1. **CodeQL**: Advanced static analysis for security vulnerabilities
2. **Bandit**: Python-specific security linter
3. **OSV Scanner**: Checks dependencies against vulnerability database
4. **Pyre**: Static type checker for Python

### Stale Management (`stale.yml`)

Runs daily to mark and close stale issues and PRs:

- Issues/PRs inactive for 30 days are marked as stale
- If no activity after being marked stale for 14 days, they are closed
- Important labels exempt issues/PRs from being marked stale

### First Interaction (`greetings.yml`)

Automatically responds to first-time contributors when they:

- Open their first issue
- Submit their first pull request

### Auto Labeler (`label.yml`)

Labels PRs based on the files that are changed, using rules from `labeler.yml`.

### Issue Summarization (`summary.yml`)

Uses AI to generate a concise summary of new issues and posts it as a comment.

### Release Automation (`release.yml`)

Triggered when a version tag (v*.*.*)  is pushed:

1. **Build**: Builds Python package artifacts
2. **Publish**: 
   - Creates a GitHub Release with assets
   - Publishes to PyPI (stable versions) or TestPyPI (pre-releases)
   - Creates a GitHub Discussion announcing the release

### Documentation (`docs.yml`)

Builds and deploys documentation:

1. **Build**: Builds MkDocs documentation on changes to docs files
2. **Deploy**: Deploys to GitHub Pages
3. **Manual Trigger**: Can be manually triggered via workflow_dispatch 
