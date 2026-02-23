# Valkey HA Stack

This stack deploys a High Availability Valkey (Redis-compatible) cluster using Sentinel.

## Components

- **3 Valkey Nodes**: 1 Leader, 2 Replicas.
- **3 Sentinel Nodes**: Monitor the cluster and handle failover.
- **HAProxy**: Routes traffic to the current write-master.
- **Valkey Exporter**: Sidecar exporters for Prometheus metrics.

## Usage

1. Start the stack:
   ```bash
   docker compose up -d --build
   ```

2. Access the cluster:
   - **Write Operations (Master)**: `localhost:6379` (Routed by HAProxy)
   - **Read Operations**: Can be split, but currently `localhost:6379` directs to Master.

## Failover Testing

To test failover, pause or stop the current master (usually `valkey-1` initially):

```bash
docker compose stop valkey-1
```

Sentinel will detect the failure (within ~5-10 seconds) and promote `valkey-2` or `valkey-3` to master. HAProxy will detect the new master and reroute traffic.

## Configuration

Configuration files are baked into the image but copied to `/data` volume at runtime to allow Sentinel to rewrite them.
- `config/valkey.conf`: Base Valkey configuration.
- `config/sentinel.conf`: Base Sentinel configuration.
- `config/haproxy.cfg`: HAProxy configuration.
