import os
import requests, re

import yt_dlp


def get_video_id(url):
    youtube_regex = r"v=([^&]+)"
    match = re.search(youtube_regex, url)
    if match:
        return match.group(1)
    else:
        return None


def grab_thumbnail(url: str, output) -> str:
    videoId = get_video_id(url)
    url = f"http://img.youtube.com/vi/{videoId}/maxresdefault.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        image_file_path = os.path.join(output, f"{videoId}_thumb.jpg")
        with open(image_file_path, "wb") as f:
            f.write(response.content)
        print("Thumbnail downloaded")
        return image_file_path
    else:
        print("Failed to download thumbnail")
        return -1


def progress_hook(d, pbar):
    if d["status"] == "downloading":
        if "total_bytes" in d and d["total_bytes"] is not None:
            pbar.total = d["total_bytes"]
            pbar.update(d["downloaded_bytes"] - pbar.n)
        elif "total_bytes_estimate" in d and d["total_bytes_estimate"] is not None:
            pbar.total = d["total_bytes_estimate"]
            pbar.update(d["downloaded_bytes"] - pbar.n)
    elif d["status"] == "finished":
        pbar.close()


def download_file(ydl_opts, url, output):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = os.path.join(output, ydl.prepare_filename(info))
        print(f"Downloaded: {filename}")
        return filename, info
