# Frontend Angular Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Angular Frontend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Angular frontend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with an optional Docker environment for containerized projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Jasmine/Karma)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

---

## Workflow Architecture

### Core Principle

**Isolated, Test-Driven Quality with Automated Gates**

Every Angular feature:
1. Gets its own **isolated worktree** branched from the current base branch
2. Goes through **mandatory quality gates** before being merged
3. Has **conflicts resolved automatically** before merge
4. Is **merged back to the base branch** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - Tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by frontend reviewer
3. **E2E Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - All tests must pass with base branch merged

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
| docker-debugger | Debugger | All | Diagnose and fix Docker issues *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Angular Frontend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  angular-developer                  → Implement Angular feature
Step 3:  angular-test-specialist            → Write Jasmine/Karma tests
Step 4:  angular-developer                  → Commit code + tests
Step 5:  integration-tester                 → Run unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  frontend-code-reviewer             → Review code [GATE]
Step 7:  angular-developer                  → Fix review issues (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  angular-developer                  → Push to feature branch
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

### Step 0: Architecture Planning (Optional)

**When to Use**:
- ✅ New Angular modules or lazy-loaded routes
- ✅ Complex state management with NgRx or Signals
- ✅ New shared libraries or design system components
- ✅ Multi-feature architectural changes

**When to Skip**:
- ❌ Simple component creation
- ❌ Style or template fixes
- ❌ Documentation updates

**Agent**: software-architect (opus model)

**Output**: Architecture document covering:
- Component hierarchy and module/route structure
- State management approach (NgRx, Signals, or services)
- Service and dependency injection design
- API integration pattern
- Testing strategy

---

### Step 1: Create Worktree

**Agent**: worktree-manager

**Action**: Create isolated worktree branched from the current branch

> **Note**: The worktree branches from whichever branch is currently checked out. At Step 12, the feature branch will be merged back to that same base branch.

**Commands**:
```bash
# Agent runs:
python scripts/worktree_create.py feature-name
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`
- Dependencies installed (`npm ci`)
- Development environment ready

> *(Docker projects only)* The script automatically starts Docker containers with unique ports, providing a completely isolated Angular development environment — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Angular Feature

**Agent**: angular-developer

**Responsibilities**:
- Generate components, services, pipes, and directives using Angular CLI
- Implement features following the Angular style guide
- Use standalone components (Angular 14+)
- Implement proper change detection strategy (OnPush preferred)
- Handle observables with the async pipe or proper unsubscription patterns
- Place all scripts in `scripts/` folder (never `/tmp/`)

**Angular CLI Commands**:
```bash
# Generate standalone component (Angular 14+)
ng generate component features/user-profile --standalone

# Generate service
ng generate service core/services/user

# Generate pipe (standalone)
ng generate pipe shared/pipes/format-date --standalone

# Generate route guard
ng generate guard core/guards/auth

# Generate interface/model
ng generate interface core/models/user
```

**Angular-Specific Pattern (RxJS + takeUntil)**:
```typescript
// user-profile.component.ts
import {
  Component, OnInit, OnDestroy, Input, ChangeDetectionStrategy
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';
import { UserService } from '../../core/services/user.service';
import { User } from '../../core/models/user.model';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './user-profile.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserProfileComponent implements OnInit, OnDestroy {
  @Input() userId!: string;

  user: User | null = null;
  isLoading = true;
  error: string | null = null;

  private readonly destroy$ = new Subject<void>();

  constructor(private readonly userService: UserService) {}

  ngOnInit(): void {
    this.userService.getUser(this.userId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (user) => { this.user = user; this.isLoading = false; },
        error: () => { this.error = 'Failed to load user profile'; this.isLoading = false; },
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**Signals Pattern (Angular 16+)**:
```typescript
// user-profile.component.ts (Signals approach)
import { Component, OnInit, signal, computed, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserService } from '../../core/services/user.service';
import { User } from '../../core/models/user.model';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './user-profile.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserProfileComponent implements OnInit {
  private readonly userService = inject(UserService);

  readonly user = signal<User | null>(null);
  readonly isLoading = signal(true);
  readonly error = signal<string | null>(null);

  readonly displayName = computed(() =>
    this.user() ? `${this.user()!.firstName} ${this.user()!.lastName}` : ''
  );

  ngOnInit(): void {
    this.userService.getUser('123').subscribe({
      next: (u) => { this.user.set(u); this.isLoading.set(false); },
      error: () => { this.error.set('Failed to load profile'); this.isLoading.set(false); },
    });
  }
}
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Jasmine/Karma Tests

**Agent**: angular-test-specialist

**Responsibilities**:
- Analyze component and service implementations
- Write unit tests using Jasmine and Angular TestBed
- Mock dependencies with `jasmine.createSpyObj`
- Test component rendering, `@Input`/`@Output`, events, and lifecycle hooks
- Test services using `HttpClientTestingModule`
- Target 80%+ coverage across statements, branches, functions, and lines

**Test Structure**:
```typescript
// user-profile.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { UserProfileComponent } from './user-profile.component';
import { UserService } from '../../core/services/user.service';

describe('UserProfileComponent', () => {
  let component: UserProfileComponent;
  let fixture: ComponentFixture<UserProfileComponent>;
  let userServiceSpy: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('UserService', ['getUser']);

    await TestBed.configureTestingModule({
      imports: [UserProfileComponent],
      providers: [{ provide: UserService, useValue: spy }],
    }).compileComponents();

    userServiceSpy = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
    fixture = TestBed.createComponent(UserProfileComponent);
    component = fixture.componentInstance;
    component.userId = '123';
  });

  it('should create', () => {
    userServiceSpy.getUser.and.returnValue(of({ id: '123', firstName: 'John', lastName: 'Doe' }));
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should load user on init', () => {
    const mockUser = { id: '123', firstName: 'John', lastName: 'Doe' };
    userServiceSpy.getUser.and.returnValue(of(mockUser));

    fixture.detectChanges();

    expect(component.user).toEqual(mockUser);
    expect(component.isLoading).toBeFalse();
    expect(userServiceSpy.getUser).toHaveBeenCalledWith('123');
  });

  it('should display user name in template', () => {
    const mockUser = { id: '123', firstName: 'John', lastName: 'Doe' };
    userServiceSpy.getUser.and.returnValue(of(mockUser));

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('John');
  });

  it('should handle error on load failure', () => {
    userServiceSpy.getUser.and.returnValue(throwError(() => new Error('Network error')));

    fixture.detectChanges();

    expect(component.error).toBe('Failed to load user profile');
    expect(component.isLoading).toBeFalse();
  });

  it('should show error message in template on failure', () => {
    userServiceSpy.getUser.and.returnValue(throwError(() => new Error('Network error')));

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Failed to load user profile');
  });

  it('should complete destroy$ on ngOnDestroy', () => {
    userServiceSpy.getUser.and.returnValue(of({ id: '123', firstName: 'John', lastName: 'Doe' }));
    fixture.detectChanges();

    const nextSpy = spyOn((component as any).destroy$, 'next');
    const completeSpy = spyOn((component as any).destroy$, 'complete');

    component.ngOnDestroy();

    expect(nextSpy).toHaveBeenCalled();
    expect(completeSpy).toHaveBeenCalled();
  });
});
```

---

### Step 4: Commit Code and Tests

**Agent**: angular-developer

**Commands**:
```bash
# Check TypeScript and lint
ng lint

# Format with Prettier (if configured)
npx prettier --write "src/**/*.{ts,html,scss}"

# Stage and commit
git add src/ e2e/
git commit -m "feat(user-profile): add user profile component with error handling

- Add standalone UserProfileComponent with OnPush change detection
- Implement RxJS unsubscription using takeUntil pattern
- Add error state handling and loading indicators
- Write Jasmine unit tests with 85% coverage"
```

**Commit Format**:
```
<type>(<scope>): <description>

- <bullet points of changes>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `chore`

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# Run unit tests with coverage
ng test --watch=false --code-coverage --no-progress

# View coverage summary
cat coverage/lcov-report/index.html | grep -E "Statements|Branches|Functions|Lines"
```

**Pass Criteria**:
- All Jasmine tests pass
- Coverage ≥ 80% (statements, branches, functions, lines)
- No TypeScript compilation errors
- No ESLint violations

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes angular-developer to fix failures (Step 5b)
- Returns to Step 5 after fix

---

### Step 6: Code Review ⚠️ GATE

**Agent**: frontend-code-reviewer (sonnet, escalate to opus for critical)

**Review Criteria**:
- ✅ **Angular Architecture** (standalone components, proper module boundaries)
- ✅ **TypeScript** (strict mode compliance, no `any` types, proper interfaces)
- ✅ **Performance** (OnPush change detection, `trackBy` in `*ngFor`, lazy loading)
- ✅ **RxJS** (no memory leaks, proper operators, complete error handling)
- ✅ **Security** (no XSS via `innerHTML`, proper DomSanitizer usage)
- ✅ **Accessibility** (ARIA labels, semantic HTML, keyboard navigation)
- ✅ **Testing** (test quality, meaningful assertions, edge cases covered)
- ✅ **Angular Style Guide** (naming conventions, file structure, single responsibility)

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Review Issues

**Agent**: angular-developer

**Action**: Address all code review feedback

**Process**:
1. Read review comments carefully
2. Fix each identified issue
3. Verify fixes do not break existing tests
4. Re-run linting and type checking
5. Commit fixes

**Commands**:
```bash
# After fixes:
ng lint
ng build --configuration=production

git add -u
git commit -m "fix(user-profile): address code review feedback

- Replace manual subscription with async pipe in template
- Add trackBy function to *ngFor directive
- Fix potential memory leak in observable subscription"
```

**Then**: Return to Step 5 to re-run quality gates

---

### Step 8: Run E2E Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# E2E tests with Cypress:
# With Docker:
docker-compose exec frontend npx cypress run --headless

# Without Docker:
npx cypress run --headless

# E2E tests with Playwright:
# With Docker:
docker-compose exec frontend npx playwright test

# Without Docker:
npx playwright test

# Production build verification:
# With Docker:
docker-compose exec frontend ng build --configuration=production

# Without Docker:
ng build --configuration=production
```

**Pass Criteria**:
- All E2E tests pass
- Production build succeeds with no errors
- Bundle sizes within limits configured in `angular.json` budgets

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes angular-developer to fix (Step 8b)
- Returns to Step 8 after fix

---

### Step 9: Push to Feature Branch

**Agent**: angular-developer

**Commands**:
```bash
# Push feature branch to remote
git push origin feature/feature-name

# Verify push succeeded
git log origin/feature/feature-name --oneline -5
```

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

**Commands**:
```bash
# Pull latest and merge base branch
git fetch origin
git merge origin/<base-branch>

# After conflict resolution - verify build still passes:
ng build --configuration=production
ng test --watch=false

# Push after conflict resolution:
git push origin HEAD --force-with-lease
```

**On Fail**:
- Complex conflicts require manual resolution
- Orchestrator alerts developer to resolve manually
- Returns to Step 10 after manual resolution

---

### Step 11: Final Integration Test ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# Full unit test suite after base branch merged
ng test --watch=false --code-coverage --no-progress

# E2E tests:
# With Docker:
docker-compose exec frontend npx cypress run --headless

# Without Docker:
npx cypress run --headless

# Production build verification:
ng build --configuration=production
```

**Pass Criteria**:
- All unit tests pass
- All E2E tests pass
- Production build succeeds
- Coverage maintained at ≥ 80%

**On Fail** (Step 11b):
- angular-developer fixes regressions introduced by base branch merge
- Returns to Step 11 after fix

---

### Step 12: Merge to Base Branch ⚠️ FINAL

**Agent**: worktree-manager

**Action**: Merge feature branch into base branch and push

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

### Step 13: Cleanup Worktree

**Agent**: worktree-manager

**Actions**:
1. Delete worktree
2. Update registry

*(Docker projects only)* Also stops and removes Docker containers, and optionally cleans up images.

**Commands**:
```bash
# Agent runs:
python scripts/worktree_cleanup.py <worktree-id>
```

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources
- Removes containers, images
- Ensures clean state

---

## Workflow Variants

### Standard Workflow (11 steps)
**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13
**Use For**: Regular features (80% of work)
**Note**: Skips E2E tests (Step 8) — use when existing E2E coverage is sufficient

### Full Workflow (13 steps)
**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13
**Use For**: New components, services, routes, or complex features
**Note**: Includes all quality gates including E2E

### Hotfix Workflow (9 steps)
**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13
**Use For**: Production bugs, urgent fixes
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)
**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13
**Use For**: Adding tests to existing code, improving coverage

### Docs-Only Workflow (5 steps)
**Steps**: 1 → 2 → 9 → 12 → 13
**Use For**: Documentation changes only

---

## Angular Development Best Practices

### DO

✅ Use standalone components (Angular 14+)
✅ Use TypeScript strict mode
✅ Implement OnPush change detection
✅ Use RxJS operators properly (takeUntil, async pipe)
✅ Follow Angular style guide naming conventions
✅ Use dependency injection with `inject()` function
✅ Write comprehensive Jasmine tests
✅ Implement proper ARIA accessibility
✅ Use signals for reactive state (Angular 16+)
✅ Unsubscribe from observables in OnDestroy

### DON'T

❌ Subscribe in templates without the async pipe
❌ Ignore memory leaks from unsubscribed observables
❌ Skip error handling in HTTP calls
❌ Ignore ESLint warnings
❌ Use `any` type
❌ Mutate state directly (use immutable patterns)
❌ Skip unit tests
❌ Create circular dependencies between modules
❌ Hardcode configuration values — use environment files
❌ Forget to implement OnDestroy when subscribing manually

---

## Resources

- [Angular Development Guide](../.claude/ANGULAR_GUIDE.md) - Angular coding standards
- [Testing Guide](TESTING_GUIDE.md) - Jasmine/Karma practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Container setup *(Docker projects only)*
- [Angular Documentation](https://angular.io/) - Official Angular docs
- [RxJS Documentation](https://rxjs.dev/) - Reactive programming guide

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
