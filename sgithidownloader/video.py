# sgithidownloader/video.py
# This module handles downloading videos.

# External package imports
import os
from tqdm import tqdm as progressbar

# Local imports
from sgithidownloader.shared import progress_hook, download_file


def download_video_file(video_url: str, output_directory: str, video_format="mp4"):
    with progressbar(
        unit="B", unit_scale=True, unit_divisor=1024, desc="Downloading video"
    ) as pbar:
        ytdlp_options = {
            "format": f"bestvideo[ext={video_format}]+bestaudio/best[ext={video_format}]/best",
            "embed-metadata": True,
            "add-metadata": True,
            "continuedl": False,
            # include extension in the template to ensure saved files have proper suffixes
            "outtmpl": os.path.join(output_directory, "%(title)s [%(id)s].%(ext)s"),
            "progress_hooks": [lambda d: progress_hook(d, pbar)],
        }
        return download_file(ytdlp_options, video_url, output_directory)


def video_main(video_url, video_format="./", format="mp4"):
    try:
        video_file_path, file_embed_info = download_video_file(video_url, video_format, format)
        print(f"Video downloaded successfully: {video_file_path}")
        return video_file_path, file_embed_info
    except Exception as e:
        print(f"An error occurred while downloading the video: {e}")
        raise
