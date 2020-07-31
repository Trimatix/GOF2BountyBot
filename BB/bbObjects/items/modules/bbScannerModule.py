from . import bbModule
from ....bbConfig import bbData

class bbScannerModule(bbModule.bbModule):
    def __init__(self, name, aliases, timeToLock=0, showClassAAsteroids=False, showCargo=False, value=0, wiki="", manufacturer="", icon="", emoji="", techLevel=-1, builtIn=False):
        super(bbScannerModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.timeToLock = timeToLock
        self.showClassAAsteroids = showClassAAsteroids
        self.showCargo = showCargo


    def statsStringShort(self):
        return "*Time To Lock: " + str(self.timeToLock) + "s, Show Class A Asteroids: " + ("Yes" if self.showClassAAsteroids else "No") + ", Show Cargo: " + ("Yes" if self.showCargo else "No") + "*"


    def getType(self):
        return bbScannerModule


def fromDict(moduleDict):
    return bbScannerModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], timeToLock=moduleDict["timeToLock"] if "timeToLock" in moduleDict else 0,
                            showClassAAsteroids=moduleDict["showClassAAsteroids"] if "showClassAAsteroids" in moduleDict else False, showCargo=moduleDict["showCargo"] if "showCargo" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "", techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
