# Postgres HA Golden Stack

Production-ready PostgreSQL High Availability cluster with Patroni.

## Architecture

- **Patroni**: HA orchestration with automatic failover
- **etcd**: Distributed configuration store
- **HAProxy**: Connection pooling and read/write split
- **Postgres Exporter**: Prometheus metrics

## Features

- 3-node Patroni cluster
- Automatic failover
- Non-root execution
- Health checks
- Prometheus observability

## Usage

### Prerequisites
Create secrets:
```bash
echo "your-secure-password" | docker secret create postgres_password -
echo "replication-password" | docker secret create replication_password -
```

### Swarm Deployment
```bash
docker stack deploy -c compose.yaml postgres-ha
```

### Testing
```bash
cd tests && ./verify.sh
```

## Ports

- 5432: Primary write connection
- 5433: Read replica connection
- 8008: Patroni REST API
- 9187: Postgres metrics

## Connection String

```
postgresql://postgres:password@haproxy:5432/mydb
```
