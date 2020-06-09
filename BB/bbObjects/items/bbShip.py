from .. import bbAliasable
from . import bbModule, bbTurret, bbWeapon, bbShipUpgrade

class bbShip(bbAliasable.Aliasable):
    hasWiki = False
    wiki = ""
    manufacturer = ""

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


    def __init__(self, name, maxPrimaries, maxTurrets, maxModules, manufacturer="", armour=0.0, cargo=0, numSecondaries=0, handling=0, value=0, aliases=[], weapons=[], modules=[], turrets=[], wiki="", upgradesApplied=[], nickname=""):
        super(bbShip, self).__init__(name, aliases)

        if len(weapons) > maxPrimaries:
            ValueError("passed more weapons than can be stored on this ship - maxPrimaries")
        if len(modules) > maxModules:
            ValueError("passed more modules than can be stored on this ship - maxModules")
        if len(turrets) > maxTurrets:
            ValueError("passed more turrets than can be stored on this ship - maxTurrets")

        self.hasWiki = wiki != ""
        self.wiki = wiki

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

        self.hasNickname = nickname != ""
        self.nickname = nickname
        self.manufacturer = manufacturer


    def getNumWeaponsEquipped(self):
        return len(self.weapons)


    def canEquipMoreWeapons(self):
        return self.getNumWeaponsEquipped() < self.maxPrimaries

    
    def getNumModulesEquipped(self):
        return len(self.modules)


    def canEquipMoreModules(self):
        return self.getNumModulesEquipped() < self.maxModules

    
    def getNumTurretsEquipped(self):
        return len(self.turrets)


    def canEquipMoreTurrets(self):
        return self.getNumTurretsEquipped() < self.maxTurrets


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

    
    def getDPS(self):
        total = 0
        multiplier = 1
        for weapon in self.weapons:
            total += weapon.dps
        for module in self.modules:
            total += module.dps
            multiplier *= module.dpsMultiplier
        return total * multiplier

    
    def getShield(self):
        total = 0
        multiplier = 1
        for module in self.modules:
            total += module.shield
            multiplier *= module.shieldMultiplier
        return total * multiplier


    def getArmour(self):
        total = self.armour
        multiplier = 1
        for module in self.modules:
            total += module.armour
            multiplier *= module.armourMultiplier
        return total * multiplier


    def getCargo(self):
        total = self.cargo
        multiplier = 1
        for module in self.modules:
            total += module.cargo
            multiplier *= module.cargoMultiplier
        return total * multiplier


    def getHandling(self):
        total = self.handling
        multiplier = 1
        for module in self.modules:
            total += module.handling
            multiplier *= module.handlingMultiplier
        return total * multiplier


    def getValue(self):
        total = self.value

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
        # if upgrade.applied:
        #     raise RuntimeError("Attempted to apply a ship upgrade that has already been applied")

        # upgrade.applied = True
        # upgrade.value = upgrade.valueForShip(self)
        self.upgradesApplied.append(upgrade)

        self.armour += upgrade.armour
        self.armour *= upgrade.armourMultiplier

        self.cargo += upgrade.cargo
        self.cargo *= upgrade.cargoMultiplier

        self.numSecondaries += upgrade.numSecondaries
        self.numSecondaries *= upgrade.numSecondariesMultiplier

        self.handling += upgrade.handling
        self.handling *= upgrade.handlingMultiplier

        self.maxPrimaries += upgrade.maxPrimaries
        self.maxPrimaries *= upgrade.maxPrimariesMultiplier
        
        self.maxTurrets += upgrade.maxTurrets
        self.maxTurrets *= upgrade.maxTurretsMultiplier

        self.maxModules += upgrade.maxModules
        self.maxModules *= upgrade.maxModulesMultiplier

    
    def changeNickname(self, nickname):
        if self.hasNickname:
            self.removeAlias(self.nickname)
        self.nickname = nickname
        if nickname != "":
            self.hasNickname = True
            self.addAlias(nickname)

    
    def removeNickname(self, nickname):
        if self.hasNickname:
            self.removeAlias(self.nickname)
            self.nickname = ""
            self.hasNickname = False

        
    def getNameOrNick(self):
        return self.nickname if self.hasNickname else self.name

    
    def getNameAndNick(self):
        return self.name if not self.hasNickname else self.nickname + " (" + self.name + ")"
    

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

        return {"name":self.name, "aliases":self.aliases, "wiki":self.wiki, "manufacturer":self.manufacturer,
                    "nickname":self.nickname, "armour":self.armour, "cargo": self.cargo, "numSecondaries":self.numSecondaries,
                    "handling":self.handling, "value":self.value, "maxPrimaries":self.maxPrimaries, "maxTurrets":self.maxTurrets,
                    "maxModules":self.maxModules, "weapons":weaponsList, "modules":modulesList, "turrets":turretsList, "upgradesApplied":upgradesList}


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

    return bbShip(shipDict["name"], shipDict["maxPrimaries"], shipDict["maxTurrets"], shipDict["maxModules"], manufacturer=shipDict["manufacturer"] if "manufacturer" in shipDict else "",
                    armour=shipDict["armour"] if "armour" in shipDict else 0, cargo=shipDict["cargo"] if "cargo" in shipDict else 0,
                    numSecondaries=shipDict["numSecondaries"] if "numSecondaries" in shipDict else 0, handling=shipDict["handling"] if "handling" in shipDict else 0,
                    value=shipDict["value"] if "value" in shipDict else 0, aliases=shipDict["aliases"] if "aliases" in shipDict else [],
                    weapons=weapons, modules=modules, turrets=turrets, wiki=shipDict["wiki"] if "wiki" in shipDict else "0",
                    upgradesApplied=shipUpgrades, nickname=shipDict["nickname"] if "nickname" in shipDict else "")
