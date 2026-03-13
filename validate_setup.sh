#!/bin/bash

# Validation script for Alembic migration setup
# This script verifies that all required components are in place

echo "==================================="
echo "Alembic Migration Setup Validation"
echo "==================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counter for checks
PASSED=0
FAILED=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 is missing"
        ((FAILED++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 directory is missing"
        ((FAILED++))
        return 1
    fi
}

# Check Alembic configuration files
echo "Checking Alembic Configuration..."
check_file "alembic.ini"
check_file "migrations/env.py"
check_file "migrations/script.py.mako"
check_dir "migrations/versions"
echo ""

# Check migration files
echo "Checking Migration Files..."
check_file "migrations/versions/001_create_initial_tables.py"
check_file "migrations/versions/002_add_request_id_to_vales.py"
check_file "migrations/versions/003_add_indexes.py"
echo ""

# Check documentation
echo "Checking Documentation..."
check_file "MIGRATIONS.md"
check_file "DEVELOPMENT.md"
check_file "migrations/README.md"
echo ""

# Check Docker files
echo "Checking Docker Configuration..."
check_file "docker-compose.yml"
check_file "Dockerfile"
check_file "entrypoint.sh"
echo ""

# Check test files
echo "Checking Test Files..."
check_dir "tests"
check_file "tests/__init__.py"
check_file "tests/test_migrations.py"
echo ""

# Check other files
echo "Checking Other Files..."
check_file ".env.example"
check_file ".gitignore"
check_file "requirements.txt"
echo ""

# Check Alembic commands
echo "Checking Alembic Commands..."
if command -v alembic &> /dev/null; then
    echo -e "${GREEN}✓${NC} Alembic is installed"
    ((PASSED++))
    
    # Check migration history
    if alembic history &> /dev/null; then
        echo -e "${GREEN}✓${NC} Alembic can read migration history"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Alembic cannot read migration history"
        ((FAILED++))
    fi
    
    # Check heads
    if alembic heads &> /dev/null; then
        echo -e "${GREEN}✓${NC} Alembic can detect migration heads"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Alembic cannot detect migration heads"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Alembic is not installed"
    ((FAILED++))
fi
echo ""

# Check Python syntax
echo "Checking Python Syntax..."
if python -m py_compile migrations/versions/*.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} All migration files have valid Python syntax"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Migration files have syntax errors"
    ((FAILED++))
fi

if python -m py_compile tests/test_migrations.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Test file has valid Python syntax"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Test file has syntax errors"
    ((FAILED++))
fi
echo ""

# Summary
echo "==================================="
echo "Validation Summary"
echo "==================================="
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the output above.${NC}"
    exit 1
fi
