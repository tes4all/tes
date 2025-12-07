# Observability Golden Stack

Production-ready observability platform with Prometheus, Grafana, and Alertmanager.

## Architecture

- **Prometheus**: Metrics collection with Swarm service discovery
- **Grafana**: Visualization with pre-configured dashboards
- **Alertmanager**: Alert routing and notification
- **Node Exporter**: Host metrics (global deployment)

## Features

- Automatic service discovery via DNS
- Pre-configured dashboards
- Non-root execution
- Persistent storage
- Edge router integration

## Usage

### Create Secret
```bash
openssl rand -base64 24 | docker secret create grafana_admin_password -
```

### Deploy
```bash
docker stack deploy -c compose.yaml observability
```

### Access
- Grafana: https://grafana.example.com
- Prometheus: https://prometheus.example.com
- Alertmanager: https://alerts.example.com

## Dashboards

Pre-configured dashboards for:
- Traefik metrics
- PostgreSQL metrics
- Host system metrics

## Testing
```bash
cd tests && ./verify.sh
```
