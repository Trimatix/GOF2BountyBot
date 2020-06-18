from ..bbModule import CloakModule

class BattleShip:
    bbShip = None
    hull = 0
    armour = 0
    shield = 0
    dps = 0
    cloaks = []
    EMPs = []
    remainingCloak = 0
    cloaking = False
    EMPCooldown = 0

    def __init__(self, bbShip):
        self.bbShip = bbShip
        self.hull = bbShip.armour
        self.armour = bbShip.getArmour() - self.hull
        self.shield = bbShip.getShield()
        self.dps = bbShip.getDPS()
        for module in bbShip.modules:
            if module.getType() == CloakModule:
                self.cloaks += module
    

    def hasHull(self):
        return self.hull > 0

    
    def hasArmour(self):
        return self.armour > 0


    def hasShield(self):
        return self.shield > 0

    
    def hasCloaks(self):
        return len(self.cloaks) > 0


    def getShield(self):
        return self.shield


    def getArmour(self):
        return self.armour


    def getHull(self):
        return self.hull


    def setShield(self, new):
        self.shield = new
        

    def setArmour(self, new):
        self.armour = new


    def setHull(self, new):
        self.hull = new



