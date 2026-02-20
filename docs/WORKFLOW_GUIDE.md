# Workflow Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Worktree-Based Workflow

---

## Overview

{{PROJECT_NAME}} uses an enhanced 13-step worktree-based workflow that integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

---

## Workflow Architecture

### Core Principle

**Isolated, Test-Driven Quality with Automated Gates**

Every feature:
1. Gets its own **isolated worktree** (with Docker environment for Docker projects)
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents**:

| Agent | Type | Scope | Role |
|-------|------|-------|------|
| software-architect | Architect | All | Design architecture (optional) |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** |
| backend-developer | Developer | Backend | Implement backend features |
| backend-test-specialist | Tester | Backend | Write backend tests |
| backend-code-reviewer | Reviewer | Backend | Review backend code |
| frontend-developer | Developer | Frontend | Implement frontend features |
| frontend-test-specialist | Tester | Frontend | Write frontend tests |
| frontend-code-reviewer | Reviewer | Frontend | Review frontend code |
| integration-tester | Tester | All | Execute all tests and enforce gates |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** |

> Replace `backend-developer` with the specific agent for your stack (e.g. `python-developer`, `dotnet-developer`, `nodejs-developer`, `go-developer`). Replace `frontend-developer` with `react-frontend-dev`, `vue-developer`, or `angular-developer` as applicable.

---

## 13-Step Workflow

### Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  backend-developer                  → Implement feature
Step 3:  backend-test-specialist            → Write tests
Step 4:  backend-developer                  → Commit code + tests
Step 5:  integration-tester                 → Run unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  backend-developer                  → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  backend-developer                  → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
Step 11b: [DOCKER/ON-FAILURE] docker-debugger → Debug integration issues
Step 12: worktree-manager                   → Merge to base branch, push
Step 13: worktree-manager                   → Cleanup worktree
Step 13b: [DOCKER/ON-FAILURE] docker-debugger → Force cleanup
```

> `b` steps only activate for Docker projects when container failures occur.

### Frontend Workflow

Same pattern with `frontend-developer`, `frontend-test-specialist`, `frontend-code-reviewer`.

---

## Step-by-Step Guide

### Step 0: Architectural Planning (Optional)

**When to Use**:
- ✅ New services or major components
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
- Proposed architecture
- Design decisions and trade-offs
- Implementation plan

---

### Step 1: Create Worktree

**Agent**: worktree-manager

**Action**: Create isolated worktree

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_create.sh feature-name "Feature description"
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`

> **Note**: The worktree branches from whichever branch is currently checked out. At Step 12, the feature branch will be merged back to that same base branch.

> *(Docker projects only)* Docker containers start with unique ports, providing a completely isolated environment with a separate database per worktree.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Feature

**Agent**: backend-developer or frontend-developer

**Responsibilities**:
- Write clean, maintainable code
- Follow project patterns
- Add docstrings and type hints
- Handle errors gracefully
- Place scripts in `scripts/` folder

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: backend-test-specialist or frontend-test-specialist

**Responsibilities**:
- Analyze implementation
- Design test scenarios (happy path, errors, edge cases, security)
- Implement tests with fixtures and mocks
- Target 80%+ coverage
- Document test purpose

**Test Structure** (AAA Pattern):
```python
def test_feature():
    # Arrange - Setup
    data = setup_test_data()

    # Act - Execute
    result = function_under_test(data)

    # Assert - Verify
    assert result == expected_value
```

---

### Step 4: Commit Code + Tests

**Agent**: backend-developer or frontend-developer

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
docker-compose exec backend <test command>
docker-compose exec frontend npm test -- --coverage

# Without Docker:
<test command>
npm test -- --coverage
```

**Pass Criteria**:
- All tests pass (0 failures)
- Coverage ≥ 80%

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes developer to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer or frontend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ Security (SQL injection, auth bypass, input validation)
- ✅ Performance (query optimization, async patterns)
- ✅ Best Practices (style guide, error handling)
- ✅ Architecture (follows project patterns)
- ✅ Accessibility (ARIA labels, keyboard navigation) — for frontend only

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: backend-developer or frontend-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
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
docker-compose exec frontend npm run test:e2e

# Without Docker:
pytest tests/integration/ -v
npm run test:e2e
```

**Pass Criteria**:
- All E2E tests pass
- No integration failures

**On Fail**:
- Workflow BLOCKED
- Developer fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: backend-developer or frontend-developer

**Commands**:
```bash
git push -u origin HEAD
```

**Verification**:
- Branch pushed successfully
- Remote tracking set up

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

**Conflict Types**:
- Simple: imports, whitespace → auto-resolve
- Logic: different implementations → integrate both
- Complex: fundamental conflicts → request manual review

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
docker-compose exec backend <test command>
docker-compose exec frontend npm test

# Without Docker:
<test command>
npm test
```

**Pass Criteria**:
- All tests pass after merge

**On Fail**:
- Workflow BLOCKED
- Developer fixes merge issues

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
bash scripts/worktree_cleanup.sh <worktree-id>
```

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources
- Removes containers, images, volumes
- Ensures clean state

---

## Workflow Variants

### Standard Workflow (11 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: Regular features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New services, architectural changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing code, improving coverage
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

## Best Practices

### DO

✅ Always create worktree for new features
✅ Write tests immediately after implementation
✅ Commit code + tests together
✅ Address all review comments
✅ Resolve conflicts carefully
✅ Keep worktrees short-lived (1-2 days max)

### DON'T

❌ Skip quality gates
❌ Commit without tests
❌ Ignore review feedback
❌ Force push without good reason
❌ Leave worktrees abandoned
❌ Create scripts outside `scripts/` folder

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### Tests Failing

1. Review test output
2. Fix implementation or tests
3. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if approach is correct
2. Consider architectural review
3. May need to restart with different approach

### Merge Conflicts Too Complex

1. Manual conflict resolution may be needed
2. Coordinate with other developers
3. Consider rebasing feature branch

---

## Resources

- [Development Guide](../.claude/DEVELOPMENT.md) - Coding standards
- [Testing Guide](TESTING_GUIDE.md) - Testing practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
