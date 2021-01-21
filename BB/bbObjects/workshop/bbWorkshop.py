from ...baseClasses import serializable
from datetime import datetime
from . import bbWorkshopListing


class bbWorkshop(serializable.Serializable):
    def __init__(self, itemTypes):
        self.items = {iType: [] for iType in itemTypes}


    def addListing(self, itemType, listing):
        self.items[itemType].append(listing)


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
