class BattleShipState:
    hull = 0
    armour = 0
    shield = 0
    remainingCloak = 0
    cloaking = False
    EMPCooldown = 0

    def __init__(self, battleShip):
        self.hull = battleShip.hull
        self.armour = battleShip.armour
        self.shield = battleShip.shield
        self.remainingCloak = battleShip.remainingCloak
        self.cloaking = battleShip.cloaking
        self.EMPCooldown = battleShip.EMPCooldown