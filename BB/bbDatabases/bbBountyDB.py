from ..bbObjects import bbBounty

class bbBountyDB:
    # Dictionary of faction name : list of bounties
    # I would like instead of lists of bounties use dicts of criminal:bounty, but criminal is not hashable
    bounties = {}
    maxBountiesPerFaction = 0
    factions = []


    def __init__(self, factions, maxBountiesPerFaction):
        self.factions = factions
        for fac in factions:
            self.bounties[fac] = []
        self.maxBountiesPerFaction = maxBountiesPerFaction


    def addFaction(self, faction):
        if self.factionExists(faction):
            raise KeyError("Attempted to add a faction that already exists: " + faction)
        self.bounties[faction] = []


    def removeFaction(self, faction):
        if not self.factionExists(faction):
            raise KeyError("Unrecognised faction: " + faction)
        self.bounties.pop(faction)


    def clearBounties(self, faction=None):
        if faction is not None:
            if not self.factionExists(faction):
                raise KeyError("Unrecognised faction: " + faction)
            self.bounties[faction] = []
        else:
            for fac in self.getFactions():
                self.clearBounties(faction=fac)

    
    def getFactions(self):
        return self.factions


    def factionExists(self, faction):
        return faction in self.getFactions()

    
    def getFactionBounties(self, faction):
        return self.bounties[faction]


    def getFactionNumBounties(self, faction):
        return len(self.bounties[faction])


    def getBounty(self, name, faction=None):
        if faction is not None:
            for bounty in self.bounties[faction]:
                if bounty.criminal.isCalled(name):
                    return bounty
        else:
            for fac in self.getFactions():
                for bounty in self.bounties[fac]:
                    if bounty.criminal.isCalled(name):
                        return bounty
        raise KeyError("Bounty not found: " + name)


    def canMakeBounty(self):
        for fac in self.getFactions():
            if self.factionCanMakeBounty(fac):
                return True
        return False
    

    def factionCanMakeBounty(self, faction):
        return self.getFactionNumBounties(faction) < self.maxBountiesPerFaction


    def bountyNameExists(self, name, faction=None):
        try:
            self.getBounty(name, faction)
        except KeyError:
            return False
        return True

    
    def bountyObjExists(self, bounty):
        return bounty in self.bounties[bounty.faction]


    # def getBountyObjIndex(self, bounty):
    #     return self.bounties[bounty.faction].index(bounty)

    
    # def getBountyNameIndex(self, name, faction=None):
    #     return self.getBountyObjIndex(self.getBounty(name, faction=faction))


    def addBounty(self, bounty):
        if not self.factionCanMakeBounty(bounty.faction):
            raise OverflowError("Requested faction's bounty DB is full")
        if self.bountyObjExists(bounty):
            raise KeyError("Attempted to add a bounty that already exists: " + bounty.name)

        self.bounties[bounty.faction].append(bounty)

    
    def removeBountyName(self, name, faction=None):
        self.removeBountyObj(self.getBounty(name, faction=faction))


    def removeBountyObj(self, bounty):
        self.bounties[bounty.faction].remove(bounty)

    
    def toDict(self):
        data = {}
        for fac in self.getFactions():
            data[fac] = []
            for bounty in self.getFactionBounties(fac):
                data[fac].append(bounty.toDict())
        return data


    def hasBounties(self, faction=None):
        if faction is None:
            for fac in self.getFactions():
                if self.getFactionNumBounties(fac) != 0:
                    return True
        else:
            return self.getFactionNumBounties(faction) != 0
        return False 


    def __str__(self):
        return "<bbBountyDB: " + str(len(self.bounties)) + " factions>"

    
def fromDict(bountyDBDict, maxBountiesPerFaction, dbReload=False):
    newDB = bbBountyDB(bountyDBDict.keys(), maxBountiesPerFaction)
    for fac in bountyDBDict.keys():
        for bountyDict in bountyDBDict[fac]:
            newDB.addBounty(bbBounty.fromDict(bountyDict, dbReload=dbReload))
    return newDB
