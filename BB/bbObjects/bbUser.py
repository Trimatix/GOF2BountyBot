from .items import bbShip, bbModule, bbWeapon
from ..bbConfig import bbConfig


defaultShipLoadoutDict = {"name": "Betty", "manufacturer": "midorian", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 3, "armour": 95, "cargo": 25, "numSecondaries": 1, "handling": 120, "value": 16038, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Betty", "builtIn":False,
                        "weapons":[{"name": "Nirai Impulse EX 1", "builtIn": True}, {"name": "Micro Gun MK I", "builtIn": True}],
                        "modules":[{"name": "E2 Exoclad", "builtIn": True}, {"name": "E2 Exoclad", "builtIn": True}, {"name": "E2 Exoclad", "builtIn": True}]}

defaultUserDict = {"credits":0, "bountyCooldownEnd":0, "lifetimeCredits":0, "systemsChecked":0, "bountyWins":0, "activeShip": defaultShipLoadoutDict}


class bbUser:
    id = 0
    credits = 0
    lifetimeCredits = 0
    bountyCooldownEnd = -1
    systemsChecked = 0
    bountyWins = 0

    activeShip = None
    inactiveShips = []
    inactiveModules = []
    inactiveWeapons = []
    inactiveTurrets = []
    

    def __init__(self, id, credits=0, lifetimeCredits=0, bountyCooldownEnd=-1, systemsChecked=0, bountyWins=0, activeShip=None, inactiveShips=[], inactiveModules=[], inactiveWeapons=[], inactiveTurrets=[]):
        if type(id) == float:
            id = int(id)
        elif type(id) != int:
            raise TypeError("id must be int, given " + str(type(id)))

        if type(credits) == float:
            credits = int(credits)
        elif type(credits) != int:
            raise TypeError("credits must be int, given " + str(type(credits)))

        if type(lifetimeCredits) == float:
            lifetimeCredits = int(lifetimeCredits)
        elif type(lifetimeCredits) != int:
            raise TypeError("lifetimeCredits must be int, given " + str(type(lifetimeCredits)))

        if type(bountyCooldownEnd) == float:
            bountyCooldownEnd = int(bountyCooldownEnd)
        elif type(bountyCooldownEnd) != int:
            raise TypeError("bountyCooldownEnd must be int, given " + str(type(bountyCooldownEnd)))

        if type(systemsChecked) == float:
            systemsChecked = int(systemsChecked)
        elif type(systemsChecked) != int:
            raise TypeError("systemsChecked must be int, given " + str(type(systemsChecked)))

        if type(bountyWins) == float:
            bountyWins = int(bountyWins)
        elif type(bountyWins) != int:
            raise TypeError("bountyWins must be int, given " + str(type(bountyWins)))

        self.id = id
        self.credits = credits
        self.lifetimeCredits = lifetimeCredits
        self.bountyCooldownEnd = bountyCooldownEnd
        self.systemsChecked = systemsChecked
        self.bountyWins = bountyWins

        self.activeShip = activeShip
        self.inactiveShips = inactiveShips
        self.inactiveModules = inactiveModules
        self.inactiveWeapons = inactiveWeapons
        self.inactiveTurrets = inactiveTurrets
    

    def resetUser(self):
        self.credits = 0
        self.lifetimeCredits = 0
        self.bountyCooldownEnd = -1
        self.systemsChecked = 0
        self.bountyWins = 0
        self.activeShip = bbShip.fromDict(defaultShipLoadoutDict)
        self.inactiveModules = []
        self.inactiveShips = []
        self.inactiveWeapons = []
        self.inactiveTurrets = []


    def numInventoryPages(self, item):
        if item not in bbConfig.validItemNames:
            raise ValueError("Requested an invalid item name: " + item)

        numWeapons = len(self.inactiveWeapons)
        numModules = len(self.inactiveModules)
        numTurrets = len(self.inactiveTurrets)
        numShips = len(self.inactiveShips)

        itemsNum = 0
        maxPerPage = 0

        if item == "all":
            itemsNum = numWeapons + numModules + numTurrets + numShips
            maxPerPage = bbConfig.maxItemsPerHangarPageAll * 3

        else:
            maxPerPage = bbConfig.maxItemsPerHangarPageIndividual
            if item == "module":
                itemsNum = numModules
            elif item == "weapon":
                itemsNum = numWeapons
            elif item == "turret":
                itemsNum = numTurrets
            elif item == "ship":
                itemsNum = numShips
            else:
                raise NotImplementedError("Valid but unsupported item name: " + item)

        return 1 if itemsNum == 0 else (int(itemsNum/maxPerPage) + (0 if itemsNum % maxPerPage == 0 else 1))


    def numEmptySlotsOnInventoryPage(self, item, pageNum, maxPerPage):
        if item not in bbConfig.validItemNames:
            raise ValueError("Requested an invalid item name: " + item)
        if pageNum < self.numInventoryPages(item):
            return 0
        elif item == "ship":
            return maxPerPage - (len(self.inactiveShips) % maxPerPage)
        elif item == "weapon":
            return maxPerPage - (len(self.inactiveWeapons) % maxPerPage)
        elif item == "module":
            return maxPerPage - (len(self.inactiveModules) % maxPerPage)
        elif item == "turret":
            return maxPerPage - (len(self.inactiveTurrets) % maxPerPage)
        else:
            raise NotImplementedError("Valid but unsupported item name: " + item)


    def toDictNoId(self):
        inactiveShipsDict = []
        for ship in self.inactiveShips:
            inactiveShipsDict.append(ship.toDict())

        inactiveModulesDict = []
        for module in self.inactiveModules:
            inactiveModulesDict.append(module.toDict())

        inactiveWeaponsDict = []
        for weapon in self.inactiveWeapons:
            inactiveWeaponsDict.append(weapon.toDict())

        inactiveTurretsDict = []
        for turret in self.inactiveTurrets:
            inactiveTurretsDict.append(turret.toDict())

        return {"credits":self.credits, "lifetimeCredits":self.lifetimeCredits,
                "bountyCooldownEnd":self.bountyCooldownEnd, "systemsChecked":self.systemsChecked,
                "bountyWins":self.bountyWins, "activeShip": self.activeShip.toDict(), "inactiveShips":inactiveShipsDict,
                "inactiveModules":inactiveModulesDict, "inactiveWeapons":inactiveWeaponsDict, "inactiveTurrets": inactiveTurretsDict}


    def userDump(self):
        data = "bbUser #" + str(self.id) + ": "
        for att in [self.credits, self.lifetimeCredits, self.bountyCooldownEnd, self.systemsChecked, self.bountyWins]:
            data += str(att) + "/"
        return data[:-1]


    def getStatByName(self, stat):
        if stat == "id":
            return self.id
        elif stat == "credits":
            return self.credits
        elif stat == "lifetimeCredits":
            return self.lifetimeCredits
        elif stat == "bountyCooldownEnd":
            return self.bountyCooldownEnd
        elif stat == "systemsChecked":
            return self.systemsChecked
        elif stat == "bountyWins":
            return self.bountyWins


    def __str__(self):
        return "<bbUser #" + str(self.id) + ">"


def fromDict(id, userDict):
    activeShip = bbShip.fromDict(userDict["activeShip"])

    inactiveShips = []
    if "inactiveShips" in userDict:
        for ship in userDict["inactiveShips"]:
            inactiveShips.append(bbShip.fromDict(ship))

    inactiveWeapons = []
    if "inactiveWeapons" in userDict:
        for weapon in userDict["inactiveWeapons"]:
            inactiveWeapons.append(bbShip.fromDict(weapon))

    inactiveModules = []
    if "inactiveModules" in userDict:
        for module in userDict["inactiveModules"]:
            inactiveModules.append(bbShip.fromDict(module))

    inactiveTurrets = []
    if "inactiveTurrets" in userDict:
        for turret in userDict["inactiveTurrets"]:
            inactiveTurrets.append(bbShip.fromDict(turret))

    return bbUser(id, credits=userDict["credits"], lifetimeCredits=userDict["lifetimeCredits"],
                    bountyCooldownEnd=userDict["bountyCooldownEnd"], systemsChecked=userDict["systemsChecked"],
                    bountyWins=userDict["bountyWins"], activeShip=activeShip, inactiveShips=inactiveShips,
                    inactiveModules=inactiveModules, inactiveWeapons=inactiveWeapons, inactiveTurrets=inactiveTurrets)
