# Workflow Guide - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Worktree-Based Workflow

---

## Overview

{{PROJECT_NAME}} uses an enhanced 13-step worktree-based workflow that integrates:
- **Worktree isolation** (each feature gets its own worktree{{#if USES_DOCKER}} + Docker environment{{/if}})
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
1. Gets its own **isolated worktree{{#if USES_DOCKER}} + Docker environment{{/if}}**
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with {{MAIN_BRANCH}} merged must pass

---

## Agent System

**Specialized Agents**:

| Agent | Type | Scope | Role |
|-------|------|-------|------|
| software-architect | Architect | All | Design architecture (optional) |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** |
| {{BACKEND_AGENT_NAME}} | Developer | Backend | Implement backend features |
| backend-test-specialist | Tester | Backend | Write backend tests |
| backend-code-reviewer | Reviewer | Backend | Review backend code |
{{#if HAS_FRONTEND}}| {{FRONTEND_AGENT_NAME}} | Developer | Frontend | Implement frontend features |
| frontend-test-specialist | Tester | Frontend | Write frontend tests |
| frontend-code-reviewer | Reviewer | Frontend | Review frontend code |{{/if}}
| integration-tester | Tester | All | Execute all tests and enforce gates |
{{#if USES_DOCKER}}| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** |{{/if}}
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** |

---

## 13-Step Workflow

### Backend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree{{#if USES_DOCKER}} + Docker{{/if}}
{{#if USES_DOCKER}}Step 1b: [ON-FAILURE] docker-debugger       → Debug setup issues{{/if}}
Step 2:  {{BACKEND_AGENT_NAME}}             → Implement feature
Step 3:  backend-test-specialist            → Write tests
Step 4:  {{BACKEND_AGENT_NAME}}             → Commit code + tests
Step 5:  integration-tester                 → Run unit tests [GATE]
{{#if USES_DOCKER}}Step 5b: [ON-FAILURE] docker-debugger       → Debug test issues{{/if}}
Step 6:  backend-code-reviewer              → Review code [GATE]
Step 7:  {{BACKEND_AGENT_NAME}}             → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
{{#if USES_DOCKER}}Step 8b: [ON-FAILURE] docker-debugger       → Debug E2E issues{{/if}}
Step 9:  {{BACKEND_AGENT_NAME}}             → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
{{#if USES_DOCKER}}Step 11b: [ON-FAILURE] docker-debugger      → Debug integration issues{{/if}}
Step 12: worktree-manager                   → Merge to {{MAIN_BRANCH}}, push
Step 13: worktree-manager                   → Cleanup worktree{{#if USES_DOCKER}} + Docker{{/if}}
{{#if USES_DOCKER}}Step 13b: [ON-FAILURE] docker-debugger      → Force cleanup{{/if}}
```

{{#if HAS_FRONTEND}}### Frontend Workflow

Same pattern with `{{FRONTEND_AGENT_NAME}}`, `frontend-test-specialist`, `frontend-code-reviewer`
{{/if}}

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

**Action**: Create isolated worktree{{#if USES_DOCKER}} with Docker environment{{/if}}

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_create.sh feature-name "Feature description"
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`
{{#if USES_DOCKER}}- Docker containers running with unique ports (including database and cache)
- Completely isolated environment with separate database per worktree
- No shared resources with main branch{{/if}}

{{#if USES_DOCKER}}**On Failure** (Step 1b):
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed
{{/if}}

---

### Step 2: Implement Feature

**Agent**: {{BACKEND_AGENT_NAME}}{{#if HAS_FRONTEND}} or {{FRONTEND_AGENT_NAME}}{{/if}}

**Responsibilities**:
- Write clean, maintainable code
- Follow project patterns
- Add docstrings and type hints
- Handle errors gracefully
- Place scripts in `scripts/` folder

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: backend-test-specialist{{#if HAS_FRONTEND}} or frontend-test-specialist{{/if}}

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

**Agent**: {{BACKEND_AGENT_NAME}}{{#if HAS_FRONTEND}} or {{FRONTEND_AGENT_NAME}}{{/if}}

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
{{#if USES_DOCKER}}# Backend
docker-compose exec backend {{TEST_COMMAND}}

{{#if HAS_FRONTEND}}# Frontend
docker-compose exec frontend npm test -- --coverage
{{/if}}{{else}}# Backend
{{TEST_COMMAND}}

{{#if HAS_FRONTEND}}# Frontend
npm test -- --coverage
{{/if}}{{/if}}
```

**Pass Criteria**:
- All tests pass (0 failures)
- Coverage ≥ 80%

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes developer to fix
- Returns to Step 5 after fix

{{#if USES_DOCKER}}**On Docker Failure** (Step 5b):
- docker-debugger diagnoses container issues
- Fixes and retries test execution
{{/if}}

---

### Step 6: Code Review ⚠️ GATE

**Agent**: backend-code-reviewer{{#if HAS_FRONTEND}} or frontend-code-reviewer{{/if}} (sonnet, opus for critical)

**Review Criteria**:
- ✅ Security (SQL injection, auth bypass, input validation)
- ✅ Performance (query optimization, async patterns)
- ✅ Best Practices (style guide, error handling)
- ✅ Architecture (follows project patterns)
{{#if HAS_FRONTEND}}- ✅ Accessibility (ARIA labels, keyboard navigation){{/if}}

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: {{BACKEND_AGENT_NAME}}{{#if HAS_FRONTEND}} or {{FRONTEND_AGENT_NAME}}{{/if}}

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
{{#if USES_DOCKER}}# Backend E2E tests
docker-compose exec backend python scripts/test_integration.py

{{#if HAS_FRONTEND}}# Frontend E2E tests
docker-compose exec frontend npm run test:e2e
{{/if}}{{else}}# Backend E2E tests
python scripts/test_integration.py

{{#if HAS_FRONTEND}}# Frontend E2E tests
npm run test:e2e
{{/if}}{{/if}}
```

**Pass Criteria**:
- All E2E tests pass
- No integration failures

**On Fail**:
- Workflow BLOCKED
- Developer fixes issues
- May loop back to Step 5-6 if code changes needed

{{#if USES_DOCKER}}**On Docker Failure** (Step 8b):
- docker-debugger diagnoses E2E test issues
- Fixes and retries
{{/if}}

---

### Step 9: Push Feature Branch

**Agent**: {{BACKEND_AGENT_NAME}}{{#if HAS_FRONTEND}} or {{FRONTEND_AGENT_NAME}}{{/if}}

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
1. Pull latest {{MAIN_BRANCH}}
2. Merge {{MAIN_BRANCH}} into feature branch
3. Detect conflicts
4. Resolve automatically (or request manual review for complex cases)
5. Commit resolution

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

**Purpose**: Verify everything works with {{MAIN_BRANCH}} merged

**Commands**:
```bash
{{#if USES_DOCKER}}# Full test suite
docker-compose exec backend pytest
{{#if HAS_FRONTEND}}docker-compose exec frontend npm test{{/if}}{{else}}# Full test suite
{{TEST_COMMAND}}
{{#if HAS_FRONTEND}}npm test{{/if}}{{/if}}
```

**Pass Criteria**:
- All tests pass after merge

**On Fail**:
- Workflow BLOCKED
- Developer fixes merge issues

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

**Use For**: Regular features, enhancements (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New services, architectural changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing code
**Time**: 15-20 minutes

### Docs-Only Workflow (6 steps)

**Steps**: 1 → 2 → 9 → 10 → 12 → 13

**Use For**: Documentation changes
**Time**: 10-15 minutes
**Note**: Skips testing and review

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
{{#if USES_DOCKER}}- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands{{/if}}
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
