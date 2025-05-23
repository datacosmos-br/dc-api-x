#!/bin/bash
#==============================================================================
# AUTO LINT FIX - AUTOMATIC CYCLE
#==============================================================================
# DESCRIPTION:
#   Script for automated execution of lint checks and fixes
#   in the dc-api-x project. The script continues to execute lint cycles and
#   correction until all problems are resolved or until reaching
#   the maximum number of attempts.
#
# USAGE:
#   cd dc-api-x
#   ./scripts/auto_lint_fix.sh
#
# OPTIONS:
#   DEBUG=1     # Sets detailed log level
#   MAX_CYCLES=n # Sets the maximum number of cycles (default: 10)
#
# EXAMPLES:
#   ./scripts/auto_lint_fix.sh                 # Run complete cycle
#   DEBUG=1 ./scripts/auto_lint_fix.sh         # Run with detailed logs
#   MAX_CYCLES=5 ./scripts/auto_lint_fix.sh    # Set maximum of 5 cycles
#
# NOTES:
#   - This script should be run from the project root
#   - Requires 'make lint', 'make lint-fix' and 'make format' to be configured
#   - Files are automatically modified during the process
#==============================================================================

set -e

# Settings
MAX_CYCLES=${MAX_CYCLES:-10}
CYCLES=0
DEBUG=${DEBUG:-0}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Initial banner
echo -e "${BLUE}${BOLD}================================================================${NC}"
echo -e "${BLUE}${BOLD}                AUTO LINT FIX - AUTOMATIC CYCLE                ${NC}"
echo -e "${BLUE}${BOLD}================================================================${NC}"
echo -e "${BOLD}This script automatically executes cycles of:${NC}"
echo -e " 1. ${YELLOW}Lint verification${NC} (make lint)"
echo -e " 2. ${YELLOW}Automatic correction${NC} (make lint-fix)"
echo -e " 3. ${YELLOW}Code formatting${NC} (make format)"
echo -e 
echo -e "${BOLD}The cycle continues until:${NC}"
echo -e " - No lint problems are found, OR"
echo -e " - The maximum number of $MAX_CYCLES cycles is reached"
echo -e 
echo -e "${BOLD}Files will be modified automatically!${NC}"
echo

# Check if we are at the project root
if [ ! -f "Makefile" ]; then
    echo -e "${RED}ERROR: This script must be run from the project root.${NC}"
    echo -e "${YELLOW}Use: cd \$(git rev-parse --show-toplevel) && ./scripts/auto_lint_fix.sh${NC}"
    exit 1
fi

PROJECT_ROOT=$(pwd)
echo -e "${BOLD}Project directory:${NC} $PROJECT_ROOT"
echo

# Debug function
debug() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${YELLOW}[DEBUG] $1${NC}"
    fi
}

# Function to execute lint verification
function run_lint() {
    echo -e "${YELLOW}[Cycle $CYCLES] Running lint verification...${NC}"
    # Save command output for analysis
    if make lint 2>&1 | tee /tmp/lint_output.log; then
        debug "Command 'make lint' executed successfully"
        return 0
    else
        debug "Command 'make lint' found problems"
        return 1
    fi
}

# Function to apply automatic fixes
function run_fix() {
    echo -e "${YELLOW}[Cycle $CYCLES] Applying automatic fixes...${NC}"
    debug "Running 'make lint-fix'"
    make lint-fix
    
    echo -e "${YELLOW}[Cycle $CYCLES] Formatting code...${NC}"
    debug "Running 'make format'"
    make format
}

# Main cycle
while [ $CYCLES -lt $MAX_CYCLES ]; do
    CYCLES=$((CYCLES + 1))
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}${BOLD}                     CYCLE $CYCLES OF $MAX_CYCLES${NC}"
    echo -e "${BLUE}================================================================${NC}"
    
    if run_lint; then
        echo -e "${GREEN}${BOLD}✓ No lint problems found!${NC}"
        echo -e "${GREEN}${BOLD}✓ Complete cycle in $CYCLES attempts.${NC}"
        exit 0
    else
        ERRORS=$(grep -ci "error\|warning\|issue" /tmp/lint_output.log || echo "0")
        echo -e "${RED}✗ Lint problems found. Trying automatic correction...${NC}"
        echo -e "${RED}  Approximately $ERRORS problems found.${NC}"
        
        # List the most common types of problems (only in debug mode)
        if [ "$DEBUG" = "1" ]; then
            echo -e "${YELLOW}[DEBUG] Most common problem types:${NC}"
            grep -o "E[0-9]\+\|F[0-9]\+\|W[0-9]\+" /tmp/lint_output.log | sort | uniq -c | sort -nr | head -5
        fi
        
        run_fix
        
        echo -e "${YELLOW}Checking results after automatic correction...${NC}"
    fi
    
    # Small pause to give processes time to complete
    sleep 1
done

# Maximum cycle reached without complete resolution
echo -e "${RED}================================================================${NC}"
echo -e "${RED}${BOLD}X Could not fix all problems after $MAX_CYCLES cycles.${NC}"
echo -e "${RED}${BOLD}X Some problems may need manual correction.${NC}"
echo -e "${RED}================================================================${NC}"
echo -e "${YELLOW}Running one last verification to show remaining problems:${NC}"
make lint

echo
echo -e "${BOLD}Recommended next steps:${NC}"
echo -e " 1. Manually fix the remaining problems"
echo -e " 2. Run 'make lint' to check again"
echo -e " 3. Run 'make fix' to apply all possible fixes"
echo -e " 4. Run this script again if necessary"

exit 1 
