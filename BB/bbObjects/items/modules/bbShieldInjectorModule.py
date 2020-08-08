from . import bbModule
from ....bbConfig import bbData
from .... import bbUtil

class bbShieldInjectorModule(bbModule.bbModule):
    def __init__(self, name, aliases, plasmaConsumption=0, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        super(bbShieldInjectorModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.plasmaConsumption = plasmaConsumption

    
    def statsStringShort(self):
        return "*Plasma Consumption: " + str(self.plasmaConsumption) + "*"


    def getType(self):
        return bbShieldInjectorModule

    
    def toDict(self):
        itemDict = super(bbShieldInjectorModule, self).toDict()
        if not self.builtIn:
            itemDict["plasmaConsumption"] = self.plasmaConsumption
        return itemDict


def fromDict(moduleDict):
    return bbShieldInjectorModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], plasmaConsumption=moduleDict["plasmaConsumption"] if "plasmaConsumption" in moduleDict else 1,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=bbUtil.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else bbUtil.EMPTY_DUMBEMOJI, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
