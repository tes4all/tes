# Implementation Plan

## Phase 1: Foundation (Valkey & API)
1.  **Valkey Service**: Add to `compose.yaml` with persistence.
2.  **API Service**: Build `images/edge-router-api` (FastAPI).
    *   Implement Pydantic models for Domain/Route.
    *   Implement Valkey connectivity.
3.  **Test**: Verify API writes keys to Valkey.

## Phase 2: Certificate Machinery
1.  **Cert Manager Image**:
    *   Install `lego`.
    *   Implement `manager.py`: Loop/Event logic.
    *   Implement "Import Legacy" flag.
2.  **Cert Syncer Image**:
    *   Implement `syncer.py`: Pub/Sub Listener.
    *   Implement `generator.py`: Create Traefik YAML from crt files.
3.  **Test**: Mock Lego (generate self-signed), verify Syncer creates file on volume.

## Phase 3: Traefik Integration
1.  **Update Compose**:
    *   Remove static config mounts.
    *   Add CLI flags:
        *   `--providers.redis.endpoints=valkey:6379`
        *   `--providers.file.directory=/certs`
        *   `--entrypoints.web.address=:80`
2.  **Secure Endpoints**:
    *   Bind ping/metrics to internal IPs only.

## Phase 4: CI/CD & CLI
1.  **Workflows**: Build/Push GitHub Actions.
2.  **Dependabot**: Config for Python/Docker.
3.  **TES CLI**: Plugin to run E2E tests.
