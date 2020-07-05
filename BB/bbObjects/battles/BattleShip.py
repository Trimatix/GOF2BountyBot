from ..items.modules import bbCloakModule

"""
A class representing ships participting in a duel.
The ship has three health pools; hull, armour and shield.

@param bbShip -- The bbShip for this BattleShip to inherit stats from
"""
class BattleShip:
    def __init__(self, bbShip):
        self.bbShip = bbShip
        self.hull = bbShip.armour
        self.armour = bbShip.getArmour() - self.hull
        self.shield = bbShip.getShield()
        self.dps = bbShip.getDPS()
        self.cloaks = []
        self.EMPs = []
        self.remainingCloak = 0
        self.cloaking = False
        self.EMPCooldown = 0
        # TODO: Update to use only one cloak module per ship
        for module in bbShip.modules:
            if isinstance(module, bbCloakModule):
                self.cloaks += module
    

    """
    Test whether this BattleShip has any hull HP remaining.

    @return -- True if this BattleShip's hull HP is greater than 0, False otherwise
    """
    def hasHull(self):
        return self.hull > 0

    
    """
    Test whether this BattleShip has any armour HP remaining.

    @return -- True if this BattleShip's armour HP is greater than 0, False otherwise
    """
    def hasArmour(self):
        return self.armour > 0


    """
    Test whether this BattleShip has any shield HP remaining.

    @return -- True if this BattleShip's shield HP is greater than 0, False otherwise
    """
    def hasShield(self):
        return self.shield > 0

    
    """
    Test whether this BattleShip has any cloak modules equipped.

    @return -- True if this BattleShip has at least one cloak module equipped, False otherwise
    """
    def hasCloaks(self):
        return len(self.cloaks) > 0


    """
    Get this BattleShip's remaining shield HP.

    @return -- Integer amount of shield HP remaining; 0 or more.
    """
    def getShield(self):
        return self.shield


    """
    Get this BattleShip's remaining armour HP.

    @return -- Integer amount of armour HP remaining; 0 or more.
    """
    def getArmour(self):
        return self.armour


    """
    Get this BattleShip's remaining hull HP.

    @return -- Integer amount of hull HP remaining; 0 or more.
    """
    def getHull(self):
        return self.hull

    """
    Set this BattleShip's remaining shield HP.

    @param new -- Integer new amount of shield HP remaining; 0 or more.
    """
    def setShield(self, new):
        self.shield = new
        
    """
    Set this BattleShip's remaining armour HP.

    @param new -- Integer new amount of armour HP remaining; 0 or more.
    """
    def setArmour(self, new):
        self.armour = new

    """
    Set this BattleShip's remaining hull HP.

    @param new -- Integer new amount of hull HP remaining; 0 or more.
    """
    def setHull(self, new):
        self.hull = new



