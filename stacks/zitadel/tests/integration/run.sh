#!/bin/bash
set -e

# Integration Test for Zitadel Stack
# Usage: ./run.sh [local|remote]

MODE=${1:-local}
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

echo "=== Running Zitadel Integration Test ($MODE) ==="

# 1. Setup Environment
export ZITADEL_MASTERKEY="MasterkeyNeedsToBe32BytesLong123"
export POSTGRES_PASSWORD="postgres"
export ZITADEL_DB_PASSWORD="postgres"
export DOMAIN="auth.test.com"

# 2. Create Networks
echo "Creating networks..."
docker network create edge-router-net 2>/dev/null || true
docker network create postgres-ha 2>/dev/null || true

# 3. Select Compose File
COMPOSE_FILE="compose.local.yaml"
if [ "$MODE" == "remote" ]; then
    COMPOSE_FILE="compose.remote.yaml"
fi

# 4. Validate Config
echo "Validating config..."
docker compose -f $COMPOSE_FILE config > /dev/null

# 5. Run Stack
echo "Starting stack..."
docker compose -f $COMPOSE_FILE up -d --wait

# 6. Verify
echo "Verifying services..."
if docker compose -f $COMPOSE_FILE ps | grep -q "zitadel"; then
    echo "✅ Zitadel is running"
else
    echo "❌ Zitadel is NOT running"
    exit 1
fi

# 7. Teardown
echo "Tearing down..."
docker compose -f $COMPOSE_FILE down -v
