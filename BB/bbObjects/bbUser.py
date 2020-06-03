class bbUser:
    id = 0
    credits = 0
    lifetimeCredits = 0
    bountyCooldownEnd = -1
    systemsChecked = 0
    bountyWins = 0

    def __init__(self, id, credits=0, lifetimeCredits=0, bountyCooldownEnd=-1, systemsChecked=0, bountyWins=0):
        if type(id) != int:
            raise TypeError("id must be int, given " + str(type(id)))
        self.id = id
        self.credits = credits
        self.lifetimeCredits = lifetimeCredits
        self.bountyCooldownEnd = bountyCooldownEnd
        self.systemsChecked = systemsChecked
        self.bountyWins = bountyWins
    
    def resetUser(self):
        self.credits = 0
        self.lifetimeCredits = 0
        self.bountyCooldownEnd = -1
        self.systemsChecked = 0
        self.bountyWins = 0

    def toDictNoId(self):
        return {"credits":self.credits, "lifetimeCredits":self.lifetimeCredits,
                "bountyCooldownEnd":self.bountyCooldownEnd, "systemsChecked":self.systemsChecked,
                "bountyWins":self.bountyWins}

    def userDump(self):
        data = "bbUser #" + str(self.id) + ": "
        for att in [self.credits, self.lifetimeCredits, self.bountyCooldownEnd, self.systemsChecked, self.bountyWins]:
            data += str(att) + "/"
        return data[:-1]

    def __str__(self):
        return "<bbUser #" + str(self.id) + ">"


def fromDict(id, userDict):
    return bbUser(id, credits=userDict["credits"], lifetimeCredits=userDict["lifetimeCredits"],
                    bountyCooldownEnd=userDict["bountyCooldownEnd"], systemsChecked=userDict["systemsChecked"],
                    bountyWins=userDict["bountyWins"])
