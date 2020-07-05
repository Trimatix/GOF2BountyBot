from . import ReactionMenu
from .bbConfig import bbConfig
maxItemsPerPage = len(bbConfig.defaultMenuEmojis)


class ReactionInventoryPicker(ReactionMenu.ReactionMenu):
    def __init__(self, msg, bbInventory, itemsPerPage, titleTxt="", desc="", col=None, footerTxt="", img="", thumb="", icon="", authorName=""):
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
            itemOptions[optionEmoji] = ReactionMenu.ReactionMenuOption(optionEmoji, self.pickItem, item, item.name + ((" " + item.emoji) if item.hasEmoji else ""))

        super(ReactionInventoryPicker, self).__init__(msg, options=itemOptions, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName)


    def pickItem(self, item):
        print("picked " + str(item))
        return item
