# {{PROJECT_NAME}} - Claude Code Configuration

## Project Overview

{{PROJECT_DESCRIPTION}}

**Tech Stack**:
- Backend: {{BACKEND_FRAMEWORK}} ({{BACKEND_LANGUAGE}})
{{#if HAS_FRONTEND}}- Frontend: {{FRONTEND_FRAMEWORK}} ({{FRONTEND_LANGUAGE}}){{/if}}
{{#if HAS_INFRASTRUCTURE}}- Infrastructure: {{INFRASTRUCTURE_TOOL}}{{/if}}
{{#if USES_DOCKER}}- Containerization: Docker{{/if}}

**Repository**: {{REPO_URL}}

---

## 🚀 Quick Start

### Prerequisites

- Git
{{#if USES_DOCKER}}- Docker & Docker Compose{{/if}}
{{#if BACKEND_LANGUAGE includes "Python"}}- Python 3.11+{{/if}}
{{#if BACKEND_LANGUAGE includes "C#"}}- .NET 8+ SDK{{/if}}
{{#if BACKEND_LANGUAGE includes "Node"}}- Node.js 20+{{/if}}
{{#if BACKEND_LANGUAGE includes "Go"}}- Go 1.21+{{/if}}

### Installation

```bash
# Clone the repository
git clone {{REPO_URL}}
cd {{PROJECT_NAME}}

{{#if USES_DOCKER}}# Start services with Docker
docker-compose up -d

# Verify services
docker-compose ps
{{else}}# Install dependencies
{{#if BACKEND_LANGUAGE includes "Python"}}pip install -r requirements.txt{{/if}}
{{#if BACKEND_LANGUAGE includes "Node"}}npm install{{/if}}
{{#if BACKEND_LANGUAGE includes "C#"}}dotnet restore{{/if}}
{{#if BACKEND_LANGUAGE includes "Go"}}go mod download{{/if}}
{{/if}}
```

---

## 📚 Documentation Navigation

### Getting Started
{{#if USES_DOCKER}}- **[Docker Guide](.claude/DOCKER_GUIDE.md)** - Container setup and commands{{/if}}
- **[Environment Variables](.claude/ENVIRONMENT.md)** - Configuration and secrets
- **[Architecture](.claude/ARCHITECTURE.md)** - System design and tech stack

### Development Workflows

#### Backend Workflow
{{#if BACKEND_LANGUAGE includes "Python"}}
- **[Python Workflow](docs/WORKFLOW_BACKEND_PYTHON.md)** - 13-step workflow for Python/FastAPI backend
- **[Python Guide](.claude/PYTHON_GUIDE.md)** - Python coding standards
{{/if}}
{{#if BACKEND_LANGUAGE includes "C#"}}
- **[.NET Workflow](docs/WORKFLOW_BACKEND_DOTNET.md)** - 13-step workflow for .NET/ASP.NET Core backend
- **[.NET Guide](.claude/DOTNET_GUIDE.md)** - C# coding standards
{{/if}}
{{#if BACKEND_LANGUAGE includes "Node"}}
- **[Node.js Workflow](docs/WORKFLOW_BACKEND_NODEJS.md)** - 13-step workflow for Node.js/Express backend
- **[Node.js Guide](.claude/NODEJS_GUIDE.md)** - Node.js coding standards
{{/if}}
{{#if BACKEND_LANGUAGE includes "Go"}}
- **[Go Workflow](docs/WORKFLOW_BACKEND_GO.md)** - 13-step workflow for Go backend
- **[Go Guide](.claude/GO_GUIDE.md)** - Go coding standards
{{/if}}

{{#if HAS_FRONTEND}}#### Frontend Workflow
{{#if FRONTEND_FRAMEWORK includes "React" or FRONTEND_FRAMEWORK includes "Next"}}
- **[React Workflow](docs/WORKFLOW_FRONTEND_REACT.md)** - 13-step workflow for React/Next.js frontend
- **[React Guide](.claude/REACT_GUIDE.md)** - React coding standards
{{/if}}
{{#if FRONTEND_FRAMEWORK includes "Vue"}}
- **[Vue Workflow](docs/WORKFLOW_FRONTEND_VUE.md)** - 13-step workflow for Vue.js/Nuxt frontend
- **[Vue Guide](.claude/VUE_GUIDE.md)** - Vue coding standards
{{/if}}
{{#if FRONTEND_FRAMEWORK includes "Angular"}}
- **[Angular Workflow](docs/WORKFLOW_FRONTEND_ANGULAR.md)** - 13-step workflow for Angular frontend
- **[Angular Guide](.claude/ANGULAR_GUIDE.md)** - Angular coding standards
{{/if}}
{{/if}}

{{#if HAS_INFRASTRUCTURE}}#### Infrastructure Workflow
{{#if INFRASTRUCTURE_TOOL includes "Terraform"}}
- **[Terraform Workflow](docs/WORKFLOW_INFRASTRUCTURE_TERRAFORM.md)** - Terraform IaC workflow
- **[Terraform Guide](.claude/TERRAFORM_GUIDE.md)** - Terraform best practices
{{/if}}
{{/if}}

### Testing
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Testing standards and practices

### Deployment & Operations
- **[Deployment Guide](.claude/DEPLOYMENT.md)** - Production deployment
- **[Troubleshooting](.claude/TROUBLESHOOTING.md)** - Common issues and fixes
{{#if BACKEND_LANGUAGE}}- **[API Reference](.claude/API_REFERENCE.md)** - API endpoints and usage{{/if}}

### Project Status
- **[Implementation Status](.claude/IMPLEMENTATION_STATUS.md)** - What's done, what's next

---

## 🤖 Development Workflow Overview

This project uses specialized AI agents following a **13-step worktree-based workflow** with quality gates.

### Workflow Principles

- **Isolated worktrees** for each feature/bugfix{{#if USES_DOCKER}} with separate Docker environments{{/if}}
- **Mandatory quality gates**: tests, code review, integration tests
- **Automated conflict resolution** before merge
- **Automated cleanup** after merge

### 13-Step Workflow

All workflows follow the same structure:

```
Step 0:  [OPTIONAL] software-architect      → Design architecture
Step 1:  worktree-manager                   → Create worktree{{#if USES_DOCKER}} + Docker{{/if}}
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
Step 12: worktree-manager                   → Merge to {{MAIN_BRANCH}}, push
Step 13: worktree-manager                   → Cleanup worktree{{#if USES_DOCKER}} + Docker{{/if}}
```

**Quality Gates** (⚠️ Blocking):
1. Unit tests must pass (80%+ coverage)
2. Code review must approve
3. Integration tests must pass
4. Merge conflicts must be resolved
5. Final integration test must pass

**See your language-specific workflow guide for detailed commands and examples.**

---

## Workflow Variants

- **Standard Workflow (11 steps)** - Regular features (80% of work) - 25-35 min
- **Full Workflow (13 steps)** - New services, architectural changes - 35-50 min
- **Hotfix Workflow (9 steps)** - Production bugs, urgent fixes - 15-20 min

**Details** → See your workflow guide

---

## Key Principles

1. {{#if USES_DOCKER}}**Docker-First**: All development in containers{{else}}**Local-First**: Consistent development environment{{/if}}
2. **Testing First**: 80%+ coverage required
3. **Security-First**: Security reviews mandatory
4. **Documentation Required**: No code without docs
5. **Quality Gates**: Blocking gates prevent bad code from merging
6. **Script Management**: ALL scripts in `scripts/` folder (never `/tmp/`)

---

## Need Help?

### Common Tasks

- **Start development** → Check your workflow guide
{{#if USES_DOCKER}}- **Docker issues** → [Docker Guide](.claude/DOCKER_GUIDE.md){{/if}}
- **Fix issues** → [Troubleshooting](.claude/TROUBLESHOOTING.md)
- **Check status** → [Implementation Status](.claude/IMPLEMENTATION_STATUS.md)

### Resources

- **Workflows**: See `docs/WORKFLOW_*.md` for language-specific workflows
- **Standards**: See `.claude/*_GUIDE.md` for coding standards
- **Testing**: See `docs/TESTING_GUIDE.md` for testing practices

---

**Version**: 2.0
**Status**: Active Development
**Last Updated**: {{CURRENT_DATE}}
