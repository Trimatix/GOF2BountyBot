# Typing imports
from __future__ import annotations
from typing import List, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from .modules import bbModule
    from discord import Embed

from .bbItem import bbItem
from . import bbTurret, bbWeapon, bbShipUpgrade, bbModuleFactory
from ...bbConfig import bbConfig, bbData
from ... import lib

class bbShip(bbItem):
    """An equippable and customisable ship for use by players and NPCs.

    :var hasNickname: whether or not this ship has a nickname
    :vartype hasNickname: bool
    :var nickname: A custom name for this ship, assigned by the owning player
    :vartype nickname: str
    :var armour: The amount of HP this ship's hull has - the last line of defence before death. #TODO: Should be renamed to hull or similar
    :vartype armour: int
    :var cargo: The amount of storage space for unequipped items and commodities this ship has
    :vartype cargo: int
    :var numSecondaries: The maximum number of secondary weapons equippable on this ship (not yet implemented) # TODO: Should probably be renamed to maxSecondaries
    :vartype numSecondaries: int
    :var handling: A measure of this ship's driveability (controls sensitivity)
    :vartype handling: int
    :var maxPrimaries: The maximum number of primary weapons equippable on this ship
    :vartype maxPrimaries: int
    :var maxTurrets: The maximum number of turrets equippable on this ship
    :vartype maxTurrets: int
    :var maxModules: The maximum number of modules equippable on this ship
    :vartype maxModules: int
    :var weapons: A list containing references to all primary weapon objects equipped by this ship. May contain duplicate references to save on memory.
    :vartype weapons: list[bbWeapon]
    :var modules: A list containing references to all module objects equipped by this ship. May contain duplicate references to save on memory.
    :vartype modules: list[bbModule]
    :var turrets: A list containing references to all turret objects equipped by this ship. May contain duplicate references to save on memory.
    :vartype turrets: list[bbTurret]
    :var upgradesApplied: A list containing references to all bbShipUpgrades objects applied to this ship. May contain duplicate references to save on memory.
    :vartype upgradesApplied: list[bbShipUpgrade]
    """

    def __init__(self, name : str, maxPrimaries : int, maxTurrets : int, maxModules : int, manufacturer="", armour=0.0, cargo=0, numSecondaries=0, handling=0, value=0, aliases=[], weapons=[], modules=[], turrets=[], wiki="", upgradesApplied=[], nickname="", icon="", emoji=lib.emojis.dumbEmoji.EMPTY, techLevel=-1, shopSpawnRate=0, builtIn=False):
        """
        :param str name: A name to uniquely identify this model of ship.
        :param str nickname: A custom name for this ship, assigned by the owning player
        :param int armour: The amount of HP this ship's hull has - the last line of defence before death. (Default 0) #TODO: Should be renamed to hull or similar
        :param int cargo: The amount of storage space for unequipped items and commodities this ship has (Default 0)
        :param int numSecondaries: The maximum number of secondary weapons equippable on this ship (not yet implemented) (Default 0)
        :param int handling: A measure of this ship's driveability (controls sensitivity) (Default 0)
        :param int maxPrimaries: The maximum number of primary weapons equippable on this ship
        :param int maxTurrets: The maximum number of turrets equippable on this ship
        :param int maxModules: The maximum number of modules equippable on this ship
        :param list[bbWeapon] weapons: A list containing references to all primary weapon objects equipped by this ship. May contain duplicate references to save on memory. (Default [])
        :param list[bbModule] modules: A list containing references to all module objects equipped by this ship. May contain duplicate references to save on memory. (Default [])
        :param list[bbTurret] turrets: A list containing references to all turret objects equipped by this ship. May contain duplicate references to save on memory. (Default [])
        :param list[bbShipUpgrade] upgradesApplied: A list containing references to all bbShipUpgrades objects applied to this ship. May contain duplicate references to save on memory. (Default [])
        :param int value: The number of credits this ship can be bought/sold for at base value at a shop. does not include any modifications or equipped items. (Default 0)
        :param list[str] aliases: Alternative name that can be used to refer to this type of ship (Default [])
        :param str wiki: A web page that is displayed as the wiki page for this ship. (Default "")
        :param str manufacturer: The name of the manufacturer of this ship (Default "")
        :param str icon: A URL pointing to an image to use for this ship's icon (Default "")
        :param lib.emojis.dumbEmoji emoji: The emoji to use for this ship's small icon (Default lib.emojis.dumbEmoji.EMPTY)
        :param int techLevel: A rating from 1 to 10 of this ship's technical advancement. Used as a rough and arbitrary measure for its effectiveness compared to other ships. (Default -1)
        :param bool builtIn: Whether this is a BountyBot standard ship (loaded in from bbData) or a custom spawned ship (Default False)
        :param float shopSpawnRate: A pre-calculated float indicating the highest spawn rate of this ship (i.e its spawn probability for a shop of the same techLevel) (Default 0)
        """
        super(bbShip, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)

        # TODO: Log to bbLogger in these cases
        if len(weapons) > maxPrimaries:
            ValueError("passed more weapons than can be stored on this ship - maxPrimaries")
        if len(modules) > maxModules:
            ValueError("passed more modules than can be stored on this ship - maxModules")
        if len(turrets) > maxTurrets:
            ValueError("passed more turrets than can be stored on this ship - maxTurrets")

        # if self.name in bbData.builtInShipData:
        #     self.shopSpawnRate = bbData.shipKeySpawnRates[self.name]
        # else:
        #     self.shopSpawnRate = 0

        self.armour = armour
        self.cargo = cargo
        self.numSecondaries = numSecondaries
        self.handling = handling
        
        self.maxPrimaries = maxPrimaries
        self.maxTurrets = maxTurrets
        self.maxModules = maxModules

        self.weapons = weapons
        self.modules = modules
        self.turrets = turrets

        self.nickname = ""
        self.hasNickname = False
        if nickname != "":
            self.changeNickname(nickname)

        self.upgradesApplied = upgradesApplied

        self.shopSpawnRate = shopSpawnRate


    def getNumWeaponsEquipped(self) -> int:
        """Fetch the number of weapons this ship currently has equipped

        :return: The number of primary weapons equipped on the ship
        :rtype: int
        """
        return len(self.weapons)


    def canEquipMoreWeapons(self) -> bool:
        """Decide whether or not this ship has any free primary weapon slots

        :return: True if at least one primary weapon slot is free, False otherwise
        :rtype: bool
        """
        return self.getNumWeaponsEquipped() < self.getMaxPrimaries()

    
    def getNumModulesEquipped(self) -> int:
        """Fetch the number of modules this ship currently has equipped

        :return: The number of modules equipped on the ship
        :rtype: int
        """
        return len(self.modules)


    def canEquipMoreModules(self) -> bool:
        """Decide whether or not this ship has any free module slots

        :return: True if at least one module slot is free, False otherwise
        :rtype: bool
        """
        return self.getNumModulesEquipped() < self.getMaxModules()

    
    def getNumTurretsEquipped(self) -> int:
        """Fetch the number of turrets this ship currently has equipped

        :return: The number of turrets equipped on the ship
        :rtype: int
        """
        return len(self.turrets)


    def canEquipMoreTurrets(self) -> bool:
        """Decide whether or not this ship has any free turret slots

        :return: True if at least one turret slot is free, False otherwise
        :rtype: bool
        """
        return self.getNumTurretsEquipped() < self.getMaxTurrets()

    
    def hasWeaponsEquipped(self) -> bool:
        """Decide whether or not this ship has any Weapons equipped

        :return: True if at least one Weapon is equipped on this ship, False otherwise
        :rtype: bool
        """
        return self.getNumWeaponsEquipped() > 0


    def hasModulesEquipped(self) -> bool:
        """Decide whether or not this ship has any Modules equipped

        :return: True if at least one Module is equipped on this ship, False otherwise
        :rtype: bool
        """
        return self.getNumModulesEquipped() > 0


    def hasTurretsEquipped(self) -> bool:
        """Decide whether or not this ship has any Turrets equipped

        :return: True if at least one Turret is equipped on this ship, False otherwise
        :rtype: bool
        """
        return self.getNumTurretsEquipped() > 0


    def equipWeapon(self, weapon : bbWeapon):
        """Equip the given weapon onto the ship

        :param bbWeapon weapon: The weapon object to equip
        :raise OverflowError: If no weapon slots are available on the ship
        """
        if not self.canEquipMoreWeapons():
            raise OverflowError("Attempted to equip a weapon but all weapon slots are full")
        self.weapons.append(weapon)
    

    def unequipWeaponObj(self, weapon : bbWeapon):
        """Unequip the given weapon object reference from the ship

        :param bbWeapon weapon: The weapon object to unequip 
        """
        self.weapons.remove(weapon)


    def unequipWeaponIndex(self, index : int):
        """Unequip a weapon by its index in the weapons array.

        :param int index: The index of the weapon to unequip from the ship
        """
        self.weapons.pop(index)


    def getWeaponAtIndex(self, index : int) -> bbWeapon:
        """Fetch the weapon object equipped at the given index

        :param int index: The index of the weapon object to fetch
        :return: The weapon object equipped at the given index
        :rtype: bbWeapon
        """
        return self.weapons[index]
    

    def canEquipModuleType(self, moduleType : type) -> bool:
        """Decide whether or not the ship has space for a module of the given type.
        This also accounts for module type limits, for example only allowing players to equip one shield module at a time.

        :param type moduleType: The bbModule subclass to test for free equip space
        :return: True if at least one module slot is free for the given bbModule type, False otherwise.
        :rtype: bool
        """
        if moduleType in bbModuleFactory.maxModuleTypeEquips and bbModuleFactory.maxModuleTypeEquips[moduleType] != -1:
            numFound = 1
            for equippedModule in self.modules:
                if equippedModule.getType() == moduleType:
                    numFound += 1
                    if numFound > bbModuleFactory.maxModuleTypeEquips[moduleType]:
                        return False
        return True


    def equipModule(self, module : bbModule.bbModule):
        """Equip the given bbModule onto the ship.

        :param bbModule module: The bbModule object to equip
        :raise OverflowError: When no module slots are free
        :raise ValueError: When the ship already has the maximum number of modules equipped of the given type.
        """
        if not self.canEquipMoreModules():
            raise OverflowError("Attempted to equip a module but all module slots are full")
        if not self.canEquipModuleType(module.getType()):
            raise ValueError("Attempted to equip a module of a type that is already at its maximum capacity: " + str(module))

        self.modules.append(module)
    

    def unequipModuleObj(self, module : bbModule.bbModule):
        """Unequip the given module object reference

        :param bbModule module: The module to unequip
        """
        self.modules.remove(module)


    def unequipModuleIndex(self, index : int):
        """Unequip the module equipped at the given index in the modules array

        :param int index: The index of the module to unequip
        """
        self.modules.pop(index)


    def getModuleAtIndex(self, index : int) -> bbModule.bbModule:
        """Fetch the bbModule object reference that is equipped at the given index

        :param int index: The index of the module to fetch
        :return: The module reference equipped at the given index
        :rtype: bbModule 
        """
        return self.modules[index]


    def equipTurret(self, turret : bbTurret):
        """Equip the given turret onto the ship

        :param bbTurret turret: The turret object to equip
        :raise OverflowError: If no turret slots are available on the ship
        """
        if not self.canEquipMoreTurrets():
            raise OverflowError("Attempted to equip a turret but all turret slots are full")
        self.turrets.append(turret)
    

    def unequipTurretObj(self, turret : bbTurret):
        """Unequip the given turret object reference from the ship

        :param bbTurret turret: The turret object to unequip 
        """
        self.turrets.remove(turret)


    def unequipTurretIndex(self, index : int):
        """Unequip a turret by its index in the turrets array.

        :param int index: The index of the turret to unequip from the ship
        """
        self.turrets.pop(index)


    def getTurretAtIndex(self, index : int) -> bbTurret:
        """Fetch the turret object equipped at the given index

        :param int index: The index of the turret object to fetch
        :return: The turret object equipped at the given index
        :rtype: bbTurret
        """
        return self.turrets[index]

    
    # TODO: All of these 'get total' functions could probably be consolidated into a single function, making use of getActivesByName etc
    def getDPS(self, shipUpgradesOnly=False) -> int:
        """Get the total DPS provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship DPS and that granted by applied shipUpgrades (Default False)
        :return: The ship's total DPS, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = 0
        multiplier = 1
        if not shipUpgradesOnly:
            for weapon in self.weapons:
                total += weapon.dps
            for turret in self.turrets:
                total += turret.dps
            for module in self.modules:
                total += module.dps
                multiplier *= module.dpsMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.dps
            multiplier *= upgrade.dpsMultiplier
        return total * multiplier

    
    def getShield(self, shipUpgradesOnly=False) -> int:
        """Get the total Shield provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship Shield and that granted by applied shipUpgrades (Default False)
        :return: The ship's total Shield, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = 0
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.shield
                multiplier *= module.shieldMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.shield
            multiplier *= upgrade.shieldMultiplier
        return int(total * multiplier)


    def getArmour(self, shipUpgradesOnly=False) -> int:
        """Get the total Armour provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship Armour and that granted by applied shipUpgrades (Default False)
        :return: The ship's total Armour, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.armour
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.armour
                multiplier *= module.armourMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.armour
            multiplier *= upgrade.armourMultiplier
        return int(total * multiplier)


    def getCargo(self, shipUpgradesOnly=False) -> int:
        """Get the total Cargo provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship Cargo and that granted by applied shipUpgrades (Default False)
        :return: The ship's total Cargo, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.cargo
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.cargo
                multiplier *= module.cargoMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.cargo
            multiplier *= upgrade.cargoMultiplier
        return int(total * multiplier)


    def getHandling(self, shipUpgradesOnly=False) -> int:
        """Get the total Handling provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship Handling and that granted by applied shipUpgrades (Default False)
        :return: The ship's total Handling, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.handling
        multiplier = 1
        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.handling
                multiplier *= module.handlingMultiplier
        
        for upgrade in self.upgradesApplied:
            total += upgrade.handling
            multiplier *= upgrade.handlingMultiplier
        return int(total * multiplier)


    def getNumSecondaries(self, shipUpgradesOnly=False) -> int:
        """Get the total NumSecondaries provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship NumSecondaries and that granted by applied shipUpgrades (Default False)
        :return: The ship's total NumSecondaries, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.numSecondaries
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.numSecondaries
            multiplier *= upgrade.numSecondariesMultiplier
        return int(total * multiplier)


    def getMaxPrimaries(self, shipUpgradesOnly=False) -> int:
        """Get the total MaxPrimaries provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship MaxPrimaries and that granted by applied shipUpgrades (Default False)
        :return: The ship's total MaxPrimaries, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.maxPrimaries
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.maxPrimaries
            multiplier *= upgrade.maxPrimariesMultiplier
        return int(total * multiplier)


    def getMaxTurrets(self, shipUpgradesOnly=False) -> int:
        """Get the total MaxTurrets provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship MaxTurrets and that granted by applied shipUpgrades (Default False)
        :return: The ship's total MaxTurrets, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.maxTurrets
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.maxTurrets
            multiplier *= upgrade.maxTurretsMultiplier
        return int(total * multiplier)


    def getMaxModules(self, shipUpgradesOnly=False) -> int:
        """Get the total MaxModules provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship MaxModules and that granted by applied shipUpgrades (Default False)
        :return: The ship's total MaxModules, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.maxModules
        multiplier = 1
        
        for upgrade in self.upgradesApplied:
            total += upgrade.maxModules
            multiplier *= upgrade.maxModulesMultiplier
        return int(total * multiplier)


    def getValue(self, shipUpgradesOnly=False) -> int:
        """Get the total Value provided by the equipped items and upgrades.
        If shipUpgradesOnly is given as True, then only applied shipUpgrades will be included in the calculation.
        This is used to give a 'base' measurement, as ship upgrades cannot be removed and are considered part of the ship once applied.

        :param bool shipUpgradesOnly: Whether to include all equipped items, or only the base ship Value and that granted by applied shipUpgrades (Default False)
        :return: The ship's total Value, including bonuses/penalties from ship upgrades (and potentially equipped items)
        :rtype: int
        """
        total = self.value

        if not shipUpgradesOnly:
            for module in self.modules:
                total += module.getValue()
            for weapon in self.weapons:
                total += weapon.getValue()
            for turret in self.turrets:
                total += turret.getValue()
        for upgrade in self.upgradesApplied:
            total += upgrade.valueForShip(self)

        return total

    
    def applyUpgrade(self, upgrade : bbShipUpgrade):
        """Apply the given ship upgrade, locking it and its stats into the ship.
        Ship upgrades cannot be removed.

        :param bbShipUpgrade upgrade: the upgrade to apply
        """
        self.upgradesApplied.append(upgrade)

    
    def changeNickname(self, nickname : str):
        """Change the ship's custom nickname.
        giving nickname = "" is equivilent to a call to removeNickname

        :param str nickname: The new nickname to set
        """
        self.nickname = nickname
        if nickname != "":
            self.hasNickname = True

    
    def removeNickname(self):
        """Remove the ship's custom nickname, setting BB to display the ship type instead where needed.
        """
        if self.hasNickname:
            self.nickname = ""
            self.hasNickname = False

        
    def getNameOrNick(self) -> str:
        """Return the ship's nickname if it has one, or the name of the ship.

        :return: The ship's nickname if it has one, the ship's name otherwise
        :rtype: str
        """
        return self.nickname if self.hasNickname else self.name

    
    def getNameAndNick(self) -> str:
        """If the ship has a nickname, return the nickname followed by the ship name in brackets. Otherwise, just return the ship's name.

        :return: If the ship has a nickname, the nickname followed by the original name in brackets. The ship name on its own otherwise.
        :rtype: str
        """
        return self.name if not self.hasNickname else self.nickname + " (" + self.name + ")"


    def transferItemsTo(self, other : bbShip):
        """Attempt to transfer as many equipped items as possible from this ship to another one.
        If there is not enough space to transfer any items, they will remain on this ship.

        :param bbShip other: The ship to transfer items to
        :raise TypeError: When given any type other than bbShip
        """
        if not isinstance(other, bbShip):
            raise TypeError("Can only transfer items to another bbShip. Given " + str(type(other)))

        while self.hasWeaponsEquipped() and other.canEquipMoreWeapons():
            other.equipWeapon(self.weapons.pop(0))

        leftoverModules = []
        while self.hasModulesEquipped() and other.canEquipMoreModules():
            if other.canEquipModuleType(self.modules[0].getType()):
                other.equipModule(self.modules.pop(0))
            else:
                leftoverModules.append(self.modules.pop(0))
                
        for leftoverModule in leftoverModules:
            self.modules.append(leftoverModule)

        while self.hasTurretsEquipped() and other.canEquipMoreTurrets():
            other.equipTurret(self.turrets.pop(0))


    def getActivesByName(self, item : str) -> Union[bbWeapon.bbWeapon, bbModule.bbModule, bbTurret.bbTurret]:
        """Return a requested array of equipped items, specified by string name.

        :param str item: one of weapon, module or turret.
        :return: An array of equipped items of the named typed.
        :rtype: list[bbWeapon or bbModule or bbTurret]
        :raise ValueError: If the requested item type is invalid
        :raise NotImplementedError: If a valid item type is requested, not just yet implemented (e.g commodity)
        """
        if item == "all" or item == "ship" or item not in bbConfig.validItemNames:
            raise ValueError("Invalid item type: " + str(item))
        elif item == "weapon":
            return self.weapons
        elif item == "module":
            return self.modules
        elif item == "turret":
            return self.turrets
        else:
            raise NotImplementedError("Valid, not unrecognised item type: " + item)


    def clearWeapons(self):
        """Delete all weapons equipped on the ship, without saving them.
        """
        self.weapons = []


    def clearModules(self):
        """Delete all modules equipped on the ship, without saving them.
        """
        self.modules = []


    def clearTurrets(self):
        """Delete all turrets equipped on the ship, without saving them.
        """
        self.turrets = []


    def statsStringShort(self) -> str:
        """Summarise all of the ship's statistics as a string, including equipped item names.
        
        :return: A summary of all of the ship's attributes and equipped items
        :rtype: str
        """
        stats = ""
        stats += "• *Armour: " + str(self.getArmour(shipUpgradesOnly=True)) + ("(+)" if self.getArmour(shipUpgradesOnly=True) > self.armour else "") + "*\n"
        # stats += "Cargo hold: " + str(self.cargo) + ", "
        # stats += "Handling: " + str(self.handling) + ", "
        stats += "• *Primaries: " + str(len(self.weapons)) + "/" + str(self.getMaxPrimaries(shipUpgradesOnly=True)) + ("(+)" if self.getMaxPrimaries(shipUpgradesOnly=True) > self.maxPrimaries else "") + "*\n"
        if len(self.weapons) > 0:
            stats += "*["
            for weapon in self.weapons:
                stats += weapon.name + ", "
            stats = stats[:-2] + "]*\n"
        # stats += "Max secondaries: " + str(self.numSecondaries) + ", "
        stats += "• *Turrets: " + str(len(self.turrets)) + "/" + str(self.getMaxTurrets(shipUpgradesOnly=True)) + ("(+)" if self.getMaxTurrets(shipUpgradesOnly=True) > self.maxTurrets else "") + "*\n"
        if len(self.turrets) > 0:
            stats += "*["
            for turret in self.turrets:
                stats += turret.name + ", "
            stats = stats[:-2] + "]*\n"
        stats += "• *Modules: " + str(len(self.modules)) + "/" + str(self.getMaxModules(shipUpgradesOnly=True)) + ("(+)" if self.getMaxModules(shipUpgradesOnly=True) > self.maxModules else "") + "*\n"
        if len(self.modules) > 0:
            stats += "*["
            for module in self.modules:
                stats += module.name + ", "
            stats = stats[:-2] + "]*\n"
        return stats

    
    def statsStringNoItems(self) -> str:
        """Return a shorter summary of the ship's statistics, ignoring any equipped items.

        :return: A string summary of the ship's statistics, ignoring any equipped items.
        :rtype: str
        """
        stats = ""
        stats += "*Armour: " + str(self.getArmour(shipUpgradesOnly=True)) + ("(+)" if self.getArmour(shipUpgradesOnly=True) > self.armour else "") + ", "
        stats += "Cargo hold: " + str(self.getCargo(shipUpgradesOnly=True)) + ("(+)" if self.getCargo(shipUpgradesOnly=True) > self.cargo else "") + ", "
        stats += "Handling: " + str(self.getHandling(shipUpgradesOnly=True)) + ("(+)" if self.getHandling(shipUpgradesOnly=True) > self.handling else "") + ", "
        stats += "Max secondaries: " + str(self.getNumSecondaries(shipUpgradesOnly=True)) + ("(+)" if self.getNumSecondaries(shipUpgradesOnly=True) > self.numSecondaries else "") + "*"
        return stats


    def fillLoadoutEmbed(self, baseEmbed : Embed, shipEmoji : bool = False):
        """Populate a discord.embed with information describing the ship.

        :param discord.Embed baseEmbed: The embed to add fields to
        :param bool shipEmoji: whether or not to use the ship's emoji next to its name. You may wish to leave this as false and instead use the ship's icon in the embed icon (Default False)
        """
        baseEmbed.add_field(name="Active Ship:", value=(self.emoji.sendable if shipEmoji and self.hasEmoji else "") + self.getNameAndNick() + "\n" + self.statsStringNoItems(), inline=False)

        if self.getMaxPrimaries() > 0:
            baseEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(self.weapons)) + "/" + str(self.getMaxPrimaries()) + "*", inline=False)
            for weaponNum in range(1, len(self.weapons) + 1):
                baseEmbed.add_field(name=str(weaponNum) + ". " + self.weapons[weaponNum - 1].name, value=(self.weapons[weaponNum - 1].emoji.sendable if self.weapons[weaponNum - 1].hasEmoji else "") + self.weapons[weaponNum - 1].statsStringShort(), inline=True)

        if self.getMaxModules() > 0:
            baseEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(self.modules)) + "/" + str(self.getMaxModules()) + "*", inline=False)
            for moduleNum in range(1, len(self.modules) + 1):
                baseEmbed.add_field(name=str(moduleNum) + ". " + self.modules[moduleNum - 1].name, value=(self.modules[moduleNum - 1].emoji.sendable if self.modules[moduleNum - 1].hasEmoji else "") + self.modules[moduleNum - 1].statsStringShort(), inline=True)
        
        if self.getMaxTurrets() > 0:
            baseEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(self.turrets)) + "/" + str(self.getMaxTurrets()) + "*", inline=False)
            for turretNum in range(1, len(self.turrets) + 1):
                baseEmbed.add_field(name=str(turretNum) + ". " + self.turrets[turretNum - 1].name, value=(self.turrets[turretNum - 1].emoji.sendable if self.turrets[turretNum - 1].hasEmoji else "") + self.turrets[turretNum - 1].statsStringShort(), inline=True)

        return baseEmbed
    

    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbShip class
        :rtype: type
        """
        return bbShip


    def toDict(self) -> dict:
        """Serialize this bbShip into dictionary format, for saving to file. Includes all equiped items and upgrades

        :return: A dictionary containing all information needed to reconstruct this ship. If the module is builtIn, several statistics are omitted to save space.
        :rtype: dict
        """
        itemDict = super(bbShip, self).toDict()

        weaponsList = []
        for weapon in self.weapons:
            weaponsList.append(weapon.toDict())
        
        modulesList = []
        for module in self.modules:
            modulesList.append(module.toDict())

        turretsList = []
        for turret in self.turrets:
            turretsList.append(turret.toDict())
        
        upgradesList = []
        for upgrade in self.upgradesApplied:
            upgradesList.append(upgrade.toDict())

        itemDict["weapons"] = weaponsList
        itemDict["modules"] = modulesList
        itemDict["turrets"] = turretsList
        itemDict["shipUpgrades"] = upgradesList
        itemDict["nickname"] = self.nickname

        if not self.builtIn:
            itemDict["armour"] = self.armour
            itemDict["cargo"] = self.cargo
            itemDict["numSecondaries"] = self.numSecondaries
            itemDict["handling"] = self.handling
            itemDict["maxPrimaries"] = self.maxPrimaries
            itemDict["maxTurrets"] = self.maxTurrets
            itemDict["maxModules"] = self.maxModules
        
        return itemDict


    def __str__(self) -> str:
        """Get a short string identifying the ship. Currenly only includes the ship name (type)

        :return: A short string identifying this bbShip object
        :rtype: str
        """
        return "<bbShip: " + self.name + ">"


def fromDict(shipDict : dict) -> bbShip:
    """Factory function constructing a new bbShip object from the given dictionary representation - the opposite of bbShip.toDict
    As with most other item fromDict functions, all missing information for builtIn ships is replaced by data from the corresponding bbData entry.

    :param dict shipDict: A dictionary containing all information required to construct the requested ship
    :return: A new bbShip object as described in shipDict
    :rtype: bbShip
    """
    weapons = []
    if "weapons" in shipDict:
        for weapon in shipDict["weapons"]:
            weapons.append(bbWeapon.fromDict(weapon))

    modules = []
    if "modules" in shipDict:
        for module in shipDict["modules"]:
            modules.append(bbModuleFactory.fromDict(module))

    turrets = []
    if "turrets" in shipDict:
        for turret in shipDict["turrets"]:
            turrets.append(bbTurret.fromDict(turret))

    shipUpgrades = []
    if "shipUpgrades" in shipDict:
        for shipUpgrade in shipDict["shipUpgrades"]:
            shipUpgrades.append(bbShipUpgrade.fromDict(shipUpgrade))
    
    if shipDict["builtIn"]:
        builtInDict = bbData.builtInShipData[shipDict["name"]]

        builtInWeapons = []
        if "weapons" in shipDict:
            for weapon in shipDict["weapons"]:
                builtInWeapons.append(bbWeapon.fromDict(weapon))

        builtInModules = []
        if "modules" in shipDict:
            for module in shipDict["modules"]:
                builtInModules.append(bbModuleFactory.fromDict(module))

        builtInTurrets = []
        if "turrets" in shipDict:
            for turret in shipDict["turrets"]:
                builtInTurrets.append(bbTurret.fromDict(turret))

        builtInShipUpgrades = []
        if "shipUpgrades" in shipDict:
            for shipUpgrade in shipDict["shipUpgrades"]:
                builtInShipUpgrades.append(bbShipUpgrade.fromDict(shipUpgrade))

        newShip = bbShip(builtInDict["name"], builtInDict["maxPrimaries"], builtInDict["maxTurrets"], builtInDict["maxModules"], manufacturer=builtInDict["manufacturer"] if "manufacturer" in builtInDict else "",
                    armour=builtInDict["armour"] if "armour" in builtInDict else 0, cargo=builtInDict["cargo"] if "cargo" in builtInDict else 0,
                    numSecondaries=builtInDict["numSecondaries"] if "numSecondaries" in builtInDict else 0, handling=builtInDict["handling"] if "handling" in builtInDict else 0,
                    value=builtInDict["value"] if "value" in builtInDict else 0, aliases=builtInDict["aliases"] if "aliases" in builtInDict else [],
                    weapons=weapons if "weapons" in shipDict else builtInWeapons, modules=modules if "modules" in shipDict else builtInModules, turrets=turrets if "turrets" in shipDict else builtInTurrets, wiki=builtInDict["wiki"] if "wiki" in builtInDict else "0",
                    upgradesApplied=shipUpgrades if "shipUpgrades" in shipDict else builtInShipUpgrades, nickname=shipDict["nickname"] if "nickname" in shipDict else (builtInDict["nickname"] if "nickname" in builtInDict else ""), icon=builtInDict["icon"] if "icon" in builtInDict else bbData.rocketIcon, emoji=lib.emojis.dumbEmojiFromStr(builtInDict["emoji"]) if "emoji" in builtInDict else lib.emojis.dumbEmoji.EMPTY, techLevel=builtInDict["techLevel"] if "techLevel" in builtInDict else -1, shopSpawnRate=builtInDict["shopSpawnRate"] if "shopSpawnRate" in builtInDict else 0,
                    builtIn=True)
        return newShip

    else:
        return bbShip(shipDict["name"], shipDict["maxPrimaries"], shipDict["maxTurrets"], shipDict["maxModules"], manufacturer=shipDict["manufacturer"] if "manufacturer" in shipDict else "",
                        armour=shipDict["armour"] if "armour" in shipDict else 0, cargo=shipDict["cargo"] if "cargo" in shipDict else 0,
                        numSecondaries=shipDict["numSecondaries"] if "numSecondaries" in shipDict else 0, handling=shipDict["handling"] if "handling" in shipDict else 0,
                        value=shipDict["value"] if "value" in shipDict else 0, aliases=shipDict["aliases"] if "aliases" in shipDict else [],
                        weapons=weapons, modules=modules, turrets=turrets, wiki=shipDict["wiki"] if "wiki" in shipDict else "0",
                        upgradesApplied=shipUpgrades, nickname=shipDict["nickname"] if "nickname" in shipDict else "", icon=shipDict["icon"] if "icon" in shipDict else bbData.rocketIcon, emoji=lib.emojis.dumbEmojiFromStr(shipDict["emoji"]) if "emoji" in shipDict else lib.emojis.dumbEmoji.EMPTY, techLevel=shipDict["techLevel"] if "techLevel" in shipDict else -1, shopSpawnRate=shipDict["shopSpawnRate"] if "shopSpawnRate" in shipDict else 0,
                        builtIn=False)
