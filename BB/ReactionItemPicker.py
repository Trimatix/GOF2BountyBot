from . import ReactionMenu
from .bbConfig import bbConfig
maxItemsPerPage = len(bbConfig.defaultMenuEmojis)


class ReactionItemPicker(ReactionMenu.ReactionMenu):
    def __init__(self, msgID, bbInventory, itemsPerPage):
        if itemsPerPage > 10:
            raise ValueError("Tried to instantiate a ReactionItemPicker with more than " + str(maxItemsPerPage) + " itemsPerPage (requested " + str(itemsPerPage) + ")")
        self.msgID = msgID
        self.bbInventory = bbInventory
        self.itemsPerPage = itemsPerPage
        
        self.page = 1
        itemOptions = {}
        itemPage = bbInventory.getPage(self.page, self.itemsPerPage)
        for itemNum in range(self.itemsPerPage):
            optionEmoji = bbConfig.defaultMenuEmojis[itemNum]
            itemOptions[optionEmoji] = ReactionMenu.ReactionMenuOption(optionEmoji, self.pickItem, itemPage[itemNum])

        super(ReactionItemPicker, self).__init__(msgID, options=itemOptions)


    def pickItem(self, item):
        print("picked " + str(item))
        return item
