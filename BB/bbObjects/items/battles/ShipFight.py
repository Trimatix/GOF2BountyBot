from .BattleShip import BattleShip
from .BattleShipState import BattleShipState
import random
from ....bbConfig import bbConfig

class ShipFight:
    ship1 = None
    ship2 = None
    battleLog = []
    battleState = []

    def __init__(self, bbShip1, bbShip2):
        self.ship1 = BattleShip(bbShip1)
        self.ship2 = BattleShip(bbShip2)


    def fightShips(self, variancePercent):
        # Fetch ship total DPSs
        ship1DPS = self.ship1.dps
        ship2DPS = self.ship2.dps

        # Vary DPSs by +=variancePercent
        ship1DPSVariance = ship1DPS * variancePercent
        ship2DPSVariance = ship2DPS * variancePercent

        if ship1DPS == 0:
            if ship2DPS == 0:
                return {"winningShip": None, "battleLog":["Both ships have zero DPS!"]}
            return {"winningShip": self.ship2.bbShip, "battleLog":["{PILOT1NAME} has zero DPS!"]}
        if ship2DPS == 0:
            if ship1DPS == 0:
                return {"winningShip": None, "battleLog":["Both ships have zero DPS!"]}
            return {"winningShip": self.ship1.bbShip, "battleLog":["{PILOT2NAME} has zero DPS!"]}


        ship1EstimatedTTK = (self.ship1.hull + self.ship1.armour + self.ship1.shield) / self.ship2.dps
        ship2EstimatedTTK = (self.ship2.hull + self.ship2.armour + self.ship2.shield) / self.ship1.dps
        shortestEstimatedTTK = min(ship1EstimatedTTK, ship2EstimatedTTK)

        tickRate = 1
        extraSteps = 0
        if shortestEstimatedTTK > bbConfig.duelLogMaxLength:
            tickRate = (shortestEstimatedTTK - (shortestEstimatedTTK % bbConfig.duelLogMaxLength)) // bbConfig.duelLogMaxLength
            extraSteps = shortestEstimatedTTK % bbConfig.duelLogMaxLength

        currentTime = 0
        while self.ship1.hasHull() and self.ship2.hasHull():
            # print("SHIP1",self.ship1.hull,self.ship1.armour,self.ship1.shield)
            # print("SHIP2",self.ship2.hull,self.ship2.armour,self.ship2.shield)

            # Use timestep of 1 until remaining time is divisible by tickRate
            if extraSteps > 0:
                currentTick = 1
                extraSteps -= 1
            else:
                currentTick = tickRate

            currentTime += int(currentTick)
            
            # Do modules
            for currentShip in [self.ship1, self.ship2]:
                if currentShip.hasCloaks():
                    if not currentShip.cloaking:
                        if random.randint(1, bbConfig.duelCloakChance) == 1:
                            usedCloak = random.choice(currentShip.cloaks)
                            currentShip.remainingCloak = usedCloak.duration
                            currentShip.cloaking = True
                            self.battleLog.append(str("{PILOT" + ("1" if currentShip == self.ship1 else "2") + "NAME} used their " + usedCloak.name + "!"))
                    else:
                        currentShip.remainingCloak -= currentTick
                        if currentShip.remainingCloak <= 0:
                            self.battleLog.append(str("{PILOT" + ("1" if currentShip == self.ship1 else "2") + "NAME}'s cloak ran out!"))
                            currentShip.cloaking = False

            # Do DPS
            if not self.ship1.cloaking and not self.ship2.cloaking:
                ship1DamageThisTick = random.randint(int(ship1DPS - ship1DPSVariance), int(ship1DPS + ship1DPSVariance)) * currentTick
                ship2DamageThisTick = random.randint(int(ship2DPS - ship2DPSVariance), int(ship2DPS + ship2DPSVariance)) * currentTick

                """
                for i in [0, 1]:
                    currentShip = [(self.ship1, "1", ship1DamageThisTick), (self.ship2, "2", ship2DamageThisTick)][i]
                    otherShip = [(self.ship1, "1", ship1DamageThisTick), (self.ship2, "2", ship2DamageThisTick)][1-i]

                    damageLeft = currentShip[2]

                    for healthType in [(otherShip[0].hasShield(), otherShip[0].shield, "shield"),
                                        (otherShip[0].hasArmour(), otherShip[0].armour, "armour"),
                                        (otherShip[0].hasHull(), otherShip[0].hull, "hull")]:
                        if healthType[0]:
                            if damageLeft < healthType[1]:
                                healthType[1] -= damageLeft
                            else:
                                damageLeft -= healthType[1]
                                healthType[1] = 0
                            if healthType[1] > 0:
                                self.battleLog.append(str("{PILOT" + currentShip[1] + "NAME} dealt " + str(damageLeft) + " damage to {PILOT" + otherShip[1] + "NAME}'s " + healthType[2] + "!"
                                break
                            else:
                                self.battleLog.append(str("{PILOT" + currentShip[1] + "NAME} broke {PILOT" + otherShip[1] + "NAME}'s " + healthType[2] + "!"
                """


                damageLeft = ship1DamageThisTick

                if self.ship2.hasShield():
                    if self.ship2.shield > damageLeft:
                        self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT1NAME}* dealt **" + str(damageLeft) + " damage** to *{PILOT1NAME}'s* shield!"))
                        self.ship2.shield -= damageLeft
                        damageLeft = 0
                    else:
                        self.ship2.shield -= damageLeft
                        damageLeft -= self.ship2.shield
                        self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT1NAME}* broke *{PILOT1NAME}'s* shield!"))
                if damageLeft > 0:
                    if self.ship2.hasArmour():
                        if self.ship2.armour > damageLeft:
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT1NAME}* dealt **" + str(damageLeft) + " damage** to *{PILOT1NAME}'s* armour!"))
                            self.ship2.armour -= damageLeft
                            damageLeft = 0
                        else:
                            self.ship2.armour -= damageLeft
                            damageLeft -= self.ship2.armour
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT1NAME}* broke *{PILOT1NAME}'s* armour!"))
                    
                    if damageLeft > 0:
                        if self.ship2.hull > damageLeft:
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT1NAME}* dealt **" + str(damageLeft) + " damage** to *{PILOT1NAME}'s* hull!"))
                            self.ship2.hull -= damageLeft
                            damageLeft = 0
                        else:
                            self.ship2.hull -= damageLeft
                            damageLeft -= self.ship2.hull
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT1NAME}* destroyed *{PILOT1NAME}'s* hull!"))

                
                damageLeft = ship2DamageThisTick

                if self.ship1.hasShield():
                    if self.ship1.shield > damageLeft:
                        self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT2NAME}* dealt **" + str(damageLeft) + " damage** to *{PILOT1NAME}'s* shield!"))
                        self.ship1.shield -= damageLeft
                        damageLeft = 0
                    else:
                        self.ship1.shield -= damageLeft
                        damageLeft -= self.ship1.shield
                        self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT2NAME}* broke *{PILOT1NAME}'s* shield!"))
                if damageLeft > 0:
                    if self.ship1.hasArmour():
                        if self.ship1.armour > damageLeft:
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT2NAME}* dealt **" + str(damageLeft) + " damage** to *{PILOT1NAME}'s* armour!"))
                            self.ship1.armour -= damageLeft
                            damageLeft = 0
                        else:
                            self.ship1.armour -= damageLeft
                            damageLeft -= self.ship1.armour
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT2NAME}* broke *{PILOT1NAME}'s* armour!"))
                    
                    if damageLeft > 0:
                        if self.ship1.hull > damageLeft:
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT2NAME}* dealt **" + str(damageLeft) + " damage** to *{PILOT1NAME}'s* hull!"))
                            self.ship1.hull -= damageLeft
                            damageLeft = 0
                        else:
                            self.ship1.hull -= damageLeft
                            damageLeft -= self.ship1.hull
                            self.battleLog.append(str("`[" + str(currentTime) + "s]` *{PILOT2NAME}* destroyed *{PILOT1NAME}'s* hull!"))
            
            self.battleState.append((BattleShipState(self.ship1), BattleShipState(self.ship2)))

        winningShip = self.ship2 if self.ship1.hasHull() else (self.ship1 if self.ship1.hasHull() else None)
        # if self.ship1.hasHull():
        #     return self.ship2
        # elif self.ship2.hasHull():
        #     return self.ship1
        # else:
        #     return None

        return {"winningShip": None if winningShip is None else winningShip.bbShip, "battleLog":self.battleLog}


        """

        # while self.ship1.hasHull() and self.ship2.hasHull():

        

        # Fetch ship total healths
        ship1HP = ship1.getArmour() + ship1.getShield()
        ship2HP = ship2.getArmour() + ship2.getShield()

        # Vary healths by +=variancePercent
        ship1HPVariance = ship1HP * variancePercent
        ship2HPVariance = ship2HP * variancePercent
        ship1HPVaried = random.randint(int(ship1HP - ship1HPVariance), int(ship1HP + ship1HPVariance))
        ship2HPVaried = random.randint(int(ship2HP - ship2HPVariance), int(ship2HP + ship2HPVariance))

        

        # Handling to be implemented
        # ship1Handling = ship1.getHandling()
        # ship2Handling = ship2.getHandling()
        # ship1HandlingPenalty = 

        # Calculate ship TTKs
        ship1TTK = ship1HPVaried / ship2DPSVaried
        ship2TTK = ship2HPVaried / ship1DPSVaried

        # Return the ship with the longest TTK as the winner
        if ship1TTK > ship2TTK:
            winningShip = ship1
        elif ship2TTK > ship1TTK:
            winningShip = ship2
        else:
            winningShip = None
        
        return {"winningShip":winningShip,
                "ship1":{"health":{"stock":ship1HP, "varied":ship1HPVaried},
                        "DPS":{"stock":ship1DPS, "varied:":ship1DPSVaried}},
                "ship2":{"health":{"stock":ship2HP, "varied":ship2HPVaried},
                        "DPS":{"stock":ship2DPS, "varied:":ship2DPSVaried}}}"""