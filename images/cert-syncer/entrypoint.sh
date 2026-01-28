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

exec gosu appuser "$@"
