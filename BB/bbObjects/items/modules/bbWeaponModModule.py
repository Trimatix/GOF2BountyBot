from . import bbModule
from ....bbConfig import bbData
from .... import bbUtil

class bbWeaponModModule(bbModule.bbModule):
    def __init__(self, name, aliases, dpsMultiplier=1, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        super(bbWeaponModModule, self).__init__(name, aliases, dpsMultiplier=dpsMultiplier, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)


    def getType(self):
        return bbWeaponModModule

    
    def toDict(self):
        itemDict = super(bbWeaponModModule, self).toDict()
        return itemDict


def fromDict(moduleDict):
    return bbWeaponModModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], dpsMultiplier=moduleDict["dpsMultiplier"] if "dpsMultiplier" in moduleDict else 1,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=bbUtil.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else bbUtil.EMPTY_DUMBEMOJI, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
