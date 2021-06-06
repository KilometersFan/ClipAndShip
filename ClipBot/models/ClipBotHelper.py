import json
import os
import re
import sys
import time
import requests.exceptions
from pprint import pprint
from json import dump, load
from datetime import datetime
from .Channel import Channel

class ClipBotHelper(object):
    """ClipBotHelper that handles individual channels and their videos"""
    def __init__(self, channel: Channel, clipBot):
        self._clipBot = clipBot
        if not clipBot.oauthConfigured:
            clipBot.setUpConfig()
        self._channel = channel
        self._helix = clipBot.getHelix()
        self._pathName = f"data/channels/{self._channel.getId()}"
        self._startTime = None
        self._endTime = None
        self._processingGroup = False

    def processComments(self, comments):
        processedComments = []
        totalComments = 0
        totalCommentDiff = 0
        totalEmotes = 0
        channelEmotes = self._channel.getEmoteNames()
        prevCommentCreated = None
        knownBots = ["Nightbot", "Fossabot", "Moobot", "PhantomBot"]
        start = time.time()
        print(f"Beginning preprocessing of comments at {datetime.now()}")
        print("=================================================================")
        for comment in comments:
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
                            emote: 1 for emote in emotesInComment # commentEmotesOnly.count(emote)
                        }
                    ,
                    "created": createdAtTime,
                }
                processedComments.append(processedComment)
                totalComments += 1
                if prevCommentCreated:
                    totalCommentDiff += createdAtTime - prevCommentCreated
                prevCommentCreated = createdAtTime
                totalEmotes += len(emotesInComment)
        end = time.time()
        rate = totalComments/totalCommentDiff
        print(f"RATE: {rate}")
        print("=================================================================")
        print(f"Finished preprocessing of comments at {datetime.now()}. Took {end - start} seconds")
        print(f"Total comments in processed comments: {totalComments}")
        # Update/Create Markov chain for recommendations
        if not os.path.exists(self._pathName):
            os.makedirs(self._pathName)
        if os.path.exists(f"{self._pathName}/recommendation_data.json"):
            with open(f"{self._pathName}/recommendation_data.json", "r") as ifile:
                chain = load(ifile)
        else:
            chain = {}
            for emote in channelEmotes:
                chain[emote] = {}
        if "totalEmotes" in chain:
            chain["totalEmotes"] += totalEmotes
        else:
            chain["totalEmotes"] = totalEmotes
        prevWords = []
        for comment in processedComments:
            words = list(comment["emoteSet"])
            print(words)

            for i in range(len(words) - 1):
                if words[i + 1] not in  chain[words[i]]:
                    chain[words[i]][words[i + 1]] = 1
                else:
                    chain[words[i]][words[i + 1]] += 1
            if len(prevWords):
                for prevWord in prevWords:
                    for i in range(len(words)):
                        if words[i] not in chain[prevWord]:
                            chain[prevWord][words[i]] = 1
                        else:
                            chain[prevWord][words[i]] += 1
            prevWords = words
        with open(f"{self._pathName}/recommendation_data.json", "w") as ofile:
            dump(chain, ofile, separators=(",", ":"), indent=4)
        return processedComments, rate


    # go through video and broadcast messages to each category thread
    def processVideo(self, response, videoId=None):
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
                processedComments, rate = self.processComments(comments)
                groups = []
                group = {}
                prevCommentEnd = None
                print("+++++++++++++++++++++++++++++++++++++++++")
                print(f"Starting clip process for video {videoId} at {datetime.now()}")
                start = time.time()
                print(f"Total processed comments {len(processedComments)}")
                # Get groups from processed comments
                for comment in processedComments:
                    if self._processingGroup and prevCommentEnd and ((comment["created"] - prevCommentEnd) > 2 * rate):
                        self._endTime = prevCommentEnd
                        # print(f"End - start time = {(self._endTime - self._startTime).total_seconds()}")
                        if (self._endTime - self._startTime) > 0:
                            group["start"] = self._startTime - (self._endTime/self._startTime)/2
                            group["end"] = self._endTime - (self._endTime/self._startTime)/4
                            group["emoteRate"] = group["totalFrequency"]/(group["end"] - group["start"])
                            groups.append(group.copy())
                        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        self._processingGroup = False
                        group.clear()
                    if not self._processingGroup:
                        self._startTime = comment["created"]
                        self._processingGroup = True
                        prevCommentEnd = self._startTime
                        group["emoteSet"] = set(comment["emoteSet"])
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
                        group["text"] = comment["text"]
                    else:
                        if (comment["created"] - self._startTime) not in group["graph_x"]:
                            group["emoteSet"] = group["emoteSet"].union(set(comment["emoteSet"]))
                            for emote in comment["emoteSet"]:
                                if emote in group["emoteFrequency"]:
                                    group["emoteFrequency"][emote] += comment["emoteFrequency"][emote]
                                else:
                                    group["emoteFrequency"][emote] = comment["emoteFrequency"][emote]
                                group["totalFrequency"] += comment["emoteFrequency"][emote]
                            group["totalComments"] += 1

                            group["comments"].append(comment["emoteFrequency"])
                            group["graph_x"].append(comment["created"] - self._startTime)
                            prevCommentEnd = comment["created"]
                            group["text"] += " " + comment["text"]
                totalGroups = len(groups)
                print(f"Total number of groups found before filter = {totalGroups}")
                avgEmotesPerGroup = sum(group["totalFrequency"] for group in groups)/totalGroups
                avgLengthPerGroup = sum((group["end"] - group["start"]) for group in groups) / totalGroups
                filteredGroups = list(filter(lambda group:
                                             group["totalFrequency"] > 1.25 * avgEmotesPerGroup
                                             and (group["end"] - group["start"]) > 1.25 * avgLengthPerGroup
                                             and group["emoteRate"] > 1.25 * avgEmotesPerGroup/avgLengthPerGroup,
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
                            group["similarities"][category] = round(similarity, 3)
                        for i,comment in enumerate(group["comments"]):
                            if category in group["graph_y"]:
                                group["graph_y"][category].append(sum(comment[emote] for emote in emotesInCategory.intersection(comment.keys())))
                            else:
                                group["graph_y"][category] = [sum(comment[emote] for emote in emotesInCategory.intersection(comment.keys()))]
                            totalEmotesInCategory = sum(comment[emote] for emote in emotesInCategory.intersection(comment.keys()))
                            if totalEmotesInCategory > 0:
                                group["graph_data"][category].append([category, group["graph_x"][i], totalEmotesInCategory])
                    for category in categories:
                        if sum(group["graph_y"][category]) == 0:
                            group["graph_y"].pop(category)
                            group["graph_data"].pop(category)
                        elif sum(group["graph_y"][category])/group["totalFrequency"] < .33:
                            group["similarities"].pop(category)
                            group["graph_y"].pop(category)
                            group["graph_data"].pop(category)
                    # clean up data
                    group.pop("comments")
                    group.pop("graph_x")
                    group.pop("graph_y")
                    group.pop("emoteRate")
                    group.pop("totalFrequency")
                    group.pop("totalComments")
                    group.pop("emoteSet")
                    group["start"] = round(group["start"])
                    group["end"] = round(group["end"])
                    group["length"] = round(group["end"] - group["start"])
                    groupTimeData = []
                    for category in group["graph_data"].keys():
                        groupTimeData.extend(group["graph_data"][category])
                    group["graph_data"] = groupTimeData
                filteredGroups = list(filter(lambda group:
                                             len(group["similarities"]) > 0,
                                             filteredGroups))
                print(f"Total number of groups found after second filter = {len(filteredGroups)}")
                end = time.time()
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Finished assigning categories to processed groups at {datetime.now()}. Process took {end - start} seconds")
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
                with open(f"{self._pathName}/{videoId}/data.csv", "w+") as ofile:
                    for group in filteredGroups:
                        labels = []
                        for category in categories:
                            label = "1" if category in group["similarities"] else "0"
                            labels.append(label)
                        ofile.write(f"{group['text']},{','.join(labels)}\n")
                response["status"] = 200
                response["msg"] = "Successfully clipped the video: " + video.title + " recorded on " + video.created_at[:10]
                response["id"] = video.id
                response["channelId"] = self._channel.getId()
                response["data"] = data
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
