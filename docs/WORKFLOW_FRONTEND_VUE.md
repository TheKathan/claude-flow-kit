# Frontend Vue Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Vue Frontend Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Vue.js/Nuxt frontend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree{{#if USES_DOCKER}} + Docker environment{{/if}})
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
1. Gets its own **isolated worktree{{#if USES_DOCKER}} + Docker environment{{/if}}**
2. Goes through **mandatory quality gates** before being pushed
3. Has **conflicts resolved automatically** before merge
4. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - All Vitest tests must pass with 80%+ coverage
2. **Code Review Gate** (Step 6) - Code must be approved by frontend reviewer
3. **Integration Test Gate** (Step 8) - End-to-end tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final tests with {{MAIN_BRANCH}} merged must pass

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
{{#if USES_DOCKER}}| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** | sonnet |{{/if}}
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Vue Frontend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree{{#if USES_DOCKER}} + Docker{{/if}}
{{#if USES_DOCKER}}Step 1b: [ON-FAILURE] docker-debugger       → Debug setup issues{{/if}}
Step 2:  vue-developer                      → Implement Vue/Nuxt feature
Step 3:  vue-test-specialist                → Write Vitest + VTU tests
Step 4:  vue-developer                      → Commit code + tests
Step 5:  integration-tester                 → Run Vitest unit tests [GATE]
{{#if USES_DOCKER}}Step 5b: [ON-FAILURE] docker-debugger       → Debug test issues{{/if}}
Step 6:  frontend-code-reviewer             → Review code [GATE]
Step 7:  vue-developer                      → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
{{#if USES_DOCKER}}Step 8b: [ON-FAILURE] docker-debugger       → Debug E2E issues{{/if}}
Step 9:  vue-developer                      → Push to feature branch
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

**Action**: Create isolated worktree{{#if USES_DOCKER}} with Docker environment{{/if}}

**Commands**:
```bash
# Agent runs:
bash scripts/worktree_create.sh feature-name "Feature description"
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`
{{#if USES_DOCKER}}- Docker container running with unique port
- Completely isolated Vue development environment
- No shared resources with main branch{{/if}}

{{#if USES_DOCKER}}**On Failure** (Step 1b):
- docker-debugger diagnoses port conflicts, container issues
- Fixes automatically if possible
- Reports if manual intervention needed
{{/if}}

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

// Form state
const formData = reactive<CreateUserData>({
  email: '',
  username: '',
  password: ''
});

const loading = ref(false);
const errors = ref<Record<string, string>>({});

// Validation rules
const emailPattern = /\S+@\S+\.\S+/;

const isFormValid = computed(() => {
  return formData.email &&
         emailPattern.test(formData.email) &&
         formData.username &&
         formData.password.length >= 8;
});

/**
 * Validate a specific field
 */
const validateField = (field: keyof CreateUserData): string | null => {
  switch (field) {
    case 'email':
      if (!formData.email) return 'Email is required';
      if (!emailPattern.test(formData.email)) return 'Email is invalid';
      return null;
    case 'username':
      if (!formData.username) return 'Username is required';
      return null;
    case 'password':
      if (!formData.password) return 'Password is required';
      if (formData.password.length < 8) return 'Password must be at least 8 characters';
      return null;
    default:
      return null;
  }
};

/**
 * Validate entire form
 */
const validateForm = (): boolean => {
  const newErrors: Record<string, string> = {};

  (['email', 'username', 'password'] as const).forEach(field => {
    const error = validateField(field);
    if (error) newErrors[field] = error;
  });

  errors.value = newErrors;
  return Object.keys(newErrors).length === 0;
};

/**
 * Clear error for a specific field
 */
const clearError = (field: string) => {
  const newErrors = { ...errors.value };
  delete newErrors[field];
  errors.value = newErrors;
};

/**
 * Handle input change
 */
const handleInput = (field: keyof CreateUserData) => {
  clearError(field);
};

/**
 * Handle form submission
 */
const handleSubmit = async () => {
  if (!validateForm()) return;

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

/**
 * Reset form
 */
const resetForm = () => {
  formData.email = '';
  formData.username = '';
  formData.password = '';
  errors.value = {};
};

defineExpose({ resetForm });
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-4" aria-label="Create user form">
    <!-- Email Field -->
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700">
        Email
      </label>
      <input
        id="email"
        v-model="formData.email"
        type="email"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.email }"
        :aria-invalid="!!errors.email"
        :aria-describedby="errors.email ? 'email-error' : undefined"
        :disabled="loading"
        @input="handleInput('email')"
      />
      <p
        v-if="errors.email"
        id="email-error"
        class="mt-1 text-sm text-red-600"
        role="alert"
      >
        {{ errors.email }}
      </p>
    </div>

    <!-- Username Field -->
    <div>
      <label for="username" class="block text-sm font-medium text-gray-700">
        Username
      </label>
      <input
        id="username"
        v-model="formData.username"
        type="text"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.username }"
        :aria-invalid="!!errors.username"
        :aria-describedby="errors.username ? 'username-error' : undefined"
        :disabled="loading"
        @input="handleInput('username')"
      />
      <p
        v-if="errors.username"
        id="username-error"
        class="mt-1 text-sm text-red-600"
        role="alert"
      >
        {{ errors.username }}
      </p>
    </div>

    <!-- Password Field -->
    <div>
      <label for="password" class="block text-sm font-medium text-gray-700">
        Password
      </label>
      <input
        id="password"
        v-model="formData.password"
        type="password"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        :class="{ 'border-red-500': errors.password }"
        :aria-invalid="!!errors.password"
        :aria-describedby="errors.password ? 'password-error' : undefined"
        :disabled="loading"
        @input="handleInput('password')"
      />
      <p
        v-if="errors.password"
        id="password-error"
        class="mt-1 text-sm text-red-600"
        role="alert"
      >
        {{ errors.password }}
      </p>
    </div>

    <!-- Submit Error -->
    <div v-if="errors.submit" class="text-sm text-red-600" role="alert">
      {{ errors.submit }}
    </div>

    <!-- Submit Button -->
    <button
      type="submit"
      class="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:bg-gray-400"
      :disabled="loading || !isFormValid"
    >
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
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import UserForm from './UserForm.vue';
import { useUserStore } from '@/stores/user';
import type { User } from '@/types/user';

// Mock router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}));

// Mock toast
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

  const mountComponent = (props = {}) => {
    return mount(UserForm, {
      global: {
        plugins: [createPinia()]
      },
      props
    });
  };

  describe('Rendering', () => {
    it('should render all form fields', () => {
      wrapper = mountComponent();

      expect(wrapper.find('label[for="email"]').text()).toBe('Email');
      expect(wrapper.find('label[for="username"]').text()).toBe('Username');
      expect(wrapper.find('label[for="password"]').text()).toBe('Password');
      expect(wrapper.find('button[type="submit"]').text()).toBe('Create User');
    });

    it('should have accessible form structure', () => {
      wrapper = mountComponent();

      const form = wrapper.find('form');
      expect(form.attributes('aria-label')).toBe('Create user form');
    });
  });

  describe('Form Validation', () => {
    it('should show error for invalid email', async () => {
      wrapper = mountComponent();

      const emailInput = wrapper.find('#email');
      await emailInput.setValue('invalid-email');
      await wrapper.find('form').trigger('submit.prevent');

      expect(wrapper.find('#email-error').text()).toContain('Email is invalid');
      expect(userStore.createUser).not.toHaveBeenCalled();
    });

    it('should show error for missing username', async () => {
      wrapper = mountComponent();

      await wrapper.find('#email').setValue('test@example.com');
      await wrapper.find('#password').setValue('password123');
      await wrapper.find('form').trigger('submit.prevent');

      expect(wrapper.find('#username-error').text()).toContain('Username is required');
    });

    it('should show error for short password', async () => {
      wrapper = mountComponent();

      await wrapper.find('#password').setValue('short');
      await wrapper.find('form').trigger('submit.prevent');

      expect(wrapper.find('#password-error').text()).toContain('at least 8 characters');
    });

    it('should clear error when field is corrected', async () => {
      wrapper = mountComponent();

      // Trigger error
      await wrapper.find('form').trigger('submit.prevent');
      expect(wrapper.find('#email-error').exists()).toBe(true);

      // Fix error
      await wrapper.find('#email').setValue('test@example.com');
      await wrapper.find('#email').trigger('input');

      expect(wrapper.find('#email-error').exists()).toBe(false);
    });

    it('should disable submit button when form is invalid', async () => {
      wrapper = mountComponent();

      const submitButton = wrapper.find('button[type="submit"]');
      expect(submitButton.attributes('disabled')).toBeDefined();

      // Fill form
      await wrapper.find('#email').setValue('test@example.com');
      await wrapper.find('#username').setValue('testuser');
      await wrapper.find('#password').setValue('password123');

      expect(submitButton.attributes('disabled')).toBeUndefined();
    });
  });

  describe('Form Submission', () => {
    it('should create user successfully', async () => {
      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser'
      };

      vi.spyOn(userStore, 'createUser').mockResolvedValue(mockUser);

      const onSuccess = vi.fn();
      wrapper = mountComponent({ onSuccess });

      await wrapper.find('#email').setValue('test@example.com');
      await wrapper.find('#username').setValue('testuser');
      await wrapper.find('#password').setValue('password123');
      await wrapper.find('form').trigger('submit.prevent');

      await wrapper.vm.$nextTick();

      expect(userStore.createUser).toHaveBeenCalledWith({
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123'
      });
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

      expect(wrapper.find('#email').attributes('disabled')).toBeDefined();
      expect(wrapper.find('#username').attributes('disabled')).toBeDefined();
      expect(wrapper.find('#password').attributes('disabled')).toBeDefined();
      expect(wrapper.find('button[type="submit"]').text()).toBe('Creating...');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes for errors', async () => {
      wrapper = mountComponent();

      await wrapper.find('form').trigger('submit.prevent');

      const emailInput = wrapper.find('#email');
      expect(emailInput.attributes('aria-invalid')).toBe('true');
      expect(emailInput.attributes('aria-describedby')).toBe('email-error');
    });

    it('should announce errors with role="alert"', async () => {
      wrapper = mountComponent();

      await wrapper.find('form').trigger('submit.prevent');

      const errors = wrapper.findAll('[role="alert"]');
      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('Exposed Methods', () => {
    it('should expose resetForm method', () => {
      wrapper = mountComponent();

      expect(wrapper.vm.resetForm).toBeDefined();
    });

    it('should reset form data when resetForm is called', async () => {
      wrapper = mountComponent();

      await wrapper.find('#email').setValue('test@example.com');
      await wrapper.find('#username').setValue('testuser');
      await wrapper.find('#password').setValue('password123');

      wrapper.vm.resetForm();
      await wrapper.vm.$nextTick();

      expect((wrapper.find('#email').element as HTMLInputElement).value).toBe('');
      expect((wrapper.find('#username').element as HTMLInputElement).value).toBe('');
      expect((wrapper.find('#password').element as HTMLInputElement).value).toBe('');
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
{{#if USES_DOCKER}}# Run Prettier formatter
docker-compose exec frontend npm run format

# Run ESLint
docker-compose exec frontend npm run lint

# Type check with TypeScript
docker-compose exec frontend npm run type-check

# Build
docker-compose exec frontend npm run build
{{else}}# Run Prettier formatter
npm run format

# Run ESLint
npm run lint

# Type check with TypeScript
npm run type-check

# Build
npm run build
{{/if}}

# Commit
git add .
git commit -m "feat: add user creation form component

- Implement UserForm.vue with Composition API and TypeScript
- Add form validation with real-time error feedback
- Add loading states and disabled inputs during submission
- Implement proper error handling with toast notifications
- Add comprehensive Vitest + VTU tests
- Ensure ARIA attributes for accessibility
- Test coverage: 85%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
{{#if USES_DOCKER}}# Run Vitest tests with coverage
docker-compose exec frontend npm test -- --coverage

# Check coverage report
docker-compose exec frontend cat coverage/index.html
{{else}}# Run Vitest tests with coverage
npm test -- --coverage

# Check coverage report
cat coverage/index.html
{{/if}}
```

**Pass Criteria**:
- All Vitest tests pass (0 failures)
- Coverage ≥ 80%
- No critical ESLint errors
- TypeScript compilation succeeds

---

### Step 6-13: [Same structure as React workflow]

Continue with same quality gates and steps...

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

## Resources

- [Vue Development Guide](../.claude/VUE_GUIDE.md) - Vue coding standards
- [Testing Guide](TESTING_GUIDE.md) - Vitest + VTU practices
- [Vue 3 Documentation](https://vuejs.org/) - Official Vue docs
- [Nuxt Documentation](https://nuxt.com/) - Nuxt framework
- [Vue Test Utils](https://test-utils.vuejs.org/) - Testing utilities

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
