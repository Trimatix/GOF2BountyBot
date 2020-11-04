from __future__ import annotations
from emoji import UNICODE_EMOJI
from .. import bbGlobals
from . import stringTyping

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
    :var EMPTY: static class variable representing an empty emoji
    :vartype EMPTY: dumbEmoji
    """
    EMPTY = None

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
        return type(other) == dumbEmoji and self.isID == other.isID and (self.id == other.id or self.unicode == other.unicode)

    
    def __str__(self) -> str:
        """Get the object's 'sendable' string.
        
        :return: A string sendable to discord that will be translated into an emoji by the discord client.
        :rtype: str
        """
        return self.sendable


# 'static' object representing an empty/lack of emoji
dumbEmoji.EMPTY = dumbEmoji(unicode=" ")
dumbEmoji.EMPTY.isUnicode = False
dumbEmoji.EMPTY.unicode = ""
dumbEmoji.EMPTY.sendable = ""


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
        return stringTyping.isInt(s[second+1:-1])
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
    elif stringTyping.isInt(s):
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