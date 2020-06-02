import json
import math
from abc import ABC, abstractmethod

class Aliasable (ABC):
    name = ""
    aliases = []

    def __init__(self, name, aliases, forceAllowEmpty=False):
        if not name and not forceAllowEmpty:
            raise RuntimeError("ALIAS_CONS_NONAM: Attempted to create an aliasable with an empty name")
        self.name = name
        for alias in range(len(aliases)):
            if not aliases[alias] and not forceAllowEmpty:
                raise RuntimeError("ALIAS_CONS_EMPTALIAS: Attempted to create an aliasable with an empty alias")
            aliases[alias] = aliases[alias].lower()
        self.aliases = aliases
        if name.lower() not in aliases:
            self.aliases += [name.lower()]
    
    def __eq__(self, other):
        return type(other) == self.getType() and self.isCalled(other.name) or other.isCalled(self.name)

    def isCalled(self, name):
        return name.lower() == self.name.lower() or name.lower() in self.aliases

    @abstractmethod
    def getType(self):
        pass


def readJDB(dbFile):
    f = open(dbFile, "r")
    txt = f.read()
    f.close()
    return json.loads(txt)


def writeJDB(dbFile, db):
    txt = json.dumps(db)
    f = open(dbFile, "w")
    txt = f.write(txt)
    f.close()


class AStarNode(System):
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