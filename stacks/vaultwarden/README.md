# Vaultwarden Golden Stack

This stack provides a hardened, high-availability Vaultwarden (Bitwarden compatible) server.

## Features

- **Security Hardened**: Runs as non-root user, read-only root filesystem (via `cap_drop`), and secure defaults.
- **High Availability**: Designed for Docker Swarm with healthchecks and restart policies.
- **Database**: Connects to the `postgres-ha` stack for robust data persistence.
- **Edge Router**: Pre-configured labels for Traefik integration (including WebSocket support).

## Configuration

The stack is configured via Environment Variables.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Connection string for Postgres | `postgresql://...` |
| `DOMAIN` | The public domain for the vault | `https://vault.example.com` |
| `SIGNUPS_ALLOWED` | Allow new user signups | `false` |
| `WEBSOCKET_ENABLED` | Enable WebSocket notifications | `true` |

## Usage

### Docker Swarm

1. Ensure `edge-router-net` and `postgres-ha` networks exist.
2. Create secrets `db_password` and `admin_token`.
3. Deploy the stack:

```bash
docker stack deploy -c compose.yaml vaultwarden
```

### Docker Compose (Testing)

```bash
export DATABASE_URL="sqlite:///data/db.sqlite3"
docker compose up -d
```

## Verification

Run the included verification script to build and test the stack in isolation (using SQLite):

```bash
./tests/verify.sh
```
