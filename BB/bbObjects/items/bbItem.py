from .. import bbAliasable
from abc import abstractmethod

class bbItem(bbAliasable.Aliasable):
    def __init__(self, name, aliases, value=0, wiki="", manufacturer="", icon="", emoji=""):
        super(bbItem, self).__init__(name, aliases)
        self.wiki = wiki
        self.hasWiki = wiki != ""

        self.manufacturer = manufacturer
        self.hasManufacturer = manufacturer != ""

        self.icon = icon
        self.hasIcon = icon != ""

        self.emoji = emoji
        self.hasEmoji = emoji != ""

        self.value = value
        self.shopSpawnRate = 0


    @abstractmethod
    def statsStringShort(self):
        return "*No effect*"


    @abstractmethod
    def getType(self):
        return bbItem

    
    def getValue(self):
        return self.value


    def toDict(self):
        return {"name": self.name, "builtIn": True}
