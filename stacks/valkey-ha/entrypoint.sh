#!/bin/sh
set -e

# Define configuration paths
VALKEY_CONF_SRC="/etc/valkey/valkey.conf"
VALKEY_CONF_DEST="/data/valkey.conf"
SENTINEL_CONF_SRC="/etc/valkey/sentinel.conf"
SENTINEL_CONF_DEST="/data/sentinel.conf"

# Function to setup permissions
setup_perms() {
    chown -R valkey:valkey /data
}

# Check the command or arguments to determine the mode
if [ "$1" = "valkey-sentinel" ] || [ "$1" = "sentinel" ]; then
    echo "Starting in Sentinel mode..."

    # Copy sentinel config to writable location if it doesn't exist
    if [ ! -f "$SENTINEL_CONF_DEST" ]; then
        if [ -f "$SENTINEL_CONF_SRC" ]; then
            cp "$SENTINEL_CONF_SRC" "$SENTINEL_CONF_DEST"
        else
            echo "Sentinel config not found at $SENTINEL_CONF_SRC"
            exit 1
        fi
    fi

    setup_perms

    # Sentinel modifies the config file, so we must use the writable one
    exec valkey-sentinel "$SENTINEL_CONF_DEST"

elif [ "$1" = "valkey-server" ] || [ "$1" = "valkey" ]; then
    echo "Starting in Valkey server mode..."

    # For Valkey server, we check if we need to copy a config or if one is provided
    # If a config file is provided as an argument, we use that.
    # Otherwise, we default to copying our template to data for read/write access if needed,
    # or just use the static one if readonly is fine.
    # However, for HA, having a writable config is often useful for state.

    # Clean up arguments to pass to exec
    CMD="$1"
    shift

    # If the first argument is a file, use it directly (standard valkey behavior)
    if [ -n "$1" ] && [ -f "$1" ]; then
        setup_perms
        exec valkey-server "$@"
    else
        # No config passed, let's copy default to data if not present
        if [ ! -f "$VALKEY_CONF_DEST" ]; then
             if [ -f "$VALKEY_CONF_SRC" ]; then
                cp "$VALKEY_CONF_SRC" "$VALKEY_CONF_DEST"
            else
                echo "Valkey config not found at $VALKEY_CONF_SRC"
            fi
        fi

        setup_perms

        # Determine command args
        ARGS="$@"

        if [ -f "$VALKEY_CONF_DEST" ]; then
             exec valkey-server "$VALKEY_CONF_DEST" --protected-mode no $ARGS
        else
             exec valkey-server --protected-mode no $ARGS
        fi
    fi
else
    # Run arbitrary commands
    setup_perms
    exec "$@"
fi
