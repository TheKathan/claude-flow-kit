# Backend Python Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Python Backend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Python/FastAPI backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree{{#if USES_DOCKER}} + Docker environment{{/if}})
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with pytest)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

---

## Workflow Architecture

### Core Principle

**Isolated, Test-Driven Quality with Automated Gates**

Every backend feature:
1. Gets its own **isolated worktree{{#if USES_DOCKER}} + Docker environment{{/if}}**
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All pytest tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with {{MAIN_BRANCH}} merged must pass

---

## Agent System

**Specialized Agents for Python Backend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **python-developer** | **Developer** | **Backend** | **Implement Python/FastAPI features** | sonnet |
| **python-test-specialist** | **Tester** | **Backend** | **Write pytest tests** | sonnet |
| **backend-code-reviewer** | **Reviewer** | **Backend** | **Review backend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
{{#if USES_DOCKER}}| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** | sonnet |{{/if}}
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Python Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree{{#if USES_DOCKER}} + Docker{{/if}}
{{#if USES_DOCKER}}Step 1b: [ON-FAILURE] docker-debugger       → Debug setup issues{{/if}}
Step 2:  python-developer                   → Implement Python/FastAPI feature
Step 3:  python-test-specialist             → Write pytest tests
Step 4:  python-developer                   → Commit code + tests
Step 5:  integration-tester                 → Run pytest unit tests [GATE]
{{#if USES_DOCKER}}Step 5b: [ON-FAILURE] docker-debugger       → Debug test issues{{/if}}
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  python-developer                   → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
{{#if USES_DOCKER}}Step 8b: [ON-FAILURE] docker-debugger       → Debug E2E issues{{/if}}
Step 9:  python-developer                   → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
{{#if USES_DOCKER}}Step 11b: [ON-FAILURE] docker-debugger      → Debug integration issues{{/if}}
Step 12: worktree-manager                   → Merge to {{MAIN_BRANCH}}, push
Step 13: worktree-manager                   → Cleanup worktree{{#if USES_DOCKER}} + Docker{{/if}}
{{#if USES_DOCKER}}Step 13b: [ON-FAILURE] docker-debugger      → Force cleanup{{/if}}
```

---

## Step-by-Step Guide

### Step 0: Architectural Planning (Optional)

**When to Use**:
- ✅ New API services or major endpoints
- ✅ Database schema changes
- ✅ Complex features with multiple integration points
- ✅ Major refactoring

**When to Skip**:
- ❌ Bug fixes
- ❌ Minor tweaks
- ❌ Simple CRUD operations

**Agent**: software-architect (opus model)

**Output**: Architecture design document with:
- Context and requirements
- Proposed FastAPI architecture
- Database schema (SQLAlchemy models)
- API endpoint design
- Design decisions and trade-offs
- Implementation plan

---

### Step 1: Create Worktree

**Agent**: worktree-manager

**Action**: Create isolated worktree{{#if USES_DOCKER}} with Docker environment{{/if}}

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_create.sh feature-name "Feature description"
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`
{{#if USES_DOCKER}}- Docker containers running with unique ports (including PostgreSQL/MySQL and Redis)
- Completely isolated Python environment with separate database per worktree
- No shared resources with main branch{{/if}}

{{#if USES_DOCKER}}**On Failure** (Step 1b):
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed
{{/if}}

---

### Step 2: Implement Feature

**Agent**: python-developer

**Responsibilities**:
- Write clean, maintainable Python code
- Follow PEP 8 style guide
- Add type hints (mypy compatible)
- Write docstrings (Google or NumPy style)
- Follow FastAPI patterns (async/await, dependency injection)
- Use Pydantic models for validation
- Handle errors gracefully with FastAPI HTTPException
- Place scripts in `scripts/` folder

**Python-Specific Patterns**:
```python
# FastAPI endpoint with dependency injection
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter()

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Create a new user.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created user data

    Raises:
        HTTPException: If user already exists
    """
    # Implementation here
    pass
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: python-test-specialist

**Responsibilities**:
- Analyze Python implementation
- Design test scenarios (happy path, errors, edge cases, security)
- Implement pytest tests with fixtures and mocks
- Target 80%+ coverage
- Document test purpose

**Python Test Structure** (pytest with AAA Pattern):
```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.models import User

@pytest.fixture
async def test_user(db_session):
    """Fixture for creating a test user."""
    user = User(email="test@example.com", username="testuser")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_create_user_success(async_client: AsyncClient):
    """Test successful user creation."""
    # Arrange
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "SecurePass123!"
    }

    # Act
    response = await async_client.post("/api/users", json=user_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "password" not in data  # Password should not be returned

@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client: AsyncClient, test_user):
    """Test that duplicate email raises 409 Conflict."""
    # Arrange
    user_data = {
        "email": test_user.email,  # Duplicate email
        "username": "different",
        "password": "SecurePass123!"
    }

    # Act
    response = await async_client.post("/api/users", json=user_data)

    # Assert
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()
```

**Test Coverage Requirements**:
- Unit tests: All functions and methods
- API tests: All endpoints (success + error cases)
- Database tests: CRUD operations with SQLAlchemy
- Security tests: Authentication, authorization, input validation
- Edge cases: Empty inputs, invalid types, boundary conditions

---

### Step 4: Commit Code + Tests

**Agent**: python-developer

**Commands**:
```bash
{{#if USES_DOCKER}}# Run black formatter
docker-compose exec backend black {{BACKEND_FOLDER}}/

# Run isort for imports
docker-compose exec backend isort {{BACKEND_FOLDER}}/

# Run ruff linter
docker-compose exec backend ruff check {{BACKEND_FOLDER}}/ --fix

# Type check with mypy
docker-compose exec backend mypy {{BACKEND_FOLDER}}/
{{else}}# Run black formatter
black {{BACKEND_FOLDER}}/

# Run isort for imports
isort {{BACKEND_FOLDER}}/

# Run ruff linter
ruff check {{BACKEND_FOLDER}}/ --fix

# Type check with mypy
mypy {{BACKEND_FOLDER}}/
{{/if}}

# Commit
git add .
git commit -m "feat: add user creation endpoint

- Implement POST /api/users endpoint with FastAPI
- Add Pydantic UserCreate and UserResponse schemas
- Add SQLAlchemy User model with email uniqueness constraint
- Implement async user service with duplicate email check
- Add comprehensive pytest tests (unit + integration)
- Test coverage: 85%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Commit Format**:
```
<type>: <short description>

- Implementation details
- Test coverage: X%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types**: feat, fix, docs, style, refactor, test, chore

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
{{#if USES_DOCKER}}# Run pytest with coverage
docker-compose exec backend pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing --cov-report=html -v

# Check coverage report
docker-compose exec backend cat htmlcov/index.html
{{else}}# Run pytest with coverage
pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing --cov-report=html -v

# Check coverage report
cat htmlcov/index.html
{{/if}}
```

**Pass Criteria**:
- All pytest tests pass (0 failures, 0 errors)
- Coverage ≥ 80%
- No critical ruff/mypy errors

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes python-developer to fix
- Returns to Step 5 after fix

{{#if USES_DOCKER}}**On Docker Failure** (Step 5b):
- docker-debugger diagnoses container issues
- Fixes and retries test execution
{{/if}}

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Security** (SQL injection, auth bypass, input validation)
- ✅ **Performance** (query optimization, async patterns, N+1 queries)
- ✅ **Best Practices** (PEP 8, type hints, docstrings, error handling)
- ✅ **Architecture** (FastAPI patterns, dependency injection, service layer)
- ✅ **Database** (SQLAlchemy best practices, migrations, constraints)
- ✅ **API Design** (RESTful conventions, status codes, response models)

**Python-Specific Checks**:
- Type hints on all functions
- Async/await used correctly
- Pydantic models for validation
- SQLAlchemy relationships configured properly
- Database sessions managed correctly (no leaks)
- Error handling with FastAPI HTTPException
- No SQL injection vulnerabilities (using parameterized queries)

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: python-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-format with black/isort
- Re-check with ruff/mypy
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
{{#if USES_DOCKER}}# Backend E2E tests
docker-compose exec backend python scripts/test_integration.py

# Or pytest integration tests
docker-compose exec backend pytest tests/integration/ -v

# Check API health
curl http://localhost:{{BACKEND_PORT}}/health
{{else}}# Backend E2E tests
python scripts/test_integration.py

# Or pytest integration tests
pytest tests/integration/ -v

# Check API health
curl http://localhost:8000/health
{{/if}}
```

**Pass Criteria**:
- All E2E tests pass
- API responds correctly to all test scenarios
- Database operations work end-to-end
- No integration failures

**On Fail**:
- Workflow BLOCKED
- python-developer fixes issues
- May loop back to Step 5-6 if code changes needed

{{#if USES_DOCKER}}**On Docker Failure** (Step 8b):
- docker-debugger diagnoses E2E test issues
- Fixes and retries
{{/if}}

---

### Step 9: Push Feature Branch

**Agent**: python-developer

**Commands**:
```bash
git push -u origin HEAD
```

**Verification**:
- Branch pushed successfully to remote
- Remote tracking set up
- CI/CD pipeline triggered (if configured)

---

### Step 10: Resolve Merge Conflicts ⚠️ GATE

**Agent**: merge-conflict-resolver (opus model)

**Actions**:
1. Pull latest {{MAIN_BRANCH}}
2. Merge {{MAIN_BRANCH}} into feature branch
3. Detect conflicts
4. Resolve automatically (or request manual review for complex cases)
5. Commit resolution

**Python-Specific Conflict Types**:
- **Simple**: imports, whitespace, formatting → auto-resolve
- **Models**: SQLAlchemy model changes → integrate both, check migrations
- **Endpoints**: Different API endpoints → integrate both
- **Logic**: Different implementations of same function → request manual review
- **Complex**: Fundamental conflicts in business logic → request manual review

**Outcomes**:
- ✅ **RESOLVED** - Continue to Step 11
- ⚠️ **MANUAL REVIEW NEEDED** - Workflow PAUSED
- ❌ **FAILED** - Workflow BLOCKED

---

### Step 11: Final Integration Test ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Purpose**: Verify everything works with {{MAIN_BRANCH}} merged

**Commands**:
```bash
{{#if USES_DOCKER}}# Full test suite
docker-compose exec backend pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing -v

# Run linters
docker-compose exec backend ruff check {{BACKEND_FOLDER}}/
docker-compose exec backend mypy {{BACKEND_FOLDER}}/
{{else}}# Full test suite
pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing -v

# Run linters
ruff check {{BACKEND_FOLDER}}/
mypy {{BACKEND_FOLDER}}/
{{/if}}
```

**Pass Criteria**:
- All tests pass after merge
- No new linting errors
- Type checking passes

**On Fail**:
- Workflow BLOCKED
- python-developer fixes merge issues

{{#if USES_DOCKER}}**On Docker Failure** (Step 11b):
- docker-debugger diagnoses issues
- Fixes and retries
{{/if}}

---

### Step 12: Merge to {{MAIN_BRANCH}}

**Agent**: worktree-manager

**Actions**:
1. Verify all gates passed
2. Merge feature branch to {{MAIN_BRANCH}}
3. Push {{MAIN_BRANCH}} to remote
4. Update worktree registry

**Commands**:
```bash
# Agent runs:
python scripts/worktree_merge.py <worktree-id>
```

**Output**:
- Feature merged to {{MAIN_BRANCH}}
- {{MAIN_BRANCH}} pushed to remote
- Ready for cleanup

---

### Step 13: Cleanup

**Agent**: worktree-manager

**Actions**:
1. Stop{{#if USES_DOCKER}} and remove Docker containers{{/if}}
2. Delete worktree
3. Update registry
{{#if USES_DOCKER}}4. Clean up Docker images/volumes (optional){{/if}}

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_cleanup.sh <worktree-id>
```

{{#if USES_DOCKER}}**On Failure** (Step 13b):
- docker-debugger force cleanups stuck resources
- Removes containers, images, volumes
- Ensures clean state
{{/if}}

---

## Workflow Variants

### Standard Workflow (11 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: Regular Python backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New Python services, architectural changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Python fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests

---

## Python Development Best Practices

### DO

✅ Use type hints on all functions
✅ Write async functions for I/O operations
✅ Use Pydantic for request/response validation
✅ Follow PEP 8 style guide (enforced by black/ruff)
✅ Write comprehensive docstrings
✅ Use dependency injection for database sessions
✅ Handle errors with FastAPI HTTPException
✅ Use SQLAlchemy async session
✅ Write pytest fixtures for reusable test data
✅ Mock external dependencies in tests

### DON'T

❌ Skip type hints
❌ Use blocking I/O in async functions
❌ Hardcode configuration values
❌ Ignore ruff/mypy warnings
❌ Leak database sessions
❌ Use raw SQL without parameterization
❌ Return plain dicts from API endpoints (use Pydantic)
❌ Commit without running black/isort
❌ Skip error handling
❌ Write tests without fixtures

---

## Python Tools and Commands

### Formatting and Linting
```bash
{{#if USES_DOCKER}}# Format code with black
docker-compose exec backend black {{BACKEND_FOLDER}}/

# Sort imports with isort
docker-compose exec backend isort {{BACKEND_FOLDER}}/

# Lint with ruff
docker-compose exec backend ruff check {{BACKEND_FOLDER}}/ --fix

# Type check with mypy
docker-compose exec backend mypy {{BACKEND_FOLDER}}/
{{else}}# Format code with black
black {{BACKEND_FOLDER}}/

# Sort imports with isort
isort {{BACKEND_FOLDER}}/

# Lint with ruff
ruff check {{BACKEND_FOLDER}}/ --fix

# Type check with mypy
mypy {{BACKEND_FOLDER}}/
{{/if}}
```

### Testing
```bash
{{#if USES_DOCKER}}# Run all tests
docker-compose exec backend pytest -v

# Run with coverage
docker-compose exec backend pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing

# Run specific test file
docker-compose exec backend pytest tests/test_users.py -v

# Run tests matching pattern
docker-compose exec backend pytest -k "test_create" -v
{{else}}# Run all tests
pytest -v

# Run with coverage
pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing

# Run specific test file
pytest tests/test_users.py -v

# Run tests matching pattern
pytest -k "test_create" -v
{{/if}}
```

### Database Migrations (Alembic)
```bash
{{#if USES_DOCKER}}# Create migration
docker-compose exec backend alembic revision --autogenerate -m "Add user table"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
{{else}}# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
{{/if}}
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for Python errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### Pytest Tests Failing

1. Review pytest output for failure details
2. Check fixtures are properly configured
3. Verify database is in clean state
4. Fix implementation or tests
5. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if Python approach is correct
2. Consider architectural review
3. May need to restart with different FastAPI pattern

### Import Errors

1. Verify dependencies in requirements.txt
2. Rebuild{{#if USES_DOCKER}} Docker container{{else}} virtual environment{{/if}}
3. Check for circular imports

---

## Resources

- [Python Development Guide](../.claude/PYTHON_GUIDE.md) - Python coding standards
- [Testing Guide](TESTING_GUIDE.md) - pytest practices
{{#if USES_DOCKER}}- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands{{/if}}
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Official FastAPI docs
- [pytest Documentation](https://docs.pytest.org/) - pytest testing framework

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
