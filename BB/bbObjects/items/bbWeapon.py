from .bbItem import bbItem
from ...bbConfig import bbData

class bbWeapon(bbItem):
    dps = 0.0

    def __init__(self, name, aliases, dps=0.0, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbWeapon, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji)
        
        self.dps = dps

    
    def statsStringShort(self):
        return "*Dps: " + str(self.dps) + "*"


    def getType(self):
        return bbWeapon


def fromDict(weaponDict):
    if weaponDict["builtIn"]:
        return bbData.builtInWeaponObjs[weaponDict["name"]]
    else:
        return bbWeapon(weaponDict["name"], weaponDict["aliases"], dps=weaponDict["dps"], value=weaponDict["value"],
        wiki=weaponDict["wiki"] if "wiki" in weaponDict else "", manufacturer=weaponDict["manufacturer"] if "manufacturer" in weaponDict else "",
        icon=weaponDict["icon"] if "icon" in weaponDict else bbData.rocketIcon, emoji=weaponDict["emoji"] if "emoji" in weaponDict else "",
                        techLevel=weaponDict["techLevel"] if "techLevel" in weaponDict else -1)
