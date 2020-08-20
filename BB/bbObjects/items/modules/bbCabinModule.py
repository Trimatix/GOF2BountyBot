from . import bbModule
from ....bbConfig import bbData
from .... import bbUtil

class bbCabinModule(bbModule.bbModule):
    def __init__(self, name, aliases, cabinSize=0, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        super(bbCabinModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.cabinSize = cabinSize


    def getType(self):
        return bbCabinModule


    def statsStringShort(self):
        return "*Cabin Size: " + str(self.cabinSize) + "*"

    
    def toDict(self):
        itemDict = super(bbCabinModule, self).toDict()
        if not self.builtIn:
            itemDict["cabinSize"] = self.cabinSize
        return itemDict


def fromDict(moduleDict):
    return bbCabinModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], cabinSize=moduleDict["cabinSize"] if "cabinSize" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=bbUtil.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else bbUtil.EMPTY_DUMBEMOJI, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
