from . import bbModule
from ....bbConfig import bbData

class bbWeaponModModule(bbModule.bbModule):
    def __init__(self, name, aliases, dpsMultiplier=1, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbWeaponModModule, self).__init__(name, aliases, dpsMultiplier=dpsMultiplier, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji)


    def getType(self):
        return bbWeaponModModule


def fromDict(moduleDict):
    return bbWeaponModModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], dpsMultiplier=moduleDict["dpsMultiplier"] if "dpsMultiplier" in moduleDict else 1,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "")
