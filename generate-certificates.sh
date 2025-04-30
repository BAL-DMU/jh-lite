#!/bin/bash
# Script to generate self-signed SSL certificates for JupyterHub
# For production, you should use proper certificates from a trusted CA

set -e

# Create directory for certificates
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/jupyterhub.key \
  -out ssl/jupyterhub.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo ""
echo "Self-signed SSL certificates created in ./ssl directory"
echo ""
echo "To enable HTTPS in JupyterHub:"
echo "1. Uncomment the certificate volume mounts in docker-compose.yml"
echo "2. Uncomment the JUPYTERHUB_SSL environment variables in docker-compose.yml"
echo "3. Change port mapping from 8000:8000 to 8443:8443 in docker-compose.yml"
echo "4. Restart JupyterHub: docker-compose down && docker-compose up -d"
echo ""
echo "Note: Self-signed certificates will cause browser warnings."
echo "For production use, replace with proper certificates from a trusted CA." 