from .. import bbAliasable
from ...bbConfig import bbData


class bbCommodity(bbAliasable.Aliasable):
    value = 0
    wiki = ""
    hasWiki = False
    icon = ""
    hasIcon = False
    emoji = ""
    hasEmoji = False

    def __init__(self, name, aliases, value=0, wiki="", icon="", emoji=""):
        super(bbCommodity, self).__init__(name, aliases)
        self.value = value
        self.wiki = wiki
        self.hasWiki = wiki != ""
        self.icon = ""
        self.hasIcon = icon != ""
        self.emoji = emoji
        self.hasEmoji = emoji != ""

    def getValue(self):
        return self.value

    def getType(self):
        return bbCommodity

    def toDict(self):
        return {"name": self.name, "builtIn": True}

def fromDict(commodityDict):
    if commodityDict["builtIn"]:
        return bbData.builtInTurretObjs[commodityDict["name"]]
    else:
        return bbCommodity(commodityDict["name"], commodityDict["aliases"],
                           value=commodityDict["value"],
                           wiki=commodityDict["wiki"] if "wiki" in commodityDict else "",
                           icon=commodityDict["icon"] if "icon" in commodityDict else bbData.rocketIcon,
                           emoji=commodityDict["emoji"] if "emoji" in commodityDict else "")
