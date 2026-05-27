# sgithidownloader/webui.py
# This module implements the web interface for SgithiDownloader using Flask.

# External package imports
import os
import threading
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from pytube import Playlist
from werkzeug.utils import secure_filename

# Local imports
from sgithidownloader.audio import audio_main
from sgithidownloader.convert import AUDIO_FORMATS, FORMAT_TO_EXTENSION, VIDEO_FORMATS, convert_main
from sgithidownloader.video import video_main

app = Flask(__name__)
app.secret_key = "sgithi-downloader-secret-key"
# Use absolute path for upload folder so send_from_directory resolves correctly
app.config["UPLOAD_FOLDER"] = os.path.abspath("./downloads")
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024  # 512MB max file size

# Ensure download directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Global variables for progress tracking
download_progress = {}
current_downloads = {}


def update_progress(task_id, status, progress=None, message=None):
    """Update download progress for a task"""
    download_progress[task_id] = {
        "status": status,
        "progress": progress,
        "message": message,
        "timestamp": time.time(),
    }


def download_worker(task_id, url, output_dir, download_type, format_type):
    """Background worker for downloads"""
    try:
        update_progress(task_id, "starting", 0, f"Starting {download_type} download...")

        saved_files = []
        if download_type == "video":
            update_progress(task_id, "downloading", 10, "Downloading video...")
            video_file, _ = video_main(url, output_dir, format_type)
            saved_files.append(os.path.basename(video_file))
        elif download_type == "audio":
            update_progress(task_id, "downloading", 10, "Downloading audio...")
            audio_file, _ = audio_main(url, output_dir, format_type)
            saved_files.append(os.path.basename(audio_file))
        elif download_type == "playlist":
            update_progress(task_id, "processing", 5, "Processing playlist...")
            yt_playlist = Playlist(url)
            total_videos = len(yt_playlist.video_urls)
            update_progress(
                task_id, "downloading", 10, f"Found {total_videos} videos in playlist"
            )

            for i, video in enumerate(yt_playlist.videos, 1):
                progress = 10 + (i / total_videos) * 80
                update_progress(
                    task_id,
                    "downloading",
                    progress,
                    f"Downloading video {i}/{total_videos}: {video.title[:50]}...",
                )

                try:
                    if format_type in [
                        "best",
                        "aac",
                        "alac",
                        "flac",
                        "m4a",
                        "mp3",
                        "opus",
                        "vorbis",
                        "wav",
                    ]:
                        audio_file, _ = audio_main(
                            video.watch_url, output_dir, format_type
                        )
                        saved_files.append(os.path.basename(audio_file))
                    else:
                        video_file, _ = video_main(
                            video.watch_url, output_dir, format_type
                        )
                        saved_files.append(os.path.basename(video_file))
                except Exception as e:
                    update_progress(
                        task_id,
                        "error",
                        progress,
                        f"Error downloading {video.title}: {str(e)}",
                    )
                    continue

        # attach list of saved files to current_downloads so frontend can trigger browser download
        current_downloads[task_id]["files"] = saved_files
        update_progress(task_id, "completed", 100, "Download completed successfully!")

    except Exception as e:
        update_progress(task_id, "error", 0, f"Download failed: {str(e)}")
        current_downloads[task_id]["files"] = []


def convert_worker(task_id, input_file, output_dir, target_format, source_name):
    """Background worker for local file conversion"""
    try:
        update_progress(task_id, "starting", 0, "Preparing file conversion...")
        update_progress(task_id, "processing", 20, "Converting file with FFmpeg...")
        output_name = os.path.splitext(source_name)[0] + FORMAT_TO_EXTENSION[target_format]
        output_path = os.path.join(output_dir, output_name)
        converted_file = convert_main(input_file, target_format, output_path)
        update_progress(task_id, "processing", 90, "Finalizing converted file...")
        current_downloads[task_id]["files"] = [os.path.basename(converted_file)]
        update_progress(task_id, "completed", 100, "Conversion completed successfully!")
    except Exception as e:
        update_progress(task_id, "error", 0, f"Conversion failed: {str(e)}")
        current_downloads[task_id]["files"] = []
    finally:
        try:
            if os.path.isfile(input_file):
                os.remove(input_file)
        except OSError:
            pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    # Use server-side uploads folder; users will download via browser
    output_dir = app.config["UPLOAD_FOLDER"]
    download_type = request.form.get("download_type")

    # Get format based on download type
    if download_type == "video":
        format_type = request.form.get("format_video", "mp4")
    elif download_type == "audio":
        format_type = request.form.get("format_audio", "best")
    elif download_type == "playlist":
        format_type = request.form.get("format_playlist", "mp4")
    else:
        format_type = "mp4"

    if not url:
        flash("Please provide a valid URL", "error")
        return redirect(url_for("index"))

    # Create unique task ID
    task_id = f"{int(time.time())}_{hash(url) % 10000}"

    # Start download in background thread
    thread = threading.Thread(
        target=download_worker,
        args=(task_id, url, output_dir, download_type, format_type),
    )
    thread.daemon = True
    thread.start()

    current_downloads[task_id] = {
        "url": url,
        "type": download_type,
        "format": format_type,
        "start_time": time.time(),
        "files": [],
    }

    flash(f"Download started! Task ID: {task_id}", "success")
    return redirect(url_for("progress", task_id=task_id))


@app.route("/convert", methods=["POST"])
def convert_file():
    uploaded_file = request.files.get("media_file")
    target_format = request.form.get("target_format", "mp3").lower()

    if uploaded_file is None or uploaded_file.filename == "":
        flash("Please choose a file to convert", "error")
        return redirect(url_for("index"))

    if target_format not in AUDIO_FORMATS | VIDEO_FORMATS:
        flash("Please choose a supported output format", "error")
        return redirect(url_for("index"))

    original_name = secure_filename(uploaded_file.filename)
    if not original_name:
        flash("Please choose a valid file name", "error")
        return redirect(url_for("index"))

    task_id = f"{int(time.time())}_{hash((original_name, target_format)) % 10000}"
    stored_name = f"{task_id}_{original_name}"
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_name)
    uploaded_file.save(input_path)

    current_downloads[task_id] = {
        "url": original_name,
        "type": "convert",
        "format": target_format,
        "start_time": time.time(),
        "files": [],
    }

    thread = threading.Thread(
        target=convert_worker,
        args=(task_id, input_path, app.config["UPLOAD_FOLDER"], target_format, original_name),
    )
    thread.daemon = True
    thread.start()

    flash(f"Conversion started! Task ID: {task_id}", "success")
    return redirect(url_for("progress", task_id=task_id))


@app.route("/progress/<task_id>")
def progress(task_id):
    if task_id not in current_downloads:
        flash("Task not found", "error")
        return redirect(url_for("index"))

    task_info = current_downloads[task_id]
    progress_info = download_progress.get(
        task_id, {"status": "unknown", "progress": 0, "message": "Initializing..."}
    )

    return render_template(
        "progress.html",
        task_id=task_id,
        task_info=task_info,
        progress_info=progress_info,
    )


@app.route("/api/progress/<task_id>")
def get_progress(task_id):
    progress_info = download_progress.get(
        task_id, {"status": "unknown", "progress": 0, "message": "Task not found"}
    )
    # include generated filenames if available
    files = current_downloads.get(task_id, {}).get("files", [])
    response = dict(progress_info)
    response["files"] = files
    return jsonify(response)


@app.route("/downloads")
def downloads():
    """List downloaded files"""
    from datetime import datetime

    download_dir = app.config["UPLOAD_FOLDER"]
    files = []

    if os.path.exists(download_dir):
        for filename in os.listdir(download_dir):
            filepath = os.path.join(download_dir, filename)
            if os.path.isfile(filepath):
                files.append(
                    {
                        "name": filename,
                        "size": os.path.getsize(filepath),
                        "modified": datetime.fromtimestamp(
                            os.path.getmtime(filepath)
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

    # Sort by modification time (newest first)
    files.sort(key=lambda x: x["modified"], reverse=True)

    return render_template("downloads.html", files=files)


@app.route("/download_file/<filename>")
def download_file(filename):
    """Serve downloaded files"""
    from flask import send_from_directory, abort

    download_dir = app.config["UPLOAD_FOLDER"]
    # Try direct match first
    candidate = os.path.join(download_dir, filename)
    if os.path.isfile(candidate):
        return send_from_directory(download_dir, filename, as_attachment=True)

    # Try common extensions
    common_exts = [
        ".mp4",
        ".mp3",
        ".opus",
        ".ogg",
        ".flac",
        ".m4a",
        ".aac",
        ".webm",
        ".avi",
        ".mkv",
        ".wav",
    ]
    for ext in common_exts:
        cand = os.path.join(download_dir, filename + ext)
        if os.path.isfile(cand):
            return send_from_directory(
                download_dir, os.path.basename(cand), as_attachment=True
            )

    # Fallback: match by basename (strip extension) to handle files saved without extension
    matches = []
    for f in os.listdir(download_dir):
        if os.path.splitext(f)[0] == filename:
            matches.append(f)

    if matches:
        # pick most recently modified match
        matches.sort(
            key=lambda f: os.path.getmtime(os.path.join(download_dir, f)), reverse=True
        )
        return send_from_directory(download_dir, matches[0], as_attachment=True)

    # No file found
    abort(404)


def run_webui(host="0.0.0.0", port=5000, debug=False):
    """Run the web UI"""
    print(f"🎵 Starting SgithiDownloader Web UI...")
    print(f"🌐 Open your browser to: http://localhost:{port}")
    print(
        f"📁 Downloads will be saved to: {os.path.abspath(app.config['UPLOAD_FOLDER'])}"
    )
    print("Press Ctrl+C to stop the server")

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_webui()
