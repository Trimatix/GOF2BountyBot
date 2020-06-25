from ...bbConfig import bbData
from . import bbAliasable
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
    hasShip = False

    def __init__(self, name, faction, icon, builtIn=False, isPlayer=False, aliases=[], wiki="", ship=None):
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

        if ship is not None:
            self.ship = bbShip.fromDict(ship.toDict())
            self.hasShip = True
        else:
            self.hasShip = False

    
    def clearShip(self):
        if not self.hasShip:
            raise RuntimeError("CRIM_CLEARSH_NOSHIP: Attempted to clearShip on a Criminal with no active ship")
        del self.ship
        self.hasShip = False


    def unequipShip(self):
        if not self.hasShip:
            raise RuntimeError("CRIM_UNEQSH_NOSHIP: Attempted to unequipShip on a Criminal with no active ship")
        self.ship = None
        self.hasShip = False


    def equipShip(self, ship):
        if self.hasShip:
            raise RuntimeError("CRIM_EQUIPSH_HASSH: Attempted to equipShip on a Criminal that already has an active ship")
        self.ship = ship
        self.hasShip = True

    
    def copyShip(self, ship):
        if self.hasShip:
            raise RuntimeError("CRIM_COPYSH_HASSH: Attempted to copyShip on a Criminal that already has an active ship")
        self.ship = bbShip.fromDict(ship.toDict())
        self.hasShip = True
        

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
