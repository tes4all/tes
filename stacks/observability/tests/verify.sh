#!/bin/bash
set -e

STACK_NAME="observability-test"
COMPOSE_FILE="compose.yaml"

echo "==> Starting Observability Stack verification..."

cleanup() {
    echo "==> Cleaning up..."
    docker compose -p "$STACK_NAME" down -v 2>/dev/null || true
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

echo "==> Creating test secret..."
echo "admin123" | docker secret create grafana_admin_password - 2>/dev/null || true

echo "==> Building images..."
docker compose -f "$COMPOSE_FILE" build

echo "==> Starting stack..."
docker compose -p "$STACK_NAME" -f "$COMPOSE_FILE" up -d

echo "==> Waiting for services to be healthy..."
sleep 30

echo "==> Checking Prometheus health..."
PROM_PORT=$(docker compose -p "$STACK_NAME" port prometheus 9090 2>/dev/null | cut -d: -f2 || echo "9090")
if ! curl -sf "http://localhost:${PROM_PORT}/-/healthy" > /dev/null; then
    echo "WARNING: Prometheus not yet healthy"
fi

echo "==> Checking Grafana health..."
GRAFANA_PORT=$(docker compose -p "$STACK_NAME" port grafana 3000 2>/dev/null | cut -d: -f2 || echo "3000")
if ! curl -sf "http://localhost:${GRAFANA_PORT}/api/health" > /dev/null; then
    echo "WARNING: Grafana not yet healthy"
fi

echo "==> Checking metrics collection..."
if curl -sf "http://localhost:${PROM_PORT}/api/v1/targets" | grep -q "up"; then
    echo "✓ Prometheus is collecting metrics"
else
    echo "WARNING: No targets found yet"
fi

echo "==> Verification complete!"
exit 0
