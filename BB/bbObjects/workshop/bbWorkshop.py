from ...baseClasses import bbSerializable
from datetime import datetime
from . import bbWorkshopListing


class bbWorkshop(bbSerializable.bbSerializable):
    def __init__(self, itemTypes):
        self.items = {iType: [] for iType in itemTypes}


    def addListing(self, itemType, listing):
        self.items[itemType].append(listing)

    
    def addItem(self, itemType, item, bbCreator, creationDate=None):
        if creationDate is None:
            now = datetime.utcnow()
            creationDate = datetime(year=now.year, month=now.month, day=now.day)

        self.addListing(itemType, bbWorkshopListing.bbWorkshopListing(item, creationDate, bbCreator))


    def toDict(self, **kwargs):
        data = super().toDict(**kwargs)
        data["items"] = {iType: [] for iType in self.items}

        for iType in self.items:
            for item in self.items[iType]:
                data["Items"][iType].append(item.toDict(**kwargs))
        
        return data


    @classmethod
    def fromDict(cls, workshopDict, **kwargs):
        newWorkshop = bbWorkshop(list(workshopDict["items"].keys()))
        for iType in workshopDict["items"]:
            for itemDict in workshopDict["items"][iType]:
                newWorkshop.addListing(iType, bbWorkshopListing.bbWorkshopListing.fromDict(itemDict))
