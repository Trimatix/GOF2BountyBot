from ...bbConfig import bbData
from .. import bbAliasable
from ..items import bbShip

class Criminal (bbAliasable.Aliasable):
    name = ""
    faction = ""
    icon = ""
    wiki = ""
    hasWiki = False
    isPlayer = False
    builtIn = False

    ship = None

    def __init__(self, name, faction, icon, builtIn=False, isPlayer=False, aliases=[], wiki=""):
        super(Criminal, self).__init__(name, aliases)
        if name == "":
            raise RuntimeError("CRIM_CONS_NONAM: Attempted to create a Criminal with an empty name")
        # if faction == "":
        #     raise RuntimeError("CRIM_CONS_NOFAC: Attempted to create a Criminal with an empty faction")
        if faction == "":
            raise RuntimeError("CRIM_CONS_NOICO: Attempted to create a Criminal with an empty icon")
        
        self.name = name
        self.faction = faction
        self.icon = icon
        self.wiki = wiki
        self.hasWiki = wiki != ""
        self.isPlayer = isPlayer
        self.builtIn = builtIn


    def getType(self):
        return Criminal


    def toDict(self):
        if self.builtIn:
            return {"builtIn":True, "name":self.name}
        else:
            return {"builtIn":False, "isPlayer": self.isPlayer, "name":self.name, "icon":self.icon, "faction":self.faction, "aliases":self.aliases, "wiki":self.wiki}


def fromDict(crimDict, builtIn=False):
    if "builtIn" in crimDict:
        if crimDict["builtIn"]:
            return bbData.builtInCriminalObjs[crimDict["name"]]
        return Criminal(crimDict["name"], crimDict["faction"], crimDict["icon"], isPlayer=crimDict["isPlayer"], aliases=crimDict["aliases"], wiki=crimDict["wiki"], builtIn=crimDict["builtIn"] or builtIn)
    return Criminal(crimDict["name"], crimDict["faction"], crimDict["icon"], isPlayer=crimDict["isPlayer"], aliases=crimDict["aliases"], wiki=crimDict["wiki"], builtIn=builtIn)
