from .. import bbAliasable
from ...bbConfig import bbData

class bbModule(bbAliasable.Aliasable):
    armour = 0
    armourMultiplier = 1.0

    shield = 0
    shieldMultiplier = 1.0

    dps = 0
    dpsMultiplier = 1.0

    cargo = 0
    cargoMultiplier = 1.0

    handling = 0
    handlingMultiplier = 0

    wiki = ""
    hasWiki = False

    value = 0

    def __init__(self, name, aliases, armour=0, armourMultiplier=1.0, shield=0, shieldMultiplier=1.0, dps=0,
                    dpsMultiplier=1.0, cargo=0, cargoMultiplier=1.0, handling=0, handlingMultiplier=1.0, value=0, wiki=""):
        super(bbModule, self).__init__(name, aliases)
        self.armour = armour
        self.armourMultiplier = armourMultiplier
        self.shield = shield
        self.shieldMultiplier = shieldMultiplier
        self.dps = dps
        self.dpsMultiplier
        self.cargo = cargo
        self.cargoMultiplier = cargoMultiplier
        self.handling = handling
        self.handlingMultiplier = handlingMultiplier
        self.value = value
        self.wiki = wiki
        self.hasWiki = wiki != ""

    
    def getType(self):
        return bbModule


    def toDict(self):
        # data = {"name": self.name, "aliases": self.aliases}
        # if self.armour != 0:
        #     data["armour"] = self.armour

        # if self.armourMultiplier != 1.0:
        #     data["armourMultiplier"] = self.armourMultiplier

        # if self.shield != 0:
        #     data["shield"] = self.shield

        # if self.shieldMultiplier != 1.0:
        #     data["shieldMultiplier"] = self.shieldMultiplier

        # if self.dps != 0:
        #     data["dps"] = self.dps

        # if self.dpsMultiplier != 1.0:
        #     data["dpsMultiplier"] = self.dpsMultiplier

        # if self.cargo != 0:
        #     data["cargo"] = self.cargo

        # if self.cargoMultiplier != 1.0:
        #     data["cargoMultiplier"] = self.cargoMultiplier

        # if self.handling != 0:
        #     data["handling"] = self.handling

        # if self.handlingMultiplier != 1.0:
        #     data["handlingMultiplier"] = self.handlingMultiplier

        # return data

        return {"name": self.name, "builtIn": True}


def fromDict(moduleDict):
    if "builtIn" in moduleDict and moduleDict["builtIn"]:
        return bbData.builtInModuleObjs[moduleDict["name"]]
    else:
        return bbModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], armour=moduleDict["armour"] if "armour" in moduleDict else 0,
                        armourMultiplier=moduleDict["armourMultiplier"] if "armourMultiplier" in moduleDict else 1, shield=moduleDict["shield"] if "shield" in moduleDict else 0,
                        shieldMultiplier=moduleDict["shieldMultiplier"] if "shieldMultiplier" in moduleDict else 1, dps=moduleDict["dps"] if "dps" in moduleDict else 0,
                        dpsMultiplier=moduleDict["dpsMultiplier"] if "dpsMultiplier" in moduleDict else 1, cargo=moduleDict["cargo"] if "cargo" in moduleDict else 0,
                        cargoMultiplier=moduleDict["cargoMultiplier"] if "cargoMultiplier" in moduleDict else 1, handling=moduleDict["handling"] if "handling" in moduleDict else 0,
                        handlingMultiplier=moduleDict["handlingMultiplier"] if "handlingMultiplier" in moduleDict else 1, value=moduleDict["value"] if "value" in moduleDict else 0,
                        wiki=moduleDict["wiki"] if "wiki" in moduleDict else "")
