from . import BattleShip

class BattleShipState:
    """Class representing the state of a BattleShip at a given moment in time.
    TODO: Move to BattleShip.py"""

    def __init__(self, battleShip : BattleShip.BattleShip):
        """
        :param BattleShip battleShip: the BattleShip to record the stats of
        """
        self.hull = battleShip.hull
        self.armour = battleShip.armour
        self.shield = battleShip.shield
        self.remainingCloak = battleShip.remainingCloak
        self.cloaking = battleShip.cloaking
        self.EMPCooldown = battleShip.EMPCooldown
