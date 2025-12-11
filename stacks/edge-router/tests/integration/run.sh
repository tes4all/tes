#!/bin/bash
set -e

# Integration Test for Edge-Router Stack
# Usage: ./run.sh [local|remote]

MODE=${1:-local}
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

echo "=== Running Edge-Router Integration Test ($MODE) ==="

# 1. Setup Environment
# Load versions from parent test env if available
if [ -f "../.env" ]; then
    set -a
    source "../.env"
    set +a
fi

# Set defaults if not set
export HAPROXY_VERSION="${HAPROXY_VERSION:-3.3.0}"
export TRAEFIK_VERSION="${TRAEFIK_VERSION:-3.6.4}"
export ACME_EMAIL="test@example.com"

# 2. Select Compose File
COMPOSE_FILE="compose.local.yaml"
if [ "$MODE" == "remote" ]; then
    COMPOSE_FILE="compose.remote.yaml"
fi

# 3. Validate Config
echo "Validating config..."
docker compose -f $COMPOSE_FILE config > /dev/null

# 4. Run Stack
echo "Starting stack..."
docker compose -f $COMPOSE_FILE up -d --wait

# 5. Verify
echo "Verifying services..."
if docker compose -f $COMPOSE_FILE ps | grep -q "haproxy"; then
    echo "✅ HAProxy is running"
else
    echo "❌ HAProxy is NOT running"
    exit 1
fi

if docker compose -f $COMPOSE_FILE ps | grep -q "traefik"; then
    echo "✅ Traefik is running"
else
    echo "❌ Traefik is NOT running"
    exit 1
fi

# 6. Teardown
echo "Tearing down..."
docker compose -f $COMPOSE_FILE down -v
