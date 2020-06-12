from .items import bbShip, bbModule, bbWeapon, bbTurret
from ..bbConfig import bbConfig


defaultShipLoadoutDict = {"name": "Betty", "builtIn":True,
                        "weapons":[{"name": "Micro Gun MK I", "builtIn": True}],
                        "modules":[{"name": "E2 Exoclad", "builtIn": True}, {"name": "E2 Exoclad", "builtIn": True}, {"name": "E2 Exoclad", "builtIn": True}]}

defaultUserDict = {"credits":0, "bountyCooldownEnd":0, "lifetimeCredits":0, "systemsChecked":0, "bountyWins":0, "activeShip": defaultShipLoadoutDict, "inactiveWeapons":[{"name": "Nirai Impulse EX 1", "builtIn": True}]}


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


    def numInventoryPages(self, item, maxPerPage):
        if item not in bbConfig.validItemNames:
            raise ValueError("Requested an invalid item name: " + item)

        numWeapons = len(self.inactiveWeapons)
        numModules = len(self.inactiveModules)
        numTurrets = len(self.inactiveTurrets)
        numShips = len(self.inactiveShips)

        itemsNum = 0

        if item == "all":
            itemsNum = max(numWeapons, numModules, numTurrets, numShips)
        elif item == "module":
            itemsNum = numModules
        elif item == "weapon":
            itemsNum = numWeapons
        elif item == "turret":
            itemsNum = numTurrets
        elif item == "ship":
            itemsNum = numShips
        else:
            raise NotImplementedError("Valid but unsupported item name: " + item)
        
        return int(itemsNum/maxPerPage) + (0 if itemsNum % maxPerPage == 0 else 1)

    
    def lastItemNumberOnPage(self, item, pageNum, maxPerPage):
        if item not in bbConfig.validItemNames:
            raise ValueError("Requested an invalid item name: " + item)
        if pageNum < self.numInventoryPages(item, maxPerPage):
            return pageNum * maxPerPage
            
        elif item == "ship":
            return len(self.inactiveShips)
        elif item == "weapon":
            return len(self.inactiveWeapons)
        elif item == "module":
            return len(self.inactiveModules)
        elif item == "turret":
            return len(self.inactiveTurrets)
        else:
            raise NotImplementedError("Valid but unsupported item name: " + item)


    def unequipAll(self, ship):
        if not type(ship) == bbShip.bbShip:
            raise TypeError("Can only transfer items to another bbShip. Given " + str(type(ship)))

        if not (self.activeShip == ship or ship in self.inactiveShips):
            raise RuntimeError("Attempted to unequipAll on a ship that isnt owned by this bbUser")

        for weapon in ship.weapons:
            self.inactiveWeapons.append(weapon)
            # ship.unequipWeaponObj(weapon)
        ship.weapons = []
        for module in ship.modules:
            self.inactiveModules.append(module)
            # ship.unequipModuleObj(module)
        ship.modules = []
        for turret in ship.turrets:
            self.inactiveTurrets.append(turret)
            # ship.unequipTurretObj(turret)
        ship.turrets = []


    def equipShipObj(self, ship, noSaveActive=False):
        if not (self.activeShip == ship or ship in self.inactiveShips):
            raise RuntimeError("Attempted to equip a ship that isnt owned by this bbUser")
        if not noSaveActive and self.activeShip is not None:
            self.inactiveShips.append(self.activeShip)
        if ship in self.inactiveShips:
            self.inactiveShips.remove(ship)
        self.activeShip = ship

    
    def equipShipIndex(self, index):
        if not (0 <= index <= len(self.inactiveShips) - 1):
            raise RuntimeError("Index out of range")
        if self.activeShip is not None:
            self.inactiveShips.append(self.activeShip)
        self.activeShip = self.inactiveShips.pop(index)


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


    def getInactivesByName(self, item):
        if item == "all" or item not in bbConfig.validItemNames:
            raise ValueError("Invalid item type: " + item)
        if item == "ship":
            return self.inactiveShips
        if item == "weapon":
            return self.inactiveWeapons
        if item == "module":
            return self.inactiveModules
        if item == "turret":
            return self.inactiveTurrets
        else:
            raise NotImplementedError("Valid, not unrecognised item type: " + item)


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
            inactiveWeapons.append(bbWeapon.fromDict(weapon))

    inactiveModules = []
    if "inactiveModules" in userDict:
        for module in userDict["inactiveModules"]:
            inactiveModules.append(bbModule.fromDict(module))

    inactiveTurrets = []
    if "inactiveTurrets" in userDict:
        for turret in userDict["inactiveTurrets"]:
            inactiveTurrets.append(bbTurret.fromDict(turret))

    return bbUser(id, credits=userDict["credits"], lifetimeCredits=userDict["lifetimeCredits"],
                    bountyCooldownEnd=userDict["bountyCooldownEnd"], systemsChecked=userDict["systemsChecked"],
                    bountyWins=userDict["bountyWins"], activeShip=activeShip, inactiveShips=inactiveShips,
                    inactiveModules=inactiveModules, inactiveWeapons=inactiveWeapons, inactiveTurrets=inactiveTurrets)
