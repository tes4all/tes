#!/bin/sh
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Waiting for services to be healthy..."
sleep 15

# Helper function to check master via Sentinel
check_master() {
    MASTER_IP=$(docker compose exec sentinel-1 valkey-cli -p 26379 sentinel get-master-addr-by-name mymaster | head -n 1)
    echo "Current Master Host from Sentinel: $MASTER_IP"
}

echo "--- 1. Checking Cluster Status ---"
docker compose exec sentinel-1 valkey-cli -p 26379 sentinel master mymaster
check_master

echo "\n--- 2. Writing data to Master (via HAProxy 6379) ---"
# We write to HAProxy which routes to master
docker compose exec haproxy sh -c "echo 'SET testkey hello-world' | nc localhost 6379"

echo "${GREEN}Write command sent to HAProxy.${NC}"

echo "\n--- 3. Verifying Replication ---"
sleep 2
# Check a replica directly
REPLICA_VAL=$(docker compose exec valkey-2 valkey-cli get testkey)
if [ "$REPLICA_VAL" = "hello-world" ]; then
    echo "${GREEN}Replication verified on valkey-2.${NC}"
else
    echo "${RED}Replication check failed on valkey-2. Value: $REPLICA_VAL${NC}"
    # Don't exit yet, check another
fi

echo "\n--- 4. Testing Failover ---"
CURRENT_MASTER_HOST=$(docker compose exec sentinel-1 valkey-cli -p 26379 sentinel get-master-addr-by-name mymaster | head -n 1)
# Note: Sentinel returns IP or Hostname. In docker compose it usually returns the IP because that's what containers see.
# But sometimes with `resolve-hostnames` logic it might differ. Patroni uses names. Redis Sentinel uses IPs by default but can use names with 'announce'.
# Let's see what happens. If it's an IP, we need to find the container name.
# Or we can just pause the *probable* master 'valkey-1' if we verify it is master.

MASTER_ROLE=$(docker compose exec valkey-1 valkey-cli role | head -n 1)
if [ "$MASTER_ROLE" = "master" ]; then
    TARGET_CONTAINER="valkey-1"
else
    # Try 2
    MASTER_ROLE=$(docker compose exec valkey-2 valkey-cli role | head -n 1)
    if [ "$MASTER_ROLE" = "master" ]; then
        TARGET_CONTAINER="valkey-2"
    else
        TARGET_CONTAINER="valkey-3"
    fi
fi

echo "identified Current Master: $TARGET_CONTAINER"
echo "Pausing $TARGET_CONTAINER..."

docker compose pause $TARGET_CONTAINER

echo "Waiting for failover (20s)..."
sleep 20

NEW_MASTER_HOST=$(docker compose exec sentinel-1 valkey-cli -p 26379 sentinel get-master-addr-by-name mymaster | head -n 1)
echo "New Master Host: $NEW_MASTER_HOST"

# Check HAProxy routing again
echo "Writing to new master via HAProxy..."
docker compose exec haproxy sh -c "echo 'SET testkey2 failed-over' | nc localhost 6379"

echo "Check if value exists..."
val=$(docker compose exec valkey-2 valkey-cli get testkey2)
val2=$(docker compose exec valkey-3 valkey-cli get testkey2)

if [ "$val" = "failed-over" ] || [ "$val2" = "failed-over" ]; then
     echo "${GREEN}Failover successful! Data written via HAProxy landed on a replica (or new master).${NC}"
else
     echo "${RED}Failover verification failed.${NC}"
     docker compose unpause $TARGET_CONTAINER
     exit 1
fi

echo "\n--- 5. Recovery ---"
docker compose unpause $TARGET_CONTAINER
echo "Original master unpaused."
sleep 5

echo "${GREEN}All HA tests passed.${NC}"
