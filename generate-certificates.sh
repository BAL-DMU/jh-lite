# !/bin/sh
# Copyright (c) 2025, Balgrist University Clinic, Digital Medicine Unit.
# Distributed under the terms of the Modified BSD License.

# Simple script to generate self-signed SSL certificates for JupyterHub
# Works in Git Bash on Windows or Linux

# Create directory for certificates
mkdir -p ssl

echo "Generating self-signed certificates..."

# Generate certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/jupyterhub.key \
  -out ssl/jupyterhub.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

if [ $? -eq 0 ]; then
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
else
  echo ""
  echo "Failed to generate certificates. Please make sure OpenSSL is installed."
  echo "For Windows: You can download OpenSSL from https://slproweb.com/products/Win32OpenSSL.html"
fi 