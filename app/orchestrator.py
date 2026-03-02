"""Main Consent Agent orchestrator - Week 1 text-only version"""

import time
import sys
from pathlib import Path
from typing import Dict, Optional

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent))

from components.stt import WhisperSTT
from components.llm import ConversationLLM
# DON'T import monitor here - it initializes CUDA too early

class ConsentAgent:
    """
    Multilingual Patient Consent Verification Agent
    Week 1: Text-only pipeline (Whisper + Qwen3-14B-AWQ)
    """
    
    def __init__(self):
        """Initialize all components"""
        print("\n" + "="*60)
        print("INITIALIZING CONSENT AGENT")
        print("="*60)
        
        # Initialize STT (skip if models not available)
        print("\n[1/2] Initializing Speech-to-Text...")
        try:
            self.stt = WhisperSTT()
        except Exception as e:
            print(f"❌ Failed to load Whisper: {e}")
            print("   Continuing without STT (text-only mode)")
            self.stt = None
        
        # Initialize LLM (must happen before monitor import)
        print("\n[2/2] Initializing Conversation LLM...")
        self.llm = ConversationLLM()
        
        # Set default procedure
        self.llm.set_procedure("colonoscopy")
        
        # NOW import and use monitoring (after CUDA is initialized by vLLM)
        try:
            from utils.monitor import print_stats, check_resource_health
            print("\n📊 Resource state after initialization:")
            print_stats(show_title=False)
            
            health = check_resource_health()
            if health["status"] == "healthy":
                print("✅ All systems nominal")
            elif health["status"] == "warning":
                print("⚠️  System warnings detected:")
                for warning in health["warnings"]:
                    print(f"   - {warning}")
        except Exception as e:
            print(f"⚠️  Monitoring not available: {e}")
        
        print("\n" + "="*60)
        print("AGENT READY")
        print("="*60 + "\n")
    
    def process_text(
        self,
        text: str,
        language: str = "en",
        verbose: bool = True
    ) -> Dict:
        """
        Process text input (Week 1: text-only mode)
        
        Args:
            text: User's text input
            language: Language code (en, es, it)
            verbose: Whether to print progress
        
        Returns:
            Dict with processing results
        """
        start_time = time.time()
        
        if verbose:
            print(f"👤 Patient ({language.upper()}): {text}")
        
        # Generate response with LLM
        llm_start = time.time()
        llm_result = self.llm.generate_response(text, language)
        llm_time = time.time() - llm_start
        
        total_time = time.time() - start_time
        
        if verbose:
            print(f"🤖 Reachy: {llm_result['text']}")
            print(f"⏱️  Latency: {total_time * 1000:.0f}ms "
                  f"(LLM: {llm_time * 1000:.0f}ms, {llm_result['tokens_per_second']:.1f} tok/s)")
        
        return {
            "patient_text": text,
            "agent_response": llm_result['text'],
            "language": language,
            "latency_ms": total_time * 1000,
            "llm_latency_ms": llm_time * 1000,
            "tokens_per_second": llm_result['tokens_per_second']
        }
    
    def process_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Process audio input (full pipeline)
        
        Args:
            audio_path: Path to audio file
            language: Language code or None for auto-detect
            verbose: Whether to print progress
        
        Returns:
            Dict with processing results
        """
        if self.stt is None:
            print("❌ STT not available - use process_text() instead")
            return {"error": "STT not initialized"}
        
        start_time = time.time()
        
        if verbose:
            print(f"🎤 Transcribing audio...")
        
        # Transcribe with Whisper
        stt_result = self.stt.transcribe(audio_path, language)
        
        if verbose:
            print(f"📝 Patient ({stt_result['language'].upper()}): {stt_result['text']}")
            print(f"   STT latency: {stt_result['latency_ms']:.0f}ms")
        
        # Generate response
        llm_result = self.llm.generate_response(
            stt_result['text'],
            stt_result['language']
        )
        
        total_time = time.time() - start_time
        
        if verbose:
            print(f"🤖 Reachy: {llm_result['text']}")
            print(f"⏱️  Total latency: {total_time * 1000:.0f}ms "
                  f"(STT: {stt_result['latency_ms']:.0f}ms, "
                  f"LLM: {llm_result['latency_ms']:.0f}ms)")
        
        return {
            "patient_text": stt_result['text'],
            "agent_response": llm_result['text'],
            "language": stt_result['language'],
            "stt_confidence": stt_result['confidence'],
            "latency_ms": total_time * 1000,
            "stt_latency_ms": stt_result['latency_ms'],
            "llm_latency_ms": llm_result['latency_ms'],
            "tokens_per_second": llm_result['tokens_per_second']
        }
    
    def set_procedure(self, procedure: str):
        """Set the current medical procedure context"""
        self.llm.set_procedure(procedure)
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.llm.clear_history()
    
    def get_conversation_history(self):
        """Get full conversation history"""
        return self.llm.get_history()

def interactive_mode():
    """Run agent in interactive CLI mode"""
    agent = ConsentAgent()
    
    print("\n" + "="*60)
    print("CONSENT AGENT - INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  quit / exit / q    - Exit")
    print("  clear              - Clear conversation history")
    print("  history            - Show conversation history")
    print("  stats              - Show resource usage")
    print("  lang <code>        - Change language (en/es/it)")
    print("\nType your message and press Enter to chat.")
    print("="*60 + "\n")
    
    current_language = "en"
    
    while True:
        try:
            user_input = input(f"You ({current_language.upper()}): ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                agent.clear_conversation()
                print("🔄 Conversation cleared\n")
                continue
            
            elif user_input.lower() == 'history':
                history = agent.get_conversation_history()
                print("\n📜 Conversation History:")
                for i, msg in enumerate(history, 1):
                    role_emoji = "👤" if msg["role"] == "user" else "🤖"
                    print(f"{i}. {role_emoji} {msg['role'].title()}: {msg['content']}")
                print()
                continue
            
            elif user_input.lower() == 'stats':
                try:
                    from utils.monitor import print_stats
                    print_stats()
                except Exception as e:
                    print(f"⚠️  Stats not available: {e}\n")
                continue
            
            elif user_input.lower().startswith('lang '):
                lang_code = user_input.split()[1].lower()
                if lang_code in ['en', 'es', 'it']:
                    current_language = lang_code
                    print(f"🌐 Language changed to {lang_code.upper()}\n")
                else:
                    print("❌ Invalid language. Use: en, es, or it\n")
                continue
            
            # Process message
            result = agent.process_text(user_input, language=current_language)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    interactive_mode()