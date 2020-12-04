from __future__ import annotations
from . import bbToolItem
from .... import lib
from ....bbConfig import bbConfig, bbData
from ..bbShip import bbShip
from .. import bbShipUpgrade
from discord import Message
from .... import bbGlobals
import asyncio
from ..bbItem import spawnableItem


@spawnableItem
class bbShipUpgradeTool(bbToolItem.bbToolItem):
    """A tool that can be used to apply a ship upgrade to a ship.
    This item is named after the ship upgrade it applies
    
    This tool is single use. If a calling user is given, the tool is removed from that user's inventory after use.
    """
    def __init__(self, shipUpgrade : bbShipUpgrade.bbShipUpgrade, value : int = 0, wiki : str = "", icon : str = bbConfig.defaultShipUpgradeToolIcon,
            emoji : lib.emojis.dumbEmoji = None, techLevel : int = -1, builtIn : bool = False):
        """
        :param bbShipUpgrade shipUpgrade: The upgrade that this tool applies.
        :param int value: The number of credits that this item can be bought/sold for at a shop. (Default 0)
        :param str wiki: A web page that is displayed as the wiki page for this item. If no wiki is given and shipSkin has one, that will be used instead. (Default "")
        :param str icon: A URL pointing to an image to use for this item's icon (Default bbConfig.defaultShipUpgradeToolIcon)
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this item's small icon (Default bbConfig.defaultShipUpgradeToolEmoji)
        :param int techLevel: A rating from 1 to 10 of this item's technical advancement. Used as a measure for its effectiveness compared to other items of the same type (Default shipSkin.averageTL)
        :param bool builtIn: Whether this is a BountyBot standard item (loaded in from bbData) or a custom spawned item (Default False)
        """
        if emoji is None:
            emoji = bbConfig.defaultShipUpgradeToolEmoji
        super().__init__(lib.stringTyping.shipUpgradeNameToToolName(shipUpgrade.name), [shipUpgrade.name, "Upgrade: " + shipUpgrade.name, "Ship Upgrade " + shipUpgrade.name + "Upgrade " + shipUpgrade.name], value=value, wiki=wiki if wiki else shipUpgrade.wiki if shipUpgrade.hasWiki else "", manufacturer=shipUpgrade.vendor if shipUpgrade.hasVendor else "", icon=icon, emoji=emoji, techLevel=techLevel if techLevel > -1 else shipUpgrade.techLevel if shipUpgrade.hasTechLevel else -1, builtIn=builtIn)
        self.shipUpgrade = shipUpgrade

    
    async def use(self, *args, **kwargs):
        """Apply the tool to the given ship.
        After use, the tool will be removed from callingBBUser's inventory. To disable this, pass callingBBUser as None.
        """
        if "ship" not in kwargs:
            raise NameError("Required kwarg not given: ship")
        if not isinstance(kwargs["ship"], bbShip):
            raise TypeError("Required kwarg is of the wrong type. Expected bbShip, received " + kwargs["ship"].__class__.__name__)
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        if kwargs["callingBBUser"] is not None and kwargs["callingBBUser"].__class__.__name__ != "bbUser":
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        ship, callingBBUser = kwargs["ship"], kwargs["callingBBUser"]

        if not callingBBUser.ownsShip(ship):
            raise RuntimeError("User '" + str(callingBBUser.id) + "' attempted to apply an upgrade to a ship that does not belong to them: " + ship.getNameAndNick())
        
        ship.applyUpgrade(self.shipUpgrade)
        if self in callingBBUser.inactiveTools:
            callingBBUser.inactiveTools.removeItem(self)


    async def userFriendlyUse(self, message : Message, *args, **kwargs) -> str:
        """Apply the upgrade to the given ship.
        After use, the tool will be removed from callingBBUser's inventory. To disable this, pass callingBBUser as None.

        :param Message message: The discord message that triggered this tool use
        :return: A user-friendly messge summarising the result of the tool use.
        :rtype: str
        """
        if "ship" not in kwargs:
            raise NameError("Required kwarg not given: ship")
        if not isinstance(kwargs["ship"], bbShip):
            raise TypeError("Required kwarg is of the wrong type. Expected bbShip, received " + kwargs["ship"].__class__.__name__)
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        
        # converted to soft type check due to circular import
        """if (not isinstance(kwargs["callingBBUser"], bbUser)) and kwargs["callingBBUser"] is not None:
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)"""
        if (kwargs["callingBBUser"].__class__.__name__ != "bbUser") and kwargs["callingBBUser"] is not None:
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        ship, callingBBUser = kwargs["ship"], kwargs["callingBBUser"]

        if not callingBBUser.ownsShip(ship):
            raise RuntimeError("User '" + str(callingBBUser.id) + "' attempted to apply an upgrade to a ship that does not belong to them: " + ship.getNameAndNick())

        confirmMsg = await message.channel.send("Are you sure you want to apply the " + self.shipUpgrade.name + " upgrade to your " + ship.getNameAndNick() + "? Please react to this message to confirm:\n" + bbConfig.defaultAcceptEmoji.sendable + " : Yes\n" + bbConfig.defaultRejectEmoji.sendable + " : Cancel\n\n*This menu will expire in " + str(bbConfig.skinApplyConfirmTimeoutSeconds) + "seconds.*") 
        
        def useConfirmCheck(reactPL):
            return reactPL.message_id == confirmMsg.id and reactPL.user_id == message.author.id and lib.emojis.dumbEmojiFromPartial(reactPL.emoji) in [bbConfig.defaultAcceptEmoji, bbConfig.defaultRejectEmoji]

        try:
            reactPL = await bbGlobals.client.wait_for("raw_reaction_add", check=useConfirmCheck, timeout=bbConfig.skinApplyConfirmTimeoutSeconds)
        except asyncio.TimeoutError:
            await confirmMsg.edit(content="This menu has now expired. Please use `" + bbConfig.commandPrefix + "use` again.")
        else:
            if lib.emojis.dumbEmojiFromPartial(reactPL.emoji) == bbConfig.defaultAcceptEmoji:
                ship.applyUpgrade(self.shipUpgrade)
                if self in callingBBUser.inactiveTools:
                    callingBBUser.inactiveTools.removeItem(self)
                
                return "🛠 Success! Your ship upgrade has been applied."
            else:
                return "🛑 Upgrade application cancelled."


    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        return self.shipUpgrade.statsStringShort()

    
    def toDict(self, **kwargs):
        """
        
        :param bool saveType: When true, include the string name of the object type in the output.
        """
        data = super().toDict(**kwargs)
        data["name"] = self.shipUpgrade.name
        data["upgrade"] = self.shipUpgrade.toDict(**kwargs)
        return data
        # raise RuntimeError("Attempted to save a non-builtIn bbShipSkinTool")
            

    @classmethod
    def fromDict(cls, toolDict : dict, **kwargs) -> bbShipUpgradeTool:
        """Construct a bbShipUpgradeTool from its dictionary-serialized representation.

        :param dict toolDict: A dictionary containing all information needed to construct the required bbShipUpgradeTool. Critically, a name, type, and builtIn specifier.
        :return: A new bbShipUpgradeTool object as described in toolDict
        :rtype: bbShipUpgradeTool
        """
        shipUpgrade = bbData.builtInUpgradeObjs[toolDict["name"]] if toolDict["builtIn"] else bbShipUpgrade.bbShipUpgrade.fromDict(toolDict["upgrade"])
        if toolDict["builtIn"]:
            return bbData.builtInToolObjs[lib.stringTyping.shipUpgradeNameToToolName(shipUpgrade.name)]
        return bbShipUpgradeTool(shipUpgrade, builtIn=False)
