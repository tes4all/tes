# Edge Router Requirements (2026)

## Goals
1.  **High Availability**: Zero-downtime reconfiguration for multiple Swarm nodes.
2.  **Dynamic Config**: API-driven addition of domains and routes without restarts.
3.  **Security**: Internal metrics/ping. Hardened images.
4.  **Modern Stack**: Use 2026 standards (Python 3.14, Valkey 8, Traefik v3+).

## Constraints
*   **Language**: Python 3.14 (Minimum) for all custom scripts.
*   **Database**: Valkey (Redis fork) v8+.
    *   Strategy: Single Node with Persistence (Acceptable 10s downtime for updates, Traffic unaffected).
*   **Traefik**:
    *   No baked configuration files (use CLI Args / Env Vars for portability).
    *   CE Edition (No Enterprise features).
*   **Certificates**:
    *   **"Real Sync"**: Use Pub/Sub (Event-driven), NO Polling.
    *   **Cleanup**: Automatic retention policy (delete old certs with grace period).
    *   **Golden Image**: Hardened Cert Manager image.
*   **Docker Swarm**:
    *   Certificates must be available on ALL nodes (overcoming `volume: driver: local`).
*   **Testing**:
    *   Full E2E test harness required.
    *   CI/CD integration.
