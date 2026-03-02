"""Enhanced Consent Agent orchestrator - Week 2 with translation, TTS, and transcripts"""

import time
import sys
from pathlib import Path
from typing import Dict, Optional

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent))

from components.llm import ConversationLLM
from components.translator import TranslationEngine
from components.tts import PiperTTS
from utils.transcript import TranscriptManager

class ConsentAgentV2:
    """
    Multilingual Patient Consent Verification Agent - Week 2
    
    Features:
    - Whisper STT (speech-to-text)
    - Qwen3-14B-AWQ (conversation)
    - NLLB-200 (translation)
    - Piper TTS (text-to-speech)
    - Bilingual transcripts
    """
    
    def __init__(self, enable_tts: bool = True, enable_translation: bool = True):
        """
        Initialize all components
        
        Args:
            enable_tts: Enable text-to-speech output
            enable_translation: Enable translation for bilingual transcripts
        """
        print("\n" + "="*60)
        print("INITIALIZING CONSENT AGENT V2 (WEEK 2)")
        print("="*60)
        
        # Show initial resources
        print("\n📊 Initial resource state:")
        # print_stats(show_title=False)
        
        # Initialize core components (Week 1)
        print("\n[1/5] Initializing Speech-to-Text...")
        try:
            self.stt = WhisperSTT()
        except Exception as e:
            print(f"❌ Failed to load Whisper: {e}")
            print("   Continuing without STT (text-only mode)")
            self.stt = None
        
        print("\n[2/5] Initializing Conversation LLM...")
        self.llm = ConversationLLM()
        self.llm.set_procedure("colonoscopy")
        
        # Initialize Week 2 components
        self.enable_translation = enable_translation
        if enable_translation:
            print("\n[3/5] Initializing Translation Engine...")
            try:
                self.translator = TranslationEngine()
            except Exception as e:
                print(f"❌ Failed to load Translator: {e}")
                print("   Continuing without translation")
                self.translator = None
                self.enable_translation = False
        else:
            print("\n[3/5] Translation disabled")
            self.translator = None
        
        self.enable_tts = enable_tts
        if enable_tts:
            print("\n[4/5] Initializing Text-to-Speech...")
            try:
                self.tts = PiperTTS()
            except Exception as e:
                print(f"❌ Failed to load TTS: {e}")
                print("   Continuing without TTS")
                self.tts = None
                self.enable_tts = False
        else:
            print("\n[4/5] TTS disabled")
            self.tts = None
        
        print("\n[5/5] Initializing Transcript Manager...")
        self.transcript = TranscriptManager()
        
        # Show final resources
        print("\n📊 Resource state after initialization:")
        # print_stats(show_title=False)
        
        # Check health
        #health = check_resource_health()
        #if health["status"] == "healthy":
            #print("✅ All systems nominal")
        #elif health["status"] == "warning":
            #print("⚠️  System warnings detected:")
            #for warning in health["warnings"]:
                #print(f"   - {warning}")
        
        print("\n" + "="*60)
        print("AGENT READY (WEEK 2 MODE)")
        print("="*60)
        print(f"Features: Translation={self.enable_translation}, TTS={self.enable_tts}")
        print("="*60 + "\n")
    
    def process_text(
        self,
        text: str,
        language: str = "en",
        generate_audio: bool = False,
        verbose: bool = True
    ) -> Dict:
        """
        Process text input with full Week 2 pipeline
        
        Args:
            text: User's text input
            language: Language code (en, es, it)
            generate_audio: Whether to generate TTS audio
            verbose: Whether to print progress
        
        Returns:
            Dict with processing results
        """
        start_time = time.time()
        
        if verbose:
            print(f"👤 Patient ({language.upper()}): {text}")
        
        # Step 1: Translate to English for logging (if not already English)
        translation_to_en = None
        if self.enable_translation and language != 'en':
            trans_result = self.translator.translate(text, language, 'en')
            translation_to_en = trans_result['text']
            if verbose:
                print(f"   [EN translation]: {translation_to_en}")
        
        # Step 2: Generate response with LLM
        if verbose:
            print("🧠 Generating response...")
        
        llm_start = time.time()
        llm_result = self.llm.generate_response(text, language)
        llm_latency = (time.time() - llm_start) * 1000
        
        # Step 3: Translate response to English for logging (if not English)
        response_translation_to_en = None
        if self.enable_translation and language != 'en':
            trans_result = self.translator.translate(
                llm_result['text'],
                language,
                'en'
            )
            response_translation_to_en = trans_result['text']
        
        # Step 4: Generate TTS audio (if requested)
        audio_path = None
        tts_latency = 0
        if generate_audio and self.enable_tts and self.tts:
            tts_start = time.time()
            timestamp = int(time.time())
            audio_path = f"data/audio/response_{timestamp}_{language}.wav"
            
            # Ensure directory exists
            Path(audio_path).parent.mkdir(parents=True, exist_ok=True)
            
            tts_result = self.tts.synthesize(
                llm_result['text'],
                language,
                audio_path
            )
            tts_latency = tts_result['latency_ms']
            
            if verbose:
                print(f"🔊 Audio generated: {audio_path} ({tts_latency:.0f}ms)")
        
        # Step 5: Add to transcript
        self.transcript.add_entry(
            speaker='PATIENT',
            text_original=text,
            text_translation=translation_to_en or text,
            language=language
        )
        
        self.transcript.add_entry(
            speaker='SYSTEM',
            text_original=llm_result['text'],
            text_translation=response_translation_to_en or llm_result['text'],
            language=language,
            metadata={
                'latency_ms': llm_latency,
                'tokens_per_second': llm_result['tokens_per_second']
            }
        )
        
        total_time = (time.time() - start_time) * 1000
        
        if verbose:
            print(f"🤖 Reachy: {llm_result['text']}")
            print(f"⏱️  Latency: {total_time:.0f}ms "
                  f"(LLM: {llm_latency:.0f}ms, {llm_result['tokens_per_second']:.1f} tok/s)")
        
        return {
            "patient_text": text,
            "patient_translation": translation_to_en,
            "agent_response": llm_result['text'],
            "agent_translation": response_translation_to_en,
            "language": language,
            "latency_ms": total_time,
            "llm_latency_ms": llm_latency,
            "tts_latency_ms": tts_latency,
            "tokens_per_second": llm_result['tokens_per_second'],
            "audio_path": audio_path
        }
    
    def set_session_metadata(
        self,
        language: str = None,
        procedure: str = None,
        patient_id: str = None
    ):
        """Update session metadata"""
        self.transcript.set_metadata(language, procedure, patient_id)
    
    def export_transcript(self, output_path: str = None):
        """
        Export current transcript
        
        Args:
            output_path: Optional path, auto-generates if None
        """
        if not output_path:
            timestamp = int(time.time())
            output_path = f"data/sessions/session_{timestamp}.json"
        
        self.transcript.export_json(output_path)
        return output_path
    
    def get_transcript_summary(self) -> Dict:
        """Get transcript statistics and clinical summary"""
        return {
            "statistics": self.transcript.get_statistics(),
            "clinical_summary": self.transcript.get_clinical_summary()
        }

def interactive_mode_v2():
    """Interactive CLI mode with Week 2 features"""
    print("\n" + "="*60)
    print("CONSENT AGENT V2 - INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  quit / exit / q    - Exit")
    print("  clear              - Clear conversation history")
    print("  history            - Show conversation history")
    print("  stats              - Show resource usage")
    print("  lang <code>        - Change language (en/es/it)")
    print("  tts on/off         - Enable/disable audio output")
    print("  export             - Export transcript")
    print("\nType your message and press Enter to chat.")
    print("="*60 + "\n")
    
    # Initialize agent
    agent = ConsentAgentV2(
        enable_tts=True,  # Start with TTS off for faster testing
        enable_translation=True
    )
    
    current_language = "en"
    generate_audio = False
    
    # Set session metadata
    agent.set_session_metadata(
        language=current_language,
        procedure="colonoscopy"
    )
    
    try:
        while True:
            try:
                user_input = input(f"\nYou ({current_language.upper()}): ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Exiting...")
                    # Export final transcript
                    path = agent.export_transcript()
                    print(f"📄 Transcript saved: {path}")
                    break
                
                elif user_input.lower() == 'clear':
                    agent.transcript = TranscriptManager()
                    print("🗑️  Conversation history cleared")
                    continue
                
                elif user_input.lower() == 'history':
                    print("\n" + agent.transcript.get_formatted_transcript())
                    continue
                
                elif user_input.lower() == 'stats':
                    print()
                    print_stats()
                    continue
                
                elif user_input.lower().startswith('lang '):
                    new_lang = user_input.split()[1].lower()
                    if new_lang in ['en', 'es', 'it']:
                        current_language = new_lang
                        # agent.llm.set_language(current_language)
                        print(f"🌐 Language changed to {current_language.upper()}")
                    else:
                        print("❌ Invalid language. Use: en, es, or it")
                    continue
                
                elif user_input.lower() == 'tts on':
                    generate_audio = True
                    print("🔊 TTS enabled")
                    continue
                
                elif user_input.lower() == 'tts off':
                    generate_audio = False
                    print("🔇 TTS disabled")
                    continue
                
                elif user_input.lower() == 'export':
                    path = agent.export_transcript()
                    print(f"📄 Transcript exported: {path}")
                    summary = agent.get_transcript_summary()
                    print(f"   Total entries: {summary['statistics']['total_entries']}")
                    print(f"   Flagged: {summary['clinical_summary']['total_flagged']}")
                    continue
                
                # Process message
                result = agent.process_text(
                    user_input,
                    language=current_language,
                    generate_audio=generate_audio,
                    verbose=True
                )
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Exiting...")
                path = agent.export_transcript()
                print(f"📄 Transcript saved: {path}")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    finally:
        # Show final summary
        summary = agent.get_transcript_summary()
        print("\n" + "="*60)
        print("SESSION SUMMARY")
        print("="*60)
        stats = summary['statistics']
        print(f"Total exchanges: {stats['total_entries']}")
        print(f"Duration: {stats['duration_seconds']:.1f}s")
        print(f"Language: {stats['language']}")
        if summary['clinical_summary']['total_flagged'] > 0:
            print(f"⚠️  Flagged for review: {summary['clinical_summary']['total_flagged']}")

if __name__ == "__main__":
    interactive_mode_v2()
