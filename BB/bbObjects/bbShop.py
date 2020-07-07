from ..bbConfig import bbData, bbConfig
from .items import bbModuleFactory, bbShip, bbWeapon, bbTurret
from . import bbInventory, bbInventoryListing
import random

class bbShop:
    def __init__(self, maxShips=bbConfig.shopDefaultShipsNum, maxModules=bbConfig.shopDefaultModulesNum, maxWeapons=bbConfig.shopDefaultWeaponsNum, maxTurrets=bbConfig.shopDefaultTurretsNum, shipsStock=bbInventory.bbInventory(), weaponsStock=bbInventory.bbInventory(), modulesStock=bbInventory.bbInventory(), turretsStock=bbInventory.bbInventory(), currentTechLevel=bbConfig.minTechLevel):
        self.maxShips = maxShips
        self.maxModules = maxModules
        self.maxWeapons = maxWeapons
        self.maxTurrets = maxTurrets
        self.currentTechLevel = currentTechLevel

        if shipsStock.isEmpty() and weaponsStock.isEmpty() and modulesStock.isEmpty() and turretsStock.isEmpty():
            self.refreshStock()
        else:
            self.shipsStock = shipsStock
            self.weaponsStock = weaponsStock
            self.modulesStock = modulesStock
            self.turretsStock = turretsStock


    def refreshStock(self):
        self.shipsStock.clear()
        self.weaponsStock.clear()
        self.modulesStock.clear()
        self.turretsStock.clear()
        # self.currentTechLevel = random.randint(bbConfig.minTechLevel, bbConfig.maxTechLevel)
        self.currentTechLevel = bbConfig.pickRandomShopTL()

        for i in range(self.maxShips):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.shipKeysByTL[itemTL - 1]) != 0:
                self.shipsStock.addItem(bbShip.fromDict(bbData.builtInShipData[random.choice(bbData.shipKeysByTL[itemTL - 1])]))

        for i in range(self.maxModules):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.moduleObjsByTL[itemTL - 1]) != 0:
                self.modulesStock.addItem(random.choice(bbData.moduleObjsByTL[itemTL - 1]))

        for i in range(self.maxWeapons):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.weaponObjsByTL[itemTL - 1]) != 0:
                self.weaponsStock.addItem(random.choice(bbData.weaponObjsByTL[itemTL - 1]))

        # if random.randint(1, 100) <= bbConfig.turretSpawnProbability:
        for i in range(self.maxTurrets):
            itemTL = bbConfig.pickRandomItemTL(self.currentTechLevel)
            if len(bbData.turretObjsByTL[itemTL - 1]) != 0:
                self.turretsStock.addItem(random.choice(bbData.turretObjsByTL[itemTL - 1]))


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
            raise NotImplementedError("Valid, but unrecognised item type: " + item)


    # SHIP MANAGEMENT
    def userCanAffordShipObj(self, user, ship):
        return user.credits >= ship.getValue()

    
    def userCanAffordShipIndex(self, user, index):
        return self.userCanAffordShipObj(user, self.shipsStock[index].item)


    def amountCanAffordShipObj(self, amount, ship):
        return amount >= ship.getValue()

    
    def amountCanAffordShipIndex(self, amount, index):
        return self.amountCanAffordShipObj(amount, self.shipsStock[index].item)


    def userBuyShipIndex(self, user, index):
        self.userBuyShipIndex(user, self.shipsStock[index].item)
        

        
    def userBuyShipObj(self, user, requestedShip):
        if self.userCanAffordShipObj(user, requestedShip):
            self.shipsStock.removeItem(requestedShip)
            user.credits -= requestedShip.getValue()
            user.inactiveShips.append(requestedShip)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy ship " + requestedShip.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedShip.getValue()))


    def userSellShipObj(self, user, ship):
        user.credits += ship.getValue()
        self.shipsStock.addItem(ship)
        user.inactiveShips.remove(ship)
    

    def userSellShipIndex(self, user, index):
        self.userSellShipObj(user, user.inactiveShips[index])


    
    # WEAPON MANAGEMENT
    def userCanAffordWeaponObj(self, user, weapon):
        return user.credits >= weapon.getValue()

    
    def userCanAffordWeaponIndex(self, user, index):
        return self.userCanAffordWeaponObj(user, self.weaponsStock[index].item)


    def userBuyWeaponIndex(self, user, index):
        self.userBuyWeaponIndex(user, self.weaponsStock[index].item)
        

    def userBuyWeaponObj(self, user, requestedWeapon):
        if self.userCanAffordWeaponObj(user, requestedWeapon):
            self.weaponsStock.removeItem(requestedWeapon)
            user.credits -= requestedWeapon.getValue()
            user.inactiveShips.append(requestedWeapon)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy weapon " + requestedWeapon.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedWeapon.getValue()))


    def userSellWeaponObj(self, user, weapon):
        user.credits += weapon.getValue()
        self.weaponsStock.addItem(weapon)
        user.inactiveWeapons.remove(weapon)
    

    def userSellWeaponIndex(self, user, index):
        self.userSellWeaponObj(user, user.inactiveWeapons[index])


    
    # MODULE MANAGEMENT
    def userCanAffordModuleObj(self, user, module):
        return user.credits >= module.getValue()

    
    def userCanAffordModuleIndex(self, user, index):
        return self.userCanAffordModuleObj(user, self.modulesStock[index].item)


    def userBuyModuleIndex(self, user, index):
        self.userBuyModuleIndex(user, self.modulesStock[index].item)
        

    def userBuyModuleObj(self, user, requestedModule):
        if self.userCanAffordModuleObj(user, requestedModule):
            self.modulesStock.removeItem(requestedModule)
            user.credits -= requestedModule.getValue()
            user.inactiveShips.append(requestedModule)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy module " + requestedModule.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedModule.getValue()))


    def userSellModuleObj(self, user, module):
        user.credits += module.getValue()
        self.modulesStock.addItem(module)
        user.inactiveModules.remove(module)
    

    def userSellModuleIndex(self, user, index):
        self.userSellModuleObj(user, user.inactiveModules[index])



    # TURRET MANAGEMENT
    def userCanAffordTurretObj(self, user, turret):
        return user.credits >= turret.getValue()

    
    def userCanAffordTurretIndex(self, user, index):
        return self.userCanAffordTurretObj(user, self.turretsStock[index].item)


    def userBuyTurretIndex(self, user, index):
        self.userBuyTurretIndex(user, self.turretsStock[index].item)
        
        
    def userBuyTurretObj(self, user, requestedTurret):
        if self.userCanAffordTurretObj(user, requestedTurret):
            self.turretsStock.removeItem(requestedTurret)
            user.credits -= requestedTurret.getValue()
            user.inactiveShips.append(requestedTurret)
        else:
            raise RuntimeError("user " + str(user.id) + " attempted to buy turret " + requestedTurret.name + " but can't afford it: " + str(user.credits) + " < " + str(requestedTurret.getValue()))


    def userSellTurretObj(self, user, turret):
        user.credits += turret.getValue()
        self.turretsStock.addItem(turret)
        user.inactiveTurrets.remove(turret)
    

    def userSellTurretIndex(self, user, index):
        self.userSellTurretObj(user, user.inactiveTurrets[index])



    def toDict(self):
        shipsStockDict = []
        for ship in self.shipsStock.keys:
            shipsStockDict.append(shipsStock[ship].toDict())

        weaponsStockDict = []
        for weapon in self.weaponsStock.keys:
            weaponsStockDict.append(weaponsStock[weapon].toDict())

        modulesStockDict = []
        for module in self.modulesStock.keys:
            modulesStockDict.append(modulesStock[module].toDict())

        turretsStockDict = []
        for turret in self.turretsStock.keys:
            turretsStockDict.append(turretsStock[turret].toDict())

        return {"maxShips":self.maxShips, "maxWeapons":self.maxWeapons, "maxModules":self.maxModules,
                    "shipsStock":shipsStockDict, "weaponsStock":weaponsStockDict, "modulesStock":modulesStockDict, "turretsStock":turretsStockDict}


def fromDict(shopDict):
    shipsStock = bbInventory.bbInventory()
    for shipListingDict in shopDict["shipsStock"]:
        shipsStock.addItem(bbShip.fromDict(shipListingDict["item"]), count=shipListingDict["count"])

    weaponsStock = bbInventory.bbInventory()
    for weaponListingDict in shopDict["weaponsStock"]:
        weaponsStock.addItem(bbWeapon.fromDict(weaponListingDict["item"]), count=weaponListingDict["count"])

    modulesStock = bbInventory.bbInventory()
    for moduleListingDict in shopDict["modulesStock"]:
        modulesStock.addItem(bbModuleFactory.fromDict(moduleListingDict["item"]), count=moduleListingDict["count"])

    turretsStock = bbInventory.bbInventory()
    for turretListingDict in shopDict["turretsStock"]:
        turretsStock.addItem(bbTurret.fromDict(turretListingDict["item"]), count=turretListingDict["count"])

    return bbShop(shopDict["maxShips"], shopDict["maxWeapons"], shopDict["maxModules"],
                    shipsStock=shipsStock, weaponsStock=weaponsStock, modulesStock=modulesStock, turretsStock=turretsStock)
