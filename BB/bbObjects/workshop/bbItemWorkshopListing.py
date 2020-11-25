from ..items import bbItem
from datetime import datetime
from ... import bbGlobals
from . import bbWorkshopListing


class bbItemWorkshopListing(bbWorkshopListing.bbWorkshopListing):
    @classmethod
    def fromDict(cls, listingDict, **kwargs):
        creationYear, creationMonth, creationDay = listingDict["item"].split("-")

        return bbItemWorkshopListing(bbItem.spawnItem(listingDict["item"]),
                                    datetime(year=int(creationYear), month=int(creationMonth), day=int(creationDay)),
                                    bbCreator=bbGlobals.usersDB.getUser(listingDict["creator"]))
