# Backend Go Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Go Backend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Go backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Go testing package)
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
1. **Unit Test Gate** (Step 5) - All Go tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents for Go Backend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **go-developer** | **Developer** | **Backend** | **Implement Go features** | sonnet |
| **go-test-specialist** | **Tester** | **Backend** | **Write Go tests** | sonnet |
| **backend-code-reviewer** | **Reviewer** | **Backend** | **Review backend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Go Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  go-developer                       → Implement Go feature
Step 3:  go-test-specialist                 → Write Go tests
Step 4:  go-developer                       → Commit code + tests
Step 5:  integration-tester                 → Run Go unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  go-developer                       → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  go-developer                       → Push to feature branch
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
- ✅ New API services or major handlers
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
- Proposed Go architecture (packages, interfaces)
- Database schema (GORM/sqlx models)
- API handler design
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

> *(Docker projects only)* The script automatically starts Docker containers with unique ports, providing a completely isolated Go environment with a separate database per worktree — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Feature

**Agent**: go-developer

**Responsibilities**:
- Write clean, idiomatic Go code
- Follow Effective Go principles
- Use interfaces for abstraction
- Write clear error messages
- Follow Go project structure (cmd/, internal/, pkg/)
- Use goroutines and channels appropriately
- Handle errors explicitly
- Place scripts in `scripts/` folder

**Go-Specific Patterns**:
```go
// HTTP handler with dependency injection
package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/myproject/internal/models"
	"github.com/myproject/internal/services"
	"github.com/go-chi/chi/v5"
)

// UserHandler handles user-related HTTP requests
type UserHandler struct {
	userService services.UserService
}

// NewUserHandler creates a new UserHandler
func NewUserHandler(userService services.UserService) *UserHandler {
	return &UserHandler{
		userService: userService,
	}
}

// CreateUser handles POST /api/users
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
	var req models.CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	user, err := h.userService.CreateUser(r.Context(), &req)
	if err != nil {
		switch err {
		case services.ErrUserExists:
			respondError(w, http.StatusConflict, "user already exists")
		default:
			respondError(w, http.StatusInternalServerError, "failed to create user")
		}
		return
	}

	respondJSON(w, http.StatusCreated, user)
}

// GetUser handles GET /api/users/{id}
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	userID := chi.URLParam(r, "id")

	user, err := h.userService.GetUserByID(r.Context(), userID)
	if err != nil {
		if err == services.ErrUserNotFound {
			respondError(w, http.StatusNotFound, "user not found")
			return
		}
		respondError(w, http.StatusInternalServerError, "failed to get user")
		return
	}

	respondJSON(w, http.StatusOK, user)
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string) {
	respondJSON(w, status, models.ErrorResponse{Error: message})
}
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: go-test-specialist

**Responsibilities**:
- Analyze Go implementation
- Design test scenarios (happy path, errors, edge cases, security)
- Implement table-driven tests
- Use testify for assertions
- Target 80%+ coverage
- Document test purpose

**Go Test Structure** (Table-Driven Tests):
```go
package handlers_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/myproject/internal/handlers"
	"github.com/myproject/internal/models"
	"github.com/myproject/internal/services"
	"github.com/myproject/internal/services/mocks"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

func TestUserHandler_CreateUser(t *testing.T) {
	tests := []struct {
		name           string
		requestBody    models.CreateUserRequest
		setupMock      func(*mocks.UserService)
		expectedStatus int
		checkResponse  func(*testing.T, *httptest.ResponseRecorder)
	}{
		{
			name: "successful user creation",
			requestBody: models.CreateUserRequest{
				Email:    "newuser@example.com",
				Username: "newuser",
				Password: "SecurePass123!",
			},
			setupMock: func(m *mocks.UserService) {
				m.On("CreateUser", mock.Anything, mock.AnythingOfType("*models.CreateUserRequest")).
					Return(&models.UserResponse{
						ID:       1,
						Email:    "newuser@example.com",
						Username: "newuser",
					}, nil)
			},
			expectedStatus: http.StatusCreated,
			checkResponse: func(t *testing.T, rec *httptest.ResponseRecorder) {
				var user models.UserResponse
				err := json.NewDecoder(rec.Body).Decode(&user)
				require.NoError(t, err)
				assert.Equal(t, "newuser@example.com", user.Email)
				assert.Equal(t, "newuser", user.Username)
				assert.NotZero(t, user.ID)
			},
		},
		{
			name: "duplicate email returns 409",
			requestBody: models.CreateUserRequest{
				Email:    "existing@example.com",
				Username: "newuser",
				Password: "SecurePass123!",
			},
			setupMock: func(m *mocks.UserService) {
				m.On("CreateUser", mock.Anything, mock.AnythingOfType("*models.CreateUserRequest")).
					Return(nil, services.ErrUserExists)
			},
			expectedStatus: http.StatusConflict,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mockService := new(mocks.UserService)
			tt.setupMock(mockService)

			handler := handlers.NewUserHandler(mockService)

			body, err := json.Marshal(tt.requestBody)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/users", bytes.NewReader(body))
			req.Header.Set("Content-Type", "application/json")
			rec := httptest.NewRecorder()

			handler.CreateUser(rec, req)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			if tt.checkResponse != nil {
				tt.checkResponse(t, rec)
			}
			mockService.AssertExpectations(t)
		})
	}
}
```

**Test Coverage Requirements**:
- Unit tests: All services and functions
- Handler tests: All HTTP handlers (success + error cases)
- Database tests: CRUD operations with GORM/sqlx
- Security tests: Authentication, authorization, input validation
- Edge cases: Nil inputs, invalid types, boundary conditions

---

### Step 4: Commit Code + Tests

**Agent**: go-developer

**Commands**:
```bash
# With Docker:
docker-compose exec backend gofmt -w .
docker-compose exec backend go vet ./...
docker-compose exec backend golangci-lint run
docker-compose exec backend go build ./...

# Without Docker:
gofmt -w .
go vet ./...
golangci-lint run
go build ./...

# Commit
git add .
git commit -m "feat: add user creation endpoint

- Implement POST /api/users handler
- Add CreateUserRequest and UserResponse models
- Add User entity with GORM
- Implement UserService with duplicate email check
- Add comprehensive table-driven tests with testify
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
docker-compose exec backend go test -v -cover ./...
docker-compose exec backend go test -coverprofile=coverage.out ./...
docker-compose exec backend go tool cover -html=coverage.out -o coverage.html

# Without Docker:
go test -v -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

**Pass Criteria**:
- All Go tests pass (PASS, no FAIL)
- Coverage ≥ 80%
- No critical golangci-lint errors
- go vet passes

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes go-developer to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Security** (SQL injection, auth bypass, input validation)
- ✅ **Performance** (query optimization, goroutine leaks, N+1 queries)
- ✅ **Best Practices** (Effective Go, error handling, interfaces)
- ✅ **Architecture** (package structure, dependency injection, service layer)
- ✅ **Database** (GORM/sqlx best practices, migrations)
- ✅ **API Design** (RESTful conventions, status codes, response structure)

**Go-Specific Checks**:
- Proper error handling (no ignored errors)
- Goroutines managed correctly (no leaks)
- Channels used safely (no deadlocks)
- Context propagation for cancellation
- Interfaces used for abstraction
- No race conditions
- Proper use of defer, panic, recover
- Database connections managed properly (no leaks)

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: go-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-format with gofmt
- Re-check with go vet and golangci-lint
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec backend go test -v -tags=integration ./tests/integration/...

# Check API health:
curl http://localhost:8080/health

# Without Docker:
go test -v -tags=integration ./tests/integration/...

# Check API health:
curl http://localhost:8080/health
```

**Pass Criteria**:
- All E2E tests pass
- API responds correctly to all test scenarios
- Database operations work end-to-end
- No integration failures
- No goroutine leaks

**On Fail**:
- Workflow BLOCKED
- go-developer fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: go-developer

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

**Go-Specific Conflict Types**:
- **Simple**: imports, whitespace, formatting → auto-resolve
- **Models**: Struct changes → integrate both
- **Handlers**: Different HTTP handlers → integrate both
- **Logic**: Different implementations of same function → request manual review
- **go.mod**: Dependency conflicts → merge carefully, run go mod tidy
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
docker-compose exec backend go test -v -cover ./...
docker-compose exec backend golangci-lint run
docker-compose exec backend go vet ./...
docker-compose exec backend go build ./...

# Without Docker:
go test -v -cover ./...
golangci-lint run
go vet ./...
go build ./...
```

**Pass Criteria**:
- All tests pass after merge
- No new linting errors
- Build succeeds

**On Fail**:
- Workflow BLOCKED
- go-developer fixes merge issues

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

**Use For**: Regular Go backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium
**Note**: Skips E2E tests (Step 8) and final integration test (Step 11)

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New Go services, architectural changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Go fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing Go code, improving coverage
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

## Go Development Best Practices

### DO

✅ Follow Effective Go principles
✅ Use interfaces for abstraction
✅ Handle all errors explicitly
✅ Use context for cancellation
✅ Write table-driven tests
✅ Use goroutines and channels appropriately
✅ Format code with gofmt
✅ Run go vet and golangci-lint
✅ Avoid goroutine leaks
✅ Use defer for cleanup

### DON'T

❌ Ignore errors
❌ Create goroutine leaks
❌ Use panic for normal errors
❌ Ignore race detector warnings
❌ Skip error checking
❌ Use global variables unnecessarily
❌ Create deadlocks with channels
❌ Forget to close resources
❌ Use synchronous operations in goroutines without careful consideration
❌ Commit without running gofmt

---

## Go Tools and Commands

### Building and Formatting
```bash
# With Docker:
docker-compose exec backend gofmt -w .
docker-compose exec backend go vet ./...
docker-compose exec backend golangci-lint run
docker-compose exec backend go build ./...
docker-compose exec backend go mod tidy

# Without Docker:
gofmt -w .
go vet ./...
golangci-lint run
go build ./...
go mod tidy
```

### Testing
```bash
# With Docker:
docker-compose exec backend go test -v ./...
docker-compose exec backend go test -v -cover ./...
docker-compose exec backend go test -v ./internal/handlers/...
docker-compose exec backend go test -race ./...
docker-compose exec backend go test -bench=. ./...

# Without Docker:
go test -v ./...
go test -v -cover ./...
go test -v ./internal/handlers/...
go test -race ./...
go test -bench=. ./...
```

### Database Migrations (golang-migrate)
```bash
# With Docker:
docker-compose exec backend migrate create -ext sql -dir migrations -seq add_users_table
docker-compose exec backend migrate -path migrations -database "postgres://..." up
docker-compose exec backend migrate -path migrations -database "postgres://..." down 1
docker-compose exec backend migrate -path migrations -database "postgres://..." version

# Without Docker:
migrate create -ext sql -dir migrations -seq add_users_table
migrate -path migrations -database "postgres://..." up
migrate -path migrations -database "postgres://..." down 1
migrate -path migrations -database "postgres://..." version
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for Go errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### Go Tests Failing

1. Review test output for failure details
2. Check for goroutine leaks
3. Run with race detector: `go test -race`
4. Fix implementation or tests
5. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if Go approach is correct
2. Consider architectural review
3. May need to restart with different pattern

### Dependency Issues

1. Run `go mod tidy`
2. Check go.mod and go.sum
3. With Docker: rebuild the Docker container. Without Docker: rebuild the project.
4. Verify module versions

---

## Resources

- [Go Development Guide](../.claude/GO_GUIDE.md) - Go coding standards
- [Testing Guide](TESTING_GUIDE.md) - Go testing practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [Effective Go](https://golang.org/doc/effective_go) - Official Go best practices
- [Go Testing Package](https://golang.org/pkg/testing/) - Standard testing package
- [Testify](https://github.com/stretchr/testify) - Testing toolkit

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
