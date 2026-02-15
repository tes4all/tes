"""
Edge Router management commands.
"""
import click
import subprocess
import os
import sys

@click.command()
def test():
    """Run E2E tests for the Edge Router stack."""
    click.echo("🚀 Starting Edge Router E2E Tests...")

    # Locate the test runner script relative to the repo root
    # Assumption: CLI is run from repo root or we can find it
    # But let's assume running from root for now as per other scripts
    script_path = "stacks/edge-router/tests/run_phase_3.sh"

    if not os.path.exists(script_path):
        # specific check if we are not in root
        if os.path.exists(f"../../{script_path}"):
             script_path = f"../../{script_path}"

    if not os.path.exists(script_path):
        click.echo(f"❌ Error: Could not find test runner at {script_path}")
        sys.exit(1)

    try:
        # Use bash explicitly
        result = subprocess.run(["bash", script_path], check=True)
        if result.returncode == 0:
            click.echo("✅ Tests passed successfully!")
    except subprocess.CalledProcessError:
        click.echo("💥 Tests failed.")
        sys.exit(1)
