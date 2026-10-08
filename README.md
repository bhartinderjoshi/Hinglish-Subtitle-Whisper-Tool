---
title: Whisper Subtitle Generator
emoji: 🎬
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
---

# **Whisper-Hindi2Hinglish + Video-to-SRT**

> **🔗 Fork Notice**: This is a fork of [OriserveAI/Whisper-Hindi2Hinglish](https://github.com/OriserveAI/Whisper-Hindi2Hinglish) by Oriserve AI team.
>
> **✨ Added Features**: Video-to-SRT subtitle generation with web UI, CLI, and REST API
>
> **Original Authors**: OriserveAI (ai-team@oriserve.com)
> **Fork Maintainer**: Sanjog Bora ([@sanjogbora](https://github.com/sanjogbora))
> **License**: Apache-2.0 (same as upstream)

---

## **🚀 Quick Start for Non-Technical Users**

Want to convert your Hindi-English videos to subtitle files? It's as easy as double-clicking a file!

### **One-Click Launch (Easiest Method)**

1. **Download this project:**
   - Click the green "Code" button at the top of this page
   - Click "Download ZIP"
   - Extract the ZIP file to a folder (e.g., Desktop or Documents)

2. **Double-click the launcher:**
   - **Windows:** Double-click `START HERE.bat`
   - **Mac:** Double-click `START HERE.command`
   - **Linux:** Run `./START HERE.sh`

3. **Let it set up automatically:**
   - The launcher will check for Python and FFmpeg
   - It will install missing dependencies automatically
   - Your browser will open automatically
   - **No terminal commands needed!**

4. **Use the app:**
   - Drag and drop your video file
   - Choose quality: **Apex** (ultimate), **Prime** (best), or **Swift** (faster)
   - Customize subtitle formatting (optional):
     - Max words per subtitle (2-10, default: 4)
     - Max characters per line (20-60, default: 42)
     - Max pause gap between words (0.1-2.0s, default: 0.5s)
   - Click "Generate SRT File"
   - Download your subtitle file automatically

**That's it!** Your `.srt` subtitle file is ready to use with any video player or video editor.

---

### **First-Time Setup Requirements**

The launcher will handle most setup automatically, but you need:

1. **Python 3.10 or newer** - [Download here](https://www.python.org/downloads/)
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation

2. **Internet connection** - For downloading dependencies (first run only)

3. **FFmpeg** - The launcher will try to install it automatically
   - If automatic install fails, see [FFmpeg Installation](#ffmpeg-installation) below

---

### **Troubleshooting**

#### **"Python not found"**
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. Restart the launcher

#### **"FFmpeg not found"**
The launcher tries to install FFmpeg automatically. If it fails:

- **Windows:** `winget install ffmpeg`
- **Mac:** `brew install ffmpeg` (requires [Homebrew](https://brew.sh))
- **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian)
- **Manual:** Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)

#### **"Port 5000 is in use"**
Close other apps using port 5000, or manually run:
```bash
python web_server.py --port 5001
```
Then open: http://localhost:5001

#### **"Dependencies installation failed"**
- Check your internet connection
- Try manually: `pip install -r requirements.txt`

#### **Server won't start**
1. Make sure Python is installed and in PATH
2. Check that port 5000 is available
3. Look for error messages in the launcher window

#### **"CUDA/GPU errors"**
The app automatically falls back to CPU (slower but works fine). No action needed.

---

### **Manual Start (Alternative Method)**

If the launcher doesn't work, you can start manually:

1. **Install Python 3.10+** from [python.org](https://www.python.org/downloads/)
2. **Install FFmpeg:**
   - Windows: `winget install ffmpeg`
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the server:**
   ```bash
   python web_server.py
   ```
5. **Open your browser to:** http://localhost:5000

---

## **About**

Whisper-Hindi2Hinglish is a variant of OpenAI's Whisper, designed for precise, speech recognition of audios with Indian accents and heavy background noise in Hinglish (Hindi written in Latin scripture) language. It is trained on Hindi and Hinglish data and is optimized for use cases where accuracy is paramount and background noise is abundant (such as those found in typical Indian background sounds). To improve transcription on Hindi language, we finetuned **Whisper-Hindi2Hinglish** using a custom-built proprietary dataset.

## **Problem Statement**:

- Existing ASR systems demonstrate significant limitations in accurately transcribing Indian speech, particularly Hindi and Hinglish conversations, leading to poor performance in real-world applications
    - Models perform inadequately with natural Indian accents and conversational patterns
    - Current systems struggle with background noise common in real-world Indian audio recordings
    - Available Hindi datasets are primarily recorded in controlled environments with scripted speech, making them unsuitable for practical applications

- Traditional Hindi transcription systems generating Devanagari scripture face critical challenges:
    - Minor transcription errors can result in completely different meanings of words and sentences
    - Integration with modern LLMs becomes complicated due to script incompatibility
    - Misalignment with user preferences, as most Indian internet users communicate in Hinglish rather than pure Hindi


- There is a significant gap in the Speech market for an ASR system that can:
    - Process and accurately transcribe Indian accents and natural conversational patterns
    - Maintain consistent performance even with substantial background noise
    - Output transcriptions in Hinglish to align with real-world usage patterns
    - Integrate smoothly with existing NLP pipelines and LLMs
    - Minimize hallucinations and false transcriptions in noisy environments


- The lack of such a system creates substantial barriers in:
    - Developing effective voice-based applications for the Indian market
    - Building reliable voice-based interfaces for various applications

## **Motivation**:

- Current state-of-the-art ASR (Automatic Speech Recognition) models exhibit a significant bias towards Western languages due to the abundant availability of high-quality training data for these languages.
- While Hindi language data exists, it suffers from several quality issues:
    - Most recordings are made in controlled environments with minimal background noise
    - Data is primarily non-conversational
    - Recordings typically feature speakers talking directly into microphones, and verbatim reading a script making the nature of the audio unnatural
    - These limitations make it difficult to train models that can handle real-world Indian accents with abundant background noise
- The crowdsourced nature of available Hindi datasets results in lower accuracy than English.
- There is a strong case for developing models that can transcribe audio into Hinglish (Hindi written in Latin script) because:
    - It reduces the likelihood of grammatical errors in transcriptions. As in the case of Hindi, even a small mistake can lead to a completely different sentence meaning. Example: बाल (baal) - "hair" vs बल (bal) - "strength", दिन (din) - "day" vs दीन (deen) - "poor/humble" etc.
    - It enables better comprehension by Large Language Models (LLMs)
    - It aligns with actual usage patterns, as most Indian internet users communicate in Hinglish rather than Hindi in Devanagari script

The above reasons were some of the main motivations behind training the Whisper-Hindi2Hinglish model.

## Key Features:
1. Hinglish as a language: Added ability to transcribe audio into spoken Hinglish language reducing chances of grammatical errors
2. Whisper Architecture: Based on the whisper architecture making it easy to use with the transformers package
3. Better Noise handling: The model is resistant to noise and thus does not return transcriptions for audio with just noise
4. Hallucination Mitigation: Minimizes transcription hallucinations to enhance accuracy.

## Relased Models:

We have open sourced three models under the `Whisper-Hindi2Hinglish` family:

- **[Oriserve/Whisper-Hindi2Hinglish-Apex](https://huggingface.co/Oriserve/Whisper-Hindi2Hinglish-Apex)** ⭐ (Default)
    - Ultimate accuracy for Hindi-English transcription
    - Best-in-class performance for Hinglish content
    - Recommended for production use
    
- **[Oriserve/Whisper-Hindi2Hinglish-Prime](https://huggingface.co/Oriserve/Whisper-Hindi2Hinglish-Prime)** 🏆
    - Superior noise resistance for cleaner transcriptions
    - Advanced hallucination mitigation
    - Enhanced accuracy across benchmark datasets
    - Lightning fast inference time and low latency streaming
    
- **[Oriserve/Whisper-Hindi2Hinglish-Swift](https://huggingface.co/Oriserve/Whisper-Hindi2Hinglish-Swift)** ⚡
    - Optimised for faster processing
    - Robust hallucination prevention
    - Exceptional performance metrics
    - Good balance of speed and quality

## Performance Overview
#### Qualitative Performance Overview
| Audio | Whisper Large V3 | Whisper-Hindi2Hinglish-Prime |
|-------|------------------|------------------------------|
| [demo1](https://github.com/user-attachments/assets/367d0992-e5c0-4fe6-ae4d-cbfa3b628676)| maynata pura, canta maynata | Mehnat to poora karte hain. |
| [demo2](https://github.com/user-attachments/assets/73839c47-40d6-432f-a89c-c1cb686abcbe) | Where did they come from? | Haan vahi ek aapko bataaya na. |
| [demo3](https://github.com/user-attachments/assets/828349b8-5712-4e17-abc4-029ce26cc695) | A Pantral Logan. | Aap pandrah log hain. |
| [demo4](https://github.com/user-attachments/assets/eb6b94bd-7845-4144-9c79-281804285afb) | Thank you, Sanchez. | Kitne saal ki? |
| [demo5](https://github.com/user-attachments/assets/343d7da1-62fc-4b7a-8fb7-c5365926d975)| Rangers, I can tell you. | Lander cycle chaahie. |
| [demo6](https://github.com/user-attachments/assets/0897acec-69ba-47ba-b5ba-d516860cd559) | Uh-huh. They can't. | Haan haan, dekhe hain. |

#### Quantitative Performance Overview

***Note***:
- *The below WER scores are for Hinglish text generated by our model and the original whisper model*
- *To check our model's real-world performance against other SOTA models please head to our [Speech-To-Text Arena](https://huggingface.co/spaces/Oriserve/ASR_arena) space.*

| Dataset | Whisper Large V3 | Whisper-Hindi2Hinglish-Prime | Whisper-Hindi2Hinglish-Swift |
|-------|------------------------|-------------------------|-------------------------|
| [Common-Voice](https://commonvoice.mozilla.org/en) | 61.9432| 32.4314 | 38.6549 |
| [FLEURS](https://huggingface.co/datasets/google/fleurs) | 50.8425 | 28.6806 | 35.0888 |
| [Indic-Voices](https://ai4bharat.iitm.ac.in/datasets/indicvoices)| 82.5621 | 60.8224 | 65.2147 |

## Setup

### Environment Setup

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/OriserveAI/Whisper-Hindi2Hinglish.git
    cd Whisper-Hindi2Hinglish
    ```

2. **Create Python Environment**:
    ```bash
    conda create --name whisperHindi2Hinglish python=3.10
    conda activate whisperHindi2Hinglish
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Additional Installations**:
    - Follow OpenAI's instructions to install additional dependencies like `ffmpeg` and `rust`: [Whisper Setup](https://github.com/openai/whisper#setup).
    - To use the `client_mic.py` to stream audio from your microphone, you will need to install `pyaudio` you can follow the instructions [Pyaudio Setup](https://people.csail.mit.edu/hubert/pyaudio/).

## Features of the App

The server and client are designed to be used in a streaming manner. The client can stream audio from a file or from your microphone. The server will process the audio and send the transcription to the client.

**Default Model**: The system now uses `Oriserve/Whisper-Hindi2Hinglish-Apex` by default for the highest accuracy. You can also choose:
- `Oriserve/Whisper-Hindi2Hinglish-Prime` for excellent quality with superior noise handling
- `Oriserve/Whisper-Hindi2Hinglish-Swift` for faster processing

**New Subtitle Customization**: You can now control:
- Maximum words per subtitle (default: 4)
- Maximum characters per line (default: 42 - Netflix standard)
- Maximum pause gap for subtitle breaks (default: 0.5 seconds)

The server and client use websockets to communicate with each other.

## 🎬 Video to SRT Converter

Convert Hindi-English mixed videos to Roman English SRT subtitle files with customizable formatting!

### Quick Start
```bash
# Web Interface (easiest) - with customization options
python web_server.py
# Then open: http://localhost:5000

# Command Line - basic usage
python video_to_srt.py your_video.mp4

# Command Line - with custom subtitle formatting
python video_to_srt.py your_video.mp4 \
  --max-words 5 \
  --max-chars 45 \
  --max-pause 0.6
```

**See [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) for detailed customization options**

**See [docs/QUICK_START.md](docs/QUICK_START.md) for complete setup guide**

### Features:
- 🎥 Upload video, get SRT file
- 🌐 Beautiful web interface with real-time status
- 🤖 Three AI models to choose from (Apex, Prime, Swift)
- ⚙️ Customizable subtitle formatting:
  - Control words per subtitle
  - Set character limits per line
  - Adjust pause gap detection
- ⚡ Fast processing with GPU (automatic CPU fallback)
- 🎯 Accurate Hindi-English transcription
- 📝 Properly timed subtitles with word-level timestamps
- 📊 See which model is currently loaded

---

## Usage

### Web Server (Recommended)
Start the web server with the Apex model (default):
```bash
python web_server.py
```
Then open http://localhost:5000 in your browser.

**Features:**
- Drag and drop video upload
- Choose between Apex, Prime, or Swift models
- Customize subtitle formatting in real-time
- See which model is currently loaded
- Automatic download of generated SRT files

### WebSocket Server (For Streaming)
To start the streaming server, run:
```bash
python websocket_server.py
```
- The server will start listening on port 8000 by default. You can change the port by passing the `--port` argument.
- The default model is now `Oriserve/Whisper-Hindi2Hinglish-Apex`. You can change it with `--model-id`:
  ```bash
  # Use Apex (default - best quality)
  python websocket_server.py --model-id Oriserve/Whisper-Hindi2Hinglish-Apex
  
  # Use Prime (excellent quality)
  python websocket_server.py --model-id Oriserve/Whisper-Hindi2Hinglish-Prime
  
  # Use Swift (faster)
  python websocket_server.py --model-id Oriserve/Whisper-Hindi2Hinglish-Swift
  ```
- To change the device: `--device cuda` or `--device cpu` (default: cuda with automatic CPU fallback)
- To change the data type: `--dtype float16` or `--dtype float32` (default: float16)

### Client

#### File Streaming
To stream audio from a file, run the following command:
```bash
python client_file.py --uri <uri> --wav-path <wav-path> --chunk-duration <chunk-duration>
```

#### Microphone Streaming
To stream audio from your microphone, run the following command:
```bash
python client_mic.py --uri <uri> --device-index <device-index> --chunk-duration <chunk-duration>
```

**Parameters:**
- `uri`: The URI at which the server is running (e.g., ws://localhost:8000)
- `device-index`: The index of the microphone device to use (default: 0)
- `wav-path`: The path to the audio file
- `chunk-duration`: The duration of each chunk in milliseconds (default: 10)

### Command Line Video to SRT

Convert videos to SRT files directly from command line:

```bash
# Basic usage (uses Apex model by default)
python video_to_srt.py your_video.mp4

# Specify output file
python video_to_srt.py your_video.mp4 --output custom_name.srt

# Choose different model
python video_to_srt.py your_video.mp4 --model-id Oriserve/Whisper-Hindi2Hinglish-Prime

# Customize subtitle formatting
python video_to_srt.py your_video.mp4 \
  --max-words 6 \
  --max-chars 50 \
  --max-pause 0.8

# All options combined
python video_to_srt.py your_video.mp4 \
  --output subtitles.srt \
  --model-id Oriserve/Whisper-Hindi2Hinglish-Apex \
  --max-words 5 \
  --max-chars 45 \
  --max-pause 0.6 \
  --device cuda
```

**Subtitle Formatting Options:**
- `--max-words`: Maximum words per subtitle (2-10, default: 4)
- `--max-chars`: Maximum characters per line (20-60, default: 42)
- `--max-pause`: Maximum pause gap in seconds (0.1-2.0, default: 0.5)

See [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) for more examples and tips.

***Note***:
- As WebRTC VAD is used for speech detection, the chunk-duration should be either 10, 20, or 30 milliseconds.
- WebRTC VAD also only accepts 16-bit mono PCM audio, sampled at 8000, 16000, 32000 or 48000 Hz, so to enable VAD ensure that the audio file is in correct format.
- Currently, the server only supports linear16 encoding, mono audios.
- To choose the correct device-index when using the client_mic.py script, you can run the following code to check for different recording devices on your system:
    ```python
    import pyaudio

    p = pyaudio.PyAudio()

    device_count = p.get_device_count()

    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        print(f"Device {i}: {device_info['name']}")
        print(f"  - Index: {device_info['index']}")
        print(f"  - Channels: {device_info['maxInputChannels']}")
        print(f"  - Default Sample Rate: {device_info['defaultSampleRate']}")
        print(f"  - Input Supported: {'Yes' if device_info['maxInputChannels'] > 0 else 'No'}")
        print(f"  - Output Supported: {'Yes' if device_info['maxOutputChannels'] > 0 else 'No'}")
        print("-" * 40)

    p.terminate()
    ```
    From the output you need to choose the device-index that supports input and has channels >= 1.

## Training:

### Data:

- **Duration**: A total of ~550 Hrs of noisy Indian-accented Hindi data was used to finetune the model.
- **Collection**: Due to a lack of ASR-ready hinglish datasets available, a specially curated proprietary dataset was used.
- **Labelling**: This data was then labeled using a SOTA model and the transcriptions were improved by human intervention.
- **Quality**: Emphasis was placed on collecting noisy data for the task as the intended use case of the model is in Indian environments where background noise is abundant.
- **Processing**: It was ensured that the audios are all chunked into chunks of length <30s, and there are at max 2 speakers in a clip. No further processing steps were done to not change the quality of the source data. As the audios in the proprietary dataset were manually collected, the quality of the data was not a concern.

### Finetuning:
- **Custom Dynamic Layer Freezing**:
    - Using `pytorch` hooks, we ran inference on a subset of the training data to collect data about layer activations.
    - We then analyzed the layer activation data and identified a subset of layers that were most active during inference, as the ones being most responsible for generating the transcriptions.
    - These layers were then kept unfrozen during the training process while all the other layers were kept frozen.
    - This enabled faster convergence and efficient finetuning.
- **Deepspeed Integration**: Deepspeed was also utilized to speed up, and optimize the training process.
- **Novel Trainer Architecture**:
    - To finetune the model we developed a custom trainer that was specifically designed to train the model.
    - The trainer was designed to be modular and extensible, allowing for easy addition of new functionalities, such as custom callbacks, custom optimizers, and custom dataloaders.
    - There were several custom callbacks that were added to the trainer to enable higher observability during the training process.
    - At every validation epoch, the model was evaluated on unseen data, that was not used during training. This allowed us to monitor the model's performance on unseen data as most of the time the model would have to perform on unseen data.

## Miscellaneous
This model is from a family of transformers-based ASR models trained by Oriserve. To compare this model against other models from the same family or other SOTA models please head to our [Speech-To-Text Arena](https://huggingface.co/spaces/Oriserve/ASR_arena). To learn more about our other models, and other queries regarding AI voice agents you can reach out to us at our email [ai-team@oriserve.com](ai-team@oriserve.com)
