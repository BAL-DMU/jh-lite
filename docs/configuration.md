# Configuration Guide

This document explains how to configure JH-Lite to customize its behavior, appearance, and functionality.

## Configuration Overview

JH-Lite's configuration is primarily managed through these files:

- `jupyterhub_config.py` - The main configuration file for JupyterHub
- `docker-compose.yml` - Docker service configuration
- `Dockerfile` - Custom container definition

## Essential Configuration: jupyterhub_config.py

The `jupyterhub_config.py` file contains the core configuration for JupyterHub. Here are the key sections you might want to customize:

### Basic Settings

```python
# Base URL for the application
c.JupyterHub.base_url = '/'

# IP address to bind to
c.JupyterHub.hub_ip = '0.0.0.0'

# Port to listen on
c.JupyterHub.hub_port = 8000

# Whether to allow signup
c.JupyterHub.allow_signup = True

# Set a timeout for idle servers
c.JupyterHub.shutdown_on_logout = False
c.JupyterHub.last_activity_interval = 300
c.JupyterHub.activity_resolution = 60
```

### Authenticator Configuration

JH-Lite uses local authentication by default. To customize:

```python
# Basic local authenticator
c.JupyterHub.authenticator_class = 'jupyterhub.auth.LocalAuthenticator'
c.LocalAuthenticator.create_system_users = True

# Or for PAM authentication
c.JupyterHub.authenticator_class = 'jupyterhub.auth.PAMAuthenticator'
```

For more advanced authentication options, use OAuthenticator to support OAuth with popular service providers in [JupyterHub OAuthenticator section](https://jupyterhub.readthedocs.io/en/latest/tutorial/getting-started/authenticators-users-basics.html).

### Docker Spawner Configuration

The Docker Spawner creates containers for users:

```python
# Set Docker Spawner
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# Default Docker image
c.DockerSpawner.image = os.environ.get('DOCKER_NOTEBOOK_IMAGE', 'jupyter/minimal-notebook:latest')

# Network name
c.DockerSpawner.network_name = os.environ.get('DOCKER_NETWORK_NAME', 'jupyterhub-network')

# Allow users to choose an image
c.DockerSpawner.allowed_images = {
    'jupyter/minimal-notebook:latest': 'Minimal Notebook',
    'jupyter/scipy-notebook:latest': 'SciPy Notebook',
    'jupyter/datascience-notebook:latest': 'Data Science Notebook'
}
```

### Volume Configuration

Configure how user data is stored:

```python
notebook_dir = '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir

# Define pre-spawn hook for volume mounting
def customize_volumes(spawner):
    username = spawner.user.name
    # Mount user-specific directory
    spawner.volumes[f'/srv/jupyterhub/data/{username}'] = {'bind': notebook_dir, 'mode': 'rw'}
    
    # For shared datasets (read-only)
    spawner.volumes['/path/to/datasets'] = {'bind': '/home/jovyan/datasets', 'mode': 'ro'}
    
    # Set permissions
    spawner.extra_create_kwargs['user'] = 'root'
    spawner.environment['NB_UID'] = '1000'
    spawner.environment['NB_GID'] = '100'
    spawner.environment['CHOWN_HOME'] = 'yes'
    spawner.environment['CHOWN_HOME_OPTS'] = '-R'
    spawner.environment['CHOWN_EXTRA'] = f'{notebook_dir}'
    spawner.environment['CHOWN_EXTRA_OPTS'] = '-R'

c.DockerSpawner.pre_spawn_hook = customize_volumes
```

### Resource Limits

Set resource limits for user containers:

```python
# Memory limits
c.DockerSpawner.mem_limit = '2G'

# CPU limits
c.DockerSpawner.cpu_limit = 2
c.DockerSpawner.cpu_guarantee = 1

# Disk space limits
c.DockerSpawner.extra_host_config = {
    "storage_opt": {
        "size": '10G'
    }
}
```

## Docker Compose Configuration

The `docker-compose.yml` file defines the Docker services, networks, and volumes for JH-Lite.

### Basic Service Configuration

```yaml
services:
  jupyterhub:
    build: .
    container_name: jupyterhub
    restart: unless-stopped
    ports:
      - "8000:8000"  # HTTP
      - "8443:8443"  # HTTPS
    volumes:
      - jupyterhub-data:/data
      - ./jupyterhub-system-data:/srv/jupyterhub
      - jupyterhub-user-data:/srv/jupyterhub/data
      - /var/run/docker.sock:/var/run/docker.sock
      - ./ssl:/srv/jupyterhub/ssl
    environment:
      - DOCKER_NETWORK_NAME=jupyterhub-network
      - DOCKER_NOTEBOOK_IMAGE=jupyter/minimal-notebook:latest
      - DOCKER_NOTEBOOK_DIR=/home/jovyan/work
      - JUPYTERHUB_SSL_KEY=/srv/jupyterhub/ssl/jupyterhub.key
      - JUPYTERHUB_SSL_CERT=/srv/jupyterhub/ssl/jupyterhub.crt
    networks:
      - jupyterhub-network

networks:
  jupyterhub-network:
    name: jupyterhub-network

volumes:
  jupyterhub-data:
  jupyterhub-user-data:
```

### Custom Port Configuration

To change the ports JH-Lite listens on:

```yaml
services:
  jupyterhub:
    ports:
      - "8888:8000"  # Change HTTP port to 8888
      - "9443:8443"  # Change HTTPS port to 9443
```

Update the corresponding settings in `jupyterhub_config.py`:

```python
c.JupyterHub.port = 8888  # For HTTP
# Or for HTTPS
c.JupyterHub.port = 9443
c.JupyterHub.ssl_key = '/srv/jupyterhub/ssl/jupyterhub.key'
c.JupyterHub.ssl_cert = '/srv/jupyterhub/ssl/jupyterhub.crt'
```

### Adding Datasets

To make datasets available to notebooks:

```yaml
services:
  jupyterhub:
    volumes:
      # Existing volumes...
      - ./datasets:/srv/jupyterhub/datasets
```

Then update `jupyterhub_config.py` to mount the datasets in user containers:

```python
def customize_volumes(spawner):
    # Existing customization...
    
    # Add datasets
    spawner.volumes['/srv/jupyterhub/datasets'] = {'bind': '/home/jovyan/datasets', 'mode': 'ro'}
```

## Further Resources

- [JupyterHub Configuration Reference](https://jupyterhub.readthedocs.io/en/stable/reference/config-reference.html)
- [DockerSpawner Documentation](https://jupyterhub-dockerspawner.readthedocs.io/en/latest/api/index.html)
- [JupyterHub Authentication Guide](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html)