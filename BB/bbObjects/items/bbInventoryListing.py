class bbInventoryListing():
    def __init__(self, item, count=0):
        self.item = item
        self.count = count

    def increaseCount(self, numIncrease):
        self.count += numIncrease

    def decreaseCount(self, numDecrease):
        if self.count < numDecrease:
            raise ValueError("INVLIS_DECRCOUNT_NEG: Attempted to decreaseCount into a negative total: " + str(self.count) + " - " + str(numDecrease))
        self.count -= numDecrease

    def getItem(self):
        return self.item

    def storesItem(self, otherItem):
        return self.commodity is otherItem
