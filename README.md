# Claude Flow Kit

A modular, language-specific template for setting up Claude Code AI agents, workflows, and documentation structure in any project.

## 🎯 What This Template Provides

- **Modular Architecture** - Pick only backend, frontend, or infrastructure components you need
- **Language-Specific Workflows** - Python, .NET, Node.js, Go, React, Vue, Angular, Terraform
- **13-Step Worktree Workflow** - Isolated development with quality gates
- **PR Workflow Support** - Optional PR-to-main workflow with human approval
- **Downloadable Installer** - Run from anywhere, no repo cloning needed
- **Quality Gates** - Automated testing, code review, and integration checks
- **All Components Optional** - Backend-only, frontend-only, or any combination

## 🚀 Quick Start

### Option 1: Downloadable Installer (Recommended)

Run the installer directly from GitHub - no need to clone the repository:

```bash
# Download and run installer in one command
curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py | python3
```

Or download first, then run:

```bash
# Download the installer
curl -O https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py

# Run the installer
python3 install.py
```

The installer will prompt you for:
- **Project information** (name, description, repository URL)
- **Backend** (Python/Node.js/.NET/Go or none)
- **Frontend** (React/Vue/Angular or none)
- **Infrastructure** (Terraform or none)
- **Docker usage** (yes/no)
- **Git configuration** (main branch name)

The installer downloads **only** the components you select to your current directory.

### Option 2: Clone and Setup Locally

For development or customization:

```bash
# Clone repository
git clone https://github.com/TheKathan/claude-flow-kit.git
cd claude-flow-kit

# Run setup script
python setup_claude.py
```

### What Gets Installed

Based on your selections, the installer creates:

- **CLAUDE.md** - Navigation hub for your project
- **Workflow files** - Language-specific development guides
- **Agent configurations** - AI agents for your tech stack
- **Documentation templates** - Ready to customize
- **Worktree scripts** - Automated workflow management

That's it! You get only what you need - no clutter.

### After Installation

1. Review your selected workflow in `docs/`
2. Customize documentation in `.claude/`
3. Start building with Claude Code agents

```bash
git add CLAUDE.md .claude/ .agents/ docs/ scripts/
git commit -m "Add Claude Code configuration

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## 🤖 Available Agents

The template includes language-specific agents that are automatically configured based on your selections:

### Backend Development Agents
- **python-developer** / **python-test-specialist** - Python/FastAPI development
- **dotnet-developer** / **dotnet-test-specialist** - .NET/ASP.NET Core development
- **nodejs-developer** / **nodejs-test-specialist** - Node.js/Express development
- **go-developer** / **go-test-specialist** - Go development

### Frontend Development Agents
- **react-frontend-dev** / **react-test-specialist** - React/Next.js development
- **vue-developer** / **vue-test-specialist** - Vue/Nuxt development
- **angular-developer** / **angular-test-specialist** - Angular development

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

## 🔄 Workflow Support

### 13-Step Worktree Workflow

All workflows follow the same structure:

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree + Docker
Step 2:  {language}-developer               → Implement feature
Step 3:  {language}-test-specialist         → Write comprehensive tests
Step 4:  {language}-developer               → Commit code + tests
Step 5:  integration-tester                 → Run unit tests [GATE]
Step 6:  {area}-code-reviewer               → Review code [GATE]
Step 7:  {language}-developer               → Fix if needed (loop to 5-6)
Step 8:  integration-tester                 → Run integration tests [GATE]
Step 9:  {language}-developer               → Push to feature branch
Step 10: merge-conflict-resolver            → Resolve conflicts [GATE]
Step 11: integration-tester                 → Final integration test [GATE]
Step 12: worktree-manager                   → Merge to main, push
Step 13: worktree-manager                   → Cleanup worktree + Docker
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

### Workflow Variants

- **Standard Workflow (13 steps)** - Most common (25-35 min)
- **Hotfix Workflow (9 steps)** - Urgent fixes (15-20 min)
- **Architecture-First (14 steps)** - New services (35-50 min)

See your language-specific workflow file in `docs/` for detailed commands.

## 🔧 Troubleshooting

### Installation Issues

**Installer fails to download:**
```bash
# Check network connection
curl -I https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py

# Try downloading manually first
curl -O https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py
python3 install.py
```

**Python not found:**
```bash
# Use Python 3 explicitly
python3 install.py

# Or check Python version
python --version  # Should be 3.7+
```

**No components selected:**
- You must select at least one component (backend, frontend, or infrastructure)
- Rerun installer and select your desired components

### Agent Configuration Issues

**Check configuration:**
1. Verify `.agents/config.json` is valid JSON
2. Check file watch patterns match your project structure
3. Ensure model names are correct (haiku/sonnet/opus)

**Merged config missing agents:**
- The installer only includes agents for selected components
- Rerun installer if you need additional components

### Worktree Scripts Issues

**Scripts not executable:**
```bash
chmod +x scripts/*.py
```

**GitHub CLI (gh) not found:**
```bash
# Install GitHub CLI for PR workflow
# macOS: brew install gh
# Linux: See https://github.com/cli/cli#installation
# Windows: See https://github.com/cli/cli#installation

# Authenticate
gh auth login
```

## 🤝 Contributing

Contributions are welcome! To add new languages or frameworks:

1. Fork the repository
2. Add workflow file (`docs/WORKFLOW_{TYPE}_{LANG}.md`)
3. Add development guide (`.claude/{LANG}_GUIDE.md`)
4. Add agent config (`.agents/config_{type}_{lang}.json`)
5. Update installer with detection logic
6. Submit pull request

## 📝 License

This template is provided as-is for use in any project. Customize freely.

## 🔗 Links

- **Repository**: https://github.com/TheKathan/claude-flow-kit
- **Installation**: `curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py | python3`
- **Issues**: https://github.com/TheKathan/claude-flow-kit/issues
- **Discussions**: https://github.com/TheKathan/claude-flow-kit/discussions

## 📊 Repository Stats

- 50+ files
- 8 language/framework workflows
- 8 development guides
- 9 modular agent configurations
- 6 worktree management scripts

---

**Version**: 2.0.0
**Last Updated**: 2026-02-12
**Status**: Production Ready
