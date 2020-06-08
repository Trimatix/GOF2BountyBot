from .. import bbAliasable
from ...bbConfig import bbData

class bbWeapon(bbAliasable.Aliasable):
    dps = 0.0
    value = 0

    def __init__(self, name, aliases, dps=0.0, value=0, wiki=""):
        super(bbWeapon, self).__init__(name, aliases)


    def getType(self):
        return bbWeapon


def fromDict(weaponDict):
    if weaponDict["builtIn"]:
        return bbData.builtInWeaponObjs[weaponDict["name"]]
    else:
        return bbWeapon(weaponDict["name"], weaponDict["aliases"], dps=weaponDict["dps"], value=weaponDict["value"], wiki=weaponDict["wiki"] if "wiki" in weaponDict else "")
