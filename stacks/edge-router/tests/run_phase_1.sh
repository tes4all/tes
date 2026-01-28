#!/bin/bash
set -e

# Path from repo root
cd "$(dirname "$0")/../../.."

echo "Installing Test Dependencies..."
# Ensure uv is installed/available or use system pip if preferred,
# but user requested uv. We assume uv is present in dev env or skip to pip.
if command -v uv &> /dev/null; then
    uv venv .venv 2>/dev/null || true
    source .venv/bin/activate 2>/dev/null || true
    uv pip install -q -r stacks/edge-router/tests/e2e/requirements.txt
else
    pip install -q -r stacks/edge-router/tests/e2e/requirements.txt
fi

echo "Starting Phase 1 Test Stack..."
docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml up -d --build valkey edge-router-api

echo "Waiting for healthchecks (10s)..."
sleep 10

echo "Running Tests..."
# Run pytest. If it fails, script exits with non-zero due to set -e,
# but we want to ensure teardown happens usually.
# For strict CI, fail is fine. For dev, maybe user wants to debug.
pytest stacks/edge-router/tests/e2e/test_phase_1.py || {
    echo "Tests Failed!"
    echo "Logs Edge-Router-API:"
    docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml logs edge-router-api
    exit 1
}

echo "Cleanup..."
docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml down -v
