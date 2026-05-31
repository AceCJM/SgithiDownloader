# sgithidownloader/audio.py
# This module handles downloading audio files and embedding metadata.

# External package imports
import base64, os
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.flac import Picture
from PIL import Image
from tqdm import tqdm as progress_bar

# Local imports
from sgithidownloader.shared import grab_thumbnail, progress_hook, download_file

EasyID3.RegisterTextKey("description", "COMM")


def crop_image_for_embeded_thumbnail(image_file_path):
    image_file = Image.open(image_file_path)
    image_width, image_height = image_file.size
    # Assuming width > height, crop to square
    if image_width > image_height:
        left = (image_width - image_height) // 2
        top = 0
        right = left + image_height
        bottom = image_height
    else:
        # If height > width, but in this case it's not
        top = (image_height - image_width) // 2
        left = 0
        bottom = top + image_width
        right = image_width
    cropped_img = image_file.crop((left, top, right, bottom))
    cropped_img.save(image_file_path)
    print(f"Cropped thumbnail to square: {image_file_path}")


def download_audio_file(audio_url: str, output_directory: str, audio_format="best"):
    with progress_bar(
        unit="B", unit_scale=True, unit_divisor=1024, desc="Downloading audio"
    ) as pbar:
        ytdlp_options = {
            "format": f"bestaudio[ext={audio_format}]/best",
            "embed-metadata": True,
            "add-metadata": True,
            "continuedl": False,
            # include extension in the template to ensure saved files have proper suffixes
            "outtmpl": os.path.join(output_directory, "%(title)s [%(id)s].%(ext)s"),
            "progress_hooks": [lambda d: progress_hook(d, pbar)],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "0",  # 0 is best
                }
            ],
        }
        return download_file(ytdlp_options, audio_url, output_directory)


def embed_image_into_audio_file(audio_file_path, image_file_path, info):
    try:
        with open(image_file_path, "rb") as f:
            image_data = f.read()

        embeded_thumbnail = Picture()
        embeded_thumbnail.data = image_data
        embeded_thumbnail.type = 3
        encoded_picture = base64.b64encode(embeded_thumbnail.write()).decode("ascii")

        if audio_file_path.endswith(".mp3"):
            # Use EasyID3 for text metadata
            audio_file_data = EasyID3(audio_file_path)
            audio_file_data["title"] = info.get("title", "")
            audio_file_data["artist"] = info.get("uploader", "")
            audio_file_data["album"] = info.get("album", "")
            audio_file_data["date"] = str(info.get("upload_date", ""))
            audio_file_data["description"] = info.get("description", "")
            audio_file_data.save()

            # Use ID3 for picture
            audio_file = ID3(audio_file_path)
            audio_file.add(
                APIC(
                    encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_data
                )
            )
            audio_file.save()
        elif audio_file_path.endswith(".opus"):
            audio_file_data = OggOpus(audio_file_path)
            audio_file_data["metadata_block_picture"] = encoded_picture
            audio_file_data["title"] = info.get("title", "")
            audio_file_data["artist"] = info.get("uploader", "")
            audio_file_data["album"] = info.get("album", "")
            audio_file_data["date"] = str(info.get("upload_date", ""))
            audio_file_data["description"] = info.get("description", "")
            audio_file_data.save()
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


def audio_main(audio_url, output_directory="./", audio_format="best"):
    audio_file_path, file_embed_info = download_audio_file(audio_url, output_directory, audio_format)
    image_file_path = grab_thumbnail(audio_url, output_directory)
    if image_file_path == -1:
        print("Skipping thumbnail embedding due to download failure.")
        return audio_file_path, file_embed_info
    crop_image_for_embeded_thumbnail(image_file_path)
    embed_image_into_audio_file(audio_file_path, image_file_path, file_embed_info)
    if os.path.exists(image_file_path):
        os.remove(image_file_path)
        print(f"Deleted thumbnail file {image_file_path}")
    return audio_file_path, file_embed_info
