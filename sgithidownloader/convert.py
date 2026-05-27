import os
import shutil
import subprocess


AUDIO_FORMATS = {"aac", "alac", "flac", "m4a", "mp3", "opus", "vorbis", "wav"}
VIDEO_FORMATS = {"mp4", "webm", "avi", "mkv"}
FORMAT_TO_EXTENSION = {
    "aac": ".aac",
    "alac": ".m4a",
    "flac": ".flac",
    "m4a": ".m4a",
    "mp3": ".mp3",
    "opus": ".opus",
    "vorbis": ".ogg",
    "wav": ".wav",
    "mp4": ".mp4",
    "webm": ".webm",
    "avi": ".avi",
    "mkv": ".mkv",
}

EXTENSION_TO_TYPE = {
    ".aac": "audio",
    ".aiff": "audio",
    ".alac": "audio",
    ".flac": "audio",
    ".m4a": "audio",
    ".mp3": "audio",
    ".ogg": "audio",
    ".opus": "audio",
    ".wav": "audio",
    ".avi": "video",
    ".mkv": "video",
    ".mov": "video",
    ".mp4": "video",
    ".webm": "video",
}


def _format_kind(format_name):
    if format_name in AUDIO_FORMATS:
        return "audio"
    if format_name in VIDEO_FORMATS:
        return "video"
    raise ValueError(f"Unsupported output format: {format_name}")


def _input_kind(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    return EXTENSION_TO_TYPE.get(extension)


def _build_output_path(input_file, output_path, target_format):
    output_extension = FORMAT_TO_EXTENSION[target_format]
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    if output_path:
        if os.path.isdir(output_path):
            return os.path.join(output_path, f"{base_name}{output_extension}")

        target_dir = os.path.dirname(output_path)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        root, extension = os.path.splitext(output_path)
        if extension:
            return output_path
        return f"{output_path}{output_extension}"

    return os.path.join(os.path.dirname(input_file), f"{base_name}{output_extension}")


def _build_ffmpeg_command(input_file, output_file, target_format):
    command = ["ffmpeg", "-y", "-i", input_file]
    target_kind = _format_kind(target_format)

    if target_kind == "audio":
        command.extend(["-vn"])

        if target_format == "alac":
            command.extend(["-c:a", "alac"])
        elif target_format == "vorbis":
            command.extend(["-c:a", "libvorbis"])
        elif target_format == "opus":
            command.extend(["-c:a", "libopus"])

    command.append(output_file)
    return command


def convert_media_file(input_file, target_format, output_path=None):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg is required for media conversion and was not found in PATH.")

    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    normalized_format = target_format.lower()
    input_kind = _input_kind(input_file)
    output_kind = _format_kind(normalized_format)

    if input_kind is None:
        raise ValueError(
            "Unsupported input file type. Supported inputs include common audio/video formats such as mp3, wav, flac, m4a, opus, mp4, webm, avi, and mkv."
        )

    if input_kind == "audio" and output_kind == "video":
        raise ValueError("Cannot convert an audio-only file into a video format.")

    output_file = _build_output_path(input_file, output_path, normalized_format)
    command = _build_ffmpeg_command(input_file, output_file, normalized_format)

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "ffmpeg conversion failed"
        raise RuntimeError(message)

    return output_file


def convert_main(input_file, output_format, output_path=None):
    output_file = convert_media_file(input_file, output_format, output_path)
    print(f"Converted file saved to: {output_file}")
    return output_file