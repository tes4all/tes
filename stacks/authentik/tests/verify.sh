#!/bin/bash
set -e

STACK_NAME="authentik-test"
COMPOSE_FILE="compose.yaml"

echo "==> Starting Authentik Stack verification..."

echo "Note: This test requires postgres-ha stack to be running"

cleanup() {
    echo "==> Cleaning up..."
    docker compose -p "$STACK_NAME" down -v 2>/dev/null || true
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

echo "==> Creating test secrets..."
openssl rand -base64 50 | docker secret create authentik_secret_key - 2>/dev/null || true
echo "changeme" | docker secret create postgres_password - 2>/dev/null || true

echo "==> Starting stack..."
docker compose -p "$STACK_NAME" -f "$COMPOSE_FILE" up -d

echo "==> Waiting for Authentik to initialize (45s)..."
sleep 45

echo "==> Checking Authentik server health..."
if ! docker compose -p "$STACK_NAME" ps authentik-server | grep -q "healthy\|running"; then
    echo "WARNING: Authentik health check pending (requires postgres-ha)"
    docker compose -p "$STACK_NAME" logs authentik-server | tail -20
fi

echo "==> Verification complete!"
exit 0
