"""Speech-to-Text using Whisper Large v3"""

import torch
from faster_whisper import WhisperModel
import numpy as np
from typing import Dict, Optional, Tuple
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import WHISPER_MODEL_PATH, WHISPER_CONFIG

class WhisperSTT:
    """Whisper Large v3 Speech-to-Text component"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize Whisper STT
        
        Args:
            model_path: Path to Whisper model (uses config default if None)
        """
        self.model_path = model_path or str(WHISPER_MODEL_PATH)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = WHISPER_CONFIG["compute_type"]
        
        print(f"🎤 Loading Whisper Large v3 on {self.device}...")
        start_time = time.time()
        
        self.model = WhisperModel(
            self.model_path,
            device=self.device,
            compute_type=self.compute_type
        )
        
        load_time = time.time() - start_time
        print(f"✅ Whisper loaded in {load_time:.1f}s")
        
        # Get VRAM usage if on GPU
        if self.device == "cuda":
            import torch
            vram_mb = torch.cuda.memory_allocated() / (1024**2)
            print(f"   VRAM usage: {vram_mb:.0f}MB")
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file (wav, mp3, etc.)
            language: Language code (en, es, it) or None for auto-detect
        
        Returns:
            Dict with keys:
                - text: Transcribed text
                - language: Detected/specified language
                - confidence: Average confidence score
                - latency_ms: Processing time in milliseconds
        """
        start_time = time.time()
        
        # Transcribe with Whisper
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=WHISPER_CONFIG["beam_size"],
            vad_filter=WHISPER_CONFIG["vad_filter"],
            vad_parameters=WHISPER_CONFIG["vad_parameters"]
        )
        
        # Collect segments
        transcription = []
        confidences = []
        
        for segment in segments:
            transcription.append(segment.text.strip())
            confidences.append(segment.avg_logprob)
        
        text = " ".join(transcription).strip()
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            "text": text,
            "language": info.language if not language else language,
            "confidence": float(avg_confidence),
            "latency_ms": latency_ms
        }
        
        return result
    
    def transcribe_numpy(
        self,
        audio_array: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio from numpy array (useful for real-time audio)
        
        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate (default 16kHz for Whisper)
            language: Language code or None for auto-detect
        
        Returns:
            Dict with transcription results
        """
        # Save to temporary file
        import tempfile
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            sf.write(tmp_path, audio_array, sample_rate)
        
        try:
            result = self.transcribe(tmp_path, language)
            return result
        finally:
            # Clean up temp file
            Path(tmp_path).unlink()

def test_whisper():
    """Test Whisper STT component"""
    print("\n" + "="*50)
    print("Whisper STT Component Test")
    print("="*50)
    
    # Check if model exists
    if not WHISPER_MODEL_PATH.exists():
        print(f"❌ Model not found at {WHISPER_MODEL_PATH}")
        print("   Run scripts/download_models.py first")
        return
    
    # Initialize
    stt = WhisperSTT()
    
    print("\n✅ Whisper STT component ready")
    print(f"   Model: {WHISPER_MODEL_PATH}")
    print(f"   Device: {stt.device}")
    print(f"   Compute type: {stt.compute_type}")
    
    print("\n💡 To test with actual audio, call:")
    print("   result = stt.transcribe('path/to/audio.wav', language='en')")

if __name__ == "__main__":
    test_whisper()
