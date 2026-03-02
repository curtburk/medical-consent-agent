# Troubleshooting Guide

## Important: PyTorch and vLLM Installation

**Always use `./scripts/setup.sh` for initial setup!**

The setup script handles PyTorch and vLLM installation in the correct order:
1. Detects your CUDA version
2. Installs PyTorch with matching CUDA support
3. Installs vLLM with `--no-deps` to avoid conflicts
4. Installs vLLM dependencies separately

**Do NOT use `pip install -r requirements.txt` directly** - it will cause PyTorch/vLLM conflicts.

### If You Already Have Version Conflicts

```bash
# Clean slate approach
rm -rf consent-env venv
./scripts/setup.sh
```

---

## Quick Fix: CUDA Library Not Found

If you see: `ImportError: libcudart.so.12: cannot open shared object file`

### Solution 1: Use the run.sh script (Easiest)

```bash
chmod +x run.sh
./run.sh
```

### Solution 2: Set CUDA path manually

```bash
# Find CUDA location
./scripts/check_cuda.sh

# Set environment variable
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Add to ~/.bashrc to make permanent
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
```

---

## Error: PyTorch CPU-only Version Installed

If check_cuda.sh shows: `PyTorch: 2.x.x+cpu` or `CUDA available: False`

**Solution: Use setup.sh which installs CUDA-enabled PyTorch**

```bash
rm -rf consent-env
./scripts/setup.sh
```

Or manually:
```bash
source consent-env/bin/activate
pip uninstall torch torchvision torchaudio vllm -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install vllm --no-deps
pip install transformers xformers ray numpy typing-extensions
```

---

## Error: vLLM and PyTorch Version Conflicts

If you see: `vllm requires torch==2.9.1, but you have torch 2.x.x`

**This happens when installing vLLM the wrong way.**

**Solution:**
```bash
# Method 1: Clean reinstall (recommended)
rm -rf consent-env
./scripts/setup.sh

# Method 2: Manual fix
pip uninstall vllm torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install vllm --no-deps
pip install transformers ray numpy typing-extensions
```

The key: Install PyTorch first, then install vLLM with `--no-deps`.

---

## Error: Models Not Found

```bash
# Check if models exist
ls -la models/

# If empty, download:
source consent-env/bin/activate
python scripts/download_models.py
```

---

## Error: CUDA Out of Memory

Edit `config/config.py`:

```python
VLLM_CONFIG = {
    "max_model_len": 2048,  # Reduce from 4096
    "gpu_memory_utilization": 0.75,  # Reduce from 0.85
}
```

---

## Slow Inference (<80 tok/s)

### Check 1: Verify AWQ quantization
Look for "quantization": "AWQ" in startup logs

### Check 2: Reduce context window
```python
# config/config.py
VLLM_CONFIG["max_model_len"] = 2048
```

### Check 3: Monitor GPU
```bash
watch -n 1 nvidia-smi
# GPU should be 60-95% utilized during inference
```

---

## Testing Individual Components

```bash
source consent-env/bin/activate

# Test monitor
python app/utils/monitor.py

# Test Whisper (if models downloaded)
python app/components/stt.py

# Test LLM (if models downloaded)
python app/components/llm.py

# Test all components
python tests/test_components.py
```

---

## Complete Clean Reinstall

```bash
cd ~/Desktop/consent-agent

# Remove everything
rm -rf consent-env venv

# Fresh install
./scripts/setup.sh

# Download models
source consent-env/bin/activate
python scripts/download_models.py

# Test
./run.sh
```

---

## Common Error Summary

| Error | Fix |
|-------|-----|
| `libcudart.so not found` | Use `./run.sh` or set `LD_LIBRARY_PATH` |
| `PyTorch CPU-only` | Run `./scripts/setup.sh` |
| `vLLM version conflicts` | Install PyTorch first, vLLM with `--no-deps` |
| `Models not found` | Run `python scripts/download_models.py` |
| `CUDA out of memory` | Reduce `max_model_len` in config |

---

## Getting Help

1. **Run diagnostics**: `./scripts/check_cuda.sh`
2. **Test components**: `python tests/test_components.py`
3. **Check README.md** for usage examples
4. **Verify setup**: Make sure you used `./scripts/setup.sh`
