# JH-Lite: Local JupyterHub for Prototyping & Customization

A lightweight JupyterHub running on localhost via Docker, based on the official JupyterHub stack. This setup enables quick local deployment for testing and development.

## Project Description

JH-Lite is ideal for:
- Testing research workflows before production deployment
- Customizing notebook environments and extensions
- Preparing for institutional JupyterHub deployment
- Providing a quick entry point for new collaborators

## Project Structure

```
jh-lite/
├── jupyterhub-system-data/ # JupyterHub system files (database, cookies)
├── ssl/                    # SSL certificates for HTTPS
├── create-admin.py         # Admin user creation script
├── docker-compose.yml      # Docker service configuration
├── Dockerfile              # Container definition
├── generate-certificates.sh # SSL certificate generator
├── jupyterhub_config.py    # JupyterHub configuration
├── README.md               # This documentation
└── LICENSE                 # Project license
```

## Quick Start

1. Clone the repository
2. Run `docker-compose up -d --build`
3. Create admin: `docker exec -it jupyterhub python /srv/jupyterhub/create-admin.py admin yourpassword`
4. Access: http://localhost:8000 (or https://localhost:8443 with HTTPS enabled)

## Installation Guide: JupyterHub with Docker Compose

### Prerequisites

- Docker and Docker Compose installed
- Windows, macOS, or Linux operating system
- Port 8000 (for HTTP) or 8443 (for HTTPS) available
- Internet access to pull Docker images

### Step 1: Build and Start JupyterHub

From the root of the `jh-lite` project:

```bash
# Make sure the system data directory exists
mkdir -p jupyterhub-system-data

# Start JupyterHub
docker-compose up -d --build
```

For Windows PowerShell users:
```powershell
# Create directory if it doesn't exist
New-Item -Path "jupyterhub-system-data" -ItemType Directory -Force

# Start the service
docker compose up -d --build
```

The service will be accessible at: `http://localhost:8000` (or `https://localhost:8443` if HTTPS is enabled)

### Step 2: Create Admin User

Create an admin user for initial login:

```bash
# Create admin user
docker exec -it jupyterhub python /srv/jupyterhub/create-admin.py admin yourpassword
```

Replace `yourpassword` with a secure password of your choice.

### Step 3: Login and User Management

Once you've created the admin user, you can:

1. Log in at `http://localhost:8000` (or `https://localhost:8443`) with your admin credentials
2. Use the admin interface at `/hub/admin` to manage users
3. Users can self-register at `/hub/signup`

### Step 4: Enabling HTTPS

JupyterHub warns about running over unsecured HTTP. To enable HTTPS:

1. Generate self-signed certificates:
   ```bash
   # Make script executable (Linux/macOS)
   chmod +x generate-certificates.sh
   
   # Run the script
   ./generate-certificates.sh
   
   # For Windows PowerShell
   # ./generate-certificates.sh or bash generate-certificates.sh
   ```

2. Update docker-compose.yml (already configured in this repository):
   - Ensure SSL certificate volume mounts are uncommented
   - Ensure SSL environment variables are uncommented
   - Ensure port 8443 is used instead of 8000

3. Restart JupyterHub:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. Access via HTTPS: `https://localhost:8443`

   Note: Self-signed certificates will trigger browser warnings. For production, use certificates from a trusted Certificate Authority.

### Step 5: Data Storage

JH-Lite uses different storage locations for different types of data:

1. **System Data** (`jupyterhub-system-data/`):
   - Local directory containing JupyterHub database and cookie secrets
   - Used by the JupyterHub service for authentication and state management
   - Do not use this for your own data files

2. **Docker Volume** (`jupyterhub-data`):
   - Docker-managed persistent volume
   - Used internally by JupyterHub

3. **User Notebooks and Files**:
   - Each user gets their own workspace inside their notebook container
   - To share datasets with notebooks, create a dedicated `datasets` directory and mount it
   - You can add dataset mounts by editing `docker-compose.yml` and `jupyterhub_config.py`

### Step 6: Stopping and Cleanup

To stop the service:
```bash
docker-compose down
```

To remove all data including volumes (warning: this deletes all persistent data):
```bash
docker-compose down -v
```

## Troubleshooting

View logs:
```bash
docker-compose logs -f
```

### Authentication Issues

If you're having authentication problems:

1. Make sure you've created an admin user with the create-admin.py script
2. Verify the user is authorized in the admin panel
3. Check logs for any authentication errors:
   ```bash
   docker-compose logs | grep auth
   ```

### Container or Network Issues

If containers aren't starting properly:

1. Check for port conflicts:
   ```bash
   docker-compose ps
   ```
2. Verify Docker socket access:
   ```bash 
   docker info
   ```
3. Try rebuilding the container:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Customization

Modify the following files to customize your deployment:
- `jupyterhub_config.py` - Configure authentication, spawner options, and security settings
- `Dockerfile` - Add custom packages or system dependencies 
- `docker-compose.yml` - Change ports, volumes, and environment variables

### Adding Datasets for Notebooks

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

For more extensive configuration options, see the [JupyterHub documentation](https://jupyterhub.readthedocs.io/).
