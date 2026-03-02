#!/bin/bash
# Setup script for Consent Agent - Week 1

set -e  # Exit on error

echo "=========================================="
echo "Consent Agent Setup - Week 1"
echo "=========================================="

# Check Python version
echo ""
echo "[1/7] Checking Python version..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Create virtual environment
echo ""
echo "[2/7] Creating virtual environment..."
VENV_NAME="consent-env"
if [ ! -d "$VENV_NAME" ]; then
    python3 -m venv $VENV_NAME
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source $VENV_NAME/bin/activate

# Upgrade pip
echo ""
echo "[3/7] Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Detect CUDA version
echo ""
echo "[4/7] Detecting CUDA version..."
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | sed -n 's/.*release \([0-9]\+\)\.\([0-9]\+\).*/\1\2/p')
    echo "✅ CUDA ${CUDA_VERSION:0:2}.${CUDA_VERSION:2} detected"
    
    # Determine PyTorch CUDA version to install
    if [ "${CUDA_VERSION:0:2}" -ge "12" ]; then
        TORCH_CUDA="cu121"  # CUDA 12.1+ compatible
    else
        TORCH_CUDA="cu118"  # CUDA 11.8 compatible
    fi
else
    echo "⚠️  CUDA not found, installing CPU-only version"
    TORCH_CUDA="cpu"
fi

# Install PyTorch with CUDA support FIRST
echo ""
echo "[5/7] Installing PyTorch with CUDA support..."
if [ "$TORCH_CUDA" != "cpu" ]; then
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$TORCH_CUDA
else
    pip install torch torchvision torchaudio
fi

# Verify PyTorch CUDA
echo ""
python3 -c "import torch; print(f'✅ PyTorch {torch.__version__}'); print(f'✅ CUDA available: {torch.cuda.is_available()}')" || {
    echo "⚠️  PyTorch installed but CUDA not available"
    echo "   This is OK for testing, but GPU acceleration won't work"
}

# Install vLLM without dependencies (to avoid PyTorch conflicts)
echo ""
echo "[6/7] Installing vLLM (without dependency conflicts)..."
pip install vllm --no-deps

# Install vLLM's other dependencies manually
echo "Installing vLLM dependencies..."
pip install transformers>=4.45.0
pip install xformers || echo "⚠️  xformers optional, skipping"
pip install ray
pip install numpy
pip install typing-extensions

# Install remaining dependencies from requirements.txt
echo ""
echo "[7/7] Installing remaining dependencies..."
pip install faster-whisper>=1.0.0
pip install sounddevice soundfile webrtcvad
pip install sentencepiece
pip install fastapi uvicorn[standard] pydantic websockets
pip install python-dotenv pyyaml requests aiofiles
pip install psutil gputil
pip install pytest pytest-asyncio
pip install huggingface-hub

# Final verification
echo ""
echo "=========================================="
echo "Verifying installation..."
echo "=========================================="
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
python3 -c "import vllm; print('vLLM: OK')" || echo "⚠️  vLLM verification failed"
python3 -c "from faster_whisper import WhisperModel; print('Whisper: OK')" || echo "⚠️  Whisper verification failed"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source $VENV_NAME/bin/activate"
echo ""
echo "2. Download models (if not already done):"
echo "   python scripts/download_models.py"
echo ""
echo "3. Test the system:"
echo "   ./run.sh"
echo "   OR: python app/orchestrator.py"
echo ""
echo "4. Run benchmarks:"
echo "   python tests/test_performance.py"
echo ""
echo "If you encounter issues:"
echo "   ./scripts/check_cuda.sh"
echo ""
