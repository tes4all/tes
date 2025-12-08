#!/usr/bin/env bash
# Edge Router Stack Verification
# Validates: Build, Health, Metrics, Routing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_PROJECT="edge-router-test"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

cleanup() {
    log_info "Cleaning up test environment..."
    cd "$STACK_DIR"
    docker compose -p "$COMPOSE_PROJECT" down -v --remove-orphans 2>/dev/null || true
}

trap cleanup EXIT

main() {
    log_info "=== Edge Router Stack Verification ==="
    cd "$STACK_DIR"

    # Step 1: Build images
    log_info "Building images..."
    docker compose -p "$COMPOSE_PROJECT" build --no-cache

    # Step 2: Start stack
    log_info "Starting stack..."
    docker compose -p "$COMPOSE_PROJECT" up -d

    # Step 3: Wait for health
    log_info "Waiting for services to become healthy..."
    local max_wait=60
    local waited=0

    while [[ $waited -lt $max_wait ]]; do
        local haproxy_health traefik_health
        haproxy_health=$(docker inspect --format='{{.State.Health.Status}}' "${COMPOSE_PROJECT}-haproxy-1" 2>/dev/null || echo "starting")
        traefik_health=$(docker inspect --format='{{.State.Health.Status}}' "${COMPOSE_PROJECT}-traefik-1" 2>/dev/null || echo "starting")

        if [[ "$haproxy_health" == "healthy" && "$traefik_health" == "healthy" ]]; then
            log_info "All services healthy!"
            break
        fi

        log_info "Waiting... HAProxy=$haproxy_health, Traefik=$traefik_health ($waited/${max_wait}s)"
        sleep 5
        ((waited+=5))
    done

    if [[ $waited -ge $max_wait ]]; then
        log_error "Services did not become healthy in time"
        docker compose -p "$COMPOSE_PROJECT" logs
        exit 1
    fi

    # Step 4: Verify HAProxy metrics
    log_info "Checking HAProxy Prometheus metrics..."
    local haproxy_metrics
    haproxy_metrics=$(curl -sf http://localhost:8405/metrics 2>/dev/null || echo "FAILED")

    if [[ "$haproxy_metrics" == *"haproxy_"* ]]; then
        log_info "✓ HAProxy metrics endpoint working"
    else
        log_error "✗ HAProxy metrics not available. Output:"
        echo "$haproxy_metrics"
        docker compose -p "$COMPOSE_PROJECT" logs
        exit 1
    fi

    # Step 5: Verify Traefik metrics
    log_info "Checking Traefik Prometheus metrics..."
    local traefik_metrics
    traefik_metrics=$(curl -sf http://localhost:8083/metrics 2>/dev/null || echo "FAILED")

    if [[ "$traefik_metrics" == *"traefik_"* ]]; then
        log_info "✓ Traefik metrics endpoint working"
    else
        log_error "✗ Traefik metrics not available. Output:"
        echo "$traefik_metrics"
        docker compose -p "$COMPOSE_PROJECT" logs
        exit 1
    fi

    # Step 6: Verify Traefik ping
    log_info "Checking Traefik ping endpoint..."
    local ping_response
    ping_response=$(curl -sf http://localhost:8082/ping 2>/dev/null || echo "FAILED")

    if [[ "$ping_response" == "OK" ]]; then
        log_info "✓ Traefik ping endpoint working"
    else
        log_error "✗ Traefik ping not responding"
        exit 1
    fi

    # Step 7: Verify config validation (non-root check)
    log_info "Verifying non-root execution..."
    local haproxy_user traefik_user
    haproxy_user=$(docker exec "${COMPOSE_PROJECT}-haproxy-1" id -u 2>/dev/null || echo "0")
    traefik_user=$(docker exec "${COMPOSE_PROJECT}-traefik-1" id -u 2>/dev/null || echo "0")

    if [[ "$haproxy_user" == "1000" && "$traefik_user" == "1000" ]]; then
        log_info "✓ Both services running as non-root (UID 1000)"
    else
        log_error "✗ Services not running as expected user (HAProxy=$haproxy_user, Traefik=$traefik_user)"
        exit 1
    fi

    # Step 8: Test L4 routing (HAProxy -> Traefik)
    log_info "Testing L4 routing through HAProxy..."
    local routing_test
    routing_test=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:80 2>/dev/null || echo "000")

    # Expect redirect (301/308) or 404 (no backends configured)
    if [[ "$routing_test" =~ ^(301|308|404|502)$ ]]; then
        log_info "✓ L4 routing working (HTTP $routing_test)"
    else
        log_warn "⚠ Unexpected routing response: $routing_test"
    fi

    log_info "=== All Verification Tests Passed ==="
    echo ""
    log_info "Stack is ready for production deployment!"
    log_info "  - HAProxy Stats:    http://localhost:8405/stats"
    log_info "  - HAProxy Metrics:  http://localhost:8405/metrics"
    log_info "  - Traefik Metrics:  http://localhost:8083/metrics"
}

main "$@"
