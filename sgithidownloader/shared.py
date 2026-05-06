
import os
import requests, re

def get_video_id(url):
    youtube_regex = r"v=([^&]+)"
    match = re.search(youtube_regex, url)
    if match:
        return match.group(1)
    else:
        return None

def grab_thumb(url: str, output) -> str:
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