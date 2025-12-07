#!/bin/bash
set -e

STACK_NAME="edge-router-test"
COMPOSE_FILE="compose.yaml"

echo "==> Starting Edge Router Stack verification..."

cleanup() {
    echo "==> Cleaning up..."
    docker compose -p "$STACK_NAME" down -v 2>/dev/null || true
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

echo "==> Building images..."
docker compose -f "$COMPOSE_FILE" build

echo "==> Starting stack..."
docker compose -p "$STACK_NAME" -f "$COMPOSE_FILE" up -d

echo "==> Waiting for services to be healthy..."
sleep 15

echo "==> Checking HAProxy health..."
if ! docker compose -p "$STACK_NAME" ps haproxy | grep -q "healthy\|running"; then
    echo "ERROR: HAProxy is not healthy"
    docker compose -p "$STACK_NAME" logs haproxy
    exit 1
fi

echo "==> Checking HAProxy metrics endpoint..."
HAPROXY_PORT=$(docker compose -p "$STACK_NAME" port haproxy 8404 | cut -d: -f2)
if ! curl -sf "http://localhost:${HAPROXY_PORT}/metrics" | grep -q "haproxy"; then
    echo "ERROR: HAProxy metrics not accessible"
    exit 1
fi

echo "==> Checking Traefik health..."
if ! docker compose -p "$STACK_NAME" ps traefik | grep -q "healthy\|running"; then
    echo "ERROR: Traefik is not healthy"
    docker compose -p "$STACK_NAME" logs traefik
    exit 1
fi

echo "==> All checks passed!"
exit 0
