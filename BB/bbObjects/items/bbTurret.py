from .. import bbAliasable
from ...bbConfig import bbData

class bbTurret(bbAliasable.Aliasable):
    dps = 0.0
    value = 0
    wiki = ""
    hasWiki = False
    manufacturer = ""
    icon = ""
    hasIcon = False
    shopSpawnRate = 0
    emoji = ""
    hasEmoji = False

    def __init__(self, name, aliases, dps=0.0, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbTurret, self).__init__(name, aliases)

        self.dps = dps
        self.value = value
        self.wiki = wiki
        self.hasWiki = wiki != ""
        self.manufacturer = manufacturer
        self.icon = ""
        self.hasIcon = icon != ""
        self.emoji = emoji
        self.hasEmoji = emoji != ""

    
    def getValue(self):
        return self.value

    
    def statsStringShort(self):
        return "*Dps: " + str(self.dps) + "*"


    def toDict(self):
        return {"name": self.name, "builtIn": True}


    def getType(self):
        return bbTurret


def fromDict(turretDict):
    if turretDict["builtIn"]:
        return bbData.builtInTurretObjs[turretDict["name"]]
    else:
        return bbTurret(turretDict["name"], turretDict["aliases"], dps=turretDict["dps"], value=turretDict["value"], wiki=turretDict["wiki"] if "wiki" in turretDict else "", manufacturer=turretDict["manufacturer"] if "manufacturer" in turretDict else "", icon=turretDict["icon"] if "icon" in turretDict else bbData.rocketIcon, emoji=turretDict["emoji"] if "emoji" in turretDict else "")
