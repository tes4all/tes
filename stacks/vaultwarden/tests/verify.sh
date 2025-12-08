#!/bin/bash
set -e

# Verification script for Vaultwarden Golden Stack
# This script spins up the stack using SQLite for self-contained testing.

STACK_DIR=$(dirname "$0")/..
cd "$STACK_DIR"

echo "Starting verification..."

# Create mock networks if they don't exist (required for compose to start)
docker network create edge-router-net 2>/dev/null || true
docker network create postgres-ha 2>/dev/null || true

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    docker compose down -v
    # We don't remove networks as they might be used by other things or were pre-existing
}
trap cleanup EXIT

# Set environment for testing (Use SQLite to avoid Postgres dependency)
# Note: For SQLite, Vaultwarden expects a file path, not a URL with scheme
export DATABASE_URL="/data/db.sqlite3"
export DOMAIN="http://localhost"

# Build and start
echo "Building and starting stack..."
docker compose up -d --build

# Wait for healthcheck
echo "Waiting for health..."
MAX_RETRIES=30
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

# Verify API endpoint internally
echo "Verifying /api/alive..."
docker compose exec -T vaultwarden curl -f http://localhost:80/api/alive
echo -e "\nAPI check passed."

echo "Verification successful!"
