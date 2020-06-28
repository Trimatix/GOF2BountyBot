from . import bbModule
from ....bbConfig import bbData

class bbRepairBeamModule(bbModule.bbModule):
    def __init__(self, name, aliases, effect=0, count=0, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbRepairBeamModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji)

        self.effect = effect
        self.count = count

    
    def statsStringShort(self):
        return "*Effect: " + ("+" if self.effect >= 1 else "-") + str(round(((self.effect - 1) * 100) if self.effect > 1 else (self.effect * 100))) + \
                "%, Count: " + str(self.count) + "*"


    def getType(self):
        return bbRepairBeamModule


def fromDict(moduleDict):
    return bbRepairBeamModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], effect=moduleDict["effect"] if "effect" in moduleDict else 1,
                            count=moduleDict["count"] if "count" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "")
