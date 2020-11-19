from . import bbModule
from ....bbConfig import bbData
from .... import lib
from typing import List

class bbThrusterModule(bbModule.bbModule):
    """A module providing a ship with a boost to its handling.
    """

    def __init__(self, name : str, aliases : List[str], handlingMultiplier=1, value=0, wiki="", manufacturer="", icon="", emoji=lib.emojis.dumbEmoji.EMPTY, techLevel=-1, builtIn=False):
        """
        :param str name: The name of the module. Must be unique.
        :param list[str] aliases: Alternative names by which this module may be referred to
        :param int handlingMultiplier: The multiplier to apply to the ship's handling (Default 1)
        :param int value: The number of credits this module may be sold or bought or at a shop (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this module. (Default "")
        :param str manufacturer: The name of the manufacturer of this module (Default "")
        :param str icon: A URL pointing to an image to use for this module's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this module's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other modules of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard module (loaded in from bbData) or a custom spawned module (Default False)
        """
        super(bbThrusterModule, self).__init__(name, aliases, handlingMultiplier=handlingMultiplier, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the object's __class__ attribute.

        :return: A reference to this class
        :rtype: type
        """
        return bbThrusterModule

    
    def toDict(self) -> dict:
        """Serialize this module into dictionary format, to be saved to file.
        No extra attributes implemented by this class, so just eses the base bbModule toDict method.

        :return: A dictionary containing all information needed to reconstruct this module
        :rtype: dict
        """
        itemDict = super(bbThrusterModule, self).toDict()
        return itemDict


def fromDict(moduleDict : dict) -> bbThrusterModule:
    """Factory function building a new module object from the information in the provided dictionary. The opposite of this class's toDict function.

    :param moduleDict: A dictionary containing all information needed to construct the requested module
    :return: The new module object as described in moduleDict
    :rtype: dict
    """
    return bbThrusterModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], handlingMultiplier=moduleDict["handlingMultiplier"] if "handlingMultiplier" in moduleDict else 1,
                            value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                            manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                            emoji=lib.emojis.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else lib.emojis.dumbEmoji.EMPTY, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
