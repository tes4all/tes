# RustFS

RustFS is a high-performance, distributed object storage server, compatible with Amazon S3.

## Configuration

This stack deploys a **Single Node** RustFS instance, optimized for reliability and security.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RUSTFS_ACCESS_KEY` | Access Key ID for S3 API (Change in production!) | `rustfsadmin` |
| `RUSTFS_SECRET_KEY` | Secret Access Key for S3 API (Change in production!) | `rustfsadmin` |
| `RUSTFS_VOLUMES` | Directory for object storage data | `/data/rustfs{0..3}` (4 volumes) |
| `RUSTFS_ADDRESS` | S3 API address | `0.0.0.0:9000` |
| `RUSTFS_CONSOLE_ADDRESS` | Console UI address | `0.0.0.0:9001` |
| `RUSTFS_CONSOLE_ENABLE` | Enable web console | `true` |

### Security Note

- The container runs as non-root user `10001:10001` with `read_only` filesystem and dropped capabilities (`cap_drop: ALL`).
- Ensure `RUSTFS_ACCESS_KEY` and `RUSTFS_SECRET_KEY` are changed in production environments.

### Data Persistency & Permissions

This stack uses 4 named volumes `rustfs_data_{0..3}` mounted to `/data/rustfs{0..3}`.
An init container (`rustfs-init`) runs at startup to ensure these volumes are writable by the non-root `rustfs` user (UID 10001).

### Distributed Mode

Distributed mode (High Availability) is currently under active development ("🚧 Under Testing") by the RustFS team.
This stack provides a robust Single Node setup. Once distributed mode is stable, this configuration can be extended to support multiple nodes/peers.

### Ports

- **9000**: S3 API
- **9001**: Console / Web UI

## Usage

```bash
docker compose up -d
```

Visit the console at `http://localhost:9001`.
