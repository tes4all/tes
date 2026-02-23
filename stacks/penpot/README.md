# Penpot "Golden Stack"

This stack deploys [Penpot](https://penpot.app/), the open-source design and prototyping platform.

## Architecture

This deployment is designed to be **stateless** regarding the application containers. All state is offloaded to external services:

*   **Database:** Connects to an external PostgreSQL cluster (e.g., `stacks/postgres-ha`).
*   **Cache/Broker:** Connects to an external Valkey/Redis cluster (e.g., `stacks/valkey-ha`).
*   **Assets:** Configured to use S3 compatible storage (e.g. `stacks/rustfs` or MinIO), though local volume fallback is provided in the configuration.

## Components

*   `penpot-frontend`: The web interface.
*   `penpot-backend`: The core application logic.
*   `penpot-exporter`: Service for exporting designs to various formats (PDF, etc.).

## Configuration

Configuration is handled via `config/config.env`.

### Prerequisites

Ensure the following networks exist or update `compose.yaml` to match your infrastructure:
*   `postgres_network` (for database access)
*   `valkey_network` (for redis access)

### Environment Variables

Key variables in `config/config.env`:

*   `PENPOT_PUBLIC_URI`: The URL where users access Penpot.
*   `PENPOT_DATABASE_URI`: Connection string for PostgreSQL.
*   `PENPOT_REDIS_URI`: Connection string for Redis/Valkey.

## Storage Configuration (S3)

To use S3 compatible storage (like MinIO or RustFS):
1.  Uncomment the S3 variables in `config/config.env`.
2.  Set `PENPOT_OBJECTS_STORAGE_BACKEND=s3`.
3.  Ensure the `storage-net` in `compose.yaml` is correctly pointing to your storage network (default: `rustfs_network`).
4.  If using `rustfs` internally, ensure `PENPOT_OBJECTS_STORAGE_S3_ENDPOINT` is reachable by the backend.

## Deployment

1.  Start the external dependencies (Postgres, Valkey, S3).
2.  Start the Penpot stack:

```bash
docker compose up -d
```

3.  Access Penpot at `http://localhost:9001`.

## Initial Setup

On first run, Penpot will initialize its database schema automatically if the database is empty. You can then create the first admin user via the interface or CLI if supported.
