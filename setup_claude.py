#!/usr/bin/env python3
"""
Claude Code Template Setup Script

Interactive script to customize the Claude Code template for your project.
Replaces placeholders with your project-specific values.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict

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

def detect_language(backend_language: str) -> str:
    """Detect primary language from backend_language string."""
    language_lower = backend_language.lower()
    if "python" in language_lower:
        return "python"
    elif "c#" in language_lower or ".net" in language_lower:
        return "dotnet"
    elif "node" in language_lower or "javascript" in language_lower or "typescript" in language_lower:
        return "nodejs"
    elif "go" in language_lower or "golang" in language_lower:
        return "go"
    return "python"  # default fallback

def detect_frontend_framework(frontend_framework: str) -> str:
    """Detect frontend framework identifier."""
    framework_lower = frontend_framework.lower()
    if "react" in framework_lower or "next" in framework_lower:
        return "react"
    elif "vue" in framework_lower or "nuxt" in framework_lower:
        return "vue"
    elif "angular" in framework_lower:
        return "angular"
    return "react"  # default

def merge_agent_configs(backend_language: str, frontend_framework: str, has_frontend: bool, template_dir: Path) -> bool:
    """Merge backend and frontend agent configs into config.json."""
    detected_backend = detect_language(backend_language)

    backend_config_file = template_dir / ".agents" / f"config_backend_{detected_backend}.json"

    if not backend_config_file.exists():
        print(f"  ⚠️  Warning: {backend_config_file.name} not found")
        return False

    try:
        # Load backend config
        with open(backend_config_file, 'r', encoding='utf-8') as f:
            merged_config = json.load(f)

        print(f"  ✅ Loaded backend config ({detected_backend})")

        # If has frontend, merge frontend config
        if has_frontend:
            frontend_lang = detect_frontend_framework(frontend_framework)
            frontend_config_file = template_dir / ".agents" / f"config_frontend_{frontend_lang}.json"

            if frontend_config_file.exists():
                with open(frontend_config_file, 'r', encoding='utf-8') as f:
                    frontend_config = json.load(f)

                # Merge agents
                merged_config.setdefault('agents', {}).update(frontend_config.get('agents', {}))
                # Merge settings
                merged_config.setdefault('settings', {}).update(frontend_config.get('settings', {}))
                print(f"  ✅ Merged frontend config ({frontend_lang})")
            else:
                print(f"  ⚠️  Frontend config not found: {frontend_config_file.name}")

        # Write merged config
        target = template_dir / ".agents" / "config.json"
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(merged_config, f, indent=2)

        print(f"  ✅ Created config.json")
        return True

    except Exception as e:
        print(f"  ❌ Error merging configs: {e}")
        return False

def replace_in_file(file_path: Path, replacements: Dict[str, str]):
    """Replace placeholders in a file."""
    if not file_path.exists():
        print(f"  ⚠️  Skipping {file_path} (not found)")
        return

    try:
        content = file_path.read_text(encoding='utf-8')

        # Replace all placeholders
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        file_path.write_text(content, encoding='utf-8')
        print(f"  ✅ Updated {file_path.name}")
    except Exception as e:
        print(f"  ❌ Error updating {file_path}: {e}")

def update_agent_config(config_path: Path, replacements: Dict[str, str]):
    """Update agent configuration with project-specific values."""
    if not config_path.exists():
        print(f"  ⚠️  Config file not found: {config_path}")
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Update project name in system prompts
        project_name = replacements.get('{{PROJECT_NAME}}', 'YOUR_PROJECT')

        for agent_key, agent_data in config.get('agents', {}).items():
            if 'system_prompt' in agent_data:
                agent_data['system_prompt'] = agent_data['system_prompt'].replace(
                    'Citadel.AI', project_name
                )

        # Update file watch patterns if needed
        backend_pattern = replacements.get('{{BACKEND_PATTERN}}', 'app')
        frontend_pattern = replacements.get('{{FRONTEND_PATTERN}}', 'dashboard')

        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        print(f"  ✅ Updated {config_path.name}")
    except Exception as e:
        print(f"  ❌ Error updating config: {e}")

def main():
    print("=" * 70)
    print("Claude Code Template Setup")
    print("=" * 70)
    print("\nThis script will customize the template for your project.\n")

    # Get project information
    print("📋 Project Information")
    print("-" * 70)
    project_name = prompt("Project name", "MyProject")
    project_description = prompt("Project description", "A great project")
    repo_url = prompt("Repository URL (optional)", "https://github.com/user/repo")

    print("\n🛠️  Technology Stack")
    print("-" * 70)
    print("Choose backend type:")
    print("1. Python (FastAPI, Django, Flask)")
    print("2. Node.js (Express, NestJS, Fastify)")
    print("3. .NET (ASP.NET Core)")
    print("4. Other")
    backend_choice = prompt("Backend choice", "1")

    # Set defaults based on choice
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
    else:
        backend_framework = prompt("Backend framework", "FastAPI")
        backend_language = prompt("Backend language", "Python 3.11")
        backend_folder = prompt("Backend code folder", "app")

    has_frontend = yes_no("Does your project have a frontend?", True)

    if has_frontend:
        frontend_framework = prompt("Frontend framework", "Next.js 14")
        frontend_language = prompt("Frontend language", "TypeScript")
        frontend_folder = prompt("Frontend code folder", "dashboard")
    else:
        frontend_framework = "N/A"
        frontend_language = "N/A"
        frontend_folder = "frontend"

    print("\n🐳 Docker Configuration")
    print("-" * 70)
    uses_docker = yes_no("Does your project use Docker?", True)

    if uses_docker:
        docker_compose_file = prompt("Docker compose file", "docker-compose.yml")
    else:
        docker_compose_file = "docker-compose.yml"

    print("\n🌿 Git Configuration")
    print("-" * 70)
    main_branch = prompt("Main branch name", "main")

    print("\n🤖 Workflow Configuration")
    print("-" * 70)
    print("Choose default workflow variant:")
    print("1. Standard (11 steps) - Most common")
    print("2. Full (13 steps) - With architecture review")
    print("3. Hotfix (9 steps) - Fast emergency fixes")
    workflow_choice = prompt("Choice", "1")

    workflow_map = {
        "1": "standard",
        "2": "full",
        "3": "hotfix"
    }
    default_workflow = workflow_map.get(workflow_choice, "standard")

    # Create replacements dictionary
    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_DESCRIPTION}}": project_description,
        "{{REPO_URL}}": repo_url,
        "{{BACKEND_FRAMEWORK}}": backend_framework,
        "{{BACKEND_LANGUAGE}}": backend_language,
        "{{BACKEND_FOLDER}}": backend_folder,
        "{{FRONTEND_FRAMEWORK}}": frontend_framework,
        "{{FRONTEND_LANGUAGE}}": frontend_language,
        "{{FRONTEND_FOLDER}}": frontend_folder,
        "{{DOCKER_COMPOSE_FILE}}": docker_compose_file,
        "{{MAIN_BRANCH}}": main_branch,
        "{{DEFAULT_WORKFLOW}}": default_workflow,
        "{{USES_DOCKER}}": "true" if uses_docker else "false",
        "{{HAS_FRONTEND}}": "true" if has_frontend else "false",
    }

    # Get current directory
    template_dir = Path.cwd()

    print(f"\n🔧 Customizing template in: {template_dir}")
    print("-" * 70)

    # Update CLAUDE.md
    print("\n📝 Updating CLAUDE.md...")
    replace_in_file(template_dir / "CLAUDE.md", replacements)

    # Update .claude/ documentation
    print("\n📚 Updating documentation...")
    claude_docs = template_dir / ".claude"
    if claude_docs.exists():
        for doc_file in claude_docs.glob("*.md"):
            replace_in_file(doc_file, replacements)

    # Update docs/ folder
    docs_folder = template_dir / "docs"
    if docs_folder.exists():
        for doc_file in docs_folder.glob("*.md"):
            replace_in_file(doc_file, replacements)

    # Merge agent configurations
    print("\n🤖 Merging agent configurations...")
    detected_language = detect_language(backend_language)
    print(f"  🔍 Detected backend language: {detected_language}")

    if has_frontend:
        detected_frontend = detect_frontend_framework(frontend_framework)
        print(f"  🔍 Detected frontend framework: {detected_frontend}")

    if merge_agent_configs(backend_language, frontend_framework, has_frontend, template_dir):
        # Update the merged config with project-specific values
        update_agent_config(template_dir / ".agents" / "config.json", replacements)
    else:
        print("  ⚠️  Using default config.json")
        update_agent_config(template_dir / ".agents" / "config.json", replacements)

    # Create scripts folder if it doesn't exist
    scripts_folder = template_dir / "scripts"
    scripts_folder.mkdir(exist_ok=True)
    print(f"  ✅ Created {scripts_folder}")

    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("1. Review and customize .agents/config.json")
    print("2. Update documentation in .claude/ folder")
    print("3. Add your project-specific content")
    print("4. Commit: git add CLAUDE.md .claude/ .agents/ docs/")
    print("5. Start using Claude Code with your configured agents!")
    print("\n💡 Tip: Run 'claude' in your terminal to start using Claude Code")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        raise
