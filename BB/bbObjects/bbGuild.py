class bbGuild:
    id = 0
    announceChannel = -1
    playChannel = -1


    def __init__(self, id, announceChannel=-1, playChannel=-1):
        if type(id) == float:
            id = int(id)
        elif type(id) != int:
            raise TypeError("id must be int, given " + str(type(id)))

        if type(announceChannel) == float:
            announceChannel = int(announceChannel)
        elif type(announceChannel) != int:
            raise TypeError("announceChannel must be int, given " + str(type(credits)))

        if type(playChannel) == float:
            playChannel = int(playChannel)
        elif type(playChannel) != int:
            raise TypeError("playChannel must be int, given " + str(type(lifetimeCredits)))


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
