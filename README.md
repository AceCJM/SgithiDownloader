# sgithidownloader

A Python tool to download YouTube videos and audio in various high-quality formats with embedded thumbnails and metadata.

## Features

- 🎬 Download individual YouTube videos or entire playlists
- 🎵 Support for multiple video formats (MP4, WebM, AVI, MKV)
- 🎧 Convert and download audio in various formats (Opus, MP3, FLAC, AAC, etc.)
- 🔄 Convert existing local audio and video files between supported formats
- 🖼️ Automatically embed video thumbnails as album art
- 📋 Include metadata (title, artist, album, date, description) in supported formats
- ✂️ Crop thumbnails to square format for better display
- 📊 Beautiful progress bars and colored output
- 🚀 Intuitive subcommand-based CLI interface
- 🌐 User-friendly web interface with real-time progress tracking

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)

### Install FFmpeg

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**On macOS:**
```bash
brew install ffmpeg
```

**On Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Install the Package

```bash
pip install sgithidownloader
```

For development:
```bash
git clone https://github.com/AceCJM/SgithiDownloader.git
cd SgithiDownloader
pip install -e .
```

## Usage

The CLI uses a modern subcommand structure for clarity:

### Download a Single Video

```bash
sgithidownloader video "https://www.youtube.com/watch?v=VIDEO_ID" -o /path/to/output/
```

### Download Audio

```bash
sgithidownloader audio "https://www.youtube.com/watch?v=VIDEO_ID" -f opus -o /path/to/output/
```

### Download a Playlist

```bash
sgithidownloader playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID" -t audio -f mp3 -o /path/to/output/
```

### List Available Formats

```bash
sgithidownloader formats
```

### Convert A Local File

```bash
sgithidownloader convert ./input.wav -f mp3
sgithidownloader convert ./clip.mp4 -f webm -o ./converted/
```

### Get Help

```bash
# General help
sgithidownloader --help

# Help for specific command
sgithidownloader video --help
sgithidownloader audio --help
sgithidownloader playlist --help
```

## Web Interface

For users who prefer a graphical interface, SgithiDownloader includes a beautiful web UI:

```bash
sgithidownloader webui
```

This will start a local web server at `http://localhost:5000` where you can:

- 📱 Use an intuitive form-based interface
- 📊 Monitor download progress in real-time
- 📁 Browse and download completed files
- 🎯 Select formats with visual options
- 🔄 Upload and convert existing local media files
- 📂 Choose custom output directories

### Web UI Features

- **Real-time Progress**: Watch downloads progress with live updates
- **Format Selection**: Easy dropdown menus for video/audio formats
- **Download History**: View and download previously completed files
- **Responsive Design**: Works on desktop and mobile devices
- **Background Processing**: Downloads run in the background without blocking the UI

## Command Reference

### `sgithidownloader video`

Download a single YouTube video.

```bash
sgithidownloader video URL [OPTIONS]
```

**Options:**
- `-o, --output DIR`: Output directory (default: current directory)
- `-f, --format FORMAT`: Video format (mp4, webm, avi, mkv) (default: mp4)

### `sgithidownloader audio`

Download audio from a YouTube video.

```bash
sgithidownloader audio URL [OPTIONS]
```

**Options:**
- `-o, --output DIR`: Output directory (default: current directory)
- `-f, --format FORMAT`: Audio format (best, aac, alac, flac, m4a, mp3, opus, vorbis, wav) (default: best)

### `sgithidownloader playlist`

Download all videos from a YouTube playlist.

```bash
sgithidownloader playlist URL [OPTIONS]
```

**Options:**
- `-o, --output DIR`: Output directory (default: current directory)
- `-t, --type TYPE`: Download type (video or audio) (default: video)
- `-f, --format FORMAT`: Format (depends on type - video: mp4/webm/avi/mkv, audio: opus/mp3/etc.) (default: mp4)

### `sgithidownloader formats`

Display all available video and audio formats with descriptions.

### `sgithidownloader convert`

Convert a local media file into another supported format.

```bash
sgithidownloader convert INPUT [OPTIONS]
```

**Options:**
- `-f, --format FORMAT`: Target format (audio: aac, alac, flac, m4a, mp3, opus, vorbis, wav; video: mp4, webm, avi, mkv)
- `-o, --output PATH`: Output directory or output file path (default: alongside the input file)

### `sgithidownloader webui`

Start the web interface for graphical downloads.

```bash
sgithidownloader webui
```

**Description:** Launches a local web server at http://localhost:5000 with a user-friendly interface for downloading YouTube content.

## Examples

```bash
# Download a single video in MP4 format
sgithidownloader video "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f mp4

# Download audio in high-quality Opus format
sgithidownloader audio "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f opus -o ~/Music/

# Download an entire playlist as MP3 files
sgithidownloader playlist "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5G1G8jQGzq9j9j9j" -t audio -f mp3 -o ~/Music/Playlist/

# Download a playlist of videos
sgithidownloader playlist "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4qtr5G1G8jQGzq9j9j9j" -o ~/Videos/

# List all available formats
sgithidownloader formats
```

## Supported Formats

### Audio Formats
- **best**: Auto-select best quality (recommended)
- **opus**: High quality, supports metadata
- **mp3**: Universal compatibility, supports metadata
- **flac**: Lossless, high quality
- **aac**: Good quality, wide support
- **m4a**: AAC in MP4 container
- **alac**: Apple Lossless
- **vorbis**: Open source, good quality
- **wav**: Uncompressed

### Video Formats
- **mp4**: Most compatible format
- **webm**: Open format, good compression
- **avi**: Legacy format
- **mkv**: Advanced container format

**Note:** Metadata embedding is only supported for opus and mp3 formats.

## Dependencies

- **yt-dlp**: For downloading and extracting media
- **mutagen**: For embedding metadata in audio files
- **pytube**: For playlist handling
- **rich**: For beautiful console output
- **tqdm**: For progress bars
- **pillow**: For image processing
- **requests**: For downloading thumbnails
- **flask**: For the web interface

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Disclaimer

This tool is for personal use only. Respect YouTube's terms of service and copyright laws. The author is not responsible for misuse.