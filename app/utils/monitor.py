"""System resource monitoring utilities"""

import psutil
import GPUtil
from typing import Dict, Optional
import torch

def get_gpu_stats() -> Dict:
    """
    Get GPU utilization statistics
    
    Returns:
        Dict with GPU stats or availability status
    """
    gpus = GPUtil.getGPUs()
    if not gpus:
        return {"available": False}
    
    gpu = gpus[0]  # First GPU (GB10)
    
    # Also get PyTorch CUDA memory if available
    torch_memory_allocated = 0
    torch_memory_reserved = 0
    if torch.cuda.is_available():
        torch_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)  # GB
        torch_memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)  # GB
    
    return {
        "available": True,
        "name": gpu.name,
        "memory_used_gb": gpu.memoryUsed / 1024,
        "memory_total_gb": gpu.memoryTotal / 1024,
        "memory_free_gb": (gpu.memoryTotal - gpu.memoryUsed) / 1024,
        "memory_percent": gpu.memoryUtil * 100,
        "gpu_percent": gpu.load * 100,
        "temperature": gpu.temperature,
        "torch_memory_allocated_gb": torch_memory_allocated,
        "torch_memory_reserved_gb": torch_memory_reserved
    }

def get_system_stats() -> Dict:
    """
    Get system resource statistics
    
    Returns:
        Dict with CPU and RAM stats
    """
    mem = psutil.virtual_memory()
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(),
        "ram_used_gb": mem.used / (1024**3),
        "ram_total_gb": mem.total / (1024**3),
        "ram_available_gb": mem.available / (1024**3),
        "ram_percent": mem.percent
    }

def print_stats(show_title: bool = True):
    """
    Print current resource usage in formatted table
    
    Args:
        show_title: Whether to show the table header
    """
    gpu_stats = get_gpu_stats()
    sys_stats = get_system_stats()
    
    if show_title:
        print("\n" + "="*60)
        print("RESOURCE USAGE")
        print("="*60)
    
    if gpu_stats["available"]:
        print(f"\n📊 GPU: {gpu_stats['name']}")
        print(f"   VRAM: {gpu_stats['memory_used_gb']:.1f}GB / {gpu_stats['memory_total_gb']:.1f}GB "
              f"({gpu_stats['memory_percent']:.1f}%) | Free: {gpu_stats['memory_free_gb']:.1f}GB")
        
        if gpu_stats['torch_memory_allocated_gb'] > 0:
            print(f"   PyTorch: Allocated {gpu_stats['torch_memory_allocated_gb']:.1f}GB, "
                  f"Reserved {gpu_stats['torch_memory_reserved_gb']:.1f}GB")
        
        print(f"   Utilization: {gpu_stats['gpu_percent']:.1f}%")
        print(f"   Temperature: {gpu_stats['temperature']}°C")
    else:
        print("\n❌ GPU: Not available")
    
    print(f"\n💻 CPU: {sys_stats['cpu_percent']:.1f}% ({sys_stats['cpu_count']} cores)")
    print(f"   RAM: {sys_stats['ram_used_gb']:.1f}GB / {sys_stats['ram_total_gb']:.1f}GB "
          f"({sys_stats['ram_percent']:.1f}%) | Available: {sys_stats['ram_available_gb']:.1f}GB")
    
    if show_title:
        print("="*60 + "\n")

def get_vram_headroom() -> Optional[float]:
    """
    Calculate available VRAM headroom
    
    Returns:
        Available VRAM in GB, or None if GPU not available
    """
    gpu_stats = get_gpu_stats()
    if not gpu_stats["available"]:
        return None
    
    return gpu_stats["memory_free_gb"]

def check_resource_health() -> Dict:
    """
    Check if resources are within healthy ranges
    
    Returns:
        Dict with health status and warnings
    """
    gpu_stats = get_gpu_stats()
    sys_stats = get_system_stats()
    
    warnings = []
    status = "healthy"
    
    # Check VRAM usage (target <90GB of 119.6GB total)
    if gpu_stats["available"]:
        if gpu_stats["memory_used_gb"] > 90:
            warnings.append(f"High VRAM usage: {gpu_stats['memory_used_gb']:.1f}GB")
            status = "warning"
        
        if gpu_stats["gpu_percent"] > 95:
            warnings.append(f"High GPU utilization: {gpu_stats['gpu_percent']:.1f}%")
            status = "warning"
        
        if gpu_stats["temperature"] > 85:
            warnings.append(f"High GPU temperature: {gpu_stats['temperature']}°C")
            status = "warning"
    else:
        warnings.append("GPU not available")
        status = "error"
    
    # Check CPU and RAM
    if sys_stats["cpu_percent"] > 80:
        warnings.append(f"High CPU usage: {sys_stats['cpu_percent']:.1f}%")
        if status == "healthy":
            status = "warning"
    
    if sys_stats["ram_percent"] > 90:
        warnings.append(f"High RAM usage: {sys_stats['ram_percent']:.1f}%")
        if status == "healthy":
            status = "warning"
    
    return {
        "status": status,
        "warnings": warnings,
        "gpu_stats": gpu_stats,
        "system_stats": sys_stats
    }

if __name__ == "__main__":
    print_stats()
    
    print("\n🏥 Resource Health Check:")
    health = check_resource_health()
    print(f"   Status: {health['status']}")
    
    if health['warnings']:
        print("   Warnings:")
        for warning in health['warnings']:
            print(f"     ⚠️  {warning}")
    else:
        print("   ✅ All resources within healthy ranges")
