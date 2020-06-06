from .. import bbAliasable

class bbModule(bbAliasable.Aliasable):
    armour = 0
    armourMultiplier = 1.0

    shield = 0
    shieldMultiplier = 1.0

    dmg = 0
    dmgMultiplier = 1.0

    cargo = 0
    cargoMultiplier = 1.0

    handling = 0
    handlingMultiplier = 0

    value = 0

    def __init__(self, name, aliases, armour=0, armourMultiplier=1.0, shield=0, shieldMultiplier=1.0, dmg=0,
                    dmgMultiplier=1.0, cargo=0, cargoMultiplier=1.0, handling=0, handlingMultiplier=1.0, value=0):
        super(bbModule, self).__init__(name, aliases)

    
    def getType(self):
        return bbModule


def fromDict(moduleDict):
    return bbModule(moduleDict["name"], moduleDict["aliases"], armour=moduleDict["armour"] if "armour" in "moduleDict" else 0,
    armourMultiplier=moduleDict["armourMultiplier"] if "armourMultiplier" in "moduleDict" else 1, shield=moduleDict["shield"] if "shield" in "moduleDict" else 0,
    shieldMultiplier=moduleDict["shieldMultiplier"] if "shieldMultiplier" in "moduleDict" else 1, dmg=moduleDict["dmg"] if "dmg" in "moduleDict" else 0,
    dmgMultiplier=moduleDict["dmgMultiplier"] if "dmgMultiplier" in "moduleDict" else 1, cargo=moduleDict["cargo"] if "cargo" in "moduleDict" else 0,
    cargoMultiplier=moduleDict["cargoMultiplier"] if "cargoMultiplier" in "moduleDict" else 1, handling=moduleDict["handling"] if "handling" in "moduleDict" else 0,
    handlingMultiplier=moduleDict["handlingMultiplier"] if "handlingMultiplier" in "moduleDict" else 1, value=moduleDict["value"] if "value" in "moduleDict" else 0)
