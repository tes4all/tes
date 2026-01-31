import os
import time
import subprocess
import logging
import sys
import json
import datetime
import re
import threading
import docker
import shlex
from valkey import Valkey
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cert-manager")

# Load Secrets
def load_secrets():
    """
    Iterates over environment variables. If a variable name ends with '_FILE',
    it reads the content of the file pointed to by the value, and sets
    the variable without the suffix to that content.
    """
    for key, value in os.environ.items():
        if key.endswith("_FILE") and os.path.isfile(value):
            target_key = key[:-5] # Remove _FILE
            try:
                with open(value, 'r') as f:
                    content = f.read().strip()
                os.environ[target_key] = content
                # logger.info(f"Loaded secret for {target_key}")
            except Exception as e:
                logger.warning(f"Failed to load secret {key}: {e}")

load_secrets()

# Configuration
VALKEY_HOST = os.getenv("VALKEY_HOST", "valkey")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))
VALKEY_PASSWORD = os.getenv("VALKEY_PASSWORD", "insecure_default")
CERTS_DIR = "/certs"

# Scheduling Keys
KEY_SCHEDULE = "cert_schedule"   # ZSET: domain -> timestamp (next check)
KEY_META = "cert_meta"           # HASH: domain -> json (errors, last_attempt)
KEY_TARGETS = "target_domains"   # SET: configured domains (source of truth)
KEY_CONFIG = "cert_config"       # HASH: domain -> json (challenge_type, etc)

# Acme Config
ACME_EMAIL = os.getenv("ACME_EMAIL", "")
ACME_CHALLENGE_TYPE = os.getenv("ACME_CHALLENGE_TYPE", "dns") # "dns" or "http"
ACME_HTTP_DOMAINS = [d.strip() for d in os.getenv("ACME_HTTP_DOMAINS", "").split(",") if d.strip()]
LEGO_DNS_PROVIDER = os.getenv("LEGO_DNS_PROVIDER", "manual")
LEGO_SERVER = os.getenv("LEGO_SERVER", "https://acme-v02.api.letsencrypt.org/directory")
LEGO_EXTRA_ARGS = os.getenv("LEGO_EXTRA_ARGS", "")

# Static Config
DOMAINS_WILDCARD = os.getenv("DOMAINS_WILDCARD", "")
WILDCARD_ROOTS = [d.strip() for d in DOMAINS_WILDCARD.split(",") if d.strip()]

# Docker Client
try:
    docker_client = docker.from_env()
except Exception as e:
    logger.warning(f"Failed to initialize Docker client: {e}. Auto-discovery will be disabled.")
    docker_client = None

def get_valkey_client():
    try:
        return Valkey(host=VALKEY_HOST, port=VALKEY_PORT, password=VALKEY_PASSWORD, decode_responses=True)
    except Exception as e:
        logger.error(f"Failed to create Valkey client: {e}")
        sys.exit(1)

def get_cert_expiry(domain):
    """
    Reads local cert file and returns expiry timestamp (unix).
    Returns None if file not found.
    """
    cert_path = os.path.join(CERTS_DIR, "certificates", f"{domain}.crt")
    if not os.path.exists(cert_path):
        return None

    try:
        with open(cert_path, "rb") as f:
            cert_data = f.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            # not_valid_after is minimal; use not_valid_after_utc if available in new crypto deps
            # but standard image might have older. .not_valid_after is deprecated but works.
            expiry = cert.not_valid_after_utc if hasattr(cert, 'not_valid_after_utc') else cert.not_valid_after
            return expiry.timestamp()
    except Exception as e:
        logger.error(f"Failed to parse cert for {domain}: {e}")
        return None

def publish_cert_to_valkey(v, domain):
    """
    Reads the certificate and key from disk and pushes them to Valkey.
    """
    cert_path = os.path.join(CERTS_DIR, "certificates", f"{domain}.crt")
    key_path = os.path.join(CERTS_DIR, "certificates", f"{domain}.key")

    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        logger.warning(f"Cannot publish {domain}: Files not found.")
        return

    try:
        with open(cert_path, "r") as f:
            cert_data = f.read()
        with open(key_path, "r") as f:
            key_data = f.read()

        # Store as Hash: cert:data:<domain> -> { crt: ..., key: ... }
        v.hset(f"cert_data:{domain}", mapping={"crt": cert_data, "key": key_data})
        logger.info(f"Published certificate data for {domain} to Valkey")

        # Notify Syncers
        v.publish(CHANNEL_EVENTS, json.dumps({"type": "cert_updated", "domain": domain}))

    except Exception as e:
        logger.error(f"Failed to publish cert for {domain} to Valkey: {e}")

def schedule_domain(v, domain, timestamp):
    """Schedule a domain for checking at a specific timestamp."""
    v.zadd(KEY_SCHEDULE, {domain: timestamp})
    logger.debug(f"Scheduled {domain} for {datetime.datetime.fromtimestamp(timestamp)}")

def resolve_challenge_type(v, domain):
    """
    Determines challenge type for a domain.
    Priority:
    1. ACME_HTTP_DOMAINS env var (Force HTTP)
    2. Redis KEY_CONFIG (Populated by Docker Labels)
    3. ACME_CHALLENGE_TYPE env var (Default)
    """
    if domain in ACME_HTTP_DOMAINS:
        return "http"

    try:
        config_raw = v.hget(KEY_CONFIG, domain)
        if config_raw:
            config = json.loads(config_raw)
            if "challenge" in config:
                return config["challenge"]
    except Exception:
        pass

    return ACME_CHALLENGE_TYPE

def issue_cert(v, domain):
    """
    Runs Lego. Returns (success: bool, output: str).
    """
    logger.info(f"Attempting to issue/renew certificate for {domain}")

    challenge_type = resolve_challenge_type(v, domain)
    logger.info(f"Using challenge type: {challenge_type} for {domain}")

    cmd = [
        "lego",
        "--email", ACME_EMAIL,
        "--domains", domain,
        "--path", CERTS_DIR,
        "--server", LEGO_SERVER,
        "--accept-tos"
    ]

    if LEGO_EXTRA_ARGS:
        cmd.extend(shlex.split(LEGO_EXTRA_ARGS))

    # Add wildcard domain if this is a wildcard root
    if domain in WILDCARD_ROOTS:
        cmd.append("--domains")
        cmd.append(f"*.{domain}")

    if challenge_type == "http":
        cmd.append("--http")
        cmd.append("--http.port")
        cmd.append(":8080")
    else:
        cmd.append("--dns")
        cmd.append(LEGO_DNS_PROVIDER)

    cmd.append("run")
    # If cert exists, "run" might fail if it's not time to renew?
    # Lego "run" obtains a cert. If one exists, it might error or overwrite.
    # Lego "renew" checks expiry.
    # Since we manage scheduling, we can use "run" if missing, "renew" if exists?
    # Actually, "run" is idempotent-ish but fails if valid cert exists.
    # "renew" --days X allows forcing.

    is_renewal = False
    if get_cert_expiry(domain) is not None:
        is_renewal = True
        cmd[-1] = "renew"
        cmd.append("--days")
        cmd.append("60") # Renew if within 60 days
        cmd.append("--reuse-key") # Good practice

    env = os.environ.copy()

    try:
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        logger.info(f"Certificate action successful for {domain}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Lego failed for {domain}: {e.stderr}")
        return False, e.stderr

CHANNEL_EVENTS = "events/certs_updated"

def reconcile_env_vars(v):
    """
    Reads DOMAINS_WILDCARD and ensures they are in target_domains.
    """
    if not DOMAINS_WILDCARD:
        return

    domains = [d.strip() for d in DOMAINS_WILDCARD.split(',') if d.strip()]
    for d in domains:
        if d.endswith((".localhost", ".local", ".lokal")):
            continue

        # For wildcards, we just manage the root domain for certificate issuance logic,
        # usually checks '*.' + d or just 'd'. The cert filenames are 'd.crt'.
        # Legacy script used the domain string directly.
        v.sadd(KEY_TARGETS, d)
        logger.debug(f"Ensured env var domain {d} is in targets")

def scan_docker_services(v):
    """
    Scans Docker Swarm Services for Traefik routers with Host() rules.
    Extracts domains and adds them to target_domains.
    """
    if not docker_client:
        return

    try:
        services = docker_client.services.list()
        found_domains = set()

        for service in services:
            labels = service.attrs.get('Spec', {}).get('Labels', {})

            # Check for override label for this service
            svc_challenge = labels.get("cert-manager.challenge", None)

            for key, value in labels.items():
                # Look for traefik.http.routers.<name>.rule
                # This matches: traefik.http.routers.my-app.rule = Host(`foo.com`)
                # or Host(`a.com`, `b.com`)
                if "traefik.http.routers" in key and ".rule" in key:
                    # Extract content inside Host(...)
                    # Simple regex for Host(`...`) or Host('...')
                    matches = re.findall(r"Host\([`'\"](.*?)[`'\"]\)", value)
                    for match in matches:
                        # Handle multiple args: Host(`a.com`, `b.com`) -> regex might get a.com`, `b.com
                        # Better to split by comma
                        parts = match.split(",")
                        for part in parts:
                            d = part.strip().strip("`'\"")
                            if d and not d.endswith((".localhost", ".local", ".lokal")):
                                # Check if covered by wildcard
                                is_covered = False
                                for root in WILDCARD_ROOTS:
                                    if d.endswith(f".{root}"):
                                        is_covered = True
                                        break

                                if not is_covered:
                                    found_domains.add(d)
                                    # Store config if specific challenge set
                                    if svc_challenge:
                                         v.hset(KEY_CONFIG, d, json.dumps({"challenge": svc_challenge}))

        # Sync to Redis
        for d in found_domains:
            if not v.sismember(KEY_TARGETS, d):
                logger.info(f"Discovered new domain from Docker: {d}")
                v.sadd(KEY_TARGETS, d)
                # Redis Key expiration logic could be added here to remove old stacks?
                # For now, append-only is safer.
                v.publish(CHANNEL_EVENTS, json.dumps({
                    "type": "domain_added",
                    "domain": d
                }))

    except Exception as e:
        logger.error(f"Docker scan failed: {e}")

def listen_docker_events(v):
    """
    Listens for Docker Swarm Service events (create/update)
    and triggers a scan immediately.
    """
    if not docker_client:
        return

    logger.info("Starting Docker Event Listener...")
    try:
        # Filter for service events
        events = docker_client.events(decode=True, filters={"type": "service"})
        for event in events:
            action = event.get("Action")
            if action in ["create", "update"]:
                logger.info(f"Docker Event detected: {action}. Triggering scan.")
                scan_docker_services(v) # Re-use the scan logic
    except Exception as e:
        logger.error(f"Docker Event Listener failed: {e}")


def reconcile_targets(v):
    """
    Syncs the Source-of-Truth SET with the Scheduler ZSET.
    Ensures newly added domains are scheduled immediately.
    """
    try:
        targets = v.smembers(KEY_TARGETS)
        scheduled = v.zrange(KEY_SCHEDULE, 0, -1)

        # Add new
        for t in targets:
            if t not in scheduled:
                logger.info(f"New domain detected: {t}. Scheduling immediately.")
                schedule_domain(v, t, time.time())

        # Cleanup (Optional: Remove scheduled items not in targets?
        # Maybe we want to keep them to revoke? For now, clean up.)
        for s in scheduled:
            if s not in targets:
                logger.info(f"Domain {s} removed from targets. Removing from schedule.")
                v.zrem(KEY_SCHEDULE, s)

    except Exception as e:
        logger.error(f"Reconciliation failed: {e}")

def process_due_domains(v):
    """
    Pops overdue items from ZSET and processes them.
    Implements rate-limit backoff.
    """
    now = time.time()
    # Fetch 1 item due before 'now'
    items = v.zrangebyscore(KEY_SCHEDULE, "-inf", now, start=0, num=1)

    if not items:
        return # Nothing to do

    domain = items[0]

    success, output = issue_cert(v, domain)

    if success:
        # Publish to Valkey for Syncers
        publish_cert_to_valkey(v, domain)

        # Check new expiry
        expiry = get_cert_expiry(domain)
        if expiry:
            # Schedule next check 30 days before expiry
            next_check = expiry - (30 * 24 * 3600)
            logger.info(f"Rescheduling {domain} for {datetime.datetime.fromtimestamp(next_check)}")
            schedule_domain(v, domain, next_check)
            # Clear errors
            v.hdel(KEY_META, domain)
        else:
            # Weird state. Schedule retry soon.
            schedule_domain(v, domain, now + 300)
    else:
        # Failure Backoff
        # Get failure count
        meta_raw = v.hget(KEY_META, domain)
        meta = json.loads(meta_raw) if meta_raw else {"failures": 0}
        meta["failures"] += 1
        meta["last_error"] = output[-200:] # store tail of log

        v.hset(KEY_META, domain, json.dumps(meta))

        # Exponential backoff: 5m, 10m, 20m, ... max 24h
        backoff = min(300 * (2 ** (meta["failures"] - 1)), 86400)

        # If rate limit detected in output, force at least 1 hour
        if "429" in output or "rate limit" in output.lower():
            backoff = max(backoff, 3600)

        logger.warning(f"Rescheduling {domain} (Failure #{meta['failures']}) in {backoff}s")
        schedule_domain(v, domain, now + backoff)

def main():
    logger.info("Starting Cert Manager Service (Scheduler Optimized)")

    v = None
    pubsub = None
    while True:
        try:
            v = get_valkey_client()
            v.ping() # Check connection

            # Subscribe pub/sub
            pubsub = v.pubsub()
            pubsub.subscribe(CHANNEL_EVENTS)
            logger.info(f"Subscribed to {CHANNEL_EVENTS}")
            break
        except Exception as e:
            logger.error(f"Waiting for Valkey... ({e})")
            time.sleep(2)

    # Initial Reconcile
    try:
        reconcile_env_vars(v)
        scan_docker_services(v) # Initial Scan
        reconcile_targets(v)
    except Exception as e:
        logger.error(f"Initial reconcile failed: {e}")

    # Start Docker Event Listener in background thread
    if docker_client:
        t = threading.Thread(target=listen_docker_events, args=(v,), daemon=True)
        t.start()

    while True:
        try:
            # Check for events (Short timeout to allow frequent polling of ZSET)
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message:
                logger.info(f"Received event: {message}")
                data = json.loads(message['data'])
                if data.get("type") == "domain_added":
                    # Force check now
                    schedule_domain(v, data["domain"], time.time())
                elif data.get("type") == "force_renew":
                    schedule_domain(v, data["domain"], time.time())

            # Reconcile periodically (e.g. every loop or every X seconds)
            # keeping it simple: reconcile every loop is overkill if loop is fast.
            # but loop waits 1s.
            if int(time.time()) % 60 == 0:
                reconcile_env_vars(v)
                # scan_docker_services(v) # Handled by events now, but keep as fallback?
                # Let's keep it as a slow fallback (every 60s) in case we miss an event.
                scan_docker_services(v)
                reconcile_targets(v)

            # Process Schedule
            process_due_domains(v)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
