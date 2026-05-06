import os
import yt_dlp

def download_video_file(url: str, output, format="mp4"):
    ydl_opts = {
        "format": f"bestvideo[ext={format}]+bestaudio/best[ext={format}]/best",
        "embed-metadata": True,
        "add-metadata": True,
        "continuedl": False,
        "outtmpl": os.path.join(output, "%(title)s [%(id)s]"),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = os.path.splitext(ydl.prepare_filename(info))[0]
        filename = f"{filename}.{format}"
        print(f"Downloaded: {filename}")
        return filename, info

def video_main(url, output="./", format="mp4"):
    try:
        video_file_path, info = download_video_file(url, output, format)
        print(f"Video downloaded successfully: {video_file_path}")
    except Exception as e:
        print(f"An error occurred while downloading the video: {e}")