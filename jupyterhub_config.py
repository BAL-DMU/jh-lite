import os
import sys
from dockerspawner import DockerSpawner
from nativeauthenticator import NativeAuthenticator

print("Loading custom jupyterhub_config.py...", file=sys.stderr)

c = get_config()

# Authentication settings - define this FIRST to ensure it's properly loaded
c.JupyterHub.authenticator_class = NativeAuthenticator

# Admin users - read from environment
admin_users = os.environ.get('JUPYTERHUB_ADMIN', 'admin')
c.Authenticator.admin_users = set(admin_users.split(','))

# Allow the admin user to log in
c.Authenticator.allowed_users = set(admin_users.split(','))

# Set up NativeAuthenticator options
c.NativeAuthenticator.enable_signup = True
c.NativeAuthenticator.open_signup = True

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = DockerSpawner
c.DockerSpawner.image = os.environ['DOCKER_NOTEBOOK_IMAGE']
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8081
c.JupyterHub.port = 8000

# HTTPS Configuration - uncomment to enable
# If environment variables for SSL cert/key are set, enable HTTPS
ssl_cert = os.environ.get('JUPYTERHUB_SSL_CERT')
ssl_key = os.environ.get('JUPYTERHUB_SSL_KEY')
if ssl_cert and ssl_key and os.path.exists(ssl_cert) and os.path.exists(ssl_key):
    c.JupyterHub.ssl_cert = ssl_cert
    c.JupyterHub.ssl_key = ssl_key
    c.JupyterHub.port = 8443
    
    # Set proper public facing URL with hostname
    c.JupyterHub.bind_url = 'https://localhost:8443'
    print(f"HTTPS enabled with provided certificates at {c.JupyterHub.bind_url}", file=sys.stderr)
else:
    # Set proper public facing URL with hostname
    c.JupyterHub.bind_url = 'http://localhost:8000'
    print(f"WARNING: Running without HTTPS at {c.JupyterHub.bind_url}. Set JUPYTERHUB_SSL_CERT and JUPYTERHUB_SSL_KEY environment variables and provide certificates to enable HTTPS.", file=sys.stderr)

c.JupyterHub.cleanup_servers = False
c.JupyterHub.allow_named_servers = True

# Notebook directory
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR', '/home/jovyan/work')
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
def customize_volumes(spawner):
    username = spawner.user.name
    # Mount data directory - adjust the paths as needed for your local setup
    spawner.volumes[f'/srv/jupyterhub/data/{username}'] = {'bind': notebook_dir, 'mode': 'rw'}

c.DockerSpawner.pre_spawn_hook = customize_volumes

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = '/data/jupyterhub_cookie_secret'
c.JupyterHub.db_url = 'sqlite:////data/jupyterhub.sqlite'

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# Set reasonable timeouts for spawning
c.DockerSpawner.http_timeout = 300
c.DockerSpawner.start_timeout = 300
c.DockerSpawner.spawn_timeout = 60