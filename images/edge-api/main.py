import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from valkey import asyncio as valkey

app = FastAPI(title="Edge Router API")

# Configuration
VALKEY_HOST = os.getenv("VALKEY_HOST", "valkey")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))
VALKEY_PASSWORD = os.getenv("VALKEY_PASSWORD", None)

# Defines
KEY_TARGET_DOMAINS = "target_domains"
CHANNEL_EVENTS = "events/certs_updated"

class DomainRequest(BaseModel):
    domain: str

class RouteRequest(BaseModel):
    name: str
    rule: str
    service_url: str

async def get_valkey():
    client = valkey.from_url(
        f"redis://{VALKEY_HOST}:{VALKEY_PORT}",
        password=VALKEY_PASSWORD,
        decode_responses=True
    )
    try:
        yield client
    finally:
        await client.close()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/domains")
async def add_domain(req: DomainRequest, vclient = Depends(get_valkey)):
    """
    Add a domain to the target list.
    Triggers certificate generation loop via Pub/Sub or polling
    (Cert Manager will pick this up).
    """
    # Add to set
    await vclient.sadd(KEY_TARGET_DOMAINS, req.domain)

    # Publish event to wake up Cert Manager immediately
    await vclient.publish(CHANNEL_EVENTS, json.dumps({
        "type": "domain_added",
        "domain": req.domain
    }))

    return {"status": "added", "domain": req.domain}

@app.get("/domains")
async def list_domains(vclient = Depends(get_valkey)):
    """List all domains configured for certificates."""
    domains = await vclient.smembers(KEY_TARGET_DOMAINS)
    return {"domains": list(domains)}

@app.delete("/domains")
async def remove_domain(req: DomainRequest, vclient = Depends(get_valkey)):
    """Remove a domain from targets."""
    await vclient.srem(KEY_TARGET_DOMAINS, req.domain)
    # We might want to trigger cleanup, but retention policy usually handles this.
    return {"status": "removed", "domain": req.domain}

@app.post("/routes")
async def add_route(req: RouteRequest, vclient = Depends(get_valkey)):
    """
    Add a dynamic route for Traefik via Redis Provider.
    Traefik Redis Provider uses specific key patterns.
    """
    # Traefik Redis Provider Key Format: traefik/http/routers/<name>/...
    # We use a transaction to ensure atomicity
    async with vclient.pipeline() as pipe:
        # Router Config
        pipe.set(f"traefik/http/routers/{req.name}/rule", req.rule)
        pipe.set(f"traefik/http/routers/{req.name}/service", req.name)
        pipe.set(f"traefik/http/routers/{req.name}/entrypoints", "websecure")
        pipe.set(f"traefik/http/routers/{req.name}/tls/certresolver", "default") # or myresolver

        # Service Config
        pipe.set(f"traefik/http/services/{req.name}/loadbalancer/servers/0/url", req.service_url)

        await pipe.execute()

    return {"status": "configured", "route": req.name}
