# Copyright (c) 2025, Balgrist University Clinic, Digital Medicine Unit.
# Distributed under the terms of the Modified BSD License.

ARG JUPYTERHUB_VERSION=latest
FROM jupyterhub/jupyterhub:${JUPYTERHUB_VERSION}

# Install dependencies and tools
RUN apt-get update && apt-get install -y \
    vim \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN python3 -m pip install --no-cache-dir \
    dockerspawner \
    jupyterhub-nativeauthenticator \
    pyyaml \
    bcrypt \
    && python3 -m pip install --no-cache-dir git+https://github.com/yuvipanda/jupyterhub-ssh.git

WORKDIR /srv/jupyterhub

# Command to run when container starts
CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
