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

# Set appropriate permissions
chmod 600 ssl/jupyterhub.key
chmod 644 ssl/jupyterhub.crt

echo ""
echo "Self-signed SSL certificates created in ./ssl directory"
echo ""
echo "Current configuration status:"
echo "- SSL certificate volume mounts are already active in docker-compose.yml"
echo "- SSL environment variables are already configured"
echo "- Port 8443 is already configured for HTTPS"
echo ""
echo "To apply the new certificates:"
echo "  docker-compose restart"
echo ""
echo "Note: Self-signed certificates will cause browser warnings."
echo "  For production use, replace with certificates from a trusted CA."
echo ""
echo "Access JupyterHub at: https://localhost:8443" 