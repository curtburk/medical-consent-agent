"""Performance benchmark for Week 1 implementation"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "app"))

from orchestrator import ConsentAgent
from utils.monitor import print_stats, get_gpu_stats

def run_benchmark():
    """Run comprehensive performance benchmarks"""
    
    print("\n" + "="*60)
    print("CONSENT AGENT - PERFORMANCE BENCHMARK")
    print("="*60)
    
    # Initialize agent
    agent = ConsentAgent()
    
    # Test queries covering different complexity levels
    test_queries = [
        ("What is a colonoscopy?", "en"),
        ("Why do I need to drink the preparation liquid?", "en"),
        ("Will the procedure be painful?", "en"),
        ("How long does it take?", "en"),
        ("When can I eat after the procedure?", "en"),
        ("¿Qué es una colonoscopia?", "es"),
        ("¿Por qué necesito beber el líquido de preparación?", "es"),
        ("Che cos'è una colonscopia?", "it")
    ]
    
    print("\n" + "="*60)
    print("RUNNING BENCHMARKS")
    print("="*60)
    
    results = []
    
    for i, (query, lang) in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Testing: {query[:50]}...")
        
        try:
            result = agent.process_text(query, language=lang, verbose=False)
            results.append(result)
            
            print(f"✅ Latency: {result['latency_ms']:.0f}ms | "
                  f"Speed: {result['tokens_per_second']:.1f} tok/s")
            
            # Brief pause between queries
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"error": str(e), "latency_ms": 0})
    
    # Calculate statistics
    valid_results = [r for r in results if "error" not in r]
    
    if not valid_results:
        print("\n❌ All benchmarks failed!")
        return
    
    latencies = [r['latency_ms'] for r in valid_results]
    speeds = [r['tokens_per_second'] for r in valid_results]
    
    min_latency = min(latencies)
    max_latency = max(latencies)
    avg_latency = sum(latencies) / len(latencies)
    
    min_speed = min(speeds)
    max_speed = max(speeds)
    avg_speed = sum(speeds) / len(speeds)
    
    # Display results
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    
    print(f"\n📊 Latency Statistics:")
    print(f"   Minimum: {min_latency:.0f}ms")
    print(f"   Maximum: {max_latency:.0f}ms")
    print(f"   Average: {avg_latency:.0f}ms")
    print(f"   Target:  <2500ms (Week 1)")
    
    if avg_latency < 2500:
        print(f"   ✅ PASS - Meeting Week 1 targets")
    else:
        print(f"   ⚠️  NEEDS OPTIMIZATION")
    
    print(f"\n🚀 Throughput Statistics:")
    print(f"   Minimum: {min_speed:.1f} tokens/sec")
    print(f"   Maximum: {max_speed:.1f} tokens/sec")
    print(f"   Average: {avg_speed:.1f} tokens/sec")
    
    # Show detailed breakdown for first test
    if len(valid_results) > 0:
        first = valid_results[0]
        print(f"\n🔍 Detailed Breakdown (first query):")
        print(f"   LLM processing: {first.get('llm_latency_ms', 0):.0f}ms")
        print(f"   Total pipeline: {first['latency_ms']:.0f}ms")
    
    # Resource usage
    print("\n" + "="*60)
    print_stats(show_title=False)
    
    # Check if meeting tech spec requirements
    gpu_stats = get_gpu_stats()
    
    print("\n📋 Tech Spec Compliance:")
    
    # VRAM target: <20GB for Week 1
    if gpu_stats["available"]:
        vram_used = gpu_stats["memory_used_gb"]
        print(f"   VRAM Usage: {vram_used:.1f}GB / 20GB target")
        if vram_used < 20:
            print(f"   ✅ VRAM within target")
        else:
            print(f"   ⚠️  VRAM exceeds target")
    
    # Latency target: <2.5s for Week 1
    print(f"   Avg Latency: {avg_latency:.0f}ms / 2500ms target")
    if avg_latency < 2500:
        print(f"   ✅ Latency within target")
    else:
        print(f"   ⚠️  Latency exceeds target")
    
    # Success rate
    success_rate = (len(valid_results) / len(test_queries)) * 100
    print(f"   Success Rate: {success_rate:.0f}%")
    if success_rate == 100:
        print(f"   ✅ All queries successful")
    else:
        print(f"   ⚠️  Some queries failed")
    
    print("\n" + "="*60)
    
    if avg_latency < 2500 and success_rate == 100:
        print("🎉 WEEK 1 BENCHMARKS: PASSED")
    else:
        print("⚠️  WEEK 1 BENCHMARKS: NEEDS IMPROVEMENT")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    run_benchmark()
