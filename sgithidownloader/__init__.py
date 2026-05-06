import sys, requests, base64, os
import yt_dlp, re
from pytube import Playlist
import argparse

from sgithidownloader.audio import audio_main
from sgithidownloader.video import video_main

def cli():
    parser = argparse.ArgumentParser(
        description="SgithiDownloader - Version 1.0.2 - Download YouTube videos"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="SgithiDownloader 1.0.2 - Developed by Cody Miller (cmiller@fuck.it) - https://github.com/AceCJM/SgithiDownloader",
    )
    parser.add_argument(
        "-s", "--single", type=str, help="Download a single video from URL"
    )
    parser.add_argument(
        "-p", "--playlist", type=str, help="Download all videos from playlist URL"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="./", help="Output directory (default: ./)"
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="mp4",
        help="File format (mp4, webm, audio, etc.) (default: mp4)",
    )
    parser.add_argument(
        "-af",
        "--audio_format",
        type=str,
        default="best",
        help="Audio format (opus, flac, etc.) (default: best)",
    )
    parser.add_argument(
        "-l",
        "--listFormats",
        action="store_true",
        help="List available audio formats and exit",
    )

    args = parser.parse_args()

    if args.listFormats:
        print("Available audio formats:")
        print(
            "- best (default, auto-selects the best format)\n- aac\n- alac\n- flac\n- m4a\n- mp3\n- opus\n- vorbis\n- wav",
            "Metadata is only embedded in opus and mp3 formats due to mutagen limitations.",
        )
        return

    if args.single:
        if args.format == "audio":
            format = args.audio_format
            audio_main(args.single, args.output, format)
        else:
            video_main(args.single, args.output, args.format)
    elif args.playlist:
        yt_play = Playlist(args.playlist)
        print(f"Downloading {len(yt_play.video_urls)} videos")
        if args.format == "audio":
            format = args.audio_format
            for video in yt_play.videos:
                audio_main(video.watch_url, args.output, format)
        else:
            for video in yt_play.videos:
                video_main(video.watch_url, args.output, args.format)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
