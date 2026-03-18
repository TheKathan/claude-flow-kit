# Contributing to Claude Flow Kit

Thank you for your interest in contributing! This guide explains how to get involved.

## How to Contribute

### Reporting Issues

- Use the [Bug Report](https://github.com/TheKathan/claude-flow-kit/issues/new?template=bug_report.yml) template for problems
- Use the [Feature Request](https://github.com/TheKathan/claude-flow-kit/issues/new?template=feature_request.yml) template for ideas
- Search existing issues before opening a new one

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main` (e.g., `feature/add-elixir-support`)
3. **Make your changes** following the guidelines below
4. **Test** the installer with your changes
5. **Submit a PR** using the pull request template

### Adding a New Language or Framework

This is the most common type of contribution. You'll need to create:

| File | Location | Purpose |
|---|---|---|
| Workflow guide | `docs/WORKFLOW_{TYPE}_{LANG}.md` | Step-by-step development workflow |
| Coding guide | `.claude/{LANG}_GUIDE.md` | Language-specific conventions |
| Agent config | `.agents/config_{type}_{lang}.json` | Agent definitions for the stack |
| Installer logic | `install.py` | Detection and download mapping |

Use existing language implementations as your reference (e.g., Python or Go files).

### Modifying the Installer

- `install.py` must remain a **single standalone file** with no dependencies beyond the Python standard library (3.7+)
- Test on at least two platforms (e.g., macOS + Windows, or Linux + Windows)
- Test both **fresh install** and **update mode** (`--mode update`)
- Ensure interactive prompts work correctly (never break stdin)

### Modifying Agents or Workflows

- Agent configs must be valid JSON
- Workflow files should follow the 14-step structure
- Use the existing naming convention: `WORKFLOW_{BACKEND|FRONTEND|INFRASTRUCTURE}_{LANG}.md`

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/claude-flow-kit.git
cd claude-flow-kit

# Test the installer locally
python install.py

# Run CI checks locally
# Markdown linting:
npx markdownlint-cli2 "**/*.md"

# JSON validation:
python -c "import json, glob; [json.load(open(f)) for f in glob.glob('.agents/*.json')]"
```

## Code Style

- **Python**: Follow PEP 8. The installer uses only stdlib modules.
- **Markdown**: Follow [markdownlint](https://github.com/DavidAnson/markdownlint) rules. The CI pipeline enforces this.
- **JSON**: Use 2-space indentation. Ensure valid JSON (no trailing commas).
- **Naming**: Use `snake_case` for files and scripts, `UPPER_CASE` for documentation.

## Commit Messages

- Use clear, descriptive commit messages
- Prefix with type: `feat:`, `fix:`, `docs:`, `ci:`, `refactor:`
- Example: `feat: add Elixir/Phoenix backend support`

## Review Process

1. A maintainer will review your PR within a few days
2. CI must pass (markdown lint, JSON validation, installer tests)
3. Changes may be requested — this is normal and collaborative
4. Once approved, a maintainer will merge your PR

## Questions?

Open a [discussion](https://github.com/TheKathan/claude-flow-kit/discussions) or comment on a relevant issue.
