from . import ReactionMenu


class ReactionItemPicker(ReactionMenu.ReactionMenu):
    def __init__(self, msgID, bbInventory, itemsPerPage):
        self.page = 1
        
