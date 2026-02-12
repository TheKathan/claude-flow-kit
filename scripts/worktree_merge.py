#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge feature branch back to base branch (dynamic, not hardcoded main).

Usage:
    python scripts/worktree_merge.py <worktree-id>

Merges the feature branch back to the base branch it was created from,
enabling nested feature development and flexible branching strategies.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Path to worktree registry
REGISTRY_DIR = Path.home() / ".claude" / "worktrees"
REGISTRY_FILE = REGISTRY_DIR / "registry.json"

def load_registry() -> Dict:
    """Load worktree registry from file."""
    if not REGISTRY_FILE.exists():
        print("❌ Worktree registry not found. No worktrees to merge.")
        return {}

    with open(REGISTRY_FILE, 'r') as f:
        return json.load(f)

def save_registry(registry: Dict):
    """Save worktree registry to file."""
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)

def get_worktree_info(worktree_id: str, registry: Dict) -> Optional[Dict]:
    """Get worktree information from registry."""
    if worktree_id not in registry:
        print(f"❌ Worktree '{worktree_id}' not found in registry")
        return None

    return registry[worktree_id]

def merge_worktree(worktree_id: str):
    """Merge feature branch to base branch."""

    # Load registry
    registry = load_registry()
    if not registry:
        sys.exit(1)

    # Get worktree info
    worktree_info = get_worktree_info(worktree_id, registry)
    if not worktree_info:
        sys.exit(1)

    feature_branch = worktree_info['branch']
    base_branch = worktree_info['base_branch']  # Dynamic base branch

    print(f"\n🔀 Merging Feature to Base Branch")
    print(f"   Feature branch: {feature_branch}")
    print(f"   Base branch: {base_branch}")

    # Checkout base branch
    print(f"\n📍 Checking out base branch: {base_branch}")
    try:
        subprocess.run(['git', 'checkout', base_branch], check=True)
        print(f"✅ Checked out {base_branch}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to checkout {base_branch}: {e}")
        sys.exit(1)

    # Pull latest changes from remote
    print(f"\n⬇️  Pulling latest changes from remote...")
    try:
        subprocess.run(['git', 'pull', 'origin', base_branch], check=True)
        print(f"✅ Pulled latest changes")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not pull from remote: {e}")

    # Merge feature branch
    print(f"\n🔀 Merging {feature_branch} → {base_branch}")
    try:
        subprocess.run(['git', 'merge', feature_branch, '--no-ff', '-m',
                       f'Merge {feature_branch} into {base_branch}'], check=True)
        print(f"✅ Merged successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Merge failed: {e}")
        print(f"\n⚠️  Please resolve conflicts manually and then run:")
        print(f"   git merge --continue")
        print(f"   python scripts/worktree_cleanup.py {worktree_id}")
        sys.exit(1)

    # Push to remote
    print(f"\n⬆️  Pushing {base_branch} to remote...")
    try:
        subprocess.run(['git', 'push', 'origin', base_branch], check=True)
        print(f"✅ Pushed {base_branch} to remote")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not push to remote: {e}")

    # Update registry status
    worktree_info['status'] = 'merged'
    registry[worktree_id] = worktree_info
    save_registry(registry)

    print(f"\n✅ Merge Complete!")
    print(f"\n📋 Next Steps:")
    print(f"1. Verify the merge: git log --oneline -10")
    print(f"2. Run cleanup: python scripts/worktree_cleanup.py {worktree_id}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/worktree_merge.py <worktree-id>")
        print("\nExample:")
        print("  python scripts/worktree_merge.py worktree-01")
        sys.exit(1)

    worktree_id = sys.argv[1]

    print("=" * 70)
    print("Worktree Manager - Merge Feature")
    print("=" * 70)

    merge_worktree(worktree_id)

    print("\n" + "=" * 70)
    print("✅ Merge Complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
