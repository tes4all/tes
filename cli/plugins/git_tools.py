import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import click


@click.group()
@click.pass_context
def tools(ctx):
    """Commands for managing Shopify themes."""
    pass


@tools.command()
@click.pass_context
@click.option(
    "--dir", required=False, default=".", help="Base directory to search for repos."
)
@click.option(
    "--show-has-no-changes",
    is_flag=True,
    default=False,
    help="Show repos with no changes.",
)
def status(ctx, dir, show_has_no_changes):
    """Check the output of all repos in the working directory."""
    init_path = os.getcwd()  # Save initial directory
    # os.chdir(working_dir)  # Change to the base directory
    working_dir = os.path.expanduser(dir)
    if not os.path.isdir(working_dir):
        click.echo(f"'{working_dir}' does not exist or is not a directory.")
        return

    repos = get_repos(working_dir)
    # os.chdir(init_path)  # Return to initial directory
    if not repos:
        click.echo("No repos found.")
        return
    print(f"{len(repos)} Repos Found... checking status...")

    # Process repos in parallel with max 20 workers
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all tasks
        future_to_repo = {
            executor.submit(check_git_status, repo): repo for repo in repos
        }

        # Process results as they complete
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                result = future.result()
                results.append(result)

                # Display immediate feedback
                repo_name = result.get("repo", os.path.basename(repo))
                if "error" in result:
                    click.echo(f"❌ {repo_name}: Error - {result['error']}")
                elif result.get("has_changes", False):
                    click.echo(
                        f"⚠️ {repo_name} ({result['branch']}): Has uncommitted changes"
                    )
                elif not result.get("has_changes", False) and show_has_no_changes:
                    click.echo(f"✅ {repo_name} ({result['branch']}): Clean")
            except Exception as e:
                click.echo(f"❌ {os.path.basename(repo)}: Error - {str(e)}")

    # Summary
    clean_count = sum(
        1 for r in results if not r.get("has_changes", False) and "error" not in r
    )
    changed_count = sum(
        1 for r in results if r.get("has_changes", True) and "error" not in r
    )
    error_count = sum(1 for r in results if "error" in r)

    click.echo("\nSummary:")
    click.echo(f"✅ Clean repos: {clean_count}")
    click.echo(f"⚠️ Repos with changes: {changed_count}")
    click.echo(f"❌ Repos with errors: {error_count}")
    click.echo("Done.")

    # click.echo("Done.")


def check_git_status(repo_path):
    """Check git status for a single repository."""
    try:
        # Get repo name for display
        repo_name = os.path.basename(repo_path)

        # Change to repo directory
        current_dir = os.getcwd()
        os.chdir(repo_path)

        # Get git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Return to original directory
        os.chdir(current_dir)

        changes = result.stdout.strip()
        branch = branch_result.stdout.strip()

        return {
            "repo": repo_name,
            "path": repo_path,
            "branch": branch,
            "has_changes": len(changes) > 0,
            "changes": changes,
        }
    except Exception as e:
        return {"repo": os.path.basename(repo_path), "path": repo_path, "error": str(e)}


def get_repos(base_path):
    """Recursively explore directories excluding certain ones and check their Git status."""
    repos = []
    for path in os.listdir(base_path):
        full_path = os.path.join(base_path, path)

        # skip if path is not a directory or starts with _
        if not os.path.isdir(full_path) or path[0] == "_":
            continue

        for repo in os.listdir(full_path):
            repo_path = os.path.join(full_path, repo)
            # skip if path is not a directory or starts with _
            if not os.path.isdir(repo_path) or repo[0] == "_":
                continue
            # Check if the directory is a Git repository
            if os.path.exists(os.path.join(repo_path, ".git")):
                repos.append(repo_path)
    return repos
