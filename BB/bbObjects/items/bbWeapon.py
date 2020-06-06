from .. import bbAliasable

class bbWeapon(bbAliasable.Aliasable):
    dps = 0.0
    value = 0

    def __init__(self, name, aliases, dps=0.0, value=0):
        super(bbWeapon, self).__init__(name, aliases)


    def getType(self):
        return bbWeapon


def fromDict(weaponDict):
    return bbWeapon(weaponDict["name"], weaponDict["aliases"])
