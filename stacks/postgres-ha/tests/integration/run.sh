#!/bin/bash
set -e

# Integration Test for Postgres-HA Stack
# Usage: ./run.sh [local|remote]

MODE=${1:-local}
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

echo "=== Running Postgres-HA Integration Test ($MODE) ==="

# 1. Setup Environment
export POSTGRES_PASSWORD="test_password"

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
if docker compose -f $COMPOSE_FILE ps | grep -q "etcd-1"; then
    echo "✅ etcd-1 is running"
else
    echo "❌ etcd-1 is NOT running"
    exit 1
fi

# 6. Teardown
echo "Tearing down..."
docker compose -f $COMPOSE_FILE down -v
