# Zitadel Golden Stack

This stack provides a complete Zitadel deployment including:
- Zitadel (Main Service)
- Zitadel Login V2
- PostgreSQL Database

## usage

To use this stack, include it in your swarm stack definition or deploy it directly setting the necessary environment variables.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ZITADEL_HOSTNAME` | The hostname for Zitadel | `auth.example.com` |
| `ZITADEL_MASTERKEY` | Masterkey (32 chars) | `MasterkeyNeedsToHave32Characters` |
| `POSTGRES_ADMIN_PASSWORD` | Postgres admin password | `postgres` |
| `ZITADEL_DB_PASSWORD` | Zitadel DB user password | `zitadel` |
| `ZITADEL_ORG_NAME` | Initial Organization Name | `MyOrg` |
| `ZITADEL_ADMIN_USERNAME` | Initial Admin Username | `zitadel-admin` |
| `ZITADEL_ADMIN_PASSWORD` | Initial Admin Password | `Password1!` |
| `TRAEFIK_NETWORK` | The external traefik network | `edge-external` |

## Notes

- This stack includes a PostgreSQL instance. For production, consider using an external database or HA setup if required.
- The `login` service provides the V2 Login UI.
