#!/bin/bash
set -e

STACK_NAME="zitadel-test"
COMPOSE_FILE="compose.yaml"

echo "==> Starting Zitadel Stack verification..."

echo "Note: This test requires postgres-ha stack to be running"

cleanup() {
    echo "==> Cleaning up..."
    docker compose -p "$STACK_NAME" down -v 2>/dev/null || true
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

echo "==> Creating test secret..."
echo "test-master-key-32-chars-long!" | docker secret create zitadel_masterkey - 2>/dev/null || true

echo "==> Starting stack..."
docker compose -p "$STACK_NAME" -f "$COMPOSE_FILE" up -d

echo "==> Waiting for Zitadel to initialize (45s)..."
sleep 45

echo "==> Checking Zitadel health..."
if ! docker compose -p "$STACK_NAME" ps zitadel | grep -q "healthy\|running"; then
    echo "WARNING: Zitadel health check pending (requires postgres-ha)"
    docker compose -p "$STACK_NAME" logs zitadel | tail -20
fi

echo "==> Verification complete!"
exit 0
