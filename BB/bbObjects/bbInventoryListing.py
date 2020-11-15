class bbInventoryListing():
    """A listing representing an object and a quantity of that object stored.
    This class is type unaware and, as such, does not have an associated fromDict function.

    :var item: The item this inventory listing represents
    :var count: The quantity of item stored
    :vartype count: int
    """

    def __init__(self, item, count : int = 0):
        """
        :param item: The item to store
        :param int quantity: The amount of item to store (Default 0)
        """
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


    def toDict(self) -> dict:
        """Return a dictionary description of this inventory listing.
        ⚠ This function assumes that the object storeed in the listing has a toDict method.

        :return: A dictionary identifying the object stored, and the amount
        :rtype: int
        """
        return {"item": self.item.toDict(), "count": self.count}
