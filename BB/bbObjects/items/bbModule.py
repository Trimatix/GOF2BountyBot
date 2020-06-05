from .. import bbAliasable

class bbModule(bbAliasable.Aliasable):

    def __init__(self, name, aliases):
        super(bbModule, self).__init__(name, aliases)
        