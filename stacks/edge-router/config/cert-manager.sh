#!/bin/sh

# ==============================================================================
# SECRET EXPANSION: Load Docker Secrets into Environment Variables
# Looks for variables ending in _FILE (e.g., INFOMANIAK_ACCESS_TOKEN_FILE)
# reads the file content, and exports the variable (e.g., INFOMANIAK_ACCESS_TOKEN)
# ==============================================================================
for var in $(env | grep '_FILE='); do
    # specific_var_FILE
    var_name="${var%%=*}"
    # specific_var
    target_name="${var_name%_FILE}"
    # /run/secrets/my_secret
    file_path="${var#*=}"

    if [ -f "$file_path" ]; then
        echo "Expanding secret $target_name from $file_path"
        export "$target_name"="$(cat "$file_path")"
    else
        echo "WARNING: Secret file $file_path defined in $var_name not found!"
    fi
done

# cert-manager.sh
# Handles ACME challenges for both Wildcard (DNS-01) and Customer Domains (HTTP-01)
# Saves certs to /certs which Traefik watches.

# Configuration
# DOMAINS_WILDCARD environment variable: "my-company.com,another-company.com"
# DOMAINS_CUSTOMER environment variable: "client.com,store.client.com"
EMAIL="${ACME_EMAIL:-admin@example.com}"
CERTS_DIR="/certs"
LEGO_SERVER="${LEGO_SERVER:-https://acme-v02.api.letsencrypt.org/directory}"
# DNS Provider for Wildcards (defaults to infomaniak if not set)
DNS_PROVIDER="${LEGO_DNS_PROVIDER:-infomaniak}"

# Function to Request Wildcard Certs (DNS-01)
request_wildcards() {
    echo "Starting Wildcard Certificate Check..."
    if [ -z "$DOMAINS_WILDCARD" ]; then
        echo "No wildcard domains configured."
        return
    fi

    echo "Using DNS Provider: $DNS_PROVIDER"

    IFS=','
    for domain in $DOMAINS_WILDCARD; do
        domain=$(echo "$domain" | xargs) # trim
        echo "Processing Wildcard for: $domain"
        # Provider credentials (e.g. INFOMANIAK_ACCESS_TOKEN, AWS_ACCESS_KEY_ID)
        # must be provided as ENV vars to the container.

        if [ -f "${CERTS_DIR}/certificates/${domain}.crt" ]; then
             echo "Certificate exists for $domain, checking renewal..."
             /lego --email "$EMAIL" --dns "$DNS_PROVIDER" --domains "*.$domain" --domains "$domain" --path "$CERTS_DIR" --server "$LEGO_SERVER" --accept-tos --dns.resolvers "9.9.9.9:53" renew --days 30
        else
             echo "Certificate missing for $domain, requesting..."
             /lego --email "$EMAIL" --dns "$DNS_PROVIDER" --domains "*.$domain" --domains "$domain" --path "$CERTS_DIR" --server "$LEGO_SERVER" --dns.resolvers "9.9.9.9:53" --accept-tos run
        fi
    done
    unset IFS
}

# Function to Request Customer Certs (HTTP-01)
request_customers() {
    if [ -z "$DOMAINS_CUSTOMER" ]; then
        echo "No customer domains to process."
        return
    fi

    echo "Starting Customer Certificate Check (HTTP-01)..."
    IFS=','
    for domain in $DOMAINS_CUSTOMER; do
        domain=$(echo "$domain" | xargs) # trim
        echo "Processing Customer Domain: $domain"
        # Uses internal port 8080. Traefik must route /.well-known/acme-challenge/ to this service:8080

        if [ -f "${CERTS_DIR}/certificates/${domain}.crt" ]; then
             echo "Certificate exists for $domain, checking renewal..."
             /lego --email "$EMAIL" --http --http.port :8080 --domains "$domain" --path "$CERTS_DIR" --server "$LEGO_SERVER" --accept-tos renew --days 30
        else
             echo "Certificate missing for $domain, requesting..."
             /lego --email "$EMAIL" --http --http.port :8080 --domains "$domain" --path "$CERTS_DIR" --server "$LEGO_SERVER" --accept-tos run
        fi
    done
    unset IFS
}

generate_yaml() {
    YAML_FILE="$CERTS_DIR/certificates.yml"
    echo "Generating Traefik YAML config at $YAML_FILE..."

    # buffer content to check if we have any certs
    CONTENT=""

    for cert in "$CERTS_DIR/certificates/"*.crt; do
        # handle case where no files match
        [ -f "$cert" ] || continue

        base=$(basename "$cert" .crt)
        key="$CERTS_DIR/certificates/$base.key"

        # Check if both cert and key exist and are not empty
        if [ -s "$cert" ] && [ -s "$key" ]; then
             # Validate content looks like a certificate to avoid empty/garbage files crashing Traefik
             if grep -q "BEGIN CERTIFICATE" "$cert"; then
                 # Use ABSOLUTE PATHS for Traefik v3 File Provider
                 # matches the mount point inside the Traefik container (/certs)
                 CONTENT="${CONTENT}    - certFile: /certs/certificates/$base.crt
      keyFile: /certs/certificates/$base.key
"
             else
                 echo "WARN: $cert exists but does not appear to be a valid PEM file. Skipping."
             fi
        fi
    done

    echo "tls:" > "$YAML_FILE"
    if [ -n "$CONTENT" ]; then
        echo "  certificates:" >> "$YAML_FILE"
        echo "$CONTENT" >> "$YAML_FILE"
    else
        # Output empty list to maintain valid YAML if no certs exist yet
        echo "  certificates: []" >> "$YAML_FILE"
    fi

    # Fix permissions so Traefik (non-root) can read them
    echo "Fixing permissions on $CERTS_DIR..."
    # Ensure directories are executable (searchable)
    find "$CERTS_DIR" -type d -exec chmod 755 {} \;
    # Ensure files are readable by everyone (traefik user 1000)
    find "$CERTS_DIR" -type f -exec chmod 644 {} \;
}

# Grant execution permissions to script inside container if needed, though usually handled by file attributes
# Main Loop
while true; do
    echo "------------------------------------------------"
    echo "(Version 7) Running Cert Manager Loop at $(date)"

    # Generate config first to clean up any bad state/permissions from previous runs
    generate_yaml

    # Check permissions immediately
    chmod -R a+rX "$CERTS_DIR"

    # We run them in sequence.

    request_wildcards
    request_customers
    generate_yaml

    echo "Cert check complete. Sleeping for 24h..."
    sleep 86400 # Check every day
done
