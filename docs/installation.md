# Detailed Installation Guide

This guide provides comprehensive instructions for installing JH-Lite in different environments. For a faster setup, see the [Quick Start Guide](quick-start.md).

## Prerequisites

Ensure your system meets the [server requirements](server-requirements.md) before proceeding.

## Installation Options

JH-Lite can be installed in two primary ways:

1. **Docker Compose Installation** (recommended for most users)
2. **The Littlest JupyterHub (TLJH) Installation** (for dedicated servers)

## Docker Compose Installation

### Prerequisites

- Docker and Docker Compose installed
- Windows, macOS, or Linux operating system
- Port 8000 (for HTTP) or 8443 (for HTTPS) available
- Internet access to pull Docker images

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/jh-lite.git
cd jh-lite
```

### Step 2: Create System Data Directory

This directory will store JupyterHub's system files:

**Linux/macOS:**
```bash
mkdir -p jupyterhub-system-data
```

**Windows PowerShell:**
```powershell
New-Item -Path "jupyterhub-system-data" -ItemType Directory -Force
```

### Step 3: Generate SSL Certificates (Optional but Recommended)

For secure HTTPS access:

**Linux/macOS:**
```bash
sh generate-certificates.sh
```

**Windows:**
```powershell
PowerShell -ExecutionPolicy Bypass -File .\generate-certificates.ps1
```

> **Note for Windows**: You'll need to install OpenSSL first from [https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)

### Step 4: Start JupyterHub

Build and start the JupyterHub service:

```bash
docker-compose up -d --build
```

> **Note**: The first run may take a few minutes as Docker downloads and builds the necessary images.

### Step 5: Create an Admin User

Create an admin user for initial login:

```bash
docker exec -it jupyterhub python /srv/jupyterhub/create-admin.py admin yourpassword
```

Replace `yourpassword` with a secure password of your choice.

### Step 6: Access JupyterHub

Open a web browser and navigate to:

- If using HTTP: [http://localhost:8000](http://localhost:8000)
- If using HTTPS: [https://localhost:8443](https://localhost:8443)
  
> **Note**: If using HTTPS with self-signed certificates, you'll need to accept the security warning in your browser.

## The Littlest JupyterHub (TLJH) Installation

For dedicated servers, you can install JH-Lite using The Littlest JupyterHub (TLJH).

### Prerequisites

- A server running **Ubuntu 20.04+** (Ubuntu 22.04 LTS recommended)
- Root (sudo) access
- Public IP address accessible from your users' browsers
- Ability to SSH into the server
- At least **1GB RAM** (32 GB recommended for production)
- Optional: mounted **NAS** volumes for persistent data

### Installation Steps

1. SSH into your server
2. Run the TLJH installer:

```bash
sudo apt update
sudo apt install python3 python3-dev git curl
curl -L https://tljh.jupyter.org/bootstrap.py | sudo -E python3 - --admin <admin-username>
```

Replace `<admin-username>` with your desired admin username.

3. Visit the server URL in your browser:
```
http://<server-ip>
```

4. Log in with the admin username and set a password

5. Configure TLJH for JH-Lite:

```bash
sudo tljh-config set user_environment.default_app jupyterlab
sudo tljh-config reload
```

For detailed TLJH configuration options, refer to the [official TLJH documentation](https://tljh.jupyter.org/en/latest/).

## Post-Installation Steps

After installing JH-Lite, consider these additional configuration steps:

### Configure Authentication

By default, JH-Lite uses local user authentication. To use other authentication methods:

1. Edit the `jupyterhub_config.py` file
2. Restart JupyterHub:

```bash
docker-compose down
docker-compose up -d
```

### Add Datasets for Notebooks

To make datasets available to notebooks:

1. Create a datasets directory:
   ```bash
   mkdir -p datasets
   # Add your data files here
   ```

2. Edit `docker-compose.yml` to add the volume:
   ```yaml
   services:
     hub:
       volumes:
         # ... existing volumes
         - ./datasets:/srv/jupyterhub/datasets
   ```

3. Edit `jupyterhub_config.py` to mount datasets in user containers:
   ```python
   # In customize_volumes function:
   spawner.volumes['/srv/jupyterhub/datasets'] = {'bind': '/home/jovyan/datasets', 'mode': 'ro'}
   ```

4. Restart JupyterHub:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Enable HTTPS (If not done during installation)

If you didn't enable HTTPS during installation:

1. Generate SSL certificates as described in Step 3
2. Update `docker-compose.yml`:
   - Ensure SSL certificate volume mounts are uncommented
   - Ensure SSL environment variables are uncommented
   - Ensure port 8443 is used instead of 8000
3. Restart JupyterHub:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Uninstallation

To remove JH-Lite:

```bash
docker-compose down   # Preserves volumes
# OR
docker-compose down -v  # Removes volumes (WARNING: This deletes all data)
```

For TLJH installations:
```bash
sudo apt purge jupyterhub
sudo apt autoremove
# Clean up user data directories as needed
```
