class bbInventory:
    def __init__(self):
        self.items = {}
        self.keys = []
        self.totalItems = 0
        self.numKeys = 0

    
    def addItem(self, item, quantity=1):
        self.totalItems += quantity
        if item in self.items:
            self.items[item].count += 1
        else:
            self.items[item] = quantity
            self.keys.append(item)
            self.numKeys += 1


    def removeItem(self, item, quantity=1):
        if item in self.items and self.items[item].count >= quantity:
            self.items[item].count -= 1
            self.totalItems -= 1
            if self.items[item].count == 0:
                del self.items[item]
                self.keys.remove(item)
                self.numKeys -= 1
        else:
            raise ValueError("Attempted to remove " + str(quantity) + " " + str(item) + "(s) when " + (str(self.items[item].count) if item in self.items else "0") + " are in inventory")

    
    def numPages(self, itemsPerPage):
        return int(self.numKeys/itemsPerPage) + (0 if self.numKeys % itemsPerPage == 0 else 1)

    
    def getPage(self, pageNum, itemsPerPage):
        if pageNum < 1 or pageNum > self.numPages(itemsPerPage):
            raise IndexError("pageNum out of range. min=1 max=" + str(self.numPages(itemsPerPage)))
        
        pageIndex = pageNum - 1
        page = {}
        for item in self.keys[pageIndex * itemsPerPage + 1: max(pageNum * itemsPerPage, self.numKeys)]:
            page[item] = self.items[item]

        return page


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
        return self.item is otherItem

    def statsStringShort(self):
        return str(self.count) + " in inventory. " + str(self.item.value) + " credits each"

    def toDict(self):
        return {"item": self.item.toDict(), "count": self.count}


