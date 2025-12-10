# Zitadel Golden Stack

This stack provides a hardened, high-availability Zitadel Identity Provider.

## Features

- **Security Hardened**: Runs as non-root user, immutable config, and `cap_drop: [ALL]`.
- **High Availability**: Stateless architecture (requires HA Postgres).
- **Database**: Connects to the `postgres-ha` stack.
- **Observability**: Prometheus metrics exposed, Traefik integration pre-configured (HTTP/2).

## Configuration

The stack is configured via Environment Variables and a baked config file.

| Variable | Description | Default |
|----------|-------------|---------|
| `ZITADEL_MASTERKEY` | Master key for encryption (32 bytes) | `MasterkeyNeeds...` |
| `POSTGRES_PASSWORD` | Password for the Postgres admin | `postgres` |
| `ZITADEL_DB_PASSWORD` | Password for the Zitadel DB user | `zitadel_secret` |
| `DOMAIN` | Public domain | `auth.example.com` |

## Integration

### Include in Parent Project

Add this to your main `compose.yaml`:

```yaml
include:
  - path: ./stacks/zitadel/compose.yaml
```

## Usage

### Docker Swarm

1. Ensure `edge-router-net` and `postgres-ha` networks exist.
2. Deploy the stack:

```bash
docker stack deploy -c compose.yaml zitadel
```

### Docker Compose (Testing)

```bash
docker compose up -d
```

## Verification

Run the included verification script to build and test the stack (spins up a temporary Postgres):

```bash
./tests/verify.sh
```
