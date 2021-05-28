import os
import re
import sys
import time
import base64
import pandas as pd
import requests.exceptions
import matplotlib.pyplot as plt
from pprint import pprint
from json import dump
from datetime import datetime
from Channel import Channel

class ClipBotHelper(object):
    """ClipBotHelper that handles individual channels and their videos"""
    def __init__(self, channel: Channel, clipBot):
        self._clipBot = clipBot
        if not clipBot.oauthConfigured:
            clipBot.setUpConfig()
        self._channel = channel
        self._helix = clipBot.getHelix()
        self._pathName = 'data/channels/' + self._channel.getName()
        self._stopVideo = {}
        self._startTime = None
        self._endTime = None
        self._processingGroup = False

    # cancel processing
    def stopProccessingVideo(self, videoId):
        self._stopVideo[videoId] = True

    def preprocessComments(self, comments):
        processedComments = []
        totalComments = 0
        totalCommentDiff = 0
        channelEmotes = self._channel.getEmoteNames()
        print(channelEmotes)
        prevCommentCreated = None
        knownBots = ["Nightbot", "Fossabot", "Moobot", "PhantomBot"]
        start = time.time()
        print(f"Beginning preprocessing of comments at {datetime.now()}")
        print("=================================================================")
        count = 0
        for comment in comments:
            # pprint(comment)
            commentText = comment.message.body.lower()
            splitComment = commentText.split()
            emotesInComment = channelEmotes.intersection(set(splitComment))
            if len(emotesInComment) and comment.commenter.display_name not in knownBots:
                regex = re.compile('|'.join(emotesInComment))
                commentEmotesOnly = " ".join(regex.findall(commentText))
                createdAtTime = comment.content_offset_seconds
                processedComment = {
                    "text": commentEmotesOnly,
                    "emoteSet": emotesInComment,
                    "emoteFrequency":
                        {
                            emote: commentEmotesOnly.count(emote) for emote in emotesInComment # commentEmotesOnly.count(emote)
                        }
                    ,
                    "created": createdAtTime,
                }
                processedComments.append(processedComment)
                totalComments += 1
                if prevCommentCreated:
                    totalCommentDiff += createdAtTime - prevCommentCreated
                prevCommentCreated = createdAtTime
        end = time.time()
        rate = totalComments/totalCommentDiff
        print(f"RATE: {rate}")
        print("=================================================================")
        print(f"Finished preprocessing of comments at {datetime.now()}. Took {end - start} seconds")
        return processedComments, rate

    # go through video and broadcast messages to each category thread
    def main(self, response, videoId=None):
        oauthWorks = False
        categories = [category.getType() for category in self._channel.getCategories()]
        while not oauthWorks:
            try:
                video, comments = None, None
                # setup video and comments to parse
                if not videoId:
                    print("Video id NOT supplied")
                    for v, c in self._helix.user(self._channel.getName()).videos(first=1).comments:
                        video = v
                        comments = c
                        videoId = v.id
                else:
                    print("Video id supplied")
                    for v, c in self._helix.videos([videoId]).comments:
                        video = v
                        comments = c
                print("Grabbed video and comments")
                # Get processed comments
                processedComments, rate = self.preprocessComments(comments)
                print(f"Rate = {rate}")
                groups = []
                group = {}
                prevCommentEnd = None
                print("+++++++++++++++++++++++++++++++++++++++++")
                print(f"Starting clip process for video {videoId} at {datetime.now()}")
                start = time.time()
                print(f"Total processed comments {len(processedComments)}")
                # Get groups from processed comments
                for comment in processedComments:
                    # if self._processingGroup and prevCommentEnd:
                    #     print(f"Diff between comments = {(comment['created'] - prevCommentEnd).total_seconds()} vs rate={rate}")
                    if self._processingGroup and prevCommentEnd and ((comment["created"] - prevCommentEnd) > 2 * rate):
                        self._endTime = prevCommentEnd
                        # print(f"End - start time = {(self._endTime - self._startTime).total_seconds()}")
                        if (self._endTime - self._startTime) > 0:
                            group["start"] = self._startTime - (self._endTime - self._startTime)/2
                            group["end"] = self._endTime - (self._endTime - self._startTime)/2
                            group["emoteRate"] = group["totalFrequency"]/(group["end"] - group["start"])
                            groups.append(group.copy())
                        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        self._processingGroup = False
                        group.clear()
                    if not self._processingGroup:
                        self._startTime = comment["created"]
                        self._processingGroup = True
                        prevCommentEnd = self._startTime
                        group["emoteSet"] = comment["emoteSet"]
                        group["emoteFrequency"] = {}
                        group["totalFrequency"] = 0
                        for emote in comment["emoteSet"]:
                            group["emoteFrequency"][emote] = comment["emoteFrequency"][emote]
                            group["totalFrequency"] += comment["emoteFrequency"][emote]
                        group["graph_x"] = [0.0]
                        group["graph_y"] = {}
                        group["graph_data"] = {}
                        group["totalComments"] = 0
                        group["comments"] = [comment["emoteFrequency"]]
                    else:
                        group["emoteSet"] = group["emoteSet"].union(comment["emoteSet"])
                        for emote in comment["emoteSet"]:
                            if emote in group["emoteFrequency"]:
                                group["emoteFrequency"][emote] += comment["emoteFrequency"][emote]
                            else:
                                group["emoteFrequency"][emote] = comment["emoteFrequency"][emote]
                            group["totalFrequency"] += comment["emoteFrequency"][emote]
                        group["totalComments"] += 1
                        group["comments"].append(comment["emoteFrequency"])
                        group["graph_x"].append(round(comment["created"] - self._startTime, 3))
                        prevCommentEnd = comment["created"]
                totalGroups = len(groups)
                print(f"Total number of groups found before filter = {totalGroups}")
                avgEmotesPerGroup = sum(group["totalFrequency"] for group in groups)/totalGroups
                avgLengthPerGroup = sum((group["end"] - group["start"]) for group in groups) / totalGroups
                filteredGroups = list(filter(lambda group:
                                             group["totalFrequency"] > avgEmotesPerGroup
                                             and (group["end"] - group["start"]) > avgLengthPerGroup,
                                             groups))
                print(f"Total number of groups found after first filter = {len(filteredGroups)}")
                end = time.time()
                print("+++++++++++++++++++++++++++++++++++++++++")
                print(f"Finished group processing for video {videoId} at {datetime.now()}. Process took {end - start} seconds")
                # Assign categories to groups
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Starting to assign categories to processed groups for video {videoId} at {datetime.now()}")
                start = time.time()
                filteredGroups = sorted(filteredGroups, key=lambda group: group["start"])
                for group in filteredGroups:
                    group["similarities"] = {}
                    for category in categories:
                        group["graph_data"][category] = []
                        group["graph_y"] = {}
                    for category in categories:
                        emotesInCategory = self._channel.getCategory(category).getEmotes()
                        # print(f"Group Emotes {' '.join(group['emoteSet'])}, Category Emotes: {' '.join(emotesInCategory)}")
                        intersection = group["emoteSet"].intersection(emotesInCategory)
                        union = group["emoteSet"].union(emotesInCategory)
                        similarity = len(intersection)/float(len(union))
                        # print(f"Number of category emotes in the group: {sum(group['emoteFrequency'][emote] for emote in group['emoteFrequency'].keys() if emote in emotesInCategory)}")
                        weight = sum(group["emoteFrequency"][emote] for emote in group["emoteFrequency"].keys() if emote in emotesInCategory)/group["totalFrequency"]
                        # print(f"Similarity: {similarity}, Weight: {weight}, Weighted Similarity: {similarity * weight}")
                        # print("*****************************************")
                        if similarity * weight > 0:
                            group["similarities"][category] = round(similarity * weight, 3)
                        for i,comment in enumerate(group["comments"]):
                            if category in group["graph_y"]:
                                group["graph_y"][category].append(sum(comment[emote] for emote in emotesInCategory.intersection(comment.keys())))
                            else:
                                group["graph_y"][category] = [sum(comment[emote] for emote in emotesInCategory.intersection(comment.keys()))]
                            group["graph_data"][category].append([category, group["graph_x"][i], sum(comment[emote] for emote in emotesInCategory.intersection(comment.keys()))])
                    for category in categories:
                        if sum(group["graph_y"][category]) == 0:
                            group["graph_y"].pop(category)
                            group["graph_data"].pop(category)
                        elif sum(group["graph_y"][category])/group["totalFrequency"] < .33:
                            group["similarities"].pop(category)
                            group["graph_y"].pop(category)
                            group["graph_data"].pop(category)
                    group.pop("comments")
                    group.pop("graph_x")
                    group.pop("graph_y")
                    group["start"] = round(group["start"], 3)
                    group["end"] = round(group["end"], 3)
                    groupTimeData = []
                    for category in group["graph_data"].keys():
                        groupTimeData.extend(group["graph_data"][category])
                    group["graph_data"] = groupTimeData
                    group["emoteSet"] = list(group["emoteSet"])
                filteredGroups = list(filter(lambda group:
                                             len(group["similarities"]) > 0,
                                             filteredGroups))
                print(f"Total number of groups found after second filter = {len(filteredGroups)}")

                for group in filteredGroups:
                    df = pd.DataFrame(group["graph_data"], columns=["category", "time", "instances"])
                    df = df.pivot(index='time', columns='category', values='instances')
                    df.plot()
                    plt.ylim(bottom=0)
                    plt.savefig("graph.png", bbox_inches="tight")
                    plt.close()
                    with open("graph.png", mode="rb") as file:
                        img = file.read()
                        group["img"] = base64.encodebytes(img).decode("utf-8").replace("\n", "")
                end = time.time()
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Finished assigning categories to processed groups at {datetime.now()}. Process took {end - start} seconds")
                # https://static-cdn.jtvnw.net/emoticons/v1/1570548/3.0
                self._stopVideo[videoId] = False
                # parse total duration of video
                try:
                    decimalIndex = video.created_at.index(".")
                except ValueError as e:
                    decimalIndex = -1
                videoStartTime = video.created_at[:decimalIndex]
                data = {
                    "groups": filteredGroups,
                    "videoStart": videoStartTime
                }
                oauthWorks = True
                # save group data to json file
                if not os.path.exists(self._pathName):
                    os.makedirs(self._pathName)
                if not os.path.exists(f"{self._pathName}/{videoId}"):
                    os.makedirs(f"{self._pathName}/{videoId}")
                with open(f"{self._pathName}/{videoId}/data.json", "w+") as ofile:
                    dump(data, ofile, separators=(",", ":"), indent=4)

                # remove from processing list
                print("Removing", videoId, "from set of videos owned by", self._channel.getId())
                self._clipBot._processing[self._channel.getId()].remove(videoId)
                response["status"] = 200
                response["msg"] = "Successfully clipped the video: " + video.title + " recorded on " + video.created_at[:10]
                response["id"] = video.id
                response["channelId"] = self._channel.getId()
                response["data"] = data
                # response["data"] = processedComments
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
                    response["status"] = statusCode
                    response["msg"] = "Error when processing the video, please try again."
            except requests.exceptions.ConnectionError as http_err:
                print("Connection error:", http_err.args)
                print("Trying again")
                time.sleep(2)
            except Exception as e:
                print(sys.exc_info()[0])
                print(e.message)
                print("Removing", videoId, "from set of videos owned by", self._channel.getId())
                self._clipBot._processing[self._channel.getId()].remove(videoId)
                response["status"] = 400
                response["msg"] = "Unable to process video, please try again."
            time.sleep(1)
