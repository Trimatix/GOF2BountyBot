import json
import math

class System:
    name = ""
    faction = ""
    neighbours = []
    security = -1
    coordinates = ()

    def __init__(self, name, faction, neighbours, security, coordinates):
        self.name = name
        self.faction = faction
        self.neighbours = neighbours
        self.security = security
        self.coordinates = coordinates

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
    g = 0
    h = 0
    f = 0
    
    def __init__(self, syst, g=0, h=0, f=0):
        self.syst = syst



def heuristic(start, end):
    return math.sqrt((end.coordinates[0] - start.coordinates[0]) ** 2,
                    (end.coordinates[1] - start.coordinates[1]) ** 2)
