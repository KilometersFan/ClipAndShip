"""
    Credits: twitch-dl by ihabunek https://github.com/ihabunek/twitch-dl
"""

import m3u8
import re
import requests
import shutil
import subprocess
import tempfile
import sys
from os import path, makedirs
from pathlib import Path
from urllib.parse import urlparse, urlencode

import twitch
import utils
import download
import exceptions
import output


def resource_path(relative_path, file_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # for onedir
    if getattr(sys, 'frozen', False):
        base_path = path.dirname(sys.executable)
        base_path = path.join(base_path, "..")
    elif __file__:
        base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        base_path = path.join(base_path, "..")
    if file_path:
        print(f"FILE PATH SET: {file_path}")
        base_path = file_path

    return path.join(base_path, relative_path)


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


def _join_vods(playlist_path, target, overwrite, file_path):
    command = [
        "ffmpeg",
        # if building with --noconsole and --onefile uncomment this line and comment the previous line
        # resource_path("ffmpeg", file_path=file_path),
        "-i", playlist_path,
        "-c", "copy",
        target,
        "-stats",
        "-loglevel", "warning",
    ]

    if overwrite:
        command.append("-y")

    output.print_out("<dim>{}</dim>".format(" ".join(command)))
    result = subprocess.run(command)
    if result.returncode != 0:
        raise exceptions.ConsoleError("Joining files failed")


def _video_target_filename(video, channel_id, format, category, file_path, start=None, end=None):
    parts = []
    if start and end:
        parts.extend([str(start), str(end)])
    else:
        parts.append(video['id'])
    name = "_".join(parts)
    if start and end:
        if not path.exists(resource_path("clips/", file_path=file_path)):
            makedirs(resource_path("clips/", file_path=file_path))
        if not path.exists(resource_path(f"clips/{channel_id}/", file_path=file_path)):
            makedirs(resource_path(f"clips/{channel_id}/", file_path=file_path))
        if not path.exists(resource_path(f"clips/{channel_id}/{video['id']}/", file_path=file_path)):
            makedirs(resource_path(f"clips/{channel_id}/{video['id']}/", file_path=file_path))
        if category is not None:
            filepath = resource_path(f"clips/{channel_id}/{video['id']}/{category}/{name}.{format}", file_path=file_path)
            if not path.exists(resource_path(f"clips/{channel_id}/{video['id']}/{category}/", file_path=file_path)):
                makedirs(resource_path(f"clips/{channel_id}/{video['id']}/{category}/", file_path=file_path))
        else:
            filepath = resource_path(f"clips/{channel_id}/{video['id']}/other_clips/{name}.{format}", file_path=file_path)
            if not path.exists(resource_path(f"clips/{channel_id}/{video['id']}/other_clips/", file_path=file_path)):
                makedirs(resource_path(f"clips/{channel_id}/{video['id']}/other_clips/", file_path=file_path))
    else:
        if not path.exists(resource_path("vods/", file_path=file_path)):
            makedirs(resource_path("vods/", file_path=file_path))
        filepath = resource_path(f"vods/{name}.{format}", file_path=file_path)
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


def download_video(args):
    video_id = utils.parse_video_identifier(args.video)
    if video_id:
        return _download_video(video_id, args)

    raise exceptions.ConsoleError("Invalid input: {}".format(args.video))


def _download_video(video_id, args):
    if args.start and args.end and args.end <= args.start:
        raise exceptions.ConsoleError("End time must be greater than start time")

    output.print_out("<dim>Looking up video...</dim>")
    video = twitch.get_video(video_id)

    output.print_out("Found: <blue>{}</blue> by <yellow>{}</yellow>".format(
        video['title'], video['creator']['displayName']))

    output.print_out("<dim>Fetching access token...</dim>")
    access_token = twitch.get_access_token(video_id)

    output.print_out("<dim>Fetching playlists...</dim>")
    playlists_m3u8 = twitch.get_playlists(video_id, access_token)
    playlists = list(_parse_playlists(playlists_m3u8))
    playlist_uri = (_get_playlist_by_name(playlists))

    output.print_out("<dim>Fetching playlist...</dim>")
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

    output.print_out("\nDownloading {} VODs using {} workers to {}".format(
        len(vod_paths), args.max_workers, target_dir))
    path_map = download.download_files(base_uri, target_dir, vod_paths, args.max_workers)

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
        output.print_out("\n\n<dim>Skipping joining files...</dim>")
        output.print_out("VODs downloaded to:\n<blue>{}</blue>".format(target_dir))
        return

    output.print_out("\n\nJoining files...")
    target = _video_target_filename(video, args.channel, args.format, args.category, args.path, args.start, args.end)
    _join_vods(playlist_path, target, args.overwrite, args.path)

    if args.keep:
        output.print_out("\n<dim>Temporary files not deleted: {}</dim>".format(target_dir))
    else:
        output.print_out("\n<dim>Deleting temporary files...</dim>")
        shutil.rmtree(target_dir)

    output.print_out("\nDownloaded: <green>{}</green>".format(target))