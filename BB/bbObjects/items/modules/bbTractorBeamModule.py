from . import bbModule
from ....bbConfig import bbData

class bbTractorBeamModule(bbModule.bbModule):
    def __init__(self, name, aliases, timeToLock=0, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbTractorBeamModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji)

        self.timeToLock = timeToLock

    
    def statsStringShort(self):
        return "*Time To Lock: " + str(self.timeToLock) + "s*"


    def getType(self):
        return bbTractorBeamModule


def fromDict(moduleDict):
    return bbTractorBeamModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], timeToLock=moduleDict["timeToLock"] if "timeToLock" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "")
