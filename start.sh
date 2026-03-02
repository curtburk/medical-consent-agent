#!/bin/bash
# Startup script for Consent Agent Docker environment
# This script builds the Docker image and starts the interactive agent

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "Consent Agent - Docker Startup"
echo -e "==========================================${NC}\n"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if nvidia-docker is available
if ! docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ NVIDIA Docker runtime not available${NC}"
    echo "Please install nvidia-container-toolkit:"
    echo "https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi

echo -e "${GREEN}✅ Docker and NVIDIA runtime detected${NC}\n"

# Check if models directory exists and has models
if [ ! -d "./models" ]; then
    echo -e "${YELLOW}⚠️  Models directory not found${NC}"
    echo "Creating models directory..."
    mkdir -p ./models
fi

MODEL_SIZE=$(du -sh ./models 2>/dev/null | cut -f1)
if [ -z "$MODEL_SIZE" ] || [ "$MODEL_SIZE" = "0" ]; then
    echo -e "${YELLOW}⚠️  No models found in ./models/${NC}"
    echo "You'll need to download models before running the agent."
    echo "Run: python scripts/download_models.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ Models directory found (${MODEL_SIZE})${NC}\n"
fi

# Parse command line arguments
BUILD_IMAGE=false
RUN_TESTS=false
INTERACTIVE=true
COMMAND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_IMAGE=true
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        --cmd)
            INTERACTIVE=false
            COMMAND="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --build       Build Docker image before running"
            echo "  --test        Run tests instead of interactive mode"
            echo "  --cmd <cmd>   Run specific command instead of interactive mode"
            echo "  --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./start.sh                    # Run interactive agent"
            echo "  ./start.sh --build            # Rebuild image and run"
            echo "  ./start.sh --test             # Run test suite"
            echo "  ./start.sh --cmd 'python tests/test_components.py'"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build image if requested or if it doesn't exist
if [ "$BUILD_IMAGE" = true ] || ! docker image inspect consent-agent:week1 &> /dev/null; then
    echo -e "${BLUE}[1/2] Building Docker image...${NC}"
    echo "This may take 5-10 minutes on first build..."
    echo ""
    
    docker build -t consent-agent:week1 . || {
        echo -e "${RED}❌ Docker build failed${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✅ Docker image built successfully${NC}\n"
else
    echo -e "${GREEN}✅ Using existing Docker image${NC}\n"
fi

# Determine what to run
if [ "$RUN_TESTS" = true ]; then
    echo -e "${BLUE}[2/2] Running tests...${NC}\n"
    docker compose run --rm consent-agent python tests/test_components.py
    
elif [ -n "$COMMAND" ]; then
    echo -e "${BLUE}[2/2] Running command: ${COMMAND}${NC}\n"
    docker compose run --rm consent-agent bash -c "$COMMAND"
    
else
    echo -e "${BLUE}[2/2] Starting interactive agent...${NC}\n"
    echo -e "${YELLOW}Note: Models will load on first run (60-90 seconds)${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop, type 'quit' to exit gracefully${NC}\n"
    
    # Run with docker compose
    docker compose run --rm consent-agent
fi

echo -e "\n${GREEN}=========================================="
echo "Session ended"
echo -e "==========================================${NC}"
