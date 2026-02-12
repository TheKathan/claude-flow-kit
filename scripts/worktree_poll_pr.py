#!/usr/bin/env python3
"""
Poll PR status until merged, then trigger cleanup.

Usage:
    python scripts/worktree_poll_pr.py <worktree-id> [--interval MINUTES]

Default polling interval: 5 minutes

This script continuously monitors a GitHub PR until it's merged by a human,
then automatically triggers cleanup. Useful for the PR workflow variant.
"""

import sys
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

def poll_pr_status(worktree_id: str, interval_minutes: int = 5):
    """Poll PR status with configurable interval."""
    print(f"🔄 Starting PR status polling (every {interval_minutes} minutes)")
    print(f"   Press Ctrl+C to stop polling\n")

    poll_count = 0
    interval_seconds = interval_minutes * 60

    while True:
        poll_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Poll #{poll_count}")

        # Check PR status
        result = subprocess.run(
            ['python', 'scripts/worktree_check_pr_status.py', worktree_id],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            # PR merged - proceed to cleanup
            print("\n" + "=" * 70)
            print("✅ PR Merged - Triggering Cleanup")
            print("=" * 70)

            cleanup_result = subprocess.run(
                ['python', 'scripts/worktree_cleanup.py', worktree_id],
                capture_output=True,
                text=True
            )

            print(cleanup_result.stdout)

            if cleanup_result.returncode == 0:
                print("\n✅ Workflow complete!")
                sys.exit(0)
            else:
                print(f"\n❌ Cleanup failed")
                print(cleanup_result.stderr)
                sys.exit(1)

        elif result.returncode == 1:
            # PR still open - continue polling
            next_poll_time = datetime.fromtimestamp(time.time() + interval_seconds)
            print(f"   Next poll: {next_poll_time.strftime('%H:%M:%S')}\n")
            time.sleep(interval_seconds)

        else:
            # PR closed without merge or error
            print(f"\n❌ PR closed without merge or error occurred")
            print(result.stderr if result.stderr else "")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Poll PR status until merged',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Poll every 5 minutes (default)
  python scripts/worktree_poll_pr.py worktree-01

  # Poll every 2 minutes
  python scripts/worktree_poll_pr.py worktree-01 --interval 2

  # Poll every 10 minutes
  python scripts/worktree_poll_pr.py worktree-01 --interval 10
        """
    )
    parser.add_argument('worktree_id', help='Worktree ID to monitor')
    parser.add_argument('--interval', type=int, default=5,
                       help='Polling interval in minutes (default: 5)')

    args = parser.parse_args()

    print("=" * 70)
    print("PR Manager - Poll PR Status")
    print("=" * 70)
    print()

    try:
        poll_pr_status(args.worktree_id, args.interval)
    except KeyboardInterrupt:
        print("\n\n⚠️  Polling stopped by user")
        print("   PR is still open - cleanup will not run automatically")
        print(f"   To manually cleanup later: python scripts/worktree_cleanup.py {args.worktree_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()
