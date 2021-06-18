import m3u8
import re
import requests
import shutil
import subprocess
import tempfile

from os import path
from pathlib import Path
from urllib.parse import urlparse, urlencode
from argparse import ArgumentParser, ArgumentTypeError
from collections import namedtuple

import src.vod_downloads.twitch as twitch
import src.vod_downloads.utils as utils
from src.vod_downloads.download import download_files
from src.vod_downloads.exceptions import ConsoleError
from src.vod_downloads.output import print_out
import __init__


def _parse_playlists(playlists_m3u8):
    playlists = m3u8.loads(playlists_m3u8)

    for p in playlists.playlists:
        name = p.media[0].name if p.media else ""
        resolution = "x".join(str(r) for r in p.stream_info.resolution)
        yield name, resolution, p.uri


def _get_playlist_by_name(playlists, quality):
    if quality == "source":
        _, _, uri = playlists[0]
        return uri

    for name, _, uri in playlists:
        if name == quality:
            return uri

    available = ", ".join([name for (name, _, _) in playlists])
    msg = "Quality '{}' not found. Available qualities are: {}".format(quality, available)
    raise ConsoleError(msg)


def _select_playlist_interactive(playlists):
    print_out("\nAvailable qualities:")
    for n, (name, resolution, uri) in enumerate(playlists):
        print_out("{}) {} [{}]".format(n + 1, name, resolution))

    no = utils.read_int("Choose quality", min=1, max=len(playlists) + 1, default=1)
    _, _, uri = playlists[no - 1]
    return uri


def _join_vods(playlist_path, target, overwrite):
    command = [
        "ffmpeg",
        "-i", playlist_path,
        "-c", "copy",
        target,
        "-stats",
        "-loglevel", "warning",
    ]

    if overwrite:
        command.append("-y")

    print_out("<dim>{}</dim>".format(" ".join(command)))
    result = subprocess.run(command)
    if result.returncode != 0:
        raise ConsoleError("Joining files failed")


def _video_target_filename(video, format):
    match = re.search(r"^(\d{4})-(\d{2})-(\d{2})T", video['publishedAt'])
    date = "".join(match.groups())

    name = "_".join([
        date,
        video['id'],
        video['creator']['login'],
        utils.slugify(video['title']),
    ])

    return name + "." + format


def _get_vod_paths(playlist, start, end):
    """Extract unique VOD paths for download from playlist."""
    files = []
    vod_start = 0
    for segment in playlist.segments:
        vod_end = vod_start + segment.duration

        # `vod_end > start` is used here becuase it's better to download a bit
        # more than a bit less, similar for the end condition
        start_condition = not start or vod_end > start
        end_condition = not end or vod_start < end

        if start_condition and end_condition and segment.uri not in files:
            files.append(segment.uri)

        vod_start = vod_end

    return files


def _create_temp_dir(base_uri):
    """Create a temp dir to store downloads if it doesn't exist."""
    path = urlparse(base_uri).path.lstrip("/")
    temp_dir = Path(tempfile.gettempdir(), "twitch-dl", path)
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def download(args):
    video_id = utils.parse_video_identifier(args.video)
    if video_id:
        return _download_video(video_id, args)

    raise ConsoleError("Invalid input: {}".format(args.video))


def _download_video(video_id, args):
    if args.start and args.end and args.end <= args.start:
        raise ConsoleError("End time must be greater than start time")

    print_out("<dim>Looking up video...</dim>")
    video = twitch.get_video(video_id)

    print_out("Found: <blue>{}</blue> by <yellow>{}</yellow>".format(
        video['title'], video['creator']['displayName']))

    print_out("<dim>Fetching access token...</dim>")
    access_token = twitch.get_access_token(video_id)

    print_out("<dim>Fetching playlists...</dim>")
    playlists_m3u8 = twitch.get_playlists(video_id, access_token)
    playlists = list(_parse_playlists(playlists_m3u8))
    playlist_uri = (_get_playlist_by_name(playlists, args.quality) if args.quality
            else _select_playlist_interactive(playlists))

    print_out("<dim>Fetching playlist...</dim>")
    response = requests.get(playlist_uri)
    response.raise_for_status()
    playlist = m3u8.loads(response.text)

    base_uri = re.sub("/[^/]+$", "/", playlist_uri)
    target_dir = _create_temp_dir(base_uri)
    vod_paths = _get_vod_paths(playlist, args.start, args.end)

    # Save playlists for debugging purposes
    with open(path.join(target_dir, "playlists.m3u8"), "w") as f:
        f.write(playlists_m3u8)
    with open(path.join(target_dir, "playlist.m3u8"), "w") as f:
        f.write(response.text)

    print_out("\nDownloading {} VODs using {} workers to {}".format(
        len(vod_paths), args.max_workers, target_dir))
    path_map = download_files(base_uri, target_dir, vod_paths, args.max_workers)

    # Make a modified playlist which references downloaded VODs
    # Keep only the downloaded segments and skip the rest
    org_segments = playlist.segments.copy()
    playlist.segments.clear()
    for segment in org_segments:
        if segment.uri in path_map:
            segment.uri = path_map[segment.uri]
            playlist.segments.append(segment)

    playlist_path = path.join(target_dir, "playlist_downloaded.m3u8")
    playlist.dump(playlist_path)

    if args.no_join:
        print_out("\n\n<dim>Skipping joining files...</dim>")
        print_out("VODs downloaded to:\n<blue>{}</blue>".format(target_dir))
        return

    print_out("\n\nJoining files...")
    target = _video_target_filename(video, args.format)
    _join_vods(playlist_path, target, args.overwrite)

    if args.keep:
        print_out("\n<dim>Temporary files not deleted: {}</dim>".format(target_dir))
    else:
        print_out("\n<dim>Deleting temporary files...</dim>")
        shutil.rmtree(target_dir)

    print_out("\nDownloaded: <green>{}</green>".format(target))


def time(value):
    """Parse a time string (hh:mm or hh:mm:ss) to number of seconds."""
    parts = [int(p) for p in value.split(":")]

    if not 2 <= len(parts) <= 3:
        raise ArgumentTypeError()

    hours = parts[0]
    minutes = parts[1]
    seconds = parts[2] if len(parts) > 2 else 0

    if hours < 0 or not (0 <= minutes <= 59) or not (0 <= seconds <= 59):
        raise ArgumentTypeError()

    return hours * 3600 + minutes * 60 + seconds


Command = namedtuple("Command", ["name", "description", "arguments"])
download_command = Command(
    name="download",
    description="Download a video",
    arguments=[
        (["video"], {
            "help": "video ID, clip slug, or URL",
            "type": str,
        }),
        (["-w", "--max-workers"], {
            "help": "maximal number of threads for downloading vods "
                    "concurrently (default 20)",
            "type": int,
            "default": 20,
        }),
        (["-s", "--start"], {
            "help": "Download video from this time (hh:mm or hh:mm:ss)",
            "type": time,
            "default": None,
        }),
        (["-e", "--end"], {
            "help": "Download video up to this time (hh:mm or hh:mm:ss)",
            "type": time,
            "default": None,
        }),
        (["-f", "--format"], {
            "help": "Video format to convert into, passed to ffmpeg as the "
                    "target file extension (default: mkv)",
            "type": str,
            "default": "mkv",
        }),
        (["-k", "--keep"], {
            "help": "Don't delete downloaded VODs and playlists after merging.",
            "action": "store_true",
            "default": False,
        }),
        (["-q", "--quality"], {
            "help": "Video quality, e.g. 720p. Set to 'source' to get best quality.",
            "type": str,
        }),
        (["--no-join"], {
            "help": "Don't run ffmpeg to join the downloaded vods, implies --keep.",
            "action": "store_true",
            "default": False,
        }),
        (["--overwrite"], {
            "help": "Overwrite the target file if it already exists without prompting.",
            "action": "store_true",
            "default": False,
        })
    ],
)

COMMON_ARGUMENTS = [
    (["--debug"], {
        "help": "show debug log in console",
        "action": 'store_true',
        "default": False,
    }),
    (["--no-color"], {
        "help": "disable ANSI colors in output",
        "action": 'store_true',
        "default": False,
    })
]

def get_parser():
    description = "A script for downloading videos from Twitch"

    parser = ArgumentParser(prog='twitch-dl', description=description)

    subparsers = parser.add_subparsers(title="commands")

    sub = subparsers.add_parser(download_command.name, help=download_command.description)

    # Set the function to call to the function of same name in the "commands" package
    sub.set_defaults(func=__init__.__dict__.get(download_command.name))

    for args, kwargs in download_command.arguments + COMMON_ARGUMENTS:
        sub.add_argument(*args, **kwargs)

    return parser

if __name__ == "__main__":
    video_id = 1039864717
    print(f"Starting download process for {video_id}")
    parser = get_parser()
    args = parser.parse_args()
    print(args)
    download(args)