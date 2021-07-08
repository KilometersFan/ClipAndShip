# -*- coding: utf-8 -*-

import sys

import argparse

import command
import exceptions
import output
import twitch


CLIENT_WEBSITE = 'https://github.com/ihabunek/twitch-dl'


download_cmd = (
    "download",
    "Download a video",
    [
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
            "type": int,
            "default": None,
        }),
        (["-e", "--end"], {
            "help": "Download video up to this time (hh:mm or hh:mm:ss)",
            "type": int,
            "default": None,
        }),
        (["-ch", "--channel"], {
            "help": "channel ID",
            "type": str,
        }),
        (["-c", "--category"], {
            "help": "category type",
            "type": str,
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
        }),
        (["--path"], {
            "help": "Path for clips/vods",
            "type": str,
            "default": "",
        })
    ]
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

    parser = argparse.ArgumentParser(prog='twitch-dl', description=description, epilog=CLIENT_WEBSITE)
    subparsers = parser.add_subparsers(title="commands")

    sub = subparsers.add_parser(download_cmd[0], help=download_cmd[1])

    # Set the function to call to the function of same name in the "commands" package
    sub.set_defaults(func=command.download_video)
    for args, kwargs in download_cmd[2] + COMMON_ARGUMENTS:
        sub.add_argument(*args, **kwargs)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if "func" not in args:
        parser.print_help()
        return

    try:
        args.func(args)
    except exceptions.ConsoleError as e:
        output.print_err(e)
        sys.exit(1)
    except KeyboardInterrupt:
        output.print_err("Operation canceled")
        sys.exit(1)
    except twitch.GQLError as e:
        output.print_err(e)
        for err in e.errors:
            output.print_err("*", err["message"])
        sys.exit(1)


if __name__ == "__main__":
    main()
