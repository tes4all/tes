#!/bin/bash
set -e

# Integration Test: Verify Stack Imports
# This script verifies that all Golden Stacks can be imported via `include`
# and that `docker compose config` resolves correctly.

SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

echo "=== Starting Import Integration Test ==="

# 1. Define necessary environment variables required by the stacks
# These are normally provided by .env or the environment
export AUTHENTIK_SECRET_KEY="test_secret_key_for_verification_only"
export POSTGRES_PASSWORD="test_postgres_password"
export ZITADEL_MASTERKEY="MasterkeyNeedsToBe32BytesLong123"
export DOMAIN="test.example.com"

# 2. Run docker compose config to validate the configuration
echo "Validating compose configuration..."
if docker compose config > /dev/null; then
    echo "✅ Configuration is valid."
else
    echo "❌ Configuration failed validation."
    exit 1
fi

# 3. Check if specific services are present in the config output
# This ensures the include actually worked and brought in the services
CONFIG_OUTPUT=$(docker compose config)

check_service() {
    local service=$1
    if echo "$CONFIG_OUTPUT" | grep -q "$service:"; then
        echo "✅ Service '$service' found."
    else
        echo "❌ Service '$service' NOT found in config."
        exit 1
    fi
}

echo "Checking for expected services..."
check_service "server"       # Authentik server
check_service "worker"       # Authentik worker
check_service "valkey"       # Authentik valkey (was redis)
check_service "etcd-1"       # Postgres-HA
check_service "haproxy"      # Edge Router
check_service "vaultwarden"  # Vaultwarden
check_service "zitadel"      # Zitadel

echo "=== Integration Test Passed ==="
