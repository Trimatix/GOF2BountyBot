from ..items import bbItem
from ...baseClasses import bbSerializable
from datetime import datetime
from ... import bbGlobals


class bbWorkshopListing(bbSerializable.bbSerializable):
    def __init__(self, item, creationDate, bbCreator):
        self.item = item
        self.creationDate = creationDate
        self.bbCreator = bbCreator
    

    def toDict(self, **kwargs):
        return {"item": self.item.toDict(saveType=True),
                "creationDate": str(self.creationDate.year) + "-" + str(self.creationDate.month) + "-" + str(self.creationDate.day),
                "creator": self.bbCreator.id}
