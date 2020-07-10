from . import bbModule
from ....bbConfig import bbData

class bbShieldModule(bbModule.bbModule):
    def __init__(self, name, aliases, shield=0, value=0, wiki="", manufacturer="", icon="", emoji="", techLevel=-1):
        super(bbShieldModule, self).__init__(name, aliases, shield=shield, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel)


    def getType(self):
        return bbShieldModule


def fromDict(moduleDict):
    return bbShieldModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], shield=moduleDict["shield"] if "shield" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "", techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1)
