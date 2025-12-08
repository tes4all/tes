# Configuration

Vaultwarden configuration is primarily handled via Environment Variables to ensure immutability and compatibility with Docker Swarm Secrets (where supported by the application).

See `compose.yaml` and `Dockerfile` for available configuration options.

Key variables:
- `SIGNUPS_ALLOWED`: Controls user registration.
- `DOMAIN`: The public URL.
- `DATABASE_URL`: Connection string.
