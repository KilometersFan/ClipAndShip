import eel
import os
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
from multiprocessing import Process, Manager
from models.ClipBot import ClipBot
from models.Channel import Channel

bot = None
videoThreads = {}
notification = False
path = os.getcwd()
print(path)

@eel.expose
def initClipBot():
	global bot
	bot = ClipBot()
	bot.setupConfig()
	bot.setupChannels()

@eel.expose
def validBot():
	global bot
	return True if bot.hasChannels and bot.oauthConfigured else False

@eel.expose
def checkCredentials():
	cfg = configparser.ConfigParser()
	cfg.read("config/config.ini")
	if cfg:
		if cfg.has_section("settings"):
			if cfg.has_option("settings", "client_id") and cfg.has_option("settings", "secret"):
				return True
		else:
			return False
	else:
		return False

@eel.expose
def enterCredentials(client_id, client_secret):
	if not os.path.exists(f"{path}/config/"):
		os.makedirs(f"{path}/config/")
	cfg = configparser.ConfigParser()
	cfg["settings"] = {}
	cfg["settings"]["client_id"] = client_id
	cfg["settings"]["secret"] = client_secret
	with open("config/config.ini", "w") as configFile:
		cfg.write(configFile)

@eel.expose
def addChannel(id):
	if not os.path.exists(f"{path}/config"):
		os.makedirs(f"{path}/config")
	try:
		cfg = configparser.RawConfigParser()
		cfg.read(f"{path}/config/channels.ini")
		global bot
		if bot.getChannel(int(id)):
			print("Channel already exists.")
			raise Exception("Channel already exists.")
		newChannel = Channel(int(id), bot.getHelix(), bot)
		bot.addChannel(newChannel)
		cfg.add_section(id)
		with open(f"{path}/config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		traceback.print_exc()
		return e.args

@eel.expose
def removeChannels(channels):
	if not os.path.exists(f"{path}/config/"):
		return "Config file not found."
	try:
		cfg = configparser.RawConfigParser()
		cfg.read(f"{path}/config/channels.ini")
		global bot
		for channel in channels:
			cfg.remove_section(channel)
			bot.removeChannel(int(channel))
		with open(f"{path}/config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		print(e.message)
		return e.args

@eel.expose
def getChannels():
	global bot
	return bot.getChannels()

@eel.expose
def getChannel(id, info=True):
	global bot
	return bot.getChannel(id, info)

@eel.expose
def getChannelEmotes(id):
	global bot
	return bot.getChannel(id, False).getEmotes()

@eel.expose
def searchChannel(channel_name):
	global bot
	return bot.searchForChannel(channel_name)


@eel.expose
def addCategory(id, type, emotes):
	if not os.path.exists("config"):
		return "Can't find config file."
	try:
		type = type.lower()
		global bot
		channel = bot.getChannel(id, False)
		channel.addCategory(type, True, id)
		channel.addEmotesToCategory(type, emotes)
		cfg = configparser.RawConfigParser()
		cfg.read(f"{path}/config/channels.ini")
		cfg.set(str(id), type, ",".join(emotes))
		with open(f"{path}/config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		return e.args

@eel.expose
def editCategory(id, type, emotes_add, emotes_left):
	if not os.path.exists(f"{path}/config"):
		return "Can't find config file."
	try:
		cfg = configparser.RawConfigParser()
		cfg.read(f"{path}/config/channels.ini")
		type = type.lower()
		global bot
		channel = bot.getChannel(id, False)
		emotesToAdd = set(emotes_add)
		emotesLeft = set(emotes_left)
		print("Emotes to Add", emotesToAdd)
		print("Emotes Left to set", emotesLeft)
		channel.rmvEmotesFromCategory(type, set(emotes_left))
		channel.addEmotesToCategory(type, set(emotes_add))
		cfg.set(str(id), type, ",".join(list(emotesToAdd.union(emotesLeft))))
		with open(f"{path}/config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		return e.args

@eel.expose
def deleteCategory(id, types):
	if not os.path.exists(f"{path}/config"):
		return 
	try:
		cfg = configparser.RawConfigParser()
		cfg.read(f"{path}/config/channels.ini")
		global bot
		channel = bot.getChannel(id, False)
		for type in types:
			type = type.lower()
			channel.removeCategory(type)
			cfg.remove_option(str(id), type)
		with open(f"{path}/config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		return e.args

@eel.expose
def getCategories(channel_id):
	global bot
	channel = bot.getChannel(channel_id, False)
	categories = channel.getCategories()
	result = [{"type": category.getType(), "emotes": category.getEmotes(True)} for category in categories]
	return result

@eel.expose
def getRecommendedEmotes(channel_id, category_type, isList=False):
	if os.path.exists(f"{path}/data/channels/{channel_id}/recommendation_data.json"):
		with open(f"data/channels/{channel_id}/recommendation_data.json") as ifile:
			channel = getChannel(channel_id, False)
			category = category_type if isList else channel.getCategory(category_type)
			chain = json.load(ifile)
			emotesInCategory = set(category_type) if isList else category.getEmotes(True)
			top5Emotes = set()
			chainIndices = {emote: 0 for emote in emotesInCategory}
			emoteFullyChecked = {emote: False for emote in emotesInCategory}
			done = False
			start = time.time()
			print(f"Beginning process of generating recommended emotes at {start}")
			for emote in emotesInCategory:
				chain[emote] = [(k,v/float(chain["totalEmotes"])) for k,v in sorted(chain[emote].items(), key=lambda item: item[1]/chain["totalEmotes"], reverse=True)]
			while len(top5Emotes) < 5 and not done:
				candidateEmote = None
				candidatePercentage = 0
				parentEmote = None
				for emote in emotesInCategory:
					if all(isChecked == True for isChecked in emoteFullyChecked.values()):
						done = True
						break
					while chainIndices[emote] < len(chain[emote]) and chain[emote][chainIndices[emote]][0] in top5Emotes:
						chainIndices[emote] += 1
					if chainIndices[emote] >= len(chain[emote]):
						emoteFullyChecked[emote] = True
						continue
					while chain[emote][chainIndices[emote]][0] in emotesInCategory:
						chainIndices[emote] += 1
					if chain[emote][chainIndices[emote]][1] > candidatePercentage \
						and chain[emote][chainIndices[emote]][0] not in top5Emotes:
						candidatePercentage = chain[emote][chainIndices[emote]][1]
						candidateEmote = chain[emote][chainIndices[emote]][0]
						parentEmote = emote
				if parentEmote is not None:
					chainIndices[parentEmote] += 1
				if candidateEmote is not None:
					top5Emotes.add(candidateEmote)
			end = time.time()
			print(f"Finished process of generating recommended emotes at {end}. Process took {end - start}s")
			print(top5Emotes)
			return list(top5Emotes)
	else:
		return []

@eel.expose
def getVideos(channel_id, videos = None):
	global bot
	channel = bot.getChannel(channel_id, False)
	return channel.getVideos(videos)

@eel.expose
def getUserVideos(channel_id=None):
	if channel_id:
		try:
			print(f"data/channels/{channel_id}")
			if os.path.exists(f"data/channels/{channel_id}"):
				video_ids =[ int(f.name) for f in os.scandir(f"{path}/data/channels/{channel_id}") if f.is_dir() ]
				print(video_ids)
				return video_ids
			else:
				print("Channel folder not found")
				return []
		except Exception as e:
			print(e.args)
			return []
	else:
		try:
			if os.path.exists("data/channels/"):
				channel_ids =[ f.name for f in os.scandir("data/channels/") if f.is_dir() ]
				response = {}
				for channel_id in channel_ids:
					response[channel_id] = [ int(f.name) for f in os.scandir(f"{path}/data/channels/{channel_id}") if f.is_dir() ]
				return response
			else:
				print("Channel folder not found")
				return []
		except Exception as e:
			print(e.args)
			return []
		
@eel.expose
def removeVideo(channel_id, video_id):
	video_id.strip()
	try:
		if os.path.exists(f"{path}/data/channels/{channel_id}/{video_id}"):
			shutil.rmtree(f"{path}/data/channels/{channel_id}/{video_id}")
			return {"success" : "Video was successfully deleted"}
		else:
			print("Video file not found")
			return {"error" : "Video file not found"}
	except Exception as e:
		print(e.args)
		return {"error" : e.args}

@eel.expose
def clipVideo(channel_id, id=None):
	videoThread = threading.Thread(target=clipVideoHelper, args=(channel_id, id), daemon=True)
	videoThread.start()

def clipVideoHelper(channel_id, id=None):
	bot.clipVideo(channel_id, id)
	print("###########################")
	global notification
	notification = True
	eel.videoHandler(notification)

@eel.expose
def getVideoResults(channel_id, video_id):
	if not video_id or not channel_id:
		return {"error" : "Unable to process request"}
	global bot
	channel = bot.getChannel(channel_id, False)
	if not os.path.exists(f"{channel._pathName}/{video_id}"):
		return {"error" : "Video was not processed"}
	results = {}
	for category in channel.getCategories():
		try:
			if os.path.exists(f"{channel._pathName}/{video_id}/data.json") :
				with open(f"{channel._pathName}/{video_id}/data.json") as ifile:
					results = json.load(ifile)
			else:
				results[category.getType()] = {}
		except Exception as e:
			print(e.args)
			print("Exception!")
			return {"error": "Unable to read file"}
	return results

@eel.expose
def getProcessingVideos():
	global bot
	return bot.getProcessingVideos()

@eel.expose
def csvExport(video_id, data):
	print(data)
	with open(f"{path}/web/exported/{video_id}_groups.csv", "w") as ofile:
		for group in data:
			line = f"{group['start']},{group['end']},{group['length']},{group['similarities']}\n"
			print(line)
			ofile.write(line)
	return {"status": 200}

@eel.expose
def getGraph(graph_data):
	df = pd.DataFrame(graph_data, columns=["category", "time", "instances"])
	fig = px.scatter(df, x="time", y="instances", color="category",
					 labels=dict(time="Time (s)", instances="Category emote usage per comment", category="Category"),
					 width=450, height=350)
	fig.update_layout(
		margin=dict(l=0,r=0,t=0,b=0)
	)
	img_bytes = fig.to_image(format="png")
	return base64.encodebytes(img_bytes).decode("utf-8").replace("\n", "")

@eel.expose
def resetNotificationCount():
	global notification
	notification = False
	eel.videoHandler(notification)

@eel.expose
def downloadClip(video_id, start, end):
	if end <= start:
		print("Invalid clip params.")
		return {"status": "400"}
	download_thread = threading.Thread(target=clipVideoHelper, args=(video_id, start, end), daemon=True)
	download_thread.start()


def download_clip_helper(video_id, start, end):
	manager = Manager()
	response = manager.dict()
	p = Process(target=invoke_twitchdl, args=(response, video_id, start, end))
	p.start()
	p.join()
	return response


def invoke_twitchdl(response, video_id, start, end):
	return_val = subprocess.run(["python3", "twitchdl/console.py", "download", video_id,
								 "--overwrite", "--format", "mp4", "--start", start, "--end", end],
								stderr=subprocess.STDOUT, universal_newlines=True)
	print(return_val.returncode)
	if return_val.returncode != 0:
		print(f"Download failed for clip at {start} to {end} for video {video_id}")
		response["status"] = 500
	else:
		print(f"Successfully downloaded clip at {start} to {end} for video {video_id}")
		response["status"] = 200


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