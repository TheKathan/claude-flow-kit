# Frontend Tauri Workflow - {{PROJECT_NAME}}

**Date**: {{CURRENT_DATE}}
**Status**: ✅ ACTIVE
**Version**: 2.0 - Tauri Worktree-Based Workflow

---

## Overview

This guide covers the 13-step worktree-based workflow for **Tauri desktop application development**. Tauri apps have two layers that must both be maintained:

- **Rust backend** (`src-tauri/`) — Tauri commands, app state, native OS integration
- **Web frontend** (`src/`) — React, Vue, or Angular UI communicating via Tauri's IPC

This workflow integrates:
- **Worktree isolation** (each feature gets its own worktree)
- **Architectural planning** (optional for complex features)
- **Automated test writing** (mandatory for both Rust and frontend layers)
- **Quality gates** (tests + code review + integration tests)
- **Merge conflict resolution** (automated before merge)
- **Automatic merge & cleanup** (after all gates pass)

---

## Workflow Architecture

### Core Principle

**Dual-Layer Quality: Rust Backend + Web Frontend**

Every Tauri feature:
1. Gets its own **isolated worktree**
2. Implements both **Rust commands** and **frontend UI** if needed
3. Goes through **mandatory quality gates** for both layers
4. Has **conflicts resolved automatically** before merge
5. Is **merged and cleaned up automatically** after approval

**Quality Gates**:
1. **Unit Test Gate** (Step 5) - Rust tests + frontend unit tests must pass
2. **Code Review Gate** (Step 6) - Both layers reviewed
3. **Integration Test Gate** (Step 8) - End-to-end Tauri tests must pass
4. **Conflict Resolution Gate** (Step 10) - Merge conflicts must be resolved
5. **Final Integration Gate** (Step 11) - Final build must succeed

---

## Agent System

**Specialized Agents for Tauri Development**:

| Agent | Type | Scope | Role | Model |
|-------|------|-------|------|-------|
| software-architect | Architect | All | Design architecture (optional) | opus |
| **worktree-manager** | **Manager** | **All** | **Create worktrees, merge, cleanup** | sonnet |
| **rust-developer** | **Developer** | **Backend** | **Implement Tauri commands (src-tauri/)** | sonnet |
| **react-frontend-dev** *(or vue/angular)* | **Developer** | **Frontend** | **Implement web UI** | sonnet |
| **rust-test-specialist** | **Tester** | **Backend** | **Write Rust tests for Tauri commands** | sonnet |
| **react-test-specialist** *(or vue/angular)* | **Tester** | **Frontend** | **Write frontend tests** | sonnet |
| **frontend-code-reviewer** | **Reviewer** | **Frontend** | **Review both layers** | sonnet/opus |
| integration-tester | Tester | All | Execute all tests and enforce gates | haiku |
| **merge-conflict-resolver** | **Resolver** | **All** | **Detect and resolve merge conflicts** | opus |

---

## 13-Step Tauri Workflow

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree
Step 2a: rust-developer                     → Implement Tauri commands (src-tauri/)
Step 2b: react-frontend-dev                 → Implement web UI + invoke() calls
Step 3a: rust-test-specialist               → Write Rust command tests
Step 3b: react-test-specialist              → Write frontend tests (mock invoke())
Step 4:  rust-developer                     → Commit code + tests
Step 5:  integration-tester                 → Run cargo test + npm test [GATE]
Step 6:  frontend-code-reviewer             → Review both layers [GATE]
Step 7:  rust-developer / react-frontend-dev → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run E2E Tauri build test [GATE]
Step 9:  rust-developer                     → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final build test [GATE]
Step 12: worktree-manager                   → Merge to base branch, push
Step 13: worktree-manager                   → Cleanup worktree
```

---

## Step-by-Step Guide

### Step 0: Architectural Planning (Optional)

**When to Use**:
- ✅ New Tauri commands with complex OS integration
- ✅ Changes to app state or permission model
- ✅ New frontend views with significant Tauri IPC usage
- ✅ Security-sensitive features (file system, network access)

**When to Skip**:
- ❌ Minor UI updates with no new commands
- ❌ Bug fixes in existing commands
- ❌ Styling or copy changes

**Agent**: software-architect (opus model)

---

### Step 1: Create Worktree

**Agent**: worktree-manager

**Commands**:
```bash
python scripts/worktree_create.py feature-name
```

**Output**:
- Worktree created at `.worktrees/feature-name`
- Branch created: `feature/feature-name`

---

### Step 2a: Implement Tauri Commands (Rust)

**Agent**: rust-developer

**Responsibilities**:
- Write safe, idiomatic Rust command handlers in `src-tauri/src/commands/`
- Use typed errors that implement `Serialize` (required for Tauri)
- Validate all file paths and inputs before processing
- Update `main.rs` to register new commands
- Update `tauri.conf.json` allowlist if new APIs are needed

**Tauri Command Pattern**:
```rust
// src-tauri/src/commands/settings.rs
use tauri::{command, State};
use crate::{errors::AppError, state::AppState};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct AppSettings {
    pub theme: String,
    pub font_size: u8,
}

#[command]
pub async fn get_settings(
    state: State<'_, AppState>,
) -> Result<AppSettings, AppError> {
    let settings = state.settings.lock()
        .map_err(|_| AppError::Internal("lock poisoned".into()))?
        .clone();
    Ok(settings)
}

#[command]
pub async fn save_settings(
    settings: AppSettings,
    state: State<'_, AppState>,
) -> Result<(), AppError> {
    *state.settings.lock()
        .map_err(|_| AppError::Internal("lock poisoned".into()))? = settings;
    Ok(())
}
```

---

### Step 2b: Implement Web Frontend

**Agent**: react-frontend-dev (or vue-developer / angular-developer)

**Responsibilities**:
- Implement UI components that call Tauri commands via `invoke()`
- Handle command errors gracefully in the UI
- Use TypeScript types matching Rust struct shapes
- Handle both loading and error states

**Frontend Pattern**:
```typescript
// src/hooks/useSettings.ts
import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';

interface AppSettings {
  theme: string;
  fontSize: number;
}

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    invoke<AppSettings>('get_settings')
      .then(setSettings)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const saveSettings = async (updated: AppSettings) => {
    await invoke('save_settings', { settings: updated });
    setSettings(updated);
  };

  return { settings, error, loading, saveSettings };
}
```

---

### Step 3a: Write Rust Tests

**Agent**: rust-test-specialist

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_settings_theme() {
        let settings = AppSettings {
            theme: "dark".to_string(),
            font_size: 14,
        };
        assert_eq!(settings.theme, "dark");
    }
}
```

---

### Step 3b: Write Frontend Tests

**Agent**: react-test-specialist (or vue-test-specialist / angular-test-specialist)

Mock the Tauri `invoke` function in tests — never call the real Tauri API in unit tests.

```typescript
// src/hooks/useSettings.test.ts
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';

vi.mock('@tauri-apps/api/tauri', () => ({
  invoke: vi.fn(),
}));

import { invoke } from '@tauri-apps/api/tauri';
import { useSettings } from './useSettings';

describe('useSettings', () => {
  beforeEach(() => vi.clearAllMocks());

  it('loads settings on mount', async () => {
    vi.mocked(invoke).mockResolvedValue({ theme: 'dark', fontSize: 14 });
    const { result } = renderHook(() => useSettings());

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.settings?.theme).toBe('dark');
  });

  it('sets error when invoke fails', async () => {
    vi.mocked(invoke).mockRejectedValue('permission denied');
    const { result } = renderHook(() => useSettings());

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).toBeTruthy();
  });
});
```

---

### Step 4: Commit Code + Tests

**Agent**: rust-developer

**Commands**:
```bash
# Format and lint Rust
cargo fmt --manifest-path src-tauri/Cargo.toml
cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings

# Format and lint frontend
npm run lint

# Run all tests
cargo test --manifest-path src-tauri/Cargo.toml
npm test

# Commit
git add src/ src-tauri/ package.json
git commit -m "feat: add settings management

- Add get_settings and save_settings Tauri commands
- Add AppState with Mutex<Settings> for thread-safe access
- Add useSettings React hook with invoke() integration
- Mock Tauri invoke in frontend unit tests
- Rust: zero clippy warnings, formatted with rustfmt"
```

---

### Step 5: Run Unit Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# Rust backend tests
cargo test --manifest-path src-tauri/Cargo.toml
cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings

# Frontend tests
npm test
npm run lint
```

**Pass Criteria**:
- All Rust tests pass
- All frontend tests pass
- Zero clippy warnings
- Zero lint errors
- Coverage ≥ 80% across both layers

---

### Step 6: Code Review ⚠️ GATE

**Agent**: frontend-code-reviewer

**Review Criteria**:
- ✅ **Tauri Security** (allowlist minimal, path validation, no arbitrary shell execution)
- ✅ **CSP Compliance** (Content Security Policy in `tauri.conf.json`)
- ✅ **Error Handling** (typed Rust errors + frontend error states)
- ✅ **Type Safety** (TypeScript types match Rust structs)
- ✅ **Rust Safety** (no `unwrap()` in production, no unsafe blocks without justification)
- ✅ **State Management** (proper Tauri managed state, no data races)

---

### Step 7: Fix Issues

**Agent**: rust-developer / react-frontend-dev

- Address ALL review issues in both layers
- Re-run formatting, linting, and tests
- Commit fixes
- Return to Step 5 → Step 6

**Max Cycles**: 3

---

### Step 8: Run Integration Tests ⚠️ GATE

**Agent**: integration-tester (haiku model)

**Commands**:
```bash
# Verify Tauri app builds successfully
npm run tauri build

# Or for faster check: just compile without full bundling
cargo build --manifest-path src-tauri/Cargo.toml --release
npm run build
```

**Pass Criteria**:
- Tauri app builds without errors
- Frontend bundles successfully
- Rust compiles in release mode with zero warnings

---

### Step 9: Push Feature Branch

**Agent**: rust-developer

```bash
git push -u origin HEAD
```

---

### Step 10: Resolve Merge Conflicts ⚠️ GATE

**Agent**: merge-conflict-resolver (opus model)

**Tauri-Specific Conflict Types**:
- **`tauri.conf.json`**: Different allowlist additions → merge both
- **`Cargo.toml`**: Different dependency additions → merge both
- **`main.rs` invoke_handler**: Different command registrations → integrate both
- **Logic conflicts**: Request manual review

---

### Step 11: Final Integration Test ⚠️ GATE

**Agent**: integration-tester (haiku model)

```bash
# Full build verification after merge
cargo test --manifest-path src-tauri/Cargo.toml
npm test
cargo build --manifest-path src-tauri/Cargo.toml
npm run build
```

---

### Step 12: Merge to Base Branch

**Agent**: worktree-manager

```bash
python scripts/worktree_merge.py feature-name
```

---

### Step 13: Cleanup

**Agent**: worktree-manager

```bash
python scripts/worktree_cleanup.py feature-name
```

---

## Workflow Variants

### Standard Workflow (11 steps) ⭐ Most Common

**Steps**: 1 → 2a/2b → 3a/3b → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Regular Tauri features (80% of work)
**Time**: 25-35 minutes

### Full Workflow (13 steps)

**Steps**: 0 → 1 → 2a/2b → 3a/3b → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Use For**: New commands, allowlist changes, state architecture changes
**Time**: 35-50 minutes

### Hotfix Workflow (10 steps) ⚡

**Steps**: 1 → 2a/2b → 4 → 5 → 6 → 7 → 9 → 10 → 12 → 13

**Use For**: Production bugs, urgent fixes
**Time**: 15-20 minutes

---

## Tauri Development Best Practices

### DO

✅ Keep `tauri.conf.json` allowlist minimal — only what the app actually needs
✅ Validate all file paths in Rust before accessing the filesystem
✅ Use typed errors that implement `Serialize` for Tauri commands
✅ Mock `@tauri-apps/api/tauri` in all frontend unit tests
✅ Use `State<'_, AppState>` for shared mutable state
✅ Test Rust command logic independently of Tauri framework
✅ Use TypeScript interfaces that mirror your Rust structs

### DON'T

❌ Use `tauri::api::shell::open` with user-controlled input (shell injection risk)
❌ Set `"all": true` in the allowlist — restrict to what you need
❌ Call `invoke()` in frontend unit tests without mocking
❌ Use `unwrap()` in Tauri command handlers
❌ Store sensitive data in Tauri managed state without encryption
❌ Skip path validation for filesystem commands

---

## Resources

- [Tauri Guide](../.claude/TAURI_GUIDE.md) - Tauri development standards
- [Rust Guide](../.claude/RUST_GUIDE.md) - Rust coding standards
- [React Guide](../.claude/REACT_GUIDE.md) - React coding standards
- [Tauri Documentation](https://tauri.app/v1/guides/) - Official Tauri docs
- [Tauri Security](https://tauri.app/v1/references/architecture/security/) - Security model

---

**Last Updated**: {{CURRENT_DATE}}
**Status**: Living Document
