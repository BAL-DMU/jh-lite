import os
import sys
from dockerspawner import DockerSpawner
from nativeauthenticator import NativeAuthenticator

print("Loading custom jupyterhub_config.py...", file=sys.stderr)

#------------------------------------------------------------------------------
# JupyterHub Configuration
#------------------------------------------------------------------------------
c = get_config()

#------------------------------------------------------------------------------
# Authentication Configuration
#------------------------------------------------------------------------------
# Authentication settings - use NativeAuthenticator
c.JupyterHub.authenticator_class = NativeAuthenticator

# Admin users - read from environment
admin_users = os.environ.get('JUPYTERHUB_ADMIN', 'admin')
c.Authenticator.admin_users = set(admin_users.split(','))

# Allow the admin user to log in
c.Authenticator.allowed_users = set(admin_users.split(','))

# Set up NativeAuthenticator options
c.NativeAuthenticator.enable_signup = True
c.NativeAuthenticator.open_signup = True

#------------------------------------------------------------------------------
# Spawner Configuration
#------------------------------------------------------------------------------
# Use DockerSpawner to spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = DockerSpawner

# Get the Docker image from environment or use default
default_image = os.environ.get('DOCKER_NOTEBOOK_IMAGE', 'jupyter/base-notebook:latest')

# Notebook directory location inside container
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR', '/home/jovyan/work')
c.DockerSpawner.notebook_dir = notebook_dir

# Docker network settings
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.remove = True  # Remove containers once they are stopped

# Debug and timeout settings
c.DockerSpawner.debug = True
c.DockerSpawner.http_timeout = 300
c.DockerSpawner.start_timeout = 300
c.DockerSpawner.spawn_timeout = 60

#------------------------------------------------------------------------------
# Volume Mount Configuration
#------------------------------------------------------------------------------
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
def customize_volumes(spawner):
    username = spawner.user.name
    # Mount data directory - adjust the paths as needed for your local setup
    spawner.volumes[f'/srv/jupyterhub/data/{username}'] = {'bind': notebook_dir, 'mode': 'rw'}
    
    # Set the user to run as the jovyan user, but allow them to create files as root
    # This is needed to prevent permission issues
    spawner.extra_create_kwargs['user'] = 'root'
    
    # Use environment variables to ensure proper permissions for data folders
    spawner.environment['NB_UID'] = '1000'  # Default jovyan user ID
    spawner.environment['NB_GID'] = '100'   # Default users group ID
    spawner.environment['CHOWN_HOME'] = 'yes'
    spawner.environment['CHOWN_HOME_OPTS'] = '-R'
    spawner.environment['CHOWN_EXTRA'] = f'{notebook_dir}'
    spawner.environment['CHOWN_EXTRA_OPTS'] = '-R'

#------------------------------------------------------------------------------
# Launcher UI and Image Selection
#------------------------------------------------------------------------------
# Define the options form for image selection
def get_options_form(spawner):
    # Hardcoded list of available Docker images
    available_images = [
        ('jupyter/base-notebook:latest', 'Base Notebook - Minimal Jupyter image'),
        ('jupyter/minimal-notebook:latest', 'Minimal Notebook - Python with Jupyter'),
        ('jupyter/scipy-notebook:latest', 'SciPy Notebook - Scientific Python stack')
    ]
    
    # Create dropdown options from available images
    option_html = ""
    for image_value, image_name in available_images:
        selected = "selected" if image_value == default_image else ""
        option_html += f'<option value="{image_value}" {selected}>{image_name}</option>\n'
    
    # Create the form with styling similar to the reference implementation
    return f"""
    <fieldset>
        <div class="form-group" id="dockerImageSelection">
            <h3>Select a Docker Image</h3>
            <select name="docker_image" id="docker_image" class="form-control">
                <option value="">Select a Docker image</option>
                {option_html}
            </select>
            
            <div class="custom-image-input">
                <input type="text" name="customImage" id="customImage" class="custom-input-field" 
                    placeholder="Or enter a custom Docker image (e.g., jupyter/datascience-notebook:latest)">
            </div>
            
            <div id="imageDetails" class="image-details" style="display: none;"></div>
        </div>
    </fieldset>
    
    <style>
        .form-group {{
            margin-bottom: 15px;
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        select {{
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }}
        .custom-image-input {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .custom-input-field {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }}
        .image-details {{
            margin-top: 20px;
            padding: 15px;
            background-color: #fff;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
    </style>
    
    <script>
        // Add event listeners once the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', function() {{
            const selectElement = document.getElementById('docker_image');
            const customImageInput = document.getElementById('customImage');
            const detailsElement = document.getElementById('imageDetails');
            
            // Event listener for docker image selection
            selectElement.addEventListener('change', function(e) {{
                if (e.target.value) {{
                    // Clear custom image input when dropdown is used
                    customImageInput.value = '';
                    
                    // Display image details
                    const imageParts = e.target.value.split(':');
                    detailsElement.style.display = 'block';
                    detailsElement.innerHTML = `
                        <h3>Image Details</h3>
                        <p><strong>Repository:</strong> ${{imageParts[0]}}</p>
                        <p><strong>Tag:</strong> ${{imageParts[1] || 'latest'}}</p>
                    `;
                }} else {{
                    detailsElement.style.display = 'none';
                }}
            }});
            
            // Event listener for custom image input
            customImageInput.addEventListener('input', function(e) {{
                if (e.target.value.trim()) {{
                    // Clear dropdown selection
                    selectElement.value = '';
                    
                    // Show details for custom image
                    const imageParts = e.target.value.trim().split(':');
                    detailsElement.style.display = 'block';
                    detailsElement.innerHTML = `
                        <h3>Custom Image Details</h3>
                        <p><strong>Repository:</strong> ${{imageParts[0]}}</p>
                        <p><strong>Tag:</strong> ${{imageParts[1] || 'latest'}}</p>
                    `;
                }} else {{
                    detailsElement.style.display = 'none';
                }}
            }});
        }});
    </script>
    """

# Set the options form
c.DockerSpawner.options_form = get_options_form

# Handle form submission
def options_from_form(form_data):
    options = {}
    
    # First check if a custom image was provided
    if 'customImage' in form_data and form_data['customImage'][0]:
        options['docker_image'] = form_data['customImage'][0]
    # Then check if a predefined image was selected
    elif 'docker_image' in form_data and form_data['docker_image'][0]:
        options['docker_image'] = form_data['docker_image'][0]
    # Otherwise use the default image
    else:
        options['docker_image'] = default_image
    
    return options

c.DockerSpawner.options_from_form = options_from_form

#------------------------------------------------------------------------------
# Spawner Hooks
#------------------------------------------------------------------------------
# Use selected image when spawning
def pre_spawn_hook(spawner):
    # First run the existing volume customization
    customize_volumes(spawner)
    
    # Then set the image based on user selection
    if 'docker_image' in spawner.user_options:
        spawner.image = spawner.user_options['docker_image']
        spawner.log.info(f"Using user-selected image: {spawner.image}")
    else:
        spawner.image = default_image
        spawner.log.info(f"Using default image: {spawner.image}")

c.DockerSpawner.pre_spawn_hook = pre_spawn_hook

#------------------------------------------------------------------------------
# Server Configuration
#------------------------------------------------------------------------------
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8081
c.JupyterHub.port = 8000

# Server behavior settings
c.JupyterHub.cleanup_servers = False
c.JupyterHub.allow_named_servers = True

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = '/data/jupyterhub_cookie_secret'
c.JupyterHub.db_url = 'sqlite:////data/jupyterhub.sqlite'

#------------------------------------------------------------------------------
# HTTPS Configuration
#------------------------------------------------------------------------------
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