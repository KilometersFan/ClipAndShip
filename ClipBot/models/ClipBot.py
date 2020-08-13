import os
import configparser
import twitch
import requests
import json
import models.Channel as Channel
import models.Category as Category
import models.ClipBotHelper as ClipBotHelper

class ClipBot(object):
    """Bot that helps find clips in a twitch VOD by analyzing chat messages"""
    def __init__(self):
        self._oauthURL = "https://id.twitch.tv/oauth2/"
        self._channels = {}
        self._helix = None
        self.oauthConfigured = False
        self.hasChannels = False
        self._channelInfo = {}
        self._processing = {}
        self._helpers = {}
    
    # return twitch Helix object
    def getHelix(self):
        return self._helix

    # add channel to user list
    def addChannel(self, channel):
        channel.populateEmotes()
        self._channels[channel.getId()] = channel
        self._channelInfo[channel.getId()] = [channel.getName(), channel.getId(), channel.getDesc(), channel.getImg()]
    
    # set up helix and twitch related stuff
    def setupConfig(self):
        cfg = configparser.ConfigParser()
        cfg.read("config/config.ini")
        settings = cfg["settings"]
        client_id = settings["client_id"]
        secret = settings["secret"]
        if not client_id or not secret:
            print("Unable to find credentials")
        else:
            try:
                authorizeRequest = requests.post(self._oauthURL + "token", params={"client_id" : client_id, "client_secret" : secret, "grant_type" : "client_credentials"})
                if(authorizeRequest.status_code == requests.codes.ok):
                    response = json.loads(authorizeRequest.text)
                    self._accessToken = response["access_token"]
                    self._helix = twitch.Helix(client_id, secret, True, None, True, self._accessToken)
                    self.oauthConfigured = True
                else:
                    print("Unable to complete post request for token")
            except requests.exceptions.Timeout:
                print("Request for refresh token timed out")

    # refresh access token when needed
    def refreshToken(self):
        cfg = configparser.ConfigParser()
        cfg.read("config/config.ini")
        settings = cfg["settings"]
        client_id = settings["client_id"]
        secret = settings["secret"]
        if not client_id or not secret:
            print("Unable to find credentials")
        else:
            try:
                authorizeRequest = requests.post(self._oauthURL + "token", params={"client_id" : client_id, "client_secret" : secret, "grant_type" : "client_credentials"}, timeout=2)
                if(authorizeRequest.status_code == requests.codes.ok):
                    response = json.loads(authorizeRequest.text)
                    self._accessToken = response["access_token"]
                    self._helix = twitch.Helix(client_id, secret, True, None, True, self._accessToken)
                else:
                    print("Unable to complete post request for token")
            except requests.exceptions.Timeout:
                print("Request for refresh token timed out")

    # read from channls.ini all the info from user's channels
    def setupChannels(self):
        cfg = configparser.ConfigParser()
        cfg.read("config/channels.ini")
        for section in cfg.sections():
            validToken = False
            while not validToken:
                try:
                    channel = Channel.Channel(int(section), self._helix, self)
                    for option in cfg.options(section):
                        category = Category.Category(option, section)
                        emoteList = cfg[section][option].split(",")
                        for emote in emoteList:
                            category.addEmote(emote)
                        channel.addCategory(category)
                    self.addChannel(channel)
                    validToken = True
                except requests.exceptions.HTTPError as http_err: 
                    statusCode = http_err.response.status_code
                    if statusCode == 401:
                        print("401 Unauthorized error, refreshing access token")
                        self.refreshToken()
                    else:
                        print("Other error received:" , statusCode)
                        break
        self.hasChannels = True
    
    # return all channels
    def getChannels(self):
        return list(self._channelInfo.values())

    # return a specific channl, either obejct or just dictionary with info
    def getChannel(self, id, info=True):
        if(info):
            return self._channelInfo.get(id, None)
        else:
            return self._channels.get(id, None)
    
    # search twitch for channel
    def searchForChannel(self, channelName):
        found = False
        while not found:
            try:
                if self._helix:
                    user = self._helix.user(channelName)
                    found = True
                    if user:
                        return {"status": 200, "id" : user.id, "displayName" : user.display_name, "desc" : user.description, "imgURL" : user.profile_image_url}
                    else:
                        return {"status", 404}
                else:
                    print("Helix creation failed")
                    self.setupConfig()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    self.setupConfig()
            except Exception as e:
                found = True
                return {"status", 404}

    # remove channel from user's list
    def removeChannel(self, channel_id):
        if self._channels.get(channel_id, None):
            del self._channels[channel_id]
        else:
            print("Channel doesn't exist.")
            raise Exception("Channel doesn't exist.")
        if self._channelInfo.get(channel_id, None):
             del self._channelInfo[channel_id]
        else:
            print("Channel doesn't exist.")
            raise Exception("Channel doesn't exist.")

    # run clip video function for channel
    def clipVideo(self, channel_id, id):
        if self._helix:
            channel = self._channels[channel_id]
            helper = ClipBotHelper.ClipBotHelper(channel, self)
            if channel_id not in self._processing:
                self._processing[channel_id] = set()
            self._processing[channel_id].add(id)
            if channel_id not in self._helpers:
                self._helpers[channel_id] = {id: helper}
            else:
                self._helpers[channel_id][id] = helper
            print("Added", id, "to set of videos owned by", channel_id)
            return helper.main(id)
        else:
            print("Helix creation failed")
            self.setupConfig()
    
    # return all videos that are currently processing
    def getProcessingVideos(self):
        results = []
        for key,value in self._processing.items():
            channel = self.getChannel(key, False)
            if len(list(value)) > 0:
                results += channel.getVideos(list(value))
        return results

    # cancel a video that is processing
    def cancelVideo(self, channel_id, video_id):
        helper = self._helpers[channel_id][video_id]
        helper.stopProccessingVideo(video_id)