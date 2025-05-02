# Copyright (c) 2025, Balgrist University Clinic, Digital Medicine Unit.
# Distributed under the terms of the Modified BSD License.

# PowerShell script to generate self-signed SSL certificates for JupyterHub
# Works on Windows

# Create directory for certificates
if (-not (Test-Path -Path "ssl")) {
    New-Item -Path "ssl" -ItemType Directory
}

Write-Host "Generating self-signed certificates..."

# Check if OpenSSL is installed
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
    Write-Host ""
    Write-Host "ERROR: OpenSSL is not installed or not in your PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install OpenSSL for Windows:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Yellow
    Write-Host "2. Choose 'Win64 OpenSSL v3.x.x Light' for most users" -ForegroundColor Yellow
    Write-Host "3. Run the installer and follow the prompts" -ForegroundColor Yellow
    Write-Host "4. Select the option to copy OpenSSL DLLs to Windows system directory" -ForegroundColor Yellow
    Write-Host "5. Add OpenSSL bin directory to your PATH:" -ForegroundColor Yellow
    Write-Host "   - Open Control Panel > System > Advanced System Settings > Environment Variables" -ForegroundColor Yellow
    Write-Host "   - Edit the 'Path' system variable and add: C:\Program Files\OpenSSL-Win64\bin" -ForegroundColor Yellow
    Write-Host "   - Restart PowerShell and try again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For more detailed instructions, see the windows-ssl-setup.md file." -ForegroundColor Yellow
    exit 1
}

# Generate certificates
$null = openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
  -keyout ssl/jupyterhub.key `
  -out ssl/jupyterhub.crt `
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Self-signed SSL certificates created in ./ssl directory" -ForegroundColor Green
    Write-Host ""
    Write-Host "Current configuration status:"
    Write-Host "- SSL certificate volume mounts are already active in docker-compose.yml"
    Write-Host "- SSL environment variables are already configured"
    Write-Host "- Port 8443 is already configured for HTTPS"
    Write-Host ""
    Write-Host "To apply the new certificates:"
    Write-Host "  docker-compose restart"
    Write-Host ""
    Write-Host "Note: Self-signed certificates will cause browser warnings."
    Write-Host "  For production use, replace with certificates from a trusted CA."
    Write-Host ""
    Write-Host "Access JupyterHub at: https://localhost:8443"
} else {
    Write-Host ""
    Write-Host "Failed to generate certificates." -ForegroundColor Red
    Write-Host "If OpenSSL is installed but you're still seeing errors, check that:" -ForegroundColor Yellow
    Write-Host "- You're running PowerShell as Administrator" -ForegroundColor Yellow
    Write-Host "- The ssl directory is writable" -ForegroundColor Yellow
    Write-Host "- For more help, see the windows-ssl-setup.md file" -ForegroundColor Yellow
}
