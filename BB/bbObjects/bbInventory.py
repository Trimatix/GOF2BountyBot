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
            self.items[item] = bbInventoryListing(item, quantity)
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
        for item in self.keys[pageIndex * itemsPerPage: min(pageNum * itemsPerPage, self.numKeys)]:
            page[item] = self.items[item]

        return page
