import eel
import os
import sys
import shutil
import configparser
import traceback
import json
import time
import threading
import multiprocessing
import base64
import subprocess
import pandas as pd
import plotly.express as px
import eel.chrome, eel.edge
from models.ClipBot import ClipBot
from models.Channel import Channel

bot = None
videoThreads = {}
notification = False


def resource_path(relative_path, is_download=False):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # if running as script, uncomment this if-else block and comment the ones below
    if getattr(sys, 'frozen', False):
        print("FIrst path")
        base_path = os.path.dirname(sys.executable)
    elif __file__:
        print("second path")
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # if building as noconsole and onefile, uncomment this if-else block and comment the other blocks
    # if not is_download:
    #     base_path = os.path.join(os.path.dirname(sys.executable), "../../../")
    # else:
    #     base_path = sys._MEIPASS
    # if building as --console and --onefile uncomment this if-else block and comment the previous two
    # if is_download:
    #     base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


"""
    Set up the Bot and get everything ready
"""


@eel.expose
def init_clip_bot():
    global bot
    bot = ClipBot()
    bot.setup_config()
    bot.setup_channels()


@eel.expose
def valid_bot():
    global bot
    return True if bot.has_channels and bot.oauth_configured else False


"""
    Deal with the Twitch API credentials     
"""


@eel.expose
def check_credentials():
    cfg = configparser.ConfigParser()
    cfg.read(resource_path("config.ini"))
    if cfg:
        if cfg.has_section("settings"):
            if cfg.has_option("settings", "client_id") and cfg.has_option("settings", "secret"):
                return {"status": 200}
        else:
            return {"status": 400}
    else:
        return {"status": 200, "msg": f"CFG not found path was {resource_path('config.ini')}"}


@eel.expose
def enter_credentials(client_id, client_secret):
    cfg = configparser.ConfigParser()
    cfg["settings"] = {}
    cfg["settings"]["client_id"] = client_id
    cfg["settings"]["secret"] = client_secret
    with open(resource_path("config.ini"), "w") as config_file:
        cfg.write(config_file)


"""
    Handle a specific channel or channels
"""


@eel.expose
def add_channel(channel_id):
    try:
        cfg = configparser.RawConfigParser()
        cfg.read(resource_path("channels.ini"))
        global bot
        if bot.get_channel(int(channel_id)):
            print("Channel already exists.")
            raise Exception("Channel already exists.")
        new_channel = Channel(int(channel_id), bot.get_helix(), bot)
        bot.add_channel(new_channel)
        cfg.add_section(channel_id)
        with open(resource_path("channels.ini"), "w") as config_file:
            cfg.write(config_file)
        return ""
    except Exception as exception:
        traceback.print_exc()
        return exception.args


@eel.expose
def remove_channels(channels):
    if not os.path.exists(resource_path("channels.ini")):
        return "Config file not found."
    try:
        cfg = configparser.RawConfigParser()
        cfg.read(resource_path("channels.ini"))
        global bot
        for channel in channels:
            cfg.remove_section(channel)
            bot.remove_channel(int(channel))
        with open(resource_path("channels.ini"), "w") as config_file:
            cfg.write(config_file)
        return ""
    except Exception as exception:
        return exception.args


@eel.expose
def get_channels():
    global bot
    return bot.get_channels()


@eel.expose
def get_channel(channel_id, info=True):
    global bot
    return bot.get_channel(channel_id, info)


@eel.expose
def get_channel_emotes(channel_id):
    global bot
    return bot.get_channel(channel_id, False).get_emotes()


@eel.expose
def search_channel(channel_name):
    global bot
    return bot.search_for_channel(channel_name)


"""
    For a channel setting, deal with a category or categories
"""


@eel.expose
def get_categories(channel_id, category=None):
    global bot
    channel = bot.get_channel(channel_id, False)
    categories = [category] if category else channel.get_categories()
    result = [{"type": category.get_type(), "emotes": category.get_emotes(True)} for category in categories]
    return result


@eel.expose
def add_category(channel_id, name, emotes):
    if not os.path.exists(resource_path("channels.ini")):
        return "Can't find config file."
    try:
        name = name.lower()
        global bot
        channel = bot.get_channel(channel_id, False)
        channel.add_category(name, True, channel_id)
        channel.add_emotes_to_category(name, emotes)
        cfg = configparser.RawConfigParser()
        cfg.read(resource_path("channels.ini"))
        cfg.set(str(channel_id), name, ",".join(emotes))
        with open(resource_path("channels.ini"), "w") as config_file:
            cfg.write(config_file)
        return ""
    except Exception as exception:
        return exception.args


@eel.expose
def edit_category(channel_id, name, emotes_add, emotes_left):
    if not os.path.exists(resource_path("channels.ini")):
        return "Can't find config file."
    try:
        cfg = configparser.RawConfigParser()
        cfg.read(resource_path("channels.ini"))
        name = name.lower()
        global bot
        channel = bot.get_channel(channel_id, False)
        emotes_to_add = set(emotes_add)
        emotes_left = set(emotes_left)
        print("Emotes to Add", emotes_to_add)
        print("Emotes Left to set", emotes_left)
        channel.rmv_emotes_from_category(name, set(emotes_left))
        channel.add_emotes_to_category(name, set(emotes_add))
        cfg.set(str(channel_id), name, ",".join(list(emotes_to_add.union(emotes_left))))
        with open(resource_path("channels.ini"), "w") as config_file:
            cfg.write(config_file)
        return ""
    except Exception as exception:
        return exception.args


@eel.expose
def delete_category(channel_id, names):
    if not os.path.exists(resource_path("channels.ini")):
        return
    try:
        cfg = configparser.RawConfigParser()
        cfg.read(resource_path("channels.ini"))
        global bot
        channel = bot.get_channel(channel_id, False)
        for name in names:
            name = name.lower()
            channel.remove_category(name)
            cfg.remove_option(str(channel_id), name)
        with open(resource_path("channels.ini"), "w") as config_file:
            cfg.write(config_file)
        return ""
    except Exception as exception:
        return exception.args


@eel.expose
def get_recommended_emotes(channel_id, category_type, is_list=False):
    if os.path.exists(resource_path(f"data/channels/{channel_id}/recommendation_data.json")):
        with open(resource_path(f"data/channels/{channel_id}/recommendation_data.json")) as ifile:
            channel = get_channel(channel_id, False)
            category = category_type if is_list else channel.get_category(category_type)
            chain = json.load(ifile)
            emotes_in_category = set(category_type) if is_list else category.get_emotes(True)
            top_5_emotes = set()
            chain_indices = {emote: 0 for emote in emotes_in_category}
            emote_fully_checked = {emote: False for emote in emotes_in_category}
            done = False
            start = time.time()
            print(f"Beginning process of generating recommended emotes at {start}")
            for emote in emotes_in_category:
                chain[emote] = [(k, v / float(chain["totalEmotes"])) for k, v in
                                sorted(chain[emote].items(), key=lambda item: item[1] / chain["totalEmotes"],
                                       reverse=True)]
            while len(top_5_emotes) < 5 and not done:
                candidate_emote = None
                candidate_percentage = 0
                parent_emote = None
                for emote in emotes_in_category:
                    if all(is_checked for is_checked in emote_fully_checked.values()):
                        done = True
                        break
                    while chain_indices[emote] < len(chain[emote]) \
                            and chain[emote][chain_indices[emote]][0] in top_5_emotes:
                        chain_indices[emote] += 1
                    if chain_indices[emote] >= len(chain[emote]):
                        emote_fully_checked[emote] = True
                        continue
                    while chain[emote][chain_indices[emote]][0] in emotes_in_category:
                        chain_indices[emote] += 1
                    if chain[emote][chain_indices[emote]][1] > candidate_percentage \
                            and chain[emote][chain_indices[emote]][0] not in top_5_emotes:
                        candidate_percentage = chain[emote][chain_indices[emote]][1]
                        candidate_emote = chain[emote][chain_indices[emote]][0]
                        parent_emote = emote
                if parent_emote is not None:
                    chain_indices[parent_emote] += 1
                if candidate_emote is not None:
                    top_5_emotes.add(candidate_emote)
            end = time.time()
            print(f"Finished process of generating recommended emotes at {end}. Process took {end - start}s")
            print(top_5_emotes)
            return list(top_5_emotes)
    else:
        print("Path not found")
        return []


@eel.expose
def get_twitch_global_emotes():
    global bot
    global_emotes = bot.get_global_emotes("twitch")
    return global_emotes

@eel.expose
def get_bttv_global_emotes():
    global bot
    global_emotes = bot.get_global_emotes("bttv")
    return global_emotes


"""
    Handle a channel's videos or the user's processed/processing videos    
"""


@eel.expose
def get_videos(channel_id, videos=None):
    global bot
    channel = bot.get_channel(channel_id, False)
    return channel.get_videos(videos) if channel else []


@eel.expose
def get_user_videos(channel_id=None):
    global bot
    if channel_id:
        try:
            if os.path.exists(resource_path(f"data/channels/{channel_id}")):
                video_ids = [int(f.name) for f in os.scandir(resource_path(f"data/channels/{channel_id}")) if f.is_dir()
                             and (not bot._processing or channel_id in bot._processing
                                  and int(f.name) not in bot._processing.get(channel_id))]
                return video_ids
            else:
                print(f"Channel folder not found for id {channel_id}")
                return []
        except Exception as exception:
            print(exception.args)
            return []
    else:
        try:
            if os.path.exists(resource_path("data/channels/")):
                channel_ids = [f.name for f in os.scandir(resource_path("data/channels/")) if f.is_dir()]
                response = {}
                for channel_id in channel_ids:
                    response[channel_id] = [int(f.name) for f in os.scandir(resource_path(f"data/channels/{channel_id}"))
                                            if f.is_dir()]
                return response
            else:
                print("Channel folder not found (No ID specified).")
                return []
        except Exception as exception:
            print(exception.args)
            return []


@eel.expose
def get_processing_videos():
    global bot
    return bot.get_processing_videos()


@eel.expose
def remove_video(channel_id, video_id):
    video_id.strip()
    try:
        if os.path.exists(resource_path(f"data/channels/{channel_id}/{video_id}")):
            shutil.rmtree(resource_path(f"data/channels/{channel_id}/{video_id}"))
            return {"success": "Video was successfully deleted"}
        else:
            print("Video file not found")
            return {"error": "Video file not found"}
    except Exception as exception:
        print(exception.args)
        return {"error": exception.args}


@eel.expose
def reset_notification_count():
    global notification
    notification = False
    eel.videoHandler(notification)


"""
    Process a video
"""


@eel.expose
def clip_video(channel_id, video_id=None):
    video_thread = threading.Thread(target=clip_video_helper, args=(channel_id, video_id), daemon=True)
    video_thread.start()


def clip_video_helper(channel_id, video_id=None):
    bot.clip_video(channel_id, video_id)
    print("Finished clipping video")
    print("###########################")
    global notification
    notification = True
    response = {
        "status": 200 if notification else 400,
        "channelId": channel_id,
        "videoId": video_id,
    }
    eel.videoHandler(response)


"""
    Handle processed video results
"""


@eel.expose
def get_video_results(channel_id, video_id):
    if not video_id or not channel_id:
        return {"error": "Unable to process request"}
    global bot
    channel = bot.get_channel(channel_id, False)
    if not os.path.exists(resource_path(f"{channel._path_name}/{video_id}")):
        return {"error": "Video was not processed"}
    results = {}
    for category in channel.get_categories():
        try:
            if os.path.exists(resource_path(f"{channel._path_name}/{video_id}/data.json")):
                with open(resource_path(f"{channel._path_name}/{video_id}/data.json")) as ifile:
                    results = json.load(ifile)
            else:
                results[category.get_type()] = {}
        except Exception as exception:
            print(exception.args)
            print("Exception!")
            return {"error": "Unable to read file"}
    if os.path.exists(resource_path(f"clips/{channel_id}/{video_id}/")):
        downloaded_video_clips = []
        for category in channel.get_categories():
            if os.path.exists(resource_path(f"clips/{channel_id}/{video_id}/{category.get_type()}/")):
                clip_names = [f.name.split(".")[0] for f in
                              os.scandir(resource_path(f"clips/{channel_id}/{video_id}/{category.get_type()}/"))
                              if not f.is_dir()]
                for name in clip_names:
                    start, end = name.split("_")
                    downloaded_video_clips.append(f"{start}-{end}")
        results["downloaded"] = downloaded_video_clips
    else:
        results["downloaded"] = []
    results["downloadedVOD"] = os.path.exists(resource_path(f"vods/{video_id}.mp4"))
    return results


@eel.expose
def get_graph(graph_data):
    df = pd.DataFrame(graph_data, columns=["category", "time", "instances"])
    fig = px.scatter(df, x="time", y="instances", color="category",
                     labels=dict(time="Time (s)", instances="Category emote usage per comment", category="Category"),
                     width=450, height=350)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )
    img_bytes = fig.to_image(format="png")
    return base64.encodebytes(img_bytes).decode("utf-8").replace("\n", "")


"""
    Download a clip/vod/csv file
"""


@eel.expose
def csv_export(video_id, data):
    print(data)
    with open(resource_path(f"/web/exported/{video_id}_groups.csv"), "w") as ofile:
        for group in data:
            line = f"{group['start']},{group['end']},{group['length']},{group['similarities']}\n"
            print(line)
            ofile.write(line)
    return {"status": 200}


def invoke_twitchdl(video_id, channel_id=None, category=None, start=-1, end=0):
    try:
        print(start, end, video_id, channel_id)
        response = {"start": start, "end": end, "video_id": video_id, "channel_id": channel_id, "category": category}
        if start == -1 and end == 0:
            response["isVOD"] = True
        elif not category:
            response["isOther"] = True
        cmd = ["python3", resource_path("twitchdl/console.py", True), "download", video_id, "--overwrite", "--format", "mp4"]
        # if building using --noconsole and --onefile uncomment this next line
        # cmd.extend(["--path", f"{os.path.join(os.path.dirname(sys.executable), '../../../')}"])
        # if building using --console and --onefile uncomment this next line
        # cmd.extend(["--path", f"{os.path.dirname(sys.executable)}"])
        if channel_id is not None:
            cmd.extend(["--channel", str(channel_id)])
        if start >= 0:
            cmd.extend(["--start", str(start)])
        if end > 0:
            cmd.extend(["--end", str(end)])
        cmd.extend(["--quality", "source"])
        if category is not None:
            cmd.extend(["--category", category])
        return_val = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = return_val.stderr.decode('utf-8').strip()
        with open(resource_path('log.txt'), 'w') as log:
            log.write(output)
        if return_val.returncode != 0:
            msg = f"Download failed for clip at {start} to {end} for video {video_id}. Error: {return_val.stderr.decode('utf-8').strip()}"
            print(msg)
            response["status"] = 500
            response["msg"] = msg
        else:
            msg = f"Successfully downloaded clip at {start} to {end} for video {video_id}"
            print(msg)
            response["status"] = 200
            response["msg"] = msg
        response["type"] = "console"
        # if running as nonconsole and onefile uncomment this line
        response["type"] = "noconsole"
        print(f"download response: {response}")
    except Exception as e:
        msg = f"Download failed for clip at {start} to {end} for video {video_id} Exception msg: {str(e)}"
        print(msg)
        response["status"] = 500
        response["msg"] = msg
    eel.downloadHandler(response)


@eel.expose
def download_clip(channel_id, video_id, category, start, end):
    if end <= start:
        print("Invalid clip params.")
        return {"status": "400"}
    download_thread = threading.Thread(target=invoke_twitchdl, args=(video_id, channel_id, category, start, end),
                                       daemon=True)
    download_thread.start()


@eel.expose
def download_vod(video_id):
    download_thread = threading.Thread(target=invoke_twitchdl, args=(video_id, None, None), daemon=True)
    download_thread.start()


"""
    Check what browser to open up on start
"""


def get_preferred_mode():
    if eel.chrome.find_path():
        return 'chrome'
    if eel.edge.find_path():
        return 'edge'

    return 'default'


if __name__ == "__main__":
    multiprocessing.freeze_support()
    eel.init("web", allowed_extensions=[".js", ".html"])
    try:
        eel.start("templates/index.html", jinja_templates="templates", mode=get_preferred_mode())
    except SystemExit as e:
        print(e.code, e.args)
        pass
    except MemoryError as e:
        print(e.args)
        pass
    except KeyboardInterrupt as e:
        print(e.args)
        pass
