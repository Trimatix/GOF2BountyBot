# Typing imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import bbUser

from .items import bbModuleFactory, bbShip, bbWeapon, bbTurret
from .items.modules import bbModule
from . import bbInventory
from .items.tools import bbToolItem, bbToolItemFactory
from . import bbShop


class LomaShop(bbShop.bbShop):
    """A shop containing a random selection of items which players can buy.
    Items cannot be sold to Loma.
    """

    def __init__(self, shipsStock : bbInventory.bbInventory = bbInventory.DiscountableTypeRestrictedInventory(bbShip.bbShip),
            weaponsStock : bbInventory.bbInventory = bbInventory.DiscountableTypeRestrictedInventory(bbWeapon.bbWeapon),
            modulesStock : bbInventory.bbInventory = bbInventory.DiscountableTypeRestrictedInventory(bbModule.bbModule),
            turretsStock : bbInventory.bbInventory = bbInventory.DiscountableTypeRestrictedInventory(bbTurret.bbTurret),
            toolsStock : bbInventory.bbInventory = bbInventory.DiscountableTypeRestrictedInventory(bbToolItem.bbToolItem)):
        """
        :param bbInventory shipsStock: The shop's current stock of ships (Default empty DiscountableTypeRestrictedInventory)
        :param bbInventory weaponsStock: The shop's current stock of weapons (Default empty DiscountableTypeRestrictedInventory)
        :param bbInventory modulesStock: The shop's current stock of modules (Default empty DiscountableTypeRestrictedInventory)
        :param bbInventory turretsStock: The shop's current stock of turrets (Default empty DiscountableTypeRestrictedInventory)
        :param bbInventory toolsStock: The shop's current stock of tools (Default empty DiscountableTypeRestrictedInventory)
        """
        super().__init__(shipsStock=shipsStock, weaponsStock=weaponsStock, modulesStock=modulesStock, turretsStock=turretsStock, toolsStock=toolsStock)


    def userSellShipObj(self, user : bbUser.bbUser, ship : bbShip.bbShip):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")
    

    def userSellShipIndex(self, user : bbUser.bbUser, index : int):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")



    def userSellWeaponObj(self, user : bbUser.bbUser, weapon : bbWeapon.bbWeapon):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")
    

    def userSellWeaponIndex(self, user : bbUser.bbUser, index : int):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")



    def userSellModuleObj(self, user : bbUser.bbUser, module : bbModule.bbModule):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")
    

    def userSellModuleIndex(self, user : bbUser.bbUser, index : int):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")



    def userSellTurretObj(self, user : bbUser.bbUser, turret : bbTurret.bbTurret):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")
    

    def userSellTurretIndex(self, user : bbUser.bbUser, index : int):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")


    def userSellToolObj(self, user : bbUser.bbUser, tool : bbToolItem.bbToolItem):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")
    

    def userSellToolIndex(self, user : bbUser.bbUser, index : int):
        """Selling items to Loma is not allowed."""
        raise NotImplementedError("Attempted to sell an item to a Loma shop")


    @classmethod
    def fromDict(cls, shopDict : dict, **kwargs) -> bbShop:
        """Recreate a bbShop instance from its dictionary-serialized representation - the opposite of bbShop.toDict
        
        :param dict shopDict: A dictionary containing all information needed to construct the shop
        :return: A new bbShop object as described by shopDict
        :rtype: bbShop
        """
        shipsStock = bbInventory.DiscountableTypeRestrictedInventory(bbShip.bbShip),
        weaponsStock = bbInventory.DiscountableTypeRestrictedInventory(bbWeapon.bbWeapon),
        modulesStock = bbInventory.DiscountableTypeRestrictedInventory(bbModule.bbModule),
        turretsStock = bbInventory.DiscountableTypeRestrictedInventory(bbTurret.bbTurret),
        toolsStock = bbInventory.DiscountableTypeRestrictedInventory(bbToolItem.bbToolItem)

        for shipListingDict in shopDict["shipsStock"]:
            shipsStock.addItem(bbShip.bbShip.fromDict(shipListingDict["item"]), quantity=shipListingDict["count"])

        for weaponListingDict in shopDict["weaponsStock"]:
            weaponsStock.addItem(bbWeapon.bbWeapon.fromDict(weaponListingDict["item"]), quantity=weaponListingDict["count"])

        for moduleListingDict in shopDict["modulesStock"]:
            modulesStock.addItem(bbModuleFactory.fromDict(moduleListingDict["item"]), quantity=moduleListingDict["count"])

        for turretListingDict in shopDict["turretsStock"]:
            turretsStock.addItem(bbTurret.bbTurret.fromDict(turretListingDict["item"]), quantity=turretListingDict["count"])

        for toolListingDict in shopDict["toolsStock"]:
            toolsStock.addItem(bbToolItemFactory.fromDict(toolListingDict["item"]), quantity=toolListingDict["count"])

        return LomaShop(shipsStock=shipsStock, weaponsStock=weaponsStock, modulesStock=modulesStock,
                        turretsStock=turretsStock, toolsStock=toolsStock)
