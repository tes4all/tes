# Edge Router Golden Stack

Production-ready edge routing stack with HAProxy (L4) and Traefik (L7).

## Architecture

- **HAProxy**: Global L4 load balancer with TCP passthrough
- **Traefik**: L7 reverse proxy with Docker Swarm integration
- **Observability**: Prometheus metrics on both services

## Security Features

- Non-root execution (UID 1000)
- Minimal capabilities (only NET_BIND_SERVICE)
- Baked configurations (no host mounts)
- Version pinning (no :latest tags)

## Usage

### Standalone Testing
```bash
docker compose up -d
```

### Swarm Deployment
```bash
docker stack deploy -c compose.yaml edge
```

### Include in Parent Stack
```yaml
include:
  - path: stacks/edge-router/compose.yaml
```

## Ports

- 80: HTTP ingress
- 443: HTTPS ingress
- 8404: HAProxy metrics
- 8082: Traefik metrics (internal)

## Verification

```bash
cd tests && ./verify.sh
```

## Integration

Services wanting to be routed through Traefik must:
1. Be on the `edge_network` overlay network
2. Have labels:
   ```yaml
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.myapp.rule=Host(`myapp.example.com`)"
     - "traefik.http.services.myapp.loadbalancer.server.port=8080"
   ```
