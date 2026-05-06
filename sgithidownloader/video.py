import os
import yt_dlp
from tqdm import tqdm

def progress_hook(d, pbar):
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes'] is not None:
            pbar.total = d['total_bytes']
            pbar.update(d['downloaded_bytes'] - pbar.n)
        elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] is not None:
            pbar.total = d['total_bytes_estimate']
            pbar.update(d['downloaded_bytes'] - pbar.n)
    elif d['status'] == 'finished':
        pbar.close()

def download_video_file(url: str, output, format="mp4"):
    with tqdm(unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading video") as pbar:
        ydl_opts = {
            "format": f"bestvideo[ext={format}]+bestaudio/best[ext={format}]/best",
            "embed-metadata": True,
            "add-metadata": True,
            "continuedl": False,
            "outtmpl": os.path.join(output, "%(title)s [%(id)s]"),
            "progress_hooks": [lambda d: progress_hook(d, pbar)],
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