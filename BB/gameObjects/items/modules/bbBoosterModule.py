from . import bbModule
from ....bbConfig import bbData
from .... import lib
from typing import List
from ..gameItem import spawnableItem


@spawnableItem
class bbBoosterModule(bbModule.bbModule):
    """"A module providing a ship with the ability to boost its speed for a short period of time.

    :var effect: Multiplier to apply to the ship's velocity
    :vartype effect: float
    :var duration: Number of seconds the boost lasts
    :vartype duration: float
    """

    def __init__(self, name : str, aliases : List[str], effect : int = 0, duration : int = 0,
            value : int = 0, wiki : str = "", manufacturer : str = "", icon : str = "",
            emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY, techLevel : int = -1,
            builtIn : bool = False):
        """
        :param str name: The name of the module. Must be unique.
        :param list[str] aliases: Alternative names by which this module may be referred to
        :param float effect: Multiplier to apply to the ship's velocity (Default 0)
        :param float duration: Number of seconds the boost lasts (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this module. (Default "")
        :param str manufacturer: The name of the manufacturer of this module (Default "")
        :param str icon: A URL pointing to an image to use for this module's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this module's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other modules of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard module (loaded in from bbData) or a custom spawned module (Default False)
        """
        super(bbBoosterModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.effect = effect
        self.duration = duration


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the object's __class__ attribute.

        :return: A reference to this class
        :rtype: type
        """
        return bbBoosterModule


    def statsStringShort(self):
        return "*Effect: " + ("+" if self.effect >= 1 else "-") + str(round(((self.effect - 1) * 100) if self.effect > 1 else (self.effect * 100))) + \
                "%, Duration: " + ("+" if self.duration > 0 else "-") + str(self.duration) + "s*"

    
    def toDict(self, **kwargs) -> dict:
        """Serialize this module into dictionary format, to be saved to file.
        Uses the base bbModule toDict method as a starting point, and adds extra attributes implemented by this specific module.

        :return: A dictionary containing all information needed to reconstruct this module
        :rtype: dict
        """
        itemDict = super(bbBoosterModule, self).toDict(**kwargs)
        if not self.builtIn:
            itemDict["effect"] = self.effect
            itemDict["duration"] = self.duration
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
            
        return bbBoosterModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], effect=moduleDict["effect"] if "effect" in moduleDict else 0,
                                duration=moduleDict["duration"] if "duration" in moduleDict else 0, value=moduleDict["value"] if "value" in moduleDict else 0,
                                wiki=moduleDict["wiki"] if "wiki" in moduleDict else "", manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "",
                                icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon, emoji=lib.emojis.dumbEmojiFromStr(moduleDict["emoji"]) if "emoji" in moduleDict else lib.emojis.dumbEmoji.EMPTY, techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
