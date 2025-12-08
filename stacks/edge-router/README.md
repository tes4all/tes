# Edge Router Stack

Production-hardened edge routing with HAProxy (L4) and Traefik (L7).

## Architecture

```
Internet → HAProxy (L4/TCP) → Traefik (L7/HTTP) → Backend Services
              ↓                    ↓
         :8405/metrics        :8083/metrics
```

## Security Features

- **Non-root execution**: Both services run as UID 1000
- **Read-only filesystem**: Containers use `read_only: true`
- **Dropped capabilities**: Only `NET_BIND_SERVICE` retained
- **Baked configurations**: No bind-mounted config files
- **Security headers**: Traefik applies HSTS, XSS protection

## Quick Start

```bash
# Build and test
cd stacks/edge-router
./tests/verify.sh

# Deploy to Swarm
docker stack deploy -c compose.yaml edge-router
```

## Exposed Ports

| Port | Service | Purpose |
|------|---------|---------|
| 80 | HAProxy | HTTP ingress |
| 443 | HAProxy | HTTPS ingress |
| 8405 | HAProxy | Prometheus metrics |
| 8083 | Traefik | Prometheus metrics |

## Prometheus Integration

Add to your Prometheus config:

```yaml
scrape_configs:
  - job_name: 'haproxy'
    static_configs:
      - targets: ['haproxy:8405']

  - job_name: 'traefik'
    static_configs:
      - targets: ['traefik:8083']
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ACME_EMAIL` | `admin@example.com` | Let's Encrypt registration email |

## Service Labels for Traefik

Expose your services to Traefik:

```yaml
services:
  myapp:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`app.example.com`)"
      - "traefik.http.routers.myapp.entrypoints=websecure"
      - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
      - "traefik.http.services.myapp.loadbalancer.server.port=8080"
```
