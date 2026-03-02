"""Text-to-Speech using Piper - SIMPLIFIED VERSION"""

from pathlib import Path
import time
from typing import Dict, Optional
import sys
import subprocess

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import MODELS_DIR

class PiperTTS:
    def __init__(self, models_dir: str = None):
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR / "piper-tts"
        
        self.voices = {
            'en': self.models_dir / 'en_US-lessac-medium.onnx',
            'es': self.models_dir / 'es_ES-davefx-medium.onnx',
            'it': self.models_dir / 'it_IT-riccardo-x_low.onnx'
        }
        
        print("🔊 Checking Piper TTS voices...")
        for lang, voice_path in self.voices.items():
            if voice_path.exists():
                print(f"  ✅ {lang.upper()} voice found")
            else:
                print(f"  ⚠️  {lang.upper()} voice not found")
        
        print(f"✅ Piper TTS ready")
    
    def synthesize(self, text: str, language: str = 'en', output_path: Optional[str] = None) -> Dict:
        if language not in self.voices:
            raise ValueError(f"Language '{language}' not available")
        
        voice_path = self.voices[language]
        if not voice_path.exists():
            raise FileNotFoundError(f"Voice model not found: {voice_path}")
        
        if not output_path:
            output_path = f"output_{language}.wav"
        
        start_time = time.time()
        
        # Use piper command line
        cmd = f'echo "{text}" | piper --model {voice_path} --output_file {output_path}'
        subprocess.run(cmd, shell=True, check=True)
        
        latency = time.time() - start_time
        
        return {
            "output_path": output_path,
            "language": language,
            "latency_ms": latency * 1000,
            "text": text
        }

def test_tts():
    print("\n" + "="*60)
    print("Piper TTS Component Test")
    print("="*60)
    
    tts = PiperTTS()
    
    print("\n" + "="*60)
    print("Test 1: English TTS")
    print("="*60)
    result = tts.synthesize("Good morning.", 'en', 'test_en.wav')
    print(f"Latency: {result['latency_ms']:.0f}ms")
    print(f"Saved to: {result['output_path']}")
    
    print("\n✅ TTS component ready")

if __name__ == "__main__":
    test_tts()