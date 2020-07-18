from ...bbConfig import bbData
from .. import bbAliasable
from ..items import bbShip

class Criminal (bbAliasable.Aliasable):
    def __init__(self, name, faction, icon, builtIn=False, isPlayer=False, aliases=[], wiki="", activeShip=None, techLevel=-1):
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

        if activeShip is not None:
            self.activeShip = bbShip.fromDict(activeShip.toDict())
            self.hasShip = True
        else:
            self.hasShip = False

        self.techLevel = techLevel

    
    def clearShip(self):
        if not self.hasShip:
            raise RuntimeError("CRIM_CLEARSH_NOSHIP: Attempted to clearShip on a Criminal with no active ship")
        del self.activeShip
        self.hasShip = False


    def unequipShip(self):
        if not self.hasShip:
            raise RuntimeError("CRIM_UNEQSH_NOSHIP: Attempted to unequipShip on a Criminal with no active ship")
        self.activeShip = None
        self.hasShip = False


    def equipShip(self, newShip):
        if self.hasShip:
            raise RuntimeError("CRIM_EQUIPSH_HASSH: Attempted to equipShip on a Criminal that already has an active ship")
        self.activeShip = newShip
        self.hasShip = True

    
    def copyShip(self, newShip):
        if self.hasShip:
            raise RuntimeError("CRIM_COPYSH_HASSH: Attempted to copyShip on a Criminal that already has an active ship")
        self.activeShip = bbShip.fromDict(newShip.toDict())
        self.hasShip = True
        

    def getType(self):
        return Criminal


    def __hash__(self):
        return hash(repr(self))


    def toDict(self):
        if self.builtIn:
            data = {"builtIn":True, "name":self.name}
        else:
            data = {"builtIn":False, "isPlayer": self.isPlayer, "name":self.name, "icon":self.icon, "faction":self.faction, "aliases":self.aliases, "wiki":self.wiki}

        if self.hasShip:
            data["activeShip"] = self.activeShip.toDict()
            data["techLevel"] = self.techLevel
        
        return data

    
    def __hash__(self):
        return hash(self.name)


def fromDict(crimDict, builtIn=False):
    if "builtIn" in crimDict:
        if crimDict["builtIn"]:
            crimObj = bbData.builtInCriminalObjs[crimDict["name"]]
        else:
            crimObj = Criminal(crimDict["name"], crimDict["faction"], crimDict["icon"], isPlayer=crimDict["isPlayer"], aliases=crimDict["aliases"], wiki=crimDict["wiki"], builtIn=crimDict["builtIn"] or builtIn)
    else:
        crimObj = Criminal(crimDict["name"], crimDict["faction"], crimDict["icon"], isPlayer=crimDict["isPlayer"], aliases=crimDict["aliases"], wiki=crimDict["wiki"], builtIn=builtIn)

    if "activeShip" in crimDict:
        crimObj.equipShip(bbShip.fromDict(crimDict["activeShip"]))
        crimObj.techLevel = crimDict["techLevel"] if "techLevel" in crimDict else crimObj.activeShip.techLevel
    
    return crimObj
