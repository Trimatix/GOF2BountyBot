from ..bbConfig import bbData, bbConfig
from .items import bbModuleFactory, bbShip, bbWeapon, bbTurret
import random

class bbShop:
    def __init__(self, maxShips=bbConfig.shopDefaultShipsNum, maxModules=bbConfig.shopDefaultModulesNum, maxWeapons=bbConfig.shopDefaultWeaponsNum, maxTurrets=bbConfig.shopDefaultTurretsNum, shipsStock=[], weaponsStock=[], modulesStock=[], turretsStock=[], currentTechLevel=bbConfig.minTechLevel):
        self.maxShips = maxShips
        self.maxModules = maxModules
        self.maxWeapons = maxWeapons
        self.maxTurrets = maxTurrets
        self.currentTechLevel = currentTechLevel

        if shipsStock == [] and weaponsStock == [] and modulesStock == [] and turretsStock == []:
            self.shipsStock = []
            self.weaponsStock = []
            self.modulesStock = []
            self.turretsStock = []
            self.refreshStock()
        else:
            self.shipsStock = shipsStock
            self.weaponsStock = weaponsStock
            self.modulesStock = modulesStock
            self.turretsStock = turretsStock


    def refreshStock(self):
        self.shipsStock = []
        self.weaponsStock = []
        self.modulesStock = []
        self.turretsStock = []
        self.currentTechLevel = random.randint(bbConfig.minTechLevel, bbConfig.maxTechLevel)

        for i in range(self.maxShips):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.shipKeysByTL[itemTL - 1]) != 0:
                self.shipsStock.append(bbShip.fromDict(bbData.builtInShipData[random.choice(bbData.shipKeysByTL[itemTL - 1])]))

        for i in range(self.maxModules):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.moduleObjsByTL[itemTL - 1]) != 0:
                self.modulesStock.append(random.choice(bbData.moduleObjsByTL[itemTL - 1]))

        for i in range(self.maxWeapons):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.weaponObjsByTL[itemTL - 1]) != 0:
                self.weaponsStock.append(random.choice(bbData.weaponObjsByTL[itemTL - 1]))

        # if random.randint(1, 100) <= bbConfig.turretSpawnProbability:
        for i in range(self.maxTurrets):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.turretObjsByTL[itemTL - 1]) != 0:
                self.turretsStock.append(random.choice(bbData.turretObjsByTL[itemTL - 1]))


    def getStockByName(self, item):
        if item == "all" or item not in bbConfig.validItemNames:
            raise ValueError("Invalid item type: " + item)
        if item == "ship":
            return self.shipsStock
        if item == "weapon":
            return self.weaponsStock
        if item == "module":
            return self.modulesStock
        if item == "turret":
            return self.turretsStock
        else:
            raise NotImplementedError("Valid, not unrecognised item type: " + item)


    # SHIP MANAGEMENT
    def userCanAffordShipObj(self, user, ship):
        return user.credits >= ship.getValue()

    
    def userCanAffordShipIndex(self, user, index):
        return self.userCanAffordShipObj(user, self.shipsStock[index])


    def amountCanAffordShipObj(self, amount, ship):
        return amount >= ship.getValue()

    
    def amountCanAffordShipIndex(self, amount, index):
        return self.amountCanAffordShipObj(amount, self.shipsStock[index])


    def userBuyShipIndex(self, user, index):
        if self.userCanAffordShipIndex(user, index):
            user.credits -= self.shipsStock[index].getValue()
            user.inactiveShips.append(self.shipsStock.pop(index))
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy ship " + self.shipsStock[index].name + " but can't afford it: " + str(user.credits) + " < " + str(self.shipsStock[index].getValue()))

        
    def userBuyShipObj(self, user, ship):
        self.userBuyShipIndex(user, self.shipsStock.index(ship))


    def userSellShipObj(self, user, ship):
        self.userSellShipIndex(user, user.inactiveShips.index(ship))
    

    def userSellShipIndex(self, user, index):
        user.credits += user.inactiveShips[index].getValue()
        self.shipsStock.append(user.inactiveShips.pop(index))


    
    # WEAPON MANAGEMENT
    def userCanAffordWeaponObj(self, user, weapon):
        return user.credits >= weapon.value

    
    def userCanAffordWeaponIndex(self, user, index):
        return self.userCanAffordWeaponObj(user, self.weaponsStock[index])


    def userBuyWeaponIndex(self, user, index):
        if self.userCanAffordWeaponIndex(user, index):
            user.credits -= self.weaponsStock[index].getValue()
            user.inactiveWeapons.append(self.weaponsStock.pop(index))
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy weapon " + self.weaponsStock[index].name + " but can't afford it: " + str(user.credits) + " < " + str(self.weaponsStock[index].getValue()))

        
    def userBuyWeaponObj(self, user, weapon):
        self.userBuyWeaponIndex(user, self.weaponsStock.index(weapon))


    def userSellWeaponObj(self, user, weapon):
        self.userSellWeaponIndex(user, user.inactiveWeapons.index(weapon))
    

    def userSellWeaponIndex(self, user, index):
        user.credits += user.inactiveWeapons[index].getValue()
        self.weaponsStock.append(user.inactiveWeapons.pop(index))


    
    # MODULE MANAGEMENT
    def userCanAffordModuleObj(self, user, module):
        return user.credits >= module.value

    
    def userCanAffordModuleIndex(self, user, index):
        return self.userCanAffordModuleObj(user, self.modulesStock[index])


    def userBuyModuleIndex(self, user, index):
        if self.userCanAffordModuleIndex(user, index):
            user.credits -= self.modulesStock[index].getValue()
            user.inactiveModules.append(self.modulesStock.pop(index))
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy module " + self.modulesStock[index].name + " but can't afford it: " + str(user.credits) + " < " + str(self.modulesStock[index].getValue()))

        
    def userBuyModuleObj(self, user, module):
        self.userBuyModuleIndex(user, self.modulesStock.index(module))


    def userSellModuleObj(self, user, module):
        self.userSellModuleIndex(user, user.inactiveModules.index(module))
    

    def userSellModuleIndex(self, user, index):
        user.credits += user.inactiveModules[index].getValue()
        self.modulesStock.append(user.inactiveModules.pop(index))


    # TURRET MANAGEMENT
    def userCanAffordTurretObj(self, user, turret):
        return user.credits >= turret.value

    
    def userCanAffordTurretIndex(self, user, index):
        return self.userCanAffordTurretObj(user, self.turretsStock[index])


    def userBuyTurretIndex(self, user, index):
        if self.userCanAffordTurretIndex(user, index):
            user.credits -= self.turretsStock[index].getValue()
            user.inactiveTurrets.append(self.turretsStock.pop(index))
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy turret " + self.turretsStock[index].name + " but can't afford it: " + str(user.credits) + " < " + str(self.turretsStock[index].getValue()))

        
    def userBuyTurretObj(self, user, turret):
        self.userBuyTurretIndex(user, self.turretsStock.index(turret))


    def userSellTurretObj(self, user, turret):
        self.userSellTurretIndex(user, user.inactiveTurrets.index(turret))
    

    def userSellTurretIndex(self, user, index):
        user.credits += user.inactiveTurrets[index].getValue()
        self.turretsStock.append(user.inactiveTurrets.pop(index))



    def toDict(self):
        shipsStockDict = []
        for ship in self.shipsStock:
            shipsStockDict.append(ship.toDict())

        weaponsStockDict = []
        for weapon in self.weaponsStock:
            weaponsStockDict.append(weapon.toDict())

        modulesStockDict = []
        for module in self.modulesStock:
            modulesStockDict.append(module.toDict())

        turretsStockDict = []
        for turret in self.turretsStock:
            turretsStockDict.append(turret.toDict())

        return {"maxShips":self.maxShips, "maxWeapons":self.maxWeapons, "maxModules":self.maxModules,
                    "shipsStock":shipsStockDict, "weaponsStock":weaponsStockDict, "modulesStock":modulesStockDict, "turretsStock":turretsStockDict}


def fromDict(shopDict):
    shipsStock = []
    for shipDict in shopDict["shipsStock"]:
        shipsStock.append(bbShip.fromDict(shipDict))

    weaponsStock = []
    for weaponDict in shopDict["weaponsStock"]:
        weaponsStock.append(bbWeapon.fromDict(weaponDict))

    modulesStock = []
    for moduleDict in shopDict["modulesStock"]:
        modulesStock.append(bbModuleFactory.fromDict(moduleDict))

    turretsStock = []
    for turret in shopDict["turretsStock"]:
        turretsStock.append(bbTurret.fromDict(turret))

    return bbShop(shopDict["maxShips"], shopDict["maxWeapons"], shopDict["maxModules"],
                    shipsStock=shipsStock, weaponsStock=weaponsStock, modulesStock=modulesStock, turretsStock=turretsStock)
