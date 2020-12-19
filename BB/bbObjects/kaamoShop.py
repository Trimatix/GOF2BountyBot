from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import bbUser

from . import bbShop
from ..bbConfig import bbConfig
from .items import bbItem, bbShip, bbWeapon, bbTurret, bbModuleFactory
from .items.modules import bbModule
from .items.tools import bbToolItem, bbToolItemFactory
from ..logging import bbLogger
from . import bbInventory


class KaamoShop(bbShop.bbShop):
    """A "shop" where all transactions are free, essentially operating an item storage service.
    KaamoShops have a maximum capacity defined in bbConfig. Items equipped onto ships count towards this cap.
    """

    def __init__(self, shipsStock : bbInventory.bbInventory = bbInventory.TypeRestrictedInventory(bbShip.bbShip),
            weaponsStock : bbInventory.bbInventory = bbInventory.TypeRestrictedInventory(bbWeapon.bbWeapon),
            modulesStock : bbInventory.bbInventory = bbInventory.TypeRestrictedInventory(bbModule.bbModule),
            turretsStock : bbInventory.bbInventory = bbInventory.TypeRestrictedInventory(bbTurret.bbTurret),
            toolsStock : bbInventory.bbInventory = bbInventory.TypeRestrictedInventory(bbToolItem.bbToolItem)):
        """
        :param bbInventory shipsStock: The shop's current stock of ships (Default empty bbInventory)
        :param bbInventory weaponsStock: The shop's current stock of weapons (Default empty bbInventory)
        :param bbInventory modulesStock: The shop's current stock of modules (Default empty bbInventory)
        :param bbInventory turretsStock: The shop's current stock of turrets (Default empty bbInventory)
        :param bbInventory toolsStock: The shop's current stock of tools (Default empty bbInventory)
        """

        super().__init__(shipsStock=shipsStock, weaponsStock=weaponsStock, modulesStock=modulesStock, turretsStock=turretsStock, toolsStock=toolsStock)
        self.totalItems = weaponsStock.totalItems + modulesStock.totalItems + turretsStock.totalItems + toolsStock.totalItems
        for ship in shipsStock.items:
            self.totalItems += 1 + len(ship.weapons) + len(ship.modules) + len(ship.turrets)


    def userCanAffordItemObj(self, user : bbUser.bbUser, item : bbItem.bbItem) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")


    # SHIP MANAGEMENT
    def userCanAffordShipIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")


    def amountCanAffordShipObj(self, amount : int, ship : bbShip.bbShip) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")

    
    def amountCanAffordShipIndex(self, amount : int, index : int) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")


    def userBuyShipIndex(self, user : bbUser.bbUser, index : int):
        """Moves the ship at the given index in the user's inventory to the shop's inventory.

        :param bbUser user: The user attempting to buy the ship
        :param int index: The index of the requested ship in the shop's ships bbInventory's array of keys
        """
        self.userBuyShipObj(user, self.shipsStock[index].item)
        
        
    def userBuyShipObj(self, user : bbUser.bbUser, requestedShip : bbShip.bbShip):
        """Moves the given ship from the shop's inventory to the user's.

        :param bbUser user: The user attempting to buy the ship
        :param bbShip requestedWeapon: The ship to sell to user
        """
        self.totalItems -= 1
        self.totalItems -= len(requestedShip.weapons)
        self.totalItems -= len(requestedShip.modules)
        self.totalItems -= len(requestedShip.turrets)
        self.shipsStock.removeItem(requestedShip)
        user.inactiveShips.addItem(requestedShip)


    def userSellShipObj(self, user : bbUser.bbUser, ship : bbShip.bbShip):
        """Moves the given ship from the user's inventory to the shop's.

        :param bbUser user: The user to buy ship from
        :param bbShip weapon: The ship to buy from user
        :raise OverflowError: When attempting to fill the shop beyond max capacity
        """
        numShipItems = 1 + len(ship.weapons) + len(ship.modules) + len(ship.turrets)
        if self.totalItems + numShipItems > bbConfig.kaamoMaxCapacity:
            raise OverflowError("Attempted to fill the shop beyond capacity.")
        self.totalItems += numShipItems
        self.shipsStock.addItem(ship)
        user.inactiveShips.removeItem(ship)
    

    def userSellShipIndex(self, user : bbUser.bbUser, index : int):
        """Moves the ship at the given index in the user's inventory to the shop's inventory.

        :param bbUser user: The user to buy ship from
        :param int index: The index of the weapon to buy from user, in the user's ships bbInventory's array of keys
        """
        self.userSellShipObj(user, user.inactiveShips[index].item)


    
    # WEAPON MANAGEMENT
    def userCanAffordWeaponIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")


    def userBuyWeaponIndex(self, user : bbUser.bbUser, index : int):
        """Moves the weapon at the given index in the shop's inventory to the user's inventory.

        :param bbUser user: The user to sell weapon to
        :param int index: The index of the weapon to sell to user, in the shop's weapon bbInventory's array of keys
        """
        self.userBuyWeaponObj(user, user.inactiveWeapons[index].item)
        

    def userBuyWeaponObj(self, user : bbUser.bbUser, requestedWeapon : bbWeapon.bbWeapon):
        """Moves the given weapon from the shop's inventory to the user's.

        :param bbUser user: The user attempting to buy the weapon
        :param bbWeapon requestedWeapon: The weapon to sell to user
        """
        self.totalItems -= 1
        self.weaponsStock.removeItem(requestedWeapon)
        user.inactiveWeapons.addItem(requestedWeapon)


    def userSellWeaponObj(self, user : bbUser.bbUser, weapon : bbWeapon.bbWeapon):
        """Moves the given weapon from the user's inventory to the shop's.

        :param bbUser user: The user to buy weapon from
        :param bbWeapon weapon: The weapon to buy from user
        :raise OverflowError: When attempting to fill the shop beyond max capacity
        """
        if self.totalItems == bbConfig.kaamoMaxCapacity:
            raise OverflowError("Attempted to fill the shop beyond capacity.")
        self.totalItems += 1
        self.weaponsStock.addItem(weapon)
        user.inactiveWeapons.removeItem(weapon)
    

    def userSellWeaponIndex(self, user : bbUser.bbUser, index : int):
        """Moves the weapon at the given index in the user's inventory to the shop's inventory.

        :param bbUser user: The user to buy weapon from
        :param int index: The index of the weapon to buy from user, in the user's weapons bbInventory's array of keys
        """
        self.userSellWeaponObj(user, user.inactiveWeapons[index].item)


    
    # MODULE MANAGEMENT
    def userCanAffordModuleIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")


    def userBuyModuleIndex(self, user : bbUser.bbUser, index : int):
        """Moves the module at the given index in the shop's inventory to the user's inventory.

        :param bbUser user: The user attempting to buy the module
        :param int index: The index of the requested module in the shop's modules bbInventory's array of keys
        """
        self.userBuyModuleObj(user, self.modulesStock[index].item)
        

    def userBuyModuleObj(self, user : bbUser.bbUser, requestedModule : bbModule.bbModule):
        """Moves the given module from the shop's inventory to the user's.

        :param bbUser user: The user attempting to buy the module
        :param bbModule requestedModule: The module to sell to user
        """
        self.totalItems -= 1
        self.modulesStock.removeItem(requestedModule)
        user.inactiveModules.addItem(requestedModule)


    def userSellModuleObj(self, user : bbUser.bbUser, module : bbModule.bbModule):
        """Moves the given module from the user's inventory to the shop's.

        :param bbUser user: The user to buy module from
        :param bbModule module: The module to buy from user
        :raise OverflowError: When attempting to fill the shop beyond max capacity
        """
        if self.totalItems == bbConfig.kaamoMaxCapacity:
            raise OverflowError("Attempted to fill the shop beyond capacity.")
        self.totalItems += 1
        self.modulesStock.addItem(module)
        user.inactiveModules.removeItem(module)
    

    def userSellModuleIndex(self, user : bbUser.bbUser, index : int):
        """Moves the module at the given index in the user's inventory to the shop's inventory.

        :param bbUser user: The user to buy module from
        :param int index: The index of the module to buy from user, in the user's modules bbInventory's array of keys
        """
        self.userSellModuleObj(user, user.inactiveModules[index].item)



    # TURRET MANAGEMENT
    def userCanAffordTurretIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")


    def userBuyTurretIndex(self, user : bbUser.bbUser, index : int):
        """Moves the turret at the given index in the shop's inventory to the user's inventory.

        :param bbUser user: The user attempting to buy the turret
        :param int index: The index of the requested turret in the shop's turrets bbInventory's array of keys
        """
        self.userBuyTurretObj(user, self.turretsStock[index].item)
        
        
    def userBuyTurretObj(self, user : bbUser.bbUser, requestedTurret : bbTurret.bbTurret):
        """Moves the given turret from the shop's inventory to the user's.

        :param bbUser user: The user attempting to buy the turret
        :param bbTurret requestedTurret: The turret to sell to user
        """
        self.totalItems -= 1
        self.turretsStock.removeItem(requestedTurret)
        user.inactiveTurrets.addItem(requestedTurret)


    def userSellTurretObj(self, user : bbUser.bbUser, turret : bbTurret.bbTurret):
        """Moves the given turret from the user's inventory to the shop's.

        :param bbUser user: The user to buy turret from
        :param bbTurret turret: The turret to buy from user
        :raise OverflowError: When attempting to fill the shop beyond max capacity
        """
        if self.totalItems == bbConfig.kaamoMaxCapacity:
            raise OverflowError("Attempted to fill the shop beyond capacity.")
        self.totalItems += 1
        self.turretsStock.addItem(turret)
        user.inactiveTurrets.removeItem(turret)
    

    def userSellTurretIndex(self, user : bbUser.bbUser, index : int):
        """Moves the turret at the given index in the user's inventory to the shop's inventory.

        :param bbUser user: The user to buy turret from
        :param int index: The index of the turret to buy from user, in the user's turrets bbInventory's array of keys
        """
        self.userSellTurretObj(user, user.inactiveTurrets[index].item)



    # TOOL MANAGEMENT
    def userCanAffordToolIndex(self, user : bbUser.bbUser, index : int) -> bool:
        """No costs are incurred when transferring items to or from a KaamoShop.
        """
        raise NotImplementedError("Item affordability is not applicable to KaamoShops.")


    def userBuyToolIndex(self, user : bbUser.bbUser, index : int):
        """Moves the tool at the given index in the shop's inventory to the user's inventory.

        :param bbUser user: The user attempting to buy the tool
        :param int index: The index of the requested tool in the shop's tools bbInventory's array of keys
        """
        self.userBuyToolObj(user, self.toolsStock[index].item)
        

    def userBuyToolObj(self, user : bbUser.bbUser, requestedTool : bbToolItem.bbToolItem):
        """Moves the given tool from the shop's inventory to the user's.

        :param bbUser user: The user attempting to buy the tool
        :param bbToolItem requestedTool: The tool to sell to user
        """
        self.totalItems -= 1
        self.toolsStock.removeItem(requestedTool)
        user.inactiveTools.addItem(requestedTool)


    def userSellToolObj(self, user : bbUser.bbUser, tool : bbToolItem.bbToolItem):
        """Moves the given tool from the user's inventory to the shop's.

        :param bbUser user: The user to buy tool from
        :param bbTool tool: The tool to buy from user
        :raise OverflowError: When attempting to fill the shop beyond max capacity
        """
        if self.totalItems == bbConfig.kaamoMaxCapacity:
            raise OverflowError("Attempted to fill the shop beyond capacity.")
        self.totalItems += 1
        self.toolsStock.addItem(tool)
        user.inactiveTools.removeItem(tool)
    

    def userSellToolIndex(self, user : bbUser.bbUser, index : int):
        """Moves the tool at the given index in the user's inventory to the shop's inventory.

        :param bbUser user: The user to buy tool from
        :param int index: The index of the tool to buy from user, in the user's tools bbInventory's array of keys
        """
        self.userSellToolObj(user, user.inactiveTools[index].item)




    def toDict(self, **kwargs) -> dict:
        """Get a dictionary containing all information needed to reconstruct this shop instance.
        This includes maximum item counts and current stocks.

        :return: A dictionary containing all information needed to reconstruct this shop object
        :rtype: dict
        """
        if "saveType" not in kwargs or not kwargs["saveType"]:
            kwargs["saveType"] = True
            
        data = {}
        for invType in ["ship", "weapon", "module", "turret", "tool"]:
            stockDict = []
            currentStock = self.getStockByName(invType)
            
            for currentItem in currentStock.keys:
                if currentItem in currentStock.items:
                    stockDict.append(currentStock.items[currentItem].toDict(**kwargs))
                else:
                    bbLogger.log("kaamoShop", "toDict", "Failed to save invalid " + invType + " key '" + str(currentItem) + "' - not found in items dict", category="shop", eventType="UNKWN_KEY")
            
            data[invType + "sStock"] = stockDict

        return data


    @classmethod
    def fromDict(cls, shopDict : dict, **kwargs) -> bbShop:
        """Recreate a bbShop instance from its dictionary-serialized representation - the opposite of bbShop.toDict
        
        :param dict shopDict: A dictionary containing all information needed to construct the shop
        :return: A new bbShop object as described by shopDict
        :rtype: bbShop
        """
        shipsStock = bbInventory.TypeRestrictedInventory(bbShip.bbShip)
        weaponsStock = bbInventory.TypeRestrictedInventory(bbWeapon.bbWeapon)
        modulesStock = bbInventory.TypeRestrictedInventory(bbModule.bbModule)
        turretsStock = bbInventory.TypeRestrictedInventory(bbTurret.bbTurret)
        toolsStock = bbInventory.TypeRestrictedInventory(bbToolItem.bbToolItem)
        

        if "shipsStock" in shopDict:
            for shipListingDict in shopDict["shipsStock"]:
                shipsStock.addItem(bbShip.bbShip.fromDict(shipListingDict["item"]), quantity=shipListingDict["count"])

        if "weaponsStock" in shopDict:
            for weaponListingDict in shopDict["weaponsStock"]:
                weaponsStock.addItem(bbWeapon.bbWeapon.fromDict(weaponListingDict["item"]), quantity=weaponListingDict["count"])

        if "modulesStock" in shopDict:
            for moduleListingDict in shopDict["modulesStock"]:
                modulesStock.addItem(bbModuleFactory.fromDict(moduleListingDict["item"]), quantity=moduleListingDict["count"])

        if "turretsStock" in shopDict:
            for turretListingDict in shopDict["turretsStock"]:
                turretsStock.addItem(bbTurret.bbTurret.fromDict(turretListingDict["item"]), quantity=turretListingDict["count"])

        if "toolsStock" in shopDict:
            for toolListingDict in shopDict["toolsStock"]:
                toolsStock.addItem(bbToolItemFactory.fromDict(toolListingDict["item"]), quantity=toolListingDict["count"])

        return KaamoShop(shipsStock=shipsStock, weaponsStock=weaponsStock, modulesStock=modulesStock,
                                turretsStock=turretsStock, toolsStock=toolsStock)

