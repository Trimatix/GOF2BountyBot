from .bbCommodity import bbCommodity

class bbCommodityInInventory():
    commodity = bbCommodity()
    count = int()

    def __init__(self, commodity, count=0):
        self.commodity = commodity
        self.count = count

    def increaseCommodity(self, numIncrease):
        self.count += numIncrease

    def decreaseCommodity(self, numDecrease):
        if self.count > numDecrease:
            raise ValueError()
        self.count -= numDecrease

    def getCommodity(self):
        return self.commodity

    def compareCommodity(self, compCommodity):
        return self.commodity == compCommodity
