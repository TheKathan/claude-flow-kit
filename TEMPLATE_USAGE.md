# Claude Code Template - Usage Guide

**Last Updated**: 2026-02-08
**Version**: 1.0.0

---

## 📋 What Was Created

This template provides a complete Claude Code workflow setup that can be customized for any project:

### ✅ Core Files

```
claude-template/
├── README.md                       # Template overview and quick start
├── TEMPLATE_USAGE.md              # This file - detailed usage guide
├── setup_claude.py                 # Interactive setup script
├── CLAUDE.md                       # Main navigation hub (with placeholders)
├── .agents/
│   └── config.json                # Agent configuration (11 agents)
├── .claude/                       # Documentation templates
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── DOCKER_GUIDE.md
│   ├── ENVIRONMENT.md
│   ├── TROUBLESHOOTING.md
│   └── [other docs]
├── docs/                          # Workflow documentation
│   ├── WORKFLOW_GUIDE.md
│   ├── TESTING_GUIDE.md
│   └── [other workflow docs]
└── scripts/                       # Scripts folder structure
    └── .gitkeep
```

---

## 🚀 Quick Start (3 Steps)

### Option A: Automated Setup (Recommended)

```bash
# 1. Copy template to your project
cp -r c:/repos/claude-template/* /path/to/your/project/

# 2. Run setup script (interactive)
cd /path/to/your/project
python setup_claude.py

# 3. Customize and commit
git add CLAUDE.md .claude/ .agents/ docs/ scripts/
git commit -m "Add Claude Code configuration"
```

### Option B: Manual Setup

```bash
# 1. Copy template files
cp -r c:/repos/claude-template/* /path/to/your/project/

# 2. Manual find-and-replace in all files:
# {{PROJECT_NAME}} → Your project name
# {{PROJECT_DESCRIPTION}} → Your project description
# {{BACKEND_FRAMEWORK}} → Your backend framework (e.g., FastAPI, Express, Django)
# {{BACKEND_LANGUAGE}} → Your backend language (e.g., Python 3.11, Node.js 20)
# {{FRONTEND_FRAMEWORK}} → Your frontend framework (e.g., Next.js 14, React, Vue)
# {{MAIN_BRANCH}} → Your main branch name (main or master)
# {{REPO_URL}} → Your repository URL
# [See complete list below]

# 3. Edit .agents/config.json for your tech stack

# 4. Commit
git add CLAUDE.md .claude/ .agents/ docs/ scripts/
git commit -m "Add Claude Code configuration"
```

---

## 🔧 Customization Guide

### Placeholder Reference

All template files contain these placeholders:

| Placeholder | Description | Example |
|------------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | "MyAwesomeApp" |
| `{{PROJECT_DESCRIPTION}}` | Short description | "A task management application" |
| `{{REPO_URL}}` | Repository URL | "https://github.com/user/repo" |
| `{{BACKEND_FRAMEWORK}}` | Backend framework | "FastAPI", "Express", "Django" |
| `{{BACKEND_LANGUAGE}}` | Backend language | "Python 3.11", "Node.js 20" |
| `{{BACKEND_FOLDER}}` | Backend code folder | "app", "src", "backend" |
| `{{FRONTEND_FRAMEWORK}}` | Frontend framework | "Next.js 14", "React", "Vue" |
| `{{FRONTEND_LANGUAGE}}` | Frontend language | "TypeScript", "JavaScript" |
| `{{FRONTEND_FOLDER}}` | Frontend code folder | "dashboard", "frontend", "client" |
| `{{MAIN_BRANCH}}` | Main branch name | "main", "master" |
| `{{USES_DOCKER}}` | Docker usage | "true", "false" |
| `{{HAS_FRONTEND}}` | Has frontend | "true", "false" |
| `{{TEST_COMMAND}}` | Test command | "pytest", "npm test" |
| `{{MIGRATION_COMMAND}}` | Migration command | "alembic upgrade head", "npm run migrate" |
| `{{CURRENT_DATE}}` | Current date | "2026-02-08" |

### setup_claude.py Interactive Prompts

The setup script will ask you:

1. **Project name**: `MyAwesomeApp`
2. **Project description**: `A task management application`
3. **Repository URL**: `https://github.com/user/myapp`
4. **Backend framework**: `FastAPI` / `Express` / `Django` / etc.
5. **Backend language**: `Python 3.11` / `Node.js 20` / etc.
6. **Backend folder**: `app` / `src` / `backend`
7. **Has frontend?**: Yes/No
8. **Frontend framework** (if yes): `Next.js 14` / `React` / `Vue`
9. **Frontend language** (if yes): `TypeScript` / `JavaScript`
10. **Frontend folder** (if yes): `dashboard` / `frontend` / `client`
11. **Uses Docker?**: Yes/No
12. **Main branch**: `main` / `master`
13. **Default workflow variant**: Standard / Full / Hotfix

Script will then:
- Replace all placeholders in template files
- Update agent configuration
- Create necessary directories
- Provide next steps

---

## 🎯 Tech Stack Adaptation

### Backend: Non-Python (Node.js, Go, Rust, etc.)

1. **Edit `.agents/config.json`**:
   ```json
   {
     "agents": {
       "backend-developer": {
         "name": "nodejs-developer",  // Rename
         "watches": ["src/**/*.js", "src/**/*.ts"],  // Update patterns
         "system_prompt": "You are a Node.js backend developer..."  // Update prompt
       }
     }
   }
   ```

2. **Update test commands** in workflow steps:
   ```json
   {
     "workflow": {
       "steps": [
         {
           "step": 5,
           "commands": {
             "backend": "npm test"  // Change from pytest
           }
         }
       ]
     }
   }
   ```

3. **Update documentation**:
   - `.claude/DEVELOPMENT.md` - Update code style guidelines
   - `.claude/TESTING_GUIDE.md` - Update test framework
   - `docs/WORKFLOW_GUIDE.md` - Update commands

### Frontend: Non-React (Vue, Svelte, Angular, etc.)

1. **Edit `.agents/config.json`**:
   ```json
   {
     "agents": {
       "frontend-developer": {
         "name": "vue-developer",  // Rename
         "watches": ["src/**/*.vue"],  // Update patterns
         "system_prompt": "You are a Vue.js frontend developer..."  // Update
       }
     }
   }
   ```

2. **Update review criteria**:
   ```json
   {
     "agents": {
       "frontend-reviewer": {
         "review_criteria": [
           "vue_best_practices",  // Update from react_best_practices
           "composition_api",
           "accessibility"
         ]
       }
     }
   }
   ```

### No Frontend Projects

1. **Remove frontend agents** from `.agents/config.json`:
   - Delete `frontend-developer` section
   - Delete `frontend-reviewer` section
   - Delete `react-tester` section

2. **Update `CLAUDE.md`**:
   - Remove frontend sections
   - Remove frontend workflow examples

3. **Simplify documentation**:
   - No need for frontend testing guide sections
   - Focus on backend documentation

### No Docker Projects

1. **Edit `.agents/config.json`**:
   ```json
   {
     "workflow": {
       "worktree_based": false,  // Disable worktree workflow
     }
   }
   ```

2. **Remove docker-debugger agent**

3. **Update test commands** (remove `docker-compose exec`)

4. **Delete `.claude/DOCKER_GUIDE.md`**

5. **Update `CLAUDE.md`** to remove Docker references

---

## 🤖 Agent Configuration

### Understanding .agents/config.json

The configuration file has these main sections:

#### 1. Agents Definition

```json
{
  "agents": {
    "backend-developer": {
      "name": "python-developer",  // Agent name used in Claude Code
      "type": "developer",  // Agent type
      "scope": "backend",  // Backend or frontend or all
      "watches": ["app/**/*.py"],  // File patterns to watch
      "reviewer": "backend-reviewer",  // Linked reviewer
      "capabilities": [...],  // What agent can do
      "model": "sonnet",  // haiku, sonnet, or opus
      "tools": [...],  // Available tools
      "system_prompt": "..."  // Agent instructions
    }
  }
}
```

#### 2. Workflow Definition

```json
{
  "workflow": {
    "max_review_cycles": 3,
    "auto_push_on_approval": true,
    "require_tests_pass": true,
    "require_integration_tests_pass": true,
    "steps": [
      {
        "step": 1,
        "agent": "worktree-manager",
        "action": "create_worktree",
        "required": true
      }
    ]
  }
}
```

#### 3. Workflow Variants

```json
{
  "workflow_variants": {
    "standard": {
      "steps": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
      "use_for": ["feature", "enhancement"]
    },
    "hotfix": {
      "steps": [1, 2, 4, 5, 6, 9, 10, 12, 13],
      "use_for": ["bug_fix", "urgent_fix"]
    }
  }
}
```

#### 4. Quality Gates

```json
{
  "gates": {
    "test_runner": {
      "min_coverage": 80,
      "allow_failures": 0,
      "blocking": true
    }
  }
}
```

### Model Selection Guide

| Model | Speed | Cost | Use Cases |
|-------|-------|------|-----------|
| **haiku** | Fastest | Lowest | Mechanical tasks (test execution, simple checks) |
| **sonnet** | Fast | Medium | Development, reviews, most tasks |
| **opus** | Slower | Highest | Architecture, complex conflict resolution |

**Cost Optimization**:
- integration-tester: Use **haiku** (60% cost savings)
- software-architect: Use **opus** (best quality)
- Developers/reviewers: Use **sonnet** (balanced)

---

## 📝 Documentation Customization

### Files to Update

#### 1. CLAUDE.md (Navigation Hub)
- Keep concise (200-300 lines)
- Update all placeholders
- Add project-specific sections
- Link to detailed docs

#### 2. .claude/ARCHITECTURE.md
- Document your architecture patterns
- Add system diagrams
- Document design decisions
- List tech stack details

#### 3. .claude/DEVELOPMENT.md
- Update code style guidelines
- Add project-specific conventions
- Document development workflow
- Add security best practices

#### 4. .claude/DOCKER_GUIDE.md (if using Docker)
- List your actual services
- Update port numbers
- Add project-specific commands
- Document volume structure

#### 5. .claude/ENVIRONMENT.md
- List all environment variables
- Provide example values
- Document required vs optional
- Add security guidelines

#### 6. docs/WORKFLOW_GUIDE.md
- Customize workflow steps
- Add project-specific examples
- Update agent names
- Add troubleshooting tips

#### 7. docs/TESTING_GUIDE.md
- Update test framework details
- Add project-specific test patterns
- Document test data setup
- Add coverage requirements

---

## ✅ Verification Checklist

After setup, verify:

- [ ] All placeholders replaced in all files
- [ ] Agent configuration matches your tech stack
- [ ] File watch patterns match your project structure
- [ ] Test commands are correct
- [ ] Migration commands are correct
- [ ] Environment variables documented
- [ ] Documentation links work
- [ ] Scripts folder created
- [ ] `.gitignore` updated (don't commit `.env`)
- [ ] Everything committed to git

---

## 🎨 Example: Setting Up for Express + React Project

```bash
# 1. Copy template
cp -r c:/repos/claude-template/* /path/to/express-react-app/

# 2. Run setup (answers shown)
cd /path/to/express-react-app
python setup_claude.py

# Prompts and answers:
# Project name: TaskMaster
# Description: A modern task management application
# Backend framework: Express.js
# Backend language: Node.js 20
# Backend folder: server
# Has frontend? Yes
# Frontend framework: React 18
# Frontend language: TypeScript
# Frontend folder: client
# Uses Docker? Yes
# Main branch: main

# 3. Manual adjustments to .agents/config.json:

# Update backend developer:
{
  "backend-developer": {
    "name": "express-developer",
    "watches": ["server/**/*.js", "server/**/*.ts"],
    "system_prompt": "You are an Express.js backend developer..."
  }
}

# Update test commands:
{
  "workflow": {
    "steps": [
      {
        "step": 5,
        "commands": {
          "backend": "npm test",
          "frontend": "npm test"
        }
      }
    ]
  }
}

# 4. Update documentation
# - .claude/DEVELOPMENT.md: Add JavaScript/TypeScript style guide
# - .claude/TESTING_GUIDE.md: Add Jest/Mocha examples
# - docs/WORKFLOW_GUIDE.md: Update command examples

# 5. Commit
git add .
git commit -m "Add Claude Code configuration for TaskMaster

- Configure Express.js backend developer agent
- Configure React frontend developer agent
- Set up 13-step worktree workflow
- Add quality gates and testing requirements

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## 🔄 Keeping Template Updated

If you improve the template for your project:

1. **Extract improvements** back to template
2. **Generalize** project-specific code
3. **Add placeholders** for customization
4. **Update documentation**
5. **Share** with team or community

---

## 🆘 Troubleshooting Template Setup

### setup_claude.py Fails

**Python not found**:
```bash
python3 setup_claude.py  # Try python3
```

**File permission error**:
```bash
chmod +x setup_claude.py
```

### Placeholders Not Replaced

**Manual replacement**:
```bash
# Find all files with placeholders
grep -r "{{PROJECT_NAME}}" .

# Replace manually in each file
```

### Agent Not Working

**Check configuration**:
1. Verify `.agents/config.json` is valid JSON
2. Check file watch patterns
3. Ensure model names are correct (haiku/sonnet/opus)
4. Verify system prompts are appropriate

**Test agent**:
```bash
# In Claude Code CLI
> Can you invoke the python-developer agent to check configuration?
```

---

## 📚 Additional Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Agent Configuration Reference](#) *(add your link)*
- [Workflow Best Practices](#) *(add your link)*
- [Example Projects Using This Template](#) *(add your link)*

---

## 💡 Tips

1. **Start with Standard Workflow** (11 steps) for most features
2. **Use Haiku for testing** to save costs
3. **Keep CLAUDE.md under 300 lines** - link to detailed docs
4. **Update documentation as you go** - keep it accurate
5. **Commit template files first** before starting development
6. **Review agent configuration regularly** - adjust as needed
7. **Share improvements** with your team

---

**Questions?** Check README.md or create an issue in the template repository.

---

**Template Version**: 1.0.0
**Last Updated**: 2026-02-08
**Status**: Production Ready
