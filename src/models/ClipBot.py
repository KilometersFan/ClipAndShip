import configparser
import twitch
import requests
import json
import shutil
import os
from multiprocessing import Process, Manager
from .Channel import Channel
from .Category import Category
from .ClipBotHelper import ClipBotHelper
from .util import resource_path


class ClipBot:
    """
        Bot that handles connecting to Twitch API, configuring/modifying channels and categories,
        and retrieving/processing videos.

    """

    def __init__(self):
        self._oauth_url = "https://id.twitch.tv/oauth2/"
        self._channels = {}
        self._helix = None
        self.oauth_configured = False
        self.has_channels = False
        self._channel_info = {}
        self._processing = {}
        self._comment_processing = {}
        self._helpers = {}
        self._access_token = None
        self._client_id = None
        self.MAX_RETRIES = 5

    # return twitch Helix object
    def get_helix(self):
        return self._helix

    # set up helix and twitch related stuff
    def setup_config(self, refresh=False):
        cfg = configparser.ConfigParser()
        cfg.read(resource_path("config.ini"))
        settings = cfg["settings"]
        client_id = settings["client_id"]
        secret = settings["secret"]
        if not client_id or not secret:
            print("Unable to find credentials")
        else:
            self._client_id = client_id
            try:
                if refresh:
                    authorize_request = requests.post(self._oauth_url + "token",
                                                      params={"client_id": client_id, "client_secret": secret,
                                                              "grant_type": "client_credentials"}, timeout=2)
                else:
                    authorize_request = requests.post(self._oauth_url + "token",
                                                      params={"client_id": client_id, "client_secret": secret,
                                                              "grant_type": "client_credentials"})
                if authorize_request.status_code == requests.codes.ok:
                    response = json.loads(authorize_request.text)
                    self._access_token = response["access_token"]
                    self._helix = twitch.Helix(client_id, secret, True, None, True, self._access_token)
                    self.oauth_configured = True
                else:
                    print("Unable to complete post request for token")
            except requests.exceptions.Timeout:
                print("Request for refresh token timed out")

    # refresh access token when needed
    def refresh_token(self):
        cfg = configparser.ConfigParser()
        cfg.read(resource_path("config.ini"))
        settings = cfg["settings"]
        client_id = settings["client_id"]
        secret = settings["secret"]
        if not client_id or not secret:
            print("Unable to find credentials")
        else:
            try:
                authorize_request = requests.post(self._oauth_url + "token",
                                                  params={"client_id": client_id, "client_secret": secret,
                                                          "grant_type": "client_credentials"}, timeout=2)
                if authorize_request.status_code == requests.codes.ok:
                    response = json.loads(authorize_request.text)
                    self._access_token = response["access_token"]
                    self._helix = twitch.Helix(client_id, secret, True, None, True, self._access_token)
                else:
                    print("Unable to complete post request for token")
            except requests.exceptions.Timeout:
                print("Request for refresh token timed out")

    # read from channls.ini all the info from user's channels
    def setup_channels(self):
        cfg = configparser.ConfigParser()
        cfg.read(resource_path("channels.ini"))
        for section in cfg.sections():
            valid_token = False
            while not valid_token:
                try:
                    channel = Channel(int(section), self._helix, self)
                    for option in cfg.options(section):
                        category = Category(option, section)
                        emote_list = cfg[section][option].split(",")
                        for emote in emote_list:
                            category.add_emote(emote)
                        channel.add_category(category)
                    self.add_channel(channel)
                    valid_token = True
                except requests.exceptions.HTTPError as http_err:
                    status_code = http_err.response.status_code
                    if status_code == 401:
                        print("401 Unauthorized error, refreshing access token")
                        self.refresh_token()
                    else:
                        print("Other error received:", status_code)
                        break
        self.has_channels = True

    # add channel to user list
    def add_channel(self, channel):
        channel.populate_emotes()
        self._channels[channel.get_id()] = channel
        self._channel_info[channel.get_id()] = {
            "name": channel.get_name(),
            "id": channel.get_id(),
            "desc": channel.get_desc(),
            "imgUrl": channel.get_img(),
            "emoteMap": channel.get_emotes_map(),
            "categories": [category.get_type() for category in channel.get_categories()],
        }

    # remove channel from user's list
    def remove_channel(self, channel_id):
        if self._channels.get(channel_id, None):
            del self._channels[channel_id]
            if os.path.exists(resource_path(f"data/channels/{channel_id}")):
                shutil.rmtree(resource_path(f"data/channels/{channel_id}"))
        else:
            print("Channel doesn't exist.")
            raise Exception("Channel doesn't exist.")
        if channel_id in self._channel_info:
            del self._channel_info[channel_id]
        else:
            print("Channel doesn't exist.")
            raise Exception("Channel doesn't exist.")

    # return all channels
    def get_channels(self):
        return list(self._channel_info.values())

    # return a specific channel, either the Channel object or just dictionary with info
    def get_channel(self, channel_id, info=True):
        if info:
            return self._channel_info.get(channel_id, None)
        else:
            return self._channels.get(channel_id, None)

    def update_channel_info(self, channel_id, data):
        self._channel_info[channel_id] = data

    # search twitch for channel
    def search_for_channel(self, channel_name):
        found = False
        num_retries = 0
        while not found:
            if num_retries >= self.MAX_RETRIES:
                print("Unable to connect to Twitch API. Quitting...")
                return {"status", 500}
            try:
                if self._helix:
                    user = self._helix.user(channel_name)
                    found = True
                    if user:
                        return {"status": 200, "id": user.id, "displayName": user.display_name,
                                "desc": user.description, "imgURL": user.profile_image_url}
                    else:
                        return {"status", 404}
                else:
                    print("Helix creation failed")
                    self.setup_config()
                    num_retries += 1
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    self.setup_config()
                    num_retries += 1
            except Exception:
                return {"status", 404}

    def get_global_emotes(self, source):
        success = False
        emotes = []
        emotes_map = {}
        headers = {"Authorization": f"Bearer {self._access_token}",
                   "Client-Id": self._client_id}
        bttv_image_url = "https://cdn.betterttv.net/emote/"
        if source == "twitch":
            global_url = "https://api.twitch.tv/helix/chat/emotes/global"
        elif source == "bttv":
            global_url = "https://api.betterttv.net/3/cached/emotes/global"
        elif source == "7tv":
            global_url = "https://api.7tv.app/v2/emotes/global"
        num_retries = 0
        while not success:
            if num_retries >= self.MAX_RETRIES:
                print(f"Unable to connect to {global_url}. Quitting...")
                break
            try:
                get_global_emotes = requests.get(global_url, headers=headers, timeout=1)
                if get_global_emotes.status_code == requests.codes.ok:
                    global_emotes = json.loads(get_global_emotes.text)
                    if source == "twitch":
                        for twitch_global_emote in global_emotes["data"]:
                            emotes.append({"name": twitch_global_emote["name"],
                                          "imageUrl": twitch_global_emote["images"]["url_1x"]})
                            emotes_map[twitch_global_emote["name"].lower()] = twitch_global_emote["name"]
                    elif source == "bttv":
                        for bttv_global_emote in global_emotes:
                            emotes.append({"name": bttv_global_emote["code"],
                                           "imageUrl": bttv_image_url + bttv_global_emote["id"] + "/1x"})
                            emotes_map[bttv_global_emote["code"].lower()] = bttv_global_emote["code"]
                    elif source == "7tv":
                        for _7tv_global_emote in global_emotes:
                            emotes.append({"name": _7tv_global_emote["name"],
                                           "imageUrl": _7tv_global_emote["urls"][0][1]})
                            emotes_map[_7tv_global_emote["name"].lower()] = _7tv_global_emote["name"]
                    success = True
                else:
                    print("Unable to complete get request for Twitch Sub Emotes")
                    print("Error code:", global_emotes.status_code)
                    num_retries += 1
            except requests.exceptions.Timeout as e:
                print(f"{source} Global Emotes Request timed out")
                print(e.args)
                num_retries += 1
        if emotes:
            emotes = sorted(emotes, key=lambda emote: emote["name"])
        return {"emotes": emotes, "emoteMap": emotes_map}

    # run clip video function for channel in a new process
    def clip_video(self, channel_id, video_id):
        num_retries = 0
        success = False
        while not success:
            if num_retries >= self.MAX_RETRIES:
                print(f"Unable to connect to Twitch API. Quitting...")
                break
            if self._helix:
                channel = self._channels[channel_id]
                print(f"Channel id: {channel_id}")
                print(f"Starting video processing of video {video_id} for {channel.get_name()}")
                helper = ClipBotHelper(channel, self)

                if channel_id not in self._processing:
                    self._processing[channel_id] = set()
                self._processing[channel_id].add(video_id)
                if channel_id not in self._helpers:
                    self._helpers[channel_id] = {video_id: helper}
                else:
                    self._helpers[channel_id][video_id] = helper
                print("Added", video_id, "to set of videos owned by", channel_id)
                success = True
                manager = Manager()
                response = manager.dict()
                p = Process(target=helper.process_video, args=(response, video_id))
                p.start()
                p.join()
                print("&&&&&&&&&&&&&&&&&&&&&&&&&")
                self._processing[channel_id].remove(video_id)
            else:
                print("Helix creation failed. Trying again...")
                self.setup_config()
                num_retries += 1

    # return all videos that are currently processing
    def get_processing_videos(self):
        results = []
        for key, value in self._processing.items():
            channel = self.get_channel(key, False)
            if len(list(value)) > 0:
                print(f"Getting videos and processing")
                results += channel.get_videos(list(value), processing_check=True)
        return results
