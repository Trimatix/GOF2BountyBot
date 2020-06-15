from .bbObjects import bbSystem

import json
import math
import random


def readJSON(dbFile):
    f = open(dbFile, "r")
    txt = f.read()
    f.close()
    return json.loads(txt)


def writeJSON(dbFile, db):
    txt = json.dumps(db)
    f = open(dbFile, "w")
    txt = f.write(txt)
    f.close()


class AStarNode(bbSystem.System):
    syst = None
    parent = None
    g = 0
    h = 0
    f = 0
    
    def __init__(self, syst, parent, g=0, h=0, f=0):
        self.syst = syst
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h


def heuristic(start, end):
    return math.sqrt((end.coordinates[1] - start.coordinates[1]) ** 2 +
                    (end.coordinates[0] - start.coordinates[0]) ** 2)


def bbAStar(start, end, graph):
    if start == end:
        return [start]
    open = [AStarNode(graph[start], None, h=heuristic(graph[start], graph[end]))]
    closed = []
    count = 0

    while open:
        q = open.pop(0)

        count += 1
        if count == 50:
            return "#"
        for succName in q.syst.getNeighbours():
            if succName == end:
                closed.append(AStarNode(graph[succName], q))
                route = []
                node = closed[-1]
                while node:
                    route.append(node.syst.name)
                    node = node.parent
                return route[::-1]

            succ = AStarNode(graph[succName], q)
            succ.g = q.g + 1
            succ.h = heuristic(succ.syst, graph[end])
            succ.f = succ.g + succ.h

            betterFound = False
            for existingNode in open + closed:
                if existingNode.syst.coordinates == succ.syst.coordinates and existingNode.f <= succ.f:
                    betterFound = True
            if betterFound:
                continue

            insertPos = len(open)
            for i in range(len(open)):
                if open[i].f > succ.f:
                    if i != 0:
                        insertPos = i -1
                    break
            open.insert(insertPos, succ)

        closed.append(q)

    return "! " + start + " -> " + end


def isInt(x):
    try:
        int(x)
    except TypeError:
        return False
    except ValueError:
        return False
    return True


def isMention(mention):
    return mention.endswith(">") and ((mention.startswith("<@") and isInt(mention[2:-1])) or (mention.startswith("<@!") and isInt(mention[3:-1])))


def isRoleMention(mention):
    return mention.endswith(">") and mention.startswith("<@&") and isInt(mention[3:-1])


def fightShips(ship1, ship2, variancePercent):
    # Fetch ship total healths
    ship1HP = ship1.getArmour() + ship1.getShield()
    ship2HP = ship2.getArmour() + ship2.getShield()

    # Vary healths by +=variancePercent
    ship1HPVariance = ship1HP * variancePercent
    ship2HPVariance = ship2HP * variancePercent
    ship1HPVaried = random.randint(ship1HP - ship1HPVariance, ship1HP + ship1HPVariance)
    ship2HPVaried = random.randint(ship2HP - ship2HPVariance, ship2HP + ship2HPVariance)

    # Fetch ship total DPSs
    ship1DPS = ship1.getDPS()
    ship2DPS = ship2.getDPS()

    # Vary DPSs by +=variancePercent
    ship1DPSVariance = ship1DPS * variancePercent
    ship2DPSVariance = ship2DPS * variancePercent
    ship1DPSVaried = random.randint(ship1DPS - ship1DPSVariance, ship1DPS + ship1DPSVariance)
    ship2DPSVaried = random.randint(ship2DPS - ship2DPSVariance, ship2DPS + ship2DPSVariance)

    # Handling to be implemented
    # ship1Handling = ship1.getHandling()
    # ship2Handling = ship2.getHandling()
    # ship1HandlingPenalty = 

    # Calculate ship TTKs
    ship1TTK = ship1HPVaried / ship2DPSVaried
    ship2TTK = ship2HPVaried / ship1DPSVaried

    # Return the ship with the longest TTK as the winner
    if ship1TTK > ship2TTK:
        return ship1
    elif ship2TTK > ship1TTK:
        return ship2
    else:
        return None
