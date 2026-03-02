"""Translation engine using NLLB-200-distilled-600M"""

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Dict, Optional
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import MODELS_DIR

class TranslationEngine:
    """NLLB-200 translation for multilingual support"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize NLLB translation model
        
        Args:
            model_path: Path to NLLB model (uses config default if None)
        """
        self.model_path = model_path or str(MODELS_DIR / "nllb-200-distilled-600m")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🌍 Loading NLLB-200 on {self.device}...")
        start_time = time.time()
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            src_lang="eng_Latn"
        )
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)
        
        # Language code mapping (NLLB uses specific codes)
        self.lang_codes = {
            'en': 'eng_Latn',
            'es': 'spa_Latn',
            'it': 'ita_Latn'
        }
        
        load_time = time.time() - start_time
        print(f"✅ NLLB-200 loaded in {load_time:.1f}s")
        
        # Get model size for monitoring
        param_size = sum(p.numel() for p in self.model.parameters())
        print(f"   Parameters: {param_size / 1e9:.2f}B")
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str = 'en'
    ) -> Dict:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, es, it)
            target_lang: Target language code (default: en)
        
        Returns:
            Dict with translation and metadata
        """
        # Skip translation if source == target
        if source_lang == target_lang:
            return {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "latency_ms": 0,
                "skipped": True,
                "needs_review": False
            }
        
        start_time = time.time()
        
        # Get NLLB language codes
        src_code = self.lang_codes.get(source_lang, 'eng_Latn')
        tgt_code = self.lang_codes.get(target_lang, 'eng_Latn')
        
        # Set source language
        self.tokenizer.src_lang = src_code
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Generate translation
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt_code),
                max_length=512,
                num_beams=4,
                early_stopping=True
            )
        
        # Decode
        translated_text = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0]
        
        latency = time.time() - start_time
        
        # Quality check
        needs_review = self._quality_check(text, translated_text)
        
        return {
            "text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "latency_ms": latency * 1000,
            "needs_review": needs_review,
            "skipped": False
        }
    
    def _quality_check(self, source: str, translation: str) -> bool:
        """
        Basic quality check for translation
        
        Returns:
            True if translation needs human review
        """
        # Check if translation is empty or very short
        if len(translation.strip()) < 3:
            return True
        
        # Check length ratio (translations should be similar length)
        source_len = len(source.split())
        trans_len = len(translation.split())
        
        if trans_len == 0:
            return True
        
        ratio = source_len / trans_len
        
        # Flag if translation is too short or too long
        # (ratio should be between 0.5 and 2.0 for most languages)
        if ratio < 0.5 or ratio > 2.0:
            return True
        
        return False
    
    def translate_conversation(
        self,
        messages: list,
        source_lang: str,
        target_lang: str = 'en'
    ) -> list:
        """
        Translate entire conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            source_lang: Source language
            target_lang: Target language
        
        Returns:
            List of translated messages
        """
        translated = []
        
        for msg in messages:
            result = self.translate(
                msg['content'],
                source_lang,
                target_lang
            )
            
            translated.append({
                'role': msg['role'],
                'content_original': msg['content'],
                'content_translation': result['text'],
                'needs_review': result['needs_review']
            })
        
        return translated

def test_translator():
    """Test translation component"""
    print("\n" + "="*60)
    print("NLLB-200 Translation Component Test")
    print("="*60)
    
    # Check if model exists
    model_path = Path(__file__).parent.parent.parent / "models" / "nllb-200-distilled-600m"
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        print("   Run scripts/download_models.py first")
        return
    
    # Initialize translator
    translator = TranslationEngine()
    
    print("\n" + "="*60)
    print("Test 1: Spanish → English")
    print("="*60)
    result = translator.translate(
        "Buenos días, necesito ayuda con mi procedimiento.",
        source_lang='es',
        target_lang='en'
    )
    print(f"Original (ES): Buenos días, necesito ayuda con mi procedimiento.")
    print(f"Translation (EN): {result['text']}")
    print(f"Latency: {result['latency_ms']:.0f}ms")
    print(f"Needs review: {result['needs_review']}")
    
    print("\n" + "="*60)
    print("Test 2: Italian → English")
    print("="*60)
    result = translator.translate(
        "Buongiorno, ho bisogno di aiuto con la mia procedura.",
        source_lang='it',
        target_lang='en'
    )
    print(f"Original (IT): Buongiorno, ho bisogno di aiuto con la mia procedura.")
    print(f"Translation (EN): {result['text']}")
    print(f"Latency: {result['latency_ms']:.0f}ms")
    print(f"Needs review: {result['needs_review']}")
    
    print("\n" + "="*60)
    print("Test 3: English → Spanish")
    print("="*60)
    result = translator.translate(
        "You need to drink all of the preparation liquid.",
        source_lang='en',
        target_lang='es'
    )
    print(f"Original (EN): You need to drink all of the preparation liquid.")
    print(f"Translation (ES): {result['text']}")
    print(f"Latency: {result['latency_ms']:.0f}ms")
    print(f"Needs review: {result['needs_review']}")
    
    print("\n" + "="*60)
    print("Test 4: English → Italian")
    print("="*60)
    result = translator.translate(
        "The procedure will take about 30 minutes.",
        source_lang='en',
        target_lang='it'
    )
    print(f"Original (EN): The procedure will take about 30 minutes.")
    print(f"Translation (IT): {result['text']}")
    print(f"Latency: {result['latency_ms']:.0f}ms")
    
    print("\n✅ Translation component ready")
    print(f"   Average latency: ~{result['latency_ms']:.0f}ms")

if __name__ == "__main__":
    test_translator()
