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

echo "Starting Phase 2 Test Stack..."
# Build all required images
docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml build valkey edge-router-api cert-manager

# Start services
docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml up -d valkey edge-router-api cert-manager

echo "Waiting for services (15s)..."
sleep 15

echo "Running Phase 2 Tests..."
pytest stacks/edge-router/tests/e2e/test_phase_2.py || {
    echo "Tests Failed!"
    echo "Logs Cert-Manager:"
    docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml logs cert-manager
    exit 1
}

echo "Cleanup..."
docker compose -f stacks/edge-router/compose.yaml -f stacks/edge-router/tests/e2e/compose.test.yaml down -v
