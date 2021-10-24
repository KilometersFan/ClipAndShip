class Category(object):
    """Clip Category based on a set of emotes"""
    def __init__(self, name, channel_id):
        self._name = name
        self._channel_id = channel_id
        self._emotes = set()
        self._timestamps = []

    # returns Twitch ID for the channel this category belongs to
    def get_channel_id(self):
        return self._channel_id

    # get the type of this category
    def get_type(self):
        return self._name

    # sets the type for this category
    def set_type(self, new_type):
        self._name = new_type

    # add emote to category
    def add_emote(self, emote):
        self._emotes.add(emote.lower())

    # erase all emotes in this category
    def clear_emotes(self):
        self._emotes.clear()

    # returns emotes in category either in sorted list or set form
    def get_emotes(self, is_list=False):
        if not is_list:
            return self._emotes
        return sorted(list(self._emotes), key=str.lower)

    # reset emotes and add the ones in emotes param
    def set_emotes(self, emotes):
        self.clear_emotes()
        for emote in emotes:
            self.add_emote(emote)
