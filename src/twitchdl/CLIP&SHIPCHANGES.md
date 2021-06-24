Clip & Ship Change List
=======================

## Root directory
- Deleted the following directories and their contents: `tests/`
- Deleted the following files and their contents: `.flake8` `.gitignore`, `Makefile`, `requirements-dev.txt`, 
  `setup.py`, `stdeb.cfg`, `twitch-dl-1.scd`
## twitchdl directory
- Deleted `commands/` directory and the following files within: `__init__.py`, `clips.py`, `info.py`, `videos.py`
- Moved `commands/download.py` up one directory (to `twitchdl/`), renamed to `command.py` 
- Deleted the following files: `__main__.py`
- Modified `command.py` with the following changes:
  - add a function `resource_path` to get the full path of a given relative path
  - modify `_get_playlist_by_name` to not have a `quality` param, remove `quality` checks and set the `uri` var to 
    `playlist[0]` only
  - delete `_select_playlist_interactive`
  - modify `_video_target_filename` to have additional params: `channel_id`, `category`, `start=None`, 
    `end=None`. Create a `parts` var initially set to `[]` and is `start` and `end`, append them to `parts`,
    otherwise append `video['id']`. Set `name` var to `" ".join(parts)`.
    `resource_path(path)` will be abbreviated to `rs(path)`. If `start` and `end`: if `rs("clips.")` doesn't
    exist, create it, if `rs("clips/{channel_id}")` doesn't exist, create it, if `rs("clips/{channel_id}/{video['id']}")` 
    doesn't exist, create it. If `category`, set a `filepath` var to `rs("clips/{channel_id}/{video['id']}/{category}/{name}.{format}"`
    and if `rs(f"clips/{channel_id}/{video['id']}/{category}/")` doesn't exist create it. Otherwise, set `filepath` to
    `rs("clips/{channel_id}/{video['id']}/other_clips/{name}.{format}")` and if `rs(f"clips/{channel_id}/{video['id']}/other_clips/")`
    doesn't exist, create it. If not `start` and `end`: create `rs("vods/")` directory if it doesn't exist and set
    `filepath` to `rs(f"vods/{name}.{format}")`. Return `filepath`
  - rename `download` to `download_video` and don't create or check `clip_slug`
  - delete `_get_clip_url`, `get_clip_authenticated_url`, `_download_clip`
  
- Modified `console.py` with the following changes:
  - import `argparse` entirely
  - remove `collections` imports
  - delete `Command` namedtuple template
  - delete `time` and `limit` functions
  - delete `COMMAND` list and extract the `download` command into a dictionary named `download_cmd`. 
  - modify `download_cmd` and add `--category`, `--channel`, `--start`, `--end` flags (`int`, `int`, `str`, `str` types.
  modify `get_parser` to not have the loop going over `COMMANDS` and to go over a `tuple` instead of a `namedtuple`. Add
    check to run the `main` function if running as a script.
    
- Modified `output.py` with teh following changes:
  - delete `print_clip` and `print_clip_urls` functions
  
- Modified `twitch.py` with the following changes:
  - delete import for `CLIENT_ID` and set it in the file
  - import `exceptions` entirely
  - delete `authenticated_get`, `kraken_get`, `gql_post`, `get_video_legacy`, `get_clip`, `get_clip_access_token`,
  `get_channel_clips`, `channel_clips_generator`, `get_channel_videos`, `channel_videos_generator`, and `get_game_id` 
    function