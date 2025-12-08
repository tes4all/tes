# Traefik 3.2 - L7 Reverse Proxy
# Golden Stack - Non-Root, Baked Config
FROM traefik:v3.2.3

# Create non-root user and directories
USER root
RUN addgroup -g 1000 traefik-user && \
    adduser -D -u 1000 -G traefik-user traefik-user && \
    mkdir -p /etc/traefik/dynamic /acme && \
    chown -R traefik-user:traefik-user /etc/traefik /acme

# Bake static configuration into image
COPY config/traefik.yml /etc/traefik/traefik.yml
RUN chown traefik-user:traefik-user /etc/traefik/traefik.yml

# Switch to non-root
USER 1000

# Expose ports: HTTP, HTTPS, Ping, Metrics
EXPOSE 80 443 8082 8083

# Healthcheck via ping endpoint
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8082/ping || exit 1

ENTRYPOINT ["traefik"]
