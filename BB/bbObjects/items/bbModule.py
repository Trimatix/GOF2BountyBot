from .. import bbAliasable

class bbModule(bbAliasable.Aliasable):
    armour = 0
    armourMultiplier = 1.0

    shield = 0
    shieldMultiplier = 1.0

    dmg = 0
    dmgMultiplier = 1.0

    cargo = 0
    cargoMultiplier = 1.0

    handling = 0
    handlingMultiplier = 0

    value = 0

    def __init__(self, name, aliases):
        super(bbModule, self).__init__(name, aliases)

    
    def getType(self):
        return bbModule
