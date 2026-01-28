#!/bin/bash
set -e

# Path from repo root
cd "$(dirname "$0")/../../.."

echo "Installing Test Dependencies..."
if command -v uv &> /dev/null; then
    uv venv .venv 2>/dev/null || true
    source .venv/bin/activate 2>/dev/null || true
    uv pip install -q -r stacks/edge-router/tests/e2e/requirements.txt
else
    pip install -q -r stacks/edge-router/tests/e2e/requirements.txt
fi

echo "Starting Phase 3 Test Stack..."
docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml build

echo "Running Phase 3 Tests..."
pytest stacks/edge-router/tests/e2e/test_phase_3.py || {
    echo "Tests Failed!"
    echo "Logs Cert-Syncer:"
    docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml logs cert-syncer
    echo "Logs Traefik:"
    docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml logs traefik
    exit 1
}

echo "Cleanup..."
docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml down -v
