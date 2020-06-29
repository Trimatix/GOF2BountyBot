from .bbCommodity import bbCommodity

class bbCommodityInInventory():
    Commodity = bbCommodity()
    count = int()

    def __init__(self, commodity, count=0):
        self.Commodity = commodity
        self.count = count

    def increaseCommodity(self, numIncrease):
        self.count += numIncrease

    def decreaseCommodity(self, numDecrease):
        if self.count > numDecrease:
            raise ValueError()
        self.count -= numDecrease

    def getCommodity(self):
        return self.Commodity

    def compareCommodity(self, compCommodity):
        return self.Commodity == compCommodity
