#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check GitHub Pull Request status and trigger cleanup when merged.

Usage:
    python scripts/worktree_check_pr_status.py <worktree-id>

Behavior:
- Checks PR status using gh CLI
- If PR is merged → Return exit code 0 (proceed to cleanup)
- If PR is open → Return exit code 1 (continue polling)
- If PR is closed without merge → Return exit code 2 (alert user)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

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

def get_worktree_info(worktree_id: str, registry: Dict) -> Optional[Dict]:
    """Get worktree information from registry."""
    if worktree_id not in registry:
        print(f"❌ Worktree '{worktree_id}' not found in registry")
        return None

    return registry[worktree_id]

def check_pr_status(worktree_id: str) -> Tuple[str, Optional[str]]:
    """
    Check PR status using gh CLI.

    Returns:
        Tuple[str, Optional[str]]: (status, merged_at)
        - status: "MERGED", "OPEN", "CLOSED"
        - merged_at: ISO timestamp if merged, None otherwise
    """

    # Load registry
    registry = load_registry()
    if not registry:
        return ("ERROR", None)

    # Get worktree info
    worktree_info = get_worktree_info(worktree_id, registry)
    if not worktree_info:
        return ("ERROR", None)

    pr_info = worktree_info.get('pr')
    if not pr_info:
        print(f"❌ No PR information found for worktree '{worktree_id}'")
        return ("ERROR", None)

    pr_number = pr_info.get('number')
    pr_title = pr_info.get('title', 'Unknown')

    print(f"🔍 Checking PR #{pr_number}: {pr_title}")

    # Query PR status
    try:
        result = subprocess.run(
            [
                'gh', 'pr', 'view', str(pr_number),
                '--json', 'state,mergedAt,closedAt,title'
            ],
            capture_output=True,
            text=True,
            check=True
        )

        pr_data = json.loads(result.stdout)
        state = pr_data['state']
        merged_at = pr_data.get('mergedAt')

        return (state, merged_at)

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to check PR status: {e.stderr}")
        return ("ERROR", None)

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/worktree_check_pr_status.py <worktree-id>")
        print("\nExample:")
        print("  python scripts/worktree_check_pr_status.py worktree-01")
        sys.exit(2)

    worktree_id = sys.argv[1]

    # Check PR status
    state, merged_at = check_pr_status(worktree_id)

    # Load registry to get PR info
    registry = load_registry()
    worktree_info = get_worktree_info(worktree_id, registry)
    if not worktree_info:
        sys.exit(2)

    pr_info = worktree_info.get('pr', {})
    pr_number = pr_info.get('number')

    if state == "MERGED":
        print(f"✅ PR #{pr_number} has been merged!")
        print(f"   Merged at: {merged_at}")
        print(f"   Proceeding to cleanup...")
        sys.exit(0)  # Signal to proceed to cleanup

    elif state == "OPEN":
        print(f"⏳ PR #{pr_number} is still open")
        print(f"   Waiting for human review and approval...")
        sys.exit(1)  # Signal to continue polling

    elif state == "CLOSED":
        print(f"⚠️  PR #{pr_number} was closed without merge")
        print(f"   Manual cleanup required.")
        print(f"   Run: python scripts/worktree_cleanup.py {worktree_id}")
        sys.exit(2)  # Signal error - PR closed without merge

    else:
        print(f"❌ Unknown PR state: {state}")
        sys.exit(2)

if __name__ == "__main__":
    main()
