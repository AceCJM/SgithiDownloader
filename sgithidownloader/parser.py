import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
VERSION = "2.0.3"

def create_parser():
    parser = argparse.ArgumentParser(
        prog="sgithidownloader",
        description="🎵 SgithiDownloader - Download YouTube videos and audio with style",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sgithidownloader video https://youtube.com/watch?v=... -o ./downloads
  sgithidownloader audio https://youtube.com/watch?v=... --format opus
  sgithidownloader playlist https://youtube.com/playlist?... -o ./music
  sgithidownloader formats

For more help: sgithidownloader <command> --help
        """
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"SgithiDownloader {VERSION} - Developed by Cody Miller - https://github.com/AceCJM/SgithiDownloader"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Video command
    video_parser = subparsers.add_parser(
        "video",
        help="Download a single video",
        description="Download a single YouTube video in various formats"
    )
    video_parser.add_argument("url", help="YouTube video URL")
    video_parser.add_argument(
        "-o", "--output",
        type=str,
        default="./",
        help="Output directory (default: current directory)"
    )
    video_parser.add_argument(
        "-f", "--format",
        type=str,
        default="mp4",
        choices=["mp4", "webm", "avi", "mkv"],
        help="Video format (default: mp4)"
    )

    # Audio command
    audio_parser = subparsers.add_parser(
        "audio",
        help="Download audio from a video",
        description="Extract and download audio from YouTube videos"
    )
    audio_parser.add_argument("url", help="YouTube video URL")
    audio_parser.add_argument(
        "-o", "--output",
        type=str,
        default="./",
        help="Output directory (default: current directory)"
    )
    audio_parser.add_argument(
        "-f", "--format",
        type=str,
        default="best",
        choices=["best", "aac", "alac", "flac", "m4a", "mp3", "opus", "vorbis", "wav"],
        help="Audio format (default: best)"
    )

    # Playlist command
    playlist_parser = subparsers.add_parser(
        "playlist",
        help="Download all videos from a playlist",
        description="Download entire YouTube playlists as video or audio"
    )
    playlist_parser.add_argument("url", help="YouTube playlist URL")
    playlist_parser.add_argument(
        "-o", "--output",
        type=str,
        default="./",
        help="Output directory (default: current directory)"
    )
    playlist_parser.add_argument(
        "-t", "--type",
        type=str,
        default="video",
        choices=["video", "audio"],
        help="Download type (default: video)"
    )
    playlist_parser.add_argument(
        "-f", "--format",
        type=str,
        default="mp4",
        help="Format for video (mp4, webm, etc.) or audio (opus, mp3, etc.)"
    )

    # Formats command
    formats_parser = subparsers.add_parser(
        "formats",
        help="List available formats",
        description="Show all supported video and audio formats"
    )

    # WebUI command
    webui_parser = subparsers.add_parser(
        "webui",
        help="Start the web interface",
        description="Run SgithiDownloader with a user-friendly web interface"
    )

    return parser

def show_welcome():
    welcome_text = Text("🎵 Welcome to SgithiDownloader!", style="bold magenta")
    panel = Panel.fit(
        "[bold blue]Your friendly YouTube downloader with embedded thumbnails and metadata[/bold blue]\n\n"
        "[dim]Use 'sgithidownloader <command> --help' for detailed help on each command[/dim]",
        title=welcome_text,
        border_style="blue"
    )
    console.print(panel)

def show_formats():
    console.print("\n[bold green]🎵 Available Audio Formats:[/bold green]")
    formats = {
        "best": "Auto-select best quality (recommended)",
        "opus": "Opus - High quality, supports metadata",
        "mp3": "MP3 - Universal compatibility, supports metadata",
        "flac": "FLAC - Lossless, high quality",
        "aac": "AAC - Good quality, wide support",
        "m4a": "M4A - AAC in MP4 container",
        "alac": "ALAC - Apple Lossless",
        "vorbis": "Vorbis - Open source, good quality",
        "wav": "WAV - Uncompressed"
    }

    for fmt, desc in formats.items():
        console.print(f"  [cyan]{fmt:8}[/cyan] - {desc}")

    console.print("\n[bold green]🎬 Available Video Formats:[/bold green]")
    video_formats = ["mp4", "webm", "avi", "mkv"]
    for fmt in video_formats:
        console.print(f"  [cyan]{fmt}[/cyan]")

    console.print("\n[dim]📝 Note: Metadata embedding is only supported for opus and mp3 formats[/dim]")
