#!/bin/bash
# Check CUDA installation and setup

echo "=========================================="
echo "CUDA Environment Check"
echo "=========================================="

# Check NVIDIA driver
echo ""
echo "[1/5] Checking NVIDIA driver..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo "✅ NVIDIA driver found"
else
    echo "❌ nvidia-smi not found"
    exit 1
fi

# Check CUDA installation
echo ""
echo "[2/5] Checking CUDA installation..."
if command -v nvcc &> /dev/null; then
    nvcc --version | grep "release"
    echo "✅ CUDA compiler found"
else
    echo "⚠️  nvcc not found (CUDA Toolkit may not be installed)"
fi

# Check for CUDA libraries
echo ""
echo "[3/5] Checking CUDA libraries..."
if [ -d "/usr/local/cuda" ]; then
    echo "✅ CUDA found at: /usr/local/cuda"
    ls -d /usr/local/cuda*/lib64/libcudart.so.* 2>/dev/null | head -1
elif [ -d "/usr/lib/x86_64-linux-gnu" ]; then
    if ls /usr/lib/x86_64-linux-gnu/libcudart.so.* 2>/dev/null | head -1; then
        echo "✅ CUDA libraries found in system path"
    fi
else
    echo "⚠️  CUDA libraries not found in standard locations"
fi

# Check LD_LIBRARY_PATH
echo ""
echo "[4/5] Checking LD_LIBRARY_PATH..."
if [[ -z "$LD_LIBRARY_PATH" ]]; then
    echo "⚠️  LD_LIBRARY_PATH is not set"
    echo ""
    echo "Fix: Add to ~/.bashrc:"
    echo "export LD_LIBRARY_PATH=/usr/local/cuda/lib64:\$LD_LIBRARY_PATH"
else
    echo "✅ LD_LIBRARY_PATH is set"
    echo "   $LD_LIBRARY_PATH"
fi

# Check PyTorch CUDA
echo ""
echo "[5/5] Checking PyTorch CUDA support..."
if [ -d "venv" ] || [ -d "consent-env" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source consent-env/bin/activate
    fi
    python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ PyTorch can access CUDA"
    else
        echo "❌ PyTorch cannot access CUDA"
    fi
else
    echo "⚠️  Virtual environment not found"
fi

echo ""
echo "=========================================="
echo "Next steps:"
echo "1. export LD_LIBRARY_PATH=/usr/local/cuda/lib64:\$LD_LIBRARY_PATH"
echo "2. Or use: ./run.sh"
echo "=========================================="
