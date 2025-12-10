#!/bin/bash
set -e

# Verification script for Authentik Golden Stack
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
    docker rm -f authentik-postgres-test 2>/dev/null || true
    # We don't remove networks
}
trap cleanup EXIT

# Start a temporary Postgres container
echo "Starting temporary Postgres..."
docker run -d --name authentik-postgres-test \
  --network postgres-ha \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=authentik \
  -e POSTGRES_DB=authentik \
  postgres:14-alpine

# Wait for Postgres to be ready
echo "Waiting for Postgres..."
sleep 5

# Set environment for testing
export AUTHENTIK_SECRET_KEY="test_secret_key_1234567890"
export POSTGRES_PASSWORD="postgres"
# Override host to point to our test container
export AUTHENTIK_POSTGRESQL__HOST="authentik-postgres-test"

# Build and start
echo "Building and starting stack..."
docker compose up -d --build

# Wait for healthcheck
echo "Waiting for health..."
MAX_RETRIES=60 # Authentik can take a while to migrate
count=0
while [ $count -lt $MAX_RETRIES ]; do
    # Check if server is healthy
    if docker compose ps server | grep -q "(healthy)"; then
        echo "Server is healthy!"
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
# We need to find the port mapping or run curl inside the network
# Since we didn't map ports to host in compose (only exposed), we might need to use docker exec or run a curl container.
# But wait, compose file has ports: "9000:9000".
if curl -s http://localhost:9000/-/metrics | grep -q "go_goroutines"; then
    echo "Metrics endpoint is active."
else
    echo "Metrics check failed."
    exit 1
fi

echo "Verification passed!"
