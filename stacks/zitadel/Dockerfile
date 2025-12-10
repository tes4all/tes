FROM ghcr.io/zitadel/zitadel:v2.42.0

# Zitadel runs as non-root (usually 1000) by default.
# We copy the config to a location where it can be read.
COPY --chown=1000:1000 config/zitadel.yaml /app/zitadel.yaml

USER 1000

ENTRYPOINT ["/app/zitadel"]
CMD ["start-from-init", "--config", "/app/zitadel.yaml", "--masterkeyFromEnv"]
