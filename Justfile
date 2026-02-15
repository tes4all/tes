# Justfile for monorepo management

# Update all python projects using uv
update-all:
    @python3 scripts/update_deps.py cli --type cli
    @python3 scripts/update_deps.py images/cert-manager --type image
    @python3 scripts/update_deps.py images/cert-syncer --type image
    @python3 scripts/update_deps.py images/edge-router-api --type image
    @python3 scripts/update_deps.py stacks/edge-router/tests/e2e --type venv

# Update Docker images
update-images:
    @uv run --with requests --with packaging python3 scripts/update_docker_images.py .
