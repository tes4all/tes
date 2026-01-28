import os
import time
import glob
import yaml
import logging
from valkey import Valkey

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cert-syncer")

# Configuration
VALKEY_HOST = os.getenv("VALKEY_HOST", "valkey")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))
VALKEY_PASSWORD = os.getenv("VALKEY_PASSWORD", "insecure_default")

CERTS_DIR = "/certs/certificates"
OUTPUT_FILE = os.getenv("TRAEFIK_DYNAMIC_CONFIG_FILE", "/certs/certificates.yml")
CHANNEL_EVENTS = "events/certs_updated"

def get_valkey_client():
    return Valkey(host=VALKEY_HOST, port=VALKEY_PORT, password=VALKEY_PASSWORD, decode_responses=True)

def sync_certs_from_valkey(v):
    """
    Downloads all certificates from Valkey to local disk.
    """
    logger.info("Syncing certificates from Valkey...")
    try:
        # Scan for all certificate keys
        cursor = '0'
        while cursor != 0:
            cursor, keys = v.scan(cursor=cursor, match="cert_data:*", count=100)
            for key in keys:
                domain = key.replace("cert_data:", "")
                data = v.hgetall(key)

                if "crt" in data and "key" in data:
                    cert_path = os.path.join(CERTS_DIR, f"{domain}.crt")
                    key_path = os.path.join(CERTS_DIR, f"{domain}.key")

                    # Atomic write could be better, but simple write is fine for now
                    with open(cert_path, "w") as f: f.write(data["crt"])
                    with open(key_path, "w") as f: f.write(data["key"])
        logger.info("Sync complete.")
    except Exception as e:
        logger.error(f"Failed to sync certs: {e}")

def generate_traefik_config():
    """
    Scans the certificates directory and generates a Traefik dynamic configuration file.
    """
    logger.info("Regenerating Traefik TLS Config...")

    cert_files = glob.glob(os.path.join(CERTS_DIR, "*.crt"))
    certificates = []

    for cert_path in cert_files:
        # Assuming matching key exists
        base_name = os.path.splitext(os.path.basename(cert_path))[0]
        key_path = os.path.join(CERTS_DIR, f"{base_name}.key")

        if os.path.exists(key_path):
            certificates.append({
                "certFile": cert_path,
                "keyFile": key_path
            })
        else:
            logger.warning(f"Missing key for certificate: {cert_path}")

    config = {
        "tls": {
            "certificates": certificates
        }
    }

    try:
        # Atomic write to avoid partial reads by Traefik
        temp_file = OUTPUT_FILE + ".tmp"
        with open(temp_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        os.rename(temp_file, OUTPUT_FILE)
        logger.info(f"Updated {OUTPUT_FILE} with {len(certificates)} certificates.")
    except Exception as e:
        logger.error(f"Failed to write config: {e}")

def main():
    logger.info("Starting Cert Syncer Service")

    # Connect to Valkey
    v = None
    while True:
        try:
            v = get_valkey_client()
            v.ping()
            break
        except Exception as e:
            logger.error(f"Waiting for Valkey: {e}")
            time.sleep(2)

    # Initial Sync & Generation
    sync_certs_from_valkey(v)
    generate_traefik_config()

    # Redis Pub/Sub Loop
    while True:
        try:
            pubsub = v.pubsub()
            pubsub.subscribe(CHANNEL_EVENTS)
            logger.info(f"Subscribed to {CHANNEL_EVENTS}")

            while True:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=10)
                if message:
                    logger.info("Received update event. Syncing & Regenerating.")
                    sync_certs_from_valkey(v)
                    generate_traefik_config()

                # Check file changes manually every 60s just in case?
                # Or relying on events is safer. Let's rely on events + FileSystem Watcher if needed.
                # For Phase 2/3 simplicity, assume Cert Manager publishes events.

        except Exception as e:
            logger.error(f"Error in syncer loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
