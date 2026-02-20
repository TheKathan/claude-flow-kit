# Backend Python Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Python Backend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Python/FastAPI backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
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
1. Gets its own **isolated worktree** (with Docker environment for Docker projects)
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All pytest tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

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
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Python Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  python-developer                   → Implement Python/FastAPI feature
Step 3:  python-test-specialist             → Write pytest tests
Step 4:  python-developer                   → Commit code + tests
Step 5:  integration-tester                 → Run pytest unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  python-developer                   → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  python-developer                   → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
Step 11b: [DOCKER/ON-FAILURE] docker-debugger → Debug integration issues
Step 12: worktree-manager                   → Merge to base branch, push
Step 13: worktree-manager                   → Cleanup worktree
Step 13b: [DOCKER/ON-FAILURE] docker-debugger → Force cleanup
```

> `b` steps only activate for Docker projects when container failures occur.

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

**Action**: Create isolated worktree

**Commands**:
```bash
# Agent runs:
python scripts/worktree_create.py feature-name
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`

> **Note**: The worktree branches from whichever branch is currently checked out. At Step 12, the feature branch will be merged back to that same base branch.

> *(Docker projects only)* The script automatically starts Docker containers with unique ports, providing a completely isolated Python environment with a separate database per worktree — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

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
# With Docker:
docker-compose exec backend black {{BACKEND_FOLDER}}/
docker-compose exec backend isort {{BACKEND_FOLDER}}/
docker-compose exec backend ruff check {{BACKEND_FOLDER}}/ --fix
docker-compose exec backend mypy {{BACKEND_FOLDER}}/

# Without Docker:
black {{BACKEND_FOLDER}}/
isort {{BACKEND_FOLDER}}/
ruff check {{BACKEND_FOLDER}}/ --fix
mypy {{BACKEND_FOLDER}}/

# Commit
git add .
git commit -m "feat: add user creation endpoint

- Implement POST /api/users endpoint with FastAPI
- Add Pydantic UserCreate and UserResponse schemas
- Add SQLAlchemy User model with email uniqueness constraint
- Implement async user service with duplicate email check
- Add comprehensive pytest tests (unit + integration)
- Test coverage: 85%"
```

**Commit Format**:
```
<type>: <short description>

- Implementation details
- Test coverage: X%
```

**Types**: feat, fix, docs, style, refactor, test, chore

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec backend pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing --cov-report=html -v

# Without Docker:
pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing --cov-report=html -v
```

**Pass Criteria**:
- All pytest tests pass (0 failures, 0 errors)
- Coverage ≥ 80%
- No critical ruff/mypy errors

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes python-developer to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

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
# With Docker:
docker-compose exec backend pytest tests/integration/ -v

# Check API health:
curl http://localhost:8000/health

# Without Docker:
pytest tests/integration/ -v

# Check API health:
curl http://localhost:8000/health
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

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

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
1. Pull latest base branch
2. Merge base branch into feature branch
3. Detect conflicts
4. Resolve automatically (or request manual review for complex cases)
5. Commit resolution
6. Push resolved feature branch to remote

```bash
# Push after conflict resolution:
git push origin HEAD --force-with-lease
```

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

**Purpose**: Verify everything works with base branch merged

**Commands**:
```bash
# With Docker:
docker-compose exec backend pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing -v
docker-compose exec backend ruff check {{BACKEND_FOLDER}}/
docker-compose exec backend mypy {{BACKEND_FOLDER}}/

# Without Docker:
pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing -v
ruff check {{BACKEND_FOLDER}}/
mypy {{BACKEND_FOLDER}}/
```

**Pass Criteria**:
- All tests pass after merge
- No new linting errors
- Type checking passes

**On Fail**:
- Workflow BLOCKED
- python-developer fixes merge issues

**On Docker Failure** (Step 11b) *(Docker projects only)*:
- docker-debugger diagnoses issues
- Fixes and retries

---

### Step 12: Merge to Base Branch

**Agent**: worktree-manager

**Actions**:
1. Verify all gates passed
2. Merge feature branch to base branch
3. Push base branch to remote
4. Update worktree registry

**Commands**:
```bash
# Agent runs:
python scripts/worktree_merge.py <worktree-id>
```

**Output**:
- Feature merged to base branch
- Base branch pushed to remote
- Ready for cleanup

---

### Step 13: Cleanup

**Agent**: worktree-manager

**Actions**:
1. Delete worktree
2. Update registry

*(Docker projects only)* Also stops and removes Docker containers, and optionally cleans up images/volumes.

**Commands**:
```bash
# Agent runs:
python scripts/worktree_cleanup.py <worktree-id>
```

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources
- Removes containers, images, volumes
- Ensures clean state

---

## Workflow Variants

### Standard Workflow (11 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Regular Python backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium
**Note**: Skips E2E tests (Step 8) and final integration test (Step 11)

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New Python services, architectural changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Python fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing Python code, improving coverage
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips implementation and E2E tests

### Docs-Only Workflow (5 steps)

**Steps**: 1 → 2 → 9 → 12 → 13

**Use For**: Documentation changes only
**Time**: 10-15 minutes
**Cost**: Very Low
**Note**: Skips testing and review; for documentation PRs only

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
# With Docker:
docker-compose exec backend black {{BACKEND_FOLDER}}/
docker-compose exec backend isort {{BACKEND_FOLDER}}/
docker-compose exec backend ruff check {{BACKEND_FOLDER}}/ --fix
docker-compose exec backend mypy {{BACKEND_FOLDER}}/

# Without Docker:
black {{BACKEND_FOLDER}}/
isort {{BACKEND_FOLDER}}/
ruff check {{BACKEND_FOLDER}}/ --fix
mypy {{BACKEND_FOLDER}}/
```

### Testing
```bash
# With Docker:
docker-compose exec backend pytest -v
docker-compose exec backend pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing
docker-compose exec backend pytest tests/test_users.py -v
docker-compose exec backend pytest -k "test_create" -v

# Without Docker:
pytest -v
pytest --cov={{BACKEND_FOLDER}} --cov-report=term-missing
pytest tests/test_users.py -v
pytest -k "test_create" -v
```

### Database Migrations (Alembic)
```bash
# With Docker:
docker-compose exec backend alembic revision --autogenerate -m "Add user table"
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic downgrade -1

# Without Docker:
alembic revision --autogenerate -m "Add user table"
alembic upgrade head
alembic downgrade -1
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
2. With Docker: rebuild the Docker container. Without Docker: rebuild the virtual environment.
3. Check for circular imports

---

## Resources

- [Python Development Guide](../.claude/PYTHON_GUIDE.md) - Python coding standards
- [Testing Guide](TESTING_GUIDE.md) - pytest practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Official FastAPI docs
- [pytest Documentation](https://docs.pytest.org/) - pytest testing framework

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
