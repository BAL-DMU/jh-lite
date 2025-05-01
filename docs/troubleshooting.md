# Troubleshooting Guide

This guide addresses common issues you might encounter when using JH-Lite and provides solutions to resolve them.

## Viewing Logs

Before troubleshooting any specific issue, check the logs:

```bash
# View all logs
docker-compose logs -f

# View only JupyterHub logs
docker-compose logs -f jupyterhub

# Filter logs for specific content
docker-compose logs | grep "error"
```

## Authentication Issues

### Cannot Log In

If you're unable to log in to JupyterHub:

1. **Admin User Not Created**
   - Verify you've created an admin user:
      ```bash
      docker exec -it jupyterhub python /srv/jupyterhub/create-admin.py admin yourpassword
      ```
   - Check for success message confirming user creation

2. **Incorrect Credentials**
   - Make sure you're using the correct username and password
   - Passwords are case-sensitive

3. **Cookie Issues**
   - Clear browser cookies and cache
   - Try a different browser
   - Check if HTTPS is configured correctly

4. **Authentication Database Issues**
   - Check the authentication database:
     ```bash
     docker exec -it jupyterhub sqlite3 /data/jupyterhub.sqlite "SELECT * FROM users;"
     ```

### "No such user" Error

If you receive a "No such user" error:

1. Check if the user exists in the database:
   ```bash
   docker exec -it jupyterhub sqlite3 /data/jupyterhub.sqlite "SELECT * FROM users WHERE name='username';"
   ```

2. Try recreating the user:
   ```bash
   docker exec -it jupyterhub python /srv/jupyterhub/create-admin.py username password
   ```

## Container Issues

### Container Won't Start

If user containers fail to start:

1. **Check Docker Service**
   - Verify Docker is running:
     ```bash
     docker info
     ```
   - Restart Docker if necessary

2. **Check Network Issues**
   - Verify Docker network exists:
     ```bash
     docker network ls | grep jupyterhub-network
     ```
   - Recreate network if needed:
     ```bash
     docker network create jupyterhub-network
     ```

3. **Resource Limitations**
   - Check if the host has enough resources:
     ```bash
     free -h  # Check RAM
     df -h    # Check disk space
     ```
   - Close unnecessary applications to free up resources

4. **Image Issues**
   - Verify that the selected Docker image exists:
     ```bash
     docker images | grep jupyter
     ```
   - Pull the image manually if it's missing:
     ```bash
     docker pull jupyter/minimal-notebook:latest
     ```

### "Permission Denied" Errors

If users encounter permission errors:

1. **Volume Permissions**
   - Check and fix permissions on the host:
     ```bash
     # Find the volume location
     docker volume inspect jupyterhub-user-data
     
     # Fix permissions (adjust paths as needed)
     sudo chmod -R 777 /var/lib/docker/volumes/jupyterhub-user-data/_data
     ```

2. **Configuration Issue**
   - Verify the `customize_volumes` function in `jupyterhub_config.py` sets the correct permissions
   - Ensure environment variables for permissions are set correctly:
     ```python
     spawner.environment['NB_UID'] = '1000'  # jovyan user ID
     spawner.environment['NB_GID'] = '100'   # users group ID
     spawner.environment['CHOWN_HOME'] = 'yes'
     ```

## Network and Connection Issues

### Cannot Access JupyterHub

If you cannot access JupyterHub:

1. **Port Conflicts**
   - Check if something else is using the same port:
     ```bash
     # For Linux/macOS
     sudo lsof -i :8000
     # For Windows
     netstat -ano | findstr :8000
     ```
   - Change the port in `docker-compose.yml` if needed

2. **Firewall Issues**
   - Check if firewall is blocking the connection
   - Allow the JupyterHub port:
     ```bash
     # For Ubuntu/Debian
     sudo ufw allow 8000/tcp
     # For Windows
     netsh advfirewall firewall add rule name="JupyterHub" dir=in action=allow protocol=TCP localport=8000
     ```

3. **Docker Network Issues**
   - Restart Docker to reset networking:
     ```bash
     # Linux
     sudo systemctl restart docker
     # Windows
     Restart Docker Desktop
     ```

### SSL/HTTPS Issues

If you're having trouble with HTTPS:

1. **Certificate Issues**
   - Regenerate certificates:
     ```bash
     sh generate-certificates.sh  # Linux/macOS
     PowerShell -ExecutionPolicy Bypass -File .\generate-certificates.ps1  # Windows
     ```

2. **SSL Configuration**
   - Verify SSL settings in `docker-compose.yml`:
     ```yaml
     environment:
       - JUPYTERHUB_SSL_KEY=/srv/jupyterhub/ssl/jupyterhub.key
       - JUPYTERHUB_SSL_CERT=/srv/jupyterhub/ssl/jupyterhub.crt
     ```
   - Check volume mounts for SSL files

3. **Browser Trust Issues**
   - Add exception for self-signed certificate in your browser
   - For production, use a trusted SSL certificate

## Volume and Storage Issues

### Missing Files or Data

If user files or notebooks are missing:

1. **Volume Mounting**
   - Check volume mounts in `docker-compose.yml`
   - Verify the volumes exist:
     ```bash
     docker volume ls | grep jupyterhub
     ```

2. **Data Location**
   - Check where the data is stored:
     ```bash
     docker volume inspect jupyterhub-user-data
     ```
   - Look at the actual files to verify their existence

3. **Container Restart**
   - Sometimes a simple container restart resolves the issue:
     ```bash
     docker-compose restart
     ```

### Disk Space Issues

If you're running out of disk space:

1. **Clean up Docker**
   - Remove unused containers:
     ```bash
     docker container prune
     ```
   - Remove unused images:
     ```bash
     docker image prune
     ```

2. **Check Volume Usage**
   - Examine volume size:
     ```bash
     du -sh /var/lib/docker/volumes/jupyterhub-user-data/_data
     ```

3. **Implement Quotas**
   - Consider implementing user disk quotas in `jupyterhub_config.py`

## Performance Issues

### Slow Notebook Performance

If notebooks are running slowly:

1. **Resource Limits**
   - Check if containers have enough resources:
     ```python
     # In jupyterhub_config.py
     c.DockerSpawner.extra_host_config = {
         'mem_limit': '4g',
         'cpu_quota': 100000  # 100% of one CPU
     }
     ```

2. **Network Performance**
   - Check if the Docker network is performing well
   - Consider switching to host networking for better performance

3. **Disk I/O**
   - Check if disk I/O is a bottleneck
   - Consider using SSD storage for improved performance

## Resetting JH-Lite

If you want to start fresh:

### Soft Reset (Preserves User Data)

```bash
# Stop and remove containers
docker-compose down

# Start fresh containers
docker-compose up -d --build
```

### Hard Reset (Removes All Data)

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Remove dangling volumes
docker volume prune

# Start fresh installation
docker-compose up -d --build
```

## Getting Additional Help

If you're still experiencing issues:

1. Check the [JupyterHub documentation](https://jupyterhub.readthedocs.io/)
2. Check the [DockerSpawner documentation](https://jupyterhub-dockerspawner.readthedocs.io/)
3. File an issue on the GitHub repository
4. Join the Jupyter community on [Discourse](https://discourse.jupyter.org/) or [Gitter](https://gitter.im/jupyterhub/jupyterhub)
