# Vaultwarden Golden Stack

This stack provides a hardened, high-availability Vaultwarden (Bitwarden compatible) server.

## Features

- **Security Hardened**: Runs as non-root user, read-only root filesystem (via `cap_drop`), and secure defaults.
- **High Availability**: Designed for Docker Swarm with healthchecks and restart policies.
- **Database**: Includes an internal PostgreSQL server by default, but can connect to the `postgres-ha` stack for robust data persistence.
- **Edge Router**: Pre-configured labels for Traefik integration (including WebSocket support).

## Configuration

The stack is configured via Environment Variables.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Connection string for Postgres | Internal DB |
| `DOMAIN` | The public domain for the vault | `http://localhost:8080` |
| `SIGNUPS_ALLOWED` | Allow new user signups | `false` |
| `WEBSOCKET_ENABLED` | Enable WebSocket notifications | `true` |

## Integration

### Include in Parent Project

Add this to your main `compose.yaml`:

```yaml
include:
  - path: ./stacks/vaultwarden/compose.yaml
```

## Usage

### Standalone (Default)

The stack runs with an internal PostgreSQL database and exposes port 8080 by default.

```bash
docker compose up -d
```

### External Database & Edge Router

To use an external database (like `postgres-ha`) or Edge Router:

1. Uncomment the external networks in `compose.yaml`.
2. Set `DATABASE_URL` to point to your external database.
3. Deploy the stack.

### Docker Swarm

1. Ensure `edge-router-net` and `postgres-ha` networks exist (if using external).
2. Create secrets `db_password` and `admin_token`.
3. Deploy the stack:

```bash
docker stack deploy -c compose.yaml vaultwarden
```


## Verification

Run the included verification script to build and test the stack in isolation (using SQLite):

```bash
./tests/verify.sh
```
