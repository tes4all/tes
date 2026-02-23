#!/bin/bash
set -e

echo "Waiting for RustFS to be healthy..."
timeout 60s bash -c 'until curl -sf http://localhost:9000/health; do sleep 2; done'

echo "RustFS is up!"
echo "Checking Console health..."
curl -sf http://localhost:9001/rustfs/console/health

echo "Verification passed."
