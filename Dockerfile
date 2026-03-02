# Dockerfile for Multilingual Patient Consent Verification Agent
# Based on NVIDIA vLLM 26.01 container with CUDA 13.0 support

FROM nvcr.io/nvidia/vllm:26.01-py3

LABEL maintainer="HP ZGX Nano Team"
LABEL description="Multilingual Patient Consent Agent with vLLM, Whisper, NLLB, Piper TTS"
LABEL version="1.0.0-week1"

# Set working directory
WORKDIR /workspace/consent-agent

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libsndfile1 \
    sox \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Core dependencies for Week 1
RUN pip install --no-cache-dir \
    faster-whisper>=1.0.0 \
    sounddevice>=0.4.6 \
    soundfile>=0.12.1 \
    webrtcvad>=2.0.10 \
    sentencepiece>=0.1.99 \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    pydantic>=2.5.0 \
    websockets>=12.0 \
    python-dotenv>=1.0.0 \
    pyyaml>=6.0 \
    requests>=2.31.0 \
    aiofiles>=23.2.1 \
    psutil>=5.9.6 \
    gputil>=1.4.0 \
    pytest>=7.4.3 \
    pytest-asyncio>=0.21.1 \
    huggingface-hub>=0.20.0

# Install Week 2 dependencies (pre-install for future use)
RUN pip install --no-cache-dir \
    piper-tts>=1.2.0 \
    pathvalidate>=3.0.0

# Create necessary directories
RUN mkdir -p /workspace/consent-agent/models \
    /workspace/consent-agent/data/sessions \
    /workspace/consent-agent/data/exports \
    /workspace/consent-agent/data/logs

# Copy application code (will be overridden by volume mount in development)
COPY . /workspace/consent-agent/

# Set permissions
RUN chmod +x /workspace/consent-agent/scripts/*.sh 2>/dev/null || true
RUN chmod +x /workspace/consent-agent/run.sh 2>/dev/null || true

# Expose ports for FastAPI (future use)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; assert torch.cuda.is_available()" || exit 1

# Default command - run interactive CLI
CMD ["python", "app/orchestrator.py"]
