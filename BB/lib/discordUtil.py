from typing import Union, List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from discord import Member, Guild, User
    from .bbObjects import bbUser

from ..logging import bbLogger
from . import stringTyping
from .. import bbGlobals
from discord import Embed


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
        if stringTyping.isInt(uRef):
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
    elif stringTyping.isInt(uRef):
        userAttempt = dcGuild.get_member(int(uRef))
        # handle the case where uRef may be the username (without discrim) of a user whose name consists only of digits.
        if userAttempt is not None:
            return userAttempt
    # Handle user names and user name+discrim combinations
    return dcGuild.get_member_named(uRef)


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


def makeEmbed(titleTxt="", desc="", col=discord.Colour.blue(), footerTxt="", img="", thumb="", authorName="", icon="") -> discord.Embed:
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