import re
import sys
import time
import requests.exceptions
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
                try:
                    decimalIndex = comment.created_at.index(".")
                except ValueError as e:
                    decimalIndex = -1
                createdAtTime = datetime.fromisoformat(comment.created_at[:decimalIndex])
                processedComment = {
                    "text": commentEmotesOnly,
                    "emoteSet": emotesInComment,
                    "emoteFrequency":
                        {
                            emote: commentEmotesOnly.count(emote) for emote in emotesInComment
                        }
                    ,
                    "created": createdAtTime,
                }
                processedComments.append(processedComment)
                totalComments += 1
                if prevCommentCreated:
                    totalCommentDiff += (createdAtTime - prevCommentCreated).total_seconds()
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
                groups = []
                group = {}
                prevCommentEnd = None
                print("+++++++++++++++++++++++++++++++++++++++++")
                print(f"Starting clip process for video {videoId} at {datetime.now()}")
                start = time.time()
                print(f"Total processed comments {len(processedComments)}")
                # Get groups from processed comments
                for comment in processedComments:
                    if prevCommentEnd and ((comment["created"] - prevCommentEnd).total_seconds() > rate):
                        self._endTime = prevCommentEnd
                        if (self._endTime - self._startTime).total_seconds() > 0:
                            group["start"] = self._startTime
                            group["end"] = self._endTime
                            group["emoteRate"] = group["totalFrequency"]/(group["end"] - group["start"]).total_seconds()
                            groups.append(group.copy())
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
                    else:
                        group["emoteSet"] = group["emoteSet"].union(comment["emoteSet"])
                        for emote in comment["emoteSet"]:
                            if emote in group["emoteFrequency"]:
                                group["emoteFrequency"][emote] += comment["emoteFrequency"][emote]
                            else:
                                group["emoteFrequency"][emote] = comment["emoteFrequency"][emote]
                            group["totalFrequency"] += comment["emoteFrequency"][emote]
                        prevCommentEnd = comment["created"]
                totalGroups = len(groups)
                avgEmotesPerGroup = sum(group["totalFrequency"] for group in groups)/totalGroups
                filteredGroups = list(filter(lambda group: group["totalFrequency"] > avgEmotesPerGroup, groups))

                end = time.time()
                print("+++++++++++++++++++++++++++++++++++++++++")
                print(f"Finished group processing for video {videoId} at {datetime.now()}. Process took {end - start} seconds")
                # Assign categories to groups
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Starting to assign categories to processed groups for video {videoId} at {datetime.now()}")
                start = time.time()
                for group in filteredGroups:
                    group["similarities"] = {}
                    for category in categories:
                        emotesInCategory = self._channel.getCategory(category).getEmotes()
                        print(f"Group Emotes {' '.join(group['emoteSet'])}, Category Emotes: {' '.join(emotesInCategory)}")
                        intersection = group["emoteSet"].intersection(emotesInCategory)
                        union = group["emoteSet"].union(emotesInCategory)
                        similarity = len(intersection)/float(len(union))
                        print(f"Number of category emotes in the group: {sum(group['emoteFrequency'][emote] for emote in group['emoteFrequency'].keys() if emote in emotesInCategory)}")
                        weight = sum(group["emoteFrequency"][emote] for emote in group["emoteFrequency"].keys() if emote in emotesInCategory)/group["totalFrequency"]
                        print(f"Similarity: {similarity}, Weight: {weight}, Weighted Similarity: {similarity * weight}")
                        print("*****************************************")
                        if similarity * weight > 0:
                            group["similarities"][category] = similarity * weight
                filteredGroups = sorted(filteredGroups, key = lambda group: group["start"])
                end = time.time()
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Finished assigning categories to processed groups at {datetime.now()}. Process took {end - start} seconds")
                for group in filteredGroups:
                    if len(group["similarities"]):
                        print(f"Group at {group['start']} to {group['end']} is labeled as {max(group['similarities'], key=group['similarities'].get)}")
                # https://static-cdn.jtvnw.net/emoticons/v1/1570548/3.0
                self._stopVideo[videoId] = False
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
                try:
                    decimalIndex = video.created_at.index(".")
                except ValueError as e:
                    decimalIndex = -1
                strippedTime = video.created_at[:decimalIndex]
                videoStartTime = datetime.fromisoformat(strippedTime)
                data = {
                    "groups": filteredGroups,
                    "videoStart": videoStartTime
                }
                oauthWorks = True
                # remove from porcessing list
                print("Removing", videoId, "from set of videos owned by", self._channel.getId())
                self._clipBot._processing[self._channel.getId()].remove(videoId)
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
