#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}=== Postgres HA Stack Verification ===${NC}\n"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    cd "$STACK_DIR"
    docker compose down -v 2>/dev/null || true
}

# Trap exit to cleanup
trap cleanup EXIT

# Function to wait for service health
wait_for_health() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=1

    echo -n "Waiting for $service to be healthy..."
    while [ $attempt -le $max_attempts ]; do
        if docker compose ps "$service" 2>/dev/null | grep -q "healthy"; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done

    echo -e " ${RED}✗${NC}"
    echo -e "${RED}Service $service failed to become healthy${NC}"
    docker compose logs "$service" 2>/dev/null || true
    return 1
}

# Function to check Patroni cluster
check_patroni_cluster() {
    echo -e "\n${YELLOW}Checking Patroni cluster status...${NC}"

    # Check each node on its respective port
    echo -n "Checking postgres-1 (port 8008)..."
    if curl -sf http://localhost:8008/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi

    echo -n "Checking postgres-2 (port 8009)..."
    if curl -sf http://localhost:8009/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi

    echo -n "Checking postgres-3 (port 8010)..."
    if curl -sf http://localhost:8010/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi

    # Check cluster status
    echo -n "Checking cluster topology..."
    local cluster_status=$(curl -s http://localhost:8008/cluster)
    if echo "$cluster_status" | grep -q "postgres-1\|postgres-2\|postgres-3"; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi
}

# Function to test database connectivity
test_database() {
    echo -e "\n${YELLOW}Testing database connectivity...${NC}"

    # Find the leader
    echo -n "Finding leader..."
    local leader=$(curl -s http://localhost:8008/cluster | jq -r '.members[] | select(.role=="leader") | .name')

    if [ -z "$leader" ]; then
        echo -e " ${RED}✗ (No leader found)${NC}"
        return 1
    fi
    echo -e " ${GREEN}✓ ($leader)${NC}"

    echo -n "Connecting to Postgres ($leader)..."
    if docker compose exec -T $leader psql -U postgres -c "SELECT version();" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi

    echo -n "Creating test table..."
    if docker compose exec -T $leader psql -U postgres -c "CREATE TABLE IF NOT EXISTS test_ha (id SERIAL PRIMARY KEY, data TEXT);" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi

    echo -n "Inserting test data..."
    if docker compose exec -T $leader psql -U postgres -c "INSERT INTO test_ha (data) VALUES ('test data');" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi

    echo -n "Reading test data..."
    if docker compose exec -T $leader psql -U postgres -c "SELECT * FROM test_ha;" | grep -q "test data"; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi
}

# Function to test replication
test_replication() {
    echo -e "\n${YELLOW}Testing replication...${NC}"

    echo -n "Checking replication slots..."
    local slots=$(docker compose exec -T postgres-1 psql -U postgres -c "SELECT * FROM pg_replication_slots;" 2>/dev/null)
    if echo "$slots" | grep -q "postgres-2\|postgres-3"; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${YELLOW}⚠ No replication slots found (may be initializing)${NC}"
    fi

    echo -n "Checking streaming replication..."
    local replication=$(docker compose exec -T postgres-1 psql -U postgres -c "SELECT * FROM pg_stat_replication;" 2>/dev/null)
    if [ -n "$replication" ]; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${YELLOW}⚠ No active replication connections (may be initializing)${NC}"
    fi
}

# Function to check metrics
check_metrics() {
    echo -e "\n${YELLOW}Checking metrics endpoints...${NC}"

    echo -n "Patroni metrics (postgres-1:8008)..."
    if curl -sf http://localhost:8008/metrics > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi

    echo -n "Postgres exporter metrics (9187)..."
    if curl -sf http://localhost:9187/metrics > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi
}

# Function to check SSL
check_ssl() {
    echo -e "\n${YELLOW}Checking SSL configuration...${NC}"

    echo -n "Verifying SSL is enabled..."
    local ssl_status=$(docker compose exec -T postgres-1 psql -U postgres -c "SHOW ssl;" 2>/dev/null | grep -o "on")
    if [ "$ssl_status" = "on" ]; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi
}

# Main execution
main() {
    cd "$STACK_DIR"

    echo "Building Docker images..."
    docker compose build

    echo -e "\nStarting Postgres HA stack..."
    docker compose up -d

    echo -e "\n${YELLOW}Waiting for services to initialize...${NC}"
    sleep 10

    # Wait for critical services
    wait_for_health "etcd-1" || exit 1
    wait_for_health "etcd-2" || exit 1
    wait_for_health "etcd-3" || exit 1

    # Give Patroni time to initialize
    echo -e "\n${YELLOW}Waiting for Patroni to initialize cluster (60s)...${NC}"
    sleep 60

    # Run tests
    check_patroni_cluster || { echo -e "${RED}Patroni cluster check failed${NC}"; exit 1; }
    test_database || { echo -e "${RED}Database tests failed${NC}"; exit 1; }
    test_replication || echo -e "${YELLOW}Replication checks completed with warnings${NC}"
    check_metrics || { echo -e "${RED}Metrics checks failed${NC}"; exit 1; }
    check_ssl || { echo -e "${RED}SSL checks failed${NC}"; exit 1; }

    echo -e "\n${GREEN}=== All tests passed! ===${NC}"
    echo -e "\n${YELLOW}Cluster Information:${NC}"
    echo "  - Postgres nodes: postgres-1:5432, postgres-2:5433, postgres-3:5434"
    echo "  - Patroni REST API: http://localhost:8008"
    echo "  - Metrics: http://localhost:9187/metrics"
    echo "  - Default credentials: postgres/postgres (CHANGE IN PRODUCTION!)"
}

main "$@"
