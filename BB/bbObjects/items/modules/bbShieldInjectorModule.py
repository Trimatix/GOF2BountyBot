from . import bbModule
from ....bbConfig import bbData

class bbShieldInjectorModule(bbModule.bbModule):
    def __init__(self, name, aliases, plasmaConsumption=0, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbShieldInjectorModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji)

        self.plasmaConsumption = plasmaConsumption

    
    def statsStringShort(self):
        return "*Plasma Consumption: " + str(self.plasmaConsumption) + "*"


    def getType(self):
        return bbShieldInjectorModule


def fromDict(moduleDict):
    return bbShieldInjectorModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], plasmaConsumption=moduleDict["plasmaConsumption"] if "plasmaConsumption" in moduleDict else 1,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=moduleDict["emoji"] if "emoji" in moduleDict else "")
