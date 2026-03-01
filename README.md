# Claude Flow Kit

A modular, language-specific template for setting up Claude Code AI agents, workflows, and documentation structure in any project.

[![Test Installer](https://github.com/TheKathan/claude-flow-kit/actions/workflows/installer-test.yml/badge.svg)](https://github.com/TheKathan/claude-flow-kit/actions/workflows/installer-test.yml)
[![Lint Markdown](https://github.com/TheKathan/claude-flow-kit/actions/workflows/markdown-lint.yml/badge.svg)](https://github.com/TheKathan/claude-flow-kit/actions/workflows/markdown-lint.yml)
[![Validate Configs](https://github.com/TheKathan/claude-flow-kit/actions/workflows/validate-configs.yml/badge.svg)](https://github.com/TheKathan/claude-flow-kit/actions/workflows/validate-configs.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-blueviolet)](https://claude.ai/claude-code)

**Backend**
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?logo=nodedotjs&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-512BD4?logo=dotnet&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?logo=rust&logoColor=white)
![Ruby](https://img.shields.io/badge/Ruby-CC342D?logo=ruby&logoColor=white)

**Frontend**
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Vue](https://img.shields.io/badge/Vue-4FC08D?logo=vuedotjs&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-DD0031?logo=angular&logoColor=white)
![Tauri](https://img.shields.io/badge/Tauri-24C8D8?logo=tauri&logoColor=white)

**Infrastructure**
![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=white)

---

## 🎯 What This Template Provides

- **Modular Architecture** - Pick only backend, frontend, or infrastructure components you need
- **Language-Specific Workflows** - Python, .NET, Node.js, Go, Rust, Ruby, React, Vue, Angular, Tauri, Terraform
- **13-Step Worktree Workflow** - Isolated development with quality gates
- **PR Workflow Support** - Optional PR-to-main workflow with human approval
- **Downloadable Installer** - Run from anywhere, no repo cloning needed
- **Quality Gates** - Automated testing, code review, and integration checks
- **All Components Optional** - Backend-only, frontend-only, or any combination

---

## 🚀 Quick Start

### Option 1: Downloadable Installer (Recommended)

Download and run the installer — no repo cloning needed.

#### Linux / macOS

```bash
curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py -o install.py
python3 install.py
```

#### Windows — PowerShell

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py" -OutFile "install.py"
python install.py
```

#### Windows — Command Prompt (cmd)

```cmd
curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py -o install.py
python install.py
```

---

The installer will prompt you for:

- **Project information** (name, description, repository URL)
- **Backend** (Python / Node.js / .NET / Go / Rust / Ruby or none)
- **Frontend** (React / Vue / Angular / Tauri or none)
- **Infrastructure** (Terraform or none)
- **Docker usage** (yes/no)
- **Git configuration** (main branch name)

The installer downloads **only** the components you select to your current directory.

---

### Option 2: Clone and Setup Locally

For development or customization of the template itself.

#### Linux / macOS

```bash
git clone https://github.com/TheKathan/claude-flow-kit.git
cd claude-flow-kit
python3 setup_claude.py
```

#### Windows — PowerShell

```powershell
git clone https://github.com/TheKathan/claude-flow-kit.git
cd claude-flow-kit
python setup_claude.py
```

---

### What Gets Installed

Based on your selections, the installer creates:

- **CLAUDE.md** — Navigation hub for your project
- **Workflow files** — Language-specific development guides
- **Agent configurations** — AI agents for your tech stack
- **Documentation templates** — Ready to customize
- **Worktree scripts** — Automated workflow management

You get only what you need — no clutter.

---

### After Installation

1. Review your selected workflow in `docs/`
2. Customize documentation in `.claude/`
3. Start building with Claude Code agents

```bash
# Works on Linux, macOS, and Windows (Git Bash / PowerShell / cmd)
git add CLAUDE.md .claude/ .agents/ docs/ scripts/
git commit -m "Add Claude Code configuration"
```

> **Note**: `.claude/` and `.agents/` are hidden directories (dot-prefix).
> - **Linux/macOS**: `ls -la` to see them
> - **PowerShell**: `Get-ChildItem -Force`
> - **cmd**: `dir /a`

---

## 🤖 Available Agents

The template includes language-specific agents automatically configured based on your selections:

### Backend Development Agents

- **python-developer** / **python-test-specialist** — Python/FastAPI development
- **dotnet-developer** / **dotnet-test-specialist** — .NET/ASP.NET Core development
- **nodejs-developer** / **nodejs-test-specialist** — Node.js/Express development
- **go-developer** / **go-test-specialist** — Go development
- **rust-developer** / **rust-test-specialist** — Rust/Axum development
- **ruby-developer** / **ruby-test-specialist** — Ruby/Rails development

### Frontend Development Agents

- **react-frontend-dev** / **react-test-specialist** — React/Next.js development
- **vue-developer** / **vue-test-specialist** — Vue/Nuxt development
- **angular-developer** / **angular-test-specialist** — Angular development
- **rust-developer** / **rust-test-specialist** — Tauri desktop apps (src-tauri/ Rust backend)

### Infrastructure Agents

- **terraform-developer** / **terraform-test-specialist** - Terraform/IaC development

### Common Agents (Included in All Configurations)

- **backend-code-reviewer** - Review backend code
- **frontend-code-reviewer** - Review frontend code (if frontend selected)
- **infrastructure-code-reviewer** - Review infrastructure code (if infrastructure selected)
- **software-architect** - Design architecture (opus model)
- **worktree-manager** - Manage isolated worktrees
- **pr-manager** - Manage GitHub Pull Requests
- **docker-debugger** - Fix Docker issues
- **merge-conflict-resolver** - Resolve merge conflicts (opus model)
- **integration-tester** - Execute E2E tests (haiku model for cost savings)

---

## ⌨️ Using the `/workflow` Command

After installation, Claude Code has a `/workflow` slash command that drives the entire 13-step process hands-free. Open Claude Code in your project directory and type:

```
/workflow <describe your task>
```

Claude reads your task, picks the right workflow variant, and orchestrates all the agents automatically — from creating an isolated worktree through testing, code review, conflict resolution, merge, and cleanup.

---

### Basic Syntax

```
/workflow <task description>
```

The description is plain English. Be specific about what you want.

---

### Workflow Variants

The command auto-detects the right variant from keywords in your task. You can also prefix explicitly.

| Variant | Auto-detected from | Steps | Time |
|---|---|---|---|
| **standard** | *(default — anything else)* | 1→2→3→4→5→6→7→9→10→12→13 | 25-35 min |
| **full** | "new service", "architecture", "redesign", "migrate" | 0→1→2→3→4→5→6→7→8→9→10→11→12→13 | 35-50 min |
| **hotfix** | "fix", "bug", "crash", "urgent" | 1→2→4→5→6→7→9→10→12→13 | 15-20 min |
| **tests** | "add tests", "coverage", "test-only" | 1→3→4→5→9→12→13 | 15-20 min |
| **docs** | "docs", "readme", "documentation" | 1→2→9→12→13 | 10-15 min |

To **force a variant**, prefix the task with its name:

```
/workflow full add user authentication with JWT
/workflow hotfix login endpoint returns 500 on empty password
/workflow tests improve coverage on the payment service
```

---

### Examples

#### Python / FastAPI

```
/workflow add a POST /api/users endpoint with email validation and password hashing
```

```
/workflow hotfix fix the user lookup query that crashes on special characters
```

#### Node.js / Express

```
/workflow add JWT refresh token rotation to the auth service
```

#### Rust / Axum

```
/workflow add a rate-limiting middleware using tower to the Axum router
```

```
/workflow full design and implement a file storage service with S3 integration
```

#### React / Next.js

```
/workflow add a paginated data table component with sorting and filtering
```

```
/workflow hotfix fix the dashboard crash when the API returns an empty array
```

#### Tauri (Rust + Web)

```
/workflow add a read_recent_files Tauri command that returns the 10 most recently opened files
```

```
/workflow full design the file watcher feature that sends events from Rust to the frontend
```

#### Vue / Nuxt

```
/workflow add a notification toast composable with auto-dismiss
```

#### Angular

```
/workflow add a reactive form with server-side validation for the profile settings page
```

#### Infrastructure (Terraform)

```
/workflow full provision an S3 bucket with versioning, encryption, and lifecycle rules
```

---

### What Happens When You Run `/workflow`

1. **Variant selection** — Claude analyses the task and picks `standard`, `full`, `hotfix`, `tests`, or `docs`, then states the chosen variant and step sequence.

2. **Worktree created** — an isolated git branch (e.g., `feature/user-auth`) and worktree are created so your main branch is never touched mid-work.

3. **Implementation** — the right developer agent (`python-developer`, `rust-developer`, `react-frontend-dev`, etc.) writes the code inside the worktree.

4. **Tests written** — the matching test specialist writes unit tests targeting 80%+ coverage.

5. **Quality gates** — `integration-tester` runs the test suite; `backend-code-reviewer` or `frontend-code-reviewer` reviews the code. Both gates must pass.

6. **Conflicts resolved** — `merge-conflict-resolver` pulls the latest base branch and resolves any conflicts automatically.

7. **Merge & cleanup** — `worktree-manager` merges to your base branch, pushes, and removes the worktree.

8. **Summary** — Claude reports what was built, the branch name, variant used, and any issues encountered.

---

### Quality Gates (Blocking)

The workflow cannot advance past a failed gate without resolution:

| Gate | Step | Must Pass |
|---|---|---|
| Unit tests | 5 | 0 failures, ≥80% coverage |
| Code review | 6 | Approved |
| Integration tests | 8 | 0 failures *(full variant only)* |
| Conflict resolution | 10 | All conflicts resolved |
| Final integration | 11 | 0 failures *(full variant only)* |

If a gate fails, the relevant developer agent is automatically invoked to fix the issue, then the gate retries. After 3 failed cycles the workflow pauses and reports to you.

---

### Tips

- **Be specific** in your task description — "add user auth" is okay, "add JWT authentication with refresh tokens and blacklisting" triggers better architecture decisions.
- **Use `full`** for new services, schema changes, or any feature that touches multiple layers.
- **Use `hotfix`** for bugs — it skips test writing (tests should already exist) and moves faster.
- **Working on a PR branch?** The worktree will branch from your current branch and merge back to it, not to `main`.
- **Stuck mid-workflow?** Tell Claude which step you're on and it will resume from there.

---

## 🔄 Workflow Steps Reference

All workflows follow the same 13-step structure. See `docs/WORKFLOW_GUIDE.md` and your language-specific `docs/WORKFLOW_BACKEND_*.md` / `docs/WORKFLOW_FRONTEND_*.md` for detailed per-step commands.

```text
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree (+ Docker if used)
Step 2:  {language}-developer               → Implement feature
Step 3:  {language}-test-specialist         → Write comprehensive tests
Step 4:  {language}-developer               → Commit code + tests
Step 5:  integration-tester                 → Run unit tests [GATE]
Step 6:  {area}-code-reviewer               → Review code [GATE]
Step 7:  {language}-developer               → Fix if needed (loop back to 5-6)
Step 8:  integration-tester                 → Run integration tests [GATE]
Step 9:  {language}-developer               → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
Step 12: worktree-manager                   → Merge to base branch, push
Step 13: worktree-manager                   → Cleanup worktree (+ Docker)
```

### Merge Strategies

**Direct Merge to Current Branch (Default)**:

- Worktrees merge back to the branch they were created from
- Supports nested feature development
- Example: On `feature/parent` → create `feature/child` → merges to `feature/parent`

**PR to Main (Optional)**:

- Create Pull Request to main (always main, regardless of current branch)
- Requires human approval before merge
- Auto-cleanup after PR is merged
- Configure with `merge_strategy: "pr-to-main"` in `.agents/config.json`

---

## 🔧 Troubleshooting

### Installation Issues

**`EOFError` or installer exits immediately:**

The installer is interactive and needs a real terminal. Never pipe it:

```bash
# Wrong — breaks stdin:
curl -sSL .../install.py | python3

# Correct — download first, then run:
# Linux/macOS:
curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py -o install.py
python3 install.py

# PowerShell:
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py" -OutFile "install.py"
python install.py
```

**Installer fails to download files:**

```bash
# Linux/macOS — check connectivity:
curl -I https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py

# PowerShell — check connectivity:
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py" -Method Head
```

**Python not found:**

```bash
# Linux/macOS:
python3 --version   # must be 3.7+
which python3

# PowerShell / cmd:
python --version    # must be 3.7+
# Download from https://www.python.org/downloads/ if missing
```

**Garbled characters on Windows (emoji not rendering):**

```powershell
# Option A — set UTF-8 console before running:
chcp 65001
python install.py

# Option B — set environment variable:
$env:PYTHONUTF8 = "1"
python install.py
```

**No components selected:**

You must select at least one component (backend, frontend, or infrastructure). Re-run the installer and make a selection.

---

### Agent Configuration Issues

**Check configuration:**

1. Verify `.agents/config.json` is valid JSON
2. Check file watch patterns match your project structure
3. Ensure model names are correct (`haiku` / `sonnet` / `opus`)

**Merged config missing agents:**

The installer only includes agents for selected components. Re-run if you need to add more.

---

### Worktree Scripts Issues

**Scripts not executable (Linux/macOS only):**

```bash
chmod +x scripts/*.py
```

Windows does not require this — Python scripts run directly via `python scripts/worktree_create.py`.

**GitHub CLI (`gh`) not found:**

```bash
# macOS:
brew install gh

# Linux (Debian/Ubuntu):
sudo apt install gh

# Windows (PowerShell — requires winget):
winget install GitHub.cli
# or: choco install gh

# Authenticate on any platform:
gh auth login
```

---

## 🤝 Contributing

Contributions are welcome! To add new languages or frameworks:

1. Fork the repository
2. Add workflow file (`docs/WORKFLOW_{TYPE}_{LANG}.md`)
3. Add development guide (`.claude/{LANG}_GUIDE.md`)
4. Add agent config (`.agents/config_{type}_{lang}.json`)
5. Update installer with detection logic
6. Submit pull request

---

## 📝 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

---

**Version**: 2.0.0
**Last Updated**: 2026-02-21
**Status**: Production Ready
