# Frontend React Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - React Frontend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **React/Next.js frontend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Jest + React Testing Library)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

---

## Workflow Architecture

### Core Principle

**Isolated, Test-Driven Quality with Automated Gates**

Every frontend feature:
1. Gets its own **isolated worktree** (with Docker environment for Docker projects)
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All Jest tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by frontend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents for React Frontend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **react-frontend-dev** | **Developer** | **Frontend** | **Implement React/Next.js features** | sonnet |
| **react-test-specialist** | **Tester** | **Frontend** | **Write React tests** | sonnet |
| **frontend-code-reviewer** | **Reviewer** | **Frontend** | **Review frontend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step React Frontend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  react-frontend-dev                 → Implement React/Next.js feature
Step 3:  react-test-specialist              → Write Jest + RTL tests
Step 4:  react-frontend-dev                 → Commit code + tests
Step 5:  integration-tester                 → Run Jest unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  frontend-code-reviewer             → Review code [GATE]
Step 7:  react-frontend-dev                 → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  react-frontend-dev                 → Push to feature branch
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
- ✅ New UI components or major features
- ✅ State management architecture
- ✅ Complex features with multiple components
- ✅ Major refactoring

**When to Skip**:
- ❌ Bug fixes
- ❌ Minor UI tweaks
- ❌ Simple component changes

**Agent**: software-architect (opus model)

**Output**: Architecture design document with:
- Context and requirements
- Proposed React component structure
- State management approach (Context, Zustand, Redux)
- Component composition design
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

> *(Docker projects only)* Docker containers start with unique ports, providing a completely isolated React development environment — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Feature

**Agent**: react-frontend-dev

**Responsibilities**:
- Write clean, maintainable React code
- Follow React best practices
- Use TypeScript for type safety
- Write JSDoc comments
- Follow Next.js patterns (Server/Client Components, routing)
- Use hooks appropriately
- Handle errors gracefully
- Place scripts in `scripts/` folder

**React-Specific Patterns**:
```typescript
// React component with TypeScript and hooks
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { UserService } from '@/services/user.service';
import { CreateUserData, User } from '@/types/user';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

interface UserFormProps {
  onSuccess?: (user: User) => void;
  onError?: (error: Error) => void;
}

export function UserForm({ onSuccess, onError }: UserFormProps): JSX.Element {
  const router = useRouter();
  const [formData, setFormData] = useState<CreateUserData>({
    email: '',
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const user = await UserService.createUser(formData);
      toast.success('User created successfully!');
      onSuccess?.(user);
      router.push('/users');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create user';
      toast.error(message);
      onError?.(error as Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" aria-label="Create user form">
      <div>
        <label htmlFor="email">Email</label>
        <Input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
          aria-invalid={!!errors.email}
          disabled={loading}
        />
        {errors.email && <p role="alert">{errors.email}</p>}
      </div>
      <Button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create User'}
      </Button>
    </form>
  );
}
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: react-test-specialist

**Responsibilities**:
- Analyze React implementation
- Design test scenarios (user interactions, error states, accessibility)
- Implement Jest + React Testing Library tests
- Target 80%+ coverage
- Document test purpose

**React Test Structure** (Jest + React Testing Library):
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserForm } from './UserForm';
import { UserService } from '@/services/user.service';
import { toast } from 'sonner';

jest.mock('@/services/user.service');
jest.mock('sonner');
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() })
}));

describe('UserForm', () => {
  const mockOnSuccess = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render all form fields', () => {
      render(<UserForm />);

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create user/i })).toBeInTheDocument();
    });

    it('should have accessible form labels', () => {
      render(<UserForm />);
      expect(screen.getByRole('form', { name: /create user form/i })).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should create user successfully', async () => {
      const user = userEvent.setup();
      const mockUser = { id: 1, email: 'test@example.com', username: 'testuser' };

      (UserService.createUser as jest.Mock).mockResolvedValue(mockUser);

      render(<UserForm onSuccess={mockOnSuccess} />);

      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /create user/i }));

      await waitFor(() => {
        expect(UserService.createUser).toHaveBeenCalled();
      });

      expect(toast.success).toHaveBeenCalledWith('User created successfully!');
      expect(mockOnSuccess).toHaveBeenCalledWith(mockUser);
    });

    it('should handle duplicate user error', async () => {
      const user = userEvent.setup();
      const error = new Error('User already exists');

      (UserService.createUser as jest.Mock).mockRejectedValue(error);

      render(<UserForm onError={mockOnError} />);

      await user.type(screen.getByLabelText(/email/i), 'existing@example.com');
      await user.click(screen.getByRole('button', { name: /create user/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('User already exists');
      });

      expect(mockOnError).toHaveBeenCalledWith(error);
    });
  });

  describe('Accessibility', () => {
    it('should announce errors to screen readers', async () => {
      const user = userEvent.setup();
      render(<UserForm />);

      await user.click(screen.getByRole('button', { name: /create user/i }));

      const errorMessages = await screen.findAllByRole('alert');
      expect(errorMessages.length).toBeGreaterThan(0);
    });
  });
});
```

**Test Coverage Requirements**:
- Component rendering: All UI elements
- User interactions: Form filling, button clicks, keyboard navigation
- Validation: All validation rules
- API integration: Success and error cases
- Accessibility: ARIA attributes, screen reader support
- Edge cases: Loading states, disabled states, error recovery

---

### Step 4: Commit Code + Tests

**Agent**: react-frontend-dev

**Commands**:
```bash
# With Docker:
docker-compose exec frontend npm run format
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run type-check
docker-compose exec frontend npm run build

# Without Docker:
npm run format
npm run lint
npm run type-check
npm run build

# Commit
git add .
git commit -m "feat: add user creation form component

- Implement UserForm component with TypeScript
- Add form validation with real-time error feedback
- Add loading states and disabled inputs during submission
- Implement proper error handling with toast notifications
- Add comprehensive Jest + RTL tests
- Ensure ARIA attributes for accessibility
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
docker-compose exec frontend npm test -- --coverage --verbose

# Without Docker:
npm test -- --coverage --verbose
```

**Pass Criteria**:
- All Jest tests pass (0 failures, 0 errors)
- Coverage ≥ 80%
- No critical ESLint errors
- TypeScript compilation succeeds

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes react-frontend-dev to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

---

### Step 6: Code Review ⚠️ GATE

**Agent**: frontend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Accessibility** (ARIA labels, keyboard navigation, screen reader support)
- ✅ **Performance** (memo, useMemo, useCallback, code splitting)
- ✅ **Best Practices** (React patterns, hooks rules, TypeScript usage)
- ✅ **UI/UX** (responsive design, loading states, error messages)
- ✅ **Security** (XSS prevention, input sanitization)
- ✅ **Testing** (comprehensive test coverage, user-centric tests)

**React-Specific Checks**:
- Proper hook usage (no hooks in loops/conditions)
- TypeScript types on all props and state
- Accessibility attributes (ARIA, semantic HTML)
- Error boundaries where needed
- Loading and error states handled
- Responsive design implemented
- No prop drilling (use Context or state management)
- Components properly memoized if needed

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: react-frontend-dev

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-format with Prettier
- Re-lint with ESLint
- Type-check with TypeScript
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# With Docker:
docker-compose exec frontend npm run test:e2e
docker-compose exec frontend npm test -- --testPathPattern=integration
docker-compose exec frontend npm run build

# Without Docker:
npm run test:e2e
npm test -- --testPathPattern=integration
npm run build
```

**Pass Criteria**:
- All E2E tests pass
- App builds successfully
- No console errors
- Visual regression tests pass (if configured)

**On Fail**:
- Workflow BLOCKED
- react-frontend-dev fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: react-frontend-dev

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

**React-Specific Conflict Types**:
- **Simple**: imports, whitespace, formatting → auto-resolve
- **Components**: Different components in same directory → integrate both
- **Styles**: Tailwind class conflicts → merge carefully
- **Logic**: Different implementations → request manual review
- **Package.json**: Dependency conflicts → merge carefully, run npm install
- **Complex**: Fundamental conflicts in component logic → request manual review

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
docker-compose exec frontend npm test -- --coverage
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run type-check
docker-compose exec frontend npm run build

# Without Docker:
npm test -- --coverage
npm run lint
npm run type-check
npm run build
```

**Pass Criteria**:
- All tests pass after merge
- No new linting errors
- Build succeeds

**On Fail**:
- Workflow BLOCKED
- react-frontend-dev fixes merge issues

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

*(Docker projects only)* Also stops and removes Docker containers, and optionally cleans up images.

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_cleanup.sh <worktree-id>
```

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources
- Removes containers, images
- Ensures clean state

---

## Workflow Variants

### Standard Workflow (11 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: Regular React features, components (80% of work)
**Time**: 25-35 minutes
**Cost**: Medium

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New pages, major UI features, architectural changes
**Time**: 35-50 minutes
**Cost**: High

### Hotfix Workflow (9 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: UI bugs, urgent fixes
**Time**: 15-20 minutes
**Cost**: Low
**Note**: Skips test writing (assumes tests exist), skips E2E tests; includes fix loop (Step 7)

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing React code, improving coverage
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

## React Development Best Practices

### DO

✅ Use TypeScript for type safety
✅ Use functional components and hooks
✅ Implement proper accessibility (ARIA, semantic HTML)
✅ Handle loading and error states
✅ Use React Testing Library for user-centric tests
✅ Optimize with memo, useMemo, useCallback
✅ Use proper key props in lists
✅ Keep components small and focused
✅ Use Prettier for code formatting
✅ Test user interactions, not implementation details

### DON'T

❌ Use class components (unless needed for error boundaries)
❌ Ignore accessibility
❌ Skip error handling
❌ Ignore ESLint warnings
❌ Use inline functions in JSX without memoization
❌ Test implementation details
❌ Skip loading states
❌ Hardcode configuration values
❌ Commit without running format/lint
❌ Use index as key in dynamic lists

---

## React Tools and Commands

### Building and Linting
```bash
# With Docker:
docker-compose exec frontend npm install
docker-compose exec frontend npm run build
docker-compose exec frontend npm run format
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run type-check
docker-compose exec frontend npm run dev

# Without Docker:
npm install
npm run build
npm run format
npm run lint
npm run type-check
npm run dev
```

### Testing
```bash
# With Docker:
docker-compose exec frontend npm test
docker-compose exec frontend npm test -- --coverage
docker-compose exec frontend npm test -- UserForm.test.tsx
docker-compose exec frontend npm test -- --watch
docker-compose exec frontend npm run test:e2e

# Without Docker:
npm test
npm test -- --coverage
npm test -- UserForm.test.tsx
npm test -- --watch
npm run test:e2e
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for React errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### Jest Tests Failing

1. Review Jest output for failure details
2. Check mocks are properly configured
3. Verify React Testing Library queries
4. Fix implementation or tests
5. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if React approach is correct
2. Consider architectural review
3. May need to restart with different component structure

### Build Errors

1. Delete .next and node_modules
2. Run npm install
3. With Docker: rebuild the Docker container. Without Docker: rebuild the project.
4. Check for TypeScript errors

---

## Resources

- [React Development Guide](../.claude/REACT_GUIDE.md) - React coding standards
- [Testing Guide](TESTING_GUIDE.md) - Jest + RTL practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [React Documentation](https://react.dev/) - Official React docs
- [Next.js Documentation](https://nextjs.org/docs) - Next.js framework
- [React Testing Library](https://testing-library.com/react) - Testing library docs

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
