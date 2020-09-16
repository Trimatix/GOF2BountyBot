from . import bbModule
from ....bbConfig import bbData
from .... import bbUtil
from typing import List

class bbTractorBeamModule(bbModule.bbModule):
    """A module providing a ship with the ability to pull nearby debris and items into the ship's cargo hold

    :var timeToLock: The amount of time in seconds needed for the beam to lock onto an item and pull it into the hold
    :vartype timeToLock: float
    """

    def __init__(self, name : str, aliases : List[str], timeToLock=0, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        """
        :param str name: The name of the module. Must be unique.
        :param list[str] aliases: Alternative names by which this module may be referred to
        :param float timeToLock: The amount of time in seconds needed for the beam to lock onto an item and pull it into the hold (Default 0)
        :param int value: The number of credits this module may be sold or bought or at a shop (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this module. (Default "")
        :param str manufacturer: The name of the manufacturer of this module (Default "")
        :param str icon: A URL pointing to an image to use for this module's icon (Default "")
        :param bbUtil.dumbEmoji emoji: The emoji to use for this module's small icon (Default bbUtil.EMPTY_DUMBEMOJI)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other modules of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard module (loaded in from bbData) or a custom spawned module (Default False)
        """
        super(bbTractorBeamModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.timeToLock = timeToLock

    
    def statsStringShort(self):
        return "*Time To Lock: " + str(self.timeToLock) + "s*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the object's __class__ attribute.

        :return: A reference to this class
        :rtype: type
        """
        return bbTractorBeamModule

    
    def toDict(self) -> dict:
        """Serialize this module into dictionary format, to be saved to file.
        Uses the base bbModule toDict method as a starting point, and adds extra attributes implemented by this specific module.

        :return: A dictionary containing all information needed to reconstruct this module
        :rtype: dict
        """
        itemDict = super(bbTractorBeamModule, self).toDict()
        if not self.builtIn:
            itemDict["timeToLock"] = self.timeToLock
        return itemDict


def fromDict(moduleDict : dict) -> bbTractorBeamModule:
    """Factory function building a new module object from the information in the provided dictionary. The opposite of this class's toDict function.

    :param moduleDict: A dictionary containing all information needed to construct the requested module
    :return: The new module object as described in moduleDict
    :rtype: dict
    """
    return bbTractorBeamModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], timeToLock=moduleDict["timeToLock"] if "timeToLock" in moduleDict else 0,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=bbUtil.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else bbUtil.EMPTY_DUMBEMOJI, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
