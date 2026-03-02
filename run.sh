#!/bin/bash
# Run the consent agent with proper CUDA environment

# Find CUDA libraries
if [ -d "/usr/local/cuda/lib64" ]; then
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    echo "✅ Added /usr/local/cuda/lib64 to LD_LIBRARY_PATH"
elif [ -d "/usr/lib/x86_64-linux-gnu" ]; then
    export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
    echo "✅ Added /usr/lib/x86_64-linux-gnu to LD_LIBRARY_PATH"
fi

# Find CUDA bin
if [ -d "/usr/local/cuda/bin" ]; then
    export PATH=/usr/local/cuda/bin:$PATH
fi

# Activate virtual environment
if [ ! -d "venv" ] && [ ! -d "consent-env" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: ./scripts/setup.sh first"
    exit 1
fi

if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "consent-env" ]; then
    source consent-env/bin/activate
fi

echo ""
echo "Starting Consent Agent..."
echo "=========================================="
python app/orchestrator.py
