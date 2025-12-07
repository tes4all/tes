# Postgres HA Golden Stack

Production-ready PostgreSQL High Availability cluster using Patroni, etcd, and pgBackRest. This stack implements true HA with automatic failover, streaming replication, and automated backups.

## Architecture

### Components

- **PostgreSQL 16.1**: Primary database engine
- **Patroni 3.2.0**: HA orchestration and automatic failover
- **etcd 3.5.11**: Distributed consensus for cluster coordination (3-node cluster)
- **pgBackRest**: Enterprise-grade backup and restore solution
- **postgres_exporter**: Prometheus metrics exporter

### Topology

```
┌─────────────────────────────────────────────────────────┐
│                    etcd Cluster (3 nodes)               │
│  etcd-1:2379  │  etcd-2:2379  │  etcd-3:2379           │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼─────────┐         ┌──────────▼────────┐
│   Patroni Node 1  │         │  Patroni Node 2   │
│   postgres-1:5432 │◄────────┤  postgres-2:5433  │
│   (Primary/Leader)│ Repl.   │   (Replica)       │
└───────────────────┘         └───────────────────┘
          │                               │
          │      ┌────────────────────────┘
          │      │
┌─────────▼──────▼─────┐
│   Patroni Node 3     │
│   postgres-3:5434    │
│   (Replica)          │
└──────────────────────┘
          │
┌─────────▼─────────┐
│   pgBackRest      │
│   (Backups)       │
└───────────────────┘
```

## Features

### Security (Following Golden Rules)

- ✅ **Non-root execution**: All containers run as unprivileged users (UID 1000/1001)
- ✅ **Baked configurations**: All configs copied into images at build time
- ✅ **SSL/TLS encryption**: Postgres enforces SSL for all connections
- ✅ **Version pinning**: No `:latest` tags used
- ✅ **Capability dropping**: Minimal Linux capabilities (CAP_DROP: ALL)
- ✅ **Self-signed certificates**: Included for development (use proper certs in production)

### High Availability

- **Automatic failover**: Patroni detects failures and promotes replicas
- **Streaming replication**: Real-time data synchronization across nodes
- **Split-brain protection**: etcd-based consensus prevents data corruption
- **Health checks**: Built-in monitoring for all services
- **Quorum-based**: 3-node etcd cluster ensures availability

### Observability

- **Prometheus labels**: All services tagged for automatic discovery
- **Metrics endpoints**:
  - Patroni: `http://localhost:8008/metrics`
  - Postgres Exporter: `http://localhost:9187/metrics`
  - etcd: Built-in metrics available
- **Health checks**: HTTP-based health endpoints for monitoring
- **Structured logging**: All components log to stdout/stderr

### Backups

- **Automated incremental backups**: pgBackRest runs hourly
- **Point-in-time recovery (PITR)**: Full WAL archiving enabled
- **Compression**: LZ4 compression for efficient storage
- **Retention policies**: Configurable backup retention

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 20GB+ disk space

### Deploy the Stack

#### Docker Compose (Development/Testing)

```bash
# Navigate to the stack directory
cd stacks/postgres-ha

# Build and start all services
docker compose up -d

# Wait for cluster initialization (takes 60-90 seconds)
docker compose logs -f postgres-1

# Check cluster status
curl http://localhost:8008/cluster
```

#### Docker Swarm (Production)

For production deployments with Docker Swarm:

```bash
# 1. Change network driver in compose.yaml from 'bridge' to 'overlay'
sed -i 's/driver: bridge/driver: overlay/' compose.yaml

# 2. Initialize swarm (if not already)
docker swarm init

# 3. Deploy as a stack
docker stack deploy -c compose.yaml postgres-ha

# 4. Check service status
docker stack services postgres-ha
```

**Note**: The compose.yaml uses `bridge` driver by default for standalone Docker Compose. For Docker Swarm deployments, change to `overlay` driver for multi-host networking.

### Verify Installation

Run the automated verification script:

```bash
./tests/verify.sh
```

This script will:
- Start the entire stack
- Wait for services to become healthy
- Test database connectivity
- Verify replication is working
- Check metrics endpoints
- Validate SSL configuration
- Clean up after testing

## Usage

### Connect to Database

```bash
# Connect to the primary node
docker compose exec postgres-1 psql -U postgres

# Or from your host (if you have psql client)
psql -h localhost -p 5432 -U postgres
```

**Default credentials** (⚠️ **CHANGE IN PRODUCTION!**):
- Username: `postgres`
- Password: `postgres`
- Admin user: `admin` / `admin`
- Replication user: `replicator` / `replicator`

### Monitor Cluster Status

```bash
# Patroni REST API
curl http://localhost:8008/cluster | jq

# Check which node is the leader
curl http://localhost:8008/leader

# Check replication lag
docker compose exec postgres-1 psql -U postgres -c "SELECT * FROM pg_stat_replication;"
```

### Test Failover

```bash
# Stop the primary node to trigger failover
docker compose stop postgres-1

# Watch Patroni elect a new leader (takes ~30 seconds)
watch -n 1 'curl -s http://localhost:8009/cluster | jq'

# Restart the old primary (it becomes a replica)
docker compose start postgres-1
```

### Perform Backup

```bash
# Manual full backup
docker compose exec pgbackrest pgbackrest --stanza=postgres-cluster backup --type=full

# List available backups
docker compose exec pgbackrest pgbackrest info

# Restore from backup (requires cluster to be stopped)
docker compose exec pgbackrest pgbackrest --stanza=postgres-cluster restore
```

### View Metrics

```bash
# Patroni metrics
curl http://localhost:8008/metrics

# Postgres metrics
curl http://localhost:9187/metrics

# etcd health
docker compose exec etcd-1 etcdctl endpoint health
```

## Integration

### Include in Parent Project

Add this to your main `compose.yaml`:

```yaml
include:
  - path: ./stacks/postgres-ha/compose.yaml

services:
  my-app:
    image: my-app:latest
    networks:
      - postgres-ha
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres-1:5432/mydb?sslmode=require
```

### Application Connection String

For applications that need to connect:

```
# Primary (read-write)
postgresql://postgres:postgres@postgres-1:5432/postgres?sslmode=require

# Replicas (read-only) - use for load balancing reads
postgresql://postgres:postgres@postgres-2:5433/postgres?sslmode=require
postgresql://postgres:postgres@postgres-3:5434/postgres?sslmode=require
```

### HAProxy for Load Balancing (Optional)

For production, consider adding HAProxy to load balance connections:

```yaml
  haproxy:
    image: haproxy:2.9-alpine
    ports:
      - "5000:5000"  # Read-write port
      - "5001:5001"  # Read-only port
    # Configuration to route writes to primary and reads to replicas
```

## Configuration

### Environment Variables

Key environment variables (can be overridden):

- `PATRONI_SCOPE`: Cluster name (default: `postgres-cluster`)
- `PATRONI_NAME`: Node name (auto-set per node)
- `POSTGRES_PASSWORD`: Superuser password (⚠️ change in production)

### Tuning

Configuration files in `config/`:

- `patroni.yml`: Patroni and cluster settings
- `postgres.conf`: PostgreSQL server configuration
- `pg_hba.conf`: Client authentication rules
- `pgbackrest.conf`: Backup configuration

To modify, edit the files and rebuild:

```bash
docker compose build
docker compose up -d
```

## Production Checklist

Before deploying to production:

- [ ] **Change all default passwords** in `config/patroni.yml` and use Docker Secrets
- [ ] **Replace self-signed SSL certificates** with proper CA-signed certs
- [ ] **Configure Docker Secrets** for all sensitive data (passwords, connection strings)
- [ ] **For Docker Swarm**: Change network driver to `overlay` in compose.yaml
- [ ] **Set resource limits** appropriate for your workload
- [ ] **Configure backup retention** policies in `pgbackrest.conf`
- [ ] **Replace simple backup scheduler** with cron or proper job scheduler
- [ ] **Enable monitoring** (Prometheus/Grafana)
- [ ] **Test failover scenarios** thoroughly
- [ ] **Document recovery procedures**
- [ ] **Set up alerting** for cluster health
- [ ] **Configure log aggregation**
- [ ] **Review security groups** and network policies

## Troubleshooting

### Cluster won't initialize

```bash
# Check etcd cluster health
docker compose exec etcd-1 etcdctl endpoint health --cluster

# Check Patroni logs
docker compose logs postgres-1

# Reset and try again
docker compose down -v
docker compose up -d
```

### Replication lag

```bash
# Check replication status
docker compose exec postgres-1 psql -U postgres -c \
  "SELECT client_addr, state, sync_state, replay_lag FROM pg_stat_replication;"

# Check Patroni lag info
curl http://localhost:8008/cluster | jq '.members[].lag'
```

### Connection refused

```bash
# Verify services are running
docker compose ps

# Check which node is the primary
curl http://localhost:8008/leader

# Test connectivity
docker compose exec postgres-1 pg_isready
```

### SSL errors

Ensure your client supports SSL and uses `sslmode=require` or `sslmode=verify-full` in connection string.

## Maintenance

### Upgrade PostgreSQL Version

1. Update version in `Dockerfile.patroni` (e.g., `postgres:16.2-alpine`)
2. Rebuild images: `docker compose build`
3. Rolling update:
   ```bash
   docker compose up -d postgres-3
   # Wait for replica to catch up
   docker compose up -d postgres-2
   # Wait for replica to catch up
   docker compose up -d postgres-1
   ```

### Scale Replicas

Add more replica nodes in `compose.yaml` following the pattern of `postgres-2` and `postgres-3`.

## Performance Tips

- **Connection pooling**: Use PgBouncer for application connection pooling
- **Read scaling**: Direct read-only queries to replica nodes
- **Monitoring**: Set up alerts for replication lag and disk space
- **Backups**: Schedule full backups during off-peak hours
- **Tuning**: Adjust `shared_buffers`, `work_mem` based on workload

## Security Considerations

- Default passwords are for **development only**
- SSL certificates are **self-signed for development**
- In production:
  - Use Docker Secrets for passwords
  - Mount proper SSL certificates
  - Enable firewall rules
  - Use network policies
  - Regular security updates

## Architecture Decisions

### Why Patroni?

- Industry-standard for Postgres HA
- Handles automatic failover reliably
- Integrates with major DCS systems (etcd, Consul, ZooKeeper)
- Active community and good documentation

### Why etcd?

- Lightweight and reliable consensus
- Better suited for containerized environments than ZooKeeper
- Used by Kubernetes (proven at scale)

### Why pgBackRest?

- Enterprise features (incremental, differential backups)
- Point-in-time recovery support
- Better performance than pg_basebackup
- Compression and encryption built-in

## License

This stack configuration is provided as-is for use in the TES project.

## Support

For issues or questions:
- Check the [troubleshooting section](#troubleshooting)
- Review Patroni logs: `docker compose logs postgres-1`
- Verify etcd cluster: `docker compose exec etcd-1 etcdctl endpoint status --cluster`
