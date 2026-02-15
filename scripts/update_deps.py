#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import re
import shutil

def run_command(command, cwd=None, capture_output=False):
    try:
        if capture_output:
            return subprocess.check_output(command, shell=True, cwd=cwd, text=True)
        else:
            subprocess.check_call(command, shell=True, cwd=cwd)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        sys.exit(e.returncode)

def bump_version_string(version_str):
    parts = version_str.strip().split('.')
    if len(parts) < 3:
        print(f"Warning: Version string '{version_str}' does not have 3 parts. Appending .1")
        return f"{version_str}.1"

    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        print(f"Warning: Last part of version '{version_str}' is not an integer. Appending .1")
        return f"{version_str}.1"

    return ".".join(parts)

def update_cli(path):
    print(f"Updating CLI in {path}...")

    # Check for uv.lock changes
    lock_file = os.path.join(path, "uv.lock")
    lock_backup = os.path.join(path, "uv.lock.bak")

    if os.path.exists(lock_file):
        shutil.copy2(lock_file, lock_backup)

    run_command("uv sync --upgrade", cwd=path)

    changed = False
    if not os.path.exists(lock_backup):
        changed = True # Created new lock file
    else:
        # Check if contents changed
        with open(lock_file, 'rb') as f1, open(lock_backup, 'rb') as f2:
            if f1.read() != f2.read():
                changed = True
        os.remove(lock_backup)

    if changed:
        print("CLI dependencies updated. Bumping version...")
        pyproject_path = os.path.join(path, "pyproject.toml")

        with open(pyproject_path, 'r') as f:
            content = f.read()

        # Regex to find version = "x.y.z"
        # We look for 'version = "..."' in the [project] section context roughly,
        # but a simple regex usually works if unique enough.
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            current_version = match.group(1)
            new_version = bump_version_string(current_version)
            new_content = content.replace(f'version = "{current_version}"', f'version = "{new_version}"')

            with open(pyproject_path, 'w') as f:
                f.write(new_content)

            print(f"Bumped CLI version to {new_version}")
        else:
            print("Could not find version in pyproject.toml")
    else:
        print("No changes in CLI dependencies.")

def update_image_references(project_root, image_name, new_version):
    """
    Search for usages of the image in stacks and update the version.
    Assumes image name logic: images/foo -> tes4all/foo
    """
    stacks_dir = os.path.join(project_root, "stacks")
    if not os.path.isdir(stacks_dir):
        return

    # Try both standard name and edge-router- prefixed name (e.g. for socket-proxy)
    # Also handle dashes correctly if needed, but basename is usually enough.
    possible_names = [
        f"tes4all/{image_name}",
        f"tes4all/edge-router-{image_name}"
    ]

    updated_files = set()
    found_any = False

    for full_image in possible_names:
        # Regex to match: image: tes4all/foo:${VAR:-old_version}
        # Group 1: image: tes4all/foo:${VAR:-
        # Group 2: old_version
        # Group 3: }
        pattern = re.compile(rf'(image:\s+{re.escape(full_image)}:\$\{{[A-Z0-9_]+:-)([^}}]+)(\}})')

        for root, dirs, files in os.walk(stacks_dir):
            for file in files:
                if file in ("compose.yaml", "compose.yml"):
                    filepath = os.path.join(root, file)

                    with open(filepath, 'r') as f:
                        content = f.read()

                    if full_image not in content:
                        continue

                    found_any = True
                    match = pattern.search(content)
                    if match:
                        current_ref_version = match.group(2)
                        if current_ref_version != new_version:
                            print(f"Updating references to {full_image} in {filepath} (from {current_ref_version} to {new_version})...")
                            new_content = pattern.sub(rf'\g<1>{new_version}\g<3>', content)
                            with open(filepath, 'w') as f:
                                f.write(new_content)
                            updated_files.add(filepath)
                        else:
                            print(f"Reference to {full_image} in {filepath} is already up to date ({new_version}).")

    if not found_any:
        # Only warn if we checked all variants and found nothing
        print(f"Note: No references found for {image_name} (checked {', '.join(possible_names)}) in stacks.")

def update_requirements(path, bump_version=True):
    print(f"Updating requirements in {path}...")
    req_in = os.path.join(path, "requirements.in")
    req_txt = os.path.join(path, "requirements.txt")
    req_new = os.path.join(path, "requirements.txt.new")

    if not os.path.exists(req_in):
        print(f"Error: {req_in} not found.")
        return

    # Compile new requirements
    run_command(f"uv pip compile requirements.in -o requirements.txt.new --upgrade", cwd=path)

    changed = False
    if not os.path.exists(req_txt):
        changed = True
    else:
        with open(req_txt, 'rb') as f1, open(req_new, 'rb') as f2:
            if f1.read() != f2.read():
                changed = True

    if changed:
        print("Dependencies updated.")
        os.replace(req_new, req_txt)

        if bump_version:
            # Update VERSION file
            version_file = os.path.join(path, "VERSION")
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    current_version = f.read().strip()

                new_version = bump_version_string(current_version)

                with open(version_file, 'w') as f:
                    f.write(new_version)
                print(f"Bumped version to {new_version}")

                # Update references in stacks
                # Assume we are running from project root or can deduce it
                # path is absolute path to image dir.
                # project root is path/../..
                project_root = os.path.abspath(os.path.join(path, "..", ".."))
                image_name = os.path.basename(path)
                update_image_references(project_root, image_name, new_version)

            else:
                print("VERSION file not found, skipping version bump.")

        # Sync venv
        print("Syncing virtual environment...")
        run_command("uv venv --allow-existing", cwd=path)
        run_command("uv pip install -r requirements.txt", cwd=path)

    else:
        if os.path.exists(req_new):
            os.remove(req_new)
        print("No changes in dependencies.")

def main():
    parser = argparse.ArgumentParser(description="Update dependencies and bump versions.")
    parser.add_argument("path", help="Path to the project directory")
    parser.add_argument("--type", choices=["cli", "image", "venv"], required=True, help="Type of project to update")

    args = parser.parse_args()

    abs_path = os.path.abspath(args.path)
    if not os.path.isdir(abs_path):
        print(f"Error: Directory {abs_path} does not exist.")
        sys.exit(1)

    if args.type == "cli":
        update_cli(abs_path)
    elif args.type == "image":
        update_requirements(abs_path, bump_version=True)
    elif args.type == "venv":
        update_requirements(abs_path, bump_version=False)

if __name__ == "__main__":
    main()
