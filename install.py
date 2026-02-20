#!/usr/bin/env python3
"""
Claude Code Template Installer

Download and run:
  curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py | python3

Or download first:
  curl -O https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py
  python3 install.py
"""

import os
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

GITHUB_RAW_URL = "https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main"

def prompt(question: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    if default:
        response = input(f"{question} [{default}]: ").strip()
        return response if response else default
    else:
        response = ""
        while not response:
            response = input(f"{question}: ").strip()
        return response

def yes_no(question: str, default: bool = True) -> bool:
    """Prompt for yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{question} [{default_str}]: ").strip().lower()
    if not response:
        return default
    return response in ['y', 'yes']

def download_file(url: str, dest: Path) -> bool:
    """Download file from URL to destination."""
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        print(f"  ✅ Downloaded {dest.name}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to download {dest.name}: {e}")
        return False

def detect_language(backend_language: Optional[str]) -> Optional[str]:
    """Detect primary language from backend_language string."""
    if not backend_language:
        return None

    language_lower = backend_language.lower()
    if "python" in language_lower:
        return "python"
    elif "c#" in language_lower or ".net" in language_lower:
        return "dotnet"
    elif "node" in language_lower or "javascript" in language_lower or "typescript" in language_lower:
        return "nodejs"
    elif "go" in language_lower or "golang" in language_lower:
        return "go"
    return None

def detect_frontend_framework(frontend_framework: Optional[str]) -> Optional[str]:
    """Detect frontend framework identifier."""
    if not frontend_framework:
        return None

    framework_lower = frontend_framework.lower()
    if "react" in framework_lower or "next" in framework_lower:
        return "react"
    elif "vue" in framework_lower or "nuxt" in framework_lower:
        return "vue"
    elif "angular" in framework_lower:
        return "angular"
    return None

def detect_infrastructure_tool(infrastructure_tool: Optional[str]) -> Optional[str]:
    """Detect infrastructure tool identifier."""
    if not infrastructure_tool:
        return None

    tool_lower = infrastructure_tool.lower()
    if "terraform" in tool_lower:
        return "terraform"
    return None

def _substitute_claude_md(file_path: Path, replacements: Dict[str, str]):
    """Substitute simple {{VAR}} placeholders in a downloaded template file."""
    if not file_path.exists():
        return
    try:
        content = file_path.read_text(encoding='utf-8')
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        file_path.write_text(content, encoding='utf-8')
        print(f"  ✅ Substituted variables in {file_path.name}")
    except Exception as e:
        print(f"  ⚠️  Could not substitute variables in {file_path.name}: {e}")


def main():
    print("=" * 70)
    print("Claude Code Template Installer")
    print("=" * 70)
    print("\nThis installer will download and set up the Claude Code template.\n")

    # Get project information
    print("📋 Project Information")
    print("-" * 70)
    project_name = prompt("Project name", "MyProject")
    project_description = prompt("Project description", "A great project")
    repo_url = prompt("Repository URL (optional)", "https://github.com/user/repo")

    # Component selection - ALL OPTIONAL
    print("\n🎯 Component Selection (ALL OPTIONAL)")
    print("-" * 70)
    print("You can choose backend, frontend, infrastructure, or any combination.")
    print("All components are optional - select only what you need.\n")

    # Backend selection (OPTIONAL)
    has_backend = yes_no("Does your project have a backend?", True)

    backend_language, backend_framework, backend_folder = None, None, None
    if has_backend:
        print("\nChoose backend type:")
        print("1. Python (FastAPI, Django, Flask)")
        print("2. Node.js (Express, NestJS, Fastify)")
        print("3. .NET (ASP.NET Core)")
        print("4. Go (Gin, Echo, Fiber)")
        print("5. Other (manual setup)")
        backend_choice = prompt("Backend choice", "1")

        if backend_choice == "1":
            backend_framework = prompt("Backend framework", "FastAPI")
            backend_language = prompt("Backend language", "Python 3.11")
            backend_folder = prompt("Backend code folder", "app")
        elif backend_choice == "2":
            backend_framework = prompt("Backend framework", "Express.js")
            backend_language = prompt("Backend language", "Node.js 20")
            backend_folder = prompt("Backend code folder", "src")
        elif backend_choice == "3":
            backend_framework = prompt("Backend framework", "ASP.NET Core 8")
            backend_language = prompt("Backend language", "C# 12")
            backend_folder = prompt("Backend code folder", "src")
        elif backend_choice == "4":
            backend_framework = prompt("Backend framework", "Gin")
            backend_language = prompt("Backend language", "Go 1.21")
            backend_folder = prompt("Backend code folder", "cmd/api")
        else:
            print("  Manual backend setup selected - no backend workflow will be downloaded")
            has_backend = False

    # Frontend selection (OPTIONAL)
    has_frontend = yes_no("\nDoes your project have a frontend?", False)

    frontend_framework, frontend_language, frontend_folder = None, None, None
    if has_frontend:
        print("\nChoose frontend framework:")
        print("1. React / Next.js")
        print("2. Vue / Nuxt")
        print("3. Angular")
        print("4. Other (manual setup)")
        frontend_choice = prompt("Frontend choice", "1")

        if frontend_choice == "1":
            frontend_framework = prompt("Frontend framework", "Next.js 14")
            frontend_language = prompt("Frontend language", "TypeScript")
            frontend_folder = prompt("Frontend code folder", "dashboard")
        elif frontend_choice == "2":
            frontend_framework = prompt("Frontend framework", "Vue 3")
            frontend_language = prompt("Frontend language", "TypeScript")
            frontend_folder = prompt("Frontend code folder", "frontend")
        elif frontend_choice == "3":
            frontend_framework = prompt("Frontend framework", "Angular 17")
            frontend_language = prompt("Frontend language", "TypeScript")
            frontend_folder = prompt("Frontend code folder", "frontend")
        else:
            print("  Manual frontend setup selected - no frontend workflow will be downloaded")
            has_frontend = False

    # Infrastructure selection (OPTIONAL)
    has_infrastructure = yes_no("\nDoes your project use Infrastructure-as-Code?", False)

    infrastructure_tool = None
    if has_infrastructure:
        print("\nChoose infrastructure tool:")
        print("1. Terraform")
        print("2. Other (manual setup)")
        infra_choice = prompt("Choice", "1")

        if infra_choice == "1":
            infrastructure_tool = "Terraform"
        else:
            print("  Manual infrastructure setup selected - no infrastructure workflow will be downloaded")
            has_infrastructure = False

    # Validate at least one component selected
    if not has_backend and not has_frontend and not has_infrastructure:
        print("\n⚠️  Warning: No components selected!")
        print("You must select at least one component (backend, frontend, or infrastructure).")
        print("Exiting installer.")
        return

    # Docker configuration
    print("\n🐳 Docker Configuration")
    print("-" * 70)
    uses_docker = yes_no("Does your project use Docker?", True)

    # Git configuration
    print("\n🌿 Git Configuration")
    print("-" * 70)
    main_branch = prompt("Main branch name", "main")

    # Detect selected components
    backend_lang = detect_language(backend_language) if has_backend else None
    frontend_lang = detect_frontend_framework(frontend_framework) if has_frontend else None
    infra_tool = detect_infrastructure_tool(infrastructure_tool) if has_infrastructure else None

    print(f"\n🔍 Detected components:")
    if backend_lang:
        print(f"  - Backend: {backend_lang}")
    if frontend_lang:
        print(f"  - Frontend: {frontend_lang}")
    if infra_tool:
        print(f"  - Infrastructure: {infra_tool}")

    # Download core files
    print("\n📥 Downloading core template files...")
    current_dir = Path.cwd()

    # Download CLAUDE.md and substitute template variables
    download_file(f"{GITHUB_RAW_URL}/CLAUDE.md", current_dir / "CLAUDE.md")
    _substitute_claude_md(current_dir / "CLAUDE.md", {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_DESCRIPTION}}": project_description,
        "{{REPO_URL}}": repo_url,
        "{{BACKEND_FRAMEWORK}}": backend_framework or "",
        "{{BACKEND_LANGUAGE}}": backend_language or "",
        "{{FRONTEND_FRAMEWORK}}": frontend_framework or "",
        "{{FRONTEND_LANGUAGE}}": frontend_language or "",
        "{{MAIN_BRANCH}}": main_branch,
        "{{CURRENT_DATE}}": __import__('datetime').date.today().isoformat(),
        "{{USES_DOCKER}}": "true" if uses_docker else "false",
        "{{HAS_FRONTEND}}": "true" if has_frontend else "false",
        "{{HAS_INFRASTRUCTURE}}": "true" if has_infrastructure else "false",
        "{{INFRASTRUCTURE_TOOL}}": infrastructure_tool or "",
    })

    # Create directories
    (current_dir / ".claude").mkdir(exist_ok=True)
    (current_dir / ".agents").mkdir(exist_ok=True)
    (current_dir / "docs").mkdir(exist_ok=True)
    (current_dir / "scripts").mkdir(exist_ok=True)

    # Download worktree management scripts
    print("\n🔧 Downloading worktree management scripts...")
    worktree_scripts = [
        "worktree_create.py",
        "worktree_merge.py",
        "worktree_cleanup.py",
        "worktree_create_pr.py",
        "worktree_check_pr_status.py",
        "worktree_poll_pr.py",
    ]
    for script in worktree_scripts:
        download_file(f"{GITHUB_RAW_URL}/scripts/{script}", current_dir / "scripts" / script)

    # Download agent definition files (.claude/agents/)
    print("\n🤖 Downloading agent definition files...")
    agents_dir = current_dir / ".claude" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Common agents — always installed
    common_agents = [
        "software-architect.md",
        "worktree-manager.md",
        "docker-debugger.md",
        "merge-conflict-resolver.md",
        "integration-tester.md",
        "project-status-reviewer.md",
    ]
    for agent in common_agents:
        download_file(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # Backend agents — conditional on selected language
    backend_agent_map = {
        "python":  ["python-developer.md", "python-test-specialist.md", "backend-code-reviewer.md"],
        "nodejs":  ["nodejs-developer.md", "nodejs-test-specialist.md", "backend-code-reviewer.md"],
        "dotnet":  ["dotnet-developer.md", "dotnet-test-specialist.md", "backend-code-reviewer.md"],
        "go":      ["go-developer.md", "go-test-specialist.md", "backend-code-reviewer.md"],
    }
    if backend_lang and backend_lang in backend_agent_map:
        for agent in backend_agent_map[backend_lang]:
            download_file(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # Frontend agents — conditional on selected framework
    frontend_agent_map = {
        "react":   ["react-frontend-dev.md", "react-test-specialist.md", "frontend-code-reviewer.md"],
        "vue":     ["vue-developer.md", "vue-test-specialist.md", "frontend-code-reviewer.md"],
        "angular": ["angular-developer.md", "angular-test-specialist.md", "frontend-code-reviewer.md"],
    }
    if frontend_lang and frontend_lang in frontend_agent_map:
        for agent in frontend_agent_map[frontend_lang]:
            download_file(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # Infrastructure agents — conditional on selected tool
    if infra_tool and infra_tool.lower() == "terraform":
        for agent in ["terraform-developer.md", "terraform-test-specialist.md", "infrastructure-code-reviewer.md"]:
            download_file(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # Download selected workflows and guides
    print("\n📋 Downloading selected workflow and guide files...")

    if backend_lang:
        workflow_file = f"WORKFLOW_BACKEND_{backend_lang.upper()}.md"
        download_file(f"{GITHUB_RAW_URL}/docs/{workflow_file}", current_dir / "docs" / workflow_file)
        guide_file = f"{backend_lang.upper()}_GUIDE.md"
        download_file(f"{GITHUB_RAW_URL}/.claude/{guide_file}", current_dir / ".claude" / guide_file)

    if frontend_lang:
        workflow_file = f"WORKFLOW_FRONTEND_{frontend_lang.upper()}.md"
        download_file(f"{GITHUB_RAW_URL}/docs/{workflow_file}", current_dir / "docs" / workflow_file)
        guide_file = f"{frontend_lang.upper()}_GUIDE.md"
        download_file(f"{GITHUB_RAW_URL}/.claude/{guide_file}", current_dir / ".claude" / guide_file)

    if infra_tool:
        workflow_file = f"WORKFLOW_INFRASTRUCTURE_{infra_tool.upper()}.md"
        download_file(f"{GITHUB_RAW_URL}/docs/{workflow_file}", current_dir / "docs" / workflow_file)
        guide_file = f"{infra_tool.upper()}_GUIDE.md"
        download_file(f"{GITHUB_RAW_URL}/.claude/{guide_file}", current_dir / ".claude" / guide_file)

    # Download and merge agent configs
    print("\n🤖 Downloading and merging agent configurations...")

    # Download main config.json as the base to preserve workflow/gates/etc. sections
    base_config_url = f"{GITHUB_RAW_URL}/.agents/config.json"
    try:
        with urllib.request.urlopen(base_config_url) as response:
            merged_config = json.loads(response.read())
            # Clear agents — they will be repopulated from component configs below
            merged_config['agents'] = {}
            print(f"  ✅ Downloaded base workflow config")
    except Exception as e:
        print(f"  ⚠️  Could not download base workflow config ({e}), using minimal defaults")
        merged_config = {"agents": {}, "settings": {}}

    if backend_lang:
        config_url = f"{GITHUB_RAW_URL}/.agents/config_backend_{backend_lang}.json"
        try:
            with urllib.request.urlopen(config_url) as response:
                raw_content = response.read()
                backend_config = json.loads(raw_content)
                merged_config['agents'].update(backend_config.get('agents', {}))
                merged_config.setdefault('settings', {}).update(backend_config.get('settings', {}))
                (current_dir / ".agents" / f"config_backend_{backend_lang}.json").write_bytes(raw_content)
                print(f"  ✅ Downloaded backend config ({backend_lang})")
        except Exception as e:
            print(f"  ❌ Failed to download backend config: {e}")

    if frontend_lang:
        config_url = f"{GITHUB_RAW_URL}/.agents/config_frontend_{frontend_lang}.json"
        try:
            with urllib.request.urlopen(config_url) as response:
                raw_content = response.read()
                frontend_config = json.loads(raw_content)
                merged_config['agents'].update(frontend_config.get('agents', {}))
                merged_config.setdefault('settings', {}).update(frontend_config.get('settings', {}))
                (current_dir / ".agents" / f"config_frontend_{frontend_lang}.json").write_bytes(raw_content)
                print(f"  ✅ Downloaded frontend config ({frontend_lang})")
        except Exception as e:
            print(f"  ❌ Failed to download frontend config: {e}")

    if infra_tool:
        config_url = f"{GITHUB_RAW_URL}/.agents/config_infrastructure_{infra_tool.lower()}.json"
        try:
            with urllib.request.urlopen(config_url) as response:
                raw_content = response.read()
                infra_config = json.loads(raw_content)
                merged_config['agents'].update(infra_config.get('agents', {}))
                merged_config.setdefault('settings', {}).update(infra_config.get('settings', {}))
                (current_dir / ".agents" / f"config_infrastructure_{infra_tool.lower()}.json").write_bytes(raw_content)
                print(f"  ✅ Downloaded infrastructure config ({infra_tool})")
        except Exception as e:
            print(f"  ❌ Failed to download infrastructure config: {e}")

    # Replace project name placeholder in agent system prompts
    config_str = json.dumps(merged_config)
    config_str = config_str.replace("Citadel.AI", project_name)
    config_str = config_str.replace("{{PROJECT_NAME}}", project_name)
    merged_config = json.loads(config_str)

    # Write merged config
    config_path = current_dir / ".agents" / "config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(merged_config, f, indent=2)
    print(f"  ✅ Created merged .agents/config.json")

    # Download common documentation files
    print("\n📚 Downloading common documentation...")
    common_docs = [
        "ARCHITECTURE.md",
        "DEVELOPMENT.md",
        "DEPLOYMENT.md",
        "ENVIRONMENT.md",
        "TROUBLESHOOTING.md",
        "IMPLEMENTATION_STATUS.md",
    ]
    if uses_docker:
        common_docs.append("DOCKER_GUIDE.md")
    for doc in common_docs:
        download_file(f"{GITHUB_RAW_URL}/.claude/{doc}", current_dir / ".claude" / doc)

    # Download testing guide and general workflow reference
    download_file(f"{GITHUB_RAW_URL}/docs/TESTING_GUIDE.md", current_dir / "docs" / "TESTING_GUIDE.md")
    download_file(f"{GITHUB_RAW_URL}/docs/WORKFLOW_GUIDE.md", current_dir / "docs" / "WORKFLOW_GUIDE.md")

    print("\n" + "=" * 70)
    print("✅ Installation Complete!")
    print("=" * 70)
    print(f"\n📁 Template installed in: {current_dir}")
    print(f"\n📋 Files created:")
    print(f"   CLAUDE.md")
    print(f"   docs/          ← workflow files")
    print(f"   scripts/       ← worktree management scripts")
    print(f"   .claude/           ← guides & documentation  ⚠️  HIDDEN DIRECTORY")
    print(f"   .claude/agents/    ← agent definitions       ⚠️  HIDDEN DIRECTORY")
    print(f"   .agents/           ← agent configs           ⚠️  HIDDEN DIRECTORY")
    print(f"\n⚠️  Note: .claude/ and .agents/ start with a dot — they are hidden")
    print(f"   on Mac/Linux. Use 'ls -la' to see them, not plain 'ls'.")
    print(f"\n📋 Components installed:")
    if backend_lang:
        print(f"   - Backend: {backend_lang} → docs/WORKFLOW_BACKEND_{backend_lang.upper()}.md")
        print(f"                               .claude/{backend_lang.upper()}_GUIDE.md")
        print(f"                               .agents/config_backend_{backend_lang}.json")
    if frontend_lang:
        print(f"   - Frontend: {frontend_lang} → docs/WORKFLOW_FRONTEND_{frontend_lang.upper()}.md")
        print(f"                                 .claude/{frontend_lang.upper()}_GUIDE.md")
        print(f"                                 .agents/config_frontend_{frontend_lang}.json")
    if infra_tool:
        print(f"   - Infrastructure: {infra_tool} → docs/WORKFLOW_INFRASTRUCTURE_{infra_tool.upper()}.md")
        print(f"                                     .claude/{infra_tool.upper()}_GUIDE.md")
        print(f"                                     .agents/config_infrastructure_{infra_tool.lower()}.json")

    print("\n📋 Next Steps:")
    print("1. Review and customize .agents/config.json")
    print("2. Update documentation in .claude/ folder")
    print("3. Review your workflow file(s) in docs/")
    print("4. Add your project-specific content")
    print("5. Commit: git add CLAUDE.md .claude/ .agents/ docs/ scripts/")
    print("6. Start using Claude Code with your configured agents!")
    print("\n💡 Tip: Run 'claude' in your terminal to start using Claude Code")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Installation failed: {e}")
        raise
