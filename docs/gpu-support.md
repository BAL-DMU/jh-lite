# GPU Acceleration Support

This guide explains how to enable GPU acceleration for CUDA-enabled Docker images in JH-Lite. GPU acceleration allows users to leverage the computational power of NVIDIA GPUs for tasks such as deep learning, scientific computing, and data processing.

## Prerequisites

Before enabling GPU support in JH-Lite, ensure your system meets these requirements:

1. **Hardware**:
   - NVIDIA GPU compatible with CUDA
   - Sufficient power and cooling for GPU workloads

2. **Host Requirements**:
   - NVIDIA GPU drivers installed on the host system
   - NVIDIA Container Toolkit (nvidia-docker2) installed
   - Docker configured to use the NVIDIA runtime

3. **Software**:
   - Docker 19.03+ (which includes integrated NVIDIA GPU support)
   - Docker Compose 1.28.0+ (for GPU support in compose files)

## Verifying GPU Setup

Before configuring JH-Lite, verify your GPU setup:

```bash
# Check for NVIDIA drivers
nvidia-smi

# Verify Docker can access GPUs
docker run --gpus all nvidia/cuda:11.0-base nvidia-smi
```

Both commands should display information about your GPU(s). If either fails, you need to resolve those issues before proceeding.

## Configuring JH-Lite for GPU Support

JH-Lite can automatically detect images with CUDA support (containing "cuda" or "gpu" in their name) and configure them to use available GPUs.

### Update jupyterhub_config.py

Add or modify the `pre_spawn_hook` function in your `jupyterhub_config.py`:

```python
def pre_spawn_hook(spawner):
    # First run the existing volume customization
    customize_volumes(spawner)
    
    # Then set the image based on user selection
    if 'docker_image' in spawner.user_options:
        spawner.image = spawner.user_options['docker_image']
        spawner.log.info(f"Using user-selected image: {spawner.image}")
        
        # Enable GPU for CUDA/GPU images
        if 'cuda' in spawner.image.lower() or 'gpu' in spawner.image.lower():
            spawner.log.info(f"Enabling GPU access for image: {spawner.image}")
            # Add GPU configuration for Docker
            spawner.extra_host_config = {
                'device_requests': [
                    {'Driver': 'nvidia', 'Count': -1, 'Capabilities': [['gpu', 'compute', 'utility']]}
                ]
            }
    else:
        spawner.image = default_image
        spawner.log.info(f"Using default image: {spawner.image}")

c.DockerSpawner.pre_spawn_hook = pre_spawn_hook
```

This configuration:
- Automatically detects images with "cuda" or "gpu" in their name
- Configures them to use all available GPUs on the host
- Provides necessary capabilities for compute workloads

### GPU-Enabled Docker Images

Add GPU-enabled images to your available options in `jupyterhub_config.py`:

```python
available_images = [
    # Existing images...
    ('jupyter/pytorch-notebook-cuda12:latest', 'PyTorch with CUDA 12 - GPU-accelerated PyTorch'),
    ('jupyter/tensorflow-notebook-gpu:latest', 'TensorFlow with GPU - GPU-accelerated TensorFlow')
]
```

### Building Custom GPU-Enabled Images

To create a custom PyTorch notebook with CUDA 12 support:

```Dockerfile
# Use scipy-notebook as the base
FROM jupyter/scipy-notebook:latest

LABEL maintainer="Your Name <your.email@example.com>"

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir --extra-index-url=https://pypi.nvidia.com --index-url "https://download.pytorch.org/whl/cu121" \
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
docker build -t myorganization/pytorch-notebook-cuda12:latest .
```

## Verifying GPU Availability in Notebooks

Users can verify GPU access inside their notebooks by running:

```python
# For PyTorch
import torch
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)
print("GPU count:", torch.cuda.device_count())
print("GPU name:", torch.cuda.get_device_name(0))

# For TensorFlow
import tensorflow as tf
print("GPU available:", tf.config.list_physical_devices('GPU'))

# Command line check
!nvidia-smi
```

## GPU Resource Allocation

### Default Configuration

The default configuration provides full access to all available GPUs. For multi-user environments, consider implementing resource limits.

### Limiting GPU Memory

To limit GPU memory per user (e.g., 4GB):

```python
spawner.extra_host_config = {
    'device_requests': [
        {'Driver': 'nvidia', 'Count': -1, 'Capabilities': [['gpu', 'compute', 'utility']]},
    ],
    'environment': [
        'NVIDIA_VISIBLE_DEVICES=all',
        'TF_MEMORY_ALLOCATION=4GB',  # For TensorFlow
        'PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:4096'  # For PyTorch, ~4GB
    ]
}
```

### Limiting GPU Device Access

To restrict access to specific GPUs:

```python
spawner.extra_host_config = {
    'device_requests': [
        {'Driver': 'nvidia', 'Count': 1, 'Capabilities': [['gpu', 'compute', 'utility']]},
    ],
    'environment': [
        'NVIDIA_VISIBLE_DEVICES=0',  # Only use GPU 0
        'CUDA_VISIBLE_DEVICES=0'     # For frameworks that check this variable
    ]
}
```

## Example GPU Use Cases

### Deep Learning Training

```python
import torch
import torch.nn as nn

# Define a simple model
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
).cuda()  # Move to GPU

# Create some dummy data
inputs = torch.randn(100, 784).cuda()
targets = torch.randint(0, 10, (100,)).cuda()

# Train the model
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

for epoch in range(10):
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")
```

### Data Processing with GPU Acceleration

```python
import cupy as cp  # GPU-accelerated array library (like NumPy)
import numpy as np
import time

# Generate large arrays
size = 10000000
cpu_array = np.random.random(size)
gpu_array = cp.random.random(size)

# Compare performance
start = time.time()
cpu_result = np.sin(cpu_array) + np.cos(cpu_array)
cpu_time = time.time() - start
print(f"CPU time: {cpu_time:.4f} seconds")

start = time.time()
gpu_result = cp.sin(gpu_array) + cp.cos(gpu_array)
gpu_result.get()  # Synchronize to get fair timing
gpu_time = time.time() - start
print(f"GPU time: {gpu_time:.4f} seconds")
print(f"Speedup: {cpu_time/gpu_time:.2f}x")
```

## Troubleshooting GPU Support

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| "CUDA not available" | NVIDIA drivers not properly installed | Reinstall NVIDIA drivers |
| | CUDA libraries missing in container | Verify image has CUDA support |
| "No NVIDIA driver found" | Docker not configured with NVIDIA runtime | Install nvidia-container-toolkit |
| "Out of memory" error | GPU memory exhausted | Limit batch sizes or model size |
| | Multiple users consuming GPU memory | Implement memory limits per user |
| Poor performance | CPU bottleneck in data pipeline | Optimize data loading with GPU acceleration |
| | Inappropriate algorithm for GPU | Use GPU-optimized libraries and algorithms |

## Additional Resources

- [NVIDIA Container Toolkit Documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html)
- [PyTorch CUDA Documentation](https://pytorch.org/docs/stable/notes/cuda.html)
- [TensorFlow GPU Documentation](https://www.tensorflow.org/guide/gpu)
- [RAPIDS (GPU Data Science)](https://rapids.ai/)
