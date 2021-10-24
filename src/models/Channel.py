import requests
import json
import re
import os
from datetime import datetime
from dateutil import tz
from pprint import pprint
from .Category import Category
from .util import resource_path


class Channel(object):
    """Twitch channel, stores categories set by channel"""
    def __init__(self, channel_id: int, helix, clip_bot):
        self._id = channel_id
        self._name = ""
        self._path_name = ""
        self._desc = ""
        self._img = ""
        self._helix = helix
        self._categories = {}
        self._emotes = set()
        self._ffz_emotes = []
        self._bttv_emotes = []
        self._twitch_emotes = []
        self._7tv_emotes = []
        self._name_to_emotes_map = {}
        self._bttv_url = "https://api.betterttv.net/3/cached/users/twitch/"
        self._bttv_img_url = "https://cdn.betterttv.net/emote/"
        self._twitch_sub_url = "https://api.twitch.tv/helix/chat/emotes?broadcaster_id="
        self._franker_face_z_url = "https://api.frankerfacez.com/v1/room/"
        self._7tv_url = "https://api.7tv.app/v2/users/"
        self._clip_bot = clip_bot
        self._is_setup = False
        valid_helix = False
        # reset helix if access token is invalid
        num_retries = 0
        while not valid_helix:
            if num_retries >= clip_bot.MAX_RETRIES:
                print("Unable to connect to Twitch API. Quitting...")
                break
            try:
                if helix is not None:
                    self._name = helix.user(channel_id).display_name
                    self._path_name = f"data/channels/{self._id}"
                    self._desc = helix.user(channel_id).description
                    self._img = helix.user(channel_id).profile_image_url
                    self._franker_face_z_url += self._name.lower()
                    self._7tv_url += f"{self._id}/emotes"
                    valid_helix = True
                else:
                    print("Helix doesn't exist")
                    num_retries += 1
                    clip_bot.setup_config()
                    self._helix = clip_bot.get_helix()
            except requests.exceptions.HTTPError as http_err:
                status_code = http_err.response.status_code
                if status_code == 401:
                    print("401 Unauthorized error, refreshing access token. Videos")
                    clip_bot.refresh_token()
                    helix = clip_bot.get_helix()
                    print("Finished")
                else:
                    print("Other error received:", status_code)
                num_retries += 1
        self._is_setup = True

    # add emote to channel
    def add_emote(self, emote):
        self._emotes.add(emote.lower())

    # return all emotes in channel
    def get_emotes(self):
        ff_emotes = sorted(list(self._ffz_emotes), key=lambda e: e['name'].lower())
        bttv_emotes = sorted(list(self._bttv_emotes), key=lambda e: e['name'].lower())
        twitch_emotes = sorted(list(self._twitch_emotes), key=lambda e: e['name'].lower())
        _7tv_emotes = sorted(list(self._7tv_emotes), key=lambda e: e['name'].lower())
        return {"ffEmotes": ff_emotes, "bttvEmotes": bttv_emotes,
                "twitchEmotes": twitch_emotes, '7tvEmotes': _7tv_emotes}

    # get emotes as a dictionary { name: url }
    def get_emotes_map(self):
        return self._name_to_emotes_map

    # get all emotes as a list [ name ]
    def get_emote_names(self):
        emote_types = ["ffEmotes", "bttvEmotes", "twitchEmotes"]
        channel_emote_list = set()
        for emoteType in emote_types:
            for emote in self.get_emotes()[emoteType]:
                channel_emote_list.add(emote["name"].lower())
        for category in self.get_categories():
            for emote in category.get_emotes():
                channel_emote_list.add(emote)
        return channel_emote_list

    # add category to channel
    def add_category(self, category, is_string=False, channel_id=None):
        # A category is being added by the user trhough the UI
        if is_string:
            if category not in self._categories:
                self._categories[category] = Category(category, channel_id)
                old_channel_info = self._clip_bot.get_channel(self._id)
                old_channel_info["categories"].append(category)
                self._clip_bot.update_channel_info(self._id, old_channel_info)
            else:
                print("Type {} already exists!".format(category))
                raise Exception("Category type is a duplicate.")
        # A category is being added during app initialization
        else:
            if category.get_type() not in self._categories:
                self._categories[category.get_type()] = category
            else:
                print("Type {} already exists!".format(category.get_type()))
                raise Exception("Category type is a duplicate.")
    
    # remove category from channel
    def remove_category(self, name):
        if name in self._categories:
            del self._categories[name]
            old_channel_info = self._clip_bot.get_channel(self._id)
            try:
                old_channel_info["categories"].remove(name)
                self._clip_bot.update_channel_info(self._id, old_channel_info)
            except ValueError:
                print(f"{name} is not in channel info. Cannot remove.")
        else:
            print("Type {} does not exist!".format(name))
            raise Exception("Category type does not exist.")
    
    # remove all categories
    def clear_categories(self):
        self._categories.clear()

    # return all categories
    def get_categories(self):
        categories = sorted(list(self._categories.values()), key=lambda c: c.get_type())
        return categories

    # return category object based on type
    def get_category(self, name):
        if name in self._categories:
            return self._categories[name]
        return None

    # add emotes in param to category specified by type
    def add_emotes_to_category(self, name, emotes):
        category = self._categories[name]
        if category:
            for emote in emotes:
                category.add_emote(emote.lower())
        else:
            print("Invalid category specified")
    
    # remove all emotes in param from category specified by type
    def rmv_emotes_from_category(self, name, emotes):
        category = self.get_category(name)
        emotes = set([emote.lower() for emote in emotes])
        if category:
            category.set_emotes(emotes)
        else:
            print("Invalid category specified")

    # return channel name
    def get_name(self):
        return self._name

    # return Twitch channel id
    def get_id(self):
        return self._id

    # return channel image
    def get_img(self):
        return self._img

    # return channel description
    def get_desc(self):
        return self._desc

    # return channel videos
    def get_videos(self, videos=None, processing_check=False):
        data = []
        valid_helix = False
        num_retries = 0
        while not valid_helix:
            if not videos:
                if self._helix is not None:
                    if num_retries >= self._clip_bot.MAX_RETRIES:
                        print("Unable to connect to Twitch API. Quitting...")
                        break
                    try:
                        for video in self._helix.user(self._name).videos():
                            thumbnail = video.thumbnail_url
                            if not thumbnail:
                                thumbnail = os.path.normpath("../video_image_placeholder.png")
                            else:
                                thumbnail = re.sub(r"%{.*?}", "300", thumbnail)
                            d = video.created_at
                            date = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
                            to_zone = tz.tzlocal()
                            date = date.astimezone(to_zone)
                            date = date.strftime("%Y-%m-%d")
                            clipped = os.path.exists(resource_path(f"{self._path_name}/{video.id}"))
                            processing_videos = self._clip_bot._processing.get(self.get_id(), None)
                            if processing_videos and (str(video.id) in processing_videos or int(video.id) in processing_videos):
                                is_processing = True
                            else:
                                is_processing = False
                            if processing_check == is_processing:
                                data.append({"id": video.id, "title": video.title, "date": date, "desc": video.description,
                                             "thumbnail": thumbnail, "url": video.url, "clipped": clipped,
                                             "channelId": self.get_id(), "processing": is_processing})
                        valid_helix = True
                    except requests.exceptions.HTTPError as e:
                        print(e.args)
                        status_code = e.response.status_code
                        if status_code == 401:
                            print("Helix is out of date, refreshing.")
                            self._clip_bot.refresh_token()
                            self._helix = self._clip_bot.get_helix()
                            num_retries += 1
                        else:
                            return {"error": "An unexpected error occurred."}
                else:
                    self._clip_bot.setup_config()
                    self._helix = self._clip_bot.get_helix()
                    num_retries += 1
            else:
                if self._helix is not None:
                    if num_retries >= self._clip_bot.MAX_RETRIES:
                        print("Unable to connect to Twitch API. Quitting...")
                        break
                    for video_id in videos:
                        try:
                            video = self._helix.video(video_id)
                            thumbnail = video.thumbnail_url
                            if not thumbnail:
                                thumbnail = os.path.normpath("../video_image_placeholder.png")
                            else:
                                thumbnail = re.sub(r"%{.*?}", "300", thumbnail)
                            d = video.created_at
                            date = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
                            to_zone = tz.tzlocal()
                            date = date.astimezone(to_zone)
                            date = date.strftime("%Y-%m-%d")
                            clipped = os.path.exists(resource_path(f"{self._path_name}/{video.id}"))
                            processing_videos = self._clip_bot._processing.get(self.get_id(), None)
                            if processing_videos and (int(video.id) in processing_videos or str(video.id) in processing_videos):
                                is_processing = True
                            else:
                                is_processing = False
                            if processing_check == is_processing:
                                data.append({"id": video.id, "title": video.title, "date": date, "desc": video.description,
                                             "thumbnail": thumbnail, "url": video.url, "clipped": clipped,
                                             "channelId": self.get_id(), "processing": is_processing})
                            valid_helix = True
                        except requests.exceptions.HTTPError as e:
                            print(e.args)
                            status_code = e.response.status_code
                            if status_code == 400:
                                print("Video not found.")
                                valid_helix = True
                            elif status_code == 401:
                                print("Helix is out of date, refreshing.")
                                self._clip_bot.refresh_token()
                                self._helix = self._clip_bot.get_helix()
                                num_retries += 1
                            else:
                                return {"error": "An unexpected error occurred."}
                else:
                    self._clip_bot.setup_config()
                    self._helix = self._clip_bot.get_helix()
                    num_retries += 1
        return data

    # Grab Twitch SUb, BTTV, FrankerFaceZ emotes and add to channel object
    def populate_emotes(self):
        bttv_success, twitch_success, ffz_success, _7tv_success = False, False, False, False
        bttv_retries, twitch_retries, ffz_retries, _7tv_retries = 0, 0, 0, 0
        while not bttv_success:
            if bttv_retries >= self._clip_bot.MAX_RETRIES:
                print("Unable to connect to BTTV API. Quitting...")
                break
            try:
                get_bttv_emotes_request = requests.get(self._bttv_url + str(self._id), timeout=1)
                if get_bttv_emotes_request.status_code == requests.codes.ok:
                    emote_types = ["sharedEmotes", "channelEmotes"]
                    bttv_emotes = json.loads(get_bttv_emotes_request.text)
                    for emote_type in emote_types:
                        for bttv_emote in bttv_emotes[emote_type]:
                            self._bttv_emotes.append({"name": bttv_emote["code"],
                                                      "imageUrl": self._bttv_img_url + bttv_emote["id"] + "/1x"})
                            self._name_to_emotes_map[bttv_emote["code"].lower()] = bttv_emote["code"]
                    bttv_success = True
                else:
                    print("Unable to complete get request for BTTV Emotes")
                    print("Error code:", get_bttv_emotes_request.status_code)
                    bttv_retries += 1
            except requests.exceptions.Timeout as e:
                print("BTTV Request timed out")
                print(e.args)
                bttv_retries += 1
        while not twitch_success:
            if twitch_retries >= self._clip_bot.MAX_RETRIES:
                print("Unable to connect to Twitch Emote API. Quitting...")
                break
            try:
                headers = {"Authorization": f"Bearer {self._clip_bot._access_token}",
                           "Client-Id": self._clip_bot._client_id}
                get_twitch_sub_emotes = requests.get(self._twitch_sub_url + str(self._id),
                                                     headers=headers, timeout=1)
                if get_twitch_sub_emotes.status_code == requests.codes.ok:
                    twitch_sub_emotes = json.loads(get_twitch_sub_emotes.text)
                    for twitch_sub_emote in twitch_sub_emotes["data"]:
                        if twitch_sub_emote["emote_type"] == "subscriptions":
                            self._twitch_emotes.append({"name": twitch_sub_emote["name"],
                                                        "imageUrl": twitch_sub_emote["images"]["url_1x"]})
                            self._name_to_emotes_map[twitch_sub_emote["name"].lower()] = twitch_sub_emote["name"]
                    twitch_success = True
                else:
                    print("Unable to complete get request for Twitch Sub Emotes")
                    print("Error code:", get_twitch_sub_emotes.status_code)
                    twitch_retries += 1
            except requests.exceptions.Timeout as e:
                print("Twitch Sub Emotes Request timed out")
                print(e.args)
                twitch_retries += 1
        while not ffz_success:
            if ffz_retries >= self._clip_bot.MAX_RETRIES:
                print("Unable to connect to FFZ API. Quitting...")
                break
            try:
                get_franker_face_z_emotes = requests.get(self._franker_face_z_url, timeout=1)
                if get_franker_face_z_emotes.status_code == requests.codes.ok:
                    franker_face_z_emotes = json.loads(get_franker_face_z_emotes.text)
                    franker_face_z_emote_set = franker_face_z_emotes["room"]["set"]
                    for franker_face_z_emote in franker_face_z_emotes["sets"][str(franker_face_z_emote_set)]["emoticons"]:
                        self._ffz_emotes.append({"name": franker_face_z_emote["name"],
                                                 "imageUrl": franker_face_z_emote["urls"]["1"]})
                        self._name_to_emotes_map[franker_face_z_emote["name"].lower()] = franker_face_z_emote["name"]
                    ffz_success = True
                else:
                    print("Unable to complete get request for FrankerFaceZ Emotes")
                    print("Error code:", get_franker_face_z_emotes.status_code)
                    ffz_retries += 1
            except requests.exceptions.Timeout as e:
                print("FFZ Emotes Request timed out")
                print(e.args)
                ffz_retries += 1
        while not _7tv_success:
            if _7tv_retries >= self._clip_bot.MAX_RETRIES:
                print("Unable to connect to 7TV API. Quitting...")
                break
            try:
                get_7tv_emotes = requests.get(self._7tv_url, timeout=1)
                if get_7tv_emotes.status_code == requests.codes.ok:
                    _7tv_emote_set = json.loads(get_7tv_emotes.text)
                    for _7tv_emote in _7tv_emote_set:
                        self._7tv_emotes.append({"name": _7tv_emote["name"],
                                                 "imageUrl": _7tv_emote["urls"][0][1]})
                        self._name_to_emotes_map[_7tv_emote["name"].lower()] = _7tv_emote["name"]
                    _7tv_success = True
                else:
                    print("Unable to complete get request for 7TV Emotes")
                    print("Error code:", get_franker_face_z_emotes.status_code)
                    _7tv_retries += 1
            except requests.exceptions.Timeout as e:
                print("7TV Emotes Request timed out")
                print(e.args)
                _7tv_retries += 1