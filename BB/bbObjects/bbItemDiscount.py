from __future__ import annotations
from ..baseClasses import bbSerializable


class bbItemDiscount(bbSerializable.bbSerializable):
    """A temporary modification to an item's value, potentially increasing or decreasing it,
    accompanied by a short description of the discount.
    bbItemDiscount comparison operators directly compare multiplier attributes. This allows for sorting a list
    of bbItemDiscount instances by the discount that they offer.

    :var mult: Scalar to multiply the discounted item's value by. E.g 0.5 to decrease the item's value (discount) by 50%
    :vartype mult: float
    :var desc: A short description of the discount.
    :vartype desc: str
    """
    def __init__(self, mult : float, desc : str):
        """
        :param float mult: Scalar to multiply the discounted item's value by. E.g 0.5 to decrease the item's value (discount) by 50%
        :param str desc: A short description of the discount.
        """
        self.mult = mult
        self.desc = desc

    
    def __eq__(self, o : bbItemDiscount) -> bool:
        return isinstance(o, bbItemDiscount) and self.mult == o.mult

    
    def __ne__(self, o: bbItemDiscount) -> bool:
        return (not isinstance(o, bbItemDiscount)) or (isinstance(o, bbItemDiscount) and self.mult != o.mult)

    
    def __lt__(self, o: bbItemDiscount) -> bool:
        return isinstance(o, bbItemDiscount) and self.mult > o.mult

    
    def __gt__(self, o: bbItemDiscount) -> bool:
        return isinstance(o, bbItemDiscount) and self.mult < o.mult

    
    def __le__(self, o: bbItemDiscount) -> bool:
        return isinstance(o, bbItemDiscount) and self.mult >= o.mult

    
    def __ge__(self, o: bbItemDiscount) -> bool:
        return isinstance(o, bbItemDiscount) and self.mult <= o.mult