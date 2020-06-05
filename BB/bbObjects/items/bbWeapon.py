from .. import bbAliasable

class bbWeapon(bbAliasable.Aliasable):
    dps = 0.0

    def __init__(self, name, aliases):
        super(bbWeapon, self).__init__(name, aliases)
