from . import bbModule
from ....bbConfig import bbData

class bbJumpDriveModule(bbModule.bbModule):
    def __init__(self, name, aliases, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbJumpDriveModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji)


    def getType(self):
        return bbJumpDriveModule


def fromDict(moduleDict):
    return bbJumpDriveModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [],
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "")
