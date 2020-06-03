from ..bbObjects import bbBounty

class bbBountyDB:
    # Dictionary of faction name : 
    #                               dict of bounty name : bounty object
    #                               was previously, and is still stored in JSON as, just a list
    bounties = {}
    maxBountiesPerFaction = 0


    def __init__(self, factions):
        for fac in factions:
            self.bounties[fac] = {}

    
    def getFactions(self):
        return self.bounties.keys()

    
    def getFactionBounties(self, faction):
        return self.bounties[faction]


    def getFactionNumBounties(self, faction):
        return len(self.bounties[faction])


    def getBounty(self, name, faction=None):
        if faction is not None:
            return self.bounties[faction][name]
        else:
            for fac in self.getFactions():
                if name in self.bounties[fac]:
                    return self.bounties[fac][name]
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
        return self.bountyNameExists(bounty.name, faction=bounty.faction)


    def addBounty(self, bounty):
        if not self.factionCanMakeBounty(bounty.faction):
            raise OverflowError("Requested faction's bounty DB is full")
        if self.bountyObjExists(bounty):
            raise KeyError("Attempted to add a bounty that already exists: " + bounty.name)

        self.bounties[bounty.faction][bounty.name] = bounty

    
    def removeBountyName(self, name, faction=None):
        self.removeBountyObj(self.getBounty(name, faction=faction))


    def removeBountyObj(self, bounty):
        self.bounties[bounty.faction].pop(bounty.name)

    
    def toDict(self):
        data = {}
        for fac in self.getFactions():
            data[fac] = []
            for bounty in self.getFactionBounties(fac):
                data[fac].append(bounty.toDict())
        return data


    def __str__(self):
        return "<bbBountyDB: " + str(len(self.bounties)) + " factions>"

    
def fromDict(bountyDBDict):
    newDB = bbBountyDB(bountyDBDict.keys())
    for fac in bountyDBDict.keys():
        for bountyDict in bountyDBDict[fac]:
            newDB.addBounty(bbBounty.fromDict(bountyDict))
    return newDB
