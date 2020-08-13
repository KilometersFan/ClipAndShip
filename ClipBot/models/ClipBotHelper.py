import twitch
import threading
import queue
import datetime
import os
import sys
import time
import requests.exceptions
from datetime import timedelta
import models.Channel as Channel
import models.Category as Category
import models.CategoryThread as CategoryThread
import models.ClipBot as ClipBot

class ClipBotHelper(object):
    """ClipBotHelper that handles individual channels and their videos"""
    def __init__(self, channel: Channel.Channel, clipBot):
        self._clipBot = clipBot
        if not clipBot.oauthConfigured:
            clipBot.setUpConfig()
        self._channel = channel
        self._helix = clipBot.getHelix()
        self._categoryThreads = {}
        for category in self._channel.getCategories():
            ct = CategoryThread.CategoryThread(category)
            self._categoryThreads[category.getType()] = ct
            ct.start()
        self._pathName = 'data/channels/' + self._channel.getName()
        self.stopVideo = {}

    # cancel processing
    def stopProccessingVideo(self, videoId):
        self.stopVideo[videoId] = True

    # go through video and broadcast messages to each category thread
    def main(self, videoId=None):
        oauthWorks = False
        categories = [category.getType() for category in self._channel.getCategories()]
        knownBots = ["Nightbot", "Fossabot", "Moobot", "PhantomBot"]
        while not oauthWorks:
            try:
                print("Starting clip process for video", videoId)
                video, comments = None, None
                # setup video and comments to parse
                if not videoId:
                    for v, c in self._helix.user(self._channel.getName()).videos(first=1).comments:
                        video = v
                        comments = c
                        videoId = v.id
                else:
                    for v, c in self._helix.user(self._channel.getName()).videos(id=videoId).comments:
                        video = v
                        comments = c
                self.stopVideo[videoId] = False
                # parse total duration of video
                duration = video.duration
                hours = duration.find('h')
                min = duration.find('m')
                sec = duration.find('s')
                h = m = s = 0;
                if (hours >= 0 and duration[0:hours]):
                    h = int(duration[0:hours])
                if (min >= 0 and duration[hours+1:min]):
                    m = int(duration[hours+1:min])
                if (sec >= 0 and duration[min+1:sec]):
                    s = int(duration[min+1:sec])
                duration = timedelta(seconds=s, minutes=m, hours=h).total_seconds()
                try:
                    decimalIndex = video.created_at.index(".")
                except ValueError as e:
                    decimalIndex = -1
                strippedTime = video.created_at[:decimalIndex]
                videoStartTime = datetime.datetime.fromisoformat(strippedTime)
                    
                count = 0
                # send comments to every category thread
                for comment in comments:
                    if self.stopVideo[videoId]:
                        print("User cancelled video processing, aborting...")
                        print("Removing", videoId, "from set of videos owned by", self._channel.getId())
                        self._clipBot._processing[self._channel.getId()].remove(videoId)
                        self._clipBot._helpers[self._channel.getId()].pop(videoId)
                        return {"status": 201, "msg": "Cancelled video processing for: " + video.title + " recorded on " + video.created_at[:10], "id": video.id, "channelId": self._channel.getId()}
                    if len(comment.message.body) > 30  or comment.message.body[0] == "!" or comment.commenter.display_name in knownBots:
                        continue
                    else:
                        for category in categories:
                            self._categoryThreads[category].addToQueue(comment)
                    if count == 5000:
                        print("5000 comments read")
                        time.sleep(1)
                        count = 0
                    else:
                        count += 1

                            
                #send terminate signal to each Category Thread
                for ct in list(self._categoryThreads.values()):
                    ct.addToQueue(None)
                    ct.join()
                print("Finished")
                #output to file(s) the timestamps for each category
                while not all(ct.finished == True for ct in self._categoryThreads.values()):
                    time.sleep(1)
                if not os.path.exists(self._pathName):
                    os.makedirs(self._pathName)
                results = []
                for category in self._channel.getCategories():
                    if not os.path.exists(self._pathName + "/" + videoId):
                        os.makedirs(self._pathName + "/" + videoId)
                    if not os.path.exists(self._pathName + "/" + videoId + "/" + category.getType()):
                        os.makedirs(self._pathName + "/" + videoId + "/" + category.getType())
                    with open(self._pathName + "/" + videoId + "/" + category.getType() + "/timestamps.txt", "w") as ofile:
                        for start, end in category.getTimestamps():
                            tdelta1 = start - videoStartTime
                            totalSeconds1 = tdelta1.total_seconds()
                            # do some math to get relative start time of clip from video start time
                            hours1 = totalSeconds1 // 3600
                            minutes1 = (totalSeconds1 % 3600) // 60
                            seconds1 = (totalSeconds1 % 3600) % 60

                            if(totalSeconds1 < 0 or totalSeconds1 > duration):
                                print("Start time of clip:", start, "Timestamp:", "{}h{}m{}s".format(int(hours1), int(minutes1), int(seconds1)))
                                continue
                            # do some math to get relative end time of clip from video start time
                            tdelta2 = end - videoStartTime
                            totalSeconds2 = tdelta2.total_seconds()
                            
                            hours2 = totalSeconds2 // 3600
                            minutes2 = (totalSeconds2 % 3600) // 60
                            seconds2 = (totalSeconds2 % 3600) % 60
                            if(totalSeconds2 < 0 or totalSeconds2 > duration):
                                print("End time of clip:", end, "Timestamp:", "Timestamp:", "{}h{}m{}s".format(int(hours2), int(minutes2), int(seconds2)))
                                continue
                            ofile.write("{}h{}m{}s".format(int(hours1), int(minutes1), int(seconds1)) + "-" + "{}h{}m{}s\n".format(int(hours2), int(minutes2), int(seconds2)))
                    category.clearTimestamps()
                print("Successfully clipped the video and outputted results to timestamps.txt")
                oauthWorks = True
                # remove from porcessing list
                print("Removing", videoId, "from set of videos owned by", self._channel.getId())
                self._clipBot._processing[self._channel.getId()].remove(videoId)
                return {"status": 200, "msg": "Successfully clipped the video: " + video.title + " recorded on " + video.created_at[:10], "id": video.id, "channelId": self._channel.getId()}
            except requests.exceptions.HTTPError as http_err: 
                statusCode = http_err.response.status_code
                if statusCode == 401:
                    print("401 Unauthorized error, refreshing access token. Helper")
                    self._clipBot.refreshToken()
                    self._helix = self._clipBot.getHelix()
                else:
                    print("Other error received:" , statusCode)
                    print("Removing", videoId, "from set of videos owned by", self._channel.getId())
                    self._clipBot._processing[self._channel.getId()].remove(videoId)
                    return {"status" : statusCode, "msg": "Error when processing the video, please try again."}
            except requests.exceptions.ConnectionError as http_err:
                print("Connection error:", http_err.args)
                print("Trying again")
                time.sleep(2)
            except Exception as e:
                print(sys.exc_info()[0])
                print(e.args)
                print("Removing", videoId, "from set of videos owned by", self._channel.getId())
                self._clipBot._processing[self._channel.getId()].remove(videoId)
                return {"status" : 400, "msg": "Unable to process video, please try again."}
            time.sleep(1)
