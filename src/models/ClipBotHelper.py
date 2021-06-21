import os
import re
import sys
import time
import requests.exceptions
from json import dump, load
from datetime import datetime
from .Channel import Channel


class ClipBotHelper(object):
    """ClipBotHelper that handles individual channels and their videos"""

    def __init__(self, channel: Channel, clip_bot):
        self._clip_bot = clip_bot
        if not clip_bot.oauth_configured:
            clip_bot.setup_config()
        self._channel = channel
        self._helix = clip_bot.get_helix()
        path = os.getcwd()
        self._path_name = f"{path}/data/channels/{self._channel.get_id()}"
        self._start_time = None
        self._end_time = None
        self._processing_group = False

    def process_comments(self, comments):
        processed_comments = []
        total_comments = 0
        total_comment_diff = 0
        total_emotes = 0
        channel_emotes = self._channel.get_emote_names()
        prev_comment_created = None
        known_bots = ["Nightbot", "Fossabot", "Moobot", "PhantomBot"]
        start = time.time()
        print(f"Beginning preprocessing of comments at {datetime.now()}")
        print("=================================================================")
        for comment in comments:
            comment_text = comment.message.body.lower()
            split_comment = comment_text.split()
            emotes_in_comment = channel_emotes.intersection(set(split_comment))
            if len(emotes_in_comment) and comment.commenter.display_name not in known_bots:
                regex = re.compile('|'.join(emotes_in_comment))
                all_emotes_in_comment = regex.findall(comment_text)
                comment_emotes_only = " ".join(all_emotes_in_comment)
                created_at_time = comment.content_offset_seconds
                processed_comment = {
                    "text": comment_emotes_only,
                    "size": len(all_emotes_in_comment),
                    "emoteSet": emotes_in_comment,
                    "emoteFrequency":
                        {
                            emote: 1 for emote in emotes_in_comment  # comment_emotes_only.count(emote)
                        },
                    "created": created_at_time,
                }
                processed_comments.append(processed_comment)
                total_comments += 1
                if prev_comment_created:
                    total_comment_diff += created_at_time - prev_comment_created
                prev_comment_created = created_at_time
                total_emotes += len(emotes_in_comment)
        end = time.time()
        rate = total_comments / total_comment_diff
        print(f"RATE: {rate}")
        print("=================================================================")
        print(f"Finished preprocessing of comments at {datetime.now()}. Took {end - start} seconds")
        print(f"Total comments in processed comments: {total_comments}")
        # Update/Create Markov chain for recommendations
        if not os.path.exists(self._path_name):
            os.makedirs(self._path_name)
        if os.path.exists(f"{self._path_name}/recommendation_data.json"):
            with open(f"{self._path_name}/recommendation_data.json", "r") as ifile:
                chain = load(ifile)
        else:
            chain = {}
            for emote in channel_emotes:
                chain[emote] = {}
        if "totalEmotes" in chain:
            chain["totalEmotes"] += total_emotes
        else:
            chain["totalEmotes"] = total_emotes
        prev_words = []
        for comment in processed_comments:
            words = list(comment["emoteSet"])
            print(words)

            for i in range(len(words) - 1):
                if words[i + 1] not in chain[words[i]]:
                    chain[words[i]][words[i + 1]] = 1
                else:
                    chain[words[i]][words[i + 1]] += 2 if words[i] == words[i + 1] else 1
            if len(prev_words):
                for prev_word in prev_words:
                    if prev_word not in chain:
                        chain[prev_word] = {}
                    for i in range(len(words)):
                        if words[i] not in chain[prev_word]:
                            chain[prev_word][words[i]] = 1
                        else:
                            chain[prev_word][words[i]] += 2 if prev_word == words[i] else 1
            prev_words = words
        with open(f"{self._path_name}/recommendation_data.json", "w") as ofile:
            dump(chain, ofile, separators=(",", ":"), indent=4)
        return processed_comments, rate

    # go through video and broadcast messages to each category thread
    def process_video(self, response, video_id=None):
        oauth_works = False
        categories = [category.get_type() for category in self._channel.get_categories()]
        while not oauth_works:
            try:
                video, comments = None, None
                # setup video and comments to parse
                if not video_id:
                    print("Video id NOT supplied")
                    for v, c in self._helix.user(self._channel.get_name()).videos(first=1).comments:
                        video = v
                        comments = c
                        video_id = v.id
                else:
                    print("Video id supplied")
                    for v, c in self._helix.videos([video_id]).comments:
                        video = v
                        comments = c
                print("Grabbed video and comments")
                processed_comments, rate = self.process_comments(comments)
                groups = []
                group = {}
                prev_comment_end = None
                print("+++++++++++++++++++++++++++++++++++++++++")
                print(f"Starting clip process for video {video_id} at {datetime.now()}")
                start = time.time()
                print(f"Total processed comments {len(processed_comments)}")
                # Get groups from processed comments
                for comment in processed_comments:
                    if self._processing_group and prev_comment_end and ((comment["created"] - prev_comment_end) >
                                                                        2 * rate):
                        self._end_time = prev_comment_end
                        if (self._end_time - self._start_time) > 0:
                            group["start"] = self._start_time - (self._end_time - self._start_time) / 2
                            group["end"] = self._end_time - (self._end_time - self._start_time) / 2
                            group["emoteRate"] = group["totalFrequency"] / (group["end"] - group["start"])
                            groups.append(group.copy())
                        self._processing_group = False
                        group.clear()
                    if not self._processing_group:
                        self._start_time = comment["created"]
                        self._processing_group = True
                        prev_comment_end = self._start_time
                        group["emoteSet"] = set(comment["emoteSet"])
                        group["emoteFrequency"] = {}
                        group["totalFrequency"] = 0
                        group["size"] = comment["size"]
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
                        if (comment["created"] - self._start_time) not in group["graph_x"]:
                            group["emoteSet"] = group["emoteSet"].union(set(comment["emoteSet"]))
                            for emote in comment["emoteSet"]:
                                if emote in group["emoteFrequency"]:
                                    group["emoteFrequency"][emote] += comment["emoteFrequency"][emote]
                                else:
                                    group["emoteFrequency"][emote] = comment["emoteFrequency"][emote]
                                group["totalFrequency"] += comment["emoteFrequency"][emote]
                            group["totalComments"] += 1
                            group["size"] += comment["size"]
                            group["comments"].append(comment["emoteFrequency"])
                            group["graph_x"].append(comment["created"] - self._start_time)
                            prev_comment_end = comment["created"]
                            group["text"] += " " + comment["text"]
                total_groups = len(groups)
                print(f"Total number of groups found before filter = {total_groups}")
                avg_emotes_per_group = sum(group["totalFrequency"] for group in groups) / total_groups
                avg_length_per_group = sum((group["end"] - group["start"]) for group in groups) / total_groups
                filtered_groups = list(filter(lambda current_group:
                                              current_group["totalFrequency"] > 1 * avg_emotes_per_group
                                              and (current_group["end"] - current_group["start"]) >
                                              1 * avg_length_per_group
                                              and current_group["emoteRate"] > 1 *
                                              avg_emotes_per_group/avg_length_per_group,
                                              groups))
                print(f"Total number of groups found after first filter = {len(filtered_groups)}")
                end = time.time()
                print("+++++++++++++++++++++++++++++++++++++++++")
                print(
                    f"Finished group processing for video {video_id} at {datetime.now()}. Process took {end - start} seconds")
                # Assign categories to groups
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(f"Starting to assign categories to processed groups for video {video_id} at {datetime.now()}")
                start = time.time()
                filtered_groups = sorted(filtered_groups, key=lambda current_group: current_group["start"])
                for group in filtered_groups:
                    group["similarities"] = {}
                    for category in categories:
                        group["graph_data"][category] = []
                        group["graph_y"] = {}
                    for category in categories:
                        emotes_in_category = self._channel.get_category(category).get_emotes()
                        intersection = group["emoteSet"].intersection(emotes_in_category)
                        union = group["emoteSet"].union(emotes_in_category)
                        similarity = len(intersection) / float(len(union))
                        weight = sum(group["emoteFrequency"][emote] for emote in group["emoteFrequency"].keys() if
                                     emote in emotes_in_category) / group["totalFrequency"]
                        if similarity * weight > 0:
                            group["similarities"][category] = round(similarity, 3)
                        for i, comment in enumerate(group["comments"]):
                            if category in group["graph_y"]:
                                group["graph_y"][category].append(
                                    sum(comment[emote] for emote in emotes_in_category.intersection(comment.keys())))
                            else:
                                group["graph_y"][category] = [
                                    sum(comment[emote] for emote in emotes_in_category.intersection(comment.keys()))]
                            total_emotes_in_category = sum(
                                comment[emote] for emote in emotes_in_category.intersection(comment.keys()))
                            if total_emotes_in_category > 0:
                                group["graph_data"][category].append(
                                    [category, group["graph_x"][i], total_emotes_in_category])
                    for category in categories:
                        if sum(group["graph_y"][category]) == 0:
                            group["graph_y"].pop(category)
                            group["graph_data"].pop(category)
                        elif sum(group["graph_y"][category]) / group["totalFrequency"] < .33:
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
                    group_time_data = []
                    for category in group["graph_data"].keys():
                        group_time_data.extend(group["graph_data"][category])
                    group["graph_data"] = group_time_data
                filtered_groups = list(filter(lambda current_group:
                                              len(current_group["similarities"]) > 0,
                                              filtered_groups))
                avg_group_size = sum(group["size"] for group in filtered_groups) / len(filtered_groups) if len(
                    filtered_groups) > 0 else 0
                print(f"Total number of groups found after second filter = {len(filtered_groups)}")
                end = time.time()
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(
                    f"Finished assigning categories to processed groups at {datetime.now()}. "
                    f"Process took {end - start} seconds")
                try:
                    decimal_index = video.created_at.index(".")
                except ValueError:
                    decimal_index = -1
                video_start_time = video.created_at[:decimal_index]
                data = {
                    "groups": filtered_groups,
                    "videoStart": video_start_time,
                    "avgSize": avg_group_size
                }
                oauth_works = True
                # save group data to json file
                if not os.path.exists(self._path_name):
                    os.makedirs(self._path_name)
                if not os.path.exists(f"{self._path_name}/{video_id}"):
                    os.makedirs(f"{self._path_name}/{video_id}")
                with open(f"{self._path_name}/{video_id}/data.json", "w+") as ofile:
                    dump(data, ofile, separators=(",", ":"), indent=4)
                with open(f"{self._path_name}/{video_id}/data.csv", "w+") as ofile:
                    ofile.write(f"text,{','.join(categories)}\n")
                    for group in filtered_groups:
                        labels = []
                        for category in categories:
                            label = "1" if category in group["similarities"] else "0"
                            labels.append(label)
                        ofile.write(f"{group['text']},{','.join(labels)}\n")
                response["status"] = 200
                response["msg"] = "Successfully clipped the video: " + video.title + " recorded on " + video.created_at[
                                                                                                       :10]
                response["id"] = video.id
                response["channelId"] = self._channel.get_id()
                response["data"] = data
            except requests.exceptions.HTTPError as http_err:
                status_code = http_err.response.status_code
                if status_code == 401:
                    print("401 Unauthorized error, refreshing access token. Helper")
                    self._clip_bot.refreshToken()
                    self._helix = self._clip_bot.get_helix()
                else:
                    print("Other error received:", status_code)
                    print("Removing", video_id, "from set of videos owned by", self._channel.get_id())
                    self._clip_bot._processing[self._channel.get_id()].remove(video_id)
                    response["status"] = status_code
                    response["msg"] = "Error when processing the video, please try again."
            except requests.exceptions.ConnectionError as http_err:
                print("Connection error:", http_err.args)
                print("Trying again")
                time.sleep(2)
            except Exception:
                print(sys.exc_info()[0])
                print("Removing", video_id, "from set of videos owned by", self._channel.get_id())
                self._clip_bot._processing[self._channel.get_id()].remove(video_id)
                response["status"] = 400
                response["msg"] = "Unable to process video, please try again."
            time.sleep(1)
