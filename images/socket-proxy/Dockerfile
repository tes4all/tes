FROM tecnativa/docker-socket-proxy:v0.4.2

# Patch HAProxy config to fix "missing timeout" warnings for event streams (HAProxy 3.x)
# We use sed to inject timeouts into the docker-events backend of the default template.
# This avoids maintaining a full copy of haproxy.cfg.
RUN sed -i '/backend docker-events/,/frontend/ s/server dockersocket $SOCKET_PATH/&\n    timeout server 8h\n    timeout connect 10s/' /usr/local/etc/haproxy/haproxy.cfg.template
