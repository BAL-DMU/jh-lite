# Server Requirements

This document outlines the hardware and software requirements for hosting JH-Lite, both on a local machine for development purposes and on a dedicated server for more robust deployments.

## Local Development Environment

For testing and development on your local machine, JH-Lite requires:

| Resource         | Minimum Requirement     | Recommended           |
|------------------|-------------------------|----------------------|
| **CPU**          | 2 cores                 | 4+ cores             |
| **Memory**       | 4 GB RAM                | 8+ GB RAM            |
| **Disk Space**   | 5 GB free space         | 10+ GB free space    |
| **Docker**       | Docker Engine 19.03+    | Latest stable release|
| **Docker Compose**| v1.27.0+               | Latest stable release|
| **Network**      | Local port 8000 or 8443 available | Local port 8000 or 8443 available |
| **OS**           | Any OS supporting Docker | Linux, macOS, or Windows 10+ |

## Production Server Requirements

For a more robust deployment on a dedicated server, we recommend the following specifications based on the [JupyterHub documentation](https://tljh.jupyter.org/en/latest/install/custom-server.html):

### Minimum Requirements

| Resource         | Minimum Requirement          | Example (OK Server)        |
|------------------|------------------------------|----------------------------|
| **CPU**          | 2 cores or more              | 8 cores                    | 
| **Memory**       | ≥ 4 GB RAM                   | 16 GB                      | 
| **Disk**         | ≥ 10 GB total storage        | 10.0 GB                    | 
| **Swap**         | Optional (≥ 1 GB recommended)| 1.0 GB                     |
| **Architecture** | x86_64                       | x86_64                     |
| **OS**           | Ubuntu 20.04+                | Ubuntu 22.04               |
| **IP Address**   | Public or routed IP          | Public or routed IP        |
| **Network**      | SSH accessible, HTTP ready   | SSH accessible, HTTP ready | 

### Recommended Production Configuration

For small to medium-sized groups with moderate resource demands (e.g., data analysis, light ML training, Python notebooks), we recommend the following production-ready configuration:

- **CPU**: 8 cores  
- **RAM**: 32 GB  
- **Disk**: 20 GB SSD  
- **Swap**: 2 GB  
- **Ubuntu**: 22.04 LTS  
- **IP**: Public IPv4 accessible from user network  
- **Network**: Configured firewall for HTTP, HTTPS, and custom JupyterHub ports
- **NAS**: Configure and mount NAS share volumes on the target servers

## GPU Support Requirements

If you plan to use GPU-accelerated containers:

1. **Hardware**: NVIDIA GPU compatible with CUDA
2. **Drivers**: NVIDIA GPU drivers installed on the host
3. **Software**: NVIDIA Container Toolkit (nvidia-docker2) installed
4. **Docker**: Docker configured to use the NVIDIA runtime

You can verify your GPU setup with:

```bash
nvidia-smi  # Should display GPU information
docker run --gpus all nvidia/cuda:11.0-base nvidia-smi  # Should display GPU info from container
```

## SSL Certificate Requirements

For HTTPS support:

- OpenSSL installed (for generating self-signed certificates)
- For production: Valid SSL certificate from a trusted Certificate Authority

## Additional Considerations

When planning your JH-Lite deployment, consider:

- **User load**: Each concurrent user may require 0.5-2 GB of RAM depending on workload
- **Storage needs**: Data-intensive work may require additional storage capacity
- **Backup strategy**: Plan for regular backups of user data
- **Network bandwidth**: Sufficient for the expected number of concurrent users
- **Security**: Firewall rules, user authentication, and access controls
