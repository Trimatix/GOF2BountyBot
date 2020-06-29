from . import bbModule
from ....bbConfig import bbData

class bbCabinModule(bbModule.bbModule):
    def __init__(self, name, aliases, cabinSize=0, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbCabinModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji)

        self.cabinSize = cabinSize


    def getType(self):
        return bbCabinModule


    def statsStringShort(self):
        return "*Cabin Size: " + str(self.cabinSize) + "*"


def fromDict(moduleDict):
    return bbCabinModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], cabinSize=moduleDict["cabinSize"] if "cabinSize" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "")
