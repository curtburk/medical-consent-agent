#!/usr/bin/env python3
"""Download all models for the consent agent"""

from huggingface_hub import snapshot_download
import os
import urllib.request
from pathlib import Path

print("=" * 50)
print("Downloading Models")
print("=" * 50)

# Create directory structure
models_dir = Path("./models")
models_dir.mkdir(exist_ok=True)

# 1. Whisper Large V3
print("\n[1/4] Downloading Whisper Large V3 (~6GB)...")
snapshot_download(
    repo_id="openai/whisper-large-v3",
    local_dir=str(models_dir / "whisper-large-v3"),
    local_dir_use_symlinks=False
)
print("✅ Whisper downloaded")

# 2. Qwen3-14B-AWQ
print("\n[2/4] Downloading Qwen3-14B-AWQ (~8GB)...")
snapshot_download(
    repo_id="Qwen/Qwen3-14B-AWQ",
    local_dir=str(models_dir / "qwen3-14b-awq"),
    local_dir_use_symlinks=False
)
print("✅ Qwen3 downloaded")

# 3. NLLB
print("\n[3/4] Downloading NLLB-200 (~1.2GB)...")
snapshot_download(
    repo_id="facebook/nllb-200-distilled-600M",
    local_dir=str(models_dir / "nllb-200-distilled-600m"),
    local_dir_use_symlinks=False
)
print("✅ NLLB downloaded")

# 4. Piper voices
print("\n[4/4] Downloading Piper TTS voices...")
piper_dir = models_dir / "piper-tts"
piper_dir.mkdir(exist_ok=True)

voices = [
    ("es", "es_ES-davefx-medium"),
    ("it", "it_IT-riccardo-x_low"),
    ("en", "en_US-lessac-medium")
]

for lang, voice in voices:
    print(f"  → Downloading {voice}...")
    base_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/{lang[:2]}/{voice.replace('-', '/')}"
    
    for ext in [".onnx", ".onnx.json"]:
        url = f"{base_url}/{voice}{ext}"
        output = piper_dir / f"{voice}{ext}"
        urllib.request.urlretrieve(url, output)

print("\n✅ All models downloaded successfully!")
