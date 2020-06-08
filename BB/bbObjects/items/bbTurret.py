from .. import bbAliasable
from ...bbConfig import bbData

class bbTurret(bbAliasable.Aliasable):
    dps = 0.0
    value = 0

    def __init__(self, name, aliases, dps=0.0, value=0, wiki=""):
        super(bbTurret, self).__init__(name, aliases)


    def getType(self):
        return bbTurret


def fromDict(turretDict):
    if turretDict["builtIn"]:
        return bbData.builtInWeaponObjs[turretDict["name"]]
    else:
        return bbTurret(turretDict["name"], turretDict["aliases"], dps=turretDict["dps"], value=turretDict["value"], wiki=turretDict["wiki"] if "wiki" in turretDict else "")
