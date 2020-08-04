from . import bbModule
from ....bbConfig import bbData

class bbMiningDrillModule(bbModule.bbModule):
    def __init__(self, name, aliases, oreYield=0, handling=0, value=0, wiki="", manufacturer="", icon="", emoji="", techLevel=-1, builtIn=False):
        super(bbMiningDrillModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.oreYield = oreYield
        self.handling = handling

    
    def statsStringShort(self):
        return "*Yield: " + ("+" if self.oreYield >= 1 else "-") + str(round(((self.oreYield - 1) * 100) if self.oreYield > 1 else (self.oreYield * 100))) + \
                "%, Handling: " + str(round(((self.handling - 1) * 100) if self.handling > 1 else (self.handling * 100))) + "%*"


    def getType(self):
        return bbMiningDrillModule

    
    def toDict(self):
        itemDict = super(bbMiningDrillModule, self).toDict()
        if not self.builtIn:
            itemDict["oreYield"] = self.oreYield
            itemDict["handling"] = self.handling
        return itemDict


def fromDict(moduleDict):
    return bbMiningDrillModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], oreYield=moduleDict["oreYield"] if "oreYield" in moduleDict else 1,
                            handling=moduleDict["handling"] if "handling" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "", techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
