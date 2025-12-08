FROM vaultwarden/server:1.32.0

# Security: Create non-root user
# The official image runs as root by default. We create a user to run the service.
# Note: We use numeric ID 1000 for better compatibility.
RUN useradd -m -u 1000 -s /bin/bash vaultwarden

# Prepare data directory with correct permissions
RUN mkdir -p /data && chown -R vaultwarden:vaultwarden /data

# Switch to non-root user
USER 1000

# Hardening: Set default environment variables
# These are baked into the image but can be overridden
ENV SIGNUPS_ALLOWED=false
ENV SHOW_PASSWORD_HINT=false
ENV WEBSOCKET_ENABLED=true
ENV ROCKET_WORKERS=10

# Expose ports (80 for HTTP, 3012 for WebSocket)
EXPOSE 80
EXPOSE 3012

# Define volume for persistence
VOLUME ["/data"]

# The base image CMD is likely correct, but we ensure we run as the user.
# We don't override CMD unless necessary, but we must ensure the binary can read /data
