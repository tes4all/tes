# Authentik Golden Stack

This stack provides a hardened, high-availability Authentik Identity Provider.

## Features

- **Security Hardened**: Runs as non-root user (uid 1000), immutable config, and `cap_drop: [ALL]`.
- **High Availability**: Stateless Server and Worker architecture, ready for scaling.
- **Database**: Connects to the `postgres-ha` stack.
- **Cache**: Includes a hardened Valkey instance for caching and message brokering.
- **Observability**: Prometheus metrics exposed on port 9300, Traefik integration pre-configured.

## Configuration

The stack is configured via Environment Variables and a baked config file.

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTHENTIK_SECRET_KEY` | Secret key for signing | `generate_me...` |
| `POSTGRES_PASSWORD` | Password for the Postgres user | `postgres` |
| `AUTHENTIK_POSTGRESQL__HOST` | Hostname of the Postgres DB | `postgres-ha` |

## Integration

### Include in Parent Project

Add this to your main `compose.yaml`:

```yaml
include:
  - path: ./stacks/authentik/compose.yaml
```

## Usage

### Docker Swarm

1. Ensure `edge-router-net` and `postgres-ha` networks exist.
2. Deploy the stack:

```bash
docker stack deploy -c compose.yaml authentik
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
