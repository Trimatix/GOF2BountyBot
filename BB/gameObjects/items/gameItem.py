# Typing imports
from __future__ import annotations
from typing import List, Type

from ...baseClasses import aliasable
from abc import abstractmethod
from ... import lib


subClassNames = {}
nameSubClasses = {}


class gameItem(aliasable.Aliasable):
    """A game item, with a value, a manufacturer, a wiki page, an icon, an emoji, and a tech level.

    :var wiki: A web page to represent as the item's wikipedia article in its info page
    :vartype wiki: str
    :var hasWiki: Whether or not this item's wiki attribute is populated
    :vartype hasWiki: bool
    :var manufacturer: The manufacturer of this item
    :vartype manufacturer: str
    :var hasManufacturer: Whether or not this item has a manufacturer
    :vartype hasManufacturer: bool
    :var icon: A URL linking to an image to use as this item's icon
    :vartype icon: str
    :var hasIcon: Whether or not this item has an icon
    :vartype hasIcon: bool
    :var emoji: An emoji reference to use as this item's small icon
    :vartype emoji: bbUti.dumbEmoji
    :var hasEmoji: whether or not this item has an emoji
    :vartype hasEmoji: bool
    :var value: The number of credits this item can be bought/sold for at the shop
    :vartype value: int
    :var shopSpawnRate: A pre-calculated float indicating the highest spawn rate of this item (i.e its spawn probability for a shop of the same techLevel)
    :vartype shopSpawnRate: float
    :var techLevel: A rating from 1 to 10 of this item's technological advancement. Used as a reference to compare against other items of the same type.
    :vartype techLevel: int
    :var hasTechLevel: whether or not this item has a tech level
    :vartype hasTechLevel: bool
    :var builtIn: Whether this item is built into BountyBot (loaded in from bbData) or was custom spawned.
    :vartype builtIn: bool
    """

    def __init__(self, name : str, aliases : List[str], value : int = 0,
            wiki : str = "", manufacturer : str = "", icon : str = "",
            emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY, techLevel : int = -1,
            builtIn : bool = False):
        """
        :param str name: The name of the item. Must be unique. (a model number is a good starting point)
        :param list[str] aliases: A list of alternative names this item may be referred to by.
        :param int value: The number of credits that this item can be bought/sold for at a shop. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this item. (Default "")
        :param str manufacturer: The name of the manufacturer of this item (Default "")
        :param str icon: A URL pointing to an image to use for this item's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this item's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other items of the same type (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard item (loaded in from bbData) or a custom spawned item (Default False)
        """
        super(gameItem, self).__init__(name, aliases)
        self.wiki = wiki
        self.hasWiki = wiki != ""

        self.manufacturer = manufacturer
        self.hasManufacturer = manufacturer != ""

        self.icon = icon
        self.hasIcon = icon != ""

        self.emoji = emoji
        self.hasEmoji = emoji is not None and emoji != lib.emojis.dumbEmoji.EMPTY

        self.value = value
        self.shopSpawnRate = 0

        self.techLevel = techLevel
        self.hasTechLevel = techLevel != -1

        self.builtIn = builtIn


    @abstractmethod
    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        return "*No effect*"


    @abstractmethod
    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The gameItem class
        :rtype: type
        """
        return gameItem

    
    def getValue(self) -> int:
        """Get the base value of this item with no additions or modifications.

        :return: The item's base value
        :rtype: int
        """
        return self.value


    @abstractmethod
    def toDict(self, **kwargs) -> dict:
        """Serialize this item into dictionary format, for saving to file.
        This base implementation should be used in gameItem implementations, and custom attributes saved into it.

        :param bool saveType: When true, include the string name of the object type in the output.
        :return: A dictionary containing all information needed to reconstruct this item. If the item is builtIn, this is only its name.
        :rtype: dict
        """
        if "saveType" in kwargs:
            saveType = kwargs["saveType"]
            del kwargs["saveType"]
        else:
            saveType = False

        if self.builtIn:
            data = {"name": self.name, "builtIn": True}
        else:
            data = super().toDict(**kwargs)
            data["value"] = self.value
            data["wiki"] = self.wiki
            data["manufacturer"] = self.manufacturer
            data["icon"] = self.icon
            data["emoji"] = self.emoji.toDict(**kwargs)
            data["techLevel"] = self.techLevel
            data["builtIn"] = False
        
        if saveType:
            data["type"] = type(self).__name__

        return data

    
    def __hash__(self) -> int:
        """Calculate a hash of this item based on its location in memory.

        :return: This item instance's unique hash
        :rtype: int
        """
        return hash(repr(self))


def spawnableItem(cls):
    if not issubclass(cls, gameItem):
        raise TypeError("Invalid use of spawnableItem decorator: " + cls.__name__ + " is not a gameItem subtype")
    if cls not in nameSubClasses:
        nameSubClasses[cls] = cls.__name__
    if cls.__name__ not in subClassNames:
        subClassNames[cls.__name__] = cls
    return cls


def spawnItem(data : dict) -> gameItem:
    if "type" not in data or data["type"] == "":
        raise NameError("Not given a type")
    elif data["type"] not in subClassNames:
        raise KeyError("Unrecognised item type: " + str(data["type"]))
    
    return subClassNames[data["type"]].fromDict(data)


def isSpawnableItemClass(cls):
    return issubclass(cls, gameItem) and cls in nameSubClasses


def isSpawnableItemInstance(o):
    return isinstance(o, gameItem) and type(o) in nameSubClasses