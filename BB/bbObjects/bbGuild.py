from . import bbShop

class bbGuild:
    id = 0
    announceChannel = -1
    playChannel = -1
    shop = None


    def __init__(self, id, announceChannel=-1, playChannel=-1, shop=None):
        if type(id) == float:
            id = int(id)
        elif type(id) != int:
            raise TypeError("id must be int, given " + str(type(id)))

        if type(announceChannel) == float:
            announceChannel = int(announceChannel)
        elif type(announceChannel) != int:
            raise TypeError("announceChannel must be int, given " + str(type(announceChannel)))

        if type(playChannel) == float:
            playChannel = int(playChannel)
        elif type(playChannel) != int:
            raise TypeError("playChannel must be int, given " + str(type(playChannel)))
        
        if shop is not None and type(shop) != bbShop.bbShop:
            raise TypeError("shop must be bbShop, given " + str(type(shop)))

        self.id = id
        self.announceChannel = announceChannel
        self.playChannel = playChannel

        self.shop = bbShop.bbShop() if shop is None else shop


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
        return {"announceChannel":self.announceChannel, "playChannel":self.playChannel
        # Shop saving disabled for now, it's not super important.
                # , "shop": self.shop.toDict()
                }


def fromDict(id, guildDict):
    return bbGuild(id, announceChannel=guildDict["announceChannel"], playChannel=guildDict["playChannel"], shop=bbShop.fromDict(guildDict["shop"]) if "shop" in guildDict else bbShop.bbShop())
