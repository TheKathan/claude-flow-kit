# Claude Code Project Template

A reusable template for setting up Claude Code AI agents, workflows, and documentation structure in any project.

## 🎯 What This Template Provides

- **AI Agent Configuration** - Pre-configured specialized agents (developers, testers, reviewers)
- **13-Step Worktree Workflow** - Isolated development with quality gates
- **Documentation Structure** - Professional documentation templates
- **Workflow Variants** - Multiple workflow options (Standard, Hotfix, Test-Only, etc.)
- **Quality Gates** - Automated testing, code review, and integration checks
- **Docker Integration** - Containerized development support

## 🚀 Quick Start

### 1. Copy Template to Your Project

```bash
# Copy the entire template to your project
cp -r c:/repos/claude-template/* /path/to/your/project/
```

### 2. Run Setup Script

```bash
cd /path/to/your/project
python setup_claude.py
```

The setup script will prompt you for:
- Project name
- Project description
- Tech stack (Backend/Frontend frameworks)
- Main branch name
- Repository URL
- Docker usage (yes/no)

### 3. Customize Agent Configuration

Edit `.agents/config.json` to:
- Adjust file watch patterns for your project structure
- Modify model selections (haiku/sonnet/opus)
- Configure workflow gates and thresholds
- Add/remove agents based on your needs

### 4. Update Documentation

Review and customize files in `.claude/` folder:
- `ARCHITECTURE.md` - Your system architecture
- `DEVELOPMENT.md` - Your development practices
- `DOCKER_GUIDE.md` - Your Docker setup (if applicable)
- `TESTING_GUIDE.md` - Your testing standards

### 5. Commit Claude Files

```bash
git add CLAUDE.md .claude/ .agents/ docs/
git commit -m "Add Claude Code configuration

- Add AI agent workflow
- Add documentation structure
- Add quality gates

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## 📁 Template Structure

```
claude-template/
├── README.md                   # This file
├── setup_claude.py             # Interactive setup script
├── CLAUDE.md                   # Main navigation hub (TEMPLATE)
├── .claude/                    # Documentation templates
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── DOCKER_GUIDE.md
│   ├── DEPLOYMENT.md
│   ├── ENVIRONMENT.md
│   ├── TESTING_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   ├── API_REFERENCE.md
│   └── IMPLEMENTATION_STATUS.md
├── .agents/                    # Agent configuration
│   └── config.json
├── docs/                       # Detailed workflow docs
│   ├── WORKFLOW_GUIDE.md
│   ├── WORKFLOW_IMPROVEMENTS.md
│   ├── WORKTREE_WORKFLOW.md
│   └── TESTING_GUIDE.md
└── scripts/                    # Scripts folder structure
    └── .gitkeep
```

## 🤖 Available Agents

### Development Agents
- **python-developer** - Backend Python/FastAPI development
- **react-frontend-dev** - Frontend React/Next.js development

### Testing Agents
- **python-test-specialist** - Write pytest tests
- **react-test-specialist** - Write React Testing Library tests
- **integration-tester** - Execute E2E tests (haiku model for cost savings)

### Review Agents
- **backend-code-reviewer** - Review Python code
- **frontend-code-reviewer** - Review React code

### Architecture & Infrastructure
- **software-architect** - Design architecture (opus model)
- **worktree-manager** - Manage isolated worktrees
- **docker-debugger** - Fix Docker issues
- **merge-conflict-resolver** - Resolve merge conflicts (opus model)

## 🔄 Workflow Variants

Choose the right workflow for your task:

### Standard Worktree (11 steps) ⭐ Most Common
- **Use For**: Regular features, enhancements
- **Steps**: Create worktree → Implement → Tests → Commit → Unit Tests → Review → Fix → E2E Tests → Push → Resolve Conflicts → Final Test → Merge → Cleanup
- **Time**: 25-35 minutes
- **Cost**: Medium

### Full Worktree (13 steps)
- **Use For**: New services, architectural changes
- **Adds**: Architecture design step (Step 0)
- **Time**: 35-50 minutes
- **Cost**: High

### Hotfix Worktree (9 steps) ⚡
- **Use For**: Production bugs, urgent fixes
- **Skips**: Test writing, E2E tests
- **Time**: 15-20 minutes
- **Cost**: Low

### Test-Only (7 steps) & Docs-Only (6 steps)
- For adding tests or documentation with isolation

### Legacy Direct (9 steps)
- For simple fixes without worktree isolation

## 🎛️ Customization Guide

### Adjusting for Different Tech Stacks

#### Non-Python Backend (Node.js, Go, Rust, etc.)
1. Edit `.agents/config.json`
2. Rename `python-developer` → `backend-developer`
3. Update `watches` patterns to match your file extensions
4. Modify `system_prompt` with language-specific best practices
5. Update test commands in workflow steps

#### Non-React Frontend (Vue, Svelte, Angular, etc.)
1. Edit `.agents/config.json`
2. Rename `react-frontend-dev` → `frontend-developer`
3. Update `watches` patterns
4. Modify test commands and review criteria

#### No Frontend
1. Remove frontend agents from `.agents/config.json`
2. Simplify `CLAUDE.md` to remove frontend references

#### No Docker
1. Set `worktree_based: false` in `.agents/config.json`
2. Remove Docker-related steps from workflow
3. Update documentation to remove Docker references

### Model Cost Optimization

The template uses optimized model selection:
- **haiku** - integration-tester (mechanical tasks, 60% cost savings)
- **sonnet** - developers, reviewers, managers (balanced quality/cost)
- **opus** - software-architect, merge-conflict-resolver (complex reasoning)

Adjust in `.agents/config.json` under each agent's `model` field.

### Workflow Gate Configuration

Edit `.agents/config.json` → `gates` section:
```json
{
  "test_runner": {
    "min_coverage": 80,        // Lower to 70 if needed
    "allow_failures": 0,       // Set to 1-2 for flexibility
    "blocking": true           // Set to false to make optional
  }
}
```

## 📚 Documentation Best Practices

### CLAUDE.md - Navigation Hub
- Keep concise (200-300 lines max)
- Focus on quick navigation
- Link to detailed docs in `.claude/` and `docs/`
- Update as project evolves

### .claude/ Folder - Focused Guides
- One topic per file
- 100-300 lines each
- Actionable information
- Examples and commands

### docs/ Folder - Detailed Documentation
- In-depth explanations
- Implementation details
- Phase documentation
- Complex workflows

## 🔧 Troubleshooting

### Setup Script Issues

**Python not found:**
```bash
# Use Python 3
python3 setup_claude.py
```

**File permissions:**
```bash
chmod +x setup_claude.py
```

### Agent Not Working

**Check configuration:**
1. Verify `.agents/config.json` is valid JSON
2. Check file watch patterns match your project structure
3. Ensure model names are correct (haiku/sonnet/opus)

**Test agent invocation:**
```bash
# In Claude Code CLI
> Can you invoke the python-developer agent to check configuration?
```

## 🤝 Contributing to Template

If you improve this template, consider:
1. Forking and sharing improvements
2. Adding support for new tech stacks
3. Creating specialized variants (mobile, ML, DevOps, etc.)
4. Improving documentation

## 📝 License

This template is provided as-is for use in any project. Customize freely.

## 🙏 Credits

Based on the Citadel.AI project workflow and agent system.

---

**Version**: 1.0.0
**Last Updated**: 2026-02-08
**Status**: Production Ready
