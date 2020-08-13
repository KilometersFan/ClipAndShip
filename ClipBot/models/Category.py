import pprint
class Category(object):
    """Clip Category based on a set of emotes"""
    def __init__(self, type, channelId):
        self._type = type
        self._channelId = channelId
        self._emotes = set()
        self._timestamps = []

    # returns Twitch ID for the channel this category belongs to
    def getChannelId(self):
        return self._channelId

    # sets the type for this category
    def setType(self, newType):
        self._type = newType

    # get the type of this category
    def getType(self):
        return self._type

    # add emote to category
    def addEmote(self, emote):
        self._emotes.add(emote)
    
    # reset emotes and add the ones in emotes param
    def setEmotes(self, emotes):
        print("Set emotes!")
        self.clearEmotes()
        for emote in emotes:
            self.addEmote(emote)

    # erase all emotes in this category
    def clearEmotes(self):
        self._emotes.clear()

    # returns emotes in category either in sorted list or set form
    def getEmotes(self, isList=False):
        if not isList:
            return self._emotes
        emotes = sorted(list(self._emotes), key=str.lower)
        return emotes

    # returns whether or not emote param is in the emotes for this category
    def checkIfEmoteExists(self, emote):
        return True if emote in self._emotes else False

    # add timestamp to list of timestamps
    def addTimestamp(self, range):
        self._timestamps.append(range)

    # erases all timestamps
    def clearTimestamps(self):
        self._timestamps.clear()

    # returns sorted list of timestamps, ensures all timestamps are unique
    def getTimestamps(self):
        timestamps = set(self._timestamps)
        timestamps = list(timestamps)
        timestamps.sort()
        return timestamps