# Integrating Jupyter Docker Stacks

This guide explains how to integrate [Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/) with JH-Lite, allowing users to select from pre-configured Docker images when launching their notebook environments.

## What are Jupyter Docker Stacks?

Jupyter Docker Stacks is a collection of ready-to-run Docker images containing Jupyter applications and interactive computing tools. These stacks provide:

- Pre-configured environments for different use cases
- Consistent and reproducible setups
- Various scientific and data analysis packages
- Different programming language kernels

## Benefits of Integration

By integrating Jupyter Docker Stacks with JH-Lite, you can:

- Offer users a variety of pre-configured computational environments
- Standardize development environments across users
- Provide specialized toolsets for different types of analysis
- Allow easy switching between environments without losing user data

## Implementation Steps

### 1. Downloading Docker Images

First, pull the desired Jupyter Docker Stack images:

```bash
# Pull the minimal-notebook image
docker pull jupyter/minimal-notebook:latest

# Pull the scipy-notebook image
docker pull jupyter/scipy-notebook:latest

# Optional: Pull additional stack images
docker pull jupyter/datascience-notebook:latest
docker pull jupyter/tensorflow-notebook:latest
docker pull jupyter/r-notebook:latest
```

Verify the images were downloaded correctly:

```bash
docker images | grep jupyter
```

### 2. Configuring JupyterHub

Update the `jupyterhub_config.py` file to include the desired Docker Stack images in the available options:

```python
available_images = [
    ('jupyter/minimal-notebook:latest', 'Minimal: Python with Jupyter'),
    ('jupyter/scipy-notebook:latest', 'SciPy: Scientific Python stack (NumPy, Pandas, Matplotlib)'),
    ('jupyter/datascience-notebook:latest', 'Data Science: SciPy with R, Julia'),
    ('jupyter/tensorflow-notebook:latest', 'TensorFlow: Deep Learning framework'),
    ('jupyter/r-notebook:latest', 'R: Statistics and data analysis in R')
]
```

Ensure the Docker Spawner is configured correctly:

```python
# DockerSpawner configuration
c.JupyterHub.spawner_class = DockerSpawner
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']

# Pre-spawn hook to set the image
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
```

### 3. Restart JupyterHub

After updating the configuration, restart JupyterHub:

```bash
docker-compose down
docker-compose up -d
```

## Creating Custom Docker Images

### Basic Custom Image

If you need to customize the Docker images with additional packages, create a `Dockerfile`:

```Dockerfile
# Example: Custom image based on scipy-notebook
FROM jupyter/scipy-notebook:latest

# Switch to root for package installation
USER root

# Install additional packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install additional Python packages
RUN pip install --no-cache-dir \
    opencv-python-headless \
    plotly \
    dash

# Switch back to the jovyan user
USER ${NB_UID}
```

Build the custom image:

```bash
docker build -t myorganization/custom-scipy-notebook:latest .
```

Add it to the available images in `jupyterhub_config.py`:

```python
available_images = [
    # Existing images...
    ('myorganization/custom-scipy-notebook:latest', 'Custom SciPy: SciPy with additional tools')
]
```

### PyTorch Notebook with CUDA Support

To create a PyTorch notebook with CUDA support:

```Dockerfile
# Use scipy-notebook as the base
FROM jupyter/scipy-notebook:latest

LABEL maintainer="Your Name <your.email@example.com>"

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir --extra-index-url=https://pypi.nvidia.com --index-url "https://download.pytorch.org/whl/cu118" \
    torch \
    torchaudio \
    torchvision && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Set NVIDIA environment variables
ENV NVIDIA_VISIBLE_DEVICES="all" \
    NVIDIA_DRIVER_CAPABILITIES="compute,utility"

# Add the nvidia-smi binary to PATH
ENV PATH="${PATH}:/usr/local/nvidia/bin" \
    LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/nvidia/lib64"
```

Build the image:

```bash
docker build -t myorganization/pytorch-notebook-cuda:latest .
```

Add it to the available images in `jupyterhub_config.py`:

```python
available_images = [
    # Existing images...
    ('myorganization/pytorch-notebook-cuda:latest', 'PyTorch: GPU-accelerated PyTorch')
]
```

## Available Default Images

The Jupyter Docker Stacks project provides these commonly used images:

| Image Name | Description | Key Packages |
|------------|-------------|-------------|
| `jupyter/base-notebook` | Minimal Jupyter Notebook | Jupyter Notebook, JupyterLab |
| `jupyter/minimal-notebook` | Minimal with additional packages | git, nano, tzdata |
| `jupyter/scipy-notebook` | Scientific computing | NumPy, Pandas, Matplotlib, scipy |
| `jupyter/r-notebook` | R programming | R kernel, tidyverse |
| `jupyter/tensorflow-notebook` | Machine learning | TensorFlow, scikit-learn |
| `jupyter/datascience-notebook` | Data science tools | Python, R, and Julia |
| `jupyter/pyspark-notebook` | Big data processing | Apache Spark, PySpark |
| `jupyter/all-spark-notebook` | Spark with all kernels | PySpark, SparkR, Toree |

## Image Management

### Updating Images

Regularly update your Docker images to get security patches and new features:

```bash
# Pull the latest versions
docker pull jupyter/minimal-notebook:latest
docker pull jupyter/scipy-notebook:latest
# Pull other images as needed

# Restart JupyterHub to use the updated images
docker-compose restart
```

### Using Specific Versions

For production environments, consider using specific version tags instead of `latest`:

```python
available_images = [
    ('jupyter/minimal-notebook:python-3.10', 'Minimal: Python 3.10'),
    ('jupyter/scipy-notebook:ubuntu-22.04', 'SciPy: Ubuntu 22.04'),
    # Other specific versions
]
```

## Testing Environments

After setting up the Docker Stacks, users can verify their environments:

1. Log in to JupyterHub
2. Select an image from the dropdown menu
3. Start the server
4. Run these commands to check the environment:

```python
# Check installed Python packages
!pip list

# Check available kernels
!jupyter kernelspec list

# Check system information
!cat /etc/os-release
```

## Additional Resources

- [Jupyter Docker Stacks Documentation](https://jupyter-docker-stacks.readthedocs.io/)
- [DockerSpawner Documentation](https://jupyterhub-dockerspawner.readthedocs.io/)
- [JupyterHub Documentation](https://jupyterhub.readthedocs.io/)
