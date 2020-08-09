from . import bbModule
from ....bbConfig import bbData
from .... import bbUtil

class bbCompressorModule(bbModule.bbModule):
    def __init__(self, name, aliases, cargoMultiplier=1.0, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        super(bbCompressorModule, self).__init__(name, aliases, cargoMultiplier=cargoMultiplier, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)


    def getType(self):
        return bbCompressorModule

    
    def toDict(self):
        itemDict = super(bbCompressorModule, self).toDict()
        return itemDict


def fromDict(moduleDict):
    return bbCompressorModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], cargoMultiplier=moduleDict["cargoMultiplier"] if "cargoMultiplier" in moduleDict else 1,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=bbUtil.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else bbUtil.EMPTY_DUMBEMOJI, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
