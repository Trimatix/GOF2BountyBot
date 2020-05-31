import bbutil
import bbdata

class Criminal (bbutil.Aliasable):
    name = ""
    faction = ""
    icon = ""
    wiki = ""
    hasWiki = False
    isPlayer = False
    builtIn = False

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
            print("BUILT IN")
            data["criminal"] = {"builtIn":True, "name":self.criminal.name}
        else:
            print("NOT BUILT IN")
            data["criminal"] = {"builtIn":False, "isPlayer": self.criminal.isPlayer, "name":self.criminal.name, "icon":self.criminal.icon}


def fromDict(crimDict):
    if crimDict["builtIn"]:
        return bbdata.criminals[crimDict["name"]]
    else:
        return Criminal(crimDict["name"], crimDict["faction"], crimDict["icon"], isPlayer=crimDict["isPlayer"], aliases=crimDict["aliases"], wiki=crimDict["wiki"])
