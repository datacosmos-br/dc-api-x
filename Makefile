###############################################################################
#  DCApiX Project Makefile
#  Author : Marlon Costa <marlon.costa@datacosmos.com.br>
#  Version: 1.1.0 – 2025-05-24
#  License: MIT
#
#  Change Log
#  | Date       | Version | Author    | Description                        |
#  |------------|---------|-----------|------------------------------------|
#  | 2025-05-24 | 1.1.0   | M. Costa  | Refactor – removed redundancies    |
###############################################################################

# ───────────────────────────[ Paths ]─────────────────────────────────────────
WORKSPACE_ROOT ?= $(shell git \
						-C "$(CURDIR)" \
						rev-parse \
						--show-toplevel \
						2>/dev/null \
							|| echo "$(CURDIR)")
PROJECT_ROOT   := $(CURDIR)
PROJECT_NAME   := $(notdir $(PROJECT_ROOT))
PACKAGE_NAME   := dc_api_x

# ───────────────────────────[ Colours & Helpers ]─────────────────────────────
ifneq ($(shell tput colors 2>/dev/null),)
	C_RESET  := $(shell tput sgr0)
	C_BLUE   := $(shell tput setaf 4)
	C_GREEN  := $(shell tput setaf 2)
	C_YELLOW := $(shell tput setaf 3)
	C_RED    := $(shell tput setaf 1)
else
	C_RESET  :=
	C_BLUE   :=
	C_GREEN  :=
	C_YELLOW :=
	C_RED    :=
endif

define MSG
	@printf '$(C_BLUE)→ %s$(C_RESET)\n'  "$(1)"
endef

define OK
	@printf '$(C_GREEN)✓ %s$(C_RESET)\n' "$(1)"
endef

define WARN
	@printf '$(C_YELLOW)• %s$(C_RESET)\n' "$(1)"
endef

define ERR
	@printf '$(C_RED)✗ %s$(C_RESET)\n'   "$(1)"
endef

# ───────────────────────────[ Default target ]───────────────────────────────
default: help
.DEFAULT_GOAL := default

# ───────────────────────────[ Public targets ]────────────────────────────────
.PHONY: \
	default help \
	install install-dev update build clean \
	test test-cov test-html test-parallel test-profile \
	lint lint-stats lint-report format lint-fix security auto-lint fix \
	workspace root-lint root-format root-test \
	monkeytype-run monkeytype-list monkeytype-apply monkeytype-apply-all \
	monkeytype-stub monkeytype-mypy monkeytype-cycle

# === Installation & Updates ==================================================
POETRY := poetry
PIP := pip

install: ## Install project dependencies (poetry install)
	$(call MSG,"Installing dependencies")
	$(POETRY) install
	$(call OK,"Dependencies installed")

install-dev: ## Install dependencies + dev extras
	$(call MSG,"Installing development dependencies")
	$(POETRY) install --with dev
	$(call OK,"Development dependencies installed")

update: ## Upgrade Poetry, dev tools and project dependencies
	$(call MSG,"Upgrading Poetry")
	$(PIP) install --upgrade poetry || { \
		$(call ERR,"Poetry upgrade failed but continuing..."); \
		true; \
	}
	
	$(call MSG,"Updating development dependencies")
	$(POETRY) add --group dev autoflake bandit black isort mypy pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist ruff types-requests pre-commit || { \
		$(call ERR,"Development dependencies update failed but continuing..."); \
		true; \
	}
	
	$(call MSG,"Updating documentation dependencies")
	$(POETRY) add --group docs sphinx-copybutton sphinx-rtd-theme myst-parser || { \
		$(call ERR,"Documentation dependencies update failed but continuing..."); \
		true; \
	}
	
	$(call MSG,"Updating all dependencies")
	$(POETRY) update --no-cache || { \
		$(call ERR,"Dependency update failed but continuing..."); \
		true; \
	}
	
	$(call MSG,"Updating pre-commit hooks")
	$(POETRY) run pre-commit autoupdate || true
	$(POETRY) run pre-commit install || true
	
	$(call MSG,"Checking for outdated packages")
	$(POETRY) show --outdated || true
	
	$(call OK,"Dependency and tool update completed")

# === Build & Clean ===========================================================
build: ## Build sdist and wheel into ./dist
	$(call MSG,"Building package")
	$(POETRY) build
	$(call OK,"Package available in ./dist")

clean: ## Remove build artefacts and caches
	$(call MSG,"Removing artefacts")
	@find . \( -name "__pycache__" \
		-o -name "*.py[cod]" \
		-o -name ".pytest_cache" \
		-o -name ".mypy_cache" \
		-o -name ".ruff_cache" \
		-o -name ".coverage" \
		-o -name "htmlcov" \
		-o -name "dist" \
		-o -name "build" \
		-o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null
	$(call OK,"Cleanup done")

# === Tests ===================================================================
define _pytest
	PYTHONPATH=. pytest $(1)
endef

test: ## Run unit tests
	$(call MSG,"Running unit tests")
	$(call _pytest,-xvs tests/unit)
	$(call OK,"Tests finished")

test-cov: ## Run tests with coverage (HTML under reports/coverage)
	$(call MSG,"Running tests with coverage")
	$(call _pytest,--cov=src/$(PACKAGE_NAME) --cov-report=term --cov-report=html:reports/coverage)
	$(call OK,"Coverage report generated at reports/coverage/index.html")

test-html: ## Run tests with HTML report
	$(call MSG,"Running tests with HTML report")
	$(call _pytest,--html=reports/pytest/report.html --self-contained-html tests/unit)
	$(call OK,"HTML report generated")

test-parallel: ## Run tests in parallel (pytest-xdist)
	$(call MSG,"Running tests in parallel")
	$(call _pytest,-n auto tests/unit)
	$(call OK,"Parallel tests finished")

test-profile: ## Run tests with profiling (pytest-profiler)
	$(call MSG,"Running tests with profiling")
	$(call _pytest,--profile-svg --profile tests/unit)
	$(call OK,"Profiling report generated")

# === Code Quality ============================================================
lint: ## Run ruff & mypy
	$(call MSG,"Linting with ruff and mypy")
	-$(POETRY) run ruff check src tests || $(call WARN,"Ruff reported issues")
	-$(POETRY) run mypy src tests      || $(call WARN,"Mypy reported issues")
	$(call OK,"Lint finished")

lint-stats: ## Show ruff statistics
	$(call MSG,"Generating lint statistics")
	-$(POETRY) run ruff check . --select="E,F,I,W,UP" --ignore="UP007" --statistics
	$(call OK,"Statistics printed above")

lint-report: ## Output ruff report to JSON (reports/lint/)
	$(call MSG,"Generating lint report")
	@mkdir -p reports/lint
	-$(POETRY) run ruff check --output-format=json --output-file=reports/lint/ruff_report.json .
	$(call OK,"Report saved to reports/lint/")

format: ## Apply black & isort
	$(call MSG,"Formatting code (black + isort)")
	$(POETRY) run black .
	$(POETRY) run isort .
	$(call OK,"Formatting complete")

lint-fix: ## Auto-fix with ruff –fix + autoflake + black + isort
	$(call MSG,"Auto-fixing lint issues")
	-$(POETRY) run ruff check --fix . || true
	$(POETRY) run autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r src tests
	$(POETRY) run isort .
	$(POETRY) run black .
	$(call OK,"Auto-fix done (manual review may still be required)")

security: ## Static security scan (bandit)
	$(call MSG,"Running Bandit security scan")
	-$(POETRY) run bandit -r src -x tests || $(call WARN,"Bandit reported issues")
	$(call OK,"Security scan finished")

auto-lint: ## Run scripts/auto_lint_fix.sh
	$(call MSG,"Executing auto_lint_fix.sh")
	chmod +x scripts/auto_lint_fix.sh
	./scripts/auto_lint_fix.sh
	$(call OK,"Auto-lint cycle complete")

fix: lint-fix format security ## One-shot code clean-up
	$(call OK,"Full fix complete")

# === Workspace integration ===================================================
workspace: ## Run "make CMD=target" in workspace root
ifndef CMD
	$(error CMD variable not set; usage: make workspace CMD=<target>)
endif
	$(call MSG,"Running '$(CMD)' from workspace root")
	@cd $(WORKSPACE_ROOT) && make $(CMD) PROJECT=$(PROJECT_NAME)

root-lint: ## Use root lint tools
	@cd $(WORKSPACE_ROOT) && make -f Makefile.lint lint-fix-all PROJECT=$(PROJECT_NAME)

root-format: ## Use root formatting tools
	@cd $(WORKSPACE_ROOT) && make -f Makefile.lint lint-fix-black PROJECT=$(PROJECT_NAME)

root-test: ## Run tests via workspace root
	@cd $(WORKSPACE_ROOT) && make test PROJECT=$(PROJECT_NAME)

# === MonkeyType workflow =====================================================
monkeytype-run: ## Run tests collecting runtime types
	$(call MSG,"Running tests with MonkeyType tracing")
	python scripts/monkeytype_runner.py run $(if $(TEST_PATH),--test-path $(TEST_PATH),)
	$(call OK,"MonkeyType run complete")

monkeytype-list: ## List modules containing collected types
	$(call MSG,"Listing collected MonkeyType modules")
	python scripts/monkeytype_runner.py list
	$(call OK,"Module list printed")

monkeytype-apply: ## Apply types to MODULE=<pkg.mod>
ifndef MODULE
	$(error MODULE not set; usage: make monkeytype-apply MODULE=<pkg.mod>)
endif
	$(call MSG,"Applying types to $(MODULE)")
	python scripts/monkeytype_runner.py apply --module $(MODULE)
	$(call OK,"Types applied")

monkeytype-apply-all: ## Apply types to all collected modules
	$(call MSG,"Applying types to all modules")
	python scripts/monkeytype_runner.py apply --all
	$(call OK,"Types applied to all modules")

monkeytype-stub: ## Generate .pyi stub for MODULE=<pkg.mod>
ifndef MODULE
	$(error MODULE not set; usage: make monkeytype-stub MODULE=<pkg.mod>)
endif
	$(call MSG,"Generating stub for $(MODULE)")
	python scripts/mk_monkeytype_runner.py generate-stub --module $(MODULE)
	$(call OK,"Stub generated")

monkeytype-mypy: ## Run mypy (optionally MODULE=<pkg.mod>)
ifndef MODULE
	$(call MSG,"Running mypy on entire package")
	python -m mypy src/$(PACKAGE_NAME)/
else
	$(call MSG,"Running mypy on $(MODULE)")
	module_path=$$(echo $(MODULE) | sed 's/$(PACKAGE_NAME)\.//' | tr '.' '/')
	python -m mypy src/$(PACKAGE_NAME)/$${module_path}.py
endif
	$(call OK,"mypy check done")

monkeytype-cycle: ## Full MonkeyType cycle: run→list→apply-all→mypy
	$(call MSG,"Starting full MonkeyType cycle")
	@$(MAKE) monkeytype-run
	@$(MAKE) monkeytype-list
	@$(MAKE) monkeytype-apply-all
	@$(MAKE) monkeytype-mypy
	$(call OK,"MonkeyType cycle finished")

# === Help ====================================================================
help: ## Show this help message
	@printf "\n$(C_BLUE)Available targets for $(PROJECT_NAME):$(C_RESET)\n\n"
	@grep -E '^[a-zA-Z_\-]+:.*?## ' $(MAKEFILE_LIST) | \
	  sed -E 's/^([a-zA-Z_\-]+):.*?## (.*)/  \1\t\2/' | \
	  expand -t25 | sort
