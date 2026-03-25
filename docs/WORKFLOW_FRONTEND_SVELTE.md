# Frontend Svelte Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Svelte Frontend Worktree-Based Workflow

---

## Overview

This guide covers the 14-step worktree-based workflow for **Svelte/SvelteKit frontend development**. This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree, with Docker environment for Docker projects)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory with Vitest + @testing-library/svelte)
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

**Specialized Agents for Svelte Frontend**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **svelte-developer** | **Developer** | **Frontend** | **Implement Svelte/SvelteKit features** | sonnet |
| **svelte-test-specialist** | **Tester** | **Frontend** | **Write Vitest + @testing-library/svelte tests** | sonnet |
| **frontend-code-reviewer** | **Reviewer** | **Frontend** | **Review frontend code** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **docker-debugger** | **Debugger** | **All** | **Diagnose and fix Docker issues** *(Docker projects only)* | sonnet |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 14-Step Svelte Frontend Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 1b: [DOCKER ONLY] docker-debugger      → Setup Docker environment
Step 2:  svelte-developer                   → Implement Svelte/SvelteKit feature
Step 3:  svelte-test-specialist             → Write Vitest + @testing-library/svelte tests
Step 4:  svelte-developer                   → Commit code + tests
Step 5:  integration-tester                 → Run Vitest unit tests [GATE]
Step 5b: [DOCKER/ON-FAILURE] docker-debugger → Debug test issues
Step 6:  frontend-code-reviewer             → Review code [GATE]
Step 7:  svelte-developer                   → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E tests [GATE]
Step 8b: [DOCKER/ON-FAILURE] docker-debugger → Debug E2E issues
Step 9:  svelte-developer                   → Push to feature branch
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
- ✅ New SvelteKit routes or major page features
- ✅ Complex state management across multiple stores
- ✅ Major refactoring
- ✅ New API route design

**When to Skip**:
- ❌ Bug fixes
- ❌ Minor UI tweaks
- ❌ Simple component changes

**Agent**: software-architect (opus model)

**Output**: Architecture design document with:
- Component hierarchy
- Store design
- SvelteKit routing plan
- Load function / form action design
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

> *(Docker projects only)* After the worktree is created, proceed to Step 1b where docker-debugger sets up the Docker environment.

**Step 1b: Setup Docker Environment** *(Docker projects only)*:
- docker-debugger creates isolated Docker environment for this worktree
- Configures unique port mappings to avoid conflicts
- Starts containers and verifies all services are healthy
- Reports access URLs and port mappings

---

### Step 2: Implement Feature

**Agent**: svelte-developer

**Responsibilities**:
- Write clean, idiomatic Svelte 5 code with runes
- Use TypeScript strict mode throughout
- Follow SvelteKit conventions (load functions, form actions, API routes)
- Build accessible components with semantic HTML
- Use Svelte stores for cross-component state
- Place scripts in `scripts/` folder

**Svelte 5 Component Pattern**:
```svelte
<script lang="ts">
  interface Props {
    categoryId: number
    pageSize?: number
  }

  let { categoryId, pageSize = 20 }: Props = $props()

  let searchQuery = $state('')
  let products = $state<Product[]>([])

  let filtered = $derived(
    products.filter(p =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  )

  $effect(() => {
    fetchProducts(categoryId).then(data => { products = data })
  })
</script>

<input bind:value={searchQuery} placeholder="Search..." />
<ul>
  {#each filtered as product (product.id)}
    <li>{product.name}</li>
  {/each}
</ul>
```

**DO NOT commit yet** — tests need to be written first

---

### Step 3: Write Tests

**Agent**: svelte-test-specialist

**Responsibilities**:
- Analyze Svelte implementation
- Design test scenarios (happy path, errors, edge cases, accessibility)
- Implement Vitest tests with @testing-library/svelte
- Target 80%+ coverage

**Test Structure**:
```typescript
import { render, screen } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import ProductList from '$lib/components/ProductList.svelte'

describe('ProductList', () => {
  it('renders product names', () => {
    render(ProductList, { props: { products: [{ id: 1, name: 'Widget' }], categoryId: 1 } })
    expect(screen.getByText('Widget')).toBeInTheDocument()
  })

  it('filters by search query', async () => {
    const user = userEvent.setup()
    render(ProductList, {
      props: { products: [{ id: 1, name: 'Widget' }, { id: 2, name: 'Gadget' }], categoryId: 1 }
    })
    await user.type(screen.getByPlaceholderText('Search...'), 'wid')
    expect(screen.queryByText('Gadget')).not.toBeInTheDocument()
  })
})
```

**Coverage Requirements**:
- Unit tests: All components and stores
- Integration tests: Load functions and form actions
- Accessibility tests: Keyboard navigation, ARIA attributes
- Edge cases: Empty states, error states, boundary conditions

---

### Step 4: Commit Code + Tests

**Agent**: svelte-developer

**Commands**:
```bash
# Type-check
npx svelte-check --tsconfig ./tsconfig.json

# Lint
npx eslint src/ --ext .svelte,.ts

# Commit
git add .
git commit -m "feat: add product list component

- Implement ProductList with Svelte 5 runes
- Add search filtering with \$derived
- Add Vitest tests with @testing-library/svelte
- Test coverage: 85%"
```

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
npx vitest run --coverage
npx svelte-check --tsconfig ./tsconfig.json
```

**Pass Criteria**:
- All Vitest tests pass (0 failures)
- Coverage ≥ 80%
- No TypeScript errors from svelte-check

**On Fail**:
- Workflow BLOCKED
- svelte-developer fixes issues
- Returns to Step 5 after fix

---

### Step 6: Code Review ⚠️ GATE

**Agent**: frontend-code-reviewer (sonnet, opus for critical)

**Review Criteria**:
- ✅ **Svelte 5 patterns** (runes, no legacy Options API in new code)
- ✅ **TypeScript** (strict mode, no implicit `any`)
- ✅ **Security** (no `{@html}` with user content, server-side validation)
- ✅ **Performance** (`$derived` for computed values, keyed `{#each}`)
- ✅ **Accessibility** (semantic HTML, ARIA, keyboard nav)
- ✅ **SvelteKit** (correct use of load functions, form actions, server routes)

**Outcomes**:
- ✅ **APPROVED** - Continue to Step 8
- ❌ **CHANGES REQUESTED** - Go to Step 7

---

### Step 7: Fix Issues

**Agent**: svelte-developer

**Responsibilities**:
- Address ALL review issues
- Make targeted fixes
- Re-check with svelte-check and eslint
- Commit fixes
- Return to Step 5 (re-test) → Step 6 (re-review)

**Max Cycles**: 3 (if stuck, reassess approach)

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
npx vitest run --reporter=verbose
# Check dev server responds:
curl http://localhost:5173
```

**Pass Criteria**:
- All integration tests pass
- SvelteKit dev server responds correctly
- No runtime errors

---

### Step 9: Push Feature Branch

**Agent**: svelte-developer

**Commands**:
```bash
git push -u origin HEAD
```

---

### Step 10: Resolve Merge Conflicts ⚠️ GATE

**Agent**: merge-conflict-resolver (opus model)

**Svelte-Specific Conflict Types**:
- **Simple**: imports, whitespace → auto-resolve
- **Components**: Different template changes → integrate both
- **Stores**: Different state shape → request manual review
- **Routes**: Different page additions → integrate both

```bash
git push origin HEAD --force-with-lease
```

---

### Step 11: Final Integration Test ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
npx vitest run --coverage
npx svelte-check --tsconfig ./tsconfig.json
```

---

### Step 12: Merge to Base Branch

**Agent**: worktree-manager

**Commands**:
```bash
python scripts/worktree_merge.py feature-name
```

---

### Step 13: Cleanup

**Agent**: worktree-manager

**Commands**:
```bash
python scripts/worktree_cleanup.py feature-name
```

*(Docker projects only)* Also stops and removes Docker containers.

**On Failure** (Step 13b) *(Docker projects only)*:
- docker-debugger force cleanups stuck resources

---

### Step 14: Skill Discovery *(standard and full variants only)*

**Agent**: skill-creator

**Actions**:
1. Review the original task description and `git log --oneline` for the merged branch
2. Identify any multi-step patterns that emerged during Steps 2–7
3. Apply four gates: non-trivial, generalizable, not already covered, durable
4. Write a new skill or decline with a written reason

**This step is non-blocking** — a declined evaluation is not a failure.

---

## Workflow Variants

### Standard Workflow (13 steps) ⭐ Most Common

**Steps**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13 → 14

**Use For**: Regular Svelte components, enhancements (80% of work)
**Time**: 25-35 minutes
**Note**: Skips E2E tests (Step 8) and final integration test (Step 11)

### Full Workflow (14 steps)

**Steps**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14

**Use For**: New SvelteKit routes, major architectural changes
**Time**: 35-50 minutes

### Hotfix Workflow (10 steps) ⚡

**Steps**: 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent Svelte fixes
**Time**: 15-20 minutes

### Test-Only Workflow (7 steps)

**Steps**: 1 → 3 → 4 → 5 → 9 → 12 → 13

**Use For**: Adding tests to existing Svelte code

### Docs-Only Workflow (5 steps)

**Steps**: 1 → 2 → 9 → 12 → 13

**Use For**: Documentation changes only

---

## Resources

- [Svelte Development Guide](../.claude/SVELTE_GUIDE.md) - Svelte coding standards
- [Testing Guide](TESTING_GUIDE.md) - Vitest practices
- [Architecture](../.claude/ARCHITECTURE.md) - System architecture
- [SvelteKit Documentation](https://kit.svelte.dev/) - Official SvelteKit docs
- [Svelte 5 Runes](https://svelte.dev/docs/svelte/what-are-runes) - Runes reference

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
