#!/bin/bash
set -euo pipefail

mkdir -p src/static/ssl
openssl req -x509 -newkey rsa:4096 -keyout src/static/ssl/localhost.key \
    -out src/static/ssl/localhost.crt -days 365 -nodes \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "Certificados SSL generados en src/static/ssl/"
