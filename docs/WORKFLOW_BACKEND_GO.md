# Backend Go Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Go Backend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Go backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree{{#if USES_DOCKER}} + Docker environment{{/if}})
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
1. Gets its own **isolated worktree{{#if USES_DOCKER}} + Docker environment{{/if}}**
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All Go tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with {{MAIN_BRANCH}} merged must pass

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
{{#if USES_DOCKER}}| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** | sonnet |{{/if}}
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Go Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree{{#if USES_DOCKER}} + Docker{{/if}}
{{#if USES_DOCKER}}Step 1b: [ON-FAILURE] docker-debugger       → Debug setup issues{{/if}}
Step 2:  go-developer                       → Implement Go feature
Step 3:  go-test-specialist                 → Write Go tests
Step 4:  go-developer                       → Commit code + tests
Step 5:  integration-tester                 → Run Go unit tests [GATE]
{{#if USES_DOCKER}}Step 5b: [ON-FAILURE] docker-debugger       → Debug test issues{{/if}}
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  go-developer                       → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
{{#if USES_DOCKER}}Step 8b: [ON-FAILURE] docker-debugger       → Debug E2E issues{{/if}}
Step 9:  go-developer                       → Push to feature branch
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
- Completely isolated Go environment with separate database per worktree
- No shared resources with main branch{{/if}}

{{#if USES_DOCKER}}**On Failure** (Step 1b):
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed
{{/if}}

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
// @Summary Create a new user
// @Description Creates a new user with the provided data
// @Tags users
// @Accept json
// @Produce json
// @Param user body models.CreateUserRequest true "User creation data"
// @Success 201 {object} models.UserResponse
// @Failure 400 {object} models.ErrorResponse
// @Failure 409 {object} models.ErrorResponse
// @Router /api/users [post]
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
	w.WriteStatus(status)
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
	"context"
	"encoding/json"
	"errors"
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
		expectedBody   interface{}
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
			checkResponse: func(t *testing.T, rec *httptest.ResponseRecorder) {
				var errResp models.ErrorResponse
				err := json.NewDecoder(rec.Body).Decode(&errResp)
				require.NoError(t, err)
				assert.Contains(t, errResp.Error, "already exists")
			},
		},
		{
			name: "invalid request body returns 400",
			requestBody: models.CreateUserRequest{
				Email: "", // Invalid: empty email
			},
			setupMock:      func(m *mocks.UserService) {},
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			mockService := new(mocks.UserService)
			tt.setupMock(mockService)

			handler := handlers.NewUserHandler(mockService)

			body, err := json.Marshal(tt.requestBody)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/users", bytes.NewReader(body))
			req.Header.Set("Content-Type", "application/json")
			rec := httptest.NewRecorder()

			// Act
			handler.CreateUser(rec, req)

			// Assert
			assert.Equal(t, tt.expectedStatus, rec.Code)
			if tt.checkResponse != nil {
				tt.checkResponse(t, rec)
			}
			mockService.AssertExpectations(t)
		})
	}
}

func TestUserHandler_GetUser(t *testing.T) {
	tests := []struct {
		name           string
		userID         string
		setupMock      func(*mocks.UserService)
		expectedStatus int
	}{
		{
			name:   "user found",
			userID: "1",
			setupMock: func(m *mocks.UserService) {
				m.On("GetUserByID", mock.Anything, "1").
					Return(&models.UserResponse{
						ID:       1,
						Email:    "user@example.com",
						Username: "testuser",
					}, nil)
			},
			expectedStatus: http.StatusOK,
		},
		{
			name:   "user not found",
			userID: "999",
			setupMock: func(m *mocks.UserService) {
				m.On("GetUserByID", mock.Anything, "999").
					Return(nil, services.ErrUserNotFound)
			},
			expectedStatus: http.StatusNotFound,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			mockService := new(mocks.UserService)
			tt.setupMock(mockService)

			handler := handlers.NewUserHandler(mockService)

			req := httptest.NewRequest(http.MethodGet, "/api/users/"+tt.userID, nil)
			rec := httptest.NewRecorder()

			// Act
			handler.GetUser(rec, req)

			// Assert
			assert.Equal(t, tt.expectedStatus, rec.Code)
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
{{#if USES_DOCKER}}# Format code with gofmt
docker-compose exec backend gofmt -w .

# Run go vet
docker-compose exec backend go vet ./...

# Run golangci-lint
docker-compose exec backend golangci-lint run

# Build
docker-compose exec backend go build ./...
{{else}}# Format code with gofmt
gofmt -w .

# Run go vet
go vet ./...

# Run golangci-lint
golangci-lint run

# Build
go build ./...
{{/if}}

# Commit
git add .
git commit -m "feat: add user creation endpoint

- Implement POST /api/users handler
- Add CreateUserRequest and UserResponse models
- Add User entity with GORM
- Implement UserService with duplicate email check
- Add comprehensive table-driven tests with testify
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
{{#if USES_DOCKER}}# Run Go tests with coverage
docker-compose exec backend go test -v -cover ./...

# Generate coverage report
docker-compose exec backend go test -coverprofile=coverage.out ./...
docker-compose exec backend go tool cover -html=coverage.out -o coverage.html

# View coverage
docker-compose exec backend cat coverage.html
{{else}}# Run Go tests with coverage
go test -v -cover ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# View coverage
cat coverage.html
{{/if}}
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

{{#if USES_DOCKER}}**On Docker Failure** (Step 5b):
- docker-debugger diagnoses container issues
- Fixes and retries test execution
{{/if}}

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
{{#if USES_DOCKER}}# Backend E2E tests
docker-compose exec backend go test -v -tags=integration ./tests/integration/...

# Check API health
curl http://localhost:{{BACKEND_PORT}}/health
{{else}}# Backend E2E tests
go test -v -tags=integration ./tests/integration/...

# Check API health
curl http://localhost:8080/health
{{/if}}
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

{{#if USES_DOCKER}}**On Docker Failure** (Step 8b):
- docker-debugger diagnoses E2E test issues
- Fixes and retries
{{/if}}

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
1. Pull latest {{MAIN_BRANCH}}
2. Merge {{MAIN_BRANCH}} into feature branch
3. Detect conflicts
4. Resolve automatically (or request manual review for complex cases)
5. Commit resolution

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

**Purpose**: Verify everything works with {{MAIN_BRANCH}} merged

**Commands**:
```bash
{{#if USES_DOCKER}}# Full test suite
docker-compose exec backend go test -v -cover ./...

# Run linters
docker-compose exec backend golangci-lint run
docker-compose exec backend go vet ./...

# Build verification
docker-compose exec backend go build ./...
{{else}}# Full test suite
go test -v -cover ./...

# Run linters
golangci-lint run
go vet ./...

# Build verification
go build ./...
{{/if}}
```

**Pass Criteria**:
- All tests pass after merge
- No new linting errors
- Build succeeds

**On Fail**:
- Workflow BLOCKED
- go-developer fixes merge issues

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

**Use For**: Regular Go backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New Go services, architectural changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Go fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests

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
{{#if USES_DOCKER}}# Format code
docker-compose exec backend gofmt -w .

# Run go vet
docker-compose exec backend go vet ./...

# Run golangci-lint
docker-compose exec backend golangci-lint run

# Build
docker-compose exec backend go build ./...

# Tidy dependencies
docker-compose exec backend go mod tidy
{{else}}# Format code
gofmt -w .

# Run go vet
go vet ./...

# Run golangci-lint
golangci-lint run

# Build
go build ./...

# Tidy dependencies
go mod tidy
{{/if}}
```

### Testing
```bash
{{#if USES_DOCKER}}# Run all tests
docker-compose exec backend go test -v ./...

# Run with coverage
docker-compose exec backend go test -v -cover ./...

# Run specific package
docker-compose exec backend go test -v ./internal/handlers/...

# Run with race detector
docker-compose exec backend go test -race ./...

# Run benchmarks
docker-compose exec backend go test -bench=. ./...
{{else}}# Run all tests
go test -v ./...

# Run with coverage
go test -v -cover ./...

# Run specific package
go test -v ./internal/handlers/...

# Run with race detector
go test -race ./...

# Run benchmarks
go test -bench=. ./...
{{/if}}
```

### Database Migrations (golang-migrate)
```bash
{{#if USES_DOCKER}}# Create migration
docker-compose exec backend migrate create -ext sql -dir migrations -seq add_users_table

# Run migrations up
docker-compose exec backend migrate -path migrations -database "postgres://..." up

# Run migrations down
docker-compose exec backend migrate -path migrations -database "postgres://..." down 1

# Check migration version
docker-compose exec backend migrate -path migrations -database "postgres://..." version
{{else}}# Create migration
migrate create -ext sql -dir migrations -seq add_users_table

# Run migrations up
migrate -path migrations -database "postgres://..." up

# Run migrations down
migrate -path migrations -database "postgres://..." down 1

# Check migration version
migrate -path migrations -database "postgres://..." version
{{/if}}
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
3. Rebuild{{#if USES_DOCKER}} Docker container{{else}} project{{/if}}
4. Verify module versions

---

## Resources

- [Go Development Guide](../.claude/GO_GUIDE.md) - Go coding standards
- [Testing Guide](TESTING_GUIDE.md) - Go testing practices
{{#if USES_DOCKER}}- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands{{/if}}
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [Effective Go](https://golang.org/doc/effective_go) - Official Go best practices
- [Go Testing Package](https://golang.org/pkg/testing/) - Standard testing package
- [Testify](https://github.com/stretchr/testify) - Testing toolkit

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
