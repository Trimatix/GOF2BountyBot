class bbGuild:
    id = 0
    announceChannel = -1
    playChannel = -1

    def __init__(self, id, announceChannel=-1, playChannel=-1):
        self.id = id
        self.announceChannel = announceChannel
        self.playChannel = playChannel


    def getAnnounceChannelId(self):
        return self.announceChannel


    def getPlayChannelId(self):
        return self.playChannel


    def setAnnounceChannelId(self, announceChannelId):
        self.announceChannel = announceChannelId


    def setPlayChannelId(self, playChannelId):
        self.playChannel = playChannelId
    

    def toDictNoId(self):
        return {"announceChannel":self.announceChannel, "playChannel":self.playChannel}


def fromDict(id, guildDict):
    return bbGuild(id, announceChannel=guildDict["announceChannel"], playChannel=guildDict["playChannel"])
