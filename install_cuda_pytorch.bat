@echo off
echo ============================================
echo Installing PyTorch with CUDA Support
echo ============================================
echo.
echo Your GPU: NVIDIA GeForce RTX 3060 Ti
echo CUDA Version: 13.0
echo.
echo This will:
echo 1. Uninstall current CPU-only PyTorch
echo 2. Install PyTorch with CUDA 12.1 support
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/2] Uninstalling CPU-only PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo [2/2] Installing PyTorch with CUDA 12.1...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo ============================================
echo Verifying Installation
echo ============================================
python -c "import torch; print('PyTorch Version:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('CUDA Version:', torch.version.cuda); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo If CUDA Available shows "True", you're ready!
echo The server will now use GPU acceleration automatically.
echo.
pause
