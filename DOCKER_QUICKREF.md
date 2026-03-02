# Docker Quick Reference Card

## 🚀 Getting Started

```bash
# First time setup
./start.sh --build

# Normal start
./start.sh

# Run tests
./start.sh --test
```

---

## 📋 Common Commands

### Start/Stop
```bash
./start.sh                    # Start interactive agent
docker-compose up -d          # Start in background
docker-compose down           # Stop all containers
```

### Development
```bash
./start.sh --build            # Rebuild image
./start.sh --cmd "bash"       # Open shell
docker-compose exec consent-agent bash  # Shell in running container
```

### Testing
```bash
./start.sh --test             # Run all tests
./start.sh --cmd "python tests/test_components.py"  # Specific test
```

### Logs & Monitoring
```bash
docker-compose logs -f        # Follow logs
docker logs consent-agent-interactive  # View logs
docker stats consent-agent-interactive # Resource usage
```

---

## 🔧 Troubleshooting

### Can't connect to Docker
```bash
sudo systemctl start docker   # Start Docker daemon
```

### GPU not available
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

### Models not loading
```bash
# Check models directory
./start.sh --cmd "ls -la models/"

# Download models
./start.sh --cmd "python scripts/download_models.py"
```

### Permission errors
```bash
sudo chown -R $USER:$USER models/ data/
```

### Out of disk space
```bash
docker system prune -a        # Clean up
docker system df              # Check usage
```

---

## 📊 Useful Checks

```bash
# Check if container is running
docker ps

# Check container health
docker inspect consent-agent-interactive | grep Health -A 5

# Check GPU inside container
docker exec consent-agent-interactive nvidia-smi

# Check Python/CUDA
docker exec consent-agent-interactive python -c "import torch; print(torch.cuda.is_available())"

# Check vLLM
docker exec consent-agent-interactive python -c "import vllm; print(vllm.__version__)"
```

---

## 🎯 Advanced

```bash
# Custom command
./start.sh --cmd "python -c 'import torch; print(torch.version.cuda)'"

# Access specific component
./start.sh --cmd "python app/components/llm.py"

# Export image
docker save consent-agent:week1 | gzip > image.tar.gz

# Load image
docker load < image.tar.gz
```

---

## 📁 Volume Locations

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./app` | `/workspace/consent-agent/app` | Code (hot reload) |
| `./models` | `/workspace/consent-agent/models` | AI models (~16GB) |
| `./data` | `/workspace/consent-agent/data` | Session data |
| `./config` | `/workspace/consent-agent/config` | Configuration |

---

## 🆘 Emergency Commands

```bash
# Stop everything
docker-compose down -v

# Remove all containers
docker rm -f $(docker ps -aq)

# Remove image
docker rmi consent-agent:week1

# Complete cleanup
docker system prune -a --volumes

# Start fresh
./start.sh --build
```

---

## 📞 Getting Help

```bash
./start.sh --help             # Startup options
docker-compose --help         # Docker Compose help
cat DOCKER_GUIDE.md           # Full documentation
```
