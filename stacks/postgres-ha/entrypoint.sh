#!/bin/sh
set -e

# Fix permissions on data directory
if [ -d "/var/lib/postgresql/data" ]; then
    chmod 700 /var/lib/postgresql/data
fi

exec "$@"
