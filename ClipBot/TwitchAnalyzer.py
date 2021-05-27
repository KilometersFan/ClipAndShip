import eel
import os
import shutil
import configparser
from requests.exceptions import HTTPError
import traceback
import models.ClipBot as ClipBot
import models.Channel as Channel
import threading

bot = None
videoThreads = {}

@eel.expose
def initClipBot():
	global bot
	bot = ClipBot.ClipBot()
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
	if not os.path.exists("config"):
		os.makedirs("config")
	cfg = configparser.ConfigParser()
	cfg["settings"] = {}
	cfg["settings"]["client_id"] = client_id
	cfg["settings"]["secret"] = client_secret
	with open("config/config.ini", "w") as configFile:
		cfg.write(configFile)

@eel.expose
def addChannel(id):
	if not os.path.exists("config"):
		os.makedirs("config")
	try:
		cfg = configparser.RawConfigParser()
		cfg.read("config/channels.ini")
		global bot
		if bot.getChannel(int(id)):
			print("Channel already exists.")
			raise Exception("Channel already exists.")
		newChannel = Channel.Channel(int(id), bot.getHelix(), bot)
		bot.addChannel(newChannel)
		cfg.add_section(id)
		with open("config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		traceback.print_exc()
		return e.args

@eel.expose
def removeChannels(channels):
	if not os.path.exists("config"):
		return "Config file not found."
	try:
		cfg = configparser.RawConfigParser()
		cfg.read("config/channels.ini")
		global bot
		for channel in channels:
			cfg.remove_section(channel)
			bot.removeChannel(int(channel))
		with open("config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		return e.args


@eel.expose
def getChannels():
	global bot
	return bot.getChannels()

@eel.expose
def getChannel(id):
	global bot
	return bot.getChannel(id)

@eel.expose
def getChannelEmotes(id):
	global bot
	return bot.getChannel(id, False).getEmotes()

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
		cfg.read("config/channels.ini")
		cfg.set(str(id), type, ",".join(emotes))
		with open("config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		return e.args

@eel.expose
def editCategory(id, type, emotes_add, emotes_left):
	if not os.path.exists("config"):
		return "Can't find config file."
	try:
		cfg = configparser.RawConfigParser()
		cfg.read("config/channels.ini")
		type = type.lower()
		global bot
		channel = bot.getChannel(id, False)
		print("Emotes to Add", emotes_add)
		print("Emotes Left to set", emotes_left)
		channel.rmvEmotesFromCategory(type, emotes_left)
		channel.addEmotesToCategory(type, emotes_add)
		cfg.set(str(id), type, ",".join(emotes_add + emotes_left))
		with open("config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		return e.args

@eel.expose
def deleteCategory(id, types):
	if not os.path.exists("config"):
		return 
	try:
		cfg = configparser.RawConfigParser()
		cfg.read("config/channels.ini")
		global bot
		channel = bot.getChannel(id, False)
		for type in types:
			type = type.lower()
			channel.removeCategory(type)
			cfg.remove_option(str(id), type)
		with open("config/channels.ini", "w") as configFile:
			cfg.write(configFile)
		return ""
	except Exception as e:
		return e.args

@eel.expose
def getCategories(channel):
	global bot
	channel = bot.getChannel(channel, False)
	categories = channel.getCategories()
	result = []
	for category in categories:
		result.append({"type" :category.getType(), "emotes" : category.getEmotes(True)})
	return result

@eel.expose
def searchChannel(channel_name):
	global bot
	return bot.searchForChannel(channel_name)

@eel.expose
def getVideos(channel_id, videos = None):
	global bot
	channel = bot.getChannel(channel_id, False)
	return channel.getVideos(videos)

@eel.expose
def getUserVideos(channel_name):
	channel_name.strip()
	try:
		if os.path.exists("data/channels/" + channel_name):
			video_ids =[ int(f.name) for f in os.scandir("data/channels/" + channel_name) if f.is_dir() ]
			return video_ids
		else:
			print("Channel folder not found")
			return []
	except Exception as e:
		print(e.args)
		return []
		
@eel.expose
def removeVideo(channel_name, video_id):
	video_id.strip()
	try:
		if os.path.exists("data/channels/" + channel_name + "/" + video_id):
			shutil.rmtree("data/channels/" + channel_name + "/" + video_id)
			return {"success" : "Video was successfully deleted"}
		else:
			print("Video file not found")
			return {"error" : "Video file not found"}
	except Exception as e:
		print(e.args)
		return {"error" : e.args}

@eel.expose
def clipVideo(channel_id, id=None):
	videoThread = threading.Thread(target=clipVideoHelper, args=(channel_id,id,), daemon=True)
	videoThreads[id] = videoThread
	videoThread.start()

def clipVideoHelper(channel_id, id=None):
	global bot
	response = bot.clipVideo(channel_id, id)
	eel.videoHandler(response)

@eel.expose
def getVideoResults(channel_id, video_id):
	if not video_id or not channel_id:
		return {"error" : "Unable to process request"}
	global bot
	channel = bot.getChannel(channel_id, False)
	if not os.path.exists(channel._pathName + "/" + video_id):
		return {"error" : "Video was not processed"}
	results = {}
	for category in channel.getCategories():
		entries = []
		try:
			if(os.path.exists(channel._pathName + "/" + video_id + "/" + category.getType() + "/timestamps.txt")):
				with open(channel._pathName + "/" + video_id + "/" + category.getType() + "/timestamps.txt") as ifile:
					timestamps = ifile.readlines()
					for timestamp in timestamps:
						start,end = timestamp.strip().split("-")
						entry = {"start": start, "end": end}
						entries.append(entry)
					results[category.getType()] = entries
			else:
				results[category.getType()] = {}
		except Exception as e:
			print(e.args)
			print("Exception!")
			return {"error" : "Unable to read file"}
	return results

@eel.expose
def getProcessingVideos():
	global bot
	return bot.getProcessingVideos()

@eel.expose
def cancelVideo(channel_id, video_id):
	global bot
	try:
		bot.cancelVideo(channel_id, video_id)
		return {"status": 200}
	except Exception as e:
		print("Unable to cancel video")
		print(e.args)
		return {"status": 400}

def get_preferred_mode():
	import eel.chrome
	import eel.edge

	if eel.chrome.find_path():
		return 'chrome'
	if eel.edge.find_path():
		return 'edge'

	return 'default'

if __name__ == "__main__":
	eel.init("web")
	try:
		eel.start("templates/index.html", jinja_templates="templates", mode=get_preferred_mode())
	except (SystemExit, MemoryError, KeyboardInterrupt) as e:
		pass
