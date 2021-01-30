from . import moduleItem
from ....bbConfig import bbData
from .... import lib
from typing import List
from ..gameItem import spawnableItem


@spawnableItem
class TractorBeamModule(moduleItem.ModuleItem):
    """A module providing a ship with the ability to pull nearby debris and items into the ship's cargo hold

    :var timeToLock: The amount of time in seconds needed for the beam to lock onto an item and pull it into the hold
    :vartype timeToLock: float
    """

    def __init__(self, name : str, aliases : List[str], timeToLock : float = 0, value : int = 0,
            wiki : str = "", manufacturer : str = "", icon : str = "",
            emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY, techLevel : int = -1,
            builtIn : bool = False):
        """
        :param str name: The name of the module. Must be unique.
        :param list[str] aliases: Alternative names by which this module may be referred to
        :param float timeToLock: The amount of time in seconds needed for the beam to lock onto an item and pull it into the hold (Default 0)
        :param int value: The number of credits this module may be sold or bought or at a shop (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this module. (Default "")
        :param str manufacturer: The name of the manufacturer of this module (Default "")
        :param str icon: A URL pointing to an image to use for this module's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this module's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other modules of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard module (loaded in from bbData) or a custom spawned module (Default False)
        """
        super(TractorBeamModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.timeToLock = timeToLock

    
    def statsStringShort(self):
        return "*Time To Lock: " + str(self.timeToLock) + "s*"

    
    def toDict(self, **kwargs) -> dict:
        """Serialize this module into dictionary format, to be saved to file.
        Uses the base moduleItem toDict method as a starting point, and adds extra attributes implemented by this specific module.

        :return: A dictionary containing all information needed to reconstruct this module
        :rtype: dict
        """
        itemDict = super(TractorBeamModule, self).toDict(**kwargs)
        if not self.builtIn:
            itemDict["timeToLock"] = self.timeToLock
        return itemDict


    @classmethod
    def fromDict(cls, moduleDict : dict, **kwargs):
        """Factory function building a new module object from the information in the provided dictionary. The opposite of this class's toDict function.

        :param moduleDict: A dictionary containing all information needed to construct the requested module
        :return: The new module object as described in moduleDict
        :rtype: dict
        """
        if "builtIn" in moduleDict and moduleDict["builtIn"]:
            return bbData.builtInModuleObjs[moduleDict["name"]]
            
        return TractorBeamModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], timeToLock=moduleDict["timeToLock"] if "timeToLock" in moduleDict else 0,
                                value=moduleDict["value"] if "value" in moduleDict else 0, wiki=moduleDict["wiki"] if "wiki" in moduleDict else "",
                                manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                                emoji=lib.emojis.dumbEmoji.fromStr(moduleDict["emoji"]) if "emoji" in moduleDict else lib.emojis.dumbEmoji.EMPTY, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
