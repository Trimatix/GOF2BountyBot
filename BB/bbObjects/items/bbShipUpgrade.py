from ...bbConfig import bbData

class bbShipUpgrade:
    wiki = ""
    hasWiki = False
    name = ""
    value = 0
    shipToUpgradeValueMult = 1.0
    applied = False
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
                    maxModules=0, maxModulesMultiplier=1.0, vendor="", wiki=""):
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



    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    
    def valueForShip(self, ship):
        return ship.value * self.shipToUpgradeValueMult

    
    def toDict(self):
        return {"name": self.name, "builtIn": True}


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
                                wiki=upgradeDict["wiki"] if "wiki" in upgradeDict else "")
