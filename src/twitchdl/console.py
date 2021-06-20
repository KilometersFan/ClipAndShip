# -*- coding: utf-8 -*-

import sys

from argparse import ArgumentParser, ArgumentTypeError
from collections import namedtuple

from exceptions import ConsoleError
from src.twitchdl.output import print_err
from src.twitchdl.twitch import GQLError
import commands


Command = namedtuple("Command", ["name", "description", "arguments"])

CLIENT_WEBSITE = 'https://github.com/ihabunek/twitch-dl'

COMMANDS = [
    Command(
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
            })
        ],
    ),
]

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

    parser = ArgumentParser(prog='twitch-dl', description=description, epilog=CLIENT_WEBSITE)
    subparsers = parser.add_subparsers(title="commands")

    for command in COMMANDS:
        sub = subparsers.add_parser(command.name, help=command.description)

        # Set the function to call to the function of same name in the "commands" package
        sub.set_defaults(func=commands.__dict__.get(command.name))
        for args, kwargs in command.arguments + COMMON_ARGUMENTS:
            sub.add_argument(*args, **kwargs)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    print(args)
    if "func" not in args:
        parser.print_help()
        return

    try:
        args.func(args)
    except ConsoleError as e:
        print_err(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print_err("Operation canceled")
        sys.exit(1)
    except GQLError as e:
        print_err(e)
        for err in e.errors:
            print_err("*", err["message"])
        sys.exit(1)


if __name__ == "__main__":
    main()
