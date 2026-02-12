# Claude Code Quick Reference

**Template Version**: 1.0.0

---

## 🚀 Setup (Choose One)

### Automated
```bash
cp -r c:/repos/claude-template/* /your/project/
cd /your/project
python setup_claude.py
```

### Manual
Replace all `{{PLACEHOLDERS}}` in files, then:
```bash
git add CLAUDE.md .claude/ .agents/ docs/ scripts/
git commit -m "Add Claude Code configuration"
```

---

## 🤖 Agents Overview

| Agent | Model | Purpose |
|-------|-------|---------|
| **worktree-manager** | sonnet | Create/merge/cleanup worktrees |
| **python-developer** | sonnet | Backend development |
| **react-frontend-dev** | sonnet | Frontend development |
| **python-test-specialist** | sonnet | Write backend tests |
| **react-test-specialist** | sonnet | Write frontend tests |
| **backend-code-reviewer** | sonnet | Review backend code |
| **frontend-code-reviewer** | sonnet | Review frontend code |
| **integration-tester** | **haiku** | Run tests (cost-optimized) |
| **software-architect** | **opus** | Design architecture |
| **docker-debugger** | sonnet | Fix Docker issues |
| **merge-conflict-resolver** | **opus** | Resolve conflicts |

---

## 🔄 Workflow Variants

### Standard (11 steps) ⭐ Most Common
**Use**: Regular features, enhancements
**Time**: 25-35 min | **Cost**: Medium

### Full (13 steps)
**Use**: New services, architectural changes
**Time**: 35-50 min | **Cost**: High

### Hotfix (9 steps) ⚡
**Use**: Production bugs, urgent fixes
**Time**: 15-20 min | **Cost**: Low

### Test-Only (7 steps)
**Use**: Add tests to existing code
**Time**: 15-20 min | **Cost**: Low

### Docs-Only (6 steps)
**Use**: Documentation updates
**Time**: 10-15 min | **Cost**: Very Low

---

## 📋 13-Step Workflow

```
0.  software-architect (optional)
1.  worktree-manager → Create worktree
2.  developer → Implement
3.  test-specialist → Write tests
4.  developer → Commit code + tests
5.  integration-tester → Unit tests [GATE]
6.  code-reviewer → Review [GATE]
7.  developer → Fix (if needed, loop 5-6)
8.  integration-tester → E2E tests [GATE]
9.  developer → Push branch
10. merge-conflict-resolver → Resolve [GATE]
11. integration-tester → Final test [GATE]
12. worktree-manager → Merge to main
13. worktree-manager → Cleanup
```

**Quality Gates**: 5 (Unit, Review, E2E, Conflicts, Final)
**Max Review Cycles**: 3

---

## 🎯 File Structure

```
your-project/
├── CLAUDE.md              # Navigation hub
├── .agents/
│   └── config.json       # Agent configuration
├── .claude/              # Focused docs (100-300 lines each)
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── DOCKER_GUIDE.md
│   ├── ENVIRONMENT.md
│   ├── TESTING_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── IMPLEMENTATION_STATUS.md
├── docs/                 # Detailed docs
│   ├── WORKFLOW_GUIDE.md
│   ├── TESTING_GUIDE.md
│   └── [phase docs]
└── scripts/              # ALL scripts here (not /tmp/)
    └── test_*.py
```

---

## 🔧 Common Customizations

### Non-Python Backend
```json
// .agents/config.json
{
  "backend-developer": {
    "name": "nodejs-developer",
    "watches": ["src/**/*.js", "src/**/*.ts"]
  }
}
```

### Non-React Frontend
```json
{
  "frontend-developer": {
    "name": "vue-developer",
    "watches": ["src/**/*.vue"]
  }
}
```

### No Frontend
Remove frontend agents from config.json

### No Docker
Set `"worktree_based": false` in config.json

---

## ⚙️ Agent Configuration Keys

```json
{
  "agents": {
    "agent-key": {
      "name": "agent-name",          // Used in Claude Code
      "type": "developer|reviewer|tester|architect|manager",
      "scope": "backend|frontend|all",
      "watches": ["file/**/*.ext"],  // File patterns
      "model": "haiku|sonnet|opus",  // Model selection
      "capabilities": [...],         // What it can do
      "system_prompt": "..."         // Instructions
    }
  },
  "workflow": {
    "max_review_cycles": 3,
    "auto_push_on_approval": true,
    "require_tests_pass": true,
    "steps": [...]
  },
  "gates": {
    "test_runner": {
      "min_coverage": 80,
      "allow_failures": 0,
      "blocking": true
    }
  }
}
```

---

## 🎨 Model Selection Guide

| Model | Speed | Cost | Use For |
|-------|-------|------|---------|
| haiku | ⚡⚡⚡ | 💰 | Testing, simple checks (60% savings) |
| sonnet | ⚡⚡ | 💰💰 | Development, reviews (default) |
| opus | ⚡ | 💰💰💰 | Architecture, complex conflicts |

---

## 📝 Template Placeholders

Find and replace in all files:

| Placeholder | Example |
|-------------|---------|
| `{{PROJECT_NAME}}` | "MyApp" |
| `{{PROJECT_DESCRIPTION}}` | "A task manager" |
| `{{BACKEND_FRAMEWORK}}` | "FastAPI" |
| `{{BACKEND_LANGUAGE}}` | "Python 3.11" |
| `{{BACKEND_FOLDER}}` | "app" |
| `{{FRONTEND_FRAMEWORK}}` | "Next.js 14" |
| `{{FRONTEND_FOLDER}}` | "dashboard" |
| `{{MAIN_BRANCH}}` | "main" |
| `{{REPO_URL}}` | "https://github.com/..." |
| `{{USES_DOCKER}}` | "true" |
| `{{HAS_FRONTEND}}` | "true" |

---

## ✅ Post-Setup Checklist

- [ ] All placeholders replaced
- [ ] Agent config matches tech stack
- [ ] File watch patterns correct
- [ ] Test commands updated
- [ ] Documentation customized
- [ ] Scripts folder created
- [ ] .gitignore updated
- [ ] All committed to git

---

## 📚 Key Documents

| Document | Purpose | Lines |
|----------|---------|-------|
| **CLAUDE.md** | Navigation hub | 200-300 |
| **.claude/ARCHITECTURE.md** | System design | 100-300 |
| **.claude/DEVELOPMENT.md** | Dev practices | 200-400 |
| **docs/WORKFLOW_GUIDE.md** | Workflow details | 300-500 |

---

## 🆘 Quick Troubleshooting

**Agent not working?**
1. Check `.agents/config.json` is valid JSON
2. Verify file watch patterns
3. Confirm model names (haiku/sonnet/opus)

**Tests failing?**
1. Check Docker containers running
2. Verify environment variables
3. Check test commands in config

**Placeholders not replaced?**
Run `grep -r "{{" .` to find them

---

## 💡 Pro Tips

1. **Start with Standard Workflow** for most features
2. **Use haiku for testing** to save 60% on costs
3. **Keep CLAUDE.md under 300 lines** - link to detailed docs
4. **Update docs as you go** - keep them accurate
5. **Review agent config regularly** - adjust as project evolves
6. **Scripts go in scripts/ folder** - not /tmp/
7. **Commit template first** before starting dev work

---

## 📞 Getting Help

- **Template Issues**: See TEMPLATE_USAGE.md
- **Workflow Questions**: See docs/WORKFLOW_GUIDE.md
- **Tech Stack Adaptation**: See TEMPLATE_USAGE.md § Tech Stack Adaptation
- **Agent Configuration**: See .agents/config.json comments

---

**Quick Start**: `python setup_claude.py`
**Full Guide**: See TEMPLATE_USAGE.md
**Template Version**: 1.0.0
