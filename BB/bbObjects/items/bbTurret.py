from .bbItem import bbItem
from ...bbConfig import bbData
from ... import bbUtil
from typing import List

class bbTurret(bbItem):
    """A turret that can be equipped onto a bbShip for use in duels.

    :var dps: The turret's damage per second to a target ship.
    :vartype dps: float
    """

    def __init__(self, name : str, aliases : List[str], dps=0.0, value=0, wiki="", manufacturer="", icon="", emoji=bbUtil.EMPTY_DUMBEMOJI, techLevel=-1, builtIn=False):
        """
        :param str name: The name of the turret. Must be unique. (a model number is a good starting point)
        :param list[str] aliases: A list of alternative names this turret may be referred to by.
        :param float dps:The turret's damage per second to a target ship. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this turret. (Default "")
        :param str manufacturer: The name of the manufacturer of this turret (Default "")
        :param str icon: A URL pointing to an image to use for this turret's icon (Default "")
        :param bbUtil.dumbEmoji emoji: The emoji to use for this turret's small icon (Default bbUtil.EMPTY_DUMBEMOJI)
        :param int techLevel: A rating from 1 to 10 of this turret's technical advancement. Used as a measure for its effectiveness compared to other turrets of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard turret (loaded in from bbData) or a custom spawned turret (Default False)
        """
        super(bbTurret, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        self.dps = dps

    
    def statsStringShort(self) -> str:
        """Get a short string summary of the turret. This currently only includes the DPS.

        :return: a short string summary of the turret's statistics
        :rtype: str
        """
        return "*Dps: " + str(self.dps) + "*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbTurret class
        :rtype: type
        """
        return bbTurret


    def toDict(self) -> dict:
        """Serialize this item into dictionary format, for saving to file.

        :return: A dictionary containing all information needed to reconstruct this turret. If the turret is builtIn, this is only its name.
        :rtype: dict
        """
        itemDict = super(bbTurret, self).toDict()
        if not self.builtIn:
            itemDict["dps"] = self.dps
        return itemDict


def fromDict(turretDict : dict) -> bbTurret:
    """Factory function constructing a new bbTurret object from a dictionary serialised representation - the opposite of bbTurret.toDict.
    
    :param dict turretDict: A dictionary containing all information needed to construct the desired bbTurret
    :return: A new bbTurret object as described in turretDict
    :rtype: bbTurret
    """
    if turretDict["builtIn"]:
        return bbData.builtInTurretObjs[turretDict["name"]]
    else:
        return bbTurret(turretDict["name"], turretDict["aliases"], dps=turretDict["dps"], value=turretDict["value"],
                        wiki=turretDict["wiki"] if "wiki" in turretDict else "", manufacturer=turretDict["manufacturer"] if "manufacturer" in turretDict else "",
                        icon=turretDict["icon"] if "icon" in turretDict else bbData.rocketIcon, emoji=bbUtil.dumbEmojiFromStr(turretDict["emoji"]) if "emoji" in turretDict else bbUtil.EMPTY_DUMBEMOJI,
                        techLevel=turretDict["techLevel"] if "techLevel" in turretDict else -1, builtIn=False)
