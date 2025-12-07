#!/bin/bash
set -e

STACK_NAME="postgres-ha-test"
COMPOSE_FILE="compose.yaml"

echo "==> Starting Postgres HA Stack verification..."

cleanup() {
    echo "==> Cleaning up..."
    docker compose -p "$STACK_NAME" down -v 2>/dev/null || true
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

echo "==> Creating test secrets..."
echo "changeme" | docker secret create postgres_password - 2>/dev/null || true
echo "replicapass" | docker secret create replication_password - 2>/dev/null || true

echo "==> Building images..."
docker compose -f "$COMPOSE_FILE" build

echo "==> Starting stack..."
docker compose -p "$STACK_NAME" -f "$COMPOSE_FILE" up -d

echo "==> Waiting for Patroni cluster to initialize (60s)..."
sleep 60

echo "==> Checking Postgres health..."
if ! docker compose -p "$STACK_NAME" ps postgres1 | grep -q "healthy\|running"; then
    echo "ERROR: Postgres1 is not healthy"
    docker compose -p "$STACK_NAME" logs postgres1
    exit 1
fi

echo "==> Checking exporter metrics..."
EXPORTER_CONTAINER=$(docker compose -p "$STACK_NAME" ps -q postgres_exporter)
if ! docker exec "$EXPORTER_CONTAINER" wget -qO- http://localhost:9187/metrics | grep -q "pg_up"; then
    echo "ERROR: Postgres exporter metrics not accessible"
    exit 1
fi

echo "==> All checks passed!"
exit 0
