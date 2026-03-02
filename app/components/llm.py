"""Conversational LLM using Qwen3-14B-AWQ with vLLM"""

import time
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import QWEN_MODEL_PATH, VLLM_CONFIG, SYSTEM_PROMPTS, PROCEDURE_INFO

class ConversationLLM:
    """Qwen3-14B-AWQ conversational AI using vLLM for inference"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize vLLM with Qwen3-14B-AWQ
        
        Args:
            model_path: Path to model (uses config default if None)
        """
        from vllm import LLM, SamplingParams
        
        self.model_path = model_path or str(QWEN_MODEL_PATH)
        self.LLM = LLM  # Store class reference
        self.SamplingParams = SamplingParams
        
        print(f"🧠 Loading Qwen3-14B-AWQ with vLLM...")
        start_time = time.time()
        
        # Initialize vLLM engine
        self.llm = LLM(
            model=self.model_path,
            quantization=VLLM_CONFIG["quantization"],
            dtype=VLLM_CONFIG["dtype"],
            max_model_len=VLLM_CONFIG["max_model_len"],
            gpu_memory_utilization=VLLM_CONFIG["gpu_memory_utilization"],
            tensor_parallel_size=VLLM_CONFIG["tensor_parallel_size"],
            trust_remote_code=VLLM_CONFIG["trust_remote_code"]
        )
        
        # Default sampling parameters
        self.default_sampling_params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=512,
            stop=["<|endoftext|>", "<|im_end|>"]
        )
        
        load_time = time.time() - start_time
        print(f"✅ Qwen3-14B-AWQ loaded in {load_time:.1f}s")
        
        # Track conversation history
        self.conversation_history: List[Dict[str, str]] = []
        self.current_language = "en"
        self.current_procedure = None
    
    def _build_prompt(self, user_message: str, language: str = "en") -> str:
        """
        Build chat prompt with conversation history
        
        Args:
            user_message: User's message
            language: Language code (en, es, it)
        
        Returns:
            Formatted prompt string
        """
        # Start with system prompt
        system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
        
        # Add procedure context if available
        if self.current_procedure:
            procedure_context = PROCEDURE_INFO.get(self.current_procedure, {}).get(language, {})
            if procedure_context:
                context_text = "\n\n".join([
                    f"**{key.title()}**: {value}"
                    for key, value in procedure_context.items()
                ])
                system_prompt += f"\n\nProcedure Information:\n{context_text}"
        
        # Build conversation in Qwen3 chat format
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 4 exchanges to stay concise)
        for msg in self.conversation_history[-8:]:  # Last 4 exchanges = 8 messages
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Format as Qwen3 chat template
        prompt = self._format_qwen3_chat(messages)
        
        return prompt
    
    def _format_qwen3_chat(self, messages: List[Dict[str, str]]) -> str:
        """Format messages in Qwen3 chat template"""
        formatted = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == "user":
                formatted += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                formatted += f"<|im_start|>assistant\n{content}<|im_end|>\n"
        
        # Add final assistant prompt
        formatted += "<|im_start|>assistant\n"
        
        return formatted
    
    def generate_response(
        self,
        user_message: str,
        language: str = "en",
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate conversational response
        
        Args:
            user_message: User's input text
            language: Language code (en, es, it)
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            Dict with keys:
                - text: Generated response
                - language: Language used
                - latency_ms: Generation time
                - tokens_per_second: Inference speed
        """
        start_time = time.time()
        self.current_language = language
        
        # Build prompt
        prompt = self._build_prompt(user_message, language)
        
        # Set sampling parameters with stop tokens to prevent reasoning
        sampling_params = self.SamplingParams(
            temperature=temperature,
            top_p=0.9,
            max_tokens=512,
            stop=["<|endoftext|>", "<|im_end|>"]
        )
        
        # Generate with vLLM
        outputs = self.llm.generate([prompt], sampling_params)
        
        # Extract response
        response_text = outputs[0].outputs[0].text.strip()
        
        # POST-PROCESSING: Remove <think> tags and content
        import re
        response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        response_text = response_text.strip()
        
        # Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        num_tokens = len(outputs[0].outputs[0].token_ids)
        tokens_per_second = num_tokens / (latency_ms / 1000) if latency_ms > 0 else 0
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        return {
            "text": response_text,
            "language": language,
            "latency_ms": latency_ms,
            "tokens_per_second": tokens_per_second,
            "num_tokens": num_tokens
        }
    
    def set_procedure(self, procedure: str):
        """Set current procedure context (e.g., 'colonoscopy')"""
        if procedure in PROCEDURE_INFO:
            self.current_procedure = procedure
            print(f"📋 Procedure context set: {procedure}")
        else:
            print(f"⚠️  Unknown procedure: {procedure}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🔄 Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()

def test_llm():
    """Test LLM component"""
    print("\n" + "="*50)
    print("Qwen3-14B-AWQ LLM Component Test")
    print("="*50)
    
    # Check if model exists
    if not QWEN_MODEL_PATH.exists():
        print(f"❌ Model not found at {QWEN_MODEL_PATH}")
        print("   Run scripts/download_models.py first")
        return
    
    # Initialize
    llm = ConversationLLM()
    
    print("\n✅ LLM component ready")
    print(f"   Model: Qwen3-14B-AWQ")
    print(f"   Context window: {VLLM_CONFIG['max_model_len']} tokens")
    print(f"   Quantization: {VLLM_CONFIG['quantization']}")
    
    # Set procedure context
    llm.set_procedure("colonoscopy")
    
    # Test conversation
    print("\n" + "="*50)
    print("Test Conversation (English)")
    print("="*50)
    
    test_queries = [
        "Hello, what is a colonoscopy?",
        "Why do I need to drink that preparation liquid?",
        "Will it hurt?"
    ]
    
    for query in test_queries:
        print(f"\n👤 Patient: {query}")
        result = llm.generate_response(query, language="en")
        print(f"🤖 Reachy: {result['text']}")
        print(f"⏱️  Latency: {result['latency_ms']:.0f}ms | Speed: {result['tokens_per_second']:.1f} tok/s")
    
    print("\n✅ LLM test complete!")

if __name__ == "__main__":
    test_llm()