# Docker Spawner Architecture

This document explains the Docker spawner implementation in JH-Lite, focusing on volume configuration and customization options.

## What is DockerSpawner?

DockerSpawner is a JupyterHub component that creates containerized Jupyter notebook environments for each user. Instead of running notebook servers directly on the host machine, DockerSpawner creates isolated Docker containers, providing:

- Better resource isolation
- Customizable environments
- Independent package installations
- Enhanced security through containerization

## Volume Architecture

JH-Lite implements a robust volume architecture to ensure data persistence and proper isolation. The system uses three distinct Docker volumes:

### 1. jupyterhub-data

**Purpose**: Stores JupyterHub's internal persistent data
**Mount Point**: `/data` inside the container
**Contains**:
- SQLite database (`jupyterhub.sqlite`) with user and server state information
- Cookie secrets for authentication
- Other internal runtime data

**Configuration in docker-compose.yml**:
```yaml
volumes:
  - jupyterhub-data:/data
```

### 2. jupyterhub-system-data

**Purpose**: Contains configuration files and system-level components
**Mount Type**: Bind mount (directly links host directory to container)
**Mount Point**: `/srv/jupyterhub` inside the container
**Contains**:
- Configuration files
- System scripts
- Admin tools

**Configuration in docker-compose.yml**:
```yaml
volumes:
  - ./jupyterhub-system-data:/srv/jupyterhub
```

### 3. jupyterhub-user-data

**Purpose**: Stores user notebooks, files, and personal data
**Mount Point**: `/srv/jupyterhub/data` inside the container
**Contains**:
- Individual user directories for notebooks and files
- User-created content that persists between container restarts

**Configuration in docker-compose.yml**:
```yaml
volumes:
  - jupyterhub-user-data:/srv/jupyterhub/data
```

## DockerSpawner Configuration

### Environment Variables

The Docker Spawner can be configured using these environment variables in `docker-compose.yml`:

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `DOCKER_NOTEBOOK_IMAGE` | Default Docker image | `jupyter/base-notebook:latest` |
| `DOCKER_NETWORK_NAME` | Docker network name | `jupyterhub-network` |
| `DOCKER_NOTEBOOK_DIR` | Notebook directory path | `/home/jovyan/work` |

### Volume Mounting Process

When a user starts a notebook server, DockerSpawner:

1. Creates a container from the selected image
2. Mounts a user-specific subdirectory from `jupyterhub-user-data` into the container
3. Applies appropriate permissions using the `root` user and environment variables
4. Maps this mount to the user's working directory inside the container

The relevant code in `jupyterhub_config.py`:

```python
def customize_volumes(spawner):
    username = spawner.user.name
    # Mount data directory with specific user folder
    spawner.volumes[f'/srv/jupyterhub/data/{username}'] = {'bind': notebook_dir, 'mode': 'rw'}
    
    # Set permissions and ownership
    spawner.extra_create_kwargs['user'] = 'root'
    spawner.environment['NB_UID'] = '1000'  # jovyan user ID
    spawner.environment['NB_GID'] = '100'   # users group ID
    spawner.environment['CHOWN_HOME'] = 'yes'
    spawner.environment['CHOWN_HOME_OPTS'] = '-R'
    spawner.environment['CHOWN_EXTRA'] = f'{notebook_dir}'
    spawner.environment['CHOWN_EXTRA_OPTS'] = '-R'
```

## Volume Customization

### Modifying jupyterhub-data

This is a Docker-managed volume. To customize:

1. **Backup**: Use `docker volume inspect jupyterhub-data` to find the location
2. **Modify**: Stop containers, modify data, restart
3. **Recreate**: Use `docker-compose down -v` to remove, then recreate

### Modifying jupyterhub-system-data

As a bind mount, edit files directly in the `./jupyterhub-system-data` directory.

### Modifying jupyterhub-user-data

For direct access on the host:
1. Convert to a bind mount in `docker-compose.yml`:
```yaml
volumes:
  jupyterhub-user-data:
    driver_opts:
      type: none
      device: ./user_data  # Path on host
      o: bind
```
2. Ensure proper permissions on the host directory

## Adding Shared Datasets

To provide read-only access to shared datasets:

```python
def customize_volumes(spawner):
    # Existing volume customization code...
    
    # Add a shared data directory
    spawner.volumes['/path/to/shared/data'] = {'bind': '/home/jovyan/shared', 'mode': 'ro'}
```

## Troubleshooting Volume Issues

| Issue | Solution |
|-------|----------|
| Permission denied | Check volume permissions or modify `customize_volumes()` |
| Missing files | Verify correct volume mounts in docker-compose.yml |
| Bind mount errors | For Windows hosts, use Docker-managed volumes instead of bind mounts |

## Security Considerations

- All volumes contain sensitive data and should be properly secured
- jupyterhub-data contains authentication information
- Regular backups of all volumes are recommended
- Enable proper permissions on bind mounts

## Advanced Configuration

For more advanced configuration options, refer to the [DockerSpawner documentation](https://jupyterhub-dockerspawner.readthedocs.io/).
