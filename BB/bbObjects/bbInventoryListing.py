from typing import Type
from ..baseClasses import bbSerializable
from .bbItemDiscount import bbItemDiscount


class bbInventoryListing(bbSerializable.bbSerializable):
    """A listing representing an object and a quantity of that object stored.
    To ensure serializability, inventorylistings can only store bbSerializable objects.

    bbSerializable deserializing is not defined in the general case, so bbInventoryListing does not have a general case fromDict function.

    :var item: The item this inventory listing represents
    :var count: The quantity of item stored
    :vartype count: int
    """

    def __init__(self, item, count : int = 0):
        """
        :param item: The item to store
        :param int quantity: The amount of item to store (Default 0)
        """
        if not isinstance(item, bbSerializable.bbSerializable):
            raise TypeError("bbInventoryListing can only store bbSerializables to ensure serializability. Given: " + type(item).__name__)
        self.item = item
        self.count = count


    def increaseCount(self, numIncrease : int):
        """Increase the number of this item stored in the listing

        :param int numIncrease: The amount to increment this listing's count by
        """
        self.count += numIncrease


    def decreaseCount(self, numDecrease : int):
        """Decrease the number of this item stored in the listing

        :param int numDecrease: The amount to decrement this listing's count by
        :raise ValueError: When attempting to decrease the listing by more than what is currently stored
        """
        if self.count < numDecrease:
            raise ValueError("INVLIS_DECRCOUNT_NEG: Attempted to decreaseCount into a negative total: " + str(self.count) + " - " + str(numDecrease))
        self.count -= numDecrease


    def getItem(self):
        """Get the object stored in this listing

        :return: the object that this listing counts
        """
        return self.item


    def storesItem(self, otherItem) -> bool:
        """Decide whether this inventory listing stores the given object
        
        :return: True if otherItem is the same object as the one stored in the listing, down to memory location. False otherwise
        :rtype: bool
        """
        return self.item is otherItem


    def statsStringShort(self) -> str:
        """Get a short string summarising string describing this inventory listing
        Written by Novahkiin22

        ⚠ WARNING
        Does not validate that the stored item has a value. Also does not return information identifying the stored item

        :return: A string describing the quantity of the item stored, and its value.
        :rtype: str
        """
        return str(self.count) + " in inventory. " + str(self.item.value) + " credits each"


    def toDict(self, **kwargs) -> dict:
        """Return a dictionary description of this inventory listing.

        :return: A dictionary identifying the object stored, and the amount
        :rtype: int
        """
        return {"item": self.item.toDict(**kwargs), "count": self.count}

    
    @classmethod
    def fromDict(cls, listingDict : dict, **kwargs):
        raise NotImplementedError("Cannot fromDict on bbInventoryListing in the general case. Instead instance bbInventoryListing with your fromDict-ed item object.")


class DiscountableItemListing(bbInventoryListing):
    """An item listing that also stores a max-sorted list of single-use value modifications.
    """
    def __init__(self, item, count : int = 0):
        """
        :param item: The item to store
        :param int quantity: The amount of item to store (Default 0)
        """
        super().__init__(item, count=count)
        self.discounts = []
    
    
    def pushDiscount(self, discount : bbItemDiscount):
        self.discounts.append(discount)
        self.discounts.sort()


    def popDiscount(self) -> bbItemDiscount:
        return self.discounts.pop(0)
