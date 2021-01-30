from ..items.modules import cloakModule
from ..items import shipItem


class BattleShip:
    """A class representing ships participting in a duel.
    The ship has three health pools; hull, armour and shield.
    """

    def __init__(self, shipItem : shipItem.Ship):
        """
        :param shipItem shipItem: The shipItem for this BattleShip to inherit stats from
        """
        self.shipItem = shipItem
        self.hull = shipItem.armour
        self.armour = shipItem.getArmour() - self.hull
        self.shield = shipItem.getShield()
        self.dps = shipItem.getDPS()
        self.cloaks = []
        self.EMPs = []
        self.remainingCloak = 0
        self.cloaking = False
        self.EMPCooldown = 0
        # TODO: Update to use only one cloak module per ship
        for module in shipItem.modules:
            if isinstance(module, cloakModule):
                self.cloaks += module
    

    def hasHull(self) -> bool:
        """Test whether this BattleShip has any hull HP remaining.

        :return: True if this BattleShip's hull HP is greater than 0, False otherwise
        :rtype: bool
        """
        return self.hull > 0

    
    
    def hasArmour(self) -> bool:
        """Test whether this BattleShip has any armour HP remaining.

        :return: True if this BattleShip's armour HP is greater than 0, False otherwise
        :rtype: bool
        """
        return self.armour > 0


    
    def hasShield(self) -> bool:
        """Test whether this BattleShip has any shield HP remaining.

        :return: True if this BattleShip's shield HP is greater than 0, False otherwise
        :rtype: bool
        """
        return self.shield > 0

    
    
    def hasCloaks(self) -> bool:
        """Test whether this BattleShip has any cloak modules equipped.

        :return: True if this BattleShip has at least one cloak module equipped, False otherwise
        :rtype: bool
        """
        return len(self.cloaks) > 0


    
    def getShield(self) -> int:
        """Get this BattleShip's remaining shield HP.

        :return: Integer amount of shield HP remaining; 0 or more.
        :rtype: int
        """
        return self.shield


    
    def getArmour(self) -> int:
        """Get this BattleShip's remaining armour HP.

        :return: Integer amount of armour HP remaining; 0 or more.
        :rtype: int
        """
        return self.armour


    
    def getHull(self) -> int:
        """Get this BattleShip's remaining hull HP.

        :return: Integer amount of hull HP remaining; 0 or more.
        :rtype: int
        """
        return self.hull

    
    def setShield(self, new : int):
        """Set this BattleShip's remaining shield HP.

        :param int new: Integer new amount of shield HP remaining; 0 or more.
        """
        self.shield = new
        
    
    def setArmour(self, new : int):
        """Set this BattleShip's remaining armour HP.

        :param int new: Integer new amount of armour HP remaining; 0 or more.
        """
        self.armour = new

    
    def setHull(self, new : int):
        """Set this BattleShip's remaining hull HP.

        :param int new: Integer new amount of hull HP remaining; 0 or more.
        """
        self.hull = new



