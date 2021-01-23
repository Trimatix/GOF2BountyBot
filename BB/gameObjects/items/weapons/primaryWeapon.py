from ..gameItem import GameItem, spawnableItem
from ....bbConfig import bbData
from ... import lib
from typing import List


@spawnableItem
class PrimaryWeapon(GameItem):
    """A primary weapon that can be equipped onto a bbShip for use in duels.

    :var dps: The weapon's damage per second to a target ship.
    :vartype dps: float
    """

    def __init__(self, name : str, aliases : List[str], dps : float = 0.0, value : int = 0,
            wiki : str = "", manufacturer : str = "", icon : str = "",
            emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY, techLevel : int = -1, builtIn : bool = False):
        """
        :param str name: The name of the weapon. Must be unique. (a model number is a good starting point)
        :param list[str] aliases: A list of alternative names this weapon may be referred to by.
        :param int valie: The amount of credits that this turret can be bought/sold for at a shop. (Default 0)
        :param float dps:The weapon's damage per second to a target ship. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this weapon. (Default "")
        :param str manufacturer: The name of the manufacturer of this weapon (Default "")
        :param str icon: A URL pointing to an image to use for this weapon's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this weapon's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this weapon's technical advancement. Used as a measure for its effectiveness compared to other weapons of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard weapon (loaded in from bbData) or a custom spawned weapon (Default False)
        """
        super(PrimaryWeapon, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.dps = dps

    
    def statsStringShort(self) -> str:
        """Get a short string summary of the weapon. This currently only includes the DPS.

        :return: a short string summary of the weapon's statistics
        :rtype: str
        """
        return "*Dps: " + str(self.dps) + "*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The primaryWeapon class
        :rtype: type
        """
        return PrimaryWeapon


    def toDict(self, **kwargs) -> dict:
        """Serialize this item into dictionary format, for saving to file.

        :param bool saveType: When true, include the string name of the object type in the output.
        :return: A dictionary containing all information needed to reconstruct this weapon. If the weapon is builtIn, this is only its name.
        :rtype: dict
        """
        itemDict = super(PrimaryWeapon, self).toDict(**kwargs)
        if not self.builtIn:
            itemDict["dps"] = self.dps
        return itemDict


    @classmethod
    def fromDict(cls, weaponDict, **kwargs):
        """Factory function constructing a new primaryWeapon object from a dictionary serialised representation - the opposite of primaryWeapon.toDict.
        
        :param dict weaponDict: A dictionary containing all information needed to construct the desired primaryWeapon
        :return: A new primaryWeapon object as described in weaponDict
        :rtype: primaryWeapon
        """
        if weaponDict["builtIn"]:
            return bbData.builtInWeaponObjs[weaponDict["name"]]
        else:
            return PrimaryWeapon(weaponDict["name"], weaponDict["aliases"], dps=weaponDict["dps"], value=weaponDict["value"],
            wiki=weaponDict["wiki"] if "wiki" in weaponDict else "", manufacturer=weaponDict["manufacturer"] if "manufacturer" in weaponDict else "",
            icon=weaponDict["icon"] if "icon" in weaponDict else bbData.rocketIcon, emoji=lib.emojis.dumbEmojiFromStr(weaponDict["emoji"]) if "emoji" in weaponDict else lib.emojis.dumbEmoji.EMPTY,
            techLevel=weaponDict["techLevel"] if "techLevel" in weaponDict else -1, builtIn=False)
