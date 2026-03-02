# Docker Deployment Guide

## Overview

The Consent Agent uses Docker for consistent, reproducible deployments across different environments. The Docker setup is based on NVIDIA's official vLLM container with CUDA 13.0 support.

---

## Prerequisites

### 1. Docker Engine
```bash
# Check Docker version
docker --version
# Should be 20.10 or higher
```

Install from: https://docs.docker.com/get-docker/

### 2. NVIDIA Container Toolkit
```bash
# Check if nvidia-docker works
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

Install from: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

### 3. Docker Compose
```bash
# Check Docker Compose version
docker-compose --version
# Should be 2.0 or higher
```

Usually included with Docker Desktop.

---

## Quick Start

### Option 1: Using start.sh (Recommended)

```bash
# Navigate to project directory
cd ~/Desktop/consent-agent

# Make script executable (first time only)
chmod +x start.sh

# Run the agent
./start.sh

# Or rebuild image first
./start.sh --build
```

### Option 2: Using docker-compose directly

```bash
# Build image
docker-compose build

# Run interactive agent
docker-compose up consent-agent

# Run in background
docker-compose up -d consent-agent

# View logs
docker-compose logs -f consent-agent

# Stop
docker-compose down
```

### Option 3: Using docker run

```bash
# Build image
docker build -t consent-agent:week1 .

# Run interactive
docker run --gpus all -it --rm \
  --shm-size=16g \
  -v $(pwd)/models:/workspace/consent-agent/models \
  -v $(pwd)/data:/workspace/consent-agent/data \
  consent-agent:week1
```

---

## Directory Structure

```
consent-agent/
├── Dockerfile              # Image definition
├── docker-compose.yml      # Service orchestration
├── start.sh               # Startup automation
├── .dockerignore          # Files to exclude from image
│
├── app/                   # Application code (mounted as volume)
├── config/                # Configuration (mounted)
├── models/                # AI models (mounted, persistent)
├── data/                  # Session data (mounted, persistent)
└── scripts/               # Utility scripts (mounted)
```

---

## Usage Examples

### Interactive Mode (Default)

```bash
./start.sh

# Inside container, you'll see:
# ============================================================
# INITIALIZING CONSENT AGENT
# ============================================================
# ...
# You (EN): What is a colonoscopy?
```

### Run Tests

```bash
./start.sh --test

# Or specific test file
./start.sh --cmd "python tests/test_performance.py"
```

### Run Custom Command

```bash
# Quick test of a component
./start.sh --cmd "python app/components/llm.py"

# Download models
./start.sh --cmd "python scripts/download_models.py"

# Start shell
./start.sh --cmd "bash"
```

### API Mode (Future)

```bash
# Start FastAPI server
docker-compose --profile api up consent-agent-api

# Access at http://localhost:8000
```

---

## Development Workflow

### Hot Reload Development

All code directories are mounted as volumes, so changes are reflected immediately:

```bash
# Start container
./start.sh

# In another terminal, edit code
nano app/components/llm.py

# Restart in container (Ctrl+C, then re-run)
# Changes are immediately available
```

### Building Custom Images

```bash
# Build with custom tag
docker build -t consent-agent:custom .

# Build with build args
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t consent-agent:py311 .
```

### Multi-Stage Builds (Future)

For production, create optimized images:

```dockerfile
# Example production Dockerfile
FROM nvcr.io/nvidia/vllm:26.01-py3 AS builder
# ... install deps

FROM nvcr.io/nvidia/vllm:26.01-py3 AS runtime
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# ... copy only runtime files
```

---

## Volume Mounts Explained

### Code Volumes (Development)
```yaml
- ./app:/workspace/consent-agent/app
- ./config:/workspace/consent-agent/config
```
- **Purpose**: Allow code changes without rebuilding image
- **Type**: Bind mount (host → container)

### Models Volume (Persistent)
```yaml
- ./models:/workspace/consent-agent/models
```
- **Purpose**: Persist large AI models across container restarts
- **Size**: ~16GB
- **Important**: Download models to `./models/` on host

### Data Volume (Persistent)
```yaml
- ./data:/workspace/consent-agent/data
```
- **Purpose**: Store session transcripts, exports, logs
- **Persistence**: Data survives container removal

---

## Resource Configuration

### GPU Access
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### Shared Memory
```yaml
shm_size: '16gb'
```
- **Required**: vLLM uses shared memory for efficient inference
- **Minimum**: 8GB
- **Recommended**: 16GB

### Environment Variables
```yaml
environment:
  - CUDA_VISIBLE_DEVICES=0        # Use GPU 0
  - PYTHONUNBUFFERED=1             # Real-time logs
  - VLLM_ALLOW_LONG_MAX_MODEL_LEN=1  # Allow large context
```

---

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"

```bash
# Start Docker service
sudo systemctl start docker

# Or on Docker Desktop
# Start Docker Desktop application
```

### Issue: "could not select device driver with capabilities: [[gpu]]"

```bash
# Install nvidia-container-toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Issue: "No space left on device"

```bash
# Clean up Docker images
docker system prune -a

# Check disk usage
docker system df

# Remove unused images
docker image prune -a
```

### Issue: Models not loading

```bash
# Check if models directory is mounted correctly
docker-compose run --rm consent-agent ls -la /workspace/consent-agent/models

# If empty, download models:
./start.sh --cmd "python scripts/download_models.py"
```

### Issue: Permission errors

```bash
# Fix permissions on host
sudo chown -R $USER:$USER models/ data/

# Or run as root (not recommended for production)
docker-compose run --user root --rm consent-agent bash
```

### Issue: vLLM import error

```bash
# Check CUDA libraries
./start.sh --cmd "python -c 'import torch; print(torch.cuda.is_available())'"

# Should print: True

# Check vLLM
./start.sh --cmd "python -c 'import vllm; print(vllm.__version__)'"
```

---

## Performance Optimization

### 1. Pin to Specific CPU Cores

```yaml
# In docker-compose.yml
cpuset: "0-7"  # Use cores 0-7
```

### 2. Limit Memory

```yaml
mem_limit: 64g
mem_reservation: 32g
```

### 3. Use tmpfs for Temporary Files

```yaml
tmpfs:
  - /tmp:size=4G
```

### 4. Network Optimization

```yaml
network_mode: host  # Use host networking for lowest latency
```

---

## Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml consent-agent

# Scale service
docker service scale consent-agent_consent-agent=3
```

### Kubernetes (Future)

Convert docker-compose to Kubernetes manifests:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.31.2/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv kompose /usr/local/bin/

# Convert
kompose convert -f docker-compose.yml
```

---

## Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats consent-agent-interactive

# GPU usage
docker exec consent-agent-interactive nvidia-smi
```

### Logs

```bash
# Follow logs
docker-compose logs -f consent-agent

# Last 100 lines
docker-compose logs --tail=100 consent-agent

# Save logs to file
docker-compose logs consent-agent > logs.txt
```

### Health Checks

```bash
# Check container health
docker inspect consent-agent-interactive | grep Health -A 10

# Manual health check
docker exec consent-agent-interactive python -c "import torch; assert torch.cuda.is_available()"
```

---

## Security Best Practices

### 1. Don't Run as Root

```dockerfile
# Add to Dockerfile
RUN useradd -m -s /bin/bash consentagent
USER consentagent
```

### 2. Read-Only Filesystems

```yaml
# In docker-compose.yml
read_only: true
tmpfs:
  - /tmp
  - /var/tmp
```

### 3. Limit Capabilities

```yaml
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # Only if needed
```

### 4. Secrets Management

```bash
# Use Docker secrets
echo "my_api_key" | docker secret create api_key -

# Reference in compose
secrets:
  - api_key
```

---

## Backup and Restore

### Backup Models and Data

```bash
# Backup script
tar -czf consent-agent-backup-$(date +%Y%m%d).tar.gz \
  models/ \
  data/ \
  config/

# Restore
tar -xzf consent-agent-backup-20260219.tar.gz
```

### Export Image

```bash
# Save image to file
docker save consent-agent:week1 | gzip > consent-agent-image.tar.gz

# Load on another machine
docker load < consent-agent-image.tar.gz
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t consent-agent:test .
      
      - name: Run tests
        run: docker run --gpus all consent-agent:test python tests/test_components.py
```

---

## Common Commands Reference

```bash
# Build
docker-compose build
./start.sh --build

# Run
docker-compose up consent-agent
./start.sh

# Stop
docker-compose down
Ctrl+C (if running in foreground)

# Shell access
docker-compose exec consent-agent bash
./start.sh --cmd "bash"

# View logs
docker-compose logs -f consent-agent

# Remove everything
docker-compose down -v
docker rmi consent-agent:week1

# Update base image
docker pull nvcr.io/nvidia/vllm:26.01-py3
docker-compose build --no-cache
```

---

## Next Steps

After Docker setup is working:

1. **Download models** (if not already done):
   ```bash
   ./start.sh --cmd "python scripts/download_models.py"
   ```

2. **Run tests**:
   ```bash
   ./start.sh --test
   ```

3. **Start interactive session**:
   ```bash
   ./start.sh
   ```

4. **For Week 2**: Same Docker setup works, just add new components!

---

**Docker Setup Version**: 1.0  
**Last Updated**: February 19, 2026  
**Compatible with**: Week 1-6 implementations
