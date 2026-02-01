#!/bin/sh
set -e

# Fix permissions
if [ -d "/certs" ]; then
    # Ensure config dir exists
    mkdir -p /certs/config
    mkdir -p /certs/certificates

    # Init config if missing
    if [ ! -f "/certs/certificates.yml" ]; then
        printf "tls:\n  certificates: []\n" > /certs/certificates.yml
    fi

    chown -R appuser:appuser /certs
fi

# Fix permissions for Traefik dynamic config directory if variable is set
if [ -n "$TRAEFIK_DYNAMIC_CONFIG_FILE" ]; then
    CONFIG_DIR=$(dirname "$TRAEFIK_DYNAMIC_CONFIG_FILE")
    if [ -d "$CONFIG_DIR" ]; then
        chown -R appuser:appuser "$CONFIG_DIR"
    fi
fi

exec gosu appuser "$@"
