#!/usr/bin/env python3
"""
Cross-platform launcher for Whisper Hindi2Hinglish Video to SRT Converter.
Checks Python version, FFmpeg, and all dependencies. Installs missing packages automatically.
Works on macOS, Windows, and Linux.
"""
import os
import sys
import subprocess
import platform
import shutil
import importlib
import time

# ── Config ──────────────────────────────────────────────────────────────────
REQUIRED_PYTHON = (3, 9)
REQUIREMENTS_FILE = "requirements.txt"
WEB_SERVER = "web_server.py"
DEFAULT_PORT = 5000

# Packages to check: (import_name, pip_name)
REQUIRED_PACKAGES = [
    ("flask", "flask"),
    ("torch", "torch"),
    ("torchaudio", "torchaudio"),
    ("torchvision", "torchvision"),
    ("transformers", "transformers"),
    ("accelerate", "accelerate"),
    ("whisper_timestamped", "whisper-timestamped"),
    ("webrtcvad", "webrtcvad"),
    ("librosa", "librosa"),
    ("numpy", "numpy"),
    ("websockets", "websockets"),
    ("werkzeug", "werkzeug"),
]

# ── Helpers ──────────────────────────────────────────────────────────────────
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def banner():
    print()
    print(f"{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}  Whisper Hindi2Hinglish - Video to SRT Converter{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")
    print()


def status(msg, ok=True):
    icon = f"{GREEN}+{RESET}" if ok else f"{RED}X{RESET}"
    print(f"  {icon} {msg}")


def info(msg):
    print(f"  {YELLOW}!{RESET} {msg}")


def section(num, total, title):
    print(f"{BOLD}[{num}/{total}]{RESET} {title}...")
    print()


# ── Checks ──────────────────────────────────────────────────────────────────
def check_python():
    v = sys.version_info
    if v < REQUIRED_PYTHON:
        print(f"{RED}X Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ required, found {v.major}.{v.minor}.{v.micro}{RESET}")
        print()
        print("  Install Python from: https://www.python.org/downloads/")
        if IS_WINDOWS:
            print("  IMPORTANT: Check 'Add Python to PATH' during installation")
        print()
        wait_for_exit()
        return False
    status(f"Python {v.major}.{v.minor}.{v.micro}")
    return True


def find_python_executable():
    for name in ("python3", "python"):
        path = shutil.which(name)
        if path:
            return path
    return sys.executable


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        status("FFmpeg found")
        return True

    status("FFmpeg not found (video processing requires FFmpeg)", ok=False)

    if IS_MAC:
        if shutil.which("brew"):
            info("Attempting install via Homebrew...")
            r = subprocess.run(["brew", "install", "ffmpeg"], capture_output=False)
            if r.returncode == 0:
                status("FFmpeg installed via Homebrew")
                return True
        info("Install Homebrew: https://brew.sh, then: brew install ffmpeg")
        info("Or download from: https://ffmpeg.org/download.html")

    elif IS_WINDOWS:
        info("Attempting install via winget...")
        r = subprocess.run(["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--silent"], capture_output=False)
        if r.returncode == 0:
            status("FFmpeg installed via winget")
            info("Restart this script for FFmpeg to be recognized.")
            return False
        info("Install manually from: https://ffmpeg.org/download.html")

    elif IS_LINUX:
        info("Attempting install via apt...")
        cmd_prefix = []
        try:
            if os.geteuid() != 0:
                cmd_prefix = ["sudo"]
        except AttributeError:
            pass
        r = subprocess.run(cmd_prefix + ["apt-get", "install", "-y", "ffmpeg"], capture_output=False)
        if r.returncode == 0:
            status("FFmpeg installed via apt")
            return True
        info("Install manually: https://ffmpeg.org/download.html")

    print()
    info("Server will start but video conversion may fail without FFmpeg")
    return False


def is_package_installed(import_name):
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def install_packages():
    py = find_python_executable()
    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), REQUIREMENTS_FILE)
    if not os.path.exists(req_path):
        info(f"{REQUIREMENTS_FILE} not found, skipping pip install")
        return False

    print(f"  Installing from {REQUIREMENTS_FILE} (this may take a few minutes)...")
    print()
    r = subprocess.run([py, "-m", "pip", "install", "-r", req_path])
    return r.returncode == 0


def check_all_packages():
    missing_import = []
    missing_pip = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        if is_package_installed(import_name):
            status(f"{pip_name}")
        else:
            status(f"{pip_name} - NOT INSTALLED", ok=False)
            missing_import.append(import_name)
            missing_pip.append(pip_name)

    if not missing_import:
        return True

    print()
    info(f"{len(missing_import)} package(s) missing")
    print()
    choice = input("  Install missing packages now? [Y/n] ").strip().lower()
    if choice in ("", "y", "yes"):
        print()
        if install_packages():
            print()
            # Verify after install
            still_missing = []
            for import_name, pip_name in REQUIRED_PACKAGES:
                if not is_package_installed(import_name):
                    still_missing.append(pip_name)
            if still_missing:
                status(f"Still missing after install: {', '.join(still_missing)}", ok=False)
                print()
                wait_for_exit()
                return False
            status("All packages installed successfully")
            return True
        else:
            status("Package installation failed", ok=False)
            print()
            wait_for_exit()
            return False
    else:
        info("Cannot start without required packages")
        print()
        wait_for_exit()
        return False


def detect_device():
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            mem = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
            return "cuda", f"GPU: {name} ({mem:.1f} GB)"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps", "Apple Silicon (MPS)"
    except Exception:
        pass
    return "cpu", "CPU"


def get_port():
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            pass
    return DEFAULT_PORT


def wait_for_exit():
    if IS_WINDOWS:
        input("  Press Enter to exit...")
    else:
        print("  Press Enter to exit...")
        input()


def open_browser(url):
    import webbrowser
    try:
        webbrowser.open(url)
    except Exception:
        pass


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    banner()

    total = 5

    # 1 – Python
    section(1, total, "Checking Python")
    if not check_python():
        return
    print()

    # 2 – FFmpeg
    section(2, total, "Checking FFmpeg")
    ffmpeg_ok = check_ffmpeg()
    print()

    # 3 – Packages
    section(3, total, "Checking Python packages")
    if not check_all_packages():
        return
    print()

    # 4 – Device info
    section(4, total, "Detecting compute device")
    device, device_label = detect_device()
    status(f"Device: {device_label}")
    print()

    # 5 – Start server
    port = get_port()
    section(5, total, f"Starting web server on port {port}")

    url = f"http://localhost:{port}"
    status(f"URL: {url}")
    print()

    # Small delay then open browser
    import threading
    threading.Timer(2.0, open_browser, args=[url,]).start()

    try:
        from web_server import app
        app.run(host="0.0.0.0", port=port, debug=False)
    except KeyboardInterrupt:
        print()
        status("Server stopped")
    except Exception as e:
        print()
        status(f"Error: {e}", ok=False)
        print()
        wait_for_exit()


if __name__ == "__main__":
    main()
