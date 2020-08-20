from .. import bbAliasable
from abc import abstractmethod
from ... import bbUtil

class bbItem(bbAliasable.Aliasable):
    def __init__(self, name, aliases, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
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

        self.techLevel = techLevel
        self.hasTechLevel = techLevel != -1

        self.builtIn = builtIn


    @abstractmethod
    def statsStringShort(self):
        return "*No effect*"


    @abstractmethod
    def getType(self):
        return bbItem

    
    def getValue(self):
        return self.value


    @abstractmethod
    def toDict(self):
        if self.builtIn:
            return {"name": self.name, "builtIn": True}
        else:
            return {"name": self.name, "aliases": self.aliases, "value":self.value, "wiki":self.wiki, "manufacturer":self.manufacturer, "icon":self.icon, "emoji":self.emoji.toDict(), "techLevel":self.techLevel, "builtIn":False}

    
    def __hash__(self):
        return hash(repr(self))
