# TODO: Look into third party library
# TODO: Add failed route lookups to bbLogger (might already be done in bountybot.py)
from ..bbObjects.bounties import bbSystem
import math

class AStarNode(bbSystem.System):
    """A node for use in a* pathfinding.
    TODO: Does this really need to extend bbSystem?

    :var syst: this node's associated bbSystem object.
    :vartype syst: bbSystem
    :var parent: The previous AStarNode in the generated path
    :vartype parent: AStarNode
    :var g: The total distance travelled to get to this node
    :vartype g: int
    :var h: The estimated distance from this node to the nearest goal
    :vartype h: int
    :var f: The node's estimated "value" when picking the next node in the route, equal to g + h
    :vartype f: int
    """
    
    def __init__(self, syst : bbSystem.System, parent : AStarNode, g=0, h=0, f=0):
        """
        :param bbSystem syst: this node's associated bbSystem object.
        :param AStarNode parent: The previous AStarNode in the generated path
        :param int g: The total distance travelled to get to this node (Default 0)
        :param int h: The estimated distance from this node to the nearest goal (Default 0)
        :param int f: The node's estimated "value" when picking the next node in the route, equal to g + h (Default g + h)
        """
        self.syst = syst
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h


def heuristic(start : bbSystem.System, end : bbSystem.System) -> float:
    """Estimate the distance between two bbSystems, using straight line (pythagorean) distance.

    :param bbSystem start: The system to start calculating distance from
    :param bbSystem end: The system to find distance to
    :return: The straight-line distance from start to end
    """
    return math.sqrt((end.coordinates[1] - start.coordinates[1]) ** 2 +
                    (end.coordinates[0] - start.coordinates[0]) ** 2)


def bbAStar(start : bbSystem.System, end : bbSystem.System, graph : Dict[str, bbSystem.System]) -> List[str]:
    """Find the shortest path from the given start bbSystem to the end bbSystem, using the given graph for edges.
    If no route can be found, the string "! " + start + " -> " + end is returned.
    If the max route length (50) is reached, "#" is returned.

    :param bbSystem start: The starting system for route generation
    :param bbSystem end: The goal system where route generation terminates
    :param dict[str, bbSystem] graph: A dictionary mapping system names to bbSystem objects
    :return: A list containing string system names representing the shortest route from start (the first element) to end (the last element)
    :rtype: list
    """

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


def makeRoute(start : str, end : str) -> List[str]:
    """Find the shortest route between two systems.

    :param str start: string name of the starting system. Must exist in bbData.builtInSystemObjs
    :param str end: string name of the target system. Must exist in bbData.builtInSystemObjs
    :return: list of string system names where the first element is start, the last element is end, and all intermediary systems are adjacent
    :rtype: list[str]
    """
    return lib.pathfinding.bbAStar(start, end, bbData.builtInSystemObjs)