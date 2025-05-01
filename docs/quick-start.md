# Quick Start Guide

This guide provides the fastest way to get JH-Lite up and running on your local machine. For more detailed instructions, see the [Installation](installation.md) guide.

## Prerequisites

Before you begin, ensure you have:

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- 4GB+ of RAM available
- Administrative/sudo access on your machine

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/jh-lite.git
cd jh-lite
```

## Step 2: Generate SSL Certificates

For secure HTTPS access (recommended):

**Linux/macOS:**
```bash
sh generate-certificates.sh
```

**Windows:**
```powershell
PowerShell -ExecutionPolicy Bypass -File .\generate-certificates.ps1
```

> **Note**: On Windows, you may need to install OpenSSL first from [https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)

## Step 3: Start JH-Lite

```bash
docker-compose up -d --build
```

This command builds and starts JupyterHub in the background. The first run may take a few minutes as Docker downloads the necessary images.

## Step 4: Create Admin User

Create an admin user for initial login:

```bash
docker exec -it jupyterhub python /srv/jupyterhub/create-admin.py admin yourpassword
```

Replace `yourpassword` with a secure password of your choice.

## Step 5: Access JH-Lite

Open a web browser and navigate to:

- **HTTP**: [http://localhost:8000](http://localhost:8000)
- **HTTPS**: [https://localhost:8443](https://localhost:8443)

> **Note**: If using HTTPS with self-signed certificates, you'll need to accept the security warning in your browser.

Log in with the admin credentials you created in Step 4.

## Step 6: Manage Users

As an admin, you can:

1. Access the admin panel at [http://localhost:8000/hub/admin](http://localhost:8000/hub/admin) (or [https://localhost:8443/hub/admin](https://localhost:8443/hub/admin) for HTTPS)
2. Create new users
3. Start and stop user servers
4. Monitor system activity

New users can self-register at `/hub/signup` if enabled in the configuration.

## Step 7: Stopping JH-Lite

When you're done using JH-Lite, you can stop it with:

```bash
docker-compose down
```

This stops the containers but preserves all data. To completely remove everything including volumes (WARNING: this will delete all data):

```bash
docker-compose down -v
```

## Next Steps

Now that you have JH-Lite running, you might want to:

- [Customize your configuration](configuration.md)
- [Integrate custom Docker images](docker-stacks.md)
- [Add GPU support](gpu-support.md) for compute-intensive workloads
- [Troubleshoot common issues](troubleshooting.md)
