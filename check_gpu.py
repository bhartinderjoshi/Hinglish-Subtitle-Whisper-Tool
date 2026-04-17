#!/usr/bin/env python
"""
Check GPU availability and configuration
"""
import torch

print("=" * 60)
print("GPU CONFIGURATION CHECK")
print("=" * 60)

print("\n1. PyTorch Information:")
print(f"   PyTorch Version: {torch.__version__}")
print(f"   CUDA Built Version: {torch.version.cuda}")

print("\n2. CUDA Availability:")
cuda_available = torch.cuda.is_available()
print(f"   CUDA Available: {cuda_available}")

if cuda_available:
    print("\n3. GPU Information:")
    print(f"   GPU Count: {torch.cuda.device_count()}")
    print(f"   Current GPU: {torch.cuda.current_device()}")
    print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
    
    print("\n4. GPU Memory:")
    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"   Total Memory: {total_memory:.2f} GB")
    
    allocated = torch.cuda.memory_allocated(0) / (1024**3)
    reserved = torch.cuda.memory_reserved(0) / (1024**3)
    print(f"   Allocated: {allocated:.2f} GB")
    print(f"   Reserved: {reserved:.2f} GB")
    print(f"   Free: {total_memory - reserved:.2f} GB")
    
    print("\n5. CUDA Capabilities:")
    capability = torch.cuda.get_device_capability(0)
    print(f"   Compute Capability: {capability[0]}.{capability[1]}")
    
    print("\n✅ GPU is ready for use!")
    print("\nThe server will automatically use GPU when you run:")
    print("   python web_server.py")
    print("\nOr explicitly specify:")
    print("   python web_server.py --device cuda")
    
else:
    print("\n❌ CUDA is NOT available!")
    print("\nPossible reasons:")
    print("1. PyTorch CPU-only version installed")
    print("2. NVIDIA drivers not installed")
    print("3. No NVIDIA GPU in system")
    
    print("\nTo install PyTorch with CUDA support:")
    print("   Run: install_cuda_pytorch.bat")
    print("   Or manually:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

print("\n" + "=" * 60)
