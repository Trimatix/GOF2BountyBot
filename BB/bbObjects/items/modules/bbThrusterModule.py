from . import bbModule
from ....bbConfig import bbData

class bbThrusterModule(bbModule.bbModule):
    def __init__(self, name, aliases, handlingMultiplier=1, value=0, wiki="", manufacturer="", icon="", emoji="", techLevel=-1, builtIn=False):
        super(bbThrusterModule, self).__init__(name, aliases, handlingMultiplier=handlingMultiplier, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)


    def getType(self):
        return bbThrusterModule

    
    def toDict(self):
        itemDict = super(bbThrusterModule, self).toDict()
        return itemDict


def fromDict(moduleDict):
    return bbThrusterModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], handlingMultiplier=moduleDict["handlingMultiplier"] if "handlingMultiplier" in moduleDict else 1,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "", techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
