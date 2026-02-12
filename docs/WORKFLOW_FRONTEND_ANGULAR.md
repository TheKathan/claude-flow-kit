# Frontend Angular Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Angular Frontend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Angular frontend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree{{#if USES_DOCKER}} + Docker environment{{/if}})
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Jasmine/Karma)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

---

## Agent System

**Specialized Agents for Angular Frontend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **angular-developer** | **Developer** | **Frontend** | **Implement Angular features** | sonnet |
| **angular-test-specialist** | **Tester** | **Frontend** | **Write Jasmine/Karma tests** | sonnet |
| **frontend-code-reviewer** | **Reviewer** | **Frontend** | **Review frontend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
{{#if USES_DOCKER}}| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** | sonnet |{{/if}}
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Angular Frontend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree{{#if USES_DOCKER}} + Docker{{/if}}
Step 2:  angular-developer                  → Implement Angular feature
Step 3:  angular-test-specialist            → Write Jasmine tests
Step 4:  angular-developer                  → Commit code + tests
Step 5:  integration-tester                 → Run unit tests [GATE]
Step 6:  frontend-code-reviewer             → Review code [GATE]
Step 7:  angular-developer                  → Fix if needed
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 9:  angular-developer                  → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
Step 12: worktree-manager                   → Merge to {{MAIN_BRANCH}}, push
Step 13: worktree-manager                   → Cleanup worktree
```

---

## Angular Development Best Practices

### DO

✅ Use standalone components (Angular 14+)
✅ Use TypeScript strict mode
✅ Implement OnPush change detection
✅ Use RxJS operators properly
✅ Follow Angular style guide
✅ Use dependency injection
✅ Write comprehensive Jasmine tests
✅ Implement proper accessibility
✅ Use signals (Angular 16+)
✅ Unsubscribe from observables

### DON'T

❌ Subscribe in templates without async pipe
❌ Ignore memory leaks
❌ Skip error handling
❌ Ignore ESLint/TSLint warnings
❌ Use `any` type
❌ Mutate state directly
❌ Skip unit tests
❌ Create circular dependencies
❌ Hardcode configuration values
❌ Forget to implement OnDestroy

---

## Resources

- [Angular Development Guide](../.claude/ANGULAR_GUIDE.md) - Angular coding standards
- [Testing Guide](TESTING_GUIDE.md) - Jasmine/Karma practices
- [Angular Documentation](https://angular.io/) - Official Angular docs
- [RxJS Documentation](https://rxjs.dev/) - Reactive programming

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
