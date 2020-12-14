import random
from . import bbToolItem
from .... import lib, bbGlobals
from discord import Message
import asyncio
from ....bbConfig import bbConfig, bbData
from .. import bbItem
from ....logging import bbLogger
from ....reactionMenus.ConfirmationReactionMenu import InlineConfirmationMenu


@bbItem.spawnableItem
class bbCrate(bbToolItem.bbToolItem):
    def __init__(self, itemPool, name : str = "", value : int = 0, wiki : str = "",
            manufacturer : str = "", icon : str = bbConfig.defaultCrateIcon, emoji : lib.emojis.dumbEmoji = None,
            techLevel : int = -1, builtIn : bool = False):

        if emoji is None:
            emoji = bbConfig.defaultCrateEmoji

        super().__init__(name, [], value=value, wiki=wiki,
            manufacturer=manufacturer, icon=icon, emoji=emoji,
            techLevel=techLevel, builtIn=builtIn)
        
        for item in itemPool:
            if not bbItem.isSpawnableItemInstance(item):
                raise RuntimeError("Attempted to create a bbCrate with something other than a spawnableItem in its itemPool.")
        self.itemPool = itemPool


    async def use(self, *args, **kwargs):
        """This item's behaviour function. Intended to be very generic at this level of implementation.
        """
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        if kwargs["callingBBUser"] is not None and kwargs["callingBBUser"].__class__.__name__ != "bbUser":
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        callingBBUser = kwargs["callingBBUser"]
        newItem = random.choice(self.itemPool)
        callingBBUser.getInventoryForItem(newItem).addItem(newItem)
        callingBBUser.inactiveTools.removeItem(self)


    async def userFriendlyUse(self, message : Message, *args, **kwargs) -> str:
        """A version of self.use intended to be called by users, where exceptions are never thrown in the case of
        user error, and results strings are always returned.

        :param Message message: The discord message that triggered this tool use
        :return: A user-friendly messge summarising the result of the tool use.
        :rtype: str
        """
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        if kwargs["callingBBUser"] is not None and kwargs["callingBBUser"].__class__.__name__ != "bbUser":
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        callingBBUser = kwargs["callingBBUser"]
        confirmMsg = await message.channel.send("Are you sure you want to open this crate?") 
        confirmation = await InlineConfirmationMenu(confirmMsg, message.author, bbConfig.toolUseConfirmTimeoutSeconds).doMenu()

        if bbConfig.defaultRejectEmoji in confirmation:
            return "🛑 Crate open cancelled."
        elif bbConfig.defaultAcceptEmoji in confirmation:
            newItem = random.choice(self.itemPool)
            callingBBUser.getInventoryForItem(newItem).addItem(newItem)
            callingBBUser.inactiveTools.removeItem(self)
            
            return "🎉 Success! You got a " + newItem.name + "!"

    
    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        return "*" + str(len(self.itemPool)) + " possible items*"


    def getType(self):
        return type(self)

    
    def toDict(self, **kwargs) -> dict:
        """Serialize this tool into dictionary format.
        This step of implementation adds a 'type' string indicating the name of this tool's subclass.

        :return: The default bbItem toDict implementation, with an added 'type' field
        :rtype: dict
        """
        data = super().toDict(**kwargs)
        if self.builtIn:
            data["crateType"] = "levelUp"
            data["typeNum"] = self.techLevel
        else:
            if "saveType" not in kwargs:
                kwargs["saveType"] = True
            
            data["itemPool"] = []
            for item in self.itemPool:
                data["itemPool"].append(item.toDict(**kwargs))
        return data


    @classmethod
    def fromDict(cls, crateDict, **kwargs):
        skipInvalidItems = kwargs["skipInvalidItems"] if "skipInvalidItems" in kwargs else False
        
        if "builtIn" in crateDict and crateDict["builtIn"]:
            if "crateType" in crateDict:
                if crateDict["crateType"] == "levelUp":
                    return bbData.levelUpCratesByTL[crateDict["typeNum"]-1]
                else:
                    raise ValueError("Unknown crateType: " + str(crateDict["crateType"]))
            else:
                raise ValueError("Attempted to spawn builtIn bbCrate with no given crateType")
        else:
            crateToSpawn = crateDict

        itemPool = []
        if "itemPool" in crateToSpawn:
            for itemDict in crateToSpawn["itemPool"]:
                errorStr = ""
                errorType = ""
                if "type" not in itemDict:
                    errorStr = "Invalid itemPool entry, missing type. Data: " + itemDict
                    errorType = "NO_TYPE"
                elif itemDict["type"] not in bbItem.subClassNames:
                    errorStr = "Invalid itemPool entry, attempted to add something other than a spawnableItem. Data: " + itemDict
                    errorType = "BAD_TYPE"
                if errorStr:
                    if skipInvalidItems:
                        bbLogger.log("bbCrate", "fromDict", errorStr, eventType=errorType)
                    else:
                        raise ValueError(errorStr)
                else:
                    itemPool.append(bbItem.spawnItem(itemDict))
        else:
            bbLogger.log("bbCrate", "fromDict", "fromDict-ing a bbCrate with no itemPool.")
        
        return bbCrate(itemPool, name=crateToSpawn["name"] if "name" in crateToSpawn else "",
            value=crateToSpawn["value"] if "value" in crateToSpawn else 0,
            wiki=crateToSpawn["wiki"] if "wiki" in crateToSpawn else "",
            manufacturer=crateToSpawn["manufacturer"] if "manufacturer" in crateToSpawn else "",
            icon=crateToSpawn["icon"] if "icon" in crateToSpawn else "",
            emoji=lib.emojis.dumbEmojiFromDict(crateToSpawn["emoji"]) if "emoji" in crateToSpawn else lib.emojis.dumbEmoji.EMPTY,
            techLevel=crateToSpawn["techLevel"] if "techLevel" in crateToSpawn else -1,
            builtIn=crateToSpawn["builtIn"] if "builtIn" in crateToSpawn else False)
