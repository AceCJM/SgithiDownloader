# WebUI Module for SgithiDownloader
# Run with: sgithidownloader webui

import os
import threading
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pytube import Playlist
from sgithidownloader.audio import audio_main
from sgithidownloader.video import video_main

app = Flask(__name__)
app.secret_key = 'sgithi-downloader-secret-key'
app.config['UPLOAD_FOLDER'] = './downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure download directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for progress tracking
download_progress = {}
current_downloads = {}

def update_progress(task_id, status, progress=None, message=None):
    """Update download progress for a task"""
    download_progress[task_id] = {
        'status': status,
        'progress': progress,
        'message': message,
        'timestamp': time.time()
    }

def download_worker(task_id, url, output_dir, download_type, format_type):
    """Background worker for downloads"""
    try:
        update_progress(task_id, 'starting', 0, f'Starting {download_type} download...')

        if download_type == 'video':
            update_progress(task_id, 'downloading', 10, 'Downloading video...')
            video_main(url, output_dir, format_type)
        elif download_type == 'audio':
            update_progress(task_id, 'downloading', 10, 'Downloading audio...')
            audio_main(url, output_dir, format_type)
        elif download_type == 'playlist':
            update_progress(task_id, 'processing', 5, 'Processing playlist...')
            yt_playlist = Playlist(url)
            total_videos = len(yt_playlist.video_urls)
            update_progress(task_id, 'downloading', 10, f'Found {total_videos} videos in playlist')

            for i, video in enumerate(yt_playlist.videos, 1):
                progress = 10 + (i / total_videos) * 80
                update_progress(task_id, 'downloading', progress,
                              f'Downloading video {i}/{total_videos}: {video.title[:50]}...')

                try:
                    if format_type in ['best', 'aac', 'alac', 'flac', 'm4a', 'mp3', 'opus', 'vorbis', 'wav']:
                        audio_main(video.watch_url, output_dir, format_type)
                    else:
                        video_main(video.watch_url, output_dir, format_type)
                except Exception as e:
                    update_progress(task_id, 'error', progress, f'Error downloading {video.title}: {str(e)}')
                    continue

        update_progress(task_id, 'completed', 100, 'Download completed successfully!')

    except Exception as e:
        update_progress(task_id, 'error', 0, f'Download failed: {str(e)}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    output_dir = request.form.get('output_dir', './downloads')
    download_type = request.form.get('download_type')

    # Get format based on download type
    if download_type == 'video':
        format_type = request.form.get('format_video', 'mp4')
    elif download_type == 'audio':
        format_type = request.form.get('format_audio', 'best')
    elif download_type == 'playlist':
        format_type = request.form.get('format_playlist', 'mp4')
    else:
        format_type = 'mp4'

    if not url:
        flash('Please provide a valid URL', 'error')
        return redirect(url_for('index'))

    # Create unique task ID
    task_id = f"{int(time.time())}_{hash(url) % 10000}"

    # Start download in background thread
    thread = threading.Thread(
        target=download_worker,
        args=(task_id, url, output_dir, download_type, format_type)
    )
    thread.daemon = True
    thread.start()

    current_downloads[task_id] = {
        'url': url,
        'type': download_type,
        'format': format_type,
        'output_dir': output_dir,
        'start_time': time.time()
    }

    flash(f'Download started! Task ID: {task_id}', 'success')
    return redirect(url_for('progress', task_id=task_id))

@app.route('/progress/<task_id>')
def progress(task_id):
    if task_id not in current_downloads:
        flash('Task not found', 'error')
        return redirect(url_for('index'))

    task_info = current_downloads[task_id]
    progress_info = download_progress.get(task_id, {'status': 'unknown', 'progress': 0, 'message': 'Initializing...'})

    return render_template('progress.html',
                         task_id=task_id,
                         task_info=task_info,
                         progress_info=progress_info)

@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    progress_info = download_progress.get(task_id, {'status': 'unknown', 'progress': 0, 'message': 'Task not found'})
    return jsonify(progress_info)

@app.route('/downloads')
def downloads():
    """List downloaded files"""
    from datetime import datetime
    download_dir = app.config['UPLOAD_FOLDER']
    files = []

    if os.path.exists(download_dir):
        for filename in os.listdir(download_dir):
            filepath = os.path.join(download_dir, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                })

    # Sort by modification time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)

    return render_template('downloads.html', files=files)

@app.route('/download_file/<filename>')
def download_file(filename):
    """Serve downloaded files"""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

def run_webui(host='0.0.0.0', port=5000, debug=False):
    """Run the web UI"""
    print(f"🎵 Starting SgithiDownloader Web UI...")
    print(f"🌐 Open your browser to: http://localhost:{port}")
    print(f"📁 Downloads will be saved to: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
    print("Press Ctrl+C to stop the server")

    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_webui()
