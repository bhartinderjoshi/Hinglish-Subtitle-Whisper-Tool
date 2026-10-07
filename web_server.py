"""
Flask API Server for Video to SRT Conversion
Upload video and get SRT file back
"""
import argparse
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import torch
from flask import Flask, request, send_file, jsonify, render_template
from werkzeug.utils import secure_filename

from logger import logger
from utils import torch_dtype_from_str, get_device
from video_to_srt import video_to_srt

# Ensure ffmpeg in PATH
for extra_path in [os.path.expanduser('~/bin'), '/opt/homebrew/bin', '/usr/local/bin']:
    if os.path.exists(extra_path) and extra_path not in os.environ.get('PATH', ''):
        os.environ['PATH'] = f"{extra_path}:{os.environ.get('PATH', '')}"

import shutil
import json
import re

app = Flask(__name__, template_folder='templates')

# Reduce logging verbosity for end users - only show important messages
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Configuration - Use isolated temporary directory so local user files are NEVER deleted or overwritten
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "hinglish_whisper_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    # Video formats
    'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'm4v',
    # Audio formats
    'wav', 'mp3', 'ogg', 'flac', 'm4a', 'aac', 'wv', 'wma', 'opus'
}
MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1000MB (1GB)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Global model config
MODEL_CONFIG = {
    'model_id': 'Oriserve/Whisper-Hindi2Hinglish-Apex',
    'device': 'cuda',
    'dtype': torch.float16
}


def get_ffmpeg_binary():
    """Find the path to ffmpeg binary"""
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    for p in [os.path.expanduser('~/bin/ffmpeg'), '/usr/local/bin/ffmpeg', '/opt/homebrew/bin/ffmpeg']:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return 'ffmpeg'


def hex_to_ass_color(hex_color, alpha=1.0):
    """
    Convert CSS hex color (#RRGGBB) to ASS color format (&HAABBGGRR).
    In ASS: AA is alpha (00=opaque, FF=transparent), then BB, GG, RR.
    """
    if not hex_color:
        return "&H00FFFFFF"
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])
    if len(hex_color) != 6:
        return "&H00FFFFFF"
    r = hex_color[0:2]
    g = hex_color[2:4]
    b = hex_color[4:6]
    
    # ASS alpha: 0 = fully opaque (00), 255 = fully transparent (FF)
    try:
        alpha_val = float(alpha)
    except (ValueError, TypeError):
        alpha_val = 1.0
    alpha_val = max(0.0, min(1.0, alpha_val))
    ass_alpha = int(round((1.0 - alpha_val) * 255))
    
    return f"&H{ass_alpha:02X}{b.upper()}{g.upper()}{r.upper()}"


def srt_time_to_ass_time(time_str):
    """Convert SRT time (HH:MM:SS,mmm) to ASS time (H:MM:SS.cs)"""
    if not time_str:
        return "0:00:00.00"
    time_str = time_str.strip().replace(',', '.')
    parts = time_str.split(':')
    if len(parts) == 3:
        try:
            h = int(parts[0])
            m = int(parts[1])
            s = float(parts[2])
            return f"{h}:{m:02d}:{s:05.2f}"
        except ValueError:
            return "0:00:00.00"
    return "0:00:00.00"


def generate_ass_script(subtitles, styles, play_res_x=1920, play_res_y=1080):
    """
    Generate Advanced SubStation Alpha (.ass) subtitle file content from subtitles and style dict.
    """
    font_name = styles.get('fontName', 'Montserrat')
    font_size = int(styles.get('fontSize', 36))
    primary_color = hex_to_ass_color(styles.get('primaryColor', '#FFFFFF'), styles.get('primaryAlpha', 1.0))
    secondary_color = "&H000000FF"
    outline_color = hex_to_ass_color(styles.get('outlineColor', '#000000'), 1.0)
    back_color = hex_to_ass_color(styles.get('backColor', '#000000'), styles.get('backAlpha', 0.8))
    
    bold = -1 if styles.get('bold', True) else 0
    italic = -1 if styles.get('italic', False) else 0
    border_style = int(styles.get('borderStyle', 1))  # 1 = outline+shadow, 3 = background box
    outline = float(styles.get('outlineWidth', 2.5))
    shadow = float(styles.get('shadow', 1.5))
    alignment = int(styles.get('alignment', 2))  # 2 = bottom center, 8 = top center, 5 = middle center
    margin_l = int(styles.get('marginL', 30))
    margin_r = int(styles.get('marginR', 30))
    margin_v = int(styles.get('marginV', 40))
    is_uppercase = bool(styles.get('uppercase', False))
    
    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {play_res_x}",
        f"PlayResY: {play_res_y}",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{font_name},{font_size},{primary_color},{secondary_color},{outline_color},{back_color},{bold},{italic},0,0,100,100,0,0,{border_style},{outline},{shadow},{alignment},{margin_l},{margin_r},{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    
    for sub in subtitles:
        start_ass = srt_time_to_ass_time(sub.get('startTime', '00:00:00,000'))
        end_ass = srt_time_to_ass_time(sub.get('endTime', '00:00:00,000'))
        text = sub.get('text', '').strip()
        if is_uppercase:
            text = text.upper()
        # Escape newlines for ASS
        text = text.replace('\r\n', '\\N').replace('\n', '\\N')
        ass_lines.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{text}")
        
    return "\n".join(ass_lines)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page - redirect to editor"""
    return render_template('editor.html')


@app.route('/favicon.ico')
def favicon():
    """Favicon endpoint to prevent 404 in browser console"""
    return ('', 204)


@app.route('/launcher')
def launcher():
    """Landing page with system status"""
    return render_template('launcher.html')


@app.route('/editor')
def editor():
    """Advanced subtitle editor page"""
    return render_template('editor.html')


@app.route('/upload-page')
def upload_page():
    """Original upload interface (for backwards compatibility)"""
    return render_template('upload.html')


@app.route('/api')
def api_info():
    """API documentation"""
    return jsonify({
        'service': 'Video to SRT Converter',
        'description': 'Upload Hindi-English mixed video and get Roman English SRT subtitles',
        'endpoints': {
            '/upload': {
                'method': 'POST',
                'description': 'Upload video file',
                'parameters': {
                    'video': 'Video file (mp4, avi, mov, mkv, webm, flv, wmv, m4v)',
                    'model': 'Optional: swift (default) or prime'
                },
                'returns': 'SRT file download'
            },
            '/health': {
                'method': 'GET',
                'description': 'Check server health'
            }
        },
        'max_file_size': '500MB',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model': MODEL_CONFIG['model_id']})


@app.route('/api/status')
def system_status():
    """Check system requirements status"""
    import subprocess
    import sys

    status = {
        'python': True,  # If we're running, Python is installed
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'ffmpeg': check_ffmpeg_installed(),
        'dependencies': check_dependencies(),
        'device': get_device_info(),
        'model': MODEL_CONFIG['model_id'],  # Add current model
        'server': True
    }
    return jsonify(status)


def check_ffmpeg_installed():
    """Check if FFmpeg is installed"""
    ffmpeg_bin = get_ffmpeg_binary()
    try:
        result = subprocess.run(
            [ffmpeg_bin, '-version'],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    required = ['flask', 'torch', 'transformers', 'whisper_timestamped']
    try:
        for module in required:
            __import__(module)
        return True
    except ImportError:
        return False


def get_device_info():
    """Get device information for processing"""
    device = MODEL_CONFIG.get('device', 'cpu')

    if device == 'cuda':
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            return f"CUDA GPU ({gpu_name})"
        else:
            return "CPU (CUDA not available)"
    elif device == 'mps':
        return "Apple Silicon (MPS)"
    else:
        return "CPU"


@app.route('/upload', methods=['POST'])
def upload_video():
    """
    Upload video and get SRT file
    """
    # Check if file is present
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    # Get model preference
    model_choice = request.form.get('model', 'apex').lower()
    if model_choice == 'prime':
        model_id = 'Oriserve/Whisper-Hindi2Hinglish-Prime'
    elif model_choice == 'swift':
        model_id = 'Oriserve/Whisper-Hindi2Hinglish-Swift'
    else:
        model_id = 'Oriserve/Whisper-Hindi2Hinglish-Apex'
    
    # Get subtitle formatting options
    try:
        max_words = int(request.form.get('maxWords', 4))
        max_chars = int(request.form.get('maxChars', 42))
        max_pause = float(request.form.get('maxPause', 0.5))
        vad_threshold = float(request.form.get('vadThreshold', 0.5))
        
        # Validate ranges
        max_words = max(1, min(10, max_words))
        max_chars = max(20, min(60, max_chars))
        max_pause = max(0.1, min(2.0, max_pause))
        vad_threshold = max(0.1, min(0.9, vad_threshold))
    except (ValueError, TypeError):
        max_words = 4
        max_chars = 42
        max_pause = 0.5
        vad_threshold = 0.6
    
    import time
    # Save uploaded file to isolated temporary path
    safe_name = secure_filename(file.filename) or "video.mp4"
    unique_prefix = f"upload_{os.getpid()}_{int(time.time()*1000)}_"
    temp_video_filename = unique_prefix + safe_name
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_video_filename)
    file.save(video_path)

    try:
        # Generate SRT file
        logger.info(f"Original filename: {file.filename}")
        logger.info(f"Temp upload path: {video_path}")
        logger.info(f"Processing video: {safe_name}")
        logger.info(f"Model: {model_id}")
        logger.info(f"Subtitle settings: max_words={max_words}, max_chars={max_chars}, max_pause={max_pause}")
        logger.info(f"VAD settings: threshold={vad_threshold} (silence filtering)")
        srt_filename = Path(safe_name).stem + '.srt'
        srt_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_prefix + srt_filename)
        logger.info(f"SRT filename: {srt_filename}")
        logger.info(f"SRT path: {srt_path}")
        
        video_to_srt(
            video_path,
            srt_path,
            model_id,
            MODEL_CONFIG['device'],
            MODEL_CONFIG['dtype'],
            max_words=max_words,
            max_chars=max_chars,
            max_pause=max_pause,
            vad_threshold=vad_threshold
        )
        
        # Check if request wants text response (for editor) or file download
        return_type = request.form.get('returnType', 'file')
        
        if return_type == 'text':
            # Return SRT content as text for editor
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            return srt_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            # Send SRT file for download
            return send_file(
                srt_path,
                as_attachment=True,
                download_name=srt_filename,
                mimetype='text/plain'
            )
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(srt_path):
            pass


@app.route('/export-ass', methods=['POST'])
def export_ass():
    """
    Generate and download styled .ass subtitle file
    """
    try:
        data = request.get_json(silent=True) or {}
        subtitles = data.get('subtitles', [])
        styles = data.get('styles', {})
        filename = data.get('filename', 'subtitles.ass')
        
        if not filename.endswith('.ass'):
            filename = Path(filename).stem + '.ass'
            
        ass_content = generate_ass_script(subtitles, styles)
        
        temp_dir = tempfile.mkdtemp()
        ass_path = os.path.join(temp_dir, filename)
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
            
        return send_file(
            ass_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Error generating ASS subtitle: {e}")
        return jsonify({'error': str(e)}), 500


EXPORT_JOBS = {}


def get_media_duration(file_path):
    """Get duration of video or audio file in seconds using FFmpeg stderr output"""
    ffmpeg_bin = get_ffmpeg_binary()
    try:
        res = subprocess.run([ffmpeg_bin, '-i', file_path], capture_output=True, text=True, timeout=5)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", res.stderr)
        if match:
            h, m, s = match.groups()
            return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception as e:
        logger.warning(f"Could not parse media duration: {e}")
    return 0.0


def run_export_burning_job(job_id, input_video_path, ass_path, out_video_path, out_video_name, total_duration):
    """Background worker that burns subtitles with FFmpeg and tracks real-time progress"""
    try:
        ffmpeg_bin = get_ffmpeg_binary()
        escaped_ass_path = ass_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
        
        EXPORT_JOBS[job_id] = {
            'status': 'rendering',
            'progress': 2.0,
            'speed': '1.0x',
            'out_time': '00:00:00',
            'total_duration': total_duration
        }
        
        cmd = [
            ffmpeg_bin,
            '-y',
            '-i', input_video_path,
            '-vf', f"ass='{escaped_ass_path}'",
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '20',
            '-c:a', 'copy',
            '-progress', 'pipe:1',
            out_video_path
        ]
        
        logger.info(f"Starting video burn job {job_id}: {cmd}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
        # Read progress lines
        for line in process.stdout:
            line = line.strip()
            if line.startswith('out_time_us='):
                try:
                    val = float(line.split('=')[1])
                    curr_sec = val / 1000000.0
                    if total_duration > 0:
                        pct = min(99.0, max(2.0, round((curr_sec / total_duration) * 100.0, 1)))
                        EXPORT_JOBS[job_id]['progress'] = pct
                except Exception:
                    pass
            elif line.startswith('out_time_ms='):
                try:
                    val = float(line.split('=')[1])
                    curr_sec = val / 1000.0 if val < 100000000 else val / 1000000.0
                    if total_duration > 0:
                        pct = min(99.0, max(2.0, round((curr_sec / total_duration) * 100.0, 1)))
                        EXPORT_JOBS[job_id]['progress'] = pct
                except Exception:
                    pass
            elif line.startswith('out_time='):
                out_time_val = line.split('=', 1)[1]
                EXPORT_JOBS[job_id]['out_time'] = out_time_val
                # Fallback calculation from out_time HH:MM:SS if out_time_us was not received
                if EXPORT_JOBS[job_id].get('progress', 0) <= 2.0 and total_duration > 0:
                    try:
                        pts = out_time_val.replace(',', '.').split(':')
                        if len(pts) == 3:
                            curr_sec = int(pts[0]) * 3600 + int(pts[1]) * 60 + float(pts[2])
                            pct = min(99.0, max(2.0, round((curr_sec / total_duration) * 100.0, 1)))
                            EXPORT_JOBS[job_id]['progress'] = pct
                    except Exception:
                        pass
            elif line.startswith('speed='):
                speed_val = line.split('=', 1)[1].strip()
                EXPORT_JOBS[job_id]['speed'] = speed_val
            elif line.startswith('progress=end'):
                EXPORT_JOBS[job_id]['progress'] = 100.0
                
        stderr_output = process.stderr.read()
        process.wait()
        
        # Audio fallback if copy failed
        if process.returncode != 0 and ('could not find tag for codec' in stderr_output.lower() or 'pcm' in stderr_output.lower() or 'flac' in stderr_output.lower()):
            logger.warning("Audio copy failed during progress burn, retrying with AAC...")
            cmd_fallback = [
                ffmpeg_bin,
                '-y',
                '-i', input_video_path,
                '-vf', f"ass='{escaped_ass_path}'",
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '20',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-progress', 'pipe:1',
                out_video_path
            ]
            process_fb = subprocess.Popen(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            for line in process_fb.stdout:
                line = line.strip()
                if line.startswith('out_time_us='):
                    try:
                        val = float(line.split('=')[1])
                        curr_sec = val / 1000000.0
                        if total_duration > 0:
                            pct = min(99.0, max(2.0, round((curr_sec / total_duration) * 100.0, 1)))
                            EXPORT_JOBS[job_id]['progress'] = pct
                    except Exception:
                        pass
                elif line.startswith('out_time_ms='):
                    try:
                        val = float(line.split('=')[1])
                        curr_sec = val / 1000.0 if val < 100000000 else val / 1000000.0
                        if total_duration > 0:
                            pct = min(99.0, max(2.0, round((curr_sec / total_duration) * 100.0, 1)))
                            EXPORT_JOBS[job_id]['progress'] = pct
                    except Exception:
                        pass
                elif line.startswith('out_time='):
                    EXPORT_JOBS[job_id]['out_time'] = line.split('=', 1)[1]
                elif line.startswith('speed='):
                    EXPORT_JOBS[job_id]['speed'] = line.split('=', 1)[1].strip()
            process_fb.wait()
            if process_fb.returncode != 0:
                raise RuntimeError(f"FFmpeg render failed: {process_fb.stderr.read()[-300:]}")
        elif process.returncode != 0:
            raise RuntimeError(f"FFmpeg render failed: {stderr_output[-300:]}")
            
        if not os.path.exists(out_video_path) or os.path.getsize(out_video_path) == 0:
            raise RuntimeError("Rendered video file is empty or missing")
            
        EXPORT_JOBS[job_id] = {
            'status': 'complete',
            'progress': 100.0,
            'out_video_path': out_video_path,
            'out_video_name': out_video_name
        }
        logger.info(f"✓ Video export job {job_id} complete! Output: {out_video_name}")
        
    except Exception as e:
        logger.error(f"Error in export job {job_id}: {e}")
        EXPORT_JOBS[job_id] = {
            'status': 'error',
            'progress': 0,
            'error': str(e)
        }


@app.route('/start-export-video', methods=['POST'])
def start_export_video():
    """Start asynchronous video burning export job and return job_id for progress tracking"""
    import threading
    import uuid
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
        
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'Empty video file'}), 400
        
    subtitles_raw = request.form.get('subtitles', '[]')
    styles_raw = request.form.get('styles', '{}')
    
    try:
        subtitles = json.loads(subtitles_raw)
    except Exception:
        subtitles = []
        
    try:
        styles = json.loads(styles_raw)
    except Exception:
        styles = {}
        
    if not subtitles:
        return jsonify({'error': 'No subtitles provided for burning'}), 400
        
    job_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp()
    input_video_filename = secure_filename(video_file.filename) or 'input.mp4'
    input_video_path = os.path.join(temp_dir, input_video_filename)
    video_file.save(input_video_path)
    
    ass_path = os.path.join(temp_dir, 'subtitles.ass')
    out_video_name = Path(input_video_filename).stem + '_subtitled.mp4'
    out_video_path = os.path.join(temp_dir, out_video_name)
    
    # 1. Generate ASS content with styles
    ass_content = generate_ass_script(subtitles, styles)
    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)
        
    total_duration = get_media_duration(input_video_path)
    # If duration could not be determined, estimate from last subtitle end time
    if total_duration <= 0 and subtitles:
        try:
            last_end = subtitles[-1].get('endTime', '00:00:10,000')
            parts = last_end.replace(',', '.').split(':')
            total_duration = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        except Exception:
            total_duration = 30.0
            
    EXPORT_JOBS[job_id] = {
        'status': 'starting',
        'progress': 1.0,
        'total_duration': total_duration
    }
    
    worker = threading.Thread(
        target=run_export_burning_job,
        args=(job_id, input_video_path, ass_path, out_video_path, out_video_name, total_duration),
        daemon=True
    )
    worker.start()
    
    return jsonify({
        'status': 'started',
        'job_id': job_id,
        'duration': total_duration
    })


@app.route('/export-progress/<job_id>', methods=['GET'])
def get_export_progress(job_id):
    """Check rendering progress percentage and speed of an export job"""
    job = EXPORT_JOBS.get(job_id)
    if not job:
        return jsonify({'status': 'not_found', 'progress': 0}), 404
    return jsonify(job)


@app.route('/download-exported-video/<job_id>', methods=['GET'])
def download_exported_video(job_id):
    """Download the completed burned MP4 video for a finished export job"""
    job = EXPORT_JOBS.get(job_id)
    if not job or job.get('status') != 'complete':
        return jsonify({'error': 'Export job is not complete or not found'}), 404
        
    out_video_path = job.get('out_video_path')
    out_video_name = job.get('out_video_name', 'subtitled_video.mp4')
    
    if not out_video_path or not os.path.exists(out_video_path):
        return jsonify({'error': 'Exported file not found on disk'}), 404
        
    return send_file(
        out_video_path,
        as_attachment=True,
        download_name=out_video_name,
        mimetype='video/mp4'
    )


@app.route('/export-video', methods=['POST'])
def export_burned_video():
    """Synchronous fallback endpoint for video burning"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
        
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'Empty video file'}), 400
        
    subtitles_raw = request.form.get('subtitles', '[]')
    styles_raw = request.form.get('styles', '{}')
    
    try:
        subtitles = json.loads(subtitles_raw)
    except Exception:
        subtitles = []
        
    try:
        styles = json.loads(styles_raw)
    except Exception:
        styles = {}
        
    if not subtitles:
        return jsonify({'error': 'No subtitles provided for burning'}), 400
        
    temp_dir = tempfile.mkdtemp()
    input_video_filename = secure_filename(video_file.filename) or 'input.mp4'
    input_video_path = os.path.join(temp_dir, input_video_filename)
    video_file.save(input_video_path)
    
    ass_path = os.path.join(temp_dir, 'subtitles.ass')
    out_video_name = Path(input_video_filename).stem + '_subtitled.mp4'
    out_video_path = os.path.join(temp_dir, out_video_name)
    
    try:
        ass_content = generate_ass_script(subtitles, styles)
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
            
        ffmpeg_bin = get_ffmpeg_binary()
        escaped_ass_path = ass_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
        
        cmd = [
            ffmpeg_bin,
            '-y',
            '-i', input_video_path,
            '-vf', f"ass='{escaped_ass_path}'",
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '20',
            '-c:a', 'copy',
            out_video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            cmd_fallback = [
                ffmpeg_bin,
                '-y',
                '-i', input_video_path,
                '-vf', f"ass='{escaped_ass_path}'",
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '20',
                '-c:a', 'aac',
                '-b:a', '192k',
                out_video_path
            ]
            subprocess.run(cmd_fallback, capture_output=True, text=True)
            
        return send_file(
            out_video_path,
            as_attachment=True,
            download_name=out_video_name,
            mimetype='video/mp4'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/trim-media', methods=['POST'])
def trim_media():
    """
    Trim / cut uploaded audio or video between start_time and end_time (in seconds)
    """
    if 'media' not in request.files:
        return jsonify({'error': 'No media file provided'}), 400
        
    media_file = request.files['media']
    if media_file.filename == '':
        return jsonify({'error': 'Empty media file'}), 400
        
    try:
        start_time = float(request.form.get('startTime', 0))
        end_time = float(request.form.get('endTime', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid start or end time specified'}), 400
        
    if end_time <= start_time:
        return jsonify({'error': 'End time must be greater than start time'}), 400
        
    temp_dir = tempfile.mkdtemp()
    input_filename = secure_filename(media_file.filename) or 'input.mp4'
    input_path = os.path.join(temp_dir, input_filename)
    media_file.save(input_path)
    
    out_filename = Path(input_filename).stem + f"_trimmed_{int(start_time)}s_to_{int(end_time)}s.mp4"
    out_path = os.path.join(temp_dir, out_filename)
    
    ffmpeg_bin = get_ffmpeg_binary()
    
    try:
        # Re-encode cleanly to ensure exact frame precision on cut boundaries
        cmd = [
            ffmpeg_bin,
            '-y',
            '-ss', str(start_time),
            '-to', str(end_time),
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '19',
            '-c:a', 'aac',
            '-b:a', '192k',
            out_path
        ]
        
        logger.info(f"Trimming media: {cmd}")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # If input was audio-only without video track, fallback to pure audio container
        if res.returncode != 0:
            logger.warning(f"Video re-encode trim failed ({res.stderr[-200:]}), trying audio-only trim...")
            out_audio_name = Path(input_filename).stem + f"_trimmed_{int(start_time)}s_to_{int(end_time)}s.mp3"
            out_path = os.path.join(temp_dir, out_audio_name)
            out_filename = out_audio_name
            cmd_audio = [
                ffmpeg_bin,
                '-y',
                '-ss', str(start_time),
                '-to', str(end_time),
                '-i', input_path,
                '-c:a', 'aac',
                '-b:a', '192k',
                out_path
            ]
            res_audio = subprocess.run(cmd_audio, capture_output=True, text=True, timeout=120)
            if res_audio.returncode != 0:
                raise RuntimeError(f"FFmpeg trim failed: {res_audio.stderr[-300:]}")
                
        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            raise RuntimeError("Trimmed media output file is empty")
            
        mimetype = 'video/mp4' if out_filename.endswith('.mp4') else 'audio/mpeg'
        return send_file(
            out_path,
            as_attachment=True,
            download_name=out_filename,
            mimetype=mimetype
        )
    except Exception as e:
        logger.error(f"Error trimming media: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/combine-audio-image', methods=['POST'])
def combine_audio_image():
    """
    Create an MP4 video from an audio file and an image cover/poster, with optional duration and aspect ratio
    """
    if 'audio' not in request.files or 'image' not in request.files:
        return jsonify({'error': 'Both audio and image files are required'}), 400
        
    audio_file = request.files['audio']
    image_file = request.files['image']
    
    if audio_file.filename == '' or image_file.filename == '':
        return jsonify({'error': 'Missing audio or image filename'}), 400
        
    aspect_ratio = request.form.get('aspectRatio', '9:16')  # '9:16' (Reels), '16:9' (Landscape), '1:1' (Square)
    try:
        custom_duration = float(request.form.get('duration', 0))
    except (ValueError, TypeError):
        custom_duration = 0.0
        
    temp_dir = tempfile.mkdtemp()
    audio_filename = secure_filename(audio_file.filename) or 'audio.mp3'
    image_filename = secure_filename(image_file.filename) or 'cover.jpg'
    
    audio_path = os.path.join(temp_dir, audio_filename)
    image_path = os.path.join(temp_dir, image_filename)
    
    audio_file.save(audio_path)
    image_file.save(image_path)
    
    out_video_name = Path(audio_filename).stem + '_with_cover.mp4'
    out_video_path = os.path.join(temp_dir, out_video_name)
    
    # Scale filters for common aspect ratios
    if aspect_ratio == '9:16':
        vf_filter = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
    elif aspect_ratio == '16:9':
        vf_filter = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black"
    elif aspect_ratio == '1:1':
        vf_filter = "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:black"
    else:
        vf_filter = "scale=trunc(iw/2)*2:trunc(ih/2)*2"
        
    ffmpeg_bin = get_ffmpeg_binary()
    
    try:
        cmd = [
            ffmpeg_bin,
            '-y',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-vf', vf_filter,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-preset', 'fast',
            '-crf', '19',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p'
        ]
        
        if custom_duration > 0:
            cmd.extend(['-t', str(custom_duration)])
        else:
            cmd.append('-shortest')
            
        cmd.append(out_video_path)
        
        logger.info(f"Combining audio & image to video: {cmd}")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg combine failed: {res.stderr[-300:]}")
            
        if not os.path.exists(out_video_path) or os.path.getsize(out_video_path) == 0:
            raise RuntimeError("Generated combined video file is empty")
            
        return send_file(
            out_video_path,
            as_attachment=True,
            download_name=out_video_name,
            mimetype='video/mp4'
        )
    except Exception as e:
        logger.error(f"Error combining audio and image: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video to SRT API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument(
        '--model-id',
        default='Oriserve/Whisper-Hindi2Hinglish-Apex',
        help='Default model ID'
    )
    parser.add_argument('--device', default='cuda', help='Device to run model on')
    parser.add_argument('--dtype', default='float16', help='Data type for model')
    
    args = parser.parse_args()

    # Detect available device with CPU fallback
    available_device = get_device(args.device)

    # Update global config
    MODEL_CONFIG['model_id'] = args.model_id
    MODEL_CONFIG['device'] = available_device
    MODEL_CONFIG['dtype'] = torch_dtype_from_str(args.dtype, available_device)

    logger.info(f"Starting API server on http://{args.host}:{args.port}")
    logger.info(f"Using model: {MODEL_CONFIG['model_id']}")
    logger.info(f"Device: {available_device}, dtype: {MODEL_CONFIG['dtype']}")
    
    # Show GPU info if available
    if available_device == 'cuda':
        import torch
        gpu_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        logger.info(f"🚀 GPU Acceleration: {gpu_name} ({total_memory:.1f} GB)")
    else:
        logger.info("💻 Running on CPU (slower). To use GPU, run: install_cuda_pytorch.bat")
    
    app.run(host=args.host, port=args.port, debug=False)
