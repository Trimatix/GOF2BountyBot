# Typing imports
from __future__ import annotations
from typing import Union, List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from .bbObjects.items import bbShip
    from discord import PartialEmoji, Guild, User
    from .bbObjects import bbUser
    from .bbObjects.bounties import bbCriminal

from .bbObjects.bounties import bbSystem

from datetime import timedelta
import json
import math
import random
import inspect
from emoji import UNICODE_EMOJI
from . import bbGlobals
from .logging import bbLogger

from discord import Embed


def readJSON(dbFile : str) -> dict:
    """Read the json file with the given path, and return the contents as a dictionary.
    
    :param str dbFile: Path to the file to read
    :return: The contents of the requested json file, parsed into a python dictionary
    :rtype: dict 
    """
    f = open(dbFile, "r")
    txt = f.read()
    f.close()
    return json.loads(txt)


def writeJSON(dbFile : str, db : dict):
    """Write the given json-serializable dictionary to the given file path. All objects in the dictionary must be JSON-serializable.
    TODO: Check this makes the file if it doesnt exist

    :param str dbFile: Path to the file which db should be written to
    :param dict db: The json-serializable dictionary to write
    """
    txt = json.dumps(db)
    f = open(dbFile, "w")
    txt = f.write(txt)
    f.close()


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


def isInt(x) -> bool:
    """Decide whether or not something is either an integer, or is castable to integer.

    :param x: The object to type-check
    :return: True if x is an integer or if x can be casted to integer. False otherwise
    :rtype: bool
    """

    try:
        int(x)
    except TypeError:
        return False
    except ValueError:
        return False
    return True


def isMention(mention : str) -> bool:
    """Decide whether the given string is a discord user mention, being either <@USERID> or <@!USERID> where USERID is an integer discord user id.

    :param str mention: The string to check
    :return: True if mention matches the formatting of a discord user mention, False otherwise
    :rtype: bool
    """
    return mention.endswith(">") and ((mention.startswith("<@") and isInt(mention[2:-1])) or (mention.startswith("<@!") and isInt(mention[3:-1])))


def isRoleMention(mention : str) -> bool:
    """Decide whether the given string is a discord role mention, being <@&ROLEID> where ROLEID is an integer discord role id.

    :param str mention: The string to check
    :return: True if mention matches the formatting of a discord role mention, False otherwise
    :rtype: bool
    """
    return mention.endswith(">") and mention.startswith("<@&") and isInt(mention[3:-1])


def fightShips(ship1 : bbShip.bbShip, ship2 : bbShip.bbShip, variancePercent : float) -> dict:
    """Simulate a duel between two ships.
    Returns a dictionary containing statistics about the duel, as well as a reference to the winning ship. 

    :param bbShip ship1: One of the ships partaking in the duel 
    :param bbShip ship2: One of the ships partaking in the duel
    :param float variancePercent: The amount of random variance to apply to ship statistics, as a float percentage (e.g 0.5 for 50% random variance lll)
    :return: A dictionary containing statistics about the duel, as well as a reference to the winning ship.
    :rtype: dict
    """

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


def commaSplitNum(num : str) -> str:
    """Insert commas into every third position in a string.
    For example: "3" -> "3", "30000" -> "30,000", and "561928301" -> "561,928,301"

    :param str num: string to insert commas into. probably just containing digits
    :return: num, but split with commas at every third digit
    :rtype: str
    """
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
    """A class that really shouldnt be necessary, acting as a union over the str (unicode) and Emoji type emojis used and returned by discord.
    To instance this class, provide exactly one of the constructor's keyword arguments.

    :var id: The ID of the Emoji that this object represents, if isID
    :vartype id: int
    :var unicode: The string unicode emoji that this object represents, if isUnicode
    :vartype unicode: 
    :var isID: True if this object represents a custom emoji, False if it represents a unicode emoji.
    :vartype isID: bool
    :var isUnicode: False if this object represents a custom emoji, True if it represents a unicode emoji.
    :vartype isUnicode: bool
    :var sendable: A string sendable in a discord message that discord will render an emoji over.
    :vartype sendable: str
    """

    def __init__(self, id=-1, unicode=""):
        """
        :param int id: The ID of the custom emoji that this object should represent.
        :param str unicode: The unicode emoji that this object should represent.
        """

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

    
    def toDict(self) -> dict:
        """Serialize this emoji to dictionary format for saving to file.

        :return: A dictionary containing all information needed to reconstruct this emoji.
        :rtype: dict
        """
        if self.isUnicode:
            return {"unicode":self.unicode}
        else:
            return {"id":self.id}


    def __repr__(self) -> str:
        """Get a string uniquely identifying this object, specifying what type of emoji it represents and the emoji itself.

        :return: A string identifying this object.
        :rtype: str
        """
        return "<dumbEmoji-" + ("id" if self.isID else "unicode") + ":" + (str(self.id) if self.isID else self.unicode) + ">"

    
    def __hash__(self) -> int:
        """Calculate a hash of this emoji, based on its repr string. Two dumbEmoji objects representing the same emoji will have the same repr and hash.

        :return: A hash of this emoji
        :rtype: int
        """
        return hash(repr(self))

    
    def __eq__(self, other : dumbEmoji) -> bool:
        """Decide if this dumbEmoji is equal to another.
        Two dumbEmojis are equal if they represent the same emoji (i.e ID/unicode) of the same type (custom/unicode)
        
        :param dumbEmoji other: the emoji to compare this one to
        :return: True of this emoji is semantically equal to the given emoji, False otherwise
        :rtype: bool
        """
        return type(other) == dumbEmoji and ((self.isID and other.isID and self.id == other.id) or (self.isUnicode and other.isUnicode and self.unicode == other.unicode))

    
    def __str__(self) -> str:
        """Get the object's 'sendable' string.
        
        :return: A string sendable to discord that will be translated into an emoji by the discord client.
        :rtype: str
        """
        return self.sendable


# 'static' object representing an empty/lack of emoji
EMPTY_DUMBEMOJI = dumbEmoji(unicode=" ")
EMPTY_DUMBEMOJI.isUnicode = False
EMPTY_DUMBEMOJI.unicode = ""
EMPTY_DUMBEMOJI.sendable = ""


def dumbEmojiFromDict(emojiDict : dict) -> dumbEmoji:
    """Construct a dumbEmoji object from its dictionary representation.
    If both an ID and a unicode representation are provided, the emoji ID will be used.

    TODO: If ID is -1, use unicode. If unicode is "", use ID.

    :param dict emojiDict: A dictionary containing either an ID (for custom emojis) or a unicode emoji string (for unicode emojis)
    :return: A new dumbEmoji object as described in emojiDict
    :rtype: dumbEmoji
    """
    if type(emojiDict) == dumbEmoji:
        return emojiDict
    if "id" in emojiDict:
        return dumbEmoji(id=emojiDict["id"])
    else:
        return dumbEmoji(unicode=emojiDict["unicode"])


def isUnicodeEmoji(c : str) -> bool:
    """Decide whether a given string contrains a single unicode emoji.

    :param str c: The string to test
    :return: True if c contains exactly one character, and that character is a unicode emoji. False otherwise.
    :rtype: bool
    """
    return c in UNICODE_EMOJI


def isCustomEmoji(s : str) -> bool:
    """Decide whether the given string matches the formatting of a discord custom emoji,
    being <:NAME:ID> where NAME is the name of the emoji, and ID is the integer ID.

    :param str c: The string to test
    :return: True if s 'looks like' a discord custom emoji, matching their structure. False otherwise.
    :rtype: bool
    """
    if s.startswith("<") and s.endswith(">"):
        try:
            first = s.index(":")
            second = first + s[first+1:].index(":") + 1
        except ValueError:
            return False
        return isInt(s[second+1:-1])
    return False


def dumbEmojiFromStr(s : str) -> dumbEmoji:
    """Construct a dumbEmoji object from a string containing either a unicode emoji or a discord custom emoji.
    s may also be a dumbEmoji (returns s), a dictionary-serialized dumbEmoji (returns dumbEmojiFromDict(s)), or
    only an ID of a discord custom emoji (may be either str or int)

    :param str s: A string containing only one of: A unicode emoji, a discord custom emoji, or the ID of a discord custom emoji.
    :return: A dumbEmoji representing the given string emoji
    :rtype: dumbEmoji
    """
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


def dumbEmojiFromPartial(e : PartialEmoji) -> dumbEmoji:
    """Construct a new dumbEmoji object from a given discord.PartialEmoji.

    :return: A dumbEmoji representing e
    :rtype: dumbEmoji
    """
    if type(e) == dumbEmoji:
        return e
    if e.is_unicode_emoji():
        return dumbEmoji(unicode=e.name)
    else:
        return dumbEmoji(id=e.id)


def timeDeltaFromDict(timeDict : dict) -> timedelta:
    """Construct a datetime.timedelta from a dictionary,
    transforming keys into keyword arguments for the timedelta constructor.

    :param dict timeDict: dictionary containing measurements for each time interval. i.e weeks, days, hours, minutes, seconds, microseconds and milliseconds. all are optional and case sensitive.
    :return: a timedelta with all of the attributes requested in the dictionary.
    :rtype: datetime.timedelta
    """
    return timedelta(weeks=timeDict["weeks"] if "weeks" in timeDict else 0,
                     days=timeDict["days"] if "days" in timeDict else 0,
                     hours=timeDict["hours"] if "hours" in timeDict else 0,
                     minutes=timeDict["minutes"] if "minutes" in timeDict else 0,
                     seconds=timeDict["seconds"] if "seconds" in timeDict else 0,
                     microseconds=timeDict["microseconds"] if "microseconds" in timeDict else 0,
                     milliseconds=timeDict["milliseconds"] if "milliseconds" in timeDict else 0)


def td_format_noYM(td_object : timedelta) -> str:
    """Create a string describing the attributes of a given datetime.timedelta object, in a
    human reader-friendly format.
    This function does not create 'week', 'month' or 'year' strings, its highest time denominator is 'day'.
    Any time denominations that are equal to zero will not be present in the string.

    :param datetime.timedelta td_object: The timedelta to describe
    :return: A string describing td_object's attributes in a human-readable format
    :rtype: str
    """
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


def findBBUserDCGuild(user : bbUser.bbUser) -> Union[Guild, None]:
    """Attempt to find a discord.guild containing the given bbUser.
    If a guild is found, it will be returned as a discord.guild. If no guild can be found, None will be returned.

    :param bbUser user: The user to attempt to locate
    :return: A discord.Guild where user is a member, if one can be found. None if no such guild can be found.
    :rtype: discord.guild or None
    """
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


def userOrMemberName(dcUser : User, dcGuild : Guild) -> str:
    """If dcUser is a member of dcGuild, return dcUser's display name in dcGuild (their nickname if they have one, or their user name otherwise),
    Otherwise, retur dcUser's discord user name.

    :param discord.User dcUser: The user whose name to get
    :return: dcUser's display name in dcGuild if dcUser is a member of dcGuild, dcUser.name otherwise
    :rtype: str
    :raise ValueError: When given a None dcUser
    """
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


# Use of this method is discouraged. It would be just as efficient to check that getMemberFromRef is not None, and that would require only one function call!
def isUserRef(uRef : str, dcGuild=None) -> bool:
    """Decide whether the given string is a valid user reference, pointing to a user.
    #TODO: if uRef is a mention or ID, validate that getUser doesnt return None
    If this method is to be used before a call to getMemberFromRef, you should instead consider
    calling getMemberRef and checking whether the result is None. Both functions perform similar
    calculations, and this method of uRef validation will use one function call rather than two.

    uRef can be one of:
    - A user mention <@123456> or <@!123456>
    - A user ID 123456
    - A user name Carl
    - A user name and discriminator Carl#0324

    If uRef is not a user mention or ID, dcGuild must be provided, to be searched for the given name.
    When validating a name uRef, the process is much more efficient when also given the user's discriminator.

    :param str uRef: The string to test
    :param discord.Guild dcGuild: The guild in which to search for a user identified by uRef. Required if uRef is not a mention or ID. (Default None)
    :return: True if uRef identifies a discord.User or a discord.Member in dcGuild, False otherwise
    """
    if isMention(uRef):
        return True
    
    if dcGuild is not None:
        if isInt(uRef):
            return dcGuild.get_member(uRef) is not None
        else:
            return dcGuild.get_member_named(uRef) is not None

    return False


def getMemberFromRef(uRef : str, dcGuild : Guild) -> Union[Member, None]:
    """Attempt to find a member of a given discord guild object from a string or integer.
    uRef can be one of:
    - A user mention <@123456> or <@!123456>
    - A user ID 123456
    - A user name Carl
    - A user name and discriminator Carl#0324

    If the passed user reference is none of the above, or a matching user cannot be found in the requested guild, None is returned.

    :param str uRef: A string or integer indentifying a user within dcGuild either by mention, ID, name, or name and discriminator
    :param discord.Guild dcGuild: A discord.guild in which to search for a member matching uRef
    :return: Either discord.member of a member belonging to dcGuild and matching uRef, or None if uRef is invalid or no matching user could be found
    :rtype: discord.Member or None
    """
    # Handle user mentions
    if isMention(uRef):
        return dcGuild.get_member(int(uRef.lstrip("<@!").rstrip(">")))
    # Handle IDs
    elif isInt(uRef):
        userAttempt = dcGuild.get_member(int(uRef))
        # handle the case where uRef may be the username (without discrim) of a user whose name consists only of digits.
        if userAttempt is not None:
            return userAttempt
    # Handle user names and user name+discrim combinations
    return dcGuild.get_member_named(uRef)


def makeEmbed(titleTxt="", desc="", col=discord.Colour.blue(), footerTxt="", img="", thumb="", authorName="", icon="") -> Embed:
    """Factory function building a simple discord embed from the provided arguments.

    :param str titleTxt: The title of the embed (Default "")
    :param str desc: The description of the embed; appears at the top below the title (Default "")
    :param discord.Colour col: The colour of the side strip of the embed (Default discord.Colour.blue())
    :param str footerTxt: Secondary description appearing at the bottom of the embed (Default "")
    :param str img: Large icon appearing as the content of the embed, left aligned like a field (Default "")
    :param str thumb: larger image appearing to the right of the title (Default "")
    :param str authorName: Secondary title for the embed (Default "")
    :param str icon: smaller image to the left of authorName. AuthorName is required for this to be displayed. (Default "")
    :return: a new discord embed as described in the given parameters
    :rtype: discord.Embed
    """
    embed = Embed(title=titleTxt, description=desc, colour=col)
    if footerTxt != "":
        embed.set_footer(text=footerTxt)
    embed.set_image(url=img)
    if thumb != "":
        embed.set_thumbnail(url=thumb)
    if icon != "":
        embed.set_author(name=authorName, icon_url=icon)
    return embed


def userTagOrDiscrim(userID : str, guild=None) -> str:
    """If a passed user mention or ID is valid and shares a common server with the bot,
    return the user's name and discriminator. TODO: Should probably change this to display name
    Otherwise, return the passed userID.

    :param str userID: A user mention or ID in string form, to attempt to convert to name and discrim
    :return: The user's name and discriminator if the user is reachable, userID otherwise
    :rtype: str
    """
    if guild is None:
        userObj = bbGlobals.client.get_user(int(userID.lstrip("<@!").rstrip(">")))
    else:
        userObj = guild.get_member(int(userID.lstrip("<@!").rstrip(">")))
    if userObj is not None:
        return userObj.name + "#" + userObj.discriminator
    # Return the given mention as a fall back - might replace this with '#UNKNOWNUSER#' at some point.
    bbLogger.log("Main", "uTgOrDscrm", "Unknown user requested." + (("Guild:" + guild.name + "#" + str(str(guild.id)))
                                                                    if guild is not None else "Global/NoGuild") + ". uID:" + str(userID), eventType="UKNWN_USR")
    return userID


def criminalNameOrDiscrim(criminal : bbCriminal.bbCriminal) -> str:
    """If a passed criminal is a player, attempt to return the user's name and discriminator.
    Otherwise, return the passed criminal's name. TODO: Should probably change this to display name

    :param bbCriminal criminal: criminal whose name to attempt to convert to name and discrim
    :return: The user's name and discriminator if the criminal is a player, criminal.name otherwise
    :rtype: str
    """
    if not criminal.isPlayer:
        return criminal.name
    return userTagOrDiscrim(criminal.name)