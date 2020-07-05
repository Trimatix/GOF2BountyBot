"""
Class representing the state of a BattleShip at a given moment in time.
TODO: Move to BattleShip.py

@param battleShip -- the BattleShip to record the stats of
"""
class BattleShipState:
    def __init__(self, battleShip):
        self.hull = battleShip.hull
        self.armour = battleShip.armour
        self.shield = battleShip.shield
        self.remainingCloak = battleShip.remainingCloak
        self.cloaking = battleShip.cloaking
        self.EMPCooldown = battleShip.EMPCooldown