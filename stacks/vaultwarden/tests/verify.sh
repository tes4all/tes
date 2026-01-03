#!/bin/bash
set -e

# Verification script for Vaultwarden Golden Stack
# This script spins up the stack using the default internal Postgres.

STACK_DIR=$(dirname "$0")/..
cd "$STACK_DIR"

echo "Starting verification..."

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    docker compose down -v
}
trap cleanup EXIT

# Set environment for testing
export DOMAIN="http://localhost:8080"

# Build image
echo "Building image..."
docker build -t tes4all/vaultwarden:latest ../../images/vaultwarden

# Build and start
echo "Starting stack..."
docker compose up -d

# Wait for healthcheck
echo "Waiting for health..."
MAX_RETRIES=60 # Increased for Postgres startup
count=0
while [ $count -lt $MAX_RETRIES ]; do
    # Check if vaultwarden service is healthy
    if docker compose ps vaultwarden | grep -q "(healthy)"; then
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
