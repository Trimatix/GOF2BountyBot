from . import bbModule
from ....bbConfig import bbData

class bbSpectralFilterModule(bbModule.bbModule):
    def __init__(self, name, aliases, showInfo=False, showOnRadar=False, value=0, wiki="", manufacturer="", icon="", emoji="", techLevel=-1, builtIn=False):
        super(bbSpectralFilterModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.showOnRadar = showOnRadar
        self.showInfo = showInfo

    
    def statsStringShort(self):
        return "*Show Info? " + ("Yes" if self.showInfo else "No") + ", Show On Radar? " + ("Yes" if self.showOnRadar else "No") + "*"


    def getType(self):
        return bbSpectralFilterModule


def fromDict(moduleDict):
    return bbSpectralFilterModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], showInfo=moduleDict["showInfo"] if "showInfo" in moduleDict else False,
                            showOnRadar=moduleDict["showOnRadar"] if "showOnRadar" in moduleDict else False, 
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "", techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
