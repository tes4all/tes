# Authentik Golden Stack

Production-ready Authentik SSO platform.

## Architecture

- **Authentik Server**: Identity provider (2 replicas)
- **Authentik Worker**: Background tasks (2 replicas)
- **Redis**: Session store
- **Integration**: postgres-ha backend, edge-router ingress

## Prerequisites

1. postgres-ha stack running
2. edge-router stack running
3. Networks created

## Usage

### Create Secrets
```bash
openssl rand -base64 50 | docker secret create authentik_secret_key -
echo "your-postgres-password" | docker secret create postgres_password -
```

### Deploy
```bash
docker stack deploy -c compose.yaml authentik
```

### Access
https://sso.example.com

## Initial Setup

Default credentials: `akadmin` / Password set during first login
