from . import ReactionMenu
from ..bbConfig import bbConfig
from .. import bbGlobals, bbUtil
maxItemsPerPage = len(bbConfig.defaultMenuEmojis)


class ReactionInventoryPickerOption(ReactionMenu.ReactionMenuOption):
    def __init__(self, item, menu, emoji=None, name=None):
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


    def toDict(self):
        baseDict = super(ReactionInventoryPickerOption, self).toDict()
        baseDict["item"] = self.item.toDict()

        return baseDict


class ReactionInventoryPicker(ReactionMenu.CancellableReactionMenu):
    def __init__(self, msg, bbInventory, itemsPerPage, titleTxt="", desc="", col=None, timeout=None, footerTxt="", img="", thumb="", icon="", authorName="", targetMember=None, targetRole=None):        
        if itemsPerPage > 10:
            raise ValueError("Tried to instantiate a ReactionItemPicker with more than " + str(maxItemsPerPage) + " itemsPerPage (requested " + str(itemsPerPage) + ")")
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


    def selectItem(self, item):
        print("picked " + str(item))
        return item


    def deselectItem(self, item):
        print("unpicked " + str(item))
        return item


    def toDict(self):
        baseDict = super(ReactionInventoryPicker, self).toDict()


# ⚠ unfinished. idk how to save to file a reference to the inventory because idk what or where it will be. might just close all inventory menus on shutdown
def fromDict(rmDict):
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