# syntax=docker/dockerfile:1
FROM vaultwarden/server:1.35.2-alpine

# Security: Create non-root user
# The official image runs as root by default. We create a user to run the service.
# Note: We use numeric ID 1000 for better compatibility.
# Alpine uses adduser/addgroup instead of useradd
RUN addgroup -g 1000 vaultwarden && \
    adduser -u 1000 -G vaultwarden -h /data -s /bin/sh -D vaultwarden

# Prepare data directory with correct permissions
RUN mkdir -p /data && chown -R vaultwarden:vaultwarden /data

# Switch to non-root user
USER 1000

# Hardening: Set default environment variables
# These are baked into the image but can be overridden
ENV SIGNUPS_ALLOWED=false
# check=skip=SecretsUsedInArgOrEnv
ENV SHOW_PASSWORD_HINT=false
ENV WEBSOCKET_ENABLED=true
ENV ROCKET_WORKERS=10
# Use non-privileged port for non-root user
ENV ROCKET_PORT=8080

# Expose ports (8080 for HTTP, 3012 for WebSocket)
EXPOSE 8080
EXPOSE 3012

# Define volume for persistence
VOLUME ["/data"]

# The base image CMD is likely correct, but we ensure we run as the user.
# We don't override CMD unless necessary, but we must ensure the binary can read /data
