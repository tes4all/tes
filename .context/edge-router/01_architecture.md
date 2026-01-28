# Edge Router Architecture

## Components

### 1. State Store (`valkey`)
*   **Image**: `valkey/valkey:8.0.1-alpine`
*   **Role**: Central Source of Truth.
*   **Data Structures**:
    *   `Set: target_domains`: List of domains we want certs for.
    *   `Hash: cert:{domain}`: The actual PEM data (Certificate + Key).
    *   `Hash: traefik:{...}`: Dynamic routing rules (Traefik Redis Provider).
*   **Channels (Pub/Sub)**:
    *   `events/certs_updated`: Payload `{ "domain": "example.com", "action": "upsert" }`

### 2. Edge API (`edge-router-api`)
*   **Image**: Custom (Python 3.14 + FastAPI)
*   **Role**: Control Plane.
*   **Endpoints**:
    *   `POST /domains`: Add to `target_domains`. Trigger `cert-manager`.
    *   `POST /routes`: Add Traefik Router Config to Valkey.

### 3. Cert Manager (`cert-manager`)
*   **Image**: Custom (Python 3.14 + Lego)
*   **Role**: Controller / Worker.
*   **Logic**:
    1.  Watches `target_domains`.
    2.  Executes `lego` (DNS-01 Challenge).
    3.  Writes output to Valkey `cert:{domain}`.
    4.  Publishes to `events/certs_updated`.
    5.  **Retention**: Prunes `cert:*` keys not in `target_domains` > 7 days.

### 4. Cert Syncer (`cert-syncer`)
*   **Image**: Custom (Python 3.14 + Redis-Py)
*   **Deploy Mode**: `global` (Runs on EVERY Swarm node).
*   **Role**: File Materialization.
*   **Logic**:
    1.  **Bootstrap**: On start, download all certs from Valkey to `/certs` volume.
    2.  **Listen**: Subscribe to `events/certs_updated`.
    3.  **Sync**: On event, download specific cert (or full sync).
    4.  **Generate**: Update `/certs/certificates.yml` for Traefik `file` provider.

### 5. Traefik (`traefik`)
*   **Image**: `traefik:v3.6`
*   **Config**: CLI Arguments in `compose.yaml`.
*   **Providers**:
    *   `--providers.redis`: Reads routing tables.
    *   `--providers.file`: Reads `/certs/certificates.yml`.

## Data Flow Diagram
User -> API -> Valkey (Add Domain)
             |
             v
       Cert Manager (Polls/Event) -> DNS-01 -> Valkey (Write Cert) -> PUB "Update"
                                                                      |
                                                                      v
                                                                 Cert Syncer (All Nodes)
                                                                 -> Download Cert
                                                                 -> Write to /certs/file.crt
                                                                      |
                                                                      v
                                                                   Traefik (File Watch)
