###############################################################################
#  DCApiX Project Makefile
#  Simple project-specific targets that integrate with root workspace
###############################################################################

# ───────────────═[ Basic Configuration ]═─────────────────────────────────────
WORKSPACE_ROOT ?= $(shell git -C "$(CURDIR)" rev-parse --show-toplevel 2>/dev/null || echo "$(CURDIR)")
PROJECT_ROOT   := $(CURDIR)
PROJECT_NAME   := $(notdir $(PROJECT_ROOT))
PACKAGE_NAME   := dc_api_x

# ───────────────═[ Commands ]═───────────────────────────────────────────────
POETRY     := poetry

# ───────────────═[ Color Detection ]═─────────────────────────────────────────
# Detect if terminal supports colors
ifneq ($(TERM),)
  ifneq ($(TERM),dumb)
    COLORTERM ?= yes
  endif
endif

# Force colors on/off with make COLORS=yes/no
ifdef COLORS
  ifeq ($(COLORS),yes)
    COLORTERM = yes
  else ifeq ($(COLORS),no)
    COLORTERM = no
  endif
endif

# Disable colors in CI environments or piped output
ifndef COLORTERM
  ifneq ($(CI),)
    COLORTERM = no
  else
    SHELL_PIPE := $(shell ps -o comm= -p $$$$ | grep -q 'pipe' && echo 1 || echo 0)
    ifeq ($(SHELL_PIPE),1)
      COLORTERM = no
    else
      COLORTERM = yes
    endif
  endif
endif

# ───────────────═[ Colors & Formatting ]═─────────────────────────────────────
ifeq ($(COLORTERM),yes)
  # Text colors
  BLACK      := \033[0;30m
  RED        := \033[0;31m
  GREEN      := \033[0;32m
  YELLOW     := \033[0;33m
  BLUE       := \033[0;34m
  MAGENTA    := \033[0;35m
  CYAN       := \033[0;36m
  WHITE      := \033[0;37m

  # Bold text colors
  BBLACK     := \033[1;30m
  BRED       := \033[1;31m
  BGREEN     := \033[1;32m
  BYELLOW    := \033[1;33m
  BBLUE      := \033[1;34m
  BMAGENTA   := \033[1;35m
  BCYAN      := \033[1;36m
  BWHITE     := \033[1;37m

  # Background colors
  BG_BLACK   := \033[40m
  BG_RED     := \033[41m
  BG_GREEN   := \033[42m
  BG_YELLOW  := \033[43m
  BG_BLUE    := \033[44m
  BG_MAGENTA := \033[45m
  BG_CYAN    := \033[46m
  BG_WHITE   := \033[47m

  # Text styles
  BOLD       := \033[1m
  UNDERLINE  := \033[4m
  REVERSED   := \033[7m

  # Reset
  NC         := \033[0m
else
  # No colors if not supported
  BLACK      :=
  RED        :=
  GREEN      :=
  YELLOW     :=
  BLUE       :=
  MAGENTA    :=
  CYAN       :=
  WHITE      :=
  BBLACK     :=
  BRED       :=
  BGREEN     :=
  BYELLOW    :=
  BBLUE      :=
  BMAGENTA   :=
  BCYAN      :=
  BWHITE     :=
  BG_BLACK   :=
  BG_RED     :=
  BG_GREEN   :=
  BG_YELLOW  :=
  BG_BLUE    :=
  BG_MAGENTA :=
  BG_CYAN    :=
  BG_WHITE   :=
  BOLD       :=
  UNDERLINE  :=
  REVERSED   :=
  NC         :=
endif

# Symbols (always available regardless of color support)
CHECK      := ✓
CROSS      := ✗
ARROW      := →
BULLET     := •

# ───────────────═[ Helper Functions ]═────────────────────────────────────────
define print_header
	@printf "$(BBLUE)╔═══════════════════════════════════════════════════════════════════╗$(NC)\n"
	@printf "$(BBLUE)║ $(BWHITE)$(1)$(BBLUE) ║$(NC)\n"
	@printf "$(BBLUE)╚═══════════════════════════════════════════════════════════════════╝$(NC)\n"
endef

define print_step
	@printf "$(BGREEN)$(ARROW) $(1)$(NC)\n"
endef

define print_substep
	@printf "$(CYAN)  $(BULLET) $(1)$(NC)\n"
endef

define print_success
	@printf "$(GREEN)  $(CHECK) $(1)$(NC)\n"
endef

define print_warning
	@printf "$(YELLOW)  $(BULLET) $(1)$(NC)\n"
endef

define print_error
	@printf "$(RED)  $(CROSS) $(1)$(NC)\n"
endef

# ───────────────═[ Targets ]═─────────────────────────────────────────────────
.DEFAULT_GOAL := help

## Project-specific commands
## ------------------------

## install: Installs project dependencies
install:
	@echo "$(BGREEN)$(ARROW) Installing dependencies for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@$(POETRY) install

## install-dev: Installs development dependencies
install-dev:
	@echo "$(BGREEN)$(ARROW) Installing development dependencies for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@$(POETRY) install --with dev

## update: Updates project dependencies and tools
update:
	@echo "$(BGREEN)$(ARROW) Atualizando Poetry para a versão mais recente$(BGREEN)$(NC)"
	@pip install --upgrade poetry
	
	@echo "$(BGREEN)$(ARROW) Instalando/atualizando ferramentas de desenvolvimento$(BGREEN)$(NC)"
	@$(POETRY) add --group dev black ruff isort mypy autoflake bandit pre-commit pytest pytest-cov pytest-mock pytest-asyncio pytest-xdist types-requests
	
	@echo "$(BGREEN)$(ARROW) Instalando/atualizando ferramentas de documentação$(BGREEN)$(NC)"
	@$(POETRY) add --group docs sphinx-rtd-theme sphinx-autodoc-typehints myst-parser sphinx-copybutton
	
	@echo "$(BGREEN)$(ARROW) Atualizando todas as dependências do projeto $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@$(POETRY) update --no-cache
	
	@echo "$(BGREEN)$(ARROW) Atualizando hooks do pre-commit$(BGREEN)$(NC)"
	@$(POETRY) run pre-commit autoupdate
	
	@echo "$(BGREEN)$(ARROW) Reinstalando hooks do pre-commit$(BGREEN)$(NC)"
	@$(POETRY) run pre-commit install
	
	@echo "$(BGREEN)$(ARROW) Verificando atualizações disponíveis$(BGREEN)$(NC)"
	@$(POETRY) show --outdated
	
	@echo "$(GREEN)  $(CHECK) Atualização de dependências e ferramentas completa$(NC)"

## build: Builds the project package
build:
	@echo "$(BGREEN)$(ARROW) Building package for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@$(POETRY) build

## clean: Cleans project artifacts
clean:
	@echo "$(BGREEN)$(ARROW) Cleaning artifacts from project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".coverage" -delete
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)  $(CHECK) Cleanup completed$(NC)"

## test: Runs project tests
test: install
	@echo "$(BGREEN)$(ARROW) Running tests for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@if [ -d "tests" ]; then \
		echo "$(CYAN)  $(BULLET) Unsetting PYTHONPATH to avoid conflicts$(NC)"; \
		PYTHONPATH="" $(POETRY) run pytest tests/ --mock-services; \
	else \
		echo "$(YELLOW)  $(BULLET) No tests directory found$(NC)"; \
	fi

## lint: Runs linting checks on the project
lint:
	@echo "$(BBLUE)╔═══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BBLUE)║ $(BWHITE)Linting Project $(PROJECT_NAME)$(BBLUE) ║$(NC)"
	@echo "$(BBLUE)╚═══════════════════════════════════════════════════════════════════╝$(NC)"
	
	@echo "$(CYAN)  $(BULLET) Running ruff check$(NC)"
	-@$(POETRY) run ruff check src/ tests/ || echo "$(YELLOW)  $(BULLET) Ruff found issues$(NC)"
	
	@echo "$(CYAN)  $(BULLET) Running mypy$(NC)"
	-@$(POETRY) run mypy src/ tests/ || echo "$(YELLOW)  $(BULLET) Mypy found issues$(NC)"
	
	@echo "$(GREEN)  $(CHECK) Linting completed - see above for any issues$(NC)"

## lint-wps: Runs only wemake-python-styleguide (disabled due to conflict)
lint-wps:
	@echo "$(BGREEN)$(ARROW) Wemake-python-styleguide check disabled due to plugin conflicts$(BGREEN)$(NC)"
	@echo "$(YELLOW)  $(BULLET) Please use 'ruff check' instead for linting$(NC)"
	@echo "$(GREEN)  $(CHECK) Check completed$(NC)"

## lint-stats: Generates lint statistics
lint-stats:
	@echo "$(BGREEN)$(ARROW) Generating lint statistics for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	-@$(POETRY) run ruff check . --select="E,F,I,W,UP" --ignore="UP007" --statistics
	@echo "$(GREEN)  $(CHECK) Statistics generated$(NC)"

## format: Formats project code
format:
	@echo "$(BBLUE)╔═══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BBLUE)║ $(BWHITE)Formatting Project $(PROJECT_NAME)$(BBLUE) ║$(NC)"
	@echo "$(BBLUE)╚═══════════════════════════════════════════════════════════════════╝$(NC)"
	
	@echo "$(CYAN)  $(BULLET) Running black$(NC)"
	@$(POETRY) run black .
	
	@echo "$(CYAN)  $(BULLET) Running isort$(NC)"
	@$(POETRY) run isort .
	
	@echo "$(GREEN)  $(CHECK) Formatting completed$(NC)"

## lint-fix: Automatically fixes lint issues
lint-fix:
	@echo "$(BBLUE)╔═══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BBLUE)║ $(BWHITE)Fixing Lint Issues in Project $(PROJECT_NAME)$(BBLUE) ║$(NC)"
	@echo "$(BBLUE)╚═══════════════════════════════════════════════════════════════════╝$(NC)"
	
	@echo "$(CYAN)  $(BULLET) Running ruff check --fix$(NC)"
	-@$(POETRY) run ruff check --fix . || echo "$(YELLOW)  $(BULLET) Ruff could not fix all issues$(NC)"
	
	@echo "$(CYAN)  $(BULLET) Running autoflake$(NC)"
	@$(POETRY) run autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r src/ tests/
	
	@echo "$(CYAN)  $(BULLET) Running isort$(NC)"
	@$(POETRY) run isort .
	
	@echo "$(CYAN)  $(BULLET) Running black$(NC)"
	@$(POETRY) run black .
	
	@echo "$(GREEN)  $(CHECK) Automatic fixes completed - some issues may require manual intervention$(NC)"

## security: Checks code for security issues
security:
	@echo "$(BGREEN)$(ARROW) Checking security for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	-@$(POETRY) run bandit -r src/ -x tests/ || echo "$(YELLOW)  $(BULLET) Security issues found$(NC)"
	@echo "$(GREEN)  $(CHECK) Security check completed$(NC)"

## auto-lint: Runs the automated lint-fix cycle
auto-lint:
	@echo "$(BGREEN)$(ARROW) Running automated lint-fix cycle for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@chmod +x scripts/auto_lint_fix.sh
	@./scripts/auto_lint_fix.sh
	@echo "$(GREEN)  $(CHECK) Automated lint cycle completed$(NC)"

## fix: Runs all fixing commands
fix: lint-fix format security
	@echo "$(GREEN)  $(CHECK) All automatic fixes and checks completed$(NC)"

## lint-report: Generates a detailed lint report
lint-report:
	@echo "$(BGREEN)$(ARROW) Generating lint report for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@mkdir -p reports/lint
	-@$(POETRY) run ruff check --output-format=json --output-file=reports/lint/ruff_report.json . || true
	@echo "$(GREEN)  $(CHECK) Lint reports generated in reports/lint/$(NC)"

## Integration with workspace
## ------------------------
## workspace: Executes command in workspace (CMD=command)
workspace:
	@echo "$(BGREEN)$(ARROW) Executing command in workspace: $(BWHITE)$(CMD)$(BGREEN)$(NC)"
	@cd $(WORKSPACE_ROOT) && make $(CMD) PROJECT=$(PROJECT_NAME)

## root-lint: Uses workspace lint tools
root-lint:
	@echo "$(BGREEN)$(ARROW) Using workspace lint tools for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@cd $(WORKSPACE_ROOT) && make -f Makefile.lint lint-fix-all PROJECT=$(PROJECT_NAME)

## root-format: Uses workspace formatting tools
root-format:
	@echo "$(BGREEN)$(ARROW) Using workspace formatting tools for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@cd $(WORKSPACE_ROOT) && make -f Makefile.lint lint-fix-black PROJECT=$(PROJECT_NAME)

## root-test: Runs tests via workspace
root-test:
	@echo "$(BGREEN)$(ARROW) Running tests via workspace for project $(BWHITE)$(PROJECT_NAME)$(BGREEN)$(NC)"
	@cd $(WORKSPACE_ROOT) && make test PROJECT=$(PROJECT_NAME)

## help: Display this help message
help:
	@echo "$(BBLUE)╔═══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BBLUE)║ $(BWHITE)DC-API-X Makefile Help$(BBLUE)                                        ║$(NC)"
	@echo "$(BBLUE)╚═══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BGREEN)Usage:$(NC)"
	@echo "  $(YELLOW)make$(NC) $(GREEN)<command>$(NC)"
	@echo ""
	@echo "$(BGREEN)Code Quality Commands:$(NC)"
	@echo "  $(CYAN)lint$(NC)            Runs linting checks on the project"
	@echo "  $(CYAN)format$(NC)          Formats code with black and isort"
	@echo "  $(CYAN)lint-fix$(NC)        Attempts to fix lint issues automatically"
	@echo "  $(CYAN)security$(NC)        Checks code for security issues"
	@echo "  $(CYAN)auto-lint$(NC)       Runs the automated lint-fix cycle until all issues are fixed"
	@echo "  $(CYAN)fix$(NC)             Runs all formatting and auto-fixes"
	@echo "  $(CYAN)lint-report$(NC)     Generates detailed lint report in reports/lint/"
	@echo "  $(CYAN)lint-stats$(NC)      Generates statistics about linting issues"
	@echo ""
	@echo "$(BGREEN)Development Commands:$(NC)"
	@echo "  $(CYAN)test$(NC)            Runs tests with pytest"
	@echo "  $(CYAN)test-cov$(NC)        Runs tests with coverage report"
	@echo "  $(CYAN)test-watch$(NC)      Runs tests continuously on file changes"
	@echo "  $(CYAN)docs$(NC)            Builds documentation"
	@echo "  $(CYAN)docs-serve$(NC)      Serves documentation locally"
	@echo "  $(CYAN)clean$(NC)           Removes build artifacts and cache files"
	@echo ""
	@echo "$(BGREEN)Build and Install Commands:$(NC)"
	@echo "  $(CYAN)build$(NC)           Builds the project package"
	@echo "  $(CYAN)install$(NC)         Installs the project package"
	@echo "  $(CYAN)install-dev$(NC)     Installs the project in development mode"
	@echo "  $(CYAN)update$(NC)          Updates dependencies and tools"
	@echo ""
	@echo "$(BGREEN)Example Usage:$(NC)"
	@echo "  $(YELLOW)make lint$(NC)          # Run linting checks"
	@echo "  $(YELLOW)make auto-lint$(NC)     # Automatically fix lint issues in a cycle"
	@echo "  $(YELLOW)make test-cov$(NC)      # Run tests with coverage"
	@echo ""
	@echo "For more information, see the project documentation."
