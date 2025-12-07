# Vaultwarden Golden Stack

Production-ready Vaultwarden (Bitwarden compatible) password manager.

## Architecture

- **Vaultwarden**: Lightweight Bitwarden server
- **PostgreSQL Backend**: Uses postgres-ha stack
- **WebSocket Support**: Real-time sync via edge router
- **Hardened**: Signups disabled by default

## Features

- PostgreSQL backend (no SQLite)
- WebSocket notifications
- Signups disabled (invite-only)
- Edge router integration
- Stateless (horizontally scalable)

## Prerequisites

1. postgres-ha stack running
2. edge-router stack running
3. Networks created

## Usage

### Create Secrets
```bash
openssl rand -base64 32 | docker secret create vaultwarden_admin_token -
echo "your-postgres-password" | docker secret create postgres_password -
```

### Deploy
```bash
docker stack deploy -c compose.yaml vaultwarden
```

### Access
- Web Vault: https://vault.example.com
- Admin Panel: https://vault.example.com/admin

## Configuration

Edit environment variables in compose.yaml:
- `SIGNUPS_ALLOWED`: Enable/disable public signups
- `INVITATIONS_ALLOWED`: Allow user invitations
- `DOMAIN`: Your public domain

## Testing
```bash
cd tests && ./verify.sh
```

## Backup

Data is stored in PostgreSQL. Use postgres-ha's pgbackrest for backups.
