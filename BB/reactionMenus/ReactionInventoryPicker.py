from . import ReactionMenu
from ..bbConfig import bbConfig
from ..bbObjects.items import bbItem
from ..bbObjects import bbInventory
from discord import Message, Colour, Member, Role
from .. import lib
from ..scheduling import TimedTask

# The maximum number of bbItems displayable per menu page
maxItemsPerPage = len(bbConfig.defaultMenuEmojis)


class ReactionInventoryPickerOption(ReactionMenu.ReactionMenuOption):
    """A reaction menu option that represents a bbItem instance.
    Unless configured otherwise, the option's name and emoji will correspond to the item's name and emoji.

    :var item: The bbItem that this option represents
    :vartype item: bbItem
    """

    def __init__(self, item : bbItem.bbItem, menu : ReactionMenu.ReactionMenu, emoji : lib.emojis.dumbEmoji = None, name : str = None):
        """
        :param bbItem item: The bbItem that this option represents
        :param ReactionMenu menu: The ReactionMenu where this option is active
        :param lib.emojis.dumbEmoji emoji: The emoji that a user must react with in order to trigger this menu option (Default item.emoji)
        :param str name: The name of this option as shown in the menu (Default item.name)
        :raise ValueError: When an emoji isn't provided and the given bbItem does not have an emoji (TODO: default to bbConfig.defaultMenuEmojis)
        """

        self.item = item

        if emoji is None:
            if item.hasEmoji:
                emoji = item.emoji
            else:
                raise ValueError("Attempted to create a ReactionInventoryPickerOption without providing an emoji, and the provided item has no emoji")
        if name is None:
            name = item.name
            if item.hasEmoji and emoji != item.emoji:
                name += " " + item.emoji.sendable
        super(ReactionInventoryPickerOption, self).__init__(name, emoji, addFunc=menu.selectItem, addArgs=self.item, removeFunc=menu.deselectItem, removeArgs=self.item)


    def toDict(self, **kwargs) -> dict:
        """Serialize this menu option to dictionary format for saving.

        :return: A dictionary containing all information needed to reconstruct this menu option instance - the item it represents
        :rtype: dict
        """
        baseDict = super(ReactionInventoryPickerOption, self).toDict(**kwargs)
        baseDict["item"] = self.item.toDict()

        return baseDict


class ReactionInventoryPicker(ReactionMenu.CancellableReactionMenu):
    """A reaction menu allowing users to select a bbItem from a bbInventory.
    TODO: Implement paging
    TODO: Display item counts?

    :var bbInventory: The bbInventory to display and select from (TODO: Rename)
    :vartype bbInventory: bbInventory
    :var itemsPerPage: The maximum number of items that can be displayed per menu page
    :vartype itemsPerPage: int
    :var page: The current page the menu is displaying from bbInventory
    :vartype page: int
    """

    def __init__(self, msg : Message, bbInventory : bbInventory.bbInventory, itemsPerPage : int = maxItemsPerPage,
            titleTxt : str = "", desc : str = "", col : Colour = None, timeout : TimedTask.TimedTask = None,
            footerTxt : str = "", img : str = "", thumb : str = "", icon : str = "", authorName : str = "",
            targetMember : Member = None, targetRole : Role = None):        
        """
        :param discord.Message msg: The discord message where this menu should be embedded
        :param bbInventory bbInventory: The bbInventory to display and select from (TODO: Rename)
        :param int maxPerPage: The maximum number of items that can be displayed per menu page (Default maxItemsPerPage)
        :param str titleTxt: The content of the embed title (Default "")
        :param str desc: The content of the embed description; appears at the top below the title (Default "")
        :param discord.Colour col: The colour of the embed's side strip (Default None)
        :param TimedTask timeout: The TimedTask responsible for expiring this menu (Default None)
        :param str footerTxt: Secondary description appearing in darker font at the bottom of the embed (Default "")
        :param str img: URL to a large icon appearing as the content of the embed, left aligned like a field (Default "")
        :param str thumb: URL to a larger image appearing to the right of the title (Default "")
        :param str authorName: Secondary, smaller title for the embed (Default "")
        :param str icon: URL to a smaller image to the left of authorName. AuthorName is required for this to be displayed. (Default "")
        :param discord.Member targetMember: The only discord.Member that is able to interact with this menu. All other reactions are ignored (Default None)
        :param discord.Role targetRole: In order to interact with this menu, users must possess this role. All other reactions are ignored (Default None)
        :raise ValueError: When itemsPerPage is bigger than maxItemsPerPage (TODO: Is this necessary? options don't currently use the default menu emojis)
        """
        if itemsPerPage > maxItemsPerPage:
            raise ValueError("Tried to instantiate a ReactionItemPicker with more than " + str(maxItemsPerPage) + " itemsPerPage (requested " + str(itemsPerPage) + ")")
        
        # TODO: Does bbInventory actually need to be stored?
        self.bbInventory = bbInventory
        self.itemsPerPage = itemsPerPage
        
        self.page = 1
        itemOptions = {}
        itemPage = bbInventory.getPage(self.page, self.itemsPerPage)
        for itemNum in range(len(itemPage)):
            optionEmoji = bbConfig.defaultMenuEmojis[itemNum]
            item = itemPage[itemNum].item
            itemOptions[optionEmoji] = ReactionInventoryPickerOption(item, self, emoji=optionEmoji)

        super(ReactionInventoryPicker, self).__init__(msg, options=itemOptions, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout, targetMember=targetMember, targetRole=targetRole)


    def selectItem(self, item : bbItem.bbItem) -> bbItem.bbItem:
        """Pass back the selected bbItem to the calling function.
        This method is called on reaction add that corresponds to a bbItem currently on display

        :param bbItem item: The bbItem that the user just selected
        :return: item
        :rtype: bbItem
        """
        print("picked " + str(item))
        return item


    def deselectItem(self, item : bbItem.bbItem) -> bbItem.bbItem:
        """Pass back the deselected bbItem to the calling function.
        This method is called on reaction remove that corresponds to a bbItem currently on display

        :param bbItem item: The bbItem that the user just deselected
        :return: item
        :rtype: bbItem
        """
        print("unpicked " + str(item))
        return item


    def toDict(self, **kwargs) -> dict:
        """⚠ ReactionInventoryPickers are not currently saveable. Do not use this method.
        Dummy method, once implemented this method will serialize this reactionMenu to dictionary format.

        :return: A dummy dictionary containing basic information about the menu, but not all information needed to reconstruct the menu.
        :rtype: dict
        :raise NotImplementedError: Always.
        """
        raise NotImplementedError("Attempted to call toDict on an unsaveable reaction menu type")
        baseDict = super(ReactionInventoryPicker, self).toDict(**kwargs)


# ⚠ unfinished. idk how to save to file a reference to the inventory because idk what or where it will be. might just close all inventory menus on shutdown
def fromDict(rmDict : dict) -> ReactionInventoryPicker:
    """⚠ ReactionInventoryPickers are not currently saveable. Do not use this method.
    When implemented, this function will construct a new ReactionInventoryPicker from a dictionary-serialized representation - The opposite of ReactionInventoryPicker.toDict.

    :param dict rmDict: A dictionary containg all information needed to construct the required ReactionInventoryPicker
    :raise NotImplementedError: Always.
    """
    raise NotImplementedError("Attempted to call fromDict on an unsaveable reaction menu type")
    # options = {}
    # for option in rmDict["options"]:


    data = {"channel": self.msg.channel.id, "msg": self.msg.id, "options": optionsDict}
        
    if self.titleTxt != "":
        data["titleTxt"] = self.titleTxt

    if self.desc != "":
        data["desc"] = self.desc

    if self.col != Colour.default():
        data["col"] = self.col

    if self.footerTxt != "":
        data["footerTxt"] = self.footerTxt

    if self.img != "":
        data["img"] = self.img

    if self.thumb != "":
        data["thumb"] = self.thumb

    if self.icon != "":
        data["icon"] = self.icon

    if self.authorName != "":
        data["authorName"] = self.authorName

    if self.timeout != None:
        data["timeout"] = self.timeout.timestamp