# Backend Rust Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Rust Backend Worktree-Based Workflow

---

## Overview

This guide covers the 14-step worktree-based workflow for **Rust backend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Rust's built-in test framework)
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
1. **Unit Test Gate** (Step 5) - All Rust tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by backend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents for Rust Backend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **rust-developer** | **Developer** | **Backend** | **Implement Rust features** | sonnet |
| **rust-test-specialist** | **Tester** | **Backend** | **Write Rust tests** | sonnet |
| **backend-code-reviewer** | **Reviewer** | **Backend** | **Review backend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 14-Step Rust Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER ONLY] docker-debugger → Setup Docker environment
Step 2:  rust-developer                     → Implement Rust feature
Step 3:  rust-test-specialist               → Write Rust tests
Step 4:  rust-developer                     → Commit code + tests
Step 5:  integration-tester                 → Run cargo test [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  rust-developer                     → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run integration tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug integration issues
Step 9:  rust-developer                     → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
Step 11b: [DOCKER/ON-FAILURE] docker-debugger → Debug integration issues
Step 12: worktree-manager                   → Merge to base branch, push
Step 13: worktree-manager                   → Cleanup worktree
Step 13b: [DOCKER/ON-FAILURE] docker-debugger → Force cleanup
```

> Step 1b activates for all Docker projects (dedicated Docker setup). Steps 5b, 8b, 11b, 13b only activate for Docker projects when container failures occur.

---

## Step-by-Step Guide

### Step 0: Architectural Planning (Optional)

**When to Use**:
- ✅ New services or major API endpoints
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
- Proposed Rust architecture (types, traits, modules)
- Database schema (SQLx models)
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

*(Docker projects only)* After the worktree is created, proceed to Step 1b where docker-debugger sets up the Docker environment.

**Step 1b: Setup Docker Environment** *(Docker projects only)*:
- docker-debugger creates isolated Docker environment for this worktree
- Configures unique port mappings to avoid conflicts
- Starts containers and verifies all services are healthy
- Reports access URLs and port mappings

---

### Step 2: Implement Feature

**Agent**: rust-developer

**Responsibilities**:
- Write safe, idiomatic Rust code
- Zero `clippy` warnings (`cargo clippy -- -D warnings`)
- Proper error handling with `thiserror` — no `unwrap()` in production paths
- Use `?` operator for error propagation
- Structured logging with `tracing`
- Place scripts in `scripts/` folder

**Rust-Specific Patterns**:
```rust
use axum::{extract::State, http::StatusCode, response::Json};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct CreateUserRequest {
    pub email: String,
    pub username: String,
    pub password: String,
}

#[derive(Serialize)]
pub struct UserResponse {
    pub id: i64,
    pub email: String,
    pub username: String,
}

pub async fn create_user(
    State(state): State<AppState>,
    Json(req): Json<CreateUserRequest>,
) -> Result<(StatusCode, Json<UserResponse>), AppError> {
    let user = state.user_service.create_user(req).await?;
    Ok((StatusCode::CREATED, Json(user)))
}
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: rust-test-specialist

**Responsibilities**:
- Analyze Rust implementation
- Design test scenarios (happy path, errors, edge cases, security)
- Write unit tests in `#[cfg(test)]` modules within source files
- Write integration tests in `tests/` directory
- Use `mockall` for mocking traits
- Target 80%+ coverage with `cargo tarpaulin`
- Document test purpose with descriptive names

**Rust Test Structure**:
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;

    #[tokio::test]
    async fn get_user_returns_user_when_found() {
        let mut mock_repo = MockUserRepository::new();
        mock_repo
            .expect_find_by_id()
            .with(eq(1i64))
            .times(1)
            .returning(|_| Ok(Some(User {
                id: 1,
                email: "alice@example.com".into(),
                username: "alice".into(),
            })));

        let service = UserService::new(Arc::new(mock_repo));
        let result = service.get_user(1).await;

        assert!(result.is_ok());
        let user = result.unwrap();
        assert_eq!(user.email, "alice@example.com");
    }

    #[tokio::test]
    async fn get_user_returns_not_found_error() {
        let mut mock_repo = MockUserRepository::new();
        mock_repo
            .expect_find_by_id()
            .with(eq(999i64))
            .times(1)
            .returning(|_| Ok(None));

        let service = UserService::new(Arc::new(mock_repo));
        let result = service.get_user(999).await;

        assert!(matches!(result, Err(AppError::NotFound)));
    }
}
```

**Test Coverage Requirements**:
- Service layer: all business logic paths
- Handler tests: all endpoints (success + error cases)
- Error variants: every `Err(...)` variant must have a test
- Security: input validation, authentication checks
- Edge cases: empty inputs, boundary conditions

---

### Step 4: Commit Code + Tests

**Agent**: rust-developer

**Commands**:
```bash
# Format and lint
cargo fmt
cargo clippy -- -D warnings
cargo audit  # Security check

# Run tests before committing
cargo test

# Commit
git add src/ tests/ Cargo.toml
git commit -m "feat: add user creation endpoint

- Implement POST /api/users handler with Axum
- Add UserService with create_user business logic
- Add SQLx repository for database operations
- Define typed AppError with IntoResponse impl
- Add unit tests with mockall (87% coverage)
- Zero clippy warnings, formatted with rustfmt"
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
docker-compose exec app cargo test
docker-compose exec app cargo clippy -- -D warnings
docker-compose exec app cargo fmt --check

# Without Docker:
cargo test
cargo clippy -- -D warnings
cargo fmt --check
```

**Pass Criteria**:
- All `cargo test` tests pass (0 failures)
- `cargo clippy -- -D warnings` reports zero warnings
- `cargo fmt --check` passes (no formatting issues)
- Coverage ≥ 80% (via `cargo tarpaulin`)

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes rust-developer to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Memory Safety** (no `unwrap()` in production, proper lifetime management)
- ✅ **Error Handling** (typed errors, no silent failures, proper propagation with `?`)
- ✅ **Security** (input validation, parameterized queries, no SQL injection risk)
- ✅ **Performance** (no unnecessary clones, proper `Arc` usage, async correctness)
- ✅ **Idiomatic Rust** (ownership patterns, trait usage, iterator chains)
- ✅ **Concurrency** (no data races, correct `Send`/`Sync` bounds, safe `Mutex` usage)

**Rust-Specific Checks**:
- No `unwrap()` or `expect()` on `Result`/`Option` in non-test code
- No `unsafe` blocks without thorough documentation
- Errors implement `IntoResponse` for Axum handlers
- `tracing` used for structured logging (not `println!`)
- Sensitive values wrapped in `secrecy::Secret`
- SQLx queries use `query!` macro for compile-time verification where possible

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: rust-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-run `cargo fmt` and `cargo clippy`
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec app cargo test --test '*'
curl http://localhost:8080/health

# Without Docker:
cargo test --test '*'
curl http://localhost:8080/health
```

**Pass Criteria**:
- All integration tests pass
- API health endpoint responds correctly
- Database operations work end-to-end
- No integration failures

**On Fail**:
- Workflow BLOCKED
- rust-developer fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: rust-developer

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

**Rust-Specific Conflict Types**:
- **Simple**: comments, whitespace, formatting → auto-resolve
- **Types/structs**: Different field additions → integrate both
- **Cargo.toml**: Different dependency additions → merge both dependency lists
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
docker-compose exec app cargo test
docker-compose exec app cargo clippy -- -D warnings

# Without Docker:
cargo test
cargo clippy -- -D warnings
```

**Pass Criteria**:
- All tests pass after merge
- No new clippy warnings
- Binary compiles successfully

**On Fail**:
- Workflow BLOCKED
- rust-developer fixes merge issues

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
python scripts/worktree_merge.py feature-name
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
python scripts/worktree_cleanup.py feature-name
```

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources
- Removes containers, images, volumes
- Ensures clean state

---

### Step 14: Skill Discovery *(standard and full variants only)*

**Agent**: skill-creator

**Actions**:
1. Review the original task description and `git log --oneline` for the merged branch
2. Identify any multi-step patterns that emerged during Steps 2–7
3. Apply four gates: non-trivial, generalizable, not already covered, durable
4. Write a new skill to `.claude/commands/` or `.claude/agents/` if all gates pass, or decline with a written reason

**This step is non-blocking** — a declined evaluation is not a failure.

**Skip if**: variant is `hotfix`, `tests`, or `docs`; or the workflow completed with unresolved failures.

---

## Workflow Variants

### Standard Workflow (13 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13 → 14

**Use For**: Regular Rust backend features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium
**Note**: Skips E2E tests (Step 8) and final integration test (Step 11)

### Full Workflow (14 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14

**Use For**: New services, API surface changes, database schema changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (10 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Rust fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing Rust code, improving coverage
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips implementation and E2E tests

---

## Rust Development Best Practices

### DO

✅ Use `?` for error propagation — never ignore `Result`
✅ Define typed errors with `thiserror`
✅ Run `cargo clippy -- -D warnings` before every commit
✅ Run `cargo fmt` before every commit
✅ Use `tracing` for structured logging
✅ Wrap sensitive values in `secrecy::Secret`
✅ Use `Arc` for shared ownership across async tasks
✅ Write unit tests in `#[cfg(test)]` modules
✅ Use `mockall` to mock traits in unit tests
✅ Run `cargo audit` to check for security vulnerabilities

### DON'T

❌ Use `unwrap()` or `expect()` in production code
❌ Use `unsafe` without thorough justification and documentation
❌ Use `clone()` unnecessarily — prefer borrowing
❌ Hold `MutexGuard` across `.await` points
❌ Use `println!` for logging — use `tracing` instead
❌ Commit with clippy warnings
❌ Use `panic!` in library code
❌ Ignore compiler warnings
❌ Use global mutable state

---

## Rust Tools and Commands

### Formatting and Linting
```bash
cargo fmt                                  # Format all code
cargo fmt --check                          # Check formatting (CI mode)
cargo clippy -- -D warnings                # Lint with zero-warning policy
cargo clippy --tests -- -D warnings        # Also lint test code
cargo audit                                # Security audit
```

### Testing
```bash
cargo test                                 # Run all tests
cargo test -- --nocapture                  # Show println! output
cargo test user_service                    # Run tests matching pattern
cargo test --test integration_tests        # Run integration tests only
cargo tarpaulin --out Html --output-dir coverage/  # Generate coverage report
```

### Building
```bash
cargo build                                # Debug build
cargo build --release                      # Release build
cargo check                                # Fast type-check without building
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for Rust compiler or clippy errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### Borrow Checker Errors

1. Review ownership — who should own the data?
2. Consider `Arc<T>` for shared ownership
3. Consider `Clone` if copying is cheap
4. Use explicit lifetimes when the compiler cannot infer them

### Cargo.toml Conflicts After Merge

1. Merge dependency lists manually (keep both sets of dependencies)
2. Run `cargo update` to resolve version conflicts
3. Run `cargo check` to verify the merged result compiles

### Coverage Below 80%

1. Identify untested modules with `cargo tarpaulin`
2. Add tests for uncovered error paths
3. Use `mockall` to test paths that require external dependencies

---

## Resources

- [Rust Development Guide](../.claude/RUST_GUIDE.md) - Rust coding standards
- [Testing Guide](TESTING_GUIDE.md) - Testing practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [The Rust Book](https://doc.rust-lang.org/book/) - Official Rust documentation
- [Axum Examples](https://github.com/tokio-rs/axum/tree/main/examples) - Axum patterns

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
