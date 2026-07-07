# 🚀 Free Deployment Guide

## Option 1: Hugging Face Spaces (RECOMMENDED - FREE 24/7)

### Steps:
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose:
   - Space name: `whisper-subtitle-generator`
   - License: `Apache 2.0`
   - Space SDK: `Gradio`
   - Space hardware: `CPU basic` (FREE)
4. Upload these files:
   - All `.py` files
   - All folders (`templates/`, `tests/`, `docs/`, `examples/`)
   - `requirements.txt`
   - `README.md`
5. Wait 2-3 minutes for build
6. Your app will be live at: `https://huggingface.co/spaces/YOUR_USERNAME/whisper-subtitle-generator`

### Important:
- Free tier is CPU-only (slower processing)
- Can upgrade to GPU for $0.60/hour if needed
- 16GB RAM, 8 CPU cores on free tier

---

## Option 2: Google Colab (FREE GPU!)

### Steps:
1. Open: https://colab.research.google.com
2. New Notebook → Copy this code:

```python
# Install dependencies
!pip install -q transformers torch flask werkzeug

# Clone your repo (or upload files)
!git clone YOUR_GITHUB_REPO_URL
%cd YOUR_REPO_NAME

# Install ngrok for public URL
!pip install pyngrok -q
from pyngrok import ngrok

# Start server in background
import subprocess
import time
proc = subprocess.Popen(['python', 'web_server.py', '--host', '0.0.0.0', '--port', '5000'])
time.sleep(3)

# Get public URL
public_url = ngrok.connect(5000)
print("🎉 Your app is live at:", public_url)
```

3. Run the cell
4. Share the ngrok URL
5. Keep browser tab open

### Limitations:
- Must keep browser open
- Session ends after 12 hours
- Need to restart manually

---

## Option 3: Railway.app (FREE $5/month credit)

### Steps:
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python and deploys
6. Get public URL from "Settings" → "Domains"

### Limitations:
- $5 free credit per month
- Runs out with heavy usage
- CPU-only

---

## Option 4: Render.com (FREE tier)

### Steps:
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect GitHub repo
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python web_server.py --host 0.0.0.0 --port 10000`
6. Click "Create Web Service"
7. Get URL from dashboard

### Limitations:
- Spins down after 15 min inactivity
- Slow cold starts (30-60 seconds)
- CPU-only

---

## 💰 Cost Comparison

| Platform | Cost | GPU | Uptime | Speed |
|----------|------|-----|--------|-------|
| **Hugging Face** | FREE | Optional ($0.60/hr) | 24/7 | Medium |
| **Google Colab** | FREE | Yes | 12hr sessions | Fast |
| **Railway** | $5 credit/month | No | 24/7 | Medium |
| **Render** | FREE | No | Sleeps after 15min | Slow |

---

## 📌 Recommendation

**For 24/7 free hosting:** Use Hugging Face Spaces

**For GPU processing:** Use Google Colab (but need to keep open)

**For quick test:** Use Railway.app ($5 credit)

---

## 🆘 Need Help?

If you get stuck, let me know which platform you chose!
