from . import bbItem
from ...bbConfig import bbData


class bbCommodity(bbItem.bbItem):
    def __init__(self, name, aliases, value=0, wiki="", icon="", emoji=""):
        super(bbCommodity, self).__init__(name, aliases, value=value, wiki=wiki, icon=icon, emoji=emoji)


    def getType(self):
        return bbCommodity


def fromDict(commodityDict):
    if commodityDict["builtIn"]:
        return bbData.builtInCommodityObjs[commodityDict["name"]]
    else:
        return bbCommodity(commodityDict["name"], commodityDict["aliases"],
                           value=commodityDict["value"],
                           wiki=commodityDict["wiki"] if "wiki" in commodityDict else "",
                           icon=commodityDict["icon"] if "icon" in commodityDict else bbData.rocketIcon,
                           emoji=commodityDict["emoji"] if "emoji" in commodityDict else "")
