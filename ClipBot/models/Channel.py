import twitch
import requests
import json
import re
import os
from datetime import datetime
from dateutil import tz
from Category import Category

class Channel(object):
    """Twitch channel, stores categories set by channel"""
    def __init__(self, id: int, helix, clipBot):
        self._id = id
        self._helix = helix
        self._categories = {}
        self._ffEmotes = []
        self._bttvEmotes = []
        self._twitchEmotes = []
        self._bttvURL = "https://api.betterttv.net/3/cached/users/twitch/"
        self._bttvImgURL = "https://cdn.betterttv.net/emote/"
        self._twitchSubURL = "https://api.twitchemotes.com/api/v4/channels/"
        self._clipBot = clipBot
        validHelix = False
        # reset helix if acces token is invalid
        while not validHelix:
            try:
                if helix is not None:
                    self._name = helix.user(id).display_name
                    self._pathName = 'data/channels/' + self._name
                    self._desc = helix.user(id).description
                    self._img = helix.user(id).profile_image_url
                    self._frankerfacezURL = "https://api.frankerfacez.com/v1/room/" + self._name.lower()
                    validHelix = True
                else:
                    print("Helix doesn't exist")
            except requests.exceptions.HTTPError as http_err:
                statusCode = http_err.response.status_code
                if statusCode == 401:
                    print("401 Unauthorized error, refreshing access token. Videos")
                    clipBot.refreshToken()
                    helix = clipBot.getHelix()
                    print("Finished")
                else:
                    print("Other error received:" , statusCode)

    # add emote to channel
    def addEmote(self, emote):
        self._emotes.add(emote)

    # return all emotes in channel
    def getEmotes(self):
        ffEmotes = sorted(list(self._ffEmotes), key=lambda e: e['name'].lower())
        bttvEmotes = sorted(list(self._bttvEmotes), key=lambda e: e['name'].lower())
        twitchEmotes = sorted(list(self._twitchEmotes), key= lambda e: e['name'].lower())
        return { "ffEmotes" : ffEmotes, "bttvEmotes" : bttvEmotes, "twitchEmotes" : twitchEmotes}

    def getEmoteNames(self):
        emoteTypes = ["ffEmotes", "bttvEmotes", "twitchEmotes"]
        channelEmoteList = set()
        for emoteType in emoteTypes:
            for emote in self.getEmotes()[emoteType]:
                channelEmoteList.add(emote["name"].lower())
        return channelEmoteList

    # add category to channel
    def addCategory(self, category, isString=False, channelId=None):
        if isString:
            if(category not in self._categories):
                self._categories[category] = Category(category, channelId)
            else:
                print("Type {} already exists!".format(category))
                raise Exception("Category type is a duplicate.")
        else:
            if(category.getType() not in self._categories):
                self._categories[category.getType()] = category
            else:
                print("Type {} already exists!".format(type))
                raise Exception("Category type is a duplicate.")
    
    # remove category from channel
    def removeCategory(self, type):
        if(type in self._categories):
            del self._categories[type]
        else:
            print("Type {} does not exist!".format(type))
            raise Exception("Category type does not exist.")
    
    # remove all categories
    def clearCategories(self):
        self._categories.clear()

    # return all categories
    def getCategories(self):
        categories = sorted(list(self._categories.values()), key= lambda c: c.getType())
        return categories

    # return category object based on type
    def getCategory(self, type):
        if type in self._categories:
            return self._categories[type]
        return None

    # add emotes in param to catgeory specified by type
    def addEmotesToCategory(self, type, emotes):
        category = self._categories[type]
        if category:
            for emote in emotes:
                category.addEmote(emote.lower())
        else:
            print("Invalid category specified")
    
    # remove all emotes in param from category specified by type
    def rmvEmotesFromCategory(self, type, emotes):
        category = self.getCategory(type)
        emotes = set([emote.lower() for emote in emotes])
        if category:
            category.setEmotes(emotes)
        else:
            print("Invalid category specified")

    # return channel name
    def getName(self):
        return self._name

    # return Twitch channel id
    def getId(self):
        return self._id

    # return channel image
    def getImg(self):
        return self._img

    # return channel description
    def getDesc(self):
        return self._desc

    # return channel videos specifed by list of ids (if present) or the 9 most recent
    def getVideos(self, videos=None):
        data = []
        validHelix = False
        while not validHelix:
            if not videos:
                try:
                    for video in self._helix.user(self._name).videos():
                        thumbnail = video.thumbnail_url
                        if not thumbnail:
                            thumbnail = "../NotFound.png"
                        else:
                            thumbnail = re.sub(r"%{.*?}", "300", thumbnail)
                        d = video.created_at
                        date = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
                        to_zone = tz.tzlocal()
                        date = date.astimezone(to_zone)
                        date = date.strftime("%Y-%m-%d") 
                        clipped = os.path.exists(self._pathName + "/" + video.id)
                        processing = self._clipBot._processing.get(self.getId(), None)
                        if processing and video.id in processing:
                            processing = True
                        else:
                            processing = False
                        data.append({"id": video.id, "title": video.title, "date": date, "desc": video.description, "thumbnail": thumbnail, "url" : video.url, "clipped": clipped, "channelId": self.getId(), "processing": processing})
                    validHelix = True
                except requests.exceptions.HTTPError as e:
                    print(e.args)
                    statusCode = e.response.status_code
                    if statusCode == 401:
                        print("Helix is out of date, refreshing.")
                        self._helix = self._clipBot.getHelix()
                    else:
                        return {"error" : "An unexpected error occurred."};
            else:
                for id in videos:
                    try:
                        video = self._helix.video(id)
                        thumbnail = video.thumbnail_url
                        if not thumbnail:
                            thumbnail = "../NotFound.png"
                        else:
                            thumbnail = re.sub(r"%{.*?}", "300", thumbnail)
                        d = video.created_at
                        date = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
                        to_zone = tz.tzlocal()
                        date = date.astimezone(to_zone)
                        date = date.strftime("%Y-%m-%d") 
                        clipped = os.path.exists(self._pathName + "/" + video.id)
                        processing = self._clipBot._processing.get(self.getId(), None)
                        if processing and video.id in processing:
                            processing = True
                        else:
                            processing = False
                        data.append({"id": video.id, "title": video.title, "date": date, "desc": video.description, "thumbnail": thumbnail, "url" : video.url, "clipped": clipped, "channelId": self.getId(), "processing": processing})
                        validHelix = True
                    except requests.exceptions.HTTPError as e:
                        print(e.args)
                        statusCode = e.response.status_code
                        if statusCode == 400:
                            print("Video not found.")
                            validHelix = True
                        elif statusCode == 401:
                            print("Helix is out of date, refreshing.")
                            self._helix = self._clipBot.getHelix()
                        else:
                            return {"error" : "An unexpected error occurred."}; 
        return data

    # Grab Twitch SUb, BTTV, FrankerFaceZ emotes and add to channel object
    def populateEmotes(self):
        bttvSuccess = False 
        twitchSuccess = False 
        ffzSuccess = False
        while not bttvSuccess:
            try:
                getBTTVEmotesRequest = requests.get(self._bttvURL + str(self._id), timeout=1)
                if(getBTTVEmotesRequest.status_code == requests.codes.ok):
                    bttvEmotes = json.loads(getBTTVEmotesRequest.text)
                    for bttvEmote in bttvEmotes["sharedEmotes"]:
                        self._bttvEmotes.append({"name" : bttvEmote["code"], "imageUrl" : self._bttvImgURL + bttvEmote["id"] + "/1x"})
                else:
                    print("Unable to complete get request for BTTV Emotes")
                    print("Error code:", getBTTVEmotesRequest.status_code)
                bttvSuccess = True
            except requests.exceptions.Timeout as e:
                print("BTTV Request timed out")
                print(e.args)
        while not twitchSuccess:
            try:
                getTwitchSubEmotes = requests.get(self._twitchSubURL + str(self._id), timeout=1)
                if(getTwitchSubEmotes.status_code == requests.codes.ok):
                    twitchSubEmotes = json.loads(getTwitchSubEmotes.text)
                    for twitchSubEmote in twitchSubEmotes["emotes"]:
                        self._twitchEmotes.append({"name" : twitchSubEmote["code"], "imageUrl" : ""})
                else:
                    print("Unable to complete get request for Twitch Sub Emotes")
                    print("Error code:", getTwitchSubEmotes.status_code)
                twitchSuccess = True
            except requests.exceptions.Timeout as e:
                print("Twitch Sub Emotes Request timed out")
                print(e.args)
        while not ffzSuccess:
            try:
                getFrankerFaceZEmotes = requests.get(self._frankerfacezURL, timeout=1)
                if(getFrankerFaceZEmotes.status_code == requests.codes.ok):
                    frankerFaceZEmotes = json.loads(getFrankerFaceZEmotes.text)
                    set = frankerFaceZEmotes["room"]["set"] 
                    for frankerFaceZEmote in frankerFaceZEmotes["sets"][str(set)]["emoticons"]:
                        self._ffEmotes.append({"name" : frankerFaceZEmote["name"], "imageUrl" : frankerFaceZEmote["urls"]["1"]})
                else:
                    print("Unable to complete get request for FrankerFaceZ Emotes")
                    print("Error code:", getFrankerFaceZEmotes.status_code)
                ffzSuccess = True
            except requests.exceptions.Timeout as e:
                print("FFZ Emotes Request timed out")
                print(e.args)



