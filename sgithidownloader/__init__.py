import sys
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text
from pytube import Playlist

from sgithidownloader.audio import audio_main
from sgithidownloader.video import video_main
from sgithidownloader.parser import create_parser, show_welcome, show_formats

console = Console()

def cli():
    parser = create_parser()

    if len(sys.argv) == 1:
        show_welcome()
        parser.print_help()
        return

    args = parser.parse_args()

    if args.command == "formats":
        show_formats()
        return

    if not args.command:
        console.print("[red]❌ Error: No command specified. Use 'sgithidownloader --help' for usage.[/red]")
        return

    # Handle video download
    if args.command == "video":
        console.print(f"[green]🎬 Downloading video from:[/green] {args.url}")
        console.print(f"[blue]📁 Output directory:[/blue] {args.output}")
        console.print(f"[yellow]📹 Format:[/yellow] {args.format}")
        try:
            video_main(args.url, args.output, args.format)
            console.print("[green]✅ Video download completed successfully![/green]")
        except Exception as e:
            console.print(f"[red]❌ Error downloading video: {e}[/red]")

    # Handle audio download
    elif args.command == "audio":
        console.print(f"[green]🎵 Downloading audio from:[/green] {args.url}")
        console.print(f"[blue]📁 Output directory:[/blue] {args.output}")
        console.print(f"[yellow]🎧 Format:[/yellow] {args.format}")
        try:
            audio_main(args.url, args.output, args.format)
            console.print("[green]✅ Audio download completed successfully![/green]")
        except Exception as e:
            console.print(f"[red]❌ Error downloading audio: {e}[/red]")

    # Handle playlist download
    elif args.command == "playlist":
        try:
            yt_play = Playlist(args.url)
            total_videos = len(yt_play.video_urls)
            console.print(f"[green]📋 Found playlist with {total_videos} videos[/green]")
            console.print(f"[blue]📁 Output directory:[/blue] {args.output}")
            console.print(f"[yellow]📋 Type:[/yellow] {args.type}")
            console.print(f"[yellow]📹 Format:[/yellow] {args.format}")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"Downloading {total_videos} {args.type}s...", total=total_videos)

                for i, video in enumerate(yt_play.videos, 1):
                    progress.update(task, description=f"Downloading {args.type} {i}/{total_videos}: {video.title[:50]}...")
                    try:
                        if args.type == "audio":
                            audio_main(video.watch_url, args.output, args.format)
                        else:
                            video_main(video.watch_url, args.output, args.format)
                        progress.update(task, advance=1)
                    except Exception as e:
                        console.print(f"[red]❌ Error downloading {video.title}: {e}[/red]")
                        progress.update(task, advance=1)

            console.print("[green]✅ Playlist download completed![/green]")

        except Exception as e:
            console.print(f"[red]❌ Error processing playlist: {e}[/red]")


if __name__ == "__main__":
    cli()
