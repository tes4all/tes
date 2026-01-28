# Testing Strategy

## Framework
*   **Core**: `pytest`
*   **Orchestration**: `python_on_whales` (Docker Client wrapper).
*   **Location**: `stacks/edge-router/tests/e2e/`

## Test Scopes

### 1. Unit Tests (Pre-Build)
*   **Target**: Python logic inside `images/*/`.
*   **Mock**: `redis` library, `lego` subprocess.
*   **Assert**: Logic correctness (Retention policy, YAML generation).

### 2. Integration Tests (Service Level)
*   **Target**: Running containers in test harness.
*   **Tests**:
    *   `test_api_valkey_write`: API call -> Check Valkey key.
    *   `test_syncer_pubsub`: Publish to Valkey manually -> Check container file system.

### 3. End-to-End (E2E)
*   **Env**: Ephemeral Docker Swarm (or local Docker).
*   **Flow**:
    1.  `docker stack deploy ...`
    2.  `client.post("/domains", json={"domain": "test.local"})`
    3.  **Wait** for Pub/Sub.
    4.  `client.get("https://test.local")` (Expect 404 from Traefik, but Valid TLS).
*   **Mocking ACME**:
    *   For E2E, the Cert Manager should have a `--test-mode` flag to generate Self-Signed certs locally instead of calling Let's Encrypt servers. This prevents rate limits.

## Scripts
*   `tests/run_unit.sh`
*   `tests/run_e2e.sh`
