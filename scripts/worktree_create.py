#!/usr/bin/env python3
"""
Create isolated git worktree for feature development.

Usage:
    python scripts/worktree_create.py <feature-name>

Creates:
- New worktree directory in ../worktrees/<feature-name>
- Feature branch from current branch (dynamic base branch)
- Isolated Docker environment (if Docker is used)
- Registry entry for tracking

The base branch is auto-detected from your current branch,
enabling nested feature development.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Path to worktree registry
REGISTRY_DIR = Path.home() / ".claude" / "worktrees"
REGISTRY_FILE = REGISTRY_DIR / "registry.json"

def get_current_branch() -> str:
    """Get the current git branch name."""
    result = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()

def get_repo_root() -> Path:
    """Get the root directory of the git repository."""
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=True
    )
    return Path(result.stdout.strip())

def load_registry() -> Dict:
    """Load worktree registry from file."""
    if not REGISTRY_FILE.exists():
        return {}

    with open(REGISTRY_FILE, 'r') as f:
        return json.load(f)

def save_registry(registry: Dict):
    """Save worktree registry to file."""
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)

def generate_worktree_id(registry: Dict) -> str:
    """Generate unique worktree ID."""
    counter = len(registry) + 1
    return f"worktree-{counter:02d}"

def create_worktree(feature_name: str) -> Optional[Dict]:
    """Create new worktree for feature development."""

    # Get current branch as base branch (dynamic!)
    base_branch = get_current_branch()
    print(f"🔍 Detected base branch: {base_branch}")
    print(f"   Feature branch will merge back to: {base_branch}")

    # Get repo root
    repo_root = get_repo_root()

    # Create worktree directory path
    worktrees_dir = repo_root.parent / "worktrees"
    worktrees_dir.mkdir(exist_ok=True)

    worktree_path = worktrees_dir / feature_name

    if worktree_path.exists():
        print(f"❌ Worktree already exists: {worktree_path}")
        return None

    # Create feature branch name
    feature_branch = f"feature/{feature_name}"

    print(f"\n📂 Creating worktree: {feature_name}")
    print(f"   Base branch: {base_branch}")
    print(f"   Feature branch: {feature_branch}")
    print(f"   Location: {worktree_path}")

    # Create worktree
    try:
        subprocess.run(
            ['git', 'worktree', 'add', '-b', feature_branch, str(worktree_path), base_branch],
            check=True
        )
        print(f"✅ Worktree created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create worktree: {e}")
        return None

    # Load registry and generate ID
    registry = load_registry()
    worktree_id = generate_worktree_id(registry)

    # Create registry entry
    worktree_info = {
        'id': worktree_id,
        'feature_name': feature_name,
        'path': str(worktree_path),
        'branch': feature_branch,
        'base_branch': base_branch,  # NEW - save base branch for merge
        'created': datetime.now().isoformat(),
        'status': 'active'
    }

    # Save to registry
    registry[worktree_id] = worktree_info
    save_registry(registry)

    print(f"\n✅ Worktree registered: {worktree_id}")
    print(f"\n📋 Next Steps:")
    print(f"1. cd {worktree_path}")
    print(f"2. Implement your feature")
    print(f"3. Commit your changes")
    print(f"4. Run merge: python scripts/worktree_merge.py {worktree_id}")

    return worktree_info

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/worktree_create.py <feature-name>")
        print("\nExample:")
        print("  python scripts/worktree_create.py auth-component")
        sys.exit(1)

    feature_name = sys.argv[1]

    # Validate feature name
    if not feature_name.replace('-', '').replace('_', '').isalnum():
        print("❌ Invalid feature name. Use only letters, numbers, hyphens, and underscores.")
        sys.exit(1)

    print("=" * 70)
    print("Worktree Manager - Create Worktree")
    print("=" * 70)

    result = create_worktree(feature_name)

    if result:
        print("\n" + "=" * 70)
        print("✅ Worktree Setup Complete!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ Worktree Setup Failed")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
