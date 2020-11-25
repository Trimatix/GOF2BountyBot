from .. import bbShipSkin
from datetime import datetime
from ... import bbGlobals
from . import bbWorkshopListing


class bbShipSkinWorkshopListing(bbWorkshopListing.bbWorkshopListing):
    @classmethod
    def fromDict(cls, listingDict, **kwargs):
        creationYear, creationMonth, creationDay = listingDict["item"].split("-")

        return bbShipSkinWorkshopListing(bbShipSkin.fromDict(listingDict["item"]),
                                    datetime(year=int(creationYear), month=int(creationMonth), day=int(creationDay)),
                                    bbCreator=bbGlobals.usersDB.getUser(listingDict["creator"]))
