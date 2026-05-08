import requests, base64, os
import yt_dlp, re
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.flac import Picture
from PIL import Image
from tqdm import tqdm

from sgithidownloader.shared import *

EasyID3.RegisterTextKey("description", "COMM")


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


def crop_thumbnail_for_audio_file(image_file_path):
    image_file = Image.open(image_file_path)
    width, height = image_file.size
    # Assuming width > height, crop to square
    if width > height:
        left = (width - height) // 2
        top = 0
        right = left + height
        bottom = height
    else:
        # If height > width, but in this case it's not
        top = (height - width) // 2
        left = 0
        bottom = top + width
        right = width
    cropped_img = image_file.crop((left, top, right, bottom))
    cropped_img.save(image_file_path)
    print(f"Cropped thumbnail to square: {image_file_path}")


def download_audio_file(url: str, output, format="best"):
    target_format = format if format != "best" else "opus"
    with tqdm(unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading audio") as pbar:
        ydl_opts = {
            "format": "bestaudio/best",
            "embed-metadata": True,
            "add-metadata": True,
            "continuedl": False,
            # include extension in the template to ensure saved files have proper suffixes
            "outtmpl": os.path.join(output, "%(title)s [%(id)s].%(ext)s"),
            "progress_hooks": [lambda d: progress_hook(d, pbar)],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": format,
                    "preferredquality": "0",  # 0 is best
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # prepare_filename returns the filename including extension; convert to target format
            filename = os.path.splitext(ydl.prepare_filename(info))[0]
            filename = f"{filename}.{target_format}"
            print(f"Downloaded: {filename}")
            return filename, info


def embed_image_in_audio_file(audio_file_path, image_file_path, info):
    try:
        with open(image_file_path, "rb") as f:
            image_data = f.read()

        cover_art = Picture()
        cover_art.data = image_data
        cover_art.type = 3

        encoded_picture = base64.b64encode(cover_art.write()).decode("ascii")
        if audio_file_path.endswith(".mp3"):
            # Use EasyID3 for text metadata
            audio_file = EasyID3(audio_file_path)
            audio_file["title"] = info.get("title", "")
            audio_file["artist"] = info.get("uploader", "")
            audio_file["album"] = info.get("album", "")
            audio_file["date"] = str(info.get("upload_date", ""))
            audio_file["description"] = info.get("description", "")
            audio_file.save()

            # Use ID3 for picture
            id3 = ID3(audio_file_path)
            id3.add(
                APIC(
                    encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_data
                )
            )
            id3.save()
        elif audio_file_path.endswith(".opus"):
            audio_file = OggOpus(audio_file_path)
            audio_file["metadata_block_picture"] = encoded_picture
            audio_file["title"] = info.get("title", "")
            audio_file["artist"] = info.get("uploader", "")
            audio_file["album"] = info.get("album", "")
            audio_file["date"] = str(info.get("upload_date", ""))
            audio_file["description"] = info.get("description", "")
            audio_file.save()
        else:
            print(
                f"Unsupported format for embedding metadata: {audio_file_path}. Skipping metadata embedding."
            )
            return

        print(f"Successfully embedded metadata and image into {audio_file_path}")

    except FileNotFoundError:
        print(
            f"Error: Make sure files '{audio_file_path}' and '{image_file_path}' exist."
        )
    except Exception as e:
        print(f"An error occurred: {e}")

def audio_main(url, output="./", format="best"):
    audio_file_path, info = download_audio_file(url, output, format)
    image_file_path = grab_thumb(url, output)
    crop_thumbnail_for_audio_file(image_file_path)
    embed_image_in_audio_file(audio_file_path, image_file_path, info)
    if os.path.exists(image_file_path):
        os.remove(image_file_path)
        print(f"Deleted thumbnail file {image_file_path}")
    return audio_file_path, info