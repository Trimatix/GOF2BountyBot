from .bbObjects.bounties import bbSystem

import json
import math
import random
import inspect
from emoji import UNICODE_EMOJI
from . import bbGlobals
from .logging import bbLogger

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
    ship1HPVaried = random.randint(int(ship1HP - ship1HPVariance), int(ship1HP + ship1HPVariance))
    ship2HPVaried = random.randint(int(ship2HP - ship2HPVariance), int(ship2HP + ship2HPVariance))

    # Fetch ship total DPSs
    ship1DPS = ship1.getDPS()
    ship2DPS = ship2.getDPS()

    if ship1DPS == 0:
        if ship2DPS == 0:
            return {"winningShip": None,
            "ship1":{"health":{"stock":ship1HP, "varied":ship1HP},
                    "DPS": {"stock":ship1DPS, "varied":ship1DPS},
                    "TTK": -1},
            "ship2":{"health":{"stock":ship2HP, "varied":ship2HP},
                    "DPS": {"stock":ship2DPS, "varied":ship2DPS},
                    "TTK": -1}}
        return {"winningShip": ship2,
            "ship1":{"health":{"stock":ship1HP, "varied":ship1HP},
                    "DPS": {"stock":ship1DPS, "varied":ship1DPS},
                    "TTK": round(ship1HP / ship2DPS, 2)},
            "ship2":{"health":{"stock":ship2HP, "varied":ship2HP},
                    "DPS": {"stock":ship2DPS, "varied":ship2DPS},
                    "TTK": -1}}
    if ship2DPS == 0:
        if ship1DPS == 0:
            return {"winningShip": None,
            "ship1":{"health":{"stock":ship1HP, "varied":ship1HP},
                    "DPS": {"stock":ship1DPS, "varied":ship1DPS},
                    "TTK": -1},
            "ship2":{"health":{"stock":ship2HP, "varied":ship2HP},
                    "DPS": {"stock":ship2DPS, "varied":ship2DPS},
                    "TTK": -1}}
        return {"winningShip": ship1,
            "ship1":{"health":{"stock":ship1HP, "varied":ship1HP},
                    "DPS": {"stock":ship1DPS, "varied":ship1DPS},
                    "TTK": -1},
            "ship2":{"health":{"stock":ship2HP, "varied":ship2HP},
                    "DPS": {"stock":ship2DPS, "varied":ship2DPS},
                    "TTK": round(ship2HP / ship1DPS, 2)}}

    # Vary DPSs by +=variancePercent
    ship1DPSVariance = ship1DPS * variancePercent
    ship2DPSVariance = ship2DPS * variancePercent
    ship1DPSVaried = random.randint(int(ship1DPS - ship1DPSVariance), int(ship1DPS + ship1DPSVariance))
    ship2DPSVaried = random.randint(int(ship2DPS - ship2DPSVariance), int(ship2DPS + ship2DPSVariance))

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
                    "DPS": {"stock":ship1DPS, "varied":ship1DPSVaried},
                    "TTK": ship1TTK},
            "ship2":{"health":{"stock":ship2HP, "varied":ship2HPVaried},
                    "DPS": {"stock":ship2DPS, "varied":ship2DPSVaried},
                    "TTK": ship2TTK}}


"""
Insert commas into every third position in a string.

@param num -- string to insert commas into. probably just containing digits
@return outStr -- num, but split with commas at every third digit
"""
def commaSplitNum(num):
    outStr = num
    for i in range(len(num), 0, -3):
        outStr = outStr[0:i] + "," + outStr[i:]
    return outStr[:-1]

"""
class funcRef:
    def __init__(self, func):
        self.func = func
        self.isCoroutine = inspect.iscoroutinefunction(func)
        self.params = inspect.signature(addFunc).parameters


    async def call(self, args):
        if self.isCoroutine:
            await self.func(args)
        else:
            self.func(args)


class funcArgs:
    def __init__(self, args{}):
"""


class dumbEmoji:
    def __init__(self, id=-1, unicode=""):
        if id == -1 and unicode == "":
            raise ValueError("At least one of id or unicode is required")
        elif id != -1 and unicode != "":
            raise ValueError("Can only accept one of id or unicode, not both")
        
        self.id = id
        self.unicode = unicode
        self.isID = id != -1
        self.isUnicode = not self.isID
        self.sendable = self.unicode if self.isUnicode else str(bbGlobals.client.get_emoji(self.id))
        # if self.sendable is None:
        #     self.sendable = '❓'

    
    def toDict(self):
        if self.isUnicode:
            return {"unicode":self.unicode}
        else:
            return {"id":self.id}


    def __repr__(self):
        return "<dumbEmoji-" + ("id" if self.isID else "unicode") + ":" + (str(self.id) if self.isID else self.unicode) + ">"

    
    def __hash__(self):
        return hash(repr(self))

    
    def __eq__(self, other):
        return type(other) == dumbEmoji and self.isID == other.isID and (self.id == other.id or self.unicode == other.unicode)

    
    def __str__(self):
        return self.sendable


EMPTY_DUMBEMOJI = dumbEmoji(unicode=" ")
EMPTY_DUMBEMOJI.isUnicode = False
EMPTY_DUMBEMOJI.unicode = ""
EMPTY_DUMBEMOJI.sendable = ""


def dumbEmojiFromDict(emojiDict):
    if type(emojiDict) == dumbEmoji:
        return emojiDict
    if "id" in emojiDict:
        return dumbEmoji(id=emojiDict["id"])
    else:
        return dumbEmoji(unicode=emojiDict["unicode"])


def isUnicodeEmoji(c):
    if len(c) != 1:
        return False
    return c in UNICODE_EMOJI


def isCustomEmoji(s):
    if s.startswith("<") and s.endswith(">"):
        try:
            first = s.index(":")
            second = first + s[first+1:].index(":") + 1
        except ValueError:
            return False
        return isInt(s[second+1:-1])
    return False


def dumbEmojiFromStr(s):
    if type(s) == dumbEmoji:
        return s
    if type(s) == dict:
        return dumbEmojiFromDict(s)
    if isUnicodeEmoji(s):
        return dumbEmoji(unicode=s)
    elif isCustomEmoji(s):
        return dumbEmoji(id=int(s[s[s.index(":")+1:].index(":")+3:-1]))
    elif isInt(s):
        return dumbEmoji(id=int(s))
    else:
        return None


def dumbEmojiFromPartial(e):
    if type(e) == dumbEmoji:
        return emojiDict
    if e.is_unicode_emoji():
        return dumbEmoji(unicode=e.name)
    else:
        return dumbEmoji(id=e.id)


def td_format_noYM(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


def findBBUserDCGuild(user):
    if user.hasLastSeenGuildId:
        lastSeenGuild = bbGlobals.client.get_guild(user.lastSeenGuildId)
        if lastSeenGuild is None or lastSeenGuild.get_member(user.id) is None:
            user.hasLastSeenGuildId = False
        else:
            return lastSeenGuild

    if not user.hasLastSeenGuildId:
        for guild in bbGlobals.guildsDB.guilds.values():
            lastSeenGuild = bbGlobals.client.get_guild(guild.id)
            if lastSeenGuild is not None and lastSeenGuild.get_member(user.id) is not None:
                user.lastSeenGuildId = guild.id
                user.hasLastSeenGuildId = True
                return lastSeenGuild
    return None


def userOrMemberName(dcUser, dcGuild):
    if dcUser is None:
        bbLogger.log("Main", "usrMmbrNme",
                     "Null dcUser given", eventType="USR_NONE")
        raise ValueError("Null dcUser given")

    if dcGuild is None:
        return dcUser.name

    guildMember = dcGuild.get_member(dcUser.id)
    if guildMember is None:
        return dcUser.name
    return guildMember.display_name