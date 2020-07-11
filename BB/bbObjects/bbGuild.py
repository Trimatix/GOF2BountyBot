from . import bbShop

class bbGuild:
    def __init__(self, id, announceChannel=-1, playChannel=-1, shop=None, bountyNotifyRoleId=-1, shopRefreshRoleId=-1, systemUpdatesMajorRoleId=-1, systemUpdatesMinorRoleId=-1, systemMiscRoleId=-1, bountyBoardChannel=-1):
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

        self.bountyNotifyRoleId = bountyNotifyRoleId
        self.shopRefreshRoleId = shopRefreshRoleId
        self.systemUpdatesMajorRoleId = systemUpdatesMajorRoleId
        self.systemUpdatesMinorRoleId = systemUpdatesMinorRoleId
        self.systemMiscRoleId = systemMiscRoleId
        
        if bountyBoardChannel == -1:
            self.hasBountyBoardChannel = False
            self.bountyBoardChannel = -1
        else:
            self.bountyBoardChannel = bountyBoardChannel
            self.hasBountyBoardChannel = True


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



    def hasBountyNotifyRoleId(self):
        return self.bountyNotifyRoleId != -1

    
    def getBountyNotifyRoleId(self):
        return self.bountyNotifyRoleId

    
    def setBountyNotifyRoleId(self, newId):
        self.bountyNotifyRoleId = newId


    def removeBountyNotifyRoleId(self):
        self.bountyNotifyRoleId = -1

    

    def hasShopRefreshRoleId(self):
        return self.shopRefreshRoleId != -1

    
    def getShopRefreshRoleId(self):
        return self.shopRefreshRoleId

    
    def setShopRefreshRoleId(self, newId):
        self.shopRefreshRoleId = newId


    def removeShopRefreshRoleId(self):
        self.shopRefreshRoleId = -1



    def hasSystemUpdatesMajorRoleId(self):
        return self.systemUpdatesMajorRoleId != -1

    
    def getSystemUpdatesMajorRoleId(self):
        return self.systemUpdatesMajorRoleId

    
    def setSystemUpdatesMajorRoleId(self, newId):
        self.bountyNotifyRoleId = systemUpdatesMajorRoleId


    def removeSystemUpdatesMajorRoleId(self):
        self.systemUpdatesMajorRoleId = -1



    def hasSystemUpdatesMinorRoleId(self):
        return self.systemUpdatesMinorRoleId != -1

    
    def getSystemUpdatesMinorRoleId(self):
        return self.systemUpdatesMinorRoleId

    
    def setSystemUpdatesMinorRoleId(self, newId):
        self.bountyNotifyRoleId = systemUpdatesMinorRoleId


    def removeSystemUpdatesMinorRoleId(self):
        self.systemUpdatesMinorRoleId = -1



    def hasSystemMiscRoleId(self):
        return self.systemMiscRoleId != -1

    
    def getSystemMiscRoleId(self):
        return self.systemMiscRoleId

    
    def setSystemMiscRoleId(self, newId):
        self.systemMiscRoleId = newId


    def removeSystemMiscRoleId(self):
        self.systemMiscRoleId = -1



    
    def addBountyBoardChannel(self, msgID):
        if self.hasBountyBoard:
            raise RuntimeError("Attempted to assign a bountyboard channel for guild " + str(self.id) + " but one is already assigned")
        self.bountyBoardChannel = msgID
        self.hasBountyBoardChannel = True

    
    def removeBountyBoardChannel(self):
        if not self.hasBountyBoard:
            raise RuntimeError("Attempted to remove a bountyboard channel for guild " + str(self.id) + " but none is assigned")
        self.bountyBoardChannel = -1
        self.hasBountyBoardChannel = False


    def toDictNoId(self):
        return {"announceChannel":self.announceChannel, "playChannel":self.playChannel, "bountyNotifyRoleId":self.bountyNotifyRoleId, "bountyBoardChannel": self.bountyBoardChannel,
                "shopRefreshRoleId": self.shopRefreshRoleId,
                "systemUpdatesMajorRoleId": self.systemUpdatesMajorRoleId,
                "systemUpdatesMinorRoleId": self.systemUpdatesMinorRoleId,
                "systemMiscRoleId": self.systemMiscRoleId
        # Shop saving disabled for now, it's not super important.
                # , "shop": self.shop.toDict()
                }


def fromDict(id, guildDict):
    return bbGuild(id, announceChannel=guildDict["announceChannel"], playChannel=guildDict["playChannel"], shop=bbShop.fromDict(guildDict["shop"]) if "shop" in guildDict else bbShop.bbShop(), bountyNotifyRoleId=guildDict["bountyNotifyRoleId"] if "bountyNotifyRoleId" in guildDict else -1, bountyBoardChannel=guildDict["bountyBoardChannel"] if "bountyBoardChannel" in guildDict else -1,
                    shopRefreshRoleId=guildDict["shopRefreshRoleId"] if "shopRefreshRoleId" in guildDict else -1,
                    systemUpdatesMajorRoleId=guildDict["systemUpdatesMajorRoleId"] if "systemUpdatesMajorRoleId" in guildDict else -1,
                    systemUpdatesMinorRoleId=guildDict["systemUpdatesMinorRoleId"] if "systemUpdatesMinorRoleId" in guildDict else -1,
                    systemMiscRoleId=guildDict["systemMiscRoleId"] if "systemMiscRoleId" in guildDict else -1)
