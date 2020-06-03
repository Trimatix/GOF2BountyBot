class bbGuild:
    id = 0
    announceChannel = -1
    playChannel = -1


    def __init__(self, id, announceChannel=-1, playChannel=-1):
        self.id = id
        self.announceChannel = announceChannel
        self.playChannel = playChannel


    def getAnnounceChannelId(self):
        if not self.hasAnnounceChannel():
            raise ValueError("This guild has no announce channel set")
        return self.announceChannel


    def getPlayChannelId(self):
        if not self.hasPlayChannel():
            raise ValueError("This guild has no play channel set")
        return self.playChannel


    def setAnnounceChannelId(self, announceChannelId):
        self.announceChannel = announceChannelId


    def setPlayChannelId(self, playChannelId):
        self.playChannel = playChannelId
    

    def hasAnnounceChannel(self):
        return self.announceChannel != -1


    def hasPlayChannel(self):
        return self.playChannel != -1


    def toDictNoId(self):
        return {"announceChannel":self.announceChannel, "playChannel":self.playChannel}


def fromDict(id, guildDict):
    return bbGuild(id, announceChannel=guildDict["announceChannel"], playChannel=guildDict["playChannel"])
