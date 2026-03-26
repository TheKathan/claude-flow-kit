#!/usr/bin/env python3
"""
Claude Code Template Installer

Fresh install:
  curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py -o install.py
  python3 install.py

Update to latest (no prompts — reads saved config):
  curl -sSL https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py -o install.py
  python3 install.py --update --yes

Windows (PowerShell):
  Invoke-WebRequest -Uri "https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main/install.py" -OutFile "install.py"
  python install.py

Note: Do NOT pipe directly via `curl ... | python3`.  The installer is
interactive and requires terminal input, which breaks when stdin is a pipe.
"""

import os
import sys
import json
import argparse
import shutil
import datetime
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

# Ensure UTF-8 output on Windows (emoji in print statements)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # Python < 3.7 — best-effort

INSTALLER_VERSION = "2.3.0"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/TheKathan/claude-flow-kit/main"


def _ssl_context() -> ssl.SSLContext:
    """Return an SSL context that validates certificates.

    On macOS, Python's bundled OpenSSL does not use the system keychain, so
    urlopen can fail with CERTIFICATE_VERIFY_FAILED.  We try certifi first
    (widely installed), then fall back to the stdlib default context.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()
MANIFEST_PATH = ".claude/install-manifest.json"

CATEGORY_A_ALWAYS_UPDATE = "always_update"   # template files, users never edit
CATEGORY_B_ASK_USER      = "ask_user"        # users may have customized
CATEGORY_C_NEVER_TOUCH   = "never_touch"     # custom config — special handling only

FILE_CATEGORIES = {
    ".claude/commands/workflow.md": CATEGORY_A_ALWAYS_UPDATE,
    "CLAUDE.md":                    CATEGORY_B_ASK_USER,
    ".claude/ARCHITECTURE.md":      CATEGORY_B_ASK_USER,
    ".claude/DEPLOYMENT.md":        CATEGORY_B_ASK_USER,
    ".claude/DEVELOPMENT.md":       CATEGORY_B_ASK_USER,
    ".claude/ENVIRONMENT.md":       CATEGORY_B_ASK_USER,
    ".claude/TROUBLESHOOTING.md":   CATEGORY_B_ASK_USER,
    ".claude/IMPLEMENTATION_STATUS.md": CATEGORY_B_ASK_USER,
    ".claude/DOCKER_GUIDE.md":      CATEGORY_B_ASK_USER,
    ".claude/API_REFERENCE.md":     CATEGORY_B_ASK_USER,
    "docs/TESTING_GUIDE.md":        CATEGORY_B_ASK_USER,
    "docs/WORKFLOW_GUIDE.md":       CATEGORY_B_ASK_USER,
    ".agents/config.json":          CATEGORY_C_NEVER_TOUCH,
    ".claude/settings.local.json":  CATEGORY_C_NEVER_TOUCH,
}

# All agent keys shipped by the template (role-based AND name-based)
KNOWN_TEMPLATE_AGENT_KEYS: frozenset = frozenset({
    "architect", "worktree-mgr", "docker-debug", "e2e-tester",
    "status-reviewer", "conflict-resolver", "skill-creator",
    "backend-developer", "backend-reviewer", "frontend-developer", "frontend-reviewer",
    "python-developer", "python-test-specialist", "python-tester",
    "nodejs-developer", "nodejs-test-specialist",
    "dotnet-developer", "dotnet-test-specialist",
    "go-developer", "go-test-specialist",
    "rust-developer", "rust-test-specialist",
    "ruby-developer", "ruby-test-specialist", "ruby-tester",
    "backend-code-reviewer", "integration-tester",
    "react-frontend-dev", "react-test-specialist", "react-tester",
    "vue-developer", "vue-test-specialist",
    "angular-developer", "angular-test-specialist",
    "svelte-developer", "svelte-test-specialist",
    "frontend-code-reviewer",
    "terraform-developer", "terraform-test-specialist", "infrastructure-code-reviewer",
})


def save_manifest(cwd: Path, config: dict):
    """Save installation config to manifest for future updates."""
    path = cwd / MANIFEST_PATH
    now = datetime.datetime.now().isoformat()
    # Preserve original install timestamp on updates
    existing = load_manifest(cwd)
    installed_at = existing.get("installed_at", now) if existing else now
    manifest = {
        "installer_version": INSTALLER_VERSION,
        "installed_at": installed_at,
        "updated_at": now,
        **config,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def load_manifest(cwd: Path) -> Optional[dict]:
    """Load installation manifest. Returns None if not found or invalid."""
    path = cwd / MANIFEST_PATH
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _rel_str(path: Path, cwd: Path) -> str:
    """Return path relative to cwd as forward-slash string."""
    try:
        return path.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()


def get_file_category(rel_path: str) -> str:
    if rel_path in FILE_CATEGORIES:
        return FILE_CATEGORIES[rel_path]
    if rel_path.startswith((".claude/agents/", "scripts/")):
        return CATEGORY_A_ALWAYS_UPDATE
    if rel_path.startswith("docs/WORKFLOW_") and rel_path.endswith(".md"):
        return CATEGORY_B_ASK_USER
    if rel_path.startswith(".claude/") and rel_path.endswith("_GUIDE.md"):
        return CATEGORY_B_ASK_USER
    return CATEGORY_B_ASK_USER  # conservative default


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
    """Download file from URL to destination, with retry on 429."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(url, context=_ssl_context()) as response:
                content = response.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            print(f"  ✅ Downloaded {dest.name}")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_attempts - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"  ⏳ Rate limited, retrying in {wait}s… ({dest.name})")
                time.sleep(wait)
            else:
                print(f"  ❌ Failed to download {dest.name}: {e}")
                return False
        except Exception as e:
            print(f"  ❌ Failed to download {dest.name}: {e}")
            return False
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
    elif "rust" in language_lower:
        return "rust"
    elif "ruby" in language_lower or "rails" in language_lower:
        return "ruby"
    return None

def detect_frontend_framework(frontend_framework: Optional[str]) -> Optional[str]:
    """Detect frontend framework identifier."""
    if not frontend_framework:
        return None

    framework_lower = frontend_framework.lower()
    if "tauri" in framework_lower:
        return "tauri"
    elif "react" in framework_lower or "next" in framework_lower:
        return "react"
    elif "vue" in framework_lower or "nuxt" in framework_lower:
        return "vue"
    elif "angular" in framework_lower:
        return "angular"
    elif "svelte" in framework_lower:
        return "svelte"
    return None

def detect_infrastructure_tool(infrastructure_tool: Optional[str]) -> Optional[str]:
    """Detect infrastructure tool identifier."""
    if not infrastructure_tool:
        return None

    tool_lower = infrastructure_tool.lower()
    if "terraform" in tool_lower:
        return "terraform"
    return None

def _evaluate_condition(condition: str, variables: Dict[str, str]) -> bool:
    """Evaluate a {{#if COND}} expression against the variable map."""
    condition = condition.strip()
    # "A or B" — any sub-condition being true is sufficient
    if " or " in condition:
        return any(_evaluate_condition(p, variables) for p in condition.split(" or "))
    # 'VAR includes "STRING"' — substring check
    import re as _re
    m = _re.match(r'(\w+)\s+includes\s+"([^"]*)"', condition)
    if m:
        value = variables.get("{{" + m.group(1) + "}}", "")
        return m.group(2).lower() in value.lower()
    # Simple variable — truthy when non-empty and not "false"
    value = variables.get("{{" + condition + "}}", "")
    return value.lower() not in ("", "false")


def _process_template(file_path: Path, replacements: Dict[str, str]):
    """Substitute {{VAR}} placeholders and evaluate {{#if}}...{{/if}} blocks."""
    if not file_path.exists():
        return
    try:
        import re
        content = file_path.read_text(encoding="utf-8")

        # Pass 1: simple variable substitution
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Pass 2: process conditionals iteratively (inner blocks resolve first)
        for _ in range(10):
            prev = content

            # Inline if-else: {{#if COND}}true content{{else}}false content{{/if}}
            # Content must not contain another {{#if (handled in later iterations)
            content = re.sub(
                r'\{\{#if ([^}]+)\}\}((?:(?!\{\{#if)[^\n])*)\{\{else\}\}((?:(?!\{\{#if)[^\n])*)\{\{/if\}\}',
                lambda m: m.group(2) if _evaluate_condition(m.group(1), replacements) else m.group(3),
                content,
            )
            # Inline if: {{#if COND}}content{{/if}} (no else, no newlines, no nested)
            content = re.sub(
                r'\{\{#if ([^}]+)\}\}((?:(?!\{\{#if)[^\n])*)\{\{/if\}\}',
                lambda m: m.group(2) if _evaluate_condition(m.group(1), replacements) else "",
                content,
            )
            # Multi-line if-else (no nested {{#if}} inside either branch)
            content = re.sub(
                r'\{\{#if ([^}]+)\}\}((?:(?!\{\{#if).)*?)\{\{else\}\}((?:(?!\{\{#if).)*?)\{\{/if\}\}',
                lambda m: m.group(2) if _evaluate_condition(m.group(1), replacements) else m.group(3),
                content,
                flags=re.DOTALL,
            )
            # Multi-line if (no nested {{#if}} inside)
            content = re.sub(
                r'\{\{#if ([^}]+)\}\}((?:(?!\{\{#if).)*?)\{\{/if\}\}',
                lambda m: m.group(2) if _evaluate_condition(m.group(1), replacements) else "",
                content,
                flags=re.DOTALL,
            )

            if content == prev:
                break

        # Clean up runs of 3+ blank lines left by removed blocks
        content = re.sub(r"\n{3,}", "\n\n", content)

        file_path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"  ✅ Processed template {file_path.name}")
    except Exception as e:
        print(f"  ⚠️  Could not process template {file_path.name}: {e}")


# Python < 3.9 compatibility shim for BooleanOptionalAction
try:
    argparse.BooleanOptionalAction
except AttributeError:
    class _BoolOptAction(argparse.Action):
        def __init__(self, option_strings, dest, default=None, **kw):
            pos = [o for o in option_strings if not o.startswith("--no-")]
            neg = ["--no-" + o.lstrip("-") for o in pos]
            super().__init__(pos + neg, dest, nargs=0, default=default, **kw)
        def __call__(self, p, ns, v, opt=None):
            setattr(ns, self.dest, not opt.startswith("--no-"))
    argparse.BooleanOptionalAction = _BoolOptAction


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Claude Code Template Installer")
    p.add_argument("--update", action="store_true", default=False,
        help="Update existing installation using saved config (skips prompts if manifest exists)")
    p.add_argument("--backup", default=True, action=argparse.BooleanOptionalAction,
        help="Create timestamped backup before overwriting (default: on)")
    p.add_argument("--yes", action="store_true", default=False,
        help="Non-interactive: skip all existing customized files, update template files")
    return p.parse_args()


class BackupManager:
    def __init__(self, cwd: Path, enabled: bool):
        self.enabled = enabled
        self.cwd = cwd
        self._root: Optional[Path] = None

    def _ensure_dir(self) -> Path:
        if self._root is None:
            ts = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            self._root = self.cwd / ".claude" / "backup" / ts
            self._root.mkdir(parents=True, exist_ok=True)
            print(f"  Backup dir: {self._root.relative_to(self.cwd)}")
        return self._root

    def backup(self, file_path: Path) -> bool:
        if not self.enabled or not file_path.exists():
            return False
        root = self._ensure_dir()
        try:
            rel = file_path.relative_to(self.cwd)
        except ValueError:
            return False
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(file_path), str(dest))
        return True


def detect_existing_installation(cwd: Path) -> bool:
    return (cwd / ".agents" / "config.json").exists() or (cwd / "CLAUDE.md").exists()


def download_file_with_policy(
    url: str, dest: Path, cwd: Path,
    install_mode: str, backup_mgr: "BackupManager",
    auto_yes: bool, user_choices: dict,
) -> bool:
    if install_mode == "fresh":
        return download_file(url, dest)

    rel = _rel_str(dest, cwd)
    cat = get_file_category(rel)

    if cat == CATEGORY_A_ALWAYS_UPDATE:
        return download_file(url, dest)

    if cat == CATEGORY_C_NEVER_TOUCH:
        # config.json handled separately; settings.local.json always skipped
        return False

    # Category B: only prompt if the file already exists
    if not dest.exists():
        return download_file(url, dest)

    if auto_yes:
        user_choices[rel] = "s"
        return False

    if rel in user_choices:
        choice = user_choices[rel]
    elif user_choices.get("_overwrite_all"):
        choice = "o"
    else:
        print(f"\n  Exists: {rel}")
        print("  [O]verwrite  [S]kip  [A]ll (overwrite all remaining) — default: Skip")
        choice = ""
        while choice not in ("o", "s", "a"):
            choice = input("  [S/o/a]: ").strip().lower() or "s"
        if choice == "a":
            user_choices["_overwrite_all"] = True
            choice = "o"
        user_choices[rel] = choice

    if choice == "s":
        return False
    backup_mgr.backup(dest)
    return download_file(url, dest)


def merge_agent_config(existing: dict, fresh: dict) -> dict:
    merged = {}
    fresh_agents = fresh.get("agents", {})
    existing_agents = existing.get("agents", {})
    user_custom = {k: v for k, v in existing_agents.items()
                   if k not in KNOWN_TEMPLATE_AGENT_KEYS}
    merged["agents"] = {**fresh_agents, **user_custom}
    for key in ("workflow", "workflow_variants", "smart_fix_loop", "gates", "paths"):
        if key in fresh:
            merged[key] = fresh[key]
    for key, val in existing.items():
        if key not in merged and key != "agents":
            merged[key] = val
    existing_settings = existing.get("settings", {})
    fresh_settings    = fresh.get("settings", {})
    if existing_settings or fresh_settings:
        merged["settings"] = {**fresh_settings, **existing_settings}
    return merged


def preflight_checks():
    """Verify the environment is ready before prompting the user."""
    errors = []

    # Python version
    if sys.version_info < (3, 7):
        errors.append(f"Python 3.7+ required (you have {sys.version.split()[0]})")

    # git installed
    import subprocess
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        errors.append("git not found — install from https://git-scm.com/")

    # Write permissions in current directory
    try:
        test_file = Path("._install_check_tmp")
        test_file.write_text("x")
        test_file.unlink()
    except OSError:
        errors.append(f"No write permission in {Path.cwd()}")

    if errors:
        print("❌ Pre-flight checks failed:")
        for err in errors:
            print(f"   • {err}")
        sys.exit(1)


def main():
    print("=" * 70)
    print("Claude Code Template Installer")
    print("=" * 70)
    print("\nThis installer will download and set up the Claude Code template.\n")

    args = parse_args()
    preflight_checks()

    current_dir = Path.cwd()
    existing = detect_existing_installation(current_dir)

    if args.update:
        install_mode = "update"
    elif not existing:
        install_mode = "fresh"
    else:
        print("\nExisting Claude setup detected.")
        if args.yes:
            install_mode = "update"
        else:
            print("  [F]resh — overwrite everything  [U]pdate — safe update (recommended)")
            choice = ""
            while choice not in ("f", "u"):
                choice = input("  Mode [U/f]: ").strip().lower() or "u"
            install_mode = "fresh" if choice == "f" else "update"

    backup_mgr = BackupManager(current_dir, enabled=(args.backup and install_mode == "update"))
    user_choices: dict = {}

    def _dl(url: str, dest: Path) -> bool:
        return download_file_with_policy(
            url, dest, current_dir, install_mode, backup_mgr, args.yes, user_choices)

    # --- Load manifest for update mode ---
    manifest = load_manifest(current_dir) if install_mode == "update" else None

    if manifest and install_mode == "update":
        # Fast-path: reuse saved config, skip all prompts
        prev_version = manifest.get("installer_version", "unknown")
        print(f"\n📦 Manifest found (installed v{prev_version}, updating to v{INSTALLER_VERSION})")
        project_name = manifest["project_name"]
        project_description = manifest["project_description"]
        repo_url = manifest["repo_url"]
        backend_language = manifest.get("backend_language")
        backend_framework = manifest.get("backend_framework")
        backend_folder = manifest.get("backend_folder")
        frontend_framework = manifest.get("frontend_framework")
        frontend_language = manifest.get("frontend_language")
        frontend_folder = manifest.get("frontend_folder")
        infrastructure_tool = manifest.get("infrastructure_tool")
        uses_docker = manifest.get("uses_docker", False)
        main_branch = manifest.get("main_branch", "main")
        has_backend = backend_language is not None
        has_frontend = frontend_framework is not None
        has_infrastructure = infrastructure_tool is not None

        print(f"  Project: {project_name}")
        if has_backend:
            print(f"  Backend: {backend_framework} ({backend_language})")
        if has_frontend:
            print(f"  Frontend: {frontend_framework} ({frontend_language})")
        if has_infrastructure:
            print(f"  Infrastructure: {infrastructure_tool}")
        if not args.yes:
            if not yes_no("\n  Proceed with these settings?", True):
                print("  Re-running with fresh prompts...\n")
                manifest = None  # fall through to interactive prompts

    if manifest is None or install_mode == "fresh":
        # Interactive prompts (fresh install or user opted out of manifest)
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
            print("5. Rust (Axum, Actix-web)")
            print("6. Ruby (Rails, Sinatra, Hanami)")
            print("7. Other (manual setup)")
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
            elif backend_choice == "5":
                backend_framework = prompt("Backend framework", "Axum")
                backend_language = prompt("Backend language", "Rust")
                backend_folder = prompt("Backend code folder", "src")
            elif backend_choice == "6":
                backend_framework = prompt("Backend framework", "Rails 7")
                backend_language = prompt("Backend language", "Ruby 3.3")
                backend_folder = prompt("Backend code folder", "app")
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
            print("4. Svelte / SvelteKit")
            print("5. Tauri (desktop app — Rust backend + web frontend)")
            print("6. Other (manual setup)")
            frontend_choice = prompt("Frontend choice", "1")

            if frontend_choice == "1":
                frontend_framework = prompt("Frontend framework", "Next.js 14")
                frontend_language = prompt("Frontend language", "TypeScript")
                frontend_folder = prompt("Frontend code folder", "src")
            elif frontend_choice == "2":
                frontend_framework = prompt("Frontend framework", "Vue 3")
                frontend_language = prompt("Frontend language", "TypeScript")
                frontend_folder = prompt("Frontend code folder", "src")
            elif frontend_choice == "3":
                frontend_framework = prompt("Frontend framework", "Angular 17")
                frontend_language = prompt("Frontend language", "TypeScript")
                frontend_folder = prompt("Frontend code folder", "src")
            elif frontend_choice == "4":
                frontend_framework = prompt("Frontend framework", "SvelteKit")
                frontend_language = prompt("Frontend language", "TypeScript")
                frontend_folder = prompt("Frontend code folder", "src")
            elif frontend_choice == "5":
                frontend_framework = prompt("Frontend framework", "Tauri")
                frontend_language = prompt("Frontend language", "TypeScript + Rust")
                frontend_folder = prompt("Frontend code folder", "src")
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

        # Validate at least one component selected — re-prompt rather than exit
        while not has_backend and not has_frontend and not has_infrastructure:
            print("\n⚠️  No components selected. You must choose at least one to continue.")
            has_backend = yes_no("Does your project have a backend?", True)
            has_frontend = yes_no("Does your project have a frontend?", False)
            has_infrastructure = yes_no("Does your project use Infrastructure-as-Code?", False)

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

    # Download CLAUDE.md and process template variables + conditionals
    if _dl(f"{GITHUB_RAW_URL}/CLAUDE.md", current_dir / "CLAUDE.md"):
        _process_template(current_dir / "CLAUDE.md", {
            "{{PROJECT_NAME}}": project_name,
            "{{PROJECT_DESCRIPTION}}": project_description,
            "{{REPO_URL}}": repo_url,
            "{{BACKEND_FRAMEWORK}}": backend_framework or "",
            "{{BACKEND_LANGUAGE}}": backend_language or "",
            "{{FRONTEND_FRAMEWORK}}": frontend_framework or "",
            "{{FRONTEND_LANGUAGE}}": frontend_language or "",
            "{{MAIN_BRANCH}}": main_branch,
            "{{CURRENT_DATE}}": datetime.date.today().isoformat(),
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
        _dl(f"{GITHUB_RAW_URL}/scripts/{script}", current_dir / "scripts" / script)

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
        "skill-creator.md",
    ]
    for agent in common_agents:
        _dl(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # API reference — conditional on backend presence
    if has_backend:
        api_ref = agents_dir.parent / "API_REFERENCE.md"
        if _dl(f"{GITHUB_RAW_URL}/.claude/API_REFERENCE.md", api_ref):
            _process_template(api_ref, {
                "{{PROJECT_NAME}}": project_name,
                "{{API_BASE_URL}}": "http://localhost:8000",
            })

    # Backend agents — conditional on selected language
    backend_agent_map = {
        "python":  ["python-developer.md", "python-test-specialist.md", "backend-code-reviewer.md"],
        "nodejs":  ["nodejs-developer.md", "nodejs-test-specialist.md", "backend-code-reviewer.md"],
        "dotnet":  ["dotnet-developer.md", "dotnet-test-specialist.md", "backend-code-reviewer.md"],
        "go":      ["go-developer.md", "go-test-specialist.md", "backend-code-reviewer.md"],
        "rust":    ["rust-developer.md", "rust-test-specialist.md", "backend-code-reviewer.md"],
        "ruby":    ["ruby-developer.md", "ruby-test-specialist.md", "backend-code-reviewer.md"],
    }
    if backend_lang and backend_lang in backend_agent_map:
        for agent in backend_agent_map[backend_lang]:
            _dl(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # Frontend agents — conditional on selected framework
    # Tauri uses rust-developer for src-tauri/ and frontend-code-reviewer for the web layer
    frontend_agent_map = {
        "react":   ["react-frontend-dev.md", "react-test-specialist.md", "frontend-code-reviewer.md"],
        "vue":     ["vue-developer.md", "vue-test-specialist.md", "frontend-code-reviewer.md"],
        "angular": ["angular-developer.md", "angular-test-specialist.md", "frontend-code-reviewer.md"],
        "svelte":  ["svelte-developer.md", "svelte-test-specialist.md", "frontend-code-reviewer.md"],
        "tauri":   ["rust-developer.md", "rust-test-specialist.md", "frontend-code-reviewer.md"],
    }
    if frontend_lang and frontend_lang in frontend_agent_map:
        for agent in frontend_agent_map[frontend_lang]:
            _dl(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # Infrastructure agents — conditional on selected tool
    if infra_tool and infra_tool.lower() == "terraform":
        for agent in ["terraform-developer.md", "terraform-test-specialist.md", "infrastructure-code-reviewer.md"]:
            _dl(f"{GITHUB_RAW_URL}/.claude/agents/{agent}", agents_dir / agent)

    # Download selected workflows and guides
    print("\n📋 Downloading selected workflow and guide files...")

    if backend_lang:
        workflow_file = f"WORKFLOW_BACKEND_{backend_lang.upper()}.md"
        _dl(f"{GITHUB_RAW_URL}/docs/{workflow_file}", current_dir / "docs" / workflow_file)
        guide_file = f"{backend_lang.upper()}_GUIDE.md"
        _dl(f"{GITHUB_RAW_URL}/.claude/{guide_file}", current_dir / ".claude" / guide_file)

    if frontend_lang:
        workflow_file = f"WORKFLOW_FRONTEND_{frontend_lang.upper()}.md"
        _dl(f"{GITHUB_RAW_URL}/docs/{workflow_file}", current_dir / "docs" / workflow_file)
        guide_file = f"{frontend_lang.upper()}_GUIDE.md"
        _dl(f"{GITHUB_RAW_URL}/.claude/{guide_file}", current_dir / ".claude" / guide_file)
        # Tauri apps have a Rust backend (src-tauri/) — also download the Rust guide
        if frontend_lang == "tauri":
            _dl(f"{GITHUB_RAW_URL}/.claude/RUST_GUIDE.md", current_dir / ".claude" / "RUST_GUIDE.md")

    if infra_tool:
        workflow_file = f"WORKFLOW_INFRASTRUCTURE_{infra_tool.upper()}.md"
        _dl(f"{GITHUB_RAW_URL}/docs/{workflow_file}", current_dir / "docs" / workflow_file)
        guide_file = f"{infra_tool.upper()}_GUIDE.md"
        _dl(f"{GITHUB_RAW_URL}/.claude/{guide_file}", current_dir / ".claude" / guide_file)

    # Download and merge agent configs
    print("\n🤖 Downloading and merging agent configurations...")

    # Read existing config before downloading fresh one (update mode only)
    existing_agent_config = {}
    if install_mode == "update":
        cp = current_dir / ".agents" / "config.json"
        if cp.exists():
            try:
                existing_agent_config = json.loads(cp.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  Warning: could not read existing config.json: {e}")

    # Common orchestration agents that are always needed regardless of stack
    _COMMON_AGENT_KEYS = {
        "architect", "worktree-mgr", "docker-debug",
        "e2e-tester", "status-reviewer", "conflict-resolver",
        "skill-creator",
    }

    # Download main config.json as the base to preserve workflow/gates/etc. sections
    base_config_url = f"{GITHUB_RAW_URL}/.agents/config.json"
    try:
        with urllib.request.urlopen(base_config_url, context=_ssl_context()) as response:
            merged_config = json.loads(response.read())
            # Keep only common orchestration agents; stack-specific ones come from
            # component configs below so we don't include mismatched generics.
            merged_config['agents'] = {
                k: v for k, v in merged_config['agents'].items()
                if k in _COMMON_AGENT_KEYS
            }
            print(f"  ✅ Downloaded base workflow config")
    except Exception as e:
        print(f"  ⚠️  Could not download base workflow config ({e}), using minimal defaults")
        merged_config = {"agents": {}, "settings": {}}

    if backend_lang:
        config_url = f"{GITHUB_RAW_URL}/.agents/config_backend_{backend_lang}.json"
        try:
            with urllib.request.urlopen(config_url, context=_ssl_context()) as response:
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
            with urllib.request.urlopen(config_url, context=_ssl_context()) as response:
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
            with urllib.request.urlopen(config_url, context=_ssl_context()) as response:
                raw_content = response.read()
                infra_config = json.loads(raw_content)
                merged_config['agents'].update(infra_config.get('agents', {}))
                merged_config.setdefault('settings', {}).update(infra_config.get('settings', {}))
                (current_dir / ".agents" / f"config_infrastructure_{infra_tool.lower()}.json").write_bytes(raw_content)
                print(f"  ✅ Downloaded infrastructure config ({infra_tool})")
        except Exception as e:
            print(f"  ❌ Failed to download infrastructure config: {e}")

    # Substitute {{PROJECT_NAME}} and write config
    config_path = current_dir / ".agents" / "config.json"
    if install_mode == "update" and existing_agent_config:
        config_str = json.dumps(merged_config).replace("{{PROJECT_NAME}}", project_name)
        fresh_merged = json.loads(config_str)
        final_config = merge_agent_config(existing_agent_config, fresh_merged)
        user_custom = {k for k in existing_agent_config.get("agents", {})
                       if k not in KNOWN_TEMPLATE_AGENT_KEYS}
        if user_custom and not args.yes:
            print(f"\n  Found {len(user_custom)} custom agent(s): {', '.join(sorted(user_custom))}")
            print("  These will be preserved. Template agents will be updated.")
            if (input("  Proceed? [Y/n]: ").strip().lower() or "y") not in ("y", "yes"):
                final_config = existing_agent_config
        backup_mgr.backup(current_dir / ".agents" / "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(final_config, f, indent=2)
    else:
        # fresh mode or no existing config — current behavior
        config_str = json.dumps(merged_config)
        config_str = config_str.replace("{{PROJECT_NAME}}", project_name)
        merged_config = json.loads(config_str)
        with open(config_path, "w", encoding="utf-8") as f:
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
        _dl(f"{GITHUB_RAW_URL}/.claude/{doc}", current_dir / ".claude" / doc)

    # Download slash commands
    print("\n⌨️  Downloading slash commands...")
    commands_dir = current_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    _dl(f"{GITHUB_RAW_URL}/.claude/commands/workflow.md", commands_dir / "workflow.md")

    # Download testing guide and general workflow reference
    _dl(f"{GITHUB_RAW_URL}/docs/TESTING_GUIDE.md", current_dir / "docs" / "TESTING_GUIDE.md")
    workflow_guide = current_dir / "docs" / "WORKFLOW_GUIDE.md"
    if _dl(f"{GITHUB_RAW_URL}/docs/WORKFLOW_GUIDE.md", workflow_guide):
        _process_template(workflow_guide, {
            "{{PROJECT_NAME}}": project_name,
            "{{CURRENT_DATE}}": datetime.date.today().isoformat(),
        })

    # Update mode summary
    if install_mode == "update":
        skipped = [p for p, c in user_choices.items() if c == "s"]
        overwritten = [p for p, c in user_choices.items() if c == "o"]
        if skipped:
            print(f"\n  Preserved (your edits kept): {len(skipped)} file(s)")
        if overwritten:
            print(f"  Overwritten (backed up): {len(overwritten)} file(s)")
        if backup_mgr._root:
            print(f"  Backups: {backup_mgr._root.relative_to(current_dir)}")
        print("  Tip: add '.claude/backup/' to .gitignore")

    # Save manifest for future updates
    save_manifest(current_dir, {
        "project_name": project_name,
        "project_description": project_description,
        "repo_url": repo_url,
        "backend_language": backend_language,
        "backend_framework": backend_framework,
        "backend_folder": backend_folder,
        "frontend_framework": frontend_framework,
        "frontend_language": frontend_language,
        "frontend_folder": frontend_folder,
        "infrastructure_tool": infrastructure_tool,
        "uses_docker": uses_docker,
        "main_branch": main_branch,
    })

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
    print(f"   .claude/commands/  ← slash commands          ⚠️  HIDDEN DIRECTORY")
    print(f"   .agents/           ← agent configs           ⚠️  HIDDEN DIRECTORY")
    print(f"\n⚠️  Note: .claude/ and .agents/ start with a dot — they are hidden directories.")
    print(f"   Linux/macOS : ls -la")
    print(f"   PowerShell  : Get-ChildItem -Force")
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
    print("\n💡 Slash command installed: type /workflow <task> to start the 14-step workflow")
    print("   Example: /workflow implement user authentication with JWT")
    print(f"\n🔄 To update later, re-download install.py and run:")
    print(f"   python install.py --update --yes")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Installation failed: {e}")
        raise
