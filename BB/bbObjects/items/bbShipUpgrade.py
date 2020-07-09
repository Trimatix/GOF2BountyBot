from ...bbConfig import bbData

class bbShipUpgrade:
    wiki = ""
    hasWiki = False
    name = ""
    value = 0
    shipToUpgradeValueMult = 1.0
    vendor = ""
    hasVendor = False

    armour = 0.0
    armourMultiplier = 1.0

    cargo = 0
    cargoMultiplier = 1.0

    numSecondaries = 0
    numSecondariesMultiplier = 1.0

    handling = 0
    handlingMultiplier = 1.0

    maxPrimaries = 0
    maxPrimariesMultiplier = 1.0
    
    maxTurrets = 0
    maxTurretsMultiplier = 1.0

    maxModules = 0
    maxModulesMultiplier = 1.0

    
    def __init__(self, name, shipToUpgradeValueMult,
                    armour=0.0, armourMultiplier=1.0, cargo=0, cargoMultiplier=1.0, numSecondaries=0, numSecondariesMultiplier=1.0,
                    handling=0, handlingMultiplier=1.0, maxPrimaries=0, maxPrimariesMultiplier=1.0, maxTurrets=0, maxTurretsMultiplier=1.0,
                    maxModules=0, maxModulesMultiplier=1.0, vendor="", wiki="", techLevel=-1):
        self.name = name
        self.shipToUpgradeValueMult = shipToUpgradeValueMult
        self.vendor = vendor
        self.hasVendor = vendor != ""

        self.armour = armour
        self.armourMultiplier = armourMultiplier

        self.cargo = cargo
        self.cargoMultiplier = cargoMultiplier

        self.numSecondaries = numSecondaries
        self.numSecondariesMultiplier = numSecondariesMultiplier

        self.handling = handling
        self.handlingMultiplier = handlingMultiplier

        self.maxPrimaries = maxPrimaries
        self.maxPrimariesMultiplier = maxPrimariesMultiplier
        
        self.maxTurrets = maxTurrets
        self.maxTurretsMultiplier = maxTurretsMultiplier

        self.maxModules = maxModules
        self.maxModulesMultiplier = maxModulesMultiplier

        self.wiki = wiki
        self.hasWiki = wiki != ""

        self.techLevel = techLevel
        self.hasTechLevel = techLevel != -1



    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    
    def valueForShip(self, ship):
        return ship.value * self.shipToUpgradeValueMult

    
    def toDict(self):
        return {"name": self.name, "builtIn": True}

    
    def statsStringShort(self):
        stats = "*"
        if self.armour != 0:
            stats += "Armour: " + ("+" if self.armour > 0 else "-") + str(self.armour) + ", "
        if self.armourMultiplier != 1:
            stats += "Armour: " + ("+" if self.armourMultiplier > 1 else "-") + str(round(((self.armourMultiplier - 1) * 100) if self.armourMultiplier > 1 else (self.armourMultiplier * 100))) + ", "

        if self.cargo != 0:
            stats += "Cargo: " + ("+" if self.cargo > 0 else "-") + str(self.cargo) + ", "
        if self.cargoMultiplier != 1:
            stats += "Cargo: " + ("+" if self.cargoMultiplier > 1 else "-") + str(round(((self.cargoMultiplier - 1) * 100) if self.cargoMultiplier > 1 else (self.cargoMultiplier * 100))) + ", "

        if self.numSecondaries != 0:
            stats += "Max secondaries: " + ("+" if self.numSecondaries > 0 else "-") + str(self.numSecondaries) + ", "
        if self.numSecondariesMultiplier != 1:
            stats += "Max secondaries: " + ("+" if self.numSecondariesMultiplier > 1 else "-") + str(round(((self.numSecondariesMultiplier - 1) * 100) if self.numSecondariesMultiplier > 1 else (self.numSecondariesMultiplier * 100))) + ", "

        if self.handling != 0:
            stats += "Handling: " + ("+" if self.handling > 0 else "-") + str(self.handling) + ", "
        if self.handlingMultiplier != 1:
            stats += "Handling: " + ("+" if self.handlingMultiplier > 1 else "-") + str(round(((self.handlingMultiplier - 1) * 100) if self.handlingMultiplier > 1 else (self.handlingMultiplier * 100))) + ", "

        if self.maxPrimaries != 0:
            stats += "Max primaries: " + ("+" if self.maxPrimaries > 0 else "-") + str(self.maxPrimaries) + ", "
        if self.maxPrimariesMultiplier != 1:
            stats += "Max primaries: " + ("+" if self.maxPrimariesMultiplier > 1 else "-") + str(round(((self.maxPrimariesMultiplier - 1) * 100) if self.maxPrimariesMultiplier > 1 else (self.maxPrimariesMultiplier * 100))) + ", "
        
        if self.maxTurrets != 0:
            stats += "Max turrets: " + ("+" if self.maxTurrets > 0 else "-") + str(self.maxTurrets) + ", "
        if self.maxTurretsMultiplier != 1:
            stats += "Max turrets: " + ("+" if self.maxTurretsMultiplier > 1 else "-") + str(round(((self.maxTurretsMultiplier - 1) * 100) if self.maxTurretsMultiplier > 1 else (self.maxTurretsMultiplier * 100))) + ", "

        if self.maxModules != 0:
            stats += "Max modules: " + ("+" if self.maxModules > 0 else "-") + str(self.maxModules) + ", "
        if self.maxModulesMultiplier != 1:
            stats += "Max modules: " + ("+" if self.maxModulesMultiplier > 1 else "-") + str(round(((self.maxModulesMultiplier - 1) * 100) if self.maxModulesMultiplier > 1 else (self.maxModulesMultiplier * 100))) + ", "

        return (stats[:-2] + "*") if stats != "*" else "*No effect*"


def fromDict(upgradeDict):
    if upgradeDict["builtIn"]:
        return bbData.builtInUpgradeObjs[upgradeDict["name"]]
    else:
        return bbShipUpgrade(upgradeDict["name"], upgradeDict["shipToUpgradeValueMult"], armour=upgradeDict["armour"] if "armour" in upgradeDict else 0.0,
                                armourMultiplier=upgradeDict["armourMultiplier"] if "armourMultiplier" in upgradeDict else 1.0,
                                cargo=upgradeDict["cargo"] if "cargo" in upgradeDict else 0,
                                cargoMultiplier=upgradeDict["cargoMultiplier"] if "cargoMultiplier" in upgradeDict else 1.0,
                                numSecondaries=upgradeDict["numSecondaries"] if "numSecondaries" in upgradeDict else 0,
                                numSecondariesMultiplier=upgradeDict["numSecondariesMultiplier"] if "numSecondariesMultiplier" in upgradeDict else 1.0,
                                handling=upgradeDict["handling"] if "handling" in upgradeDict else 0,
                                handlingMultiplier=upgradeDict["handlingMultiplier"] if "handlingMultiplier" in upgradeDict else 1.0,
                                maxPrimaries=upgradeDict["maxPrimaries"] if "maxPrimaries" in upgradeDict else 0,
                                maxPrimariesMultiplier=upgradeDict["maxPrimariesMultiplier"] if "maxPrimariesMultiplier" in upgradeDict else 1.0,
                                maxTurrets=upgradeDict["maxTurrets"] if "maxTurrets" in upgradeDict else 0,
                                maxTurretsMultiplier=upgradeDict["maxTurretsMultiplier"] if "maxTurretsMultiplier" in upgradeDict else 1.0,
                                maxModules=upgradeDict["maxModules"] if "maxModules" in upgradeDict else 0,
                                maxModulesMultiplier=upgradeDict["maxModulesMultiplier"] if "maxModulesMultiplier" in upgradeDict else 1.0,
                                vendor=upgradeDict["vendor"] if "vendor" in upgradeDict else "",
                                wiki=upgradeDict["wiki"] if "wiki" in upgradeDict else "", techLevel=upgradeDict["techLevel"] if "techLevel" in upgradeDict else -1)
