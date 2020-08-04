from . import bbModule
from ....bbConfig import bbData

class bbJumpDriveModule(bbModule.bbModule):
    def __init__(self, name, aliases, value=0, wiki="", manufacturer="", icon="", emoji="", techLevel=-1, builtIn=False):
        super(bbJumpDriveModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)


    def getType(self):
        return bbJumpDriveModule

    
    def toDict(self):
        itemDict = super(bbJumpDriveModule, self).toDict()
        return itemDict


def fromDict(moduleDict):
    return bbJumpDriveModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [],
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "", techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
