Execute the worktree-based development workflow for this task:

**Task**: $ARGUMENTS

---

## Step 1 — Select Workflow Variant

Inspect the task and pick the right variant. If the task starts with a variant keyword (`full`, `hotfix`, `tests`, `docs`), strip it and use that variant. Otherwise, auto-select:

| Variant | When to use | Steps |
|---------|-------------|-------|
| **standard** | Regular features and enhancements (default) | 1→2→3→4→5→6→7→9→10→12→13→14 |
| **full** | New services, major architecture changes | 0→1→2→3→4→5→6→7→8→9→10→11→12→13→14 |
| **hotfix** | Production bugs, urgent fixes | 1→2→4→5→6→7→9→10→12→13 |
| **tests** | Adding tests to existing code | 1→3→4→5→9→12→13 |
| **docs** | Documentation-only changes | 1→2→9→12→13 |

Auto-select signals:
- Keywords like "fix", "bug", "crash", "urgent" → **hotfix**
- Keywords like "new service", "architecture", "redesign", "migrate" → **full**
- "add tests", "coverage", "test-only" → **tests**
- "docs", "readme", "documentation" → **docs**
- Everything else → **standard**

State the selected variant and confirm the step sequence before proceeding.

---

## Step 2 — Execute the Workflow

Read `CLAUDE.md` and `docs/WORKFLOW_GUIDE.md` to understand the project's stack and conventions, then execute each step below in order.

**CRITICAL**: You MUST use the Agent tool (subagent) for EVERY step that lists an **Agent**. Never perform the agent's work inline — always delegate to the specified agent via the Agent tool. This is mandatory, not optional. The only work you do directly is orchestration (deciding which step to run next, reading gate results, and reporting status).

### Step 0 — Architecture Design *(full variant only, or complex features)*
**Agent**: `software-architect`
Invoke if the task involves new services, database schema changes, or significant architectural decisions. Output a design document before any code is written.

### Step 1 — Create Worktree
**Agent**: `worktree-manager`
Create an isolated worktree and branch for this task. Derive a short kebab-case branch name from the task description (e.g., `feature/user-auth`, `fix/login-crash`).

If Docker is in use and container setup fails → invoke `docker-debugger` (Step 1b).

### Step 2 — Implement
**Agent**: appropriate developer for the stack (e.g., `python-developer`, `nodejs-developer`, `react-frontend-dev`)
Implement the feature inside the worktree. Do **not** commit yet — tests come first.

*Skip for `tests` and `docs` variants.*

### Step 3 — Write Tests
**Agent**: appropriate test specialist (e.g., `python-test-specialist`, `react-test-specialist`)
Write tests covering happy paths, error cases, edge cases, and security. Target 80%+ coverage.

*Skip for `hotfix` and `docs` variants.*

### Step 4 — Commit
**Agent**: same developer as Step 2
Commit implementation + tests together. Commit message format:
```
<type>: <short description>

- What changed and why
- Test coverage: X%
```
Never include Co-Authored-By or AI references.

*Skip for `docs` variant.*

### Step 5 — Unit Tests ⚠️ GATE
**Agent**: `integration-tester`
Run the project's unit test suite. Must pass with 0 failures and ≥80% coverage. If this gate fails, invoke the developer to fix then retry.

If Docker containers fail → invoke `docker-debugger` (Step 5b), then retry.

*Skip for `tests`, `docs` variants.*

### Step 6 — Code Review ⚠️ GATE
**Agent**: appropriate reviewer (`backend-code-reviewer` or `frontend-code-reviewer`)
Review committed code for security, performance, best practices, and architecture. Must be APPROVED before continuing. If CHANGES REQUESTED, go to Step 7.

*Skip for `hotfix`, `tests`, `docs` variants.*

### Step 7 — Fix Issues *(if Step 6 requested changes)*
**Agent**: same developer as Step 2
Address every review comment. Commit fixes, then loop back to Step 5 (re-test) → Step 6 (re-review). Maximum 3 cycles.

### Step 8 — Integration Tests ⚠️ GATE *(full variant only)*
**Agent**: `integration-tester`
Run end-to-end and integration tests. Must pass with 0 failures.

If Docker containers fail → invoke `docker-debugger` (Step 8b), then retry.

### Step 9 — Push Branch
**Agent**: same developer as Step 2
Push the feature branch to the remote.

### Step 10 — Resolve Conflicts ⚠️ GATE
**Agent**: `merge-conflict-resolver`
Pull the base branch, merge it into the feature branch, resolve any conflicts, then push the resolved branch.

### Step 11 — Final Integration Test ⚠️ GATE *(full variant only)*
**Agent**: `integration-tester`
Run the full test suite one final time after merging the base branch. Must pass.

If Docker containers fail → invoke `docker-debugger` (Step 11b), then retry.

### Step 12 — Merge
**Agent**: `worktree-manager`
Merge the feature branch to the base branch and push.

### Step 13 — Cleanup
**Agent**: `worktree-manager`
Remove the worktree and associated resources. If cleanup fails → invoke `docker-debugger` (Step 13b) for force cleanup.

### Step 14 — Skill Discovery *(opt-in — only when a reusable pattern was identified)*
**Agent**: `skill-creator`

**Only invoke this step if** during Steps 2–7 you identified a specific, concrete multi-step pattern that:
- You performed at least twice, OR
- Took 10+ minutes and would clearly recur in future workflows

If no such pattern was identified, **skip this step entirely** — do not invoke skill-creator speculatively.

When invoking, provide:
1. The specific pattern you identified (not just the task description)
2. Why you believe it's reusable (concrete examples of when it would recur)
3. Output of `git log --oneline` for the merged feature branch

The agent self-assesses against its five gates and either writes a new skill file or declines with a written reason. **This step is non-blocking** — a declined evaluation is the expected outcome most of the time.

**Skip this step if**: variant is `hotfix`, `tests`, or `docs`; the workflow completed with unresolved failures; or no reusable pattern was explicitly identified during implementation.

---

## Quality Gates

Gates are blocking — the workflow cannot advance past a failed gate without resolution.

| Gate | Step | Pass Criteria |
|------|------|---------------|
| Unit tests | 5 | 0 failures, ≥80% coverage |
| Code review | 6 | Approved |
| Integration tests | 8 | 0 failures |
| Conflict resolution | 10 | All conflicts resolved |
| Final integration | 11 | 0 failures |

---

After all steps complete, summarise: what was built, which variant was used, branch name, and any issues encountered.
