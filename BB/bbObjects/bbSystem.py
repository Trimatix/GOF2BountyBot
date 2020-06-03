from ..bbObjects import bbSystem
from .. import bbUtil
import math

class System (bbUtil.Aliasable):
    name = ""
    faction = ""
    neighbours = []
    security = -1
    coordinates = ()
    wiki = ""
    hasWiki = False

    def __init__(self, name, faction, neighbours, security, coordinates, aliases=[], wiki=""):
        super(System, self).__init__(name, aliases)
        self.name = name
        self.faction = faction
        self.neighbours = neighbours
        self.security = security
        self.coordinates = coordinates
        self.wiki = wiki
        self.hasWiki = wiki != ""

    def getNeighbours(self):
        return self.neighbours

    def distanceTo(self, other):
        return math.sqrt((other.coordinates[1] - self.coordinates[1]) ** 2 +
                    (other.coordinates[0] - self.coordinates[0]) ** 2)

    def hasJumpGate(self):
        return bool(self.neighbours)

    def getType(self):
        return System


def fromDict(sysDict):
    return bbSystem.bbSystem(sysDict["name"], sysDict["faction"], sysDict["neighbours"], sysDict["security"], sysDict["coordinates"],
                                aliases=sysDict["aliases"] if "aliases" in sysDict else [], wiki=sysDict["wiki"] if "wiki" in sysDict else "")
