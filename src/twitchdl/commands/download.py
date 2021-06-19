"""
    Credits: twitch-dl by ihabunek https://github.com/ihabunek/twitch-dl
"""

import m3u8
import re
import requests
import shutil
import subprocess
import tempfile

from os import path, makedirs
from pathlib import Path
from urllib.parse import urlparse, urlencode

import src.twitchdl.twitch as twitch
import src.twitchdl.utils as utils
from src.twitchdl.download import download_files
from src.twitchdl.exceptions import ConsoleError
from src.twitchdl.output import print_out


def _parse_playlists(playlists_m3u8):
    playlists = m3u8.loads(playlists_m3u8)

    for p in playlists.playlists:
        name = p.media[0].name if p.media else ""
        resolution = "x".join(str(r) for r in p.stream_info.resolution)
        yield name, resolution, p.uri


def _get_playlist_by_name(playlists):
    _, _, uri = playlists[0]
    return uri
    msg = "Unable to retrieve playlist."
    raise ConsoleError(msg)


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


def _video_target_filename(video, channel_id, format, start, end, category):
    match = re.search(r"^(\d{4})-(\d{2})-(\d{2})T", video['publishedAt'])
    date = "".join(match.groups())

    name = "_".join([
        video['id'],
        date,
        str(start),
        str(end),
    ])
    filepath = f"clips/{channel_id}/{video['id']}/{category}/{name}.{format}"
    if not path.exists("clips/"):
        makedirs("clips/")
    if not path.exists(f"clips/{channel_id}/"):
        makedirs(f"clips/{channel_id}/")
    if not path.exists(f"clips/{channel_id}/{video['id']}/"):
        makedirs(f"clips/{channel_id}/{video['id']}/")
    if not path.exists(f"clips/{channel_id}/{video['id']}/{category}/"):
        makedirs(f"clips/{channel_id}/{video['id']}/{category}/")
    return filepath


def _get_vod_paths(playlist, start, end):
    """Extract unique VOD paths for download from playlist."""
    files = []
    vod_start = 0
    for segment in playlist.segments:
        vod_end = vod_start + segment.duration

        # `vod_end > start` is used here because it's better to download a bit
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
    playlist_uri = (_get_playlist_by_name(playlists))

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
    target = _video_target_filename(video, args.channel, args.format, args.start, args.end, args.category)
    _join_vods(playlist_path, target, args.overwrite)

    if args.keep:
        print_out("\n<dim>Temporary files not deleted: {}</dim>".format(target_dir))
    else:
        print_out("\n<dim>Deleting temporary files...</dim>")
        shutil.rmtree(target_dir)

    print_out("\nDownloaded: <green>{}</green>".format(target))