from .. import bbAliasable
from . import bbModule, bbTurret, bbWeapon, bbShipUpgrade
from ...bbConfig import bbConfig, bbData

class bbShip(bbAliasable.Aliasable):
    hasWiki = False
    wiki = ""
    manufacturer = ""
    icon = ""
    hasIcon = False

    hasNickname = False
    nickname = ""

    armour = 0.0
    cargo = 0
    numSecondaries = 0
    handling = 0
    value = 0

    maxPrimaries = 0
    maxTurrets = 0
    maxModules = 0

    weapons = []
    modules = []
    turrets = []

    upgradesApplied = []


    def __init__(self, name, maxPrimaries, maxTurrets, maxModules, manufacturer="", armour=0.0, cargo=0, numSecondaries=0, handling=0, value=0, aliases=[], weapons=[], modules=[], turrets=[], wiki="", upgradesApplied=[], nickname="", icon=""):
        super(bbShip, self).__init__(name, aliases)

        if len(weapons) > maxPrimaries:
            ValueError("passed more weapons than can be stored on this ship - maxPrimaries")
        if len(modules) > maxModules:
            ValueError("passed more modules than can be stored on this ship - maxModules")
        if len(turrets) > maxTurrets:
            ValueError("passed more turrets than can be stored on this ship - maxTurrets")

        self.hasWiki = wiki != ""
        self.wiki = wiki
        self.icon = icon
        self.hasIcon = icon != ""

        self.name = name
        self.armour = armour
        self.cargo = cargo
        self.numSecondaries = numSecondaries
        self.handling = handling
        self.value = value
        
        self.maxPrimaries = maxPrimaries
        self.maxTurrets = maxTurrets
        self.maxModules = maxModules

        self.weapons = weapons
        self.modules = modules
        self.turrets = turrets

        if nickname != "":
            self.changeNickname(nickname)
        self.manufacturer = manufacturer


    def getNumWeaponsEquipped(self):
        return len(self.weapons)


    def canEquipMoreWeapons(self):
        return self.getNumWeaponsEquipped() < self.getMaxPrimaries()

    
    def getNumModulesEquipped(self):
        return len(self.modules)


    def canEquipMoreModules(self):
        return self.getNumModulesEquipped() < self.getMaxModules()

    
    def getNumTurretsEquipped(self):
        return len(self.turrets)


    def canEquipMoreTurrets(self):
        return self.getNumTurretsEquipped() < self.getMaxTurrets()

    
    def hasWeaponsEquipped(self):
        return self.getNumWeaponsEquipped() > 0

    def hasModulesEquipped(self):
        return self.getNumModulesEquipped() > 0

    def hasTurretsEquipped(self):
        return self.getNumTurretsEquipped() > 0


    def equipWeapon(self, weapon):
        if not self.canEquipMoreWeapons():
            raise OverflowError("Attempted to equip a weapon but all weapon slots are full")
        self.weapons.append(weapon)
    

    def unequipWeaponObj(self, weapon):
        self.weapons.remove(weapon)


    def unequipWeaponIndex(self, index):
        self.weapons.pop(index)


    def getWeaponAtIndex(self, index):
        return self.weapons[index]


    def equipModule(self, module):
        if not self.canEquipMoreModules():
            raise OverflowError("Attempted to equip a module but all module slots are full")
        self.modules.append(module)
    

    def unequipModuleObj(self, module):
        self.modules.remove(module)


    def unequipModuleIndex(self, index):
        self.modules.pop(index)


    def getModuleAtIndex(self, index):
        return self.modules[index]


    def equipTurret(self, turret):
        if not self.canEquipMoreTurrets():
            raise OverflowError("Attempted to equip a turret but all turret slots are full")
        self.turrets.append(turret)
    

    def unequipTurretObj(self, turret):
        self.turrets.remove(turret)


    def unequipTurretIndex(self, index):
        self.turrets.pop(index)


    def getTurretAtIndex(self, index):
        return self.turrets[index]

    
    def getDPS(self, shipUpgradesOnly=False):
        total = 0
        multiplier = 1
        if not shipUpgradesOnly:
            for weapon in self.weapons:
                total += weapon.dps
            for module in self.modules:
                total += module.dps
                multiplier *= module.dpsMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.dps
            multiplier *= upgrade.dpsMultiplier
        return total * multiplier

    
    def getShield(self, shipUpgradesOnly=False):
        total = 0
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.shield
                multiplier *= module.shieldMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.shield
            multiplier *= upgrade.shieldMultiplier
        return total * multiplier


    def getArmour(self, shipUpgradesOnly=False):
        total = self.armour
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.armour
                multiplier *= module.armourMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.armour
            multiplier *= upgrade.armourMultiplier
        return total * multiplier


    def getCargo(self, shipUpgradesOnly=False):
        total = self.cargo
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.cargo
                multiplier *= module.cargoMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.cargo
            multiplier *= upgrade.cargoMultiplier
        return total * multiplier


    def getHandling(self, shipUpgradesOnly=False):
        total = self.handling
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.handling
                multiplier *= module.handlingMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.handling
            multiplier *= upgrade.handlingMultiplier
        return total * multiplier


    def getNumSecondaries(self, shipUpgradesOnly=False):
        total = self.numSecondaries
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.numSecondaries
            multiplier *= upgrade.numSecondariesMultiplier
        return total * multiplier


    def getMaxPrimaries(self, shipUpgradesOnly=False):
        total = self.maxPrimaries
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.maxPrimaries
            multiplier *= upgrade.maxPrimariesMultiplier
        return total * multiplier


    def getMaxTurrets(self, shipUpgradesOnly=False):
        total = self.maxTurrets
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.maxTurrets
            multiplier *= upgrade.maxTurretsMultiplier
        return total * multiplier


    def getMaxModules(self, shipUpgradesOnly=False):
        total = self.maxModules
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.maxModules
            multiplier *= upgrade.maxModulesMultiplier
        return total * multiplier


    def getValue(self, shipUpgradesOnly=False):
        total = self.value

        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.value
            for weapon in self.weapons:
                total += weapon.value
            for turret in self.turrets:
                total += turret.value
        for upgrade in self.upgradesApplied:
            total += upgrade.value

        return total

    
    def applyUpgrade(self, upgrade):
        self.upgradesApplied.append(upgrade)

    
    def changeNickname(self, nickname):
        self.nickname = nickname
        if nickname != "":
            self.hasNickname = True

    
    def removeNickname(self):
        if self.hasNickname:
            self.nickname = ""
            self.hasNickname = False

        
    def getNameOrNick(self):
        return self.nickname if self.hasNickname else self.name

    
    def getNameAndNick(self):
        return self.name if not self.hasNickname else self.nickname + " (" + self.name + ")"


    def transferItemsTo(self, other):
        if not type(other) == bbShip:
            raise TypeError("Can only transfer items to another bbShip. Given " + str(type(other)))

        while self.hasWeaponsEquipped() and other.canEquipMoreWeapons():
            other.equipWeapon(self.weapons.pop(0))

        while self.hasModulesEquipped() and other.canEquipMoreModules():
            other.equipModule(self.modules.pop(0))

        while self.hasTurretsEquipped() and other.canEquipMoreTurrets():
            other.equipTurret(self.turrets.pop(0))


    def getActivesByName(self, item):
        if item == "all" or item == "ship" or item not in bbConfig.validItemNames:
            raise ValueError("Invalid item type: " + item)
        elif item == "weapon":
            return self.weapons
        elif item == "module":
            return self.modules
        elif item == "turret":
            return self.turrets
        else:
            raise NotImplementedError("Valid, not unrecognised item type: " + item)


    def statsStringShort(self):
        stats = ""
        stats += "• *Armour: " + str(self.armour) + ("(+)" if self.armour < self.getArmour(shipUpgradesOnly=True) else "") + "*\n"
        # stats += "Cargo hold: " + str(self.cargo) + ", "
        # stats += "Handling: " + str(self.handling) + ", "
        stats += "• *Primaries: " + str(len(self.weapons)) + "/" + str(self.maxPrimaries) + ("(+)" if self.maxPrimaries < self.getMaxPrimaries(shipUpgradesOnly=True) else "") + "*\n"
        if len(self.weapons) > 0:
            stats += "*["
            for weapon in self.weapons:
                stats += weapon.name + ", "
            stats = stats[:-2] + "]*\n"
        # stats += "Max secondaries: " + str(self.numSecondaries) + ", "
        stats += "• *Turrets: " + str(len(self.turrets)) + "/" + str(self.maxTurrets) + ("(+)" if self.maxTurrets < self.getMaxTurrets(shipUpgradesOnly=True) else "") + "*\n"
        if len(self.turrets) > 0:
            stats += "*["
            for turret in self.turrets:
                stats += turret.name + ", "
            stats = stats[:-2] + "]*\n"
        stats += "• *Modules: " + str(len(self.modules)) + "/" + str(self.maxModules) + ("(+)" if self.maxModules < self.getMaxModules(shipUpgradesOnly=True) else "") + "*\n"
        if len(self.modules) > 0:
            stats += "*["
            for module in self.modules:
                stats += module.name + ", "
            stats = stats[:-2] + "]*\n"
        return stats

    
    def statsStringNoItems(self):
        stats = ""
        stats += "*Armour: " + str(self.armour) + ("(+)" if self.armour < self.getArmour(shipUpgradesOnly=True) else "") + ", "
        stats += "Cargo hold: " + str(self.cargo) + ("(+)" if self.cargo < self.getCargo(shipUpgradesOnly=True) else "") + ", "
        stats += "Handling: " + str(self.handling) + ("(+)" if self.handling < self.getHandling(shipUpgradesOnly=True) else "") + ", "
        stats += "Max secondaries: " + str(self.numSecondaries) + ("(+)" if self.numSecondaries < self.getNumSecondaries(shipUpgradesOnly=True) else "") + "*"
        return stats
    

    def getType(self):
        return bbShip


    def toDict(self):
        weaponsList = []
        for weapon in self.weapons:
            weaponsList.append(weapon.toDict())
        
        modulesList = []
        for module in self.modules:
            modulesList.append(module.toDict())

        turretsList = []
        for turret in self.turrets:
            turretsList.append(turret.toDict())
        
        upgradesList = []
        for upgrade in self.upgradesApplied:
            upgradesList.append(upgrade.toDict())

        # Old method with every ship explicit and non-builtIn to allow customisability
        # return {"name":self.name, "aliases":self.aliases, "wiki":self.wiki, "manufacturer":self.manufacturer,
        #             "nickname":self.nickname, "armour":self.armour, "cargo": self.cargo, "numSecondaries":self.numSecondaries,
        #             "handling":self.handling, "value":self.value, "maxPrimaries":self.maxPrimaries, "maxTurrets":self.maxTurrets,
        #             "maxModules":self.maxModules, "weapons":weaponsList, "modules":modulesList, "turrets":turretsList, "upgradesApplied":upgradesList}

        # New method with everys ship builtIn, but overwriting inheriting attributes
        return {"name": self.name, "builtIn":True, "nickname": self.nickname, "weapons":weaponsList, "modules":modulesList, "turrets":turretsList, "upgradesApplied":upgradesList}


def fromDict(shipDict):
    weapons = []
    if "weapons" in shipDict:
        for weapon in shipDict["weapons"]:
            weapons.append(bbWeapon.fromDict(weapon))

    modules = []
    if "modules" in shipDict:
        for module in shipDict["modules"]:
            modules.append(bbModule.fromDict(module))

    turrets = []
    if "turrets" in shipDict:
        for turret in shipDict["turrets"]:
            turrets.append(bbTurret.fromDict(turret))

    shipUpgrades = []
    if "shipUpgrade" in shipDict:
        for shipUpgrade in shipDict["shipUpgrades"]:
            shipUpgrades.append(bbShipUpgrade.fromDict(shipUpgrade))
    
    if shipDict["builtIn"]:
        builtInDict = bbData.builtInShipData[shipDict["name"]]

        builtInWeapons = []
        if "weapons" in shipDict:
            for weapon in shipDict["weapons"]:
                builtInWeapons.append(bbWeapon.fromDict(weapon))

        builtInModules = []
        if "modules" in shipDict:
            for module in shipDict["modules"]:
                builtInModules.append(bbModule.fromDict(module))

        builtInTurrets = []
        if "turrets" in shipDict:
            for turret in shipDict["turrets"]:
                builtInTurrets.append(bbTurret.fromDict(turret))

        builtInShipUpgrades = []
        if "shipUpgrade" in shipDict:
            for shipUpgrade in shipDict["shipUpgrades"]:
                builtInShipUpgrades.append(bbShipUpgrade.fromDict(shipUpgrade))

        newShip = bbShip(builtInDict["name"], builtInDict["maxPrimaries"], builtInDict["maxTurrets"], builtInDict["maxModules"], manufacturer=builtInDict["manufacturer"] if "manufacturer" in builtInDict else "",
                    armour=builtInDict["armour"] if "armour" in builtInDict else 0, cargo=builtInDict["cargo"] if "cargo" in builtInDict else 0,
                    numSecondaries=builtInDict["numSecondaries"] if "numSecondaries" in builtInDict else 0, handling=builtInDict["handling"] if "handling" in builtInDict else 0,
                    value=builtInDict["value"] if "value" in builtInDict else 0, aliases=builtInDict["aliases"] if "aliases" in builtInDict else [],
                    weapons=weapons if "weapons" in shipDict else builtInWeapons, modules=modules if "modules" in shipDict else builtInModules, turrets=turrets if "turrets" in shipDict else builtInTurrets, wiki=builtInDict["wiki"] if "wiki" in builtInDict else "0",
                    upgradesApplied=shipUpgrades if "shipUpgrades" in shipDict else builtInShipUpgrades, nickname=shipDict["nickname"] if "nickname" in shipDict else (builtInDict["nickname"] if "nickname" in builtInDict else ""), icon=builtInDict["icon"] if "icon" in builtInDict else bbData.rocketIcon)
        return newShip

    else:
        return bbShip(shipDict["name"], shipDict["maxPrimaries"], shipDict["maxTurrets"], shipDict["maxModules"], manufacturer=shipDict["manufacturer"] if "manufacturer" in shipDict else "",
                        armour=shipDict["armour"] if "armour" in shipDict else 0, cargo=shipDict["cargo"] if "cargo" in shipDict else 0,
                        numSecondaries=shipDict["numSecondaries"] if "numSecondaries" in shipDict else 0, handling=shipDict["handling"] if "handling" in shipDict else 0,
                        value=shipDict["value"] if "value" in shipDict else 0, aliases=shipDict["aliases"] if "aliases" in shipDict else [],
                        weapons=weapons, modules=modules, turrets=turrets, wiki=shipDict["wiki"] if "wiki" in shipDict else "0",
                        upgradesApplied=shipUpgrades, nickname=shipDict["nickname"] if "nickname" in shipDict else "", icon=shipDict["icon"] if "icon" in shipDict else bbData.rocketIcon)
