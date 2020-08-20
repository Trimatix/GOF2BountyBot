from . import bbModule
from ....bbConfig import bbData
from .... import bbUtil

class bbSignatureModule(bbModule.bbModule):
    def __init__(self, name, aliases, manufacturer, value=0, wiki="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        super(bbSignatureModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        if manufacturer == "":
            raise ValueError("Attempted to create a bbSignatureModule with no manufacturer (faction)")

    
    def statsStringShort(self):
        return "*Faction: " + self.manufacturer + "*"


    def getType(self):
        return bbSignatureModule

    
    def toDict(self):
        itemDict = super(bbSignatureModule, self).toDict()
        return itemDict


def fromDict(moduleDict):
    return bbSignatureModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], moduleDict["manufacturer"],
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=bbUtil.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else bbUtil.EMPTY_DUMBEMOJI, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
