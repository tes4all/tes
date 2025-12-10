#!/bin/bash
set -e

# Verification script for Zitadel Golden Stack
# This script spins up the stack along with a temporary Postgres container for testing.

STACK_DIR=$(dirname "$0")/..
cd "$STACK_DIR"

echo "Starting verification..."

# Create mock networks
docker network create edge-router-net 2>/dev/null || true
docker network create postgres-ha 2>/dev/null || true

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    docker compose down -v
    docker rm -f zitadel-postgres-test 2>/dev/null || true
    # We don't remove networks
}
trap cleanup EXIT

# Start a temporary Postgres container
echo "Starting temporary Postgres..."
docker run -d --name zitadel-postgres-test \
  --network postgres-ha \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  postgres:14-alpine

# Wait for Postgres to be ready
echo "Waiting for Postgres..."
sleep 5

# Set environment for testing
export ZITADEL_MASTERKEY="MasterkeyNeedsToBe32BytesLong123"
export POSTGRES_PASSWORD="changeit"
export ZITADEL_DB_PASSWORD="zitadel_secret"
export DOMAIN="localhost"

# We need to override the config to point to our test container instead of 'postgres-ha'
# Since config is baked, we can override via env vars if Zitadel supports it, or we rely on docker alias.
# Zitadel config supports env vars.
# But our config.yaml has `Host: postgres-ha`.
# We can use a network alias or just rely on the fact that we can't easily change the baked config host without rebuilding.
# However, we can use `extra_hosts` or just run the postgres container with the alias `postgres-ha` in the network?
# No, `postgres-ha` is the network name in the compose file, but the host in config is `postgres-ha`.
# We can start the test postgres container with `--network-alias postgres-ha`.

docker rm -f zitadel-postgres-test 2>/dev/null || true
docker run -d --name zitadel-postgres-test \
  --network postgres-ha \
  --network-alias postgres-ha \
  -e POSTGRES_PASSWORD=changeit \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  postgres:14-alpine

echo "Waiting for Postgres (again)..."
sleep 5

# Build and start
echo "Building and starting stack..."
docker compose up -d --build

# Wait for healthcheck
echo "Waiting for health..."
MAX_RETRIES=60 # Zitadel init takes time
count=0
while [ $count -lt $MAX_RETRIES ]; do
    if docker compose ps | grep -q "(healthy)"; then
        echo "Service is healthy!"
        break
    fi
    sleep 2
    count=$((count+1))
    echo "Waiting... ($count/$MAX_RETRIES)"
done

if [ $count -ge $MAX_RETRIES ]; then
    echo "Timeout waiting for health."
    docker compose logs
    exit 1
fi

# Verify Metrics
echo "Verifying metrics..."
# Zitadel exposes metrics on /debug/metrics or similar, but we configured it.
# Default port 8080.
if curl -s http://localhost:8080/debug/metrics | grep -q "go_goroutines"; then
    echo "Metrics endpoint is active."
else
    echo "Metrics check failed (or path is different)."
    # Try /metrics
    if curl -s http://localhost:8080/metrics | grep -q "go_goroutines"; then
         echo "Metrics endpoint is active (at /metrics)."
    else
         echo "Metrics check failed."
         exit 1
    fi
fi

echo "Verification passed!"
