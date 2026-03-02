"""Test individual components"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "app"))

def test_monitor():
    """Test monitoring utilities"""
    print("\n" + "="*50)
    print("Testing Monitor Component")
    print("="*50)
    
    try:
        from utils.monitor import print_stats, get_gpu_stats, check_resource_health
        
        print("\n1. Resource Stats:")
        print_stats()
        
        print("\n2. GPU Stats:")
        gpu = get_gpu_stats()
        print(f"   GPU Available: {gpu.get('available', False)}")
        if gpu.get('available'):
            print(f"   Name: {gpu['name']}")
            print(f"   VRAM: {gpu['memory_used_gb']:.1f}GB / {gpu['memory_total_gb']:.1f}GB")
        
        print("\n3. Health Check:")
        health = check_resource_health()
        print(f"   Status: {health['status']}")
        if health['warnings']:
            for w in health['warnings']:
                print(f"   ⚠️  {w}")
        
        print("\n✅ Monitor component working")
        return True
        
    except Exception as e:
        print(f"\n❌ Monitor test failed: {e}")
        return False

def test_stt():
    """Test Whisper STT component"""
    print("\n" + "="*50)
    print("Testing Whisper STT Component")
    print("="*50)
    
    try:
        from components.stt import WhisperSTT
        from config.config import WHISPER_MODEL_PATH
        
        if not WHISPER_MODEL_PATH.exists():
            print(f"⚠️  Model not found at {WHISPER_MODEL_PATH}")
            print("   Run scripts/download_models.py first")
            return False
        
        print("\nInitializing Whisper...")
        stt = WhisperSTT()
        
        print("\n✅ Whisper STT component working")
        print(f"   Device: {stt.device}")
        print(f"   Compute type: {stt.compute_type}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ STT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm():
    """Test Qwen3 LLM component"""
    print("\n" + "="*50)
    print("Testing Qwen3-14B-AWQ LLM Component")
    print("="*50)
    
    try:
        from components.llm import ConversationLLM
        from config.config import QWEN_MODEL_PATH
        
        if not QWEN_MODEL_PATH.exists():
            print(f"⚠️  Model not found at {QWEN_MODEL_PATH}")
            print("   Run scripts/download_models.py first")
            return False
        
        print("\nInitializing Qwen3-14B-AWQ with vLLM...")
        llm = ConversationLLM()
        
        print("\n✅ LLM initialized")
        
        # Test a simple query
        print("\nTesting simple query...")
        llm.set_procedure("colonoscopy")
        
        result = llm.generate_response(
            "What is a colonoscopy?",
            language="en"
        )
        
        print(f"\n📝 Response: {result['text'][:100]}...")
        print(f"⏱️  Latency: {result['latency_ms']:.0f}ms")
        print(f"🚀 Speed: {result['tokens_per_second']:.1f} tok/s")
        
        print("\n✅ LLM component working")
        return True
        
    except Exception as e:
        print(f"\n❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all component tests"""
    print("\n" + "="*60)
    print("COMPONENT TESTS")
    print("="*60)
    
    results = {
        "Monitor": test_monitor(),
        "Whisper STT": test_stt(),
        "Qwen3 LLM": test_llm()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {component}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nResult: {passed_count}/{total_count} components working")
    
    if passed_count == total_count:
        print("\n🎉 All components operational!")
    else:
        print("\n⚠️  Some components need attention")
        print("\nTroubleshooting:")
        if not results["Whisper STT"] or not results["Qwen3 LLM"]:
            print("- Run: python scripts/download_models.py")
        print("- Check: README.md for troubleshooting guide")

if __name__ == "__main__":
    main()
