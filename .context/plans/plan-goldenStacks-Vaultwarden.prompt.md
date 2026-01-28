## Plan: Golden Stacks Implementation (Swarm & Stack Focused)

I will design production-ready "Golden Stacks" optimized for Docker Swarm (via `docker stack deploy`) but compatible with Docker Compose for testing. Each stack will be self-contained in `stacks/<stack-name>` with baked configurations, non-root users, and observability built-in.

### Steps
**Vaultwarden (`stacks/vaultwarden`)**
    *   **Hardening**: Disabled signups (configurable), WebSocket support via Edge Router.
    *   **Backend**: Connects to `postgres-ha` if needed

### Further Considerations
1.  **Swarm vs. Compose**: `compose.yaml` will use Swarm-specific keys (`deploy`, `secrets`) which Compose ignores or handles gracefully.
2.  **Secrets Management**: While configs are baked, sensitive data (DB passwords, SSL certs) should ideally use Docker Secrets. I will implement the "Golden" templates to expect Secrets but provide dev defaults.
3.  **Verification**: `tests/verify.sh` will primarily use `docker compose` for functional testing (health, config validity). Full HA failover testing requires a running Swarm.
