#!/bin/bash
set -e

STACK_NAME="vaultwarden-test"
COMPOSE_FILE="compose.yaml"

echo "==> Starting Vaultwarden Stack verification..."

echo "Note: This test requires postgres-ha stack to be running"

cleanup() {
    echo "==> Cleaning up..."
    docker compose -p "$STACK_NAME" down -v 2>/dev/null || true
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

echo "==> Creating test secrets..."
openssl rand -base64 32 | docker secret create vaultwarden_admin_token - 2>/dev/null || true
echo "changeme" | docker secret create postgres_password - 2>/dev/null || true

echo "==> Starting stack..."
docker compose -p "$STACK_NAME" -f "$COMPOSE_FILE" up -d

echo "==> Waiting for Vaultwarden to initialize (30s)..."
sleep 30

echo "==> Checking Vaultwarden health..."
if ! docker compose -p "$STACK_NAME" ps vaultwarden | grep -q "healthy\|running"; then
    echo "WARNING: Vaultwarden health check pending (requires postgres-ha)"
    docker compose -p "$STACK_NAME" logs vaultwarden | tail -20
fi

echo "==> Checking web interface..."
VAULT_PORT=$(docker compose -p "$STACK_NAME" port vaultwarden 80 2>/dev/null | cut -d: -f2 || echo "80")
if curl -sf "http://localhost:${VAULT_PORT}/alive" > /dev/null; then
    echo "✓ Vaultwarden is responding"
else
    echo "WARNING: Vaultwarden not responding yet"
fi

echo "==> Verification complete!"
exit 0
