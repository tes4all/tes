# Zitadel Golden Stack

Production-ready Zitadel identity platform.

## Architecture

- **Zitadel**: Modern identity management
- **Integration**: postgres-ha backend, edge-router ingress
- **Stateless**: Horizontally scalable

## Prerequisites

1. postgres-ha stack running
2. edge-router stack running
3. Networks created:
   ```bash
   docker network create -d overlay edge_network
   docker network create -d overlay postgres_network
   ```

## Usage

### Create Secret
```bash
openssl rand -base64 32 | docker secret create zitadel_masterkey -
```

### Deploy
```bash
docker stack deploy -c compose.yaml zitadel
```

### Access
https://auth.example.com

## Configuration

Edit `config/zitadel.yaml` and rebuild the stack.
