#!/bin/sh
set -e

# Fix permissions on the volume
# We need to ensure appuser (uid 1000) can read/write
if [ -d "/certs" ]; then
    chown -R appuser:appuser /certs
fi

# Drop privileges and execute the command
exec gosu appuser "$@"
