# Frontend Vue Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Vue Frontend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Vue.js/Nuxt frontend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Vitest + Vue Test Utils)
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
1. **Unit Test Gate** (Step 5) - All Vitest tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by frontend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with base branch merged must pass

---

## Agent System

**Specialized Agents for Vue Frontend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **vue-developer** | **Developer** | **Frontend** | **Implement Vue/Nuxt features** | sonnet |
| **vue-test-specialist** | **Tester** | **Frontend** | **Write Vitest + VTU tests** | sonnet |
| **frontend-code-reviewer** | **Reviewer** | **Frontend** | **Review frontend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Vue Frontend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER/ON-FAILURE] docker-debugger → Debug setup issues
Step 2:  vue-developer                      → Implement Vue/Nuxt feature
Step 3:  vue-test-specialist                → Write Vitest + VTU tests
Step 4:  vue-developer                      → Commit code + tests
Step 5:  integration-tester                 → Run Vitest unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  frontend-code-reviewer             → Review code [GATE]
Step 7:  vue-developer                      → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  vue-developer                      → Push to feature branch
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
- ✅ New Vue components or major features
- ✅ State management architecture (Pinia stores)
- ✅ Complex features with multiple components
- ✅ Major refactoring

**When to Skip**:
- ❌ Bug fixes
- ❌ Minor UI tweaks
- ❌ Simple component changes

**Agent**: software-architect (opus model)

**Output**: Architecture design document with:
- Context and requirements
- Proposed Vue component structure
- Pinia store design
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

> *(Docker projects only)* Docker containers start with unique ports, providing a completely isolated Vue development environment — no shared resources.

**On Failure** (Step 1b) *(Docker projects only)*:
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed

---

### Step 2: Implement Feature

**Agent**: vue-developer

**Responsibilities**:
- Write clean, maintainable Vue code
- Follow Vue 3 Composition API patterns
- Use TypeScript for type safety
- Write clear comments
- Follow Nuxt conventions (pages, layouts, composables)
- Use composables for reusable logic
- Handle errors gracefully
- Place scripts in `scripts/` folder

**Vue-Specific Patterns**:
```vue
<!-- UserForm.vue - Vue 3 Composition API with TypeScript -->
<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useToast } from '@/composables/useToast';
import type { CreateUserData, User } from '@/types/user';

interface Props {
  onSuccess?: (user: User) => void;
  onError?: (error: Error) => void;
}

const props = defineProps<Props>();

const router = useRouter();
const userStore = useUserStore();
const { showSuccess, showError } = useToast();

const formData = reactive<CreateUserData>({
  email: '',
  username: '',
  password: ''
});

const loading = ref(false);
const errors = ref<Record<string, string>>({});

const isFormValid = computed(() =>
  formData.email && formData.username && formData.password.length >= 8
);

const handleSubmit = async () => {
  loading.value = true;
  errors.value = {};

  try {
    const user = await userStore.createUser(formData);
    showSuccess('User created successfully!');
    props.onSuccess?.(user);
    await router.push('/users');
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to create user';
    showError(message);
    errors.value = { submit: message };
    props.onError?.(error as Error);
  } finally {
    loading.value = false;
  }
};

defineExpose({ resetForm: () => {
  formData.email = '';
  formData.username = '';
  formData.password = '';
  errors.value = {};
} });
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-4" aria-label="Create user form">
    <div>
      <label for="email">Email</label>
      <input
        id="email"
        v-model="formData.email"
        type="email"
        :aria-invalid="!!errors.email"
        :disabled="loading"
      />
      <p v-if="errors.email" id="email-error" role="alert">{{ errors.email }}</p>
    </div>

    <div v-if="errors.submit" role="alert">{{ errors.submit }}</div>

    <button type="submit" :disabled="loading || !isFormValid">
      {{ loading ? 'Creating...' : 'Create User' }}
    </button>
  </form>
</template>
```

**DO NOT commit yet** - tests need to be written first

---

### Step 3: Write Tests

**Agent**: vue-test-specialist

**Responsibilities**:
- Analyze Vue implementation
- Design test scenarios (user interactions, error states, accessibility)
- Implement Vitest + Vue Test Utils tests
- Target 80%+ coverage
- Document test purpose

**Vue Test Structure** (Vitest + Vue Test Utils):
```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import UserForm from './UserForm.vue';
import { useUserStore } from '@/stores/user';
import type { User } from '@/types/user';

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() })
}));

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn()
  })
}));

describe('UserForm.vue', () => {
  let wrapper: VueWrapper<any>;
  let userStore: ReturnType<typeof useUserStore>;

  beforeEach(() => {
    setActivePinia(createPinia());
    userStore = useUserStore();
  });

  afterEach(() => {
    wrapper?.unmount();
  });

  const mountComponent = (props = {}) =>
    mount(UserForm, {
      global: { plugins: [createPinia()] },
      props
    });

  describe('Rendering', () => {
    it('should render all form fields', () => {
      wrapper = mountComponent();

      expect(wrapper.find('label[for="email"]').exists()).toBe(true);
      expect(wrapper.find('button[type="submit"]').text()).toBe('Create User');
    });

    it('should have accessible form structure', () => {
      wrapper = mountComponent();
      expect(wrapper.find('form').attributes('aria-label')).toBe('Create user form');
    });
  });

  describe('Form Submission', () => {
    it('should create user successfully', async () => {
      const mockUser: User = { id: 1, email: 'test@example.com', username: 'testuser' };
      vi.spyOn(userStore, 'createUser').mockResolvedValue(mockUser);

      const onSuccess = vi.fn();
      wrapper = mountComponent({ onSuccess });

      await wrapper.find('#email').setValue('test@example.com');
      await wrapper.find('#username').setValue('testuser');
      await wrapper.find('#password').setValue('password123');
      await wrapper.find('form').trigger('submit.prevent');
      await wrapper.vm.$nextTick();

      expect(userStore.createUser).toHaveBeenCalled();
      expect(onSuccess).toHaveBeenCalledWith(mockUser);
    });

    it('should handle duplicate user error', async () => {
      const error = new Error('User already exists');
      vi.spyOn(userStore, 'createUser').mockRejectedValue(error);

      const onError = vi.fn();
      wrapper = mountComponent({ onError });

      await wrapper.find('#email').setValue('existing@example.com');
      await wrapper.find('#username').setValue('testuser');
      await wrapper.find('#password').setValue('password123');
      await wrapper.find('form').trigger('submit.prevent');
      await wrapper.vm.$nextTick();

      expect(onError).toHaveBeenCalledWith(error);
      expect(wrapper.text()).toContain('User already exists');
    });

    it('should disable form during submission', async () => {
      vi.spyOn(userStore, 'createUser').mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      wrapper = mountComponent();

      await wrapper.find('#email').setValue('test@example.com');
      await wrapper.find('#username').setValue('testuser');
      await wrapper.find('#password').setValue('password123');
      await wrapper.find('form').trigger('submit.prevent');

      expect(wrapper.find('button[type="submit"]').text()).toBe('Creating...');
    });
  });

  describe('Accessibility', () => {
    it('should announce errors with role="alert"', async () => {
      wrapper = mountComponent();
      await wrapper.find('form').trigger('submit.prevent');

      const alerts = wrapper.findAll('[role="alert"]');
      expect(alerts.length).toBeGreaterThan(0);
    });
  });
});
```

**Test Coverage Requirements**:
- Component rendering: All UI elements
- User interactions: Form filling, button clicks, keyboard navigation
- Validation: All validation rules
- Pinia store integration: Success and error cases
- Accessibility: ARIA attributes, screen reader support
- Edge cases: Loading states, disabled states, error recovery

---

### Step 4: Commit Code + Tests

**Agent**: vue-developer

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

- Implement UserForm.vue with Composition API and TypeScript
- Add form validation with real-time error feedback
- Add loading states and disabled inputs during submission
- Implement proper error handling with toast notifications
- Add comprehensive Vitest + VTU tests
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
docker-compose exec frontend npx vitest run --coverage

# Without Docker:
npx vitest run --coverage
```

**Pass Criteria**:
- All Vitest tests pass (0 failures)
- Coverage ≥ 80%
- No critical ESLint errors
- TypeScript compilation succeeds

**On Fail**:
- Workflow BLOCKED
- Orchestrator invokes vue-developer to fix
- Returns to Step 5 after fix

**On Docker Failure** (Step 5b) *(Docker projects only)*:
- docker-debugger diagnoses container issues
- Fixes and retries test execution

---

### Step 6: Code Review ⚠️ GATE

**Agent**: frontend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Accessibility** (ARIA labels, keyboard navigation, screen reader support)
- ✅ **Performance** (v-memo, lazy loading, avoiding watchers where computed suffices)
- ✅ **Best Practices** (Composition API, ref/reactive/computed usage, no prop mutation)
- ✅ **UI/UX** (responsive design, loading states, error messages)
- ✅ **Security** (XSS prevention, v-html risks)
- ✅ **Testing** (comprehensive test coverage)

**Vue-Specific Checks**:
- Composition API used correctly (`<script setup>`)
- TypeScript types on all props and state
- No direct prop mutation
- Pinia store patterns followed correctly
- Composables used for reusable logic
- No memory leaks (cleared intervals, removed event listeners)
- Accessibility attributes on interactive elements

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: vue-developer

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
docker-compose exec frontend nuxt build

# Without Docker:
npm run test:e2e
nuxt build
```

**Pass Criteria**:
- All E2E tests pass
- App builds successfully
- No console errors

**On Fail**:
- Workflow BLOCKED
- vue-developer fixes issues
- May loop back to Step 5-6 if code changes needed

**On Docker Failure** (Step 8b) *(Docker projects only)*:
- docker-debugger diagnoses E2E test issues
- Fixes and retries

---

### Step 9: Push Feature Branch

**Agent**: vue-developer

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

**Vue-Specific Conflict Types**:
- **Simple**: imports, whitespace, formatting → auto-resolve
- **Components**: Different components in same directory → integrate both
- **Stores**: Pinia store changes → integrate both carefully
- **Logic**: Different component implementations → request manual review
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
docker-compose exec frontend npx vitest run --coverage
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run type-check
docker-compose exec frontend nuxt build

# Without Docker:
npx vitest run --coverage
npm run lint
npm run type-check
nuxt build
```

**Pass Criteria**:
- All tests pass after merge
- No new linting errors
- Build succeeds

**On Fail**:
- Workflow BLOCKED
- vue-developer fixes merge issues

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

**Use For**: Regular Vue features, components (80% of work)
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

**Use For**: Adding tests to existing Vue code, improving coverage
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

## Vue Development Best Practices

### DO

✅ Use Composition API for new components
✅ Use TypeScript for type safety
✅ Use `<script setup>` syntax
✅ Implement proper accessibility (ARIA, semantic HTML)
✅ Use Pinia for state management
✅ Use composables for reusable logic
✅ Use computed for derived state
✅ Keep components small and focused
✅ Use Prettier for code formatting
✅ Test user interactions with Vue Test Utils

### DON'T

❌ Use Options API for new code
❌ Ignore accessibility
❌ Skip error handling
❌ Ignore ESLint warnings
❌ Mutate props directly
❌ Use `this` in Composition API
❌ Skip loading states
❌ Hardcode configuration values
❌ Commit without running format/lint
❌ Create memory leaks with uncleared intervals/listeners

---

## Vue Tools and Commands

### Building and Linting
```bash
# With Docker:
docker-compose exec frontend npm install
docker-compose exec frontend nuxt build
docker-compose exec frontend npm run format
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run type-check
docker-compose exec frontend npm run dev

# Without Docker:
npm install
nuxt build
npm run format
npm run lint
npm run type-check
npm run dev
```

### Testing
```bash
# With Docker:
docker-compose exec frontend npx vitest run
docker-compose exec frontend npx vitest run --coverage
docker-compose exec frontend npx vitest run UserForm.test.ts
docker-compose exec frontend npx vitest

# Without Docker:
npx vitest run
npx vitest run --coverage
npx vitest run UserForm.test.ts
npx vitest
```

---

## Troubleshooting

### Workflow Stuck

1. **Identify which step failed**
2. **Check agent output** for Vue errors
3. **Fix the issue** manually if needed
4. **Resume workflow** from failed step

### Vitest Tests Failing

1. Review test output for failure details
2. Check mocks are properly configured
3. Verify Pinia store setup in tests
4. Fix implementation or tests
5. Re-run from Step 5

### Review Rejected Multiple Times

1. Discuss with team if Vue approach is correct
2. Consider architectural review
3. May need to restart with different component structure

### Build Errors

1. Delete .nuxt and node_modules
2. Run npm install
3. With Docker: rebuild the Docker container. Without Docker: rebuild the project.
4. Check for TypeScript errors

---

## Resources

- [Vue Development Guide](../.claude/VUE_GUIDE.md) - Vue coding standards
- [Testing Guide](TESTING_GUIDE.md) - Vitest + VTU practices
- [Docker Guide](../.claude/DOCKER_GUIDE.md) - Docker commands *(Docker projects only)*
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [Vue 3 Documentation](https://vuejs.org/) - Official Vue docs
- [Nuxt Documentation](https://nuxt.com/) - Nuxt framework
- [Vue Test Utils](https://test-utils.vuejs.org/) - Testing utilities

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
