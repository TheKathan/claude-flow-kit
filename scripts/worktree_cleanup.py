#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup worktree and Docker resources, return to base branch.

Usage:
    python scripts/worktree_cleanup.py <worktree-id>

Actions:
- Remove worktree directory
- Remove Docker containers/volumes/networks (if Docker is used)
- Update worktree registry
- Return to base branch (dynamic, not hardcoded main)
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
        print("❌ Worktree registry not found.")
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

def cleanup_docker(worktree_path: Path):
    """Cleanup Docker resources for worktree."""
    print(f"\n🐳 Cleaning up Docker resources...")

    # Check if docker-compose.yml exists in worktree
    docker_compose = worktree_path / "docker-compose.yml"
    if not docker_compose.exists():
        print("  ⚠️  No docker-compose.yml found, skipping Docker cleanup")
        return

    # Stop and remove containers
    try:
        subprocess.run(
            ['docker-compose', 'down', '-v'],
            cwd=worktree_path,
            check=True
        )
        print("  ✅ Removed Docker containers and volumes")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Warning: Could not cleanup Docker: {e}")
    except FileNotFoundError:
        print("  ⚠️  docker-compose not found, skipping Docker cleanup")

def cleanup_worktree(worktree_id: str):
    """Cleanup worktree and associated resources."""

    # Load registry
    registry = load_registry()
    if not registry:
        sys.exit(1)

    # Get worktree info
    worktree_info = get_worktree_info(worktree_id, registry)
    if not worktree_info:
        sys.exit(1)

    worktree_path = Path(worktree_info['path'])
    feature_branch = worktree_info['branch']
    base_branch = worktree_info['base_branch']  # Dynamic base branch

    print(f"\n🧹 Cleaning up worktree: {worktree_id}")
    print(f"   Feature: {worktree_info['feature_name']}")
    print(f"   Branch: {feature_branch}")
    print(f"   Base: {base_branch}")

    # Cleanup Docker if worktree exists
    if worktree_path.exists():
        cleanup_docker(worktree_path)

    # Remove worktree
    print(f"\n📂 Removing worktree...")
    try:
        subprocess.run(['git', 'worktree', 'remove', str(worktree_path), '--force'], check=True)
        print(f"✅ Removed worktree directory")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not remove worktree: {e}")

        # Try manual removal
        if worktree_path.exists():
            print(f"  Attempting manual removal...")
            import shutil
            try:
                shutil.rmtree(worktree_path)
                print(f"  ✅ Manually removed worktree directory")
            except Exception as e2:
                print(f"  ❌ Failed to manually remove: {e2}")

    # Delete feature branch
    print(f"\n🌿 Deleting feature branch: {feature_branch}")
    try:
        subprocess.run(['git', 'branch', '-D', feature_branch], check=True)
        print(f"✅ Deleted local feature branch")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not delete branch: {e}")

    # Delete remote feature branch (if exists)
    print(f"\n🌐 Deleting remote feature branch...")
    try:
        subprocess.run(['git', 'push', 'origin', '--delete', feature_branch], check=True)
        print(f"✅ Deleted remote feature branch")
    except subprocess.CalledProcessError as e:
        print(f"  ℹ️  Remote branch may not exist or already deleted")

    # Return to base branch
    print(f"\n📍 Returning to base branch: {base_branch}")
    try:
        subprocess.run(['git', 'checkout', base_branch], check=True)
        print(f"✅ Returned to {base_branch}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not checkout {base_branch}: {e}")

    # Update registry
    worktree_info['status'] = 'cleaned_up'
    registry[worktree_id] = worktree_info
    save_registry(registry)

    print(f"\n✅ Cleanup Complete!")
    print(f"   Worktree: {worktree_id}")
    print(f"   Status: cleaned_up")
    print(f"   Current branch: {base_branch}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/worktree_cleanup.py <worktree-id>")
        print("\nExample:")
        print("  python scripts/worktree_cleanup.py worktree-01")
        sys.exit(1)

    worktree_id = sys.argv[1]

    print("=" * 70)
    print("Worktree Manager - Cleanup Worktree")
    print("=" * 70)

    cleanup_worktree(worktree_id)

    print("\n" + "=" * 70)
    print("✅ Cleanup Complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
