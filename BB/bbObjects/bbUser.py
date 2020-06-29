from .items import bbShip, bbModuleFactory, bbWeapon, bbTurret
from .items.bbCommodityInInventory import bbCommodityInInventory
from .items.modules import bbMiningDrillModule
from ..bbConfig import bbConfig


defaultShipLoadoutDict = {"name": "Betty", "builtIn":True,
                        "weapons":[{"name": "Micro Gun MK I", "builtIn": True}],
                        "modules":[{"name": "Telta Quickscan", "builtIn": True}, {"name": "E2 Exoclad", "builtIn": True}, {"name": "IMT Extract 1.3", "builtIn": True}]}

defaultUserDict = {"credits":0, "bountyCooldownEnd":0, "lifetimeCredits":0, "systemsChecked":0, "bountyWins":0, "activeShip": defaultShipLoadoutDict, "inactiveWeapons":[{"name": "Nirai Impulse EX 1", "builtIn": True}]}


class bbUser:
    id = 0
    credits = 0
    lifetimeCredits = 0
    bountyCooldownEnd = -1
    systemsChecked = 0
    bountyWins = 0
    lastSeenGuildId = -1
    hasLastSeenGuildId = False

    defaultMineIsRisky = False
    commoditiesCollected = 0

    activeShip = None
    inactiveShips = []
    inactiveModules = []
    inactiveWeapons = []
    inactiveTurrets = []

    storedCommodities = []

    # dict of targetBBUser:DuelRequest
    duelRequests = {}
    duelWins = 0
    duelLosses = 0
    duelCreditsWins = 0
    duelCreditsLosses = 0
    

    def __init__(self, id, credits=0, lifetimeCredits=0, bountyCooldownEnd=-1, systemsChecked=0, bountyWins=0, activeShip=None, inactiveShips=[], inactiveModules=[], inactiveWeapons=[], inactiveTurrets=[], lastSeenGuildId=-1, duelWins=0, duelLosses=0, duelCreditsWins=0, duelCreditsLosses=0):
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

        self.defaultMineIsRisky = False
        self.commoditiesCollected = 0

        self.lastSeenGuildId = lastSeenGuildId
        self.haslastSeenGuildId = lastSeenGuildId != -1

        self.duelWins = duelWins
        self.duelRequests = {}

        self.duelLosses = duelLosses
        self.duelCreditsWins = duelCreditsWins
        self.duelCreditsLosses = duelCreditsLosses

    

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
        self.storedCommodities = []
        self.defaultMineIsRisky = False


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


    def validateLoadout(self):
        incompatibleModules = []
        allModulesChecked = False

        for currentModule in self.activeShip.modules:
            if not self.activeShip.canEquipModuleType(currentModule.getType()):
                incompatibleModules.append(currentModule)
                self.activeShip.unequipModuleObj(currentModule)

        finalModules = []
        for currentModule in incompatibleModules:
            if self.activeShip.canEquipModuleType(currentModule.getType()):
                self.activeShip.equipModule(currentModule)
            else:
                finalModules.append(currentModule)
        
        for currentModule in finalModules:
            self.inactiveModules.append(currentModule)


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
                "inactiveModules":inactiveModulesDict, "inactiveWeapons":inactiveWeaponsDict, "inactiveTurrets": inactiveTurretsDict, "lastSeenGuildId":self.lastSeenGuildId,
                "duelWins": self.duelWins, "duelLosses": self.duelLosses, "duelCreditsWins": self.duelCreditsWins, "duelCreditsLosses": self.duelCreditsLosses}


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
        elif stat == "value":
            modulesValue = 0
            for module in self.inactiveModules:
                modulesValue += module.getValue()
            turretsValue = 0
            for turret in self.inactiveTurrets:
                turretsValue += turret.getValue()
            weaponsValue = 0
            for weapon in self.inactiveWeapons:
                weaponsValue += weapon.getValue()
            shipsValue = 0
            for ship in self.inactiveShips:
                shipsValue += ship.getValue()

            return modulesValue + turretsValue + weaponsValue + shipsValue + self.activeShip.getValue() + self.credits


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
            raise NotImplementedError("Valid, but unrecognised item type: " + item)


    def hasDuelChallengeFor(self, targetBBUser):
        return targetBBUser in self.duelRequests


    def addDuelChallenge(self, duelReq):
        if duelReq.sourceBBUser is not self:
            raise ValueError("Attempted to add a DuelRequest for a different source user: " + str(duelReq.sourceBBUser.id))
        if self.hasDuelChallengeFor(duelReq.targetBBUser):
            raise ValueError("Attempted to add a DuelRequest for an already challenged user: " + str(duelReq.sourceBBUser.id))
        if duelReq.targetBBUser is self:
            raise ValueError("Attempted to add a DuelRequest for self: " + str(duelReq.sourceBBUser.id))
        self.duelRequests[duelReq.targetBBUser] = duelReq
        # print("user " + str(self.id) + " stored a new duel request, from " + str(duelReq.sourceBBUser.id) + " to " + str(duelReq.targetBBUser.id))


    def removeDuelChallengeObj(self, duelReq):
        if not duelReq.targetBBUser in self.duelRequests or self.duelRequests[duelReq.targetBBUser] is not duelReq:
            raise ValueError("Duel request not found: " + str(duelReq.sourceBBUser.id) + " -> " + str(duelReq.sourceBBUser.id))
        del self.duelRequests[duelReq.targetBBUser]
    
    
    def removeDuelChallengeTarget(self, duelTarget):
        self.removeDuelChallengeObj(self.duelRequests[duelTarget])


    def __str__(self):
        return "<bbUser #" + str(self.id) + ">"

    def getDrill(self):
        numModulesequipped = self.activeShip.getNumModulesEquipped()
        potentialDrill = []
        for i in range(numModulesequipped):
            if self.activeShip.getModuleAtIndex(i) is bbMiningDrillModule.bbMiningDrillModule:
                return self.activeShip.getModuleAtIndex(i)
        return None

    def addCommodity(self, commodity, quantity):
        try:
            commodityIndex = self.storedCommodities.index(commodity)
            self.storedCommodities[commodityIndex].increaseCommodity(quantity)
        except ValueError:
            self.storedCommodities.append(bbCommodityInInventory(commodity, quantity))

    def sellCommodity(self, commodity, quantity):
        for i in self.storedCommodities:
            if i.compareCommodity(commodity):
                if i.count < quantity:
                    return 1
                self.credits += (commodity.value * quantity)
                i.decreaseCommodity(quantity)
                if i.count == 0:
                    self.storedCommodities.remove(i)
                return 0
        return 2

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
            inactiveModules.append(bbModuleFactory.fromDict(module))

    inactiveTurrets = []
    if "inactiveTurrets" in userDict:
        for turret in userDict["inactiveTurrets"]:
            inactiveTurrets.append(bbTurret.fromDict(turret))

    return bbUser(id, credits=userDict["credits"], lifetimeCredits=userDict["lifetimeCredits"],
                    bountyCooldownEnd=userDict["bountyCooldownEnd"], systemsChecked=userDict["systemsChecked"],
                    bountyWins=userDict["bountyWins"], activeShip=activeShip, inactiveShips=inactiveShips,
                    inactiveModules=inactiveModules, inactiveWeapons=inactiveWeapons, inactiveTurrets=inactiveTurrets, lastSeenGuildId=userDict["lastSeenGuildId"] if "lastSeenGuildId" in userDict else -1,
                    duelWins=userDict["duelWins"] if "duelWins" in userDict else 0, duelLosses=userDict["duelLosses"] if "duelLosses" in userDict else 0, duelCreditsWins=userDict["duelCreditsWins"] if "duelCreditsWins" in userDict else 0, duelCreditsLosses=userDict["duelCreditsLosses"] if "duelCreditsLosses" in userDict else 0)
