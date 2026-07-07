# 🚀 Deploy to Hugging Face Spaces (FREE 24/7)

## Step-by-Step Guide

### Step 1: Create Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up (free, no credit card needed)
3. Verify your email

### Step 2: Create New Space
1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Owner:** Your username
   - **Space name:** `whisper-subtitle-generator` (or any name you like)
   - **License:** Apache 2.0
   - **Select the Space SDK:** Choose **Docker**
   - **Space hardware:** CPU basic - **FREE**
3. Click **"Create Space"**

### Step 3: Upload Files
You need to upload these files to your Space:

**Required Files:**
1. `Dockerfile`
2. `requirements.txt`
3. `web_server.py`
4. `video_to_srt.py`
5. `logger.py`
6. `utils.py`
7. `MODEL_INFO.txt`

**Required Folders:**
1. `templates/` (with all HTML files inside)

**How to Upload:**
1. In your Space, click **"Files and versions"** tab
2. Click **"Add file"** → **"Upload files"**
3. Drag and drop all the files listed above
4. Click **"Commit changes to main"**

### Step 4: Wait for Build
1. Go to **"App"** tab
2. Wait 3-5 minutes while it builds
3. You'll see build logs
4. When done, you'll see "Running" status

### Step 5: Get Your URL
Your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/whisper-subtitle-generator
```

Example: `https://huggingface.co/spaces/johndoe/whisper-subtitle-generator`

### Step 6: Share It!
- Share the URL with anyone
- They can use it for free
- No login required for users

---

## 📋 What Files Do You Need?

I've already created everything you need. Just upload:

### Core Files:
- ✅ Dockerfile (already created)
- ✅ requirements.txt
- ✅ web_server.py
- ✅ video_to_srt.py
- ✅ logger.py
- ✅ utils.py
- ✅ MODEL_INFO.txt

### Folders:
- ✅ templates/ folder with:
  - editor.html
  - launcher.html
  - upload.html

---

## 🐛 Troubleshooting

### Build Failed?
- Check if all files are uploaded
- Make sure Dockerfile is in root directory
- Check build logs for errors

### App Not Loading?
- Wait 5 minutes for first build
- Refresh the page
- Check "Build" tab for logs

### Out of Memory?
- Free tier has 16GB RAM
- For large files, users might need to wait longer
- Consider upgrading to paid tier if needed

---

## 💰 Costs

**Free Tier:**
- ✅ FREE forever
- ✅ 16GB RAM
- ✅ 8 CPU cores
- ✅ Always online
- ❌ CPU-only (slower for large files)

**Upgrade Options (if you want GPU later):**
- T4 small: $0.60/hour (only when processing)
- T4 medium: $1.05/hour
- A10G small: $3.15/hour

---

## 🎉 That's It!

Your app will be live 24/7 for FREE!

Share your URL with anyone and they can generate subtitles!

---

## Need Help?

If you get stuck:
1. Check Hugging Face docs: https://huggingface.co/docs/hub/spaces
2. Ask in their Discord: https://hf.co/join/discord
3. Or message me!
