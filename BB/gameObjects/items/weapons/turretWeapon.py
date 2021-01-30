from __future__ import annotations
from ..gameItem import GameItem, spawnableItem
from ....bbConfig import bbData
from ... import lib
from typing import List


@spawnableItem
class TurretWeapon(GameItem):
    """A turret that can be equipped onto a bbShip for use in duels.

    :var dps: The turret's damage per second to a target ship.
    :vartype dps: float
    """

    def __init__(self, name : str, aliases : List[str], dps : float = 0.0, value : int = 0,
            wiki : str = "", manufacturer : str = "", icon : str = "",
            emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY, techLevel : int = -1, builtIn : bool = False):
        """
        :param str name: The name of the turret. Must be unique. (a model number is a good starting point)
        :param list[str] aliases: A list of alternative names this turret may be referred to by.
        :param int valie: The amount of credits that this turret can be bought/sold for at a shop. (Default 0)
        :param float dps:The turret's damage per second to a target ship. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this turret. (Default "")
        :param str manufacturer: The name of the manufacturer of this turret (Default "")
        :param str icon: A URL pointing to an image to use for this turret's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this turret's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this turret's technical advancement. Used as a measure for its effectiveness compared to other turrets of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard turret (loaded in from bbData) or a custom spawned turret (Default False)
        """
        super(TurretWeapon, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.dps = dps

    
    def statsStringShort(self) -> str:
        """Get a short string summary of the turret. This currently only includes the DPS.

        :return: a short string summary of the turret's statistics
        :rtype: str
        """
        return "*Dps: " + str(self.dps) + "*"


    def toDict(self, **kwargs) -> dict:
        """Serialize this item into dictionary format, for saving to file.

        :param bool saveType: When true, include the string name of the object type in the output.
        :return: A dictionary containing all information needed to reconstruct this turret. If the turret is builtIn, this is only its name.
        :rtype: dict
        """
        itemDict = super(TurretWeapon, self).toDict(**kwargs)
        if not self.builtIn:
            itemDict["dps"] = self.dps
        return itemDict


    @classmethod
    def fromDict(cls, turretDict : dict, **kwargs) -> TurretWeapon:
        """Factory function constructing a new turretWeapon object from a dictionary serialised representation - the opposite of turretWeapon.toDict.
        
        :param dict turretDict: A dictionary containing all information needed to construct the desired turretWeapon
        :return: A new turretWeapon object as described in turretDict
        :rtype: turretWeapon
        """
        if turretDict["builtIn"]:
            return bbData.builtInTurretObjs[turretDict["name"]]
        else:
            return TurretWeapon(turretDict["name"], turretDict["aliases"], dps=turretDict["dps"], value=turretDict["value"],
                            wiki=turretDict["wiki"] if "wiki" in turretDict else "", manufacturer=turretDict["manufacturer"] if "manufacturer" in turretDict else "",
                            icon=turretDict["icon"] if "icon" in turretDict else bbData.rocketIcon, emoji=lib.emojis.dumbEmojiFromStr(turretDict["emoji"]) if "emoji" in turretDict else lib.emojis.dumbEmoji.EMPTY,
                            techLevel=turretDict["techLevel"] if "techLevel" in turretDict else -1, builtIn=False)
