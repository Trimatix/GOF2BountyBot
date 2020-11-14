# Typing imports
from __future__ import annotations

from ...bbConfig import bbData
from .. import bbAliasable
from ..items import bbShip

class Criminal (bbAliasable.Aliasable):
    """
    A criminal to be wanted in bounties.

    :var name: The name of the criminal
    :vartype name: str
    :var faction: the faction that this criminal is wanted by
    :vartype faction: str
    :var icon: A URL pointing to an image to use as the criminal's icon
    :vartype icon: str
    :var wiki: A URL pointing to a web page to use as this criminal's wiki page in their info embed
    :vartype wiki: str
    :var hasWiki: Whether or not this criminal has a wiki page
    :vartype hasWiki: bool
    :var isPlayer: Whether this criminal is a player or an NPC
    :vartype isPlayer: bool
    :var builtIn: If this criminal is an NPC, are they built in or custom?
    :vartype builtIn: bool
    :var ship: The ship equipped by this criminal
    :vartype ship: bbShip
    :var hasShip: Whether this criminal has a ship equipped or not
    :vartype hasShip: bool
    """

    def __init__(self, name : str, faction : str, icon : icon, builtIn=False, isPlayer=False, aliases=[], wiki="", ship=None):
        """
        :param str name: The name of the criminal
        :param str faction: the faction that this criminal is wanted by
        :param str icon: A URL pointing to an image to use as the criminal's icon
        :param str wiki: A URL pointing to a web page to use as this criminal's wiki page in their info embed
        :param bool isPlayer: Whether this criminal is a player or an NPC
        :param bool builtIn: If this criminal is an NPC, are they built in or custom?
        :param bbShip ship: The ship equipped by this criminal
        :param list[str] aliases: Alias names that can be used to refer to this criminal
        """
        super(Criminal, self).__init__(name, aliases)
        if name == "":
            raise RuntimeError("CRIM_CONS_NONAM: Attempted to create a Criminal with an empty name")
        # if faction == "":
        #     raise RuntimeError("CRIM_CONS_NOFAC: Attempted to create a Criminal with an empty faction")
        if faction == "":
            raise RuntimeError("CRIM_CONS_NOICO: Attempted to create a Criminal with an empty icon")
        
        self.name = name
        self.faction = faction
        self.icon = icon
        self.wiki = wiki
        self.hasWiki = wiki != ""
        self.isPlayer = isPlayer
        self.builtIn = builtIn

        if ship is not None:
            self.ship = bbShip.fromDict(ship.toDict())
            self.hasShip = True
        else:
            self.hasShip = False

    
    def clearShip(self):
        """Delete the equipped ship, removing it from memory

        :raise RuntimeError: If the criminal does not have a ship equipped
        """
        if not self.hasShip:
            raise RuntimeError("CRIM_CLEARSH_NOSHIP: Attempted to clearShip on a Criminal with no active ship")
        del self.ship
        self.hasShip = False


    def unequipShip(self):
        """unequip the equipped ship, without deleting the object

        :raise RuntimeError: If the criminal does not have a ship equipped
        """
        if not self.hasShip:
            raise RuntimeError("CRIM_UNEQSH_NOSHIP: Attempted to unequipShip on a Criminal with no active ship")
        self.ship = None
        self.hasShip = False


    def equipShip(self, ship : bbShip):
        """Equip the given ship, by reference to the given object

        :param bbShip ship: The ship to equip
        :raise RuntimeError: If the criminal already has a ship equipped
        """
        if self.hasShip:
            raise RuntimeError("CRIM_EQUIPSH_HASSH: Attempted to equipShip on a Criminal that already has an active ship")
        self.ship = ship
        self.hasShip = True

    
    def copyShip(self, ship : bbShip):
        """Equip the given ship, by taking a deep copy of the given object

        :param bbShip ship: The ship to equip
        :raise RuntimeError: If the criminal already has a ship equipped
        """
        if self.hasShip:
            raise RuntimeError("CRIM_COPYSH_HASSH: Attempted to copyShip on a Criminal that already has an active ship")
        self.ship = bbShip.fromDict(ship.toDict())
        self.hasShip = True
        

    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object

        :return: The Criminal class
        :rtype: type
        """
        return Criminal


    def __hash__(self) -> int:
        """Provide a hash of this object based on the object's location in memory.

        :return: A hash of this criminal
        :rtype: int
        """
        return hash(repr(self))


    def toDict(self) -> dict:
        """Serialize this criminal into dictionary format, for saving to file.
        
        :return: A dictionary containing all data necessary to replicate this object
        :rtype: dict
        """
        if self.builtIn:
            return {"builtIn":True, "name":self.name}
        else:
            return {"builtIn":False, "isPlayer": self.isPlayer, "name":self.name, "icon":self.icon, "faction":self.faction, "aliases":self.aliases, "wiki":self.wiki}


def fromDict(crimDict : dict, builtIn=False) -> Criminal:
    """Factory function that will either provide a reference to a builtIn bbCriminal if a builtIn criminal is requested, or construct a new bbCriminal object from the provided data.

    :param dict crimDict: A dictionary containing all data necessary to construct the desired bbCriminal. If the criminal is builtIn, this need only be their name, "builtIn": True, and possibly the equipped ship.
    :return: The requested bbCriminal object reference
    :rtype: bbCriminal
    """
    if "builtIn" in crimDict:
        if crimDict["builtIn"]:
            return bbData.builtInCriminalObjs[crimDict["name"]]
        return Criminal(crimDict["name"], crimDict["faction"], crimDict["icon"], isPlayer=crimDict["isPlayer"], aliases=crimDict["aliases"], wiki=crimDict["wiki"], builtIn=crimDict["builtIn"] or builtIn)
    return Criminal(crimDict["name"], crimDict["faction"], crimDict["icon"], isPlayer=crimDict["isPlayer"], aliases=crimDict["aliases"], wiki=crimDict["wiki"], builtIn=builtIn)
