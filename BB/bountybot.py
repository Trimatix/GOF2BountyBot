# Typing imports
from __future__ import annotations
from typing import List, Dict, Union, TYPE_CHECKING

# Discord Imports

import discord
from discord.ext import commands

# Utility Imports

from datetime import datetime, timedelta
import asyncio
import random
# used for leaderboard sorting
import operator
# used for spawning items from dict in dev_cmd_give
import json
import traceback
from os import path
from aiohttp import client_exceptions

# BountyBot Imports

from .bbConfig import bbConfig, bbData, bbPRIVATE
from .bbObjects import bbUser, bbInventory
from .bbObjects.bounties import bbBounty, bbBountyConfig, bbCriminal, bbSystem
from .bbObjects.items import bbShip, bbModuleFactory, bbShipUpgrade, bbTurret, bbWeapon
from .bbObjects.battles import ShipFight, DuelRequest
from .scheduling import TimedTask
from .bbDatabases import bbBountyDB, bbGuildDB, bbUserDB, HeirarchicalCommandsDB, reactionMenuDB
from .scheduling import TimedTaskHeap
from . import lib, bbGlobals
from .userAlerts import UserAlerts
from .logging import bbLogger
from .reactionMenus import ReactionMenu, ReactionInventoryPicker, ReactionRolePicker, ReactionDuelChallengeMenu, ReactionPollMenu

if TYPE_CHECKING:
    from .bbObjects import bbGuild



####### GLOBAL VARIABLES #######

# interface into the discord servers
bbGlobals.client = commands.Bot(command_prefix=bbConfig.commandPrefix)

# BountyBot commands DB
bbCommands = HeirarchicalCommandsDB.HeirarchicalCommandsDB(bbConfig.numCommandAccessLevels)
# Commands usable in DMs
dmCommands = HeirarchicalCommandsDB.HeirarchicalCommandsDB(bbConfig.numCommandAccessLevels)

# Do not change these!
botLoggedIn = False



####### DATABASE FUNCTIONS #####



def loadUsersDB(filePath : str) -> bbUserDB.bbUserDB:
    """Build a bbUserDB from the specified JSON file.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a bbUserDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return bbUserDB.fromDict(lib.jsonHandler.readJSON(filePath))


def loadGuildsDB(filePath : str) -> bbGuildDB.bbGuildDB:
    """Build a bbGuildDB from the specified JSON file.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a bbGuildDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return bbGuildDB.fromDict(lib.jsonHandler.readJSON(filePath))


async def loadReactionMenusDB(filePath : str) -> reactionMenuDB.reactionMenuDB:
    """Build a reactionMenuDB from the specified JSON file.
    This method must be called asynchronously, to allow awaiting of discord message fetching functions.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a reactionMenuDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return await reactionMenuDB.fromDict(lib.jsonHandler.readJSON(filePath))



####### UTIL FUNCTIONS #######



async def makeBountyBoardChannelMessage(guild : bbGuild.bbGuild, bounty : bbBounty.Bounty, msg="", embed=None) -> discord.Message:
    """Create a new BountyBoardChannel listing for the given bounty, in the given guild.
    guild must own a BountyBoardChannel.

    :param bbGuild guild: The guild in which to create the BBC listing. Must own a BountyBoardChannel.
    :param bbBounty.Bounty bounty: The bounty for which to create a listing
    :param str msg: The text to display in the listing message content (Default "")
    :param discord.Embed embed: The embed to display in the listing message - this will be removed immediately in place of the embed generated during BountyBoardChannel.updateBountyMessage, so is only really useful in case updateBountyMessage fails. (Default None)
    :return: The new discord message containing the BBC listing
    :rtype: discord.Message
    :raise ValueError: If guild does not own a BountyBoardChannel
    """
    if not guild.hasBountyBoardChannel:
        raise ValueError("The requested bbGuild has no bountyBoardChannel")
    bountyListing = await guild.bountyBoardChannel.channel.send(msg, embed=embed)
    await guild.bountyBoardChannel.addBounty(bounty, bountyListing)
    await guild.bountyBoardChannel.updateBountyMessage(bounty)
    return bountyListing


async def removeBountyBoardChannelMessage(guild : bbGuild.bbGuild, bounty : bbBounty.Bounty):
    """Remove guild's BountyBoardChannel listing for bounty.

    :param bbGuild guild: The guild in which to remove bounty's BBC listing
    :param bbBounty bounty: The bounty whose BBC listing should be removed
    :raise ValueError: If guild does not own a BBC
    :raise KeyError: If the guild's BBC does not have a listing for bounty
    """
    if not guild.hasBountyBoardChannel:
        raise ValueError("The requested bbGuild has no bountyBoardChannel")
    if guild.bountyBoardChannel.hasMessageForBounty(bounty):
        try:
            await guild.bountyBoardChannel.getMessageForBounty(bounty).delete()
        except discord.HTTPException:
            bbLogger.log("Main", "rmBBCMsg", "HTTPException thrown when removing bounty listing message for criminal: " +
                         bounty.criminal.name, category='bountyBoards', eventType="RM_LISTING-HTTPERR")
        except discord.Forbidden:
            bbLogger.log("Main", "rmBBCMsg", "Forbidden exception thrown when removing bounty listing message for criminal: " +
                         bounty.criminal.name, category='bountyBoards', eventType="RM_LISTING-FORBIDDENERR")
        except discord.NotFound:
            bbLogger.log("Main", "rmBBCMsg", "Bounty listing message no longer exists, BBC entry removed: " +
                         bounty.criminal.name, category='bountyBoards', eventType="RM_LISTING-NOT_FOUND")
        await guild.bountyBoardChannel.removeBounty(bounty)
    else:
        raise KeyError("The requested bbGuild (" + str(guild.id) + ") does not have a BountyBoardChannel listing for the given bounty: " + bounty.criminal.name)


async def updateBountyBoardChannel(guild: bbGuild.bbGuild, bounty : bbBounty.Bounty, bountyComplete=False):
    """Update the BBC listing for the given bounty in the given server.

    :param bbGuild.bbGuild guild: The guild in which to update the listing
    :param bbBounty bounty: The bounty whose listings should be updated
    :param bool bountyComplete: Whether or not the bounty has now been completed. When True, bounty listings will be removed rather than updated. (Default False)
    """
    if guild.hasBountyBoardChannel:
        if bountyComplete and guild.bountyBoardChannel.hasMessageForBounty(bounty):
            await removeBountyBoardChannelMessage(guild, bounty)
        else:
            if not guild.bountyBoardChannel.hasMessageForBounty(bounty):
                await makeBountyBoardChannelMessage(guild, bounty, "A new bounty is now available from **" + \
                                                                    bounty.faction.title() + "** central command:")
            else:
                await guild.bountyBoardChannel.updateBountyMessage(bounty)


async def announceNewShopStock(guildID=-1):
    """Announce the refreshing of shop stocks to one or all joined guilds.
    Messages will be sent to the playChannels of all guilds in the bbGlobals.guildsDB, if they have one

    :param int guildID: The guild to announce to. If guildID is -1, the shop refresh will be announced to all joined guilds. (Default -1)
    """
    if guildID == -1:
        # loop over all guilds
        for guild in bbGlobals.guildsDB.guilds.values():
            # ensure guild has a valid playChannel
            if guild.hasPlayChannel() and not guild.shopDisabled:
                playCh = guild.getPlayChannel()
                if playCh is not None:
                    msg = "The shop stock has been refreshed!\n**        **Now at tech level: **" + \
                        str(guild.shop.currentTechLevel) + "**"
                    try:
                        if guild.hasUserAlertRoleID("shop_refresh"):
                            # announce to the given channel
                            await playCh.send(":arrows_counterclockwise: <@&" + str(guild.getUserAlertRoleID("shop_refresh")) + "> " + msg)
                        else:
                            await playCh.send(":arrows_counterclockwise: " + msg)
                    except discord.Forbidden:
                        bbLogger.log("Main", "anncNwShp", "Failed to post shop stock announcement to guild " + bbGlobals.client.get_guild(
                            guild.id).name + "#" + str(guild.id) + " in channel " + playCh.name + "#" + str(playCh.id), category="shop", eventType="PLCH_SND_FRBDN")
    else:
        guild = bbGlobals.guildsDB.getGuild(guildID)
        # ensure guild has a valid playChannel
        if guild.hasPlayChannel() and not guild.shopDisabled:
            playCh = guild.getPlayChannel()
            if playCh is not None:
                msg = "The shop stock has been refreshed!\n**        **Now at tech level: **" + \
                    str(guild.shop.currentTechLevel) + "**"
                try:
                    if guild.hasUserAlertRoleID("shop_refresh"):
                        # announce to the given channel
                        await playCh.send(":arrows_counterclockwise: <@&" + str(guild.getUserAlertRoleID("shop_refresh")) + "> " + msg)
                    else:
                        await playCh.send(":arrows_counterclockwise: " + msg)
                except discord.Forbidden:
                    bbLogger.log("Main", "anncNwShp", "Failed to post shop stock announcement to guild " + bbGlobals.client.get_guild(
                        guild.id).name + "#" + str(guild.id) + " in channel " + playCh.name + "#" + str(playCh.id), category="shop", eventType="PLCH_NONE")


async def refreshAndAnnounceAllShopStocks():
    """Generate new tech levels and inventories for the shops of all joined guilds,
    and announce the stock refresh to those guilds.
    """
    bbGlobals.guildsDB.refreshAllShopStocks()
    await announceNewShopStock()


def saveAllDBs():
    """Save all of the bot's savedata to file.
    This currently saves:
    - the users database
    - the bounties database
    - the guilds database
    - the reaction menus database
    """
    lib.jsonHandler.saveDB(bbConfig.userDBPath, bbGlobals.usersDB)
    lib.jsonHandler.saveDB(bbConfig.guildDBPath, bbGlobals.guildsDB)
    lib.jsonHandler.saveDB(bbConfig.reactionMenusDBPath, bbGlobals.reactionMenusDB)
    bbLogger.save()
    print(datetime.now().strftime("%H:%M:%S: Data saved!"))


async def expireAndAnnounceDuelReq(duelReqDict : DuelRequest.DuelRequest):
    """Foce the expiry of a given DuelRequest. The duel expiry will be announced to the issuing user.
    TODO: Announce duel expiry to target user, if they have the UA.

    :param DuelRequest duelReqDict: The duel request to expire
    """
    duelReq = duelReqDict["duelReq"]
    await duelReq.duelTimeoutTask.forceExpire(callExpiryFunc=False)
    if duelReq.sourceBBGuild.hasPlayChannel():
        playCh = duelReq.sourceBBGuild.getPlayChannel()
        if playCh is not None:
            await playCh.send(":stopwatch: <@" + str(duelReq.sourceBBUser.id) + ">, your duel challenge for **" + str(bbGlobals.client.get_user(duelReq.targetBBUser.id)) + "** has now expired.")
    duelReq.sourceBBUser.removeDuelChallengeObj(duelReq)


def typeAlertedUserMentionOrName(alertType : UserAlerts.UABase, dcUser=None, bbUser=None, bbGuild=None, dcGuild=None) -> str:
    """If the given user has subscribed to the given alert type, return the user's mention. Otherwise, return their display name and discriminator.
    At least one of dcUser or bbUser must be provided.
    bbGuild and dcGuild are both optional. If neither are provided then the joined guilds will be searched for the given user.
    This means that giving at least one of bbGuild or dcGuild will drastically improve efficiency.
    TODO: rename bbUser and bbGuild so it doesnt match the class name

    :param UserAlerts.UABase alertType: The type of alert to check the state of
    :param discord.User dcUser: The user to check the alert state of. One of dcUser or bbUser is required. (Default None)
    :param bbUser bbUser: The user to check the alert state of. One of dcUser or bbUser is required. (Default None)
    :param bbGuild bbGuild: The guild in which to check the alert state. Optional, but improves efficiency. (Default None)
    :param dcGuild dcGuild: The guild in which to check the alert state. Optional, but improves efficiency. (Default None)
    :return: If the given user is alerted for the given type in the selected guild, the user's mention. The user's display name and discriminator otherwise.
    :rtype: str
    :raise ValueError: When given neither dcUser nor bbUser
    :raise KeyError: When given neither bbGuild nor dcGuild, and the user could not be located in any of the bot's joined guilds.
    """
    if dcUser is None and bbUser is None:
        raise ValueError("At least one of dcUser or bbUser must be given.")

    if bbGuild is None and dcGuild is None:
        dcGuild = lib.discordUtil.findBBUserDCGuild(dcUser)
        if dcGuild is None:
            raise KeyError("user does not share an guilds with the bot")
    if bbGuild is None:
        bbGuild = bbGlobals.guildsDB.getGuild(dcGuild.id)
    elif dcGuild is None:
        dcGuild = bbGlobals.client.get_guild(bbGuild.id)
    if bbUser is None:
        bbUser = bbGlobals.usersDB.getOrAddID(dcUser.id)

    guildMember = dcGuild.get_member(dcUser.id)
    if guildMember is None:
        return dcUser.name + "#" + str(dcUser.discriminator)
    if bbUser.isAlertedForType(alertType, dcGuild, bbGuild, dcUser):
        return guildMember.mention
    return guildMember.display_name + "#" + str(guildMember.discriminator)


def IDAlertedUserMentionOrName(alertID : str, dcUser=None, bbUser=None, bbGuild=None, dcGuild=None) -> str:
    """If the given user has subscribed to the alert type of the given ID, return the user's mention. Otherwise, return their display name and discriminator.
    At least one of dcUser or bbUser must be provided.
    bbGuild and dcGuild are both optional. If neither are provided then the joined guilds will be searched for the given user.
    This means that giving at least one of bbGuild or dcGuild will drastically improve efficiency.
    TODO: rename bbUser and bbGuild so it doesnt match the class name

    :param UserAlerts.UABase alertType: The ID, according to UserAlerts.userAlertsIDsTypes, of type of alert to check the state of
    :param discord.User dcUser: The user to check the alert state of. One of dcUser or bbUser is required. (Default None)
    :param bbUser bbUser: The user to check the alert state of. One of dcUser or bbUser is required. (Default None)
    :param bbGuild bbGuild: The guild in which to check the alert state. Optional, but improves efficiency. (Default None)
    :param dcGuild dcGuild: The guild in which to check the alert state. Optional, but improves efficiency. (Default None)
    :return: If the given user is alerted for the given type in the selected guild, the user's mention. The user's display name otherwise.
    :rtype: str
    """
    return typeAlertedUserMentionOrName(UserAlerts.userAlertsIDsTypes[alertID], dcUser=dcUser, bbUser=bbUser, bbGuild=bbGuild, dcGuild=dcGuild)


def getAlertIDFromHeirarchicalAliases(alertName : Union[str, List[str]]) -> List[str]:
    """Look up a given multi-levelled alert reference, and return a list of associated UserAlert IDs.
    This function implements:
    - user friendly alert names
    - user alert heirarchical referencing
    - multi-alert references TODO: Currently unused and/or broken. Implement bot updates all
    - aliases at every level of the alert reference

    ⚠ If the given string could not be deferenced to UserAlerts, then the 0th element of the returned list
    will be 'ERR'. Before handling the returned list, check to make sure this is not the case.

    TODO: Replace with a LUT implementation

    # :param alertName: A reference to an alert. Heirarchy levels can be given as a space-separated string, or ordered list elements. E.g: 'bot patches major' or ['bot', 'patches', 'major']
    :type alertName: list[str] or str
    :return: A list of UserAlert IDs in accordance with UserAlerts.userAlertsIDsTypes, that are associated with the requested alert reference.
    :rtype: list[str]
    """
    if type(alertName) != list:
        alertName = alertName.split(" ")

    if alertName[0] in ["bounty", "bounties"]:
        return ["bounties_new"]

    elif alertName[0] in ["duel", "duels", "fight", "fights"]:
        if len(alertName) < 2:
            return ["ERR", ":x: Please provide the type of duel notification you would like. E.g: `duels new`"]
        if alertName[1] in ["new", "challenge", "me", "incoming"]:
            return ["duels_challenge_incoming_new"]
        elif alertName[1] in ["cancel", "cancelled", "expire", "expired", "end", "ended"]:
            return ["duels_challenge_incoming_cancel"]
        else:
            return ["ERR", ":x: Unknown duel notification type! Valid types include `new` or `cancel`."]

    elif alertName[0] in ["shop", "shops"]:
        if len(alertName) < 2:
            return ["ERR", ":x: Please provide the type of shop notification you would like. E.g: `shop refresh`"]
        if alertName[1] in ["refresh", "new", "reset", "stock"]:
            return ["shop_refresh"]
        else:
            return ["ERR", ":x: Unknown shop notification type! Valid types include `refresh`."]

    elif alertName[0] in ["bot", "system", "sys"]:
        if len(alertName) < 2:
            return ["ERR", ":x: Please provide the type of system notification you would like. E.g: `bot updates major`"]
        if alertName[1] in ["update", "updates", "patch", "patches", "version", "versions"]:
            if len(alertName) < 3:
                return ["ERR", ":x: Please provide the type of updates pings you would like! Valid types include `major` and `minor`."]
            elif alertName[2] in ["major", "big", "large"]:
                return ["system_updates_major"]
            elif alertName[2] in ["minor", "small", "bug", "fix"]:
                return ["system_updates_minor"]
            else:
                return ["ERR", ":x: Unknown system updates notification type! Valid types include `major` and `minor`."]

        elif alertName[1] in ["misc", "misc.", "announce", "announcement", "announcements", "announces", "miscellaneous"]:
            return ["system_misc"]
        else:
            return ["ERR", ":x: Unknown system notification type! Valid types include `updates` and `misc`."]

    # elif alertName[0] in bbConfig.validItemNames and alertName[0] != "all":
    #     return ["ERR", "Item notifications have not been implemented yet! \:("]
    else:
        return ["ERR", ":x: Unknown notification type! Please refer to `" + bbConfig.commandPrefix + "help notify`"]



async def shutdown():
    """Cleanly prepare for, and then perform, shutdown of the bot.

    This currently:
    - expires all non-saveable reaction menus
    - logs out of discord
    - saves all savedata to file
    """
    menus = list(bbGlobals.reactionMenusDB.values())
    for menu in menus:
        if not menu.saveable:
            await menu.delete()
    botLoggedIn = False
    await bbGlobals.client.logout()
    saveAllDBs()
    print(datetime.now().strftime("%H:%M:%S: Data saved!"))



def getMemberByRefOverDB(uRef : str, dcGuild=None) -> discord.User:
    """Attempt to get a user object from a given string user reference.
    a user reference can be one of:
    - A user mention <@123456> or <@!123456>
    - A user ID 123456
    - A user name Carl
    - A user name and discriminator Carl#0324

    If uRef is not a user mention or ID, dcGuild must be provided, to be searched for the given name.
    When validating a name uRef, the process is much more efficient when also given the user's discriminator.

    :param str uRef: A string or integer indentifying the user object to look up
    :param discord.Guild dcGuild: The guild in which to search for a user identified by uRef. Required if uRef is not a mention or ID. (Default None)
    :return: Either discord.member of a member belonging to dcGuild and matching uRef, or None if uRef is invalid or no matching user could be found
    :rtype: discord.Member or None
    """
    if dcGuild is not None:
        userAttempt = lib.discordUtil.getMemberFromRef(uRef, dcGuild)
    else:
        userAttempt = None
    if userAttempt is None and lib.stringTyping.isInt(uRef):
        if bbGlobals.usersDB.userIDExists(int(uRef)):
            userGuild = lib.discordUtil.findBBUserDCGuild(bbGlobals.usersDB.getUser(int(uRef)))
            if userGuild is not None:
                return userGuild.get_member(int(uRef))
    return userAttempt



####### SYSTEM COMMANDS #######



async def err_nodm(message : discord.Message, args : str, isDM : bool):
    """Send an error message when a command is requested that cannot function outside of a guild

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: ignored
    """
    await message.channel.send(":x: This command can only be used from inside of a server!")



####### USER COMMANDS #######



# @bbGlobals.client.command(name='runHelp')
async def cmd_help(message : discord.Message, args : str, isDM : bool):
    """Print the help strings defined in bbData as an embed.
    If a command is provided in args, the associated help string for just that command is printed.

    :param discord.Message message: the discord message calling the command
    :param str args: empty, or a single command name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    helpEmbed = lib.discordUtil.makeEmbed(titleTxt="BountyBot Commands",
                          thumb=bbGlobals.client.user.avatar_url_as(size=64))
    page = 0
    maxPage = len(bbData.helpDict)
    sectionNames = list(bbData.helpDict.keys())

    if args != "":
        if lib.stringTyping.isInt(args):
            page = int(args)
            if page > maxPage:
                await message.channel.send(":x: There are only " + str(maxPage) + " help pages! Showing page " + str(maxPage) + ":")
                page = maxPage
        elif args.title() in sectionNames:
            page = sectionNames.index(args.title()) + 1
        elif args != "all":
            for section in sectionNames:
                if args in bbData.helpDict[section]:
                    helpEmbed.add_field(
                        name="‎", value="__" + section + "__", inline=False)
                    helpEmbed.add_field(name=bbData.helpDict[section][args][0], value=bbData.helpDict[section][args][1].replace(
                        "$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)
                    await message.channel.send(embed=helpEmbed)
                    return
            await message.channel.send(":x: Help: Command not found!")
            return

    sendChannel = None
    sendDM = False

    if message.author.dm_channel is None:
        await message.author.create_dm()
    if message.author.dm_channel is None:
        sendChannel = message.channel
    else:
        sendChannel = message.author.dm_channel
        sendDM = True

    # list of tuples, 0th element is message, 1st element is embed
    messagesToSend = []

    if page == 0:
        for sectionNum in range(maxPage):
            if sectionNum == maxPage - 1 and maxPage % 2 != 0:
                helpEmbed = lib.discordUtil.makeEmbed(titleTxt="BountyBot Commands",
                                      thumb=bbGlobals.client.user.avatar_url_as(size=64))
                helpEmbed.set_footer(text="Page " + str(maxPage))
                helpEmbed.add_field(name="‎", value="__" +
                                    sectionNames[maxPage-1] + "__", inline=False)
                for currentCommand in bbData.helpDict[sectionNames[maxPage-1]].values():
                    helpEmbed.add_field(name=currentCommand[0], value=currentCommand[1].replace(
                        "$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)
                messagesToSend.append(("‎", helpEmbed))
            elif sectionNum % 2 == 0:
                helpEmbed = lib.discordUtil.makeEmbed(titleTxt="BountyBot Commands",
                                      thumb=bbGlobals.client.user.avatar_url_as(size=64))
                helpEmbed.set_footer(
                    text="Pages " + str(sectionNum + 1) + " - " + str(sectionNum + 2))
                for section in sectionNames[sectionNum:sectionNum + 2]:
                    # section = sectionNames[page - 1]
                    helpEmbed.add_field(name="‎", value="__" +
                                        section + "__", inline=False)
                    for currentCommand in bbData.helpDict[section].values():
                        helpEmbed.add_field(name=currentCommand[0], value=currentCommand[1].replace(
                            "$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)
                messagesToSend.append(("‎", helpEmbed))

    else:
        helpEmbed.set_footer(text="Page " + str(page) + "/" + str(maxPage))
        section = list(bbData.helpDict.keys())[page - 1]
        helpEmbed.add_field(name="‎", value="__" +
                            section + "__", inline=False)
        for currentCommand in bbData.helpDict[section].values():
            helpEmbed.add_field(name=currentCommand[0], value=currentCommand[1].replace(
                "$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)
        messagesToSend.append(("‎", helpEmbed))

    try:
        if page in [0, 1]:
            await sendChannel.send(bbData.helpIntro.replace("$COMMANDPREFIX$", bbConfig.commandPrefix))
        for msg in messagesToSend:
            await sendChannel.send(msg[0], embed=msg[1])
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return

    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji.sendable)

bbCommands.register("help", cmd_help, 0)
dmCommands.register("help", cmd_help, 0)


async def cmd_how_to_play(message : discord.Message, args : str, isDM : bool):
    """Print a short guide, teaching users how to play bounties.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    sendChannel = None
    sendDM = False

    if message.author.dm_channel is None:
        await message.author.create_dm()
    if message.author.dm_channel is None:
        sendChannel = message.channel
    else:
        sendChannel = message.author.dm_channel
        sendDM = True

    try:
        newBountiesChannelStr = ""
        if not isDM:
            requestedBBGuild = bbGlobals.guildsDB.addGuildID(message.guild.id)
            if requestedBBGuild.hasBountyBoardChannel:
                newBountiesChannelStr = " in <#" + str(requestedBBGuild.bountyBoardChannel.channel.id) + ">"
            elif requestedBBGuild.hasAnnounceChannel:
                newBountiesChannelStr = " in <#" + str(requestedBBGuild.getAnnounceChannel().id) + ">"

        howToPlayEmbed = lib.discordUtil.makeEmbed(titleTxt='**How To Play**', desc="This game is based on the *'Most Wanted'* system from Galaxy on Fire 2. If you have played the Supernova addon, this should be familiar!\n\nIf at any time you would like information about a command, use the `" +
                                   bbConfig.commandPrefix + "help [command]` command. To see all commands, just use `" + bbConfig.commandPrefix + "help`.\n‎", footerTxt="Have fun! 🚀", thumb='https://cdn.discordapp.com/avatars/699740424025407570/1bfc728f46646fa964c6a77fc0cf2335.webp')
        howToPlayEmbed.add_field(name="1. New Bounties", value="Every 15m - 1h (randomly), bounties are announced" + newBountiesChannelStr + ".\n• Use `" + bbConfig.commandPrefix +
                                 "bounties` to see the currently active bounties.\n• Criminals spawn in a system somewhere on the `" + bbConfig.commandPrefix + "map`.\n• To view a criminal's current route *(possible systems)*, use `" + bbConfig.commandPrefix + "route [criminal]`.\n‎", inline=False)
        howToPlayEmbed.add_field(name="2. System Checking", value="Now that we know where our criminal could be, we can check a system with `" + bbConfig.commandPrefix +
                                 "check [system]`.\nThis system will now be crossed out in the criminal's `" + bbConfig.commandPrefix + "route`, so we know not to check there.\n\n> Didn't win the bounty? No worries!\nYou will be awarded credits for helping *narrow down the search*.\n‎", inline=False)
        howToPlayEmbed.add_field(name="3. Items", value="Now that you've got some credits, try customising your `" + bbConfig.commandPrefix + "loadout`!\n• You can see your inventory of inactive items in the `" +
                                 bbConfig.commandPrefix + "hangar`.\n• You can `" + bbConfig.commandPrefix + "buy` more items from the `" + bbConfig.commandPrefix + "shop`.\n‎", inline=False)
        howToPlayEmbed.add_field(name="Extra Notes/Tips", value="• Bounties are shared across all servers, everyone is competing to find them!\n• Each server has its own `" + bbConfig.commandPrefix +
                                 "shop`. The shops refresh every *6 hours.*\n• Is a criminal, item or system name too long? Use an alias instead! You can see aliases with `" + bbConfig.commandPrefix + "info`.\n• Having trouble getting to new bounties in time? Try out the new `" + bbConfig.commandPrefix + "notify bounties` command!", inline=False)

        await sendChannel.send(embed=howToPlayEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return

    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji.sendable)

bbCommands.register("how-to-play", cmd_how_to_play, 0, aliases=["guide"])
dmCommands.register("how-to-play", cmd_how_to_play, 0, aliases=["guide"])


async def cmd_hello(message : discord.Message, args : str, isDM : bool):
    """say hello!

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("Greetings, pilot! **o7**")

bbCommands.register("hello", cmd_hello, 0)
dmCommands.register("hello", cmd_hello, 0)


async def cmd_balance(message : discord.Message, args : str, isDM : bool):
    """print the balance of the specified user, use the calling user if no user is specified.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # If no user is specified, send the balance of the calling user
    if args == "":
        if not bbGlobals.usersDB.userIDExists(message.author.id):
            bbGlobals.usersDB.addUser(message.author.id)
        await message.channel.send(":moneybag: **" + message.author.display_name + "**, you have **" + str(bbGlobals.usersDB.getUser(message.author.id).credits) + " Credits**.")

    # If a user is specified
    else:
        # Verify the passed user tag
        requestedUser = getMemberByRefOverDB(args, dcGuild=message.guild)
        if requestedUser is None:
            await message.channel.send(":x: Unknown user!")
            return
        # ensure that the user is in the users database
        if not bbGlobals.usersDB.userIDExists(requestedUser.id):
            bbGlobals.usersDB.addUser(requestedUser.id)
        # send the user's balance
        await message.channel.send(":moneybag: **" + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "** has **" + str(bbGlobals.usersDB.getUser(requestedUser.id).credits) + " Credits**.")

bbCommands.register("balance", cmd_balance, 0, aliases=["bal", "credits"], forceKeepArgsCasing=True)
dmCommands.register("balance", cmd_balance, 0, aliases=["bal", "credits"], forceKeepArgsCasing=True)


async def cmd_stats(message : discord.Message, args : str, isDM : bool):
    """print the stats of the specified user, use the calling user if no user is specified.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # if no user is specified
    if args == "":
        # create the embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=message.author.display_name,
                               footerTxt="Pilot number #" + message.author.discriminator, thumb=message.author.avatar_url_as(size=64))
        # If the calling user is not in the database, don't bother adding them just print zeroes.
        if not bbGlobals.usersDB.userIDExists(message.author.id):
            statsEmbed.add_field(name="Credits balance:", value=0, inline=True)
            statsEmbed.add_field(name="Total value:",
                                 value=str(bbUser.defaultUserValue), inline=True)
            statsEmbed.add_field(
                name="‎", value="__Bounty Hunting__", inline=False)
            statsEmbed.add_field(
                name="Total systems checked:", value=0, inline=True)
            statsEmbed.add_field(
                name="Total bounties won:", value=0, inline=True)
            statsEmbed.add_field(
                name="Total earned from bounties:", value=0, inline=True)
            statsEmbed.add_field(name="‎", value="__Dueling__", inline=False)
            statsEmbed.add_field(name="Duels won:", value="0", inline=True)
            statsEmbed.add_field(name="Duels lost:", value="0", inline=True)
            statsEmbed.add_field(name="Total credits won:",
                                 value="0", inline=True)
            statsEmbed.add_field(name="Total credits lost:",
                                 value="0", inline=True)
        # If the calling user is in the database, print the stats stored in the user's database entry
        else:
            userObj = bbGlobals.usersDB.getUser(message.author.id)
            statsEmbed.add_field(name="Credits balance:",
                                 value=str(userObj.credits), inline=True)
            statsEmbed.add_field(name="Total value:",
                                 value=str(userObj.getStatByName("value")), inline=True)
            statsEmbed.add_field(
                name="‎", value="__Bounty Hunting__", inline=False)
            statsEmbed.add_field(name="Total systems checked:", value=str(
                userObj.systemsChecked), inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=str(
                userObj.bountyWins), inline=True)
            statsEmbed.add_field(name="Total credits earned from bounties:", value=str(
                userObj.lifetimeCredits), inline=True)
            statsEmbed.add_field(name="‎", value="__Dueling__", inline=False)
            statsEmbed.add_field(name="Duels won:", value=str(
                userObj.duelWins), inline=True)
            statsEmbed.add_field(name="Duels lost:", value=str(
                userObj.duelLosses), inline=True)
            statsEmbed.add_field(name="Total credits won:", value=str(
                userObj.duelCreditsWins), inline=True)
            statsEmbed.add_field(name="Total credits lost:", value=str(
                userObj.duelCreditsLosses), inline=True)

        # send the stats embed
        await message.channel.send(embed=statsEmbed)
        return

    # If a user is specified
    else:
        requestedUser = getMemberByRefOverDB(args, dcGuild=message.guild)
        # verify the user mention
        if requestedUser is None:
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance <user>` to display someone else's balance!\nWhen referencing a player from another server, you must use their long ID number")
            return

        # create the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=lib.discordUtil.userOrMemberName(requestedUser, message.guild),
                               footerTxt="Pilot number #" + requestedUser.discriminator, thumb=requestedUser.avatar_url_as(size=64))
        # If the requested user is not in the database, don't bother adding them just print zeroes
        if not bbGlobals.usersDB.userIDExists(requestedUser.id):
            statsEmbed.add_field(name="Credits balance:", value=0, inline=True)
            statsEmbed.add_field(name="Total value:",
                                 value=str(bbUser.defaultUserValue), inline=True)
            statsEmbed.add_field(
                name="‎", value="__Bounty Hunting__", inline=False)
            statsEmbed.add_field(
                name="Total systems checked:", value=0, inline=True)
            statsEmbed.add_field(
                name="Total bounties won:", value=0, inline=True)
            statsEmbed.add_field(
                name="Total earned from bounties:", value=0, inline=True)
            statsEmbed.add_field(name="‎", value="__Dueling__", inline=False)
            statsEmbed.add_field(name="Duels won:", value="0", inline=True)
            statsEmbed.add_field(name="Duels lost:", value="0", inline=True)
            statsEmbed.add_field(name="Total credits won:",
                                 value="0", inline=True)
            statsEmbed.add_field(name="Total credits lost:",
                                 value="0", inline=True)
        # Otherwise, print the stats stored in the user's database entry
        else:
            userObj = bbGlobals.usersDB.getUser(requestedUser.id)
            statsEmbed.add_field(name="Credits balance:",
                                 value=str(userObj.credits), inline=True)
            statsEmbed.add_field(name="Total value:",
                                 value=str(userObj.getStatByName("value")), inline=True)
            statsEmbed.add_field(
                name="‎", value="__Bounty Hunting__", inline=False)
            statsEmbed.add_field(name="Total systems checked:", value=str(
                userObj.systemsChecked), inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=str(
                userObj.bountyWins), inline=True)
            statsEmbed.add_field(name="Total credits earned from bounties:", value=str(
                userObj.lifetimeCredits), inline=True)
            statsEmbed.add_field(name="‎", value="__Dueling__", inline=False)
            statsEmbed.add_field(name="Duels won:", value=str(
                userObj.duelWins), inline=True)
            statsEmbed.add_field(name="Duels lost:", value=str(
                userObj.duelLosses), inline=True)
            statsEmbed.add_field(name="Total credits won:", value=str(
                userObj.duelCreditsWins), inline=True)
            statsEmbed.add_field(name="Total credits lost:", value=str(
                userObj.duelCreditsLosses), inline=True)

        # send the stats embed
        await message.channel.send(embed=statsEmbed)

bbCommands.register("stats", cmd_stats, 0, aliases=["profile"], forceKeepArgsCasing=True)
dmCommands.register("stats", cmd_stats, 0, aliases=["profile"], forceKeepArgsCasing=True)


async def cmd_map(message : discord.Message, args : str, isDM : bool):
    """send the image of the GOF2 starmap. If -g is passed, send the grid image

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain -g
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # If -g is specified, send the image with grid overlay
    if args == "-g":
        await message.channel.send(bbData.mapImageWithGraphLink)
    # otherwise, send the image with no grid overlay
    else:
        await message.channel.send(bbData.mapImageNoGraphLink)

bbCommands.register("map", cmd_map, 0, aliases=["starmap"])
dmCommands.register("map", cmd_map, 0, aliases=["starmap"])


async def cmd_check(message : discord.Message, args : str, isDM : bool):
    """⚠ WARNING: MARKED FOR CHANGE ⚠
    The following function is provisional and marked as planned for overhaul.
    Details: Criminal fights are to switch algorithm, using bbObjects.items.battles as a base. Criminals are to be assigned
    Procedurally generated ships based on a difficulty rating (by direct extension of the items' rarity rankings from bbConfig.__init__)

    Check a system for bounties and handle rewards

    :param discord.Message message: the discord message calling the command
    :param str args: string containing one system to check
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # Verify that this guild has bounties enabled
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if callingBBGuild.bountiesDisabled:
        await message.channel.send(":x: This server does not have bounties enabled.")
        return

    # verify this is the calling user's home guild. If no home guild is set, transfer here.
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if not requestedBBUser.hasHomeGuild():
        await requestedBBUser.transferGuild(message.guild)
        await message.channel.send(":airplane_arriving: Your home guild has been set.")
    elif requestedBBUser.homeGuildID != message.guild.id:
        await message.channel.send(":x: This command can only be used from your home guild!")
        return

    # verify a system was given
    if args == "":
        await message.channel.send(":x: Please provide a system to check! E.g: `" + bbConfig.commandPrefix + "check Pescal Inartu`")
        return

    requestedSystem = args.title()
    systObj = None

    # attempt to find the requested system in the database
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(requestedSystem):
            systObj = bbData.builtInSystemObjs[syst]

    # reject if the requested system is not in the database
    if systObj is None:
        if len(requestedSystem) < 20:
            await message.channel.send(":x: The **" + requestedSystem + "** system is not on my star map! :map:")
        else:
            await message.channel.send(":x: The **" + requestedSystem[0:15] + "**... system is not on my star map! :map:")
        return

    requestedSystem = systObj.name

    if not requestedBBUser.activeShip.hasWeaponsEquipped() and not requestedBBUser.activeShip.hasTurretsEquipped():
        await message.channel.send(":x: Your ship has no weapons equipped!")
        return

    # Restrict the number of bounties a player may win in a single day
    if requestedBBUser.dailyBountyWinsReset < datetime.utcnow():
        requestedBBUser.bountyWinsToday = 0
        requestedBBUser.dailyBountyWinsReset = datetime.utcnow().replace(
                            hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})

    if requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
        await message.channel.send(":x: You have reached the maximum number of bounty wins allowed for today! Check back tomorrow.")
        return

    # ensure the calling user is not on checking cooldown
    if datetime.utcfromtimestamp(requestedBBUser.bountyCooldownEnd) < datetime.utcnow():
        bountyWon = False
        systemInBountyRoute = False
        dailyBountiesMaxReached = False

        # Loop over all bounties in the database
        for fac in callingBBGuild.bountiesDB.getFactions():
            # list of completed bounties to remove from the bounties database
            toPop = []
            for bounty in callingBBGuild.bountiesDB.getFactionBounties(fac):

                # Check the passed system in current bounty
                # If current bounty resides in the requested system
                checkResult = bounty.check(requestedSystem, message.author.id)
                if checkResult == 3:
                    requestedBBUser.bountyWinsToday += 1
                    if not dailyBountiesMaxReached and requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
                        requestedBBUser.dailyBountyWinsReset = datetime.utcnow().replace(
                            hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})
                        dailyBountiesMaxReached = True

                    bountyWon = True
                    # reward all contributing users
                    rewards = bounty.calcRewards()
                    for userID in rewards:
                        bbGlobals.usersDB.getUser(
                            userID).credits += rewards[userID]["reward"]
                        bbGlobals.usersDB.getUser(
                            userID).lifetimeCredits += rewards[userID]["reward"]
                    # add this bounty to the list of bounties to be removed
                    toPop += [bounty]
                    # Announce the bounty has ben completed
                    await callingBBGuild.announceBountyWon(bounty, rewards, message.author)

                if checkResult != 0:
                    systemInBountyRoute = True
                    await updateBountyBoardChannel(callingBBGuild, bounty, bountyComplete=checkResult == 3)

            # remove all completed bounties
            for bounty in toPop:
                callingBBGuild.bountiesDB.removeBountyObj(bounty)

        sightedCriminalsStr = ""
        # Check if any bounties are close to the requested system in their route, defined by bbConfig.closeBountyThreshold
        for fac in callingBBGuild.bountiesDB.getFactions():
            for bounty in callingBBGuild.bountiesDB.getFactionBounties(fac):
                if requestedSystem in bounty.route:
                    if 0 < bounty.route.index(bounty.answer) - bounty.route.index(requestedSystem) < bbConfig.closeBountyThreshold:
                        # Print any close bounty names
                        sightedCriminalsStr += "**       **• Local security forces spotted **" + \
                            lib.discordUtil.criminalNameOrDiscrim(
                                bounty.criminal) + "** here recently.\n"
        sightedCriminalsStr = sightedCriminalsStr[:-1]

        # If a bounty was won, print a congratulatory message
        if bountyWon:
            requestedBBUser.bountyWins += 1
            await message.channel.send(sightedCriminalsStr + "\n" + ":moneybag: **" + message.author.display_name + "**, you now have **" + str(requestedBBUser.credits) + " Credits!**\n" +
                                       ("You have now reached the maximum number of bounty wins allowed for today! Please check back tomorrow." if dailyBountiesMaxReached else "You have **" + str(bbConfig.maxDailyBountyWins - requestedBBUser.bountyWinsToday) + "** remaining bounty wins today!"))
                                       
        # If no bounty was won, print an error message
        else:
            await message.channel.send(":telescope: **" + message.author.display_name + "**, you did not find any criminals in **" + requestedSystem.title() + "**!\n" + sightedCriminalsStr)

        # Only put the calling user on checking cooldown and increment systemsChecked stat if the system checked is on an active bounty's route.
        if systemInBountyRoute:
            requestedBBUser.systemsChecked += 1
            # Put the calling user on checking cooldown
            requestedBBUser.bountyCooldownEnd = (datetime.utcnow() +
                                                 timedelta(minutes=bbConfig.checkCooldown["minutes"])).timestamp()

    # If the calling user is on checking cooldown
    else:
        # Print an error message with the remaining time on the calling user's cooldown
        diff = datetime.utcfromtimestamp(bbGlobals.usersDB.getUser(
            message.author.id).bountyCooldownEnd) - datetime.utcnow()
        minutes = int(diff.total_seconds() / 60)
        seconds = int(diff.total_seconds() % 60)
        await message.channel.send(":stopwatch: **" + message.author.display_name + "**, your *Khador Drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")

bbCommands.register("check", cmd_check, 0, aliases=["search"])
dmCommands.register("check", cmd_check, 0, aliases=["search"])


async def cmd_bounties(message : discord.Message, args : str, isDM : bool):
    """List a summary of all currently active bounties.
    If a faction is specified, print a more detailed summary of that faction's active bounties

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a faction
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # Verify that this guild has bounties enabled
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if callingBBGuild.bountiesDisabled:
        await message.channel.send(":x: This server does not have bounties enabled.")
        return

    # If no faction is specified
    if args == "":
        outmessage = "__**Active Bounties**__\nTimes given in UTC. See more detailed information with `" + \
            bbConfig.commandPrefix + "bounties <faction>`\n```css"
        preLen = len(outmessage)
        # Collect and print summaries of all active bounties
        for fac in callingBBGuild.bountiesDB.getFactions():
            if callingBBGuild.bountiesDB.hasBounties(faction=fac):
                outmessage += "\n • [" + fac.title() + "]: "
                for bounty in callingBBGuild.bountiesDB.getFactionBounties(fac):
                    outmessage += lib.discordUtil.criminalNameOrDiscrim(bounty.criminal) + ", "
                outmessage = outmessage[:-2]
        # If no active bounties were found, print an error
        if len(outmessage) == preLen:
            outmessage += "\n[  No currently active bounties! Please check back later.  ]"
        # Restrict the number of bounties a player may win in a single day
        requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
        if requestedBBUser.dailyBountyWinsReset < datetime.utcnow():
            requestedBBUser.bountyWinsToday = 0
            requestedBBUser.dailyBountyWinsReset = datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})
        if requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
            maxBountiesMsg = "\nYou have reached the maximum number of bounty wins allowed for today! Check back tomorrow."
        else:
            maxBountiesMsg = "\nYou have **" + str(bbConfig.maxDailyBountyWins - requestedBBUser.bountyWinsToday) + "** remaining bounty wins today!"
        outmessage += "```" + maxBountiesMsg
        await message.channel.send(outmessage)

    # if a faction is specified
    else:
        requestedFaction = args.lower()
        # verify the passed faction
        if requestedFaction not in bbData.bountyFactions:
            if len(requestedFaction) < 20:
                await message.channel.send(":x: Unrecognised faction: **" + requestedFaction + "**")
            else:
                await message.channel.send(":x: Unrecognised faction **" + requestedFaction[0:15] + "**...")
            return

        # Ensure the requested faction has active bounties
        if not callingBBGuild.bountiesDB.hasBounties(faction=requestedFaction):
            await message.channel.send(":stopwatch: There are no **" + requestedFaction.title() + "** bounties active currently!\nYou have **" + str(bbConfig.maxDailyBountyWins - bbGlobals.usersDB.getOrAddID(message.author.id).bountyWinsToday) + "** remaining bounty wins today!")
        else:
            # Collect and print summaries of the requested faction's active bounties
            outmessage = "__**Active " + requestedFaction.title() + \
                " Bounties**__\nTimes given in UTC.```css"
            for bounty in callingBBGuild.bountiesDB.getFactionBounties(requestedFaction):
                endTimeStr = datetime.utcfromtimestamp(
                    bounty.endTime).strftime("%B %d %H %M %S").split(" ")
                outmessage += "\n • [" + lib.discordUtil.criminalNameOrDiscrim(bounty.criminal) + "]" + " " * (bbData.longestBountyNameLength + 1 - len(lib.discordUtil.criminalNameOrDiscrim(bounty.criminal))) + ": " + str(
                    int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + lib.stringTyping.getNumExtension(int(endTimeStr[1])) + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                if endTimeStr[4] != "00":
                    outmessage += ":" + endTimeStr[4]
                else:
                    outmessage += "   "
                outmessage += " - " + \
                    str(len(bounty.route)) + " possible system"
                if len(bounty.route) != 1:
                    outmessage += "s"
            maxBountiesMsg = ""
            if bbGlobals.usersDB.userIDExists(message.author.id):
                requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
                # Restrict the number of bounties a player may win in a single day
                if requestedBBUser.dailyBountyWinsReset < datetime.utcnow():
                    requestedBBUser.bountyWinsToday = 0
                    requestedBBUser.dailyBountyWinsReset = datetime.utcnow().replace(
                            hour=0, minute=0, second=0, microsecond=0) + lib.timeUtil.timeDeltaFromDict({"hours": 24})
                if requestedBBUser.bountyWinsToday >= bbConfig.maxDailyBountyWins:
                    maxBountiesMsg = "\nYou have reached the maximum number of bounty wins allowed for today! Check back tomorrow."
                else:
                    maxBountiesMsg = "\nYou have **" + str(bbConfig.maxDailyBountyWins - requestedBBUser.bountyWinsToday) + "** remaining bounty wins today!"
            await message.channel.send(outmessage + "```\nTrack down criminals and **win credits** using `" + bbConfig.commandPrefix + "route` and `" + bbConfig.commandPrefix + "check`!" + maxBountiesMsg)

bbCommands.register("bounties", cmd_bounties, 0)
dmCommands.register("bounties", err_nodm, 0)


async def cmd_route(message : discord.Message, args : str, isDM : bool):
    """Display the current route of the requested criminal

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a criminal name or alias
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # Verify that this guild has bounties enabled
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if callingBBGuild.bountiesDisabled:
        await message.channel.send(":x: This server does not have bounties enabled.")
        return

    # verify a criminal was specified
    if args == "":
        await message.channel.send(":x: Please provide the criminal name! E.g: `" + bbConfig.commandPrefix + "route Kehnor`")
        return

    requestedBountyName = args
    # if the named criminal is wanted
    if callingBBGuild.bountiesDB.bountyNameExists(requestedBountyName.lower()):
        # display their route
        bounty = callingBBGuild.bountiesDB.getBounty(requestedBountyName.lower())
        outmessage = "**" + \
            lib.discordUtil.criminalNameOrDiscrim(bounty.criminal) + "**'s current route:\n> "
        for system in bounty.route:
            outmessage += " " + ("~~" if bounty.checked[system] != -1 else "") + system + (
                "~~" if bounty.checked[system] != -1 else "") + ","
        outmessage = outmessage[:-1] + ". :rocket:"
        await message.channel.send(outmessage)
    # if the named criminal is not wanted
    else:
        # display an error
        outmsg = ":x: That pilot isn't on any bounty boards! :clipboard:"
        # accept user name + discrim instead of tags to avoid mention spam
        if lib.stringTyping.isMention(requestedBountyName):
            outmsg += "\n:warning: **Don't tag users**, use their name and ID number like so: `" + \
                bbConfig.commandPrefix + "route Trimatix#2244`"
        await message.channel.send(outmsg)

bbCommands.register("route", cmd_route, 0)
dmCommands.register("route", cmd_route, 0)


async def cmd_make_route(message : discord.Message, args : str, isDM : bool):
    """display the shortest route between two systems

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the start and end systems, separated by a comma and a space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify two systems are given separated by a comma and a space
    if args == "" or "," not in args or len(args[:args.index(",")]) < 1 or len(args[args.index(","):]) < 2:
        await message.channel.send(":x: Please provide source and destination systems, separated with a comma and space.\nFor example: `" + bbConfig.commandPrefix + "make-route Pescal Inartu, Loma`")
        return
    if args.count(",") > 1:
        await message.channel.send(":x: Please only provide **two** systems!")
        return

    requestedStart = args.split(",")[0].title()
    requestedEnd = args.split(",")[1][1:].title()
    startSyst = ""
    endSyst = ""

    # attempt to look up the requested systems in the built in systems database
    systemsFound = {requestedStart: False, requestedEnd: False}
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(requestedStart):
            systemsFound[requestedStart] = True
            startSyst = syst
        if bbData.builtInSystemObjs[syst].isCalled(requestedEnd):
            systemsFound[requestedEnd] = True
            endSyst = syst

    # report any unrecognised systems
    for syst in [requestedStart, requestedEnd]:
        if not systemsFound[syst]:
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system is not on my star map! :map:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system is not on my star map! :map:")
            return

    # report any systems that were recognised, but do not have any neighbours
    for syst in [startSyst, endSyst]:
        if not bbData.builtInSystemObjs[syst].hasJumpGate():
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system does not have a jump gate! :rocket:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system does not have a jump gate! :rocket:")
            return

    # build and print the route, reporting any errors in the route generation process
    routeStr = ""
    for currentSyst in lib.pathfinding.makeRoute(startSyst, endSyst):
        routeStr += currentSyst + ", "
    if routeStr.startswith("#"):
        await message.channel.send(":x: ERR: Processing took too long! :stopwatch:")
    elif routeStr.startswith("!"):
        await message.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
    elif startSyst == endSyst:
        await message.channel.send(":thinking: You're already there, pilot!")
    else:
        await message.channel.send("Here's the shortest route from **" + startSyst + "** to **" + endSyst + "**:\n> " + routeStr[:-2] + " :rocket:")

bbCommands.register("make-route", cmd_make_route, 0)
dmCommands.register("make-route", cmd_make_route, 0)


async def cmd_system(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified system

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a system in the GOF2 starmap
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a systemw as specified
    if args == "":
        await message.channel.send(":x: Please provide a system! Example: `" + bbConfig.commandPrefix + "system Augmenta`")
        return

    # attempt to look up the specified system
    systArg = args.title()
    systObj = None
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(systArg):
            systObj = bbData.builtInSystemObjs[syst]

    # report unrecognised systems
    if systObj is None:
        if len(systArg) < 20:
            await message.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
        else:
            await message.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
    else:
        # build the neighbours statistic into a string
        neighboursStr = ""
        for x in systObj.neighbours:
            neighboursStr += x + ", "
        if neighboursStr == "":
            neighboursStr = "No Jumpgate"
        else:
            neighboursStr = neighboursStr[:-2]

        # build the statistics embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[systObj.faction], desc="__System Information__",
                               titleTxt=systObj.name, footerTxt=systObj.faction.title(), thumb=bbData.factionIcons[systObj.faction])
        statsEmbed.add_field(
            name="Security Level:", value=bbData.securityLevels[systObj.security].title())
        statsEmbed.add_field(name="Neighbour Systems:", value=neighboursStr)

        # list the system's aliases as a string
        if len(systObj.aliases) > 1:
            aliasStr = ""
            for alias in systObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        # list the system's wiki if one exists
        if systObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + systObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-system", 0, cmd_system)


async def cmd_criminal(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt criminal

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a criminal name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a criminal was given
    if args == "":
        await message.channel.send(":x: Please provide a criminal! Example: `" + bbConfig.commandPrefix + "criminal Toma Prakupy`")
        return

    # look up the criminal object
    criminalName = args.title()
    criminalObj = None
    for crim in bbData.builtInCriminalObjs.keys():
        if bbData.builtInCriminalObjs[crim].isCalled(criminalName):
            criminalObj = bbData.builtInCriminalObjs[crim]

    # report unrecognised criminal names
    if criminalObj is None:
        if len(criminalName) < 20:
            await message.channel.send(":x: **" + criminalName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + criminalName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[criminalObj.faction],
                               desc="__Criminal File__", titleTxt=criminalObj.name, thumb=criminalObj.icon)
        statsEmbed.add_field(
            name="Wanted By:", value=criminalObj.faction.title() + "s")
        # include the criminal's aliases and wiki if they exist
        if len(criminalObj.aliases) > 1:
            aliasStr = ""
            for alias in criminalObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if criminalObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + criminalObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-criminal", 0, cmd_criminal)


async def cmd_ship(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt ship

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")
        return

    # look up the ship object
    itemName = args.title()
    itemObj = None
    for ship in bbData.builtInShipData.values():
        shipObj = bbShip.fromDict(ship)
        if shipObj.isCalled(itemName):
            itemObj = shipObj

    # report unrecognised ship names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Ship File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        statsEmbed.add_field(name="Value:", value=lib.stringTyping.commaSplitNum(
            str(itemObj.getValue(shipUpgradesOnly=True))) + " Credits")
        statsEmbed.add_field(name="Armour:", value=str(itemObj.getArmour()))
        statsEmbed.add_field(name="Cargo:", value=str(itemObj.getCargo()))
        statsEmbed.add_field(
            name="Handling:", value=str(itemObj.getHandling()))
        statsEmbed.add_field(name="Max Primaries:",
                             value=str(itemObj.getMaxPrimaries()))
        if len(itemObj.weapons) > 0:
            weaponStr = "*["
            for weapon in itemObj.weapons:
                weaponStr += weapon.name + ", "
            statsEmbed.add_field(name="Equipped Primaries:",
                                 value=weaponStr[:-2] + "]*")
        statsEmbed.add_field(name="Max Secondaries:",
                             value=str(itemObj.getNumSecondaries()))
        # if len(itemObj.secondaries) > 0:
        #     secondariesStr = "*["
        #     for secondary in itemObj.secondaries:
        #         secondariesStr += secondary.name + ", "
        #     statsEmbed.add_field(name="Equipped Secondaries",value=secondariesStr[:-2] + "]*")
        statsEmbed.add_field(name="Turret Slots:",
                             value=str(itemObj.getMaxTurrets()))
        if len(itemObj.turrets) > 0:
            turretsStr = "*["
            for turret in itemObj.turrets:
                turretsStr += turret.name + ", "
            statsEmbed.add_field(name="Equipped Turrets:",
                                 value=turretsStr[:-2] + "]*")
        statsEmbed.add_field(name="Modules Slots:",
                             value=str(itemObj.getMaxModules()))
        if len(itemObj.modules) > 0:
            modulesStr = "*["
            for module in itemObj.modules:
                modulesStr += module.name + ", "
            statsEmbed.add_field(name="Equipped Modules:",
                                 value=modulesStr[:-2] + "]*")
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-ship", 0, cmd_ship)


async def cmd_weapon(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt weapon

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a weapon name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a weapon! Example: `" + bbConfig.commandPrefix + "weapon Nirai Impulse EX 1`")
        return

    # look up the weapon object
    itemName = args.title()
    itemObj = None
    for weap in bbData.builtInWeaponObjs.keys():
        if bbData.builtInWeaponObjs[weap].isCalled(itemName):
            itemObj = bbData.builtInWeaponObjs[weap]

    # report unrecognised weapon names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Weapon File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:", value=str(itemObj.dps))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-weapon", 0, cmd_weapon)


async def cmd_module(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt module

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a module name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a module! Example: `" + bbConfig.commandPrefix + "module Groza Mk II`")
        return

    # look up the module object
    itemName = args.title()
    itemObj = None
    for module in bbData.builtInModuleObjs.keys():
        if bbData.builtInModuleObjs[module].isCalled(itemName):
            itemObj = bbData.builtInModuleObjs[module]

    # report unrecognised module names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Module File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="Stats:", value=str(
            itemObj.statsStringShort()))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-module", 0, cmd_module)


async def cmd_turret(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt turret

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a turret name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a turret! Example: `" + bbConfig.commandPrefix + "turret Groza Mk II`")
        return

    # look up the turret object
    itemName = args.title()
    itemObj = None
    for turr in bbData.builtInTurretObjs.keys():
        if bbData.builtInTurretObjs[turr].isCalled(itemName):
            itemObj = bbData.builtInTurretObjs[turr]

    # report unrecognised turret names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Turret File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:", value=str(itemObj.dps))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-turret", 0, cmd_turret)


async def cmd_commodity(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt commodity

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a commodity name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("Commodity items have not been implemented yet!")
    return

    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a commodity! Example: `" + bbConfig.commandPrefix + "commodity Groza Mk II`")
        return

    # look up the commodity object
    itemName = args.title()
    itemObj = None
    for crim in bbData.builtInCommodityObjs.keys():
        if bbData.builtInCommodityObjs[crim].isCalled(itemName):
            itemObj = bbData.builtInCommodityObjs[crim]

    # report unrecognised commodity names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(
            col=bbData.factionColours[itemObj.faction], desc="__Item File__", titleTxt=itemObj.name, thumb=itemObj.icon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(
            name="Wanted By:", value=itemObj.faction.title() + "s")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-commodity", 0, cmd_commodity)


async def cmd_info(message : discord.Message, args : str, isDM : bool):
    """Return statistics about a named game object, of a specified type.
    The named used to reference the object may be an alias.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an object type, followed by a space, followed by the object name. For example, 'criminal toma prakupy'
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send(":x: Please give an object type to look up! (system/criminal/ship/weapon/module/turret/commodity)")
        return

    argsSplit = args.split(" ")
    if argsSplit[0] not in ["system", "criminal", "ship", "weapon", "module", "turret", "commodity"]:
        await message.channel.send(":x: Invalid object type! (system/criminal/ship/weapon/module/turret/commodity)")
        return

    if argsSplit[0] == "system":
        await cmd_system(message, args[7:], isDM)
    elif argsSplit[0] == "criminal":
        await cmd_criminal(message, args[9:], isDM)
    elif argsSplit[0] == "ship":
        await cmd_ship(message, args[5:], isDM)
    elif argsSplit[0] == "weapon":
        await cmd_weapon(message, args[7:], isDM)
    elif argsSplit[0] == "module":
        await cmd_module(message, args[7:], isDM)
    elif argsSplit[0] == "turret":
        await cmd_turret(message, args[7:], isDM)
    elif argsSplit[0] == "commodity":
        await cmd_commodity(message, args[10:], isDM)
    else:
        await message.channel.send(":x: Unknown object type! (system/criminal/ship/weapon/module/turret/commodity)")

bbCommands.register("info", cmd_info, 0)
dmCommands.register("info", cmd_info, 0)


async def cmd_leaderboard(message : discord.Message, args : str, isDM : bool):
    """display leaderboards for different statistics
    if no arguments are given, display the local leaderboard for pilot value (value of loadout, hangar and balance, summed)
    if -g is given, display the appropriate leaderbaord across all guilds
    if -c is given, display the leaderboard for current balance
    if -s is given, display the leaderboard for systems checked
    if -w is given, display the leaderboard for bounties won

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the arguments the user passed to the command
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # across all guilds?
    globalBoard = False
    # stat to display
    stat = "value"
    # "global" or the local guild name
    boardScope = message.guild.name
    # user friendly string for the stat
    boardTitle = "Total Player Value"
    # units for the stat
    boardUnit = "Credit"
    boardUnits = "Credits"
    boardDesc = "*The total value of player inventory, loadout and credits balance"

    # change leaderboard arguments based on the what is provided in args
    if args != "":
        args = args.lower()
        if not args.startswith("-"):
            await message.channel.send(":x: Please prefix your arguments with a dash! E.g: `" + bbConfig.commandPrefix + "leaderboard -gc`")
            return
        args = args[1:]
        if ("g" not in args and len(args) > 2) or ("g" in args and len(args) > 3):
            await message.channel.send(":x: Too many arguments! Please only specify one leaderboard. E.g: `" + bbConfig.commandPrefix + "leaderboard -gc`")
            return
        for arg in args:
            if arg not in "gcsw":
                await message.channel.send(":x: Unknown argument: '**" + arg + "**'. Please refer to `" + bbConfig.commandPrefix + "help leaderboard`")
                return
        if "c" in args:
            stat = "credits"
            boardTitle = "Current Balance"
            boardUnit = "Credit"
            boardUnits = "Credits"
            boardDesc = "*Current player credits balance"
        elif "s" in args:
            stat = "systemsChecked"
            boardTitle = "Systems Checked"
            boardUnit = "System"
            boardUnits = "Systems"
            boardDesc = "*Total number of systems `" + bbConfig.commandPrefix + "check`ed"
        elif "w" in args:
            stat = "bountyWins"
            boardTitle = "Bounties Won"
            boardUnit = "Bounty"
            boardUnits = "Bounties"
            boardDesc = "*Total number of bounties won"
        if "g" in args:
            globalBoard = True
            boardScope = "Global Leaderboard"
            boardDesc += " across all servers"

    boardDesc += ".*"

    # get the requested stats and sort users by the stat
    inputDict = {}
    for user in bbGlobals.usersDB.getUsers():
        if (globalBoard and bbGlobals.client.get_user(user.id) is not None) or (not globalBoard and message.guild.get_member(user.id) is not None):
            inputDict[user.id] = user.getStatByName(stat)
    sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]

    # build the leaderboard embed
    leaderboardEmbed = lib.discordUtil.makeEmbed(titleTxt=boardTitle, authorName=boardScope,
                                 icon=bbData.winIcon, col=bbData.factionColours["neutral"], desc=boardDesc)

    # add all users to the leaderboard embed with places and values
    externalUser = False
    first = True
    for place in range(min(len(sortedUsers), 10)):
        # handling for global leaderboards and users not in the local guild
        if globalBoard and message.guild.get_member(sortedUsers[place][0]) is None:
            leaderboardEmbed.add_field(value="*" + str(place + 1) + ". " + str(bbGlobals.client.get_user(sortedUsers[place][0])), name=(
                "⭐ " if first else "") + str(sortedUsers[place][1]) + " " + (boardUnit if sortedUsers[place][1] == 1 else boardUnits), inline=False)
            externalUser = True
            if first:
                first = False
        else:
            leaderboardEmbed.add_field(value=str(place + 1) + ". " + message.guild.get_member(sortedUsers[place][0]).mention, name=(
                "⭐ " if first else "") + str(sortedUsers[place][1]) + " " + (boardUnit if sortedUsers[place][1] == 1 else boardUnits), inline=False)
            if first:
                first = False
    # If at least one external use is on the leaderboard, give a key
    if externalUser:
        leaderboardEmbed.set_footer(
            text="An `*` indicates a user that is from another server.")
    # send the embed
    await message.channel.send(embed=leaderboardEmbed)

bbCommands.register("leaderboard", cmd_leaderboard, 0)
dmCommands.register("leaderboard", err_nodm, 0)


async def cmd_hangar(message : discord.Message, args : str, isDM : bool):
    """return a page listing the calling user's items. Administrators may view the hangar of any user.
    can apply to a specified user, or the calling user if none is specified.
    can apply to a type of item (ships, modules, turrets or weapons), or all items if none is specified.
    can apply to a page, or the first page if none is specified.
    Arguments can be given in any order, and must be separated by a single space.

    TODO: try displaying as a discord message rather than embed?
    TODO: add icons for ships and items!?

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the arguments as specified above
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")

    requestedUser = message.author
    item = "all"
    page = 1

    foundUser = False
    foundItem = False
    foundPage = False

    useDummyData = False

    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! I can only take a target user, an item type (ship/weapon/module), and a page number!")
        return

    if args != "":
        argNum = 1
        for arg in argsSplit:
            if arg != "":
                if lib.discordUtil.isUserRef(arg, dcGuild=message.guild):
                    if foundUser:
                        await message.channel.send(":x: I can only take one user!")
                        return
                    else:
                        requestedUser = getMemberByRefOverDB(arg, dcGuild=message.guild)
                        foundUser = True

                elif arg.rstrip("s") in bbConfig.validItemNames:
                    if foundItem:
                        await message.channel.send(":x: I can only take one item type (ship/weapon/module/turret)!")
                        return
                    else:
                        item = arg.rstrip("s")
                        foundItem = True

                elif lib.stringTyping.isInt(arg):
                    if foundPage:
                        await message.channel.send(":x: I can only take one page number!")
                        return
                    else:
                        page = int(arg)
                        foundPage = True
                else:
                    await message.channel.send(":x: " + str(argNum) + lib.stringTyping.getNumExtension(argNum) + " argument invalid! I can only take a target user, an item type (ship/weapon/module/turret), and a page number!")
                    return
                argNum += 1

    if requestedUser is None:
        await message.channel.send(":x: Unrecognised user!")
        return

    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        if not foundUser:
            bbGlobals.usersDB.addUser(requestedUser.id)
        else:
            useDummyData = True

    sendChannel = None
    sendDM = False

    if item == "all":
        if message.author.dm_channel is None:
            await message.author.create_dm()
        if message.author.dm_channel is None:
            sendChannel = message.channel
        else:
            sendChannel = message.author.dm_channel
            sendDM = True
    else:
        sendChannel = message.channel

    if useDummyData:
        if page > 1:
            await message.channel.send(":x: " + ("The requested pilot" if foundUser else "You") + " only " + ("has" if foundUser else "have") + " one page of items. Showing page one:")
            page = 1
        elif page < 1:
            await message.channel.send(":x: Invalid page number. Showing page one:")
            page = 1

        hangarEmbed = lib.discordUtil.makeEmbed(titleTxt="Hangar", desc=requestedUser.mention, col=bbData.factionColours["neutral"], footerTxt="All items" if item == "all" else item.rstrip(
            "s").title() + "s - page " + str(page), thumb=requestedUser.avatar_url_as(size=64))

        hangarEmbed.add_field(name="No Stored Items", value="‎", inline=False)
        await message.channel.send(embed=hangarEmbed)
        return

    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)

        if item == "all":
            maxPerPage = bbConfig.maxItemsPerHangarPageAll
        else:
            maxPerPage = bbConfig.maxItemsPerHangarPageIndividual

        if page < 1:
            await message.channel.send(":x: Invalid page number. Showing page one:")
            page = 1
        else:
            maxPage = requestedBBUser.numInventoryPages(item, maxPerPage)
            if maxPage == 0:
                await message.channel.send(":x: " + ("The requested pilot doesn't" if foundUser else "You don't") + " have any " + ("items" if item == "all" else "of that item") + "!")
                return
            elif page > maxPage:
                await message.channel.send(":x: " + ("The requested pilot" if foundUser else "You") + " only " + ("has " if foundUser else "have ") + str(maxPage) + " page(s) of items. Showing page " + str(maxPage) + ":")
                page = maxPage

        hangarEmbed = lib.discordUtil.makeEmbed(titleTxt="Hangar", desc=requestedUser.mention, col=bbData.factionColours["neutral"], footerTxt=("All item" if item == "all" else item.rstrip(
            "s").title()) + "s - page " + str(page) + "/" + str(requestedBBUser.numInventoryPages(item, maxPerPage)), thumb=requestedUser.avatar_url_as(size=64))
        firstPlace = maxPerPage * (page - 1) + 1

        if item in ["all", "ship"]:
            for shipNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("ship", page, maxPerPage) + 1):
                if shipNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Ships**__", inline=False)
                currentItem = requestedBBUser.inactiveShips[shipNum - 1].item
                currentItemCount = requestedBBUser.inactiveShips.items[currentItem].count
                hangarEmbed.add_field(name=str(shipNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") +
                                      currentItem.getNameAndNick(), value=currentItem.statsStringShort(), inline=False)

        if item in ["all", "weapon"]:
            for weaponNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("weapon", page, maxPerPage) + 1):
                if weaponNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Weapons**__", inline=False)
                currentItem = requestedBBUser.inactiveWeapons[weaponNum - 1].item
                currentItemCount = requestedBBUser.inactiveWeapons.items[currentItem].count
                hangarEmbed.add_field(name=str(weaponNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") +
                                      currentItem.name, value=currentItem.statsStringShort(), inline=False)

        if item in ["all", "module"]:
            for moduleNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("module", page, maxPerPage) + 1):
                if moduleNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Modules**__", inline=False)
                currentItem = requestedBBUser.inactiveModules[moduleNum - 1].item
                currentItemCount = requestedBBUser.inactiveModules.items[currentItem].count
                hangarEmbed.add_field(name=str(moduleNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItem.name,
                                      value=currentItem.statsStringShort(), inline=False)

        if item in ["all", "turret"]:
            for turretNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("turret", page, maxPerPage) + 1):
                if turretNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Turrets**__", inline=False)
                currentItem = requestedBBUser.inactiveTurrets[turretNum - 1].item
                currentItemCount = requestedBBUser.inactiveTurrets.items[currentItem].count
                hangarEmbed.add_field(name=str(turretNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItem.name,
                                      value=currentItem.statsStringShort(), inline=False)

        try:
            await sendChannel.send(embed=hangarEmbed)
            if sendDM:
                await message.add_reaction(bbConfig.dmSentEmoji.sendable)
        except discord.Forbidden:
            await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")

bbCommands.register("hangar", cmd_hangar, 0, aliases=["hanger"], forceKeepArgsCasing=True)
dmCommands.register("hangar", cmd_hangar, 0, aliases=["hanger"], forceKeepArgsCasing=True)


async def cmd_shop(message : discord.Message, args : str, isDM : bool):
    """list the current stock of the bbShop owned by the guild containing the sent message.
    Can specify an item type to list. TODO: Make specified item listings more detailed as in !bb bounties

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string, or one of bbConfig.validItemNames
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.shopDisabled:
        await message.channel.send(":x: This server does not have a shop.")
        return

    item = "all"
    if args.rstrip("s") in bbConfig.validItemNames:
        item = args.rstrip("s")
    elif args != "":
        await message.channel.send(":x: Invalid item type! (ship/weapon/module/turret/all)")
        return

    sendChannel = None
    sendDM = False

    if item == "all":
        if message.author.dm_channel is None:
            await message.author.create_dm()
        if message.author.dm_channel is None:
            sendChannel = message.channel
        else:
            sendChannel = message.author.dm_channel
            sendDM = True
    else:
        sendChannel = message.channel

    requestedShop = bbGlobals.guildsDB.getGuild(message.guild.id).shop
    shopEmbed = lib.discordUtil.makeEmbed(titleTxt="Shop", desc="__" + message.guild.name + "__\n`Current Tech Level: " + str(requestedShop.currentTechLevel) + "`",
                          footerTxt="All items" if item == "all" else (
                              item + "s").title(),
                          thumb=("https://cdn.discordapp.com/icons/" + str(message.guild.id) + "/" + message.guild.icon + ".png?size=64") if message.guild.icon is not None else "")

    if item in ["all", "ship"]:
        for shipNum in range(1, requestedShop.shipsStock.numKeys + 1):
            if shipNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Ships**__", inline=False)

            try:
                currentItem = requestedShop.shipsStock[shipNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested ship '" + requestedShop.shipsStock.keys[shipNum-1].name + "' (index " + str(shipNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.shipsStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in shipsstock KEYS, index " + str(shipNum-1) + ". Expected bbShip, got " + type(requestedShop.shipsStock.keys[shipNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(shipNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.shipsStock.keys[shipNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(shipNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.shipsStock.keys[shipNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.shipsStock.items[currentItem].count
            shopEmbed.add_field(name=str(shipNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.getNameAndNick() + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.getValue())) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    if item in ["all", "weapon"]:
        for weaponNum in range(1, requestedShop.weaponsStock.numKeys + 1):
            if weaponNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Weapons**__", inline=False)

            try:
                currentItem = requestedShop.weaponsStock[weaponNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested weapon '" + requestedShop.weaponsStock.keys[weaponNum-1].name + "' (index " + str(weaponNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.weaponsStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in weaponsstock KEYS, index " + str(weaponNum-1) + ". Expected bbWeapon, got " + type(requestedShop.weaponsStock.keys[weaponNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(weaponNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.weaponsStock.keys[weaponNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(weaponNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.weaponsStock.keys[weaponNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.weaponsStock.items[currentItem].count
            shopEmbed.add_field(name=str(weaponNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.name + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.value)) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    if item in ["all", "module"]:
        for moduleNum in range(1, requestedShop.modulesStock.numKeys + 1):
            if moduleNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Modules**__", inline=False)

            try:
                currentItem = requestedShop.modulesStock[moduleNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested module '" + requestedShop.modulesStock.keys[moduleNum-1].name + "' (index " + str(moduleNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.modulesStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in modulesstock KEYS, index " + str(moduleNum-1) + ". Expected bbModule, got " + type(requestedShop.modulesStock.keys[moduleNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(moduleNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.modulesStock.keys[moduleNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(moduleNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.modulesStock.keys[moduleNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.modulesStock.items[currentItem].count
            shopEmbed.add_field(name=str(moduleNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.name + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.value)) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    if item in ["all", "turret"]:
        for turretNum in range(1, requestedShop.turretsStock.numKeys + 1):
            if turretNum == 1:
                shopEmbed.add_field(
                    name="‎", value="__**Turrets**__", inline=False)

            try:
                currentItem = requestedShop.turretsStock[turretNum - 1].item
            except KeyError:
                try:
                    bbLogger.log("Main", "cmd_shop", "Requested turret '" + requestedShop.turretsStock.keys[turretNum-1].name + "' (index " + str(turretNum-1) + "), which was not found in the shop stock",
                                 category="shop", eventType="UNKWN_KEY")
                except IndexError:
                    break
                except AttributeError as e:
                    keysStr = ""
                    for item in requestedShop.turretsStock.items:
                        keysStr += str(item) + ", "
                    bbLogger.log("Main", "cmd_shop", "Unexpected type in turretsstock KEYS, index " + str(turretNum-1) + ". Expected bbTurret, got " + type(requestedShop.turretsStock.keys[turretNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                 category="shop", eventType="INVTY_KEY_TYPE")
                    shopEmbed.add_field(name=str(turretNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.turretsStock.keys[turretNum-1] + "'",
                                        value="Do not attempt to buy. Could cause issues.", inline=True)
                    continue
                shopEmbed.add_field(name=str(turretNum) + ". **⚠ #INVALID-ITEM# '" + requestedShop.turretsStock.keys[turretNum-1].name + "'",
                                    value="Do not attempt to buy. Could cause issues.", inline=True)
                continue

            currentItemCount = requestedShop.turretsStock.items[currentItem].count
            shopEmbed.add_field(name=str(turretNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.name + "**",
                                value=lib.stringTyping.commaSplitNum(str(currentItem.value)) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    try:
        await sendChannel.send(embed=shopEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return
    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji.sendable)

bbCommands.register("shop", cmd_shop, 0, aliases=["store"])
dmCommands.register("shop", cmd_shop, 0, aliases=["store"])


async def cmd_loadout(message : discord.Message, args : str, isDM : bool):
    """list the requested user's currently equipped items.

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string, or a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedUser = message.author
    useDummyData = False
    userFound = False

    if len(args.split(" ")) > 1:
        await message.channel.send(":x: Too many arguments! I can only take a target user!")
        return

    if args != "":
        requestedUser = getMemberByRefOverDB(args, dcGuild=message.guild)
        if requestedUser is None:
            await message.channel.send(":x: Invalid user requested! Please either ping them, or give their ID!")
            return

    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        if not userFound:
            bbGlobals.usersDB.addUser(requestedUser.id)
        else:
            useDummyData = True

    if useDummyData:
        activeShip = bbShip.fromDict(bbUser.defaultShipLoadoutDict)
        loadoutEmbed = lib.discordUtil.makeEmbed(titleTxt="Loadout", desc=requestedUser.mention, col=bbData.factionColours[activeShip.manufacturer] if activeShip.manufacturer in bbData.factionColours else bbData.factionColours[
                                 "neutral"], thumb=activeShip.icon if activeShip.hasIcon else requestedUser.avatar_url_as(size=64))
        loadoutEmbed.add_field(name="Active Ship:", value=activeShip.name +
                               "\n" + activeShip.statsStringNoItems(), inline=False)

        loadoutEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(
            activeShip.weapons)) + "/" + str(activeShip.getMaxPrimaries()) + ("(+)" if activeShip.getMaxPrimaries(shipUpgradesOnly=True) > activeShip.maxPrimaries else "") + "*", inline=False)
        for weaponNum in range(1, len(activeShip.weapons) + 1):
            loadoutEmbed.add_field(name=str(weaponNum) + ". " + (activeShip.weapons[weaponNum - 1].emoji.sendable + " " if activeShip.weapons[weaponNum - 1].hasEmoji else "") + activeShip.weapons[weaponNum - 1].name, value=activeShip.weapons[weaponNum - 1].statsStringShort(), inline=True)

        loadoutEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(
            activeShip.modules)) + "/" + str(activeShip.getMaxModules()) + ("(+)" if activeShip.getMaxModules(shipUpgradesOnly=True) > activeShip.maxModules else "") + "*", inline=False)
        for moduleNum in range(1, len(activeShip.modules) + 1):
            loadoutEmbed.add_field(name=str(moduleNum) + ". " + (activeShip.modules[moduleNum - 1].emoji.sendable + " " if activeShip.modules[moduleNum - 1].hasEmoji else "") + activeShip.modules[moduleNum - 1].name, value=activeShip.modules[moduleNum - 1].statsStringShort(), inline=True)

        loadoutEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(
            activeShip.turrets)) + "/" + str(activeShip.getMaxTurrets()) + ("(+)" if activeShip.getMaxTurrets(shipUpgradesOnly=True) > activeShip.maxTurrets else "") + "*", inline=False)
        for turretNum in range(1, len(activeShip.turrets) + 1):
            loadoutEmbed.add_field(name=str(turretNum) + ". " + (activeShip.turrets[turretNum - 1].emoji.sendable + " " if activeShip.turrets[turretNum - 1].hasEmoji else "") + activeShip.turrets[turretNum - 1].name, value=activeShip.turrets[turretNum - 1].statsStringShort(), inline=True)

        await message.channel.send(embed=loadoutEmbed)
        return

    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
        activeShip = requestedBBUser.activeShip
        loadoutEmbed = lib.discordUtil.makeEmbed(titleTxt="Loadout", desc=requestedUser.mention, col=bbData.factionColours[activeShip.manufacturer] if activeShip.manufacturer in bbData.factionColours else bbData.factionColours[
                                 "neutral"], thumb=activeShip.icon if activeShip.hasIcon else requestedUser.avatar_url_as(size=64))

        if activeShip is None:
            loadoutEmbed.add_field(name="Active Ship:",
                                   value="None", inline=False)
        else:
            loadoutEmbed.add_field(name="Active Ship:", value=activeShip.getNameAndNick(
            ) + "\n" + activeShip.statsStringNoItems(), inline=False)

            if activeShip.getMaxPrimaries() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(
                    activeShip.weapons)) + "/" + str(activeShip.getMaxPrimaries()) + ("(+)" if activeShip.getMaxPrimaries(shipUpgradesOnly=True) > activeShip.maxPrimaries else "") + "*", inline=False)
                for weaponNum in range(1, len(activeShip.weapons) + 1):
                    loadoutEmbed.add_field(name=str(weaponNum) + ". " + (activeShip.weapons[weaponNum - 1].emoji.sendable + " " if activeShip.weapons[weaponNum - 1].hasEmoji else "") + activeShip.weapons[weaponNum - 1].name, value=activeShip.weapons[weaponNum - 1].statsStringShort(), inline=True)

            if activeShip.getMaxModules() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(
                    activeShip.modules)) + "/" + str(activeShip.getMaxModules()) + ("(+)" if activeShip.getMaxModules(shipUpgradesOnly=True) > activeShip.maxModules else "") + "*", inline=False)
                for moduleNum in range(1, len(activeShip.modules) + 1):
                    loadoutEmbed.add_field(name=str(moduleNum) + ". " + (activeShip.modules[moduleNum - 1].emoji.sendable + " " if activeShip.modules[moduleNum - 1].hasEmoji else "") + activeShip.modules[moduleNum - 1].name, value=activeShip.modules[moduleNum - 1].statsStringShort(), inline=True)

            if activeShip.getMaxTurrets() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(
                    activeShip.turrets)) + "/" + str(activeShip.getMaxTurrets()) + ("(+)" if activeShip.getMaxTurrets(shipUpgradesOnly=True) > activeShip.maxTurrets else "") + "*", inline=False)
                for turretNum in range(1, len(activeShip.turrets) + 1):
                    loadoutEmbed.add_field(name=str(turretNum) + ". " + (activeShip.turrets[turretNum - 1].emoji.sendable + " " if activeShip.turrets[turretNum - 1].hasEmoji else "") + activeShip.turrets[turretNum - 1].name, value=activeShip.turrets[turretNum - 1].statsStringShort(), inline=True)

        await message.channel.send(embed=loadoutEmbed)

bbCommands.register("loadout", cmd_loadout, 0, forceKeepArgsCasing=True)
dmCommands.register("loadout", cmd_loadout, 0, forceKeepArgsCasing=True)


async def cmd_shop_buy(message : discord.Message, args : str, isDM : bool):
    """Buy the item of the given item type, at the given index, from the guild's shop.
    if "transfer" is specified, the new ship's items are unequipped, and the old ship's items attempt to fill the new ship.
    any items left unequipped are added to the user's inactive items lists.
    if "sell" is specified, the user's old activeShip is stripped of items and sold to the shop.
    "transfer" and "sell" are only valid when buying a ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number, and optionally "transfer", and optionally "sell" separated by a single space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.shopDisabled:
        await message.channel.send(":x: This server does not have a shop.")
        return
        
    requestedShop = requestedBBGuild.shop

    # verify this is the calling user's home guild. If no home guild is set, transfer here.
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if not requestedBBUser.hasHomeGuild():
        await requestedBBUser.transferGuild(message.guild)
        await message.channel.send(":airplane_arriving: Your home guild has been set.")
    elif requestedBBUser.homeGuildID != message.guild.id:
        await message.channel.send(":x: This command can only be used from your home guild!")
        return

    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "shop`")
        return
    if len(argsSplit) > 4:
        await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `transfer` and/or `sell` when buying a ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    itemNum = argsSplit[1]
    requestedShop = bbGlobals.guildsDB.getGuild(message.guild.id).shop
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)
    shopItemStock = requestedShop.getStockByName(item)
    if itemNum > shopItemStock.numKeys:
        if shopItemStock.numKeys == 0:
            await message.channel.send(":x: This shop has no " + item + "s in stock!")
        else:
            await message.channel.send(":x: Invalid item number! This shop has " + str(shopItemStock.numKeys) + " " + item + "(s).")
        return

    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    transferItems = False
    sellOldShip = False
    if len(argsSplit) > 2:
        for arg in argsSplit[2:]:
            if arg == "transfer":
                if transferItems:
                    await message.channel.send(":x: Invalid argument! Please only specify `transfer` once!")
                    return
                if item != "ship":
                    await message.channel.send(":x: `transfer` can only be used when buying a ship!")
                    return
                transferItems = True
            elif arg == "sell":
                if sellOldShip:
                    await message.channel.send(":x: Invalid argument! Please only specify `sell` once!")
                    return
                if item != "ship":
                    await message.channel.send(":x: `sell` can only be used when buying a ship!")
                    return
                sellOldShip = True
            else:
                await message.channel.send(":x: Invalid argument! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `transfer` and/or `sell` when buying a ship.")
                return

    requestedItem = shopItemStock[itemNum - 1].item

    if item == "ship":
        newShipValue = requestedItem.getValue()
        activeShip = requestedBBUser.activeShip

        # Check the item can be afforded
        if (not sellOldShip and not requestedShop.userCanAffordItemObj(requestedBBUser, requestedItem)) or \
                (sellOldShip and not requestedShop.amountCanAffordShipObj(requestedBBUser.credits + requestedBBUser.activeShip.getValue(shipUpgradesOnly=transferItems), requestedItem)):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedItem.getValue()) + ")")
            return

        requestedBBUser.inactiveShips.addItem(requestedItem)

        if transferItems:
            requestedBBUser.unequipAll(requestedItem)
            activeShip.transferItemsTo(requestedItem)
            requestedBBUser.unequipAll(activeShip)

        if sellOldShip:
            # TODO: move to a separate sellActiveShip function
            oldShipValue = activeShip.getValue(shipUpgradesOnly=transferItems)
            requestedBBUser.credits += oldShipValue
            shopItemStock.addItem(activeShip)
        else:
            oldShipValue = None

        requestedBBUser.equipShipObj(requestedItem, noSaveActive=sellOldShip)
        requestedBBUser.credits -= newShipValue
        shopItemStock.removeItem(requestedItem)

        outStr = ":moneybag: Congratulations on your new **" + requestedItem.name + "**!"
        if sellOldShip:
            outStr += "\nYou received **" + \
                str(oldShipValue) + " credits** for your old **" + \
                str(activeShip.name) + "**."
        else:
            outStr += " Your old **" + activeShip.name + "** can be found in the hangar."
        if transferItems:
            outStr += "\nItems thay could not fit in your new ship can be found in the hangar."
        outStr += "\n\nYour balance is now: **" + \
            str(requestedBBUser.credits) + " credits**."

        await message.channel.send(outStr)

    elif item in ["weapon", "module", "turret"]:
        if not requestedShop.userCanAffordItemObj(requestedBBUser, requestedItem):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedItem.value) + ")")
            return

        requestedBBUser.credits -= requestedItem.value
        requestedBBUser.getInactivesByName(item).addItem(requestedItem)
        shopItemStock.removeItem(requestedItem)

        await message.channel.send(":moneybag: Congratulations on your new **" + requestedItem.name + "**! \n\nYour balance is now: **" + str(requestedBBUser.credits) + " credits**.")
    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("buy", cmd_shop_buy, 0)
dmCommands.register("buy", err_nodm, 0)


async def cmd_shop_sell(message : discord.Message, args : str, isDM : bool):
    """Sell the item of the given item type, at the given index, from the user's inactive items, to the guild's shop.
    if "clear" is specified, the ship's items are unequipped before selling.
    "clear" is only valid when selling a ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number, and optionally "clear", separated by a single space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.shopDisabled:
        await message.channel.send(":x: This server does not have a shop.")
        return
        
    requestedShop = requestedBBGuild.shop

    # verify this is the calling user's home guild. If no home guild is set, transfer here.
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if not requestedBBUser.hasHomeGuild():
        await requestedBBUser.transferGuild(message.guild)
        await message.channel.send(":airplane_arriving: Your home guild has been set.")
    elif requestedBBUser.homeGuildID != message.guild.id:
        await message.channel.send(":x: This command can only be used from your home guild!")
        return
        
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar`")
        return
    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `clear` when selling a ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    itemNum = argsSplit[1]
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)

    userItemInactives = requestedBBUser.getInactivesByName(item)
    if itemNum > userItemInactives.numKeys:
        await message.channel.send(":x: Invalid item number! You have " + str(userItemInactives.numKeys) + " " + item + "s.")
        return
    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    clearItems = False
    if len(argsSplit) == 3:
        if argsSplit[2] == "clear":
            if item != "ship":
                await message.channel.send(":x: `clear` can only be used when selling a ship!")
                return
            clearItems = True
        else:
            await message.channel.send(":x: Invalid argument! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `clear` when selling a ship.")
            return

    requestedShop = bbGlobals.guildsDB.getGuild(message.guild.id).shop
    shopItemStock = requestedShop.getStockByName(item)
    requestedItem = userItemInactives[itemNum - 1].item

    if item == "ship":
        if clearItems:
            requestedBBUser.unequipAll(requestedItem)

        requestedBBUser.credits += requestedItem.getValue()
        userItemInactives.removeItem(requestedItem)
        shopItemStock.addItem(requestedItem)

        outStr = ":moneybag: You sold your **" + requestedItem.getNameOrNick() + \
            "** for **" + str(requestedItem.getValue()) + " credits**!"
        if clearItems:
            outStr += "\nItems removed from the ship can be found in the hangar."
        await message.channel.send(outStr)

    elif item in ["weapon", "module", "turret"]:
        requestedBBUser.credits += requestedItem.getValue()
        userItemInactives.removeItem(requestedItem)

        if requestedItem is None:
            raise ValueError("selling NoneType Item")
        shopItemStock.addItem(requestedItem)

        await message.channel.send(":moneybag: You sold your **" + requestedItem.name + "** for **" + str(requestedItem.getValue()) + " credits**!")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("sell", cmd_shop_sell, 0)
dmCommands.register("sell", err_nodm, 0)


async def cmd_equip(message : discord.Message, args : str, isDM : bool):
    """Equip the item of the given item type, at the given index, from the user's inactive items.
    if "transfer" is specified, the new ship's items are cleared, and the old ship's items attempt to fill new ship.
    "transfer" is only valid when equipping a ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number, and optionally "transfer", separated by a single space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar`")
        return
    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `transfer` when equipping a ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)

    itemNum = argsSplit[1]
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)

    userItemInactives = requestedBBUser.getInactivesByName(item)
    if itemNum > userItemInactives.numKeys:
        await message.channel.send(":x: Invalid item number! You have " + str(userItemInactives.numKeys) + " " + item + "s.")
        return
    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    transferItems = False
    if len(argsSplit) == 3:
        if argsSplit[2] == "transfer":
            if item != "ship":
                await message.channel.send(":x: `transfer` can only be used when equipping a ship!")
                return
            transferItems = True
        else:
            await message.channel.send(":x: Invalid argument! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `transfer` when equipping a ship.")
            return

    requestedItem = userItemInactives[itemNum - 1].item

    if item == "ship":
        activeShip = requestedBBUser.activeShip
        if transferItems:
            requestedBBUser.unequipAll(requestedItem)
            requestedBBUser.activeShip.transferItemsTo(requestedItem)
            requestedBBUser.unequipAll(activeShip)

        requestedBBUser.equipShipObj(requestedItem)

        outStr = ":rocket: You switched to the **" + requestedItem.getNameOrNick() + \
            "**."
        if transferItems:
            outStr += "\nItems thay could not fit in your new ship can be found in the hangar."
        await message.channel.send(outStr)

    elif item == "weapon":
        if not requestedBBUser.activeShip.canEquipMoreWeapons():
            await message.channel.send(":x: Your active ship does not have any free weapon slots!")
            return

        requestedBBUser.activeShip.equipWeapon(requestedItem)
        requestedBBUser.inactiveWeapons.removeItem(requestedItem)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    elif item == "module":
        if not requestedBBUser.activeShip.canEquipMoreModules():
            await message.channel.send(":x: Your active ship does not have any free module slots!")
            return

        if not requestedBBUser.activeShip.canEquipModuleType(requestedItem.getType()):
            await message.channel.send(":x: You already have the max of this type of module equipped!")
            return

        requestedBBUser.activeShip.equipModule(requestedItem)
        requestedBBUser.inactiveModules.removeItem(requestedItem)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    elif item == "turret":
        if not requestedBBUser.activeShip.canEquipMoreTurrets():
            await message.channel.send(":x: Your active ship does not have any free turret slots!")
            return

        requestedBBUser.activeShip.equipTurret(requestedItem)
        requestedBBUser.inactiveTurrets.removeItem(requestedItem)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("equip", cmd_equip, 0)
dmCommands.register("equip", cmd_equip, 0)


async def cmd_unequip(message : discord.Message, args : str, isDM : bool):
    """Unequip the item of the given item type, at the given index, from the user's active ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing either "all", or (an item type and either an index number or "all", separated by a single space)
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    unequipAllItems = len(argsSplit) > 0 and argsSplit[0] == "all"

    if not unequipAllItems and len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (all/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar` or `all`.")
        return
    if len(argsSplit) > 2:
        await message.channel.send(":x: Too many arguments! Please only give an item type (all/weapon/module/turret), an item number or `all`.")
        return

    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)

    if unequipAllItems:
        requestedBBUser.unequipAll(requestedBBUser.activeShip)

        await message.channel.send(":wrench: You unequipped **all items** from your ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: weapon, module or turret.")
        return
    if item == "ship":
        await message.channel.send(":x: You can't go without a ship! Instead, switch to another one.")
        return

    unequipAll = argsSplit[1] == "all"
    if not unequipAll:
        itemNum = argsSplit[1]
        if not lib.stringTyping.isInt(itemNum):
            await message.channel.send(":x: Invalid item number!")
            return
        itemNum = int(itemNum)
        if itemNum > len(requestedBBUser.activeShip.getActivesByName(item)):
            await message.channel.send(":x: Invalid item number! Your ship has " + str(len(requestedBBUser.activeShip.getActivesByName(item))) + " " + item + "s.")
            return
        if itemNum < 1:
            await message.channel.send(":x: Invalid item number! Must be at least 1.")
            return
    else:
        itemNum = None

    if item == "weapon":
        if not requestedBBUser.activeShip.hasWeaponsEquipped():
            await message.channel.send(":x: Your active ship does not have any weapons equipped!")
            return
        if unequipAll:
            for weapon in requestedBBUser.activeShip.weapons:
                requestedBBUser.inactiveWeapons.addItem(weapon)
                requestedBBUser.activeShip.unequipWeaponObj(weapon)

            await message.channel.send(":wrench: You unequipped all **weapons**.")
        else:
            requestedItem = requestedBBUser.activeShip.weapons[itemNum - 1]
            requestedBBUser.inactiveWeapons.addItem(requestedItem)
            requestedBBUser.activeShip.unequipWeaponIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    elif item == "module":
        if not requestedBBUser.activeShip.hasModulesEquipped():
            await message.channel.send(":x: Your active ship does not have any modules equipped!")
            return
        if unequipAll:
            for module in requestedBBUser.activeShip.modules:
                requestedBBUser.inactiveModules.addItem(module)
                requestedBBUser.activeShip.unequipModuleObj(module)

            await message.channel.send(":wrench: You unequipped all **modules**.")
        else:
            requestedItem = requestedBBUser.activeShip.modules[itemNum - 1]
            requestedBBUser.inactiveModules.addItem(requestedItem)
            requestedBBUser.activeShip.unequipModuleIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    elif item == "turret":
        if not requestedBBUser.activeShip.hasTurretsEquipped():
            await message.channel.send(":x: Your active ship does not have any turrets equipped!")
            return
        if unequipAll:
            for turret in requestedBBUser.activeShip.turrets:
                requestedBBUser.inactiveTurrets.addItem(turret)
                requestedBBUser.activeShip.unequipTurretObj(turret)

            await message.channel.send(":wrench: You unequipped all **turrets**.")
        else:
            requestedItem = requestedBBUser.activeShip.turrets[itemNum - 1]
            requestedBBUser.inactiveTurrets.addItem(requestedItem)
            requestedBBUser.activeShip.unequipTurretIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("unequip", cmd_unequip, 0)
dmCommands.register("unequip", cmd_unequip, 0)


async def cmd_nameship(message : discord.Message, args : str, isDM : bool):
    """Set the nickname of the active ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the new nickname.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if bbGlobals.usersDB.userIDExists(message.author.id):
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        requestedBBUser = bbGlobals.usersDB.addUser(message.author.id)

    if requestedBBUser.activeShip is None:
        await message.channel.send(":x: You do not have a ship equipped!")
        return

    if args == "":
        await message.channel.send(":x: Not enough arguments. Please give the new nickname!")
        return

    if (message.author.id not in bbConfig.developers and len(args) > bbConfig.maxShipNickLength) or len(args) > bbConfig.maxDevShipNickLength:
        await message.channel.send(":x: Nicknames must be " + str(bbConfig.maxShipNickLength) + " characters or less!")
        return

    requestedBBUser.activeShip.changeNickname(args)
    await message.channel.send(":pencil: You named your " + requestedBBUser.activeShip.name + ": **" + args + "**.")

bbCommands.register("nameship", cmd_nameship, 0, forceKeepArgsCasing=True)
dmCommands.register("nameship", cmd_nameship, 0, forceKeepArgsCasing=True)


async def cmd_unnameship(message : discord.Message, args : str, isDM : bool):
    """Remove the nickname of the active ship.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if bbGlobals.usersDB.userIDExists(message.author.id):
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        requestedBBUser = bbGlobals.usersDB.addUser(message.author.id)

    if requestedBBUser.activeShip is None:
        await message.channel.send(":x: You do not have a ship equipped!")
        return

    if not requestedBBUser.activeShip.hasNickname:
        await message.channel.send(":x: Your active ship does not have a nickname!")
        return

    requestedBBUser.activeShip.removeNickname()
    await message.channel.send(":pencil: You reset your **" + requestedBBUser.activeShip.name + "**'s nickname.")

bbCommands.register("unnameship", cmd_unnameship, 0)
dmCommands.register("unnameship", cmd_unnameship, 0)


async def cmd_pay(message : discord.Message, args : str, isDM : bool):
    """Pay a givne user the given number of credits from your balance.
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a target user and an amount!")
        return

    if not lib.stringTyping.isInt(argsSplit[1]):
        await message.channel.send(":x: Invalid amount!")
        return

    requestedUser = getMemberByRefOverDB(argsSplit[0], dcGuild=message.guild)
    if requestedUser is None:
        await message.channel.send(":x: Unknown user!")
        return

    amount = int(argsSplit[1])
    if amount < 1:
        await message.channel.send(":x: You have to pay at least 1 credit!")
        return

    if bbGlobals.usersDB.userIDExists(message.author.id):
        sourceBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        sourceBBUser = bbGlobals.usersDB.addUser(message.author.id)

    if not sourceBBUser.credits >= amount:
        await message.channel.send(":x: You don't have that many credits!")
        return

    if bbGlobals.usersDB.userIDExists(requestedUser.id):
        targetBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
    else:
        targetBBUser = bbGlobals.usersDB.addUser(requestedUser.id)

    sourceBBUser.credits -= amount
    targetBBUser.credits += amount

    await message.channel.send(":moneybag: You paid " + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + " **" + str(amount) + "** credits!")

bbCommands.register("pay", cmd_pay, 0, forceKeepArgsCasing=True)
dmCommands.register("pay", cmd_pay, 0, forceKeepArgsCasing=True)


async def cmd_notify(message : discord.Message, args : str, isDM : bool):
    """⚠ WARNING: MARKED FOR CHANGE ⚠
    The following function is provisional and marked as planned for overhaul.
    Details: Notifications for shop items have yet to be implemented.

    Allow a user to subscribe and unsubscribe from pings when certain events occur.
    Currently only new bounty notifications are implemented, but more are planned.
    For example, a ping when a requested item is in stock in the guild's shop.

    :param discord.Message message: the discord message calling the command
    :param str args: the notification type (e.g ship), possibly followed by a specific notification (e.g groza mk II), separated by a single space.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if not message.guild.me.guild_permissions.manage_roles:
        await message.channel.send(":x: I do not have the 'Manage Roles' permission in this server! Please contact an admin :robot:")
        return
    if args == "":
        await message.channel.send(":x: Please name what you would like to be notified for! E.g `" + bbConfig.commandPrefix + "notify bounties`")
        return

    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)

    argsSplit = args.split(" ")
    alertsToToggle = getAlertIDFromHeirarchicalAliases(argsSplit)

    if alertsToToggle[0] == "ERR":
        await message.channel.send(alertsToToggle[1])
        return

    for alertID in alertsToToggle:
        alertType = UserAlerts.userAlertsIDsTypes[alertID]
        try:
            alertNewState = await requestedBBUser.toggleAlertType(alertType, message.guild, requestedBBGuild, message.author)
            await message.channel.send(":white_check_mark: You have " + ("subscribed to" if alertNewState else "unsubscribed from") + " " + UserAlerts.userAlertsTypesNames[alertType] + " notifications.")
        except discord.Forbidden:
            await message.channel.send(":woozy_face: I don't have permission to do that! Please ensure the requested role is beneath the BountyBot role.")
        except discord.HTTPException:
            await message.channel.send(":woozy_face: Something went wrong! Please contact an admin or try again later.")
        except ValueError:
            await message.channel.send(":x: This server does not have a role for " + UserAlerts.userAlertsTypesNames[alertType] + " notifications. :robot:")
        except client_exceptions.ClientOSError:
            await message.channel.send(":thinking: Whoops! A connection error occurred, and the error has been logged. Could you try that again please?")
            bbLogger.log("main", "cmd_notify", "aiohttp.client_exceptions.ClientOSError occurred when attempting to grant " + message.author.name + "#" + str(message.author.id) + " alert " + alertID + "in guild " + message.guild.name + "#" + str(message.guild.id) + ".", category="userAlerts", eventType="ClientOSError", trace=traceback.format_exc())

bbCommands.register("notify", cmd_notify, 0)
dmCommands.register("notify", err_nodm, 0)


async def cmd_total_value(message : discord.Message, args : str, isDM : bool):
    """⚠ WARNING: MARKED FOR CHANGE ⚠
    The following function is provisional and marked as planned for overhaul.
    Details: The command output is finalised. However, the inner workings of the command are to be replaced with attribute getters.
    It is inefficient to calculate total value measurements on every call, so current totals should be cached in object attributes whenever modified.

    print the total value of the specified user, use the calling user if no user is specified.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention or ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # If no user is specified, send the balance of the calling user
    if args == "":
        if not bbGlobals.usersDB.userIDExists(message.author.id):
            bbGlobals.usersDB.addUser(message.author.id)
        await message.channel.send(":moneybag: **" + message.author.display_name + "**, your items and balance are worth a total of **" + str(bbGlobals.usersDB.getUser(message.author.id).getStatByName("value")) + " Credits**.")

    # If a user is specified
    else:
        # Verify the passed user tag
        requestedUser = getMemberByRefOverDB(args, dcGuild=message.guild)
        if requestedUser is None:
            await message.channel.send(":x: Unknown user!")
            return
        # ensure that the user is in the users database
        if not bbGlobals.usersDB.userIDExists(requestedUser.id):
            bbGlobals.usersDB.addUser(requestedUser.id)
        # send the user's balance
        await message.channel.send(":moneybag: **" + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "**'s items and balance have a total value of **" + str(bbGlobals.usersDB.getUser(requestedUser.id).getStatByName("value")) + " Credits**.")

bbCommands.register("total-value", cmd_total_value, 0, forceKeepArgsCasing=True)
dmCommands.register("total-value", cmd_total_value, 0, forceKeepArgsCasing=True)


async def cmd_duel(message : discord.Message, args : str, isDM : bool):
    """⚠ WARNING: MARKED FOR CHANGE ⚠
    The following function is provisional and marked as planned for overhaul.
    Details: Overhaul is part-way complete, with a few fighting algorithm provided in bbObjects.items.battles. However, printing the fight details is yet to be implemented.
    This is planned to be done using simple message editing-based animation of player ships and progress bars for health etc.
    This command is functional for now, but the output is subject to change.

    Challenge another player to a duel, with an amount of credits as the stakes.
    The winning user is given stakes credits, the loser has stakes credits taken away.
    give 'challenge' to create a new duel request.
    give 'cancel' to cancel an existing duel request.
    give 'accept' to accept another user's duel request targetted at you.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the action (challenge/cancel/accept), a target user (mention or ID), and the stakes (int amount of credits). stakes are only required when "challenge" is specified.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) == 0:
        await message.channel.send(":x: Please provide an action (`challenge`/`cancel`/`accept`/`reject or decline`), a user, and the stakes (an amount of credits)!")
        return
    action = argsSplit[0]
    if action not in ["challenge", "cancel", "accept", "reject", "decline"]:
        await message.channel.send(":x: Invalid action! please choose from `challenge`, `cancel`, `reject/decline` or `accept`.")
        return
    if action == "challenge":
        if len(argsSplit) < 3:
            await message.channel.send(":x: Please provide a user and the stakes (an amount of credits)!")
            return
    else:
        if len(argsSplit) < 2:
            await message.channel.send(":x: Please provide a user!")
            return
    requestedUser = getMemberByRefOverDB(argsSplit[1], dcGuild=message.guild)
    if requestedUser is None:
        await message.channel.send(":x: User not found!")
        return
    if requestedUser.id == message.author.id:
        await message.channel.send(":x: You can't challenge yourself!")
        return
    if action == "challenge" and (not lib.stringTyping.isInt(argsSplit[2]) or int(argsSplit[2]) < 0):
        await message.channel.send(":x: Invalid stakes (amount of credits)!")
        return

    sourceBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    targetBBUser = bbGlobals.usersDB.getOrAddID(requestedUser.id)

    if action == "challenge":
        stakes = int(argsSplit[2])
        if sourceBBUser.hasDuelChallengeFor(targetBBUser):
            await message.channel.send(":x: You already have a duel challenge pending for " + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "! To make a new one, cancel it first. (see `" + bbConfig.commandPrefix + "help duel`)")
            return

        try:
            newDuelReq = DuelRequest.DuelRequest(
                sourceBBUser, targetBBUser, stakes, None, bbGlobals.guildsDB.getGuild(message.guild.id))
            duelTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(
                bbConfig.duelReqExpiryTime), expiryFunction=expireAndAnnounceDuelReq, expiryFunctionArgs={"duelReq": newDuelReq})
            newDuelReq.duelTimeoutTask = duelTT
            bbGlobals.duelRequestTTDB.scheduleTask(duelTT)
            sourceBBUser.addDuelChallenge(newDuelReq)
        except KeyError:
            await message.channel.send(":x: User not found! Did they leave the server?")
            return
        except Exception:
            await message.channel.send(":woozy_face: An unexpected error occurred! Tri, what did you do...")
            return

        expiryTimesSplit = duelTT.expiryTime.strftime("%d %B %H %M").split(" ")
        duelExpiryTimeString = "This duel request will expire on the **" + expiryTimesSplit[0].lstrip('0') + lib.stringTyping.getNumExtension(int(
            expiryTimesSplit[0])) + "** of **" + expiryTimesSplit[1] + "**, at **" + expiryTimesSplit[2] + ":" + expiryTimesSplit[3] + "** UTC."

        sentMsgs = []

        if message.guild.get_member(requestedUser.id) is None:
            targetUserDCGuild = lib.discordUtil.findBBUserDCGuild(targetBBUser)
            if targetUserDCGuild is None:
                await message.channel.send(":x: User not found! Did they leave the server?")
                return
            else:
                targetUserBBGuild = bbGlobals.guildsDB.getGuild(targetUserDCGuild.id)
                if targetUserBBGuild.hasPlayChannel():
                    targetUserNameOrTag = IDAlertedUserMentionOrName(
                        "duels_challenge_incoming_new", dcGuild=targetUserDCGuild, bbGuild=targetUserBBGuild, dcUser=requestedUser, bbUser=targetBBUser)
                    sentMsgs.append(await targetUserBBGuild.getPlayChannel().send(":crossed_swords: **" + str(message.author) + "** challenged " + targetUserNameOrTag + " to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString))
            sentMsgs.append(await message.channel.send(":crossed_swords: " + message.author.mention + " challenged **" + str(requestedUser) + "** to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString))
        else:
            targetUserNameOrTag = IDAlertedUserMentionOrName(
                "duels_challenge_incoming_new", dcGuild=message.guild, dcUser=requestedUser, bbUser=targetBBUser)
            sentMsgs.append(await message.channel.send(":crossed_swords: " + message.author.mention + " challenged " + targetUserNameOrTag + " to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString))

        for msg in sentMsgs:
            menuTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.duelChallengeMenuDefaultTimeout), expiryFunction=ReactionMenu.removeEmbedAndOptions, expiryFunctionArgs=msg.id)
            bbGlobals.reactionMenusTTDB.scheduleTask(menuTT)
            newMenu = ReactionDuelChallengeMenu.ReactionDuelChallengeMenu(msg, newDuelReq, timeout=menuTT)
            newDuelReq.menus.append(newMenu)
            await newMenu.updateMessage()
            bbGlobals.reactionMenusDB[msg.id] = newMenu


    elif action == "cancel":
        if not sourceBBUser.hasDuelChallengeFor(targetBBUser):
            await message.channel.send(":x: You do not have an active duel challenge for this user! Did it already expire?")
            return

        if message.guild.get_member(requestedUser.id) is None:
            await message.channel.send(":white_check_mark: You have cancelled your duel challenge for **" + str(requestedUser) + "**.")
            targetUserGuild = lib.discordUtil.findBBUserDCGuild(targetBBUser)
            if targetUserGuild is not None:
                targetUserBBGuild = bbGlobals.guildsDB.getGuild(targetUserGuild.id)
                if targetUserBBGuild.hasPlayChannel() and \
                        targetBBUser.isAlertedForID("duels_challenge_incoming_cancel", targetUserGuild, targetUserBBGuild, targetUserGuild.get_member(targetBBUser.id)):
                    await targetUserBBGuild.getPlayChannel().send(":shield: " + requestedUser.mention + ", " + str(message.author) + " has cancelled their duel challenge.")
        else:
            if targetBBUser.isAlertedForID("duels_challenge_incoming_cancel", message.guild, bbGlobals.guildsDB.getGuild(message.guild.id), message.guild.get_member(targetBBUser.id)):
                await message.channel.send(":white_check_mark: You have cancelled your duel challenge for " + requestedUser.mention + ".")
            else:
                await message.channel.send(":white_check_mark: You have cancelled your duel challenge for **" + str(requestedUser) + "**.")

        # IDAlertedUserMentionOrName(alertType, dcUser=None, bbUser=None, bbGuild=None, dcGuild=None)
        for menu in sourceBBUser.duelRequests[targetBBUser].menus:
            await menu.delete()
        await sourceBBUser.duelRequests[targetBBUser].duelTimeoutTask.forceExpire(callExpiryFunc=False)
        sourceBBUser.removeDuelChallengeTarget(targetBBUser)

    elif action in ["reject", "decline"]:
        if not targetBBUser.hasDuelChallengeFor(sourceBBUser):
            await message.channel.send(":x: This user does not have an active duel challenge for you! Did it expire?")
            return

        duelReq = targetBBUser.duelRequests[sourceBBUser]
        await DuelRequest.rejectDuel(duelReq, message, requestedUser, message.author)

    elif action == "accept":
        if not targetBBUser.hasDuelChallengeFor(sourceBBUser):
            await message.channel.send(":x: This user does not have an active duel challenge for you! Did it expire?")
            return

        requestedDuel = targetBBUser.duelRequests[sourceBBUser]

        if sourceBBUser.credits < requestedDuel.stakes:
            await message.channel.send(":x: You do not have enough credits to accept this duel request! (" + str(requestedDuel.stakes) + ")")
            return
        if targetBBUser.credits < requestedDuel.stakes:
            await message.channel.send(":x:" + str(requestedUser) + " does not have enough credits to fight this duel! (" + str(requestedDuel.stakes) + ")")
            return

        await DuelRequest.fightDuel(message.author, requestedUser, requestedDuel, message)

bbCommands.register("duel", cmd_duel, 0, forceKeepArgsCasing=True)
dmCommands.register("duel", err_nodm, 0)


async def cmd_source(message : discord.Message, args : str, isDM : bool):
    """Print a short message with information about BountyBot's source code.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    srcEmbed = lib.discordUtil.makeEmbed(authorName="BB Source Code", desc="I am written using the rewrite branch of discord's python API.\n",
                         col=discord.Colour.purple(), footerTxt="BountyBot Source", icon="https://image.flaticon.com/icons/png/512/25/25231.png")
    srcEmbed.add_field(name="__GitHub Repository__",
                       value="My source code is public, and open to community contribution.\n[Click here](https://github.com/Trimatix/GOF2BountyBot/) to view my GitHub repo - please note, the project's readme file has not been written yet!", inline=False)
    srcEmbed.add_field(name="__Upcoming Features__",
                       value="To see a list of upcoming goodies, take a look at the [todo list](https://github.com/Trimatix/GOF2BountyBot/projects/1).\nIf you would like to make a feature request or suggestion, please ping or DM `Trimatix#2244`.\nIf you would like to help contribute to BountyBot, the todo list is a solid place to start!", inline=False)
    srcEmbed.add_field(name="__Special Thanks__", value=" • **DeepSilver FishLabs**, for building the fantastic game franchise that this bot is dedicated to. I don't own any Galaxy on Fire assets intellectual property, nor rights to any assets the bot references.\n • **The BountyBot testing team** who have all been lovely and supportive since the beginning, and who will *always* find a way to break things ;)\n • **NovahKiin22**, for his upcoming major feature release, along with minor bug fixes and *brilliant* insight throughout development\n • **Poisonwasp**, for another minor bug fix, but mostly for his continuous support\n • **You!** The community is what makes developing this bot so fun :)", inline=False)
    await message.channel.send(embed=srcEmbed)

bbCommands.register("source", cmd_source, 0)
dmCommands.register("source", cmd_source, 0)


async def cmd_poll(message : discord.Message, args : str, isDM : bool):
    """Run a reaction-based poll, allowing users to choose between several named options.
    Users may not create more than one poll at a time, anywhere.
    Option reactions must be either unicode, or custom to the server where the poll is being created.

    args must contain a comma-separated list of emoji-option pairs, where each pair is separated with a space.
    For example: '0️⃣ option a, 1️⃣ my second option, 2️⃣ three' will produce three options:
    - 'option a'         which participants vote for by adding the 0️⃣ reaction
    - 'my second option' which participants vote for by adding the 1️⃣ reaction
    - 'three'            which participants vote for by adding the 2️⃣ reaction

    args may also optionally contain the following keyword arguments, given as argname=value
    - target         : A role or user to restrict participants by. Must be a user or role mention, not ID.
    - multiplechoice : Whether or not to allow participants to vote for multiple poll options. Must be true or false.
    - days           : The number of days that the poll should run for. Must be at least one, or unspecified.
    - hours          : The number of hours that the poll should run for. Must be at least one, or unspecified.
    - minutes        : The number of minutes that the poll should run for. Must be at least one, or unspecified.
    - seconds        : The number of seconds that the poll should run for. Must be at least one, or unspecified.

    Polls must have a run length. That is, specifying ALL run time kwargs as 'off' will return an error.

    TODO: restrict target kwarg to just roles, not users
    TODO: Change options list formatting from comma separated to new line separated
    TODO: Support target IDs

    :param discord.Message message: the discord message calling the command
    :param str args: A comma-separated list of space-separated emoji-option pairs, and optionally any kwargs as specified in this function's docstring
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if bbGlobals.usersDB.getOrAddID(message.author.id).pollOwned:
        await message.channel.send(":x: You can only make one poll at a time!")
        return

    pollOptions = {}

    argsSplit = args.split(",")
    argPos = 0
    arg = ""
    for arg in argsSplit:
        argPos += 1
        optionName, dumbReact = arg.strip(" ")[arg.strip(" ").index(" "):], lib.emojis.dumbEmojiFromStr(arg.strip(" ").split(" ")[0])
        if dumbReact is None:
            await message.channel.send(":x: Invalid emoji: " + arg.strip(" ").split(" ")[1])
            return
        elif dumbReact.isID:
            localEmoji = False
            for localEmoji in message.guild.emojis:
                if localEmoji.id == dumbReact.id:
                    localEmoji = True
                    break
            if not localEmoji:
                await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
                return

        if dumbReact in pollOptions:
            await message.channel.send(":x: Cannot use the same emoji for two options!")
            return

        for kwArg in [" target=", " days=", " hours=", " seconds=", " minutes=", " multiplechoice="]:
            if kwArg in optionName.lower():
                optionName = optionName[:optionName.lower().index(kwArg)]

        pollOptions[dumbReact] = ReactionMenu.DummyReactionMenuOption(optionName, dumbReact)

    if len(pollOptions) == 0:
        await message.channel.send(":x: No options given!")
        return

    targetRole = None
    targetMember = None
    if "target=" in arg.lower():
        argIndex = arg.lower().index("target=") + len("target=")
        try:
            arg[argIndex:].index(" ")
        except ValueError:
            endIndex = len(arg)
        else:
            endIndex = arg[argIndex:].index(" ") + argIndex + 1

        targetStr = arg[argIndex:endIndex]

        if lib.stringTyping.isRoleMention(targetStr):
            targetRole = message.guild.get_role(int(targetStr.lstrip("<@&").rstrip(">")))
            if targetRole is None:
                await message.channel.send(":x: Unknown target role!")
                return
        
        elif lib.stringTyping.isMention(targetStr):
            targetMember = message.guild.get_member(int(targetStr.lstrip("<@!").rstrip(">")))
            if targetMember is None:
                await message.channel.send(":x: Unknown target user!")
                return

        else:
            await message.channel.send(":x: Invalid target role/user!")
            return
    
    timeoutDict = {}

    for timeName in ["days", "hours", "minutes", "seconds"]:
        if timeName + "=" in arg.lower():
            argIndex = arg.lower().index(timeName + "=") + len(timeName + "=")
            try:
                arg[argIndex:].index(" ")
            except ValueError:
                endIndex = len(arg)
            else:
                endIndex = arg[argIndex:].index(" ") + argIndex + 1

            targetStr = arg[argIndex:endIndex]

            if targetStr == "off":
                timeoutDict[timeName] = -1
            else:
                if not lib.stringTyping.isInt(targetStr) or int(targetStr) < 1:
                    await message.channel.send(":x: Invalid number of " + timeName + " before timeout!")
                    return

                timeoutDict[timeName] = int(targetStr)


    multipleChoice = True

    if "multiplechoice=" in arg.lower():
        argIndex = arg.lower().index("multiplechoice=") + len("multiplechoice=")
        try:
            arg[argIndex:].index(" ")
        except ValueError:
            endIndex = len(arg)
        else:
            endIndex = arg[argIndex:].index(" ") + argIndex

        targetStr = arg[argIndex:endIndex]

        if targetStr.lower() in ["off", "no", "false", "single", "one"]:
            multipleChoice = False
        elif targetStr.lower() not in ["on", "yes", "true", "multiple", "many"]:
            await message.channel.send("Invalid `multiplechoice` argument '" + targetStr + "'! Please use either `multiplechoice=yes` or `multiplechoice=no`")
            return


    timeoutExists = False
    for timeName in timeoutDict:
        if timeoutDict[timeName] != -1:
            timeoutExists = True
    timeoutExists = timeoutExists or timeoutDict == {}

    if not timeoutExists:
        await message.channel.send(":x: Poll timeouts cannot be disabled!")
        return
    
    menuMsg = await message.channel.send("‎")

    timeoutDelta = lib.timeUtil.timeDeltaFromDict(bbConfig.pollMenuDefaultTimeout if timeoutDict == {} else timeoutDict)
    timeoutTT = TimedTask.TimedTask(expiryDelta=timeoutDelta, expiryFunction=ReactionPollMenu.printAndExpirePollResults, expiryFunctionArgs=menuMsg.id)
    bbGlobals.reactionMenusTTDB.scheduleTask(timeoutTT)

    menu = ReactionPollMenu.ReactionPollMenu(menuMsg, pollOptions, timeoutTT, pollStarter=message.author, multipleChoice=multipleChoice, targetRole=targetRole, targetMember=targetMember, owningBBUser=bbGlobals.usersDB.getUser(message.author.id))
    await menu.updateMessage()
    bbGlobals.reactionMenusDB[menuMsg.id] = menu
    bbGlobals.usersDB.getUser(message.author.id).pollOwned = True

bbCommands.register("poll", cmd_poll, 0, forceKeepArgsCasing=True)
dmCommands.register("poll", err_nodm, 0)


async def cmd_transfer(message : discord.Message, args : str, isDM : bool):
    """Transfer the calling user's home guild to the guild where the message was sent.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if message.guild.id == requestedBBUser.homeGuildID:
        await message.channel.send(":x: This is already your home server!")
    elif not requestedBBUser.canTransferGuild():
        await message.channel.send(":x: This command is still on cooldown. (" + lib.timeUtil.td_format_noYM(requestedBBUser.guildTransferCooldownEnd - datetime.utcnow()) + " left)")
    else:
        confirmEmbed = lib.discordUtil.makeEmbed(desc="This command's cooldown is " + lib.timeUtil.td_format_noYM(lib.timeUtil.timeDeltaFromDict(bbConfig.homeGuildTransferCooldown)) + ".", footerTxt="This menu will expire in " + str(bbConfig.homeGuildTransferConfirmTimeoutSeconds) + " seconds.")
        confirmEmbed.add_field(name=bbConfig.defaultAcceptEmoji.sendable + " : Confirm transfer", value="‎", inline=False)
        confirmEmbed.add_field(name=bbConfig.defaultRejectEmoji.sendable + " : Cancel transfer", value="‎", inline=False)
        confirmMsg = await message.channel.send("Move your home server to '" + message.guild.name + "'?\n", embed=confirmEmbed)

        for optionReact in [bbConfig.defaultAcceptEmoji, bbConfig.defaultRejectEmoji]:
            await confirmMsg.add_reaction(optionReact.sendable)

        def homeGuildTransferConfirmCheck(reactPL):
            return reactPL.message_id == confirmMsg.id and reactPL.user_id == message.author.id and lib.emojis.dumbEmojiFromPartial(reactPL.emoji) in [bbConfig.defaultAcceptEmoji, bbConfig.defaultRejectEmoji]

        try:
            reactPL = await bbGlobals.client.wait_for("raw_reaction_add", check=homeGuildTransferConfirmCheck, timeout=bbConfig.homeGuildTransferConfirmTimeoutSeconds)
            confirmEmbed.set_footer(text="This menu has now expired.")
            await confirmMsg.edit(embed=confirmEmbed)
        except asyncio.TimeoutError:
            await confirmMsg.edit(content="This menu has now expired. Please try the command again.")
        else:
            react = lib.emojis.dumbEmojiFromPartial(reactPL.emoji)
            if react == bbConfig.defaultAcceptEmoji:
                await requestedBBUser.transferGuild(message.guild)
                await message.channel.send(":airplane_arriving: You transferred your home server to " + message.guild.name + "!")
            else:
                await message.channel.send("🛑 Home guild transfer cancelled.")

bbCommands.register("transfer", cmd_transfer, 0)
dmCommands.register("transfer", err_nodm, 0)


async def cmd_home(message : discord.Message, args : str, isDM : bool):
    """Display the name of the calling user's home guild, if they have one.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if bbGlobals.usersDB.userIDExists(message.author.id):
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
        if message.guild is not None and message.guild.id == requestedBBUser.homeGuildID:
            await message.channel.send("🌍 This is your home server.")
            return
        elif requestedBBUser.hasHomeGuild() and bbGlobals.client.get_guild(requestedBBUser.homeGuildID) is not None:
            await message.channel.send("🪐 Your home server is '" + bbGlobals.client.get_guild(requestedBBUser.homeGuildID).name + "'.")
            return
    await message.channel.send("🌑 Your home server has not yet been set.\nSet your home server by using the shop or bounty board, or with the `" + bbConfig.commandPrefix + "transfer` command.")

bbCommands.register("home", cmd_home, 0)
dmCommands.register("home", cmd_home, 0)



####### ADMINISTRATOR COMMANDS #######



async def admin_cmd_set_announce_channel(message : discord.Message, args : str, isDM : bool):
    """admin command for setting the current guild's announcements channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if args == "off":
        if requestedBBGuild.hasAnnounceChannel():
            requestedBBGuild.removeAnnounceChannel()
            await message.channel.send(":ballot_box_with_check: Announcements channel removed!")
        else:
            await message.channel.send(":x: This server has no announce channel set!")
    elif args != "":
        await message.channel.send(":x: Invalid arguments! Can only be `off` to disable this server's announce channel, or no args to use this channel as the announce channel.")
    else:
        requestedBBGuild.setAnnounceChannel(message.channel)
        await message.channel.send(":ballot_box_with_check: Announcements channel set!")

bbCommands.register("set-announce-channel", admin_cmd_set_announce_channel, 1)


async def admin_cmd_set_bounty_board_channel(message : discord.Message, args : str, isDM : bool):
    """
    admin command for setting the current guild's bounty board channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if guild.hasBountyBoardChannel:
        await message.channel.send(":x: This server already has a bounty board channel! Use `" + bbConfig.commandPrefix + "remove-bounty-board-channel` to remove it.")
        return
    await guild.addBountyBoardChannel(message.channel, bbGlobals.client, bbData.bountyFactions)
    await message.channel.send(":ballot_box_with_check: Bounty board channel set!")

bbCommands.register("set-bounty-board-channel", admin_cmd_set_bounty_board_channel, 1)


async def admin_cmd_remove_bounty_board_channel(message : discord.Message, args : str, isDM : bool):
    """admin command for removing the current guild's bounty board channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if guild.hasBountyBoardChannel:
        guild.removeBountyBoardChannel()
        await message.channel.send(":ballot_box_with_check: Bounty board channel removed!")
    else:
        await message.channel.send(":x: This is not a bounty board channel!")

bbCommands.register("remove-bounty-board-channel", admin_cmd_remove_bounty_board_channel, 1)


async def admin_cmd_set_play_channel(message : discord.Message, args : str, isDM : bool):
    """admin command for setting the current guild's play channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if args == "off":
        if requestedBBGuild.hasPlayChannel():
            requestedBBGuild.removePlayChannel()
            await message.channel.send(":ballot_box_with_check: Bounty play channel removed!")
        else:
            await message.channel.send(":x: This server has no play channel set!")
    elif args != "":
        await message.channel.send(":x: Invalid arguments! Can only be `off` to disable this server's play channel, or no args to use this channel as the play channel.")
    else:
        requestedBBGuild.setPlayChannel(message.channel)
        await message.channel.send(":ballot_box_with_check: Bounty play channel set!")

bbCommands.register("set-play-channel", admin_cmd_set_play_channel, 1)


async def admin_cmd_admin_help(message : discord.Message, args : str, isDM : bool):
    """admin command printing help strings for admin commands as defined in bbData

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    sendChannel = None
    sendDM = False

    if message.author.dm_channel is None:
        await message.author.create_dm()
    if message.author.dm_channel is None:
        sendChannel = message.channel
    else:
        sendChannel = message.author.dm_channel
        sendDM = True

    helpEmbed = lib.discordUtil.makeEmbed(titleTxt="BB Administrator Commands",
                          thumb=bbGlobals.client.user.avatar_url_as(size=64))
    for section in bbData.adminHelpDict.keys():
        helpEmbed.add_field(name="‎", value="__" +
                            section + "__", inline=False)
        for currentCommand in bbData.adminHelpDict[section].values():
            helpEmbed.add_field(name=currentCommand[0], value=currentCommand[1].replace(
                "$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)

    try:
        await sendChannel.send(bbData.adminHelpIntro.replace("$COMMANDPREFIX$", bbConfig.commandPrefix), embed=helpEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return
    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji.sendable)

bbCommands.register("admin-help", admin_cmd_admin_help, 1)


async def admin_cmd_set_notify_role(message : discord.Message, args : str, isDM : bool):
    """For the current guild, set a role to mention when certain events occur.

    can take either a role mention or ID.

    :param discord.Message message: the discord message calling the command
    :param str args: the notfy role type, and either a role mention or a role ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please provide both a notification type, and either a role mention or ID!")
        return
    if not (lib.stringTyping.isInt(argsSplit[-1]) or lib.stringTyping.isRoleMention(argsSplit[-1])):
        await message.channel.send(":x: Invalid role! Please give either a role mention or ID!")
        return

    alertsToSet = getAlertIDFromHeirarchicalAliases(argsSplit)
    if alertsToSet[0] == "ERR":
        await message.channel.send(alertsToSet[1])
        return

    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if lib.stringTyping.isRoleMention(argsSplit[-1]):
        requestedRole = message.guild.get_role(int(argsSplit[-1][3:-1]))
    else:
        requestedRole = message.guild.get_role(int(argsSplit[-1]))

    if requestedRole is None:
        await message.channel.send(":x: Role not found!")
        return

    for alertID in alertsToSet:
        alertType = UserAlerts.userAlertsIDsTypes[alertID]
        requestedBBGuild.setUserAlertRoleID(alertID, requestedRole.id)
        await message.channel.send(":white_check_mark: Role set for " + UserAlerts.userAlertsTypesNames[alertType] + " notifications!")

bbCommands.register("set-notify-role", admin_cmd_set_notify_role, 1)


async def admin_cmd_remove_notify_role(message : discord.Message, args : str, isDM : bool):
    """For the current guild, remove role mentioning when certain events occur.
    Takes only a UserAlert ID.

    :param discord.Message message: the discord message calling the command
    :param str args: the notfy role type, and either a role mention or a role ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send(":x: Please provide both a notification type!")
        return

    alertsToSet = getAlertIDFromHeirarchicalAliases(args)
    if alertsToSet[0] == "ERR":
        await message.channel.send(alertsToSet[1])
        return

    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)

    for alertID in alertsToSet:
        alertType = UserAlerts.userAlertsIDsTypes[alertID]
        requestedBBGuild.removeUserAlertRoleID(alertID)
        await message.channel.send(":white_check_mark: Role pings disabled for " + UserAlerts.userAlertsTypesNames[alertType] + " notifications.")

bbCommands.register("remove-notify-role", admin_cmd_remove_notify_role, 1)


async def admin_cmd_make_role_menu(message : discord.Message, args : str, isDM : bool):
    """Create a reaction role menu, allowing users to self-assign or remove roles by adding and removing reactions.
    Each guild may have a maximum of bbConfig.maxRoleMenusPerGuild role menus active at any one time.
    Option reactions must be either unicode, or custom to the server where the menu is being created.

    args must contain a comma-separated list of emoji-option pairs, where each pair is separated with a space.
    For example: '0️⃣ @Role-1, 1️⃣ @Role-2, 2️⃣ @Role-3' will produce three options:
    - Toggling the 0️⃣ reaction will toggle user ownership of @Role-1
    - Toggling the 1️⃣ reaction will toggle user ownership of @Role-2
    - Toggling the 2️⃣ reaction will toggle user ownership of @Role-3

    args may also optionally contain the following keyword arguments, given as argname=value
    - target         : A role or user to restrict participants by. Must be a user or role mention, not ID.
    - days           : The number of days that the menu should run for. Must be at least one, or unspecified.
    - hours          : The number of hours that the menu should run for. Must be at least one, or unspecified.
    - minutes        : The number of minutes that the menu should run for. Must be at least one, or unspecified.
    - seconds        : The number of seconds that the menu should run for. Must be at least one, or unspecified.

    Reaction menus can be forced to run forever. To do this, specify ALL run time kwargs as 'off'.

    TODO: Change options list formatting from comma separated to new line separated
    TODO: Support target IDs
    TODO: Implement single choice/grouped roles
    TODO: Change non-expiring menu specification from all kwargs 'off' to a special kwarg 'on'

    :param discord.Message message: the discord message calling the command
    :param str args: A comma-separated list of space-separated emoji-option pairs, and optionally any kwargs as specified in this function's docstring
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.ownedRoleMenus >= bbConfig.maxRoleMenusPerGuild:
        await message.channel.send(":x: Guilds can have at most " + str(bbConfig.maxRoleMenusPerGuild) + " role menus!")
        return
    requestedBBGuild.ownedRoleMenus += 1

    botRole = None
    potentialRoles = []
    for currRole in message.guild.me.roles:
        if currRole.name == message.guild.me.name and currRole.managed:
            potentialRoles.append(currRole)
    
    if potentialRoles == []:
        await message.channel.send(":x: I can't find my '" + message.guild.me.name + "' role! Have you renamed it?")
        return
    botRole = potentialRoles[-1]

    reactionRoles = {}

    argsSplit = args.split(",")
    argPos = 0
    arg = ""
    for arg in argsSplit:
        argPos += 1
        roleStr, dumbReact = arg.strip(" ").split(" ")[1], lib.emojis.dumbEmojiFromStr(arg.strip(" ").split(" ")[0])
        if dumbReact is None:
            await message.channel.send(":x: Invalid emoji: " + arg.strip(" ").split(" ")[1])
            return
        elif dumbReact.isID:
            localEmoji = False
            for localEmoji in message.guild.emojis:
                if localEmoji.id == dumbReact.id:
                    localEmoji = True
                    break
            if not localEmoji:
                await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
                return
            
        if dumbReact in reactionRoles:
            await message.channel.send(":x: Cannot use the same emoji for two options!")
            return


        role = message.guild.get_role(int(roleStr.lstrip("<@&").rstrip(">")))
        if role is None:
            await message.channel.send(":x: Unrecognised role: " + roleStr)
            return
        elif role.position > botRole.position:
            await message.channel.send(":x: I can't grant the **" + role.name + "** role!\nMake sure it's below my '" + botRole.name + "' role in the server roles list.")
        reactionRoles[dumbReact] = role

    if len(reactionRoles) == 0:
        await message.channel.send(":x: No roles given!")
        return

    targetRole = None
    targetMember = None
    if "target=" in arg:
        argIndex = arg.lower().index("target=") + len("target=")
        try:
            arg[argIndex:].lower().index(" ")
        except ValueError:
            endIndex = len(arg)
        else:
            endIndex = arg[argIndex:].index(" ") + argIndex + 1

        targetStr = arg[argIndex:endIndex]

        if lib.stringTyping.isRoleMention(targetStr):
            targetRole = message.guild.get_role(int(targetStr.lstrip("<@&").rstrip(">")))
            if targetRole is None:
                await message.channel.send(":x: Unknown target role!")
                return
        
        elif lib.stringTyping.isMention(targetStr):
            targetMember = message.guild.get_member(int(targetStr.lstrip("<@!").rstrip(">")))
            if targetMember is None:
                await message.channel.send(":x: Unknown target user!")
                return

        else:
            await message.channel.send(":x: Invalid target role/user!")
            return
    
    timeoutDict = {}

    for timeName in ["days", "hours", "minutes", "seconds"]:
        if timeName + "=" in arg.lower():
            argIndex = arg.lower().index(timeName + "=") + len(timeName + "=")
            try:
                arg[argIndex:].index(" ")
            except ValueError:
                endIndex = len(arg)
            else:
                endIndex = arg[argIndex:].index(" ") + argIndex + 1

            targetStr = arg[argIndex:endIndex]

            if targetStr == "off":
                timeoutDict[timeName] = -1
            else:
                if not lib.stringTyping.isInt(targetStr) or int(targetStr) < 1:
                    await message.channel.send(":x: Invalid number of " + timeName + " before timeout!")
                    return

                timeoutDict[timeName] = int(targetStr)

    timeoutExists = False
    for timeName in timeoutDict:
        if timeoutDict[timeName] != -1:
            timeoutExists = True
    timeoutExists = timeoutExists or timeoutDict == {}
    
    menuMsg = await message.channel.send("‎")

    if timeoutExists:
        timeoutDelta = lib.timeUtil.timeDeltaFromDict(bbConfig.roleMenuDefaultTimeout if timeoutDict == {} else timeoutDict)
        timeoutTT = TimedTask.TimedTask(expiryDelta=timeoutDelta, expiryFunction=ReactionRolePicker.markExpiredRoleMenu, expiryFunctionArgs=menuMsg.id)
        bbGlobals.reactionMenusTTDB.scheduleTask(timeoutTT)
    
    else:
        timeoutTT = None

    menu = ReactionRolePicker.ReactionRolePicker(menuMsg, reactionRoles, message.guild, targetRole=targetRole, targetMember=targetMember, timeout=timeoutTT)
    await menu.updateMessage()
    bbGlobals.reactionMenusDB[menuMsg.id] = menu

bbCommands.register("make-role-menu", admin_cmd_make_role_menu, 1, forceKeepArgsCasing=True)


async def admin_cmd_del_reaction_menu(message : discord.Message, args : str, isDM : bool):
    """Force the expiry of the specified reaction menu message, regardless of reaction menu type.

    :param discord.Message message: the discord message calling the command
    :param str args: A string containing the message ID of an active reaction menu.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    msgID = int(args)
    if msgID in bbGlobals.reactionMenusDB:
        await bbGlobals.reactionMenusDB[msgID].delete()
    else:
        await message.channel.send(":x: Unrecognised reaction menu!")


bbCommands.register("del-reaction-menu", admin_cmd_del_reaction_menu, 1)


async def admin_cmd_config(message : discord.Message, args : str, isDM : bool):
    """Apply various bountybot configuration settings for the calling guild.
    TODO: Refactor!

    :param discord.Message message: the discord message calling the command
    :param str args: A string containing a config setting id followed by a value
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")

    if len(argsSplit) < 2 or not (argsSplit[0] and argsSplit[1]):
        await message.channel.send(":x: Please provide both a setting and a value! e.g: `" + bbConfig.commandPrefix + "config bounties enable`")
        return

    setting, value = argsSplit[0], " ".join(argsSplit[1:])

    trueStrings = ["yes","true","on","enable","enabled"]
    falseStrings = ["no","false","off","disable","disabled"]
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)

    if setting in ["bounty","bounties"]:
        if value in trueStrings:
            if not callingBBGuild.bountiesDisabled:
                await message.channel.send(":x: Bounties are already enabled in this server!")
            else:
                callingBBGuild.enableBounties()
                await message.channel.send(":white_check_mark: Bounties are now enabled on this server!")
        elif value in falseStrings:
            if callingBBGuild.bountiesDisabled:
                await message.channel.send(":x: Bounties are already disabled in this server!")
            else:
                callingBBGuild.disableBounties()
                await message.channel.send(":white_check_mark: Bounties are now disabled on this server!")
        else:
            await message.channel.send(":x: Unknown value!")
    elif setting in ["shop", "shops"]:
        if value in trueStrings:
            if not callingBBGuild.shopDisabled:
                await message.channel.send(":x: The shop is already enabled in this server!")
            else:
                callingBBGuild.enableShop()
                await message.channel.send(":white_check_mark: The shop is now enabled on this server!")
        elif value in falseStrings:
            if callingBBGuild.shopDisabled:
                await message.channel.send(":x: The shop is already disabled in this server!")
            else:
                callingBBGuild.disableShop()
                await message.channel.send(":white_check_mark: The shop is now disabled on this server!")
        else:
            await message.channel.send(":x: Unknown value!")
    else:
        await message.channel.send(":x: Unknown setting!")


bbCommands.register("config", admin_cmd_config, 1)



####### DEVELOPER COMMANDS #######


async def dev_cmd_sleep(message : discord.Message, args : str, isDM : bool):
    """developer command saving all data to JSON and then shutting down the bot

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("zzzz....")
    await shutdown()

bbCommands.register("sleep", dev_cmd_sleep, 2)
dmCommands.register("sleep", dev_cmd_sleep, 2)


async def dev_cmd_save(message : discord.Message, args : str, isDM : bool):
    """developer command saving all databases to JSON

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    try:
        saveAllDBs()
    except Exception as e:
        print("SAVING ERROR", e.__class__.__name__)
        print(traceback.format_exc())
        await message.channel.send("failed!")
        return
    print(datetime.now().strftime("%H:%M:%S: Data saved manually!"))
    await message.channel.send("saved!")

bbCommands.register("save", dev_cmd_save, 2)
dmCommands.register("save", dev_cmd_save, 2)


async def dev_cmd_has_announce(message : discord.Message, args : str, isDM : bool):
    """developer command printing whether or not the current guild has an announcements channel set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    await message.channel.send(":x: Unknown guild!" if guild is None else guild.hasAnnounceChannel())

bbCommands.register("has-announce", dev_cmd_has_announce, 2)
dmCommands.register("has-announce", err_nodm, 2)


async def dev_cmd_get_announce(message : discord.Message, args : str, isDM : bool):
    """developer command printing the current guild's announcements channel if one is set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("<#" + str(bbGlobals.guildsDB.getGuild(message.guild.id).getAnnounceChannel().id) + ">")

bbCommands.register("get-announce", dev_cmd_get_announce, 2)
dmCommands.register("get-announce", err_nodm, 2)


async def dev_cmd_has_play(message : discord.Message, args : str, isDM : bool):
    """developer command printing whether or not the current guild has a play channel set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    await message.channel.send(":x: Unknown guild!" if guild is None else guild.hasPlayChannel())

bbCommands.register("has-play", dev_cmd_has_play, 2)
dmCommands.register("has-play", err_nodm, 2)


async def dev_cmd_get_play(message : discord.Message, args : str, isDM : bool):
    """developer command printing the current guild's play channel if one is set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("<#" + str(bbGlobals.guildsDB.getGuild(message.guild.id).getPlayChannel().id) + ">")

bbCommands.register("get-play", dev_cmd_get_play, 2)
dmCommands.register("get-play", err_nodm, 2)


async def dev_cmd_clear_bounties(message : discord.Message, args : str, isDM : bool):
    """developer command clearing all active bounties. If a guild ID is given, clear bounties in that guild.
    If 'all' is given, clear bounties in all guilds. If nothing is given, clear bounties in the calling guild.

    :param discord.Message message: the discord message calling the command
    :param str args: empty or a guild id
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "all":
        for guild in bbGlobals.guildsDB.getGuilds():
            if not guild.bountiesDisabled:
                if guild.hasBountyBoardChannel:
                    await guild.bountyBoardChannel.clear()
                guild.bountiesDB.clearBounties()
        await message.channel.send(":ballot_box_with_check: All active bounties cleared.")
        return
    elif args == "":
        if isDM:
            await message.channel.send("Give either an id or 'all', or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(args):
        if not bbGlobals.guildsDB.guildsDB.guildIdExists(int(args)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(args))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + args)
        return
    
    if callingBBGuild.hasBountyBoardChannel:
        await callingBBGuild.bountyBoardChannel.clear()
    callingBBGuild.bountiesDB.clearBounties()
    await message.channel.send(":ballot_box_with_check: Active bounties cleared" + ((" for '" + callingBBGuild.dcGuild.name + "'.") if callingBBGuild.dcGuild is not None else "."))

bbCommands.register("clear-bounties", dev_cmd_clear_bounties, 2)
dmCommands.register("clear-bounties", dev_cmd_clear_bounties, 2)


async def dev_cmd_get_cooldown(message : discord.Message, args : str, isDM : bool):
    """developer command printing the calling user's checking cooldown

    :param discord.Message message: the discord message calling the command
    :param str args: ignore
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    diff = datetime.utcfromtimestamp(bbGlobals.usersDB.getUser(
        message.author.id).bountyCooldownEnd) - datetime.utcnow()
    minutes = int(diff.total_seconds() / 60)
    seconds = int(diff.total_seconds() % 60)
    await message.channel.send(str(bbGlobals.usersDB.getUser(message.author.id).bountyCooldownEnd) + " = " + str(minutes) + "m, " + str(seconds) + "s.")
    await message.channel.send(datetime.utcfromtimestamp(bbGlobals.usersDB.getUser(message.author.id).bountyCooldownEnd).strftime("%Hh%Mm%Ss"))
    await message.channel.send(datetime.utcnow().strftime("%Hh%Mm%Ss"))

bbCommands.register("get-cool", dev_cmd_get_cooldown, 2)
dmCommands.register("get-cool", dev_cmd_get_cooldown, 2)


async def dev_cmd_reset_cooldown(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the checking cooldown of the calling user, or the specified user if one is given

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).bountyCooldownEnd = datetime.utcnow().timestamp()
    # otherwise get the specified user's discord object and reset their cooldown.
    # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))
                        ).bountyCooldownEnd = datetime.utcnow().timestamp()
    await message.channel.send("Done!")

bbCommands.register("reset-cool", dev_cmd_reset_cooldown, 2)
dmCommands.register("reset-cool", dev_cmd_reset_cooldown, 2)


async def dev_cmd_reset_has_poll(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the poll ownership of the calling user, or the specified user if one is given.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).pollOwned = False
        # otherwise get the specified user's discord object and reset their cooldown.
        # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))).pollOwned = False
    await message.channel.send("Done!")

bbCommands.register("reset-has-poll", dev_cmd_reset_has_poll, 2)


async def dev_cmd_reset_daily_wins(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the max daily bounty wins of the calling user, or the specified user if one is given

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        # [!] no validation is done.
        requestedBBUser = bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">")))
    requestedBBUser.dailyBountyWinsReset = datetime.utcnow()
    requestedBBUser.bountyWinsToday = 0
    # otherwise get the specified user's discord object and reset their cooldown.

    await message.channel.send("Done!")

bbCommands.register("reset-daily-wins", dev_cmd_reset_daily_wins, 2)
dmCommands.register("reset-daily-wins", dev_cmd_reset_daily_wins, 2)


async def dev_cmd_give(message : discord.Message, args : str, isDM : bool):
    """developer command giving the provided user the provided item of the provided type.
    user must be either a mention or an ID or empty (to give the item to the calling user).
    type must be in bbConfig.validItemNames (but not 'all')
    item must be a json format description in line with the item's to and fromDict functions.

    :param discord.Message message: the discord message calling the command
    :param str args: string, containing either a user ID or mention or nothing (to give item to caller), followed by a string from bbConfig.validItemNames (but not 'all'), followed by an item dictionary representation
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if not lib.stringTyping.isInt(args.split(" ")[0]) and not lib.stringTyping.isMention(args.split(" ")[0]):
        requestedUser = bbGlobals.usersDB.getOrAddID(message.author.id)
        itemStr = args

    # otherwise get the specified user's bb object
    # [!] no validation is done.
    else:
        requestedUser = bbGlobals.usersDB.getOrAddID(
            int(args.split(" ")[0].lstrip("<@!").rstrip(">")))
        itemStr = args[len(args.split(" ")[0]) + 1:]

    itemType = itemStr.split(" ")[0].lower()

    if itemType == "all" or itemType not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item type - " + itemType)
        return

    itemDict = json.loads(itemStr[len(itemStr.split(" ")[0]):])
    itemConstructors = {"ship": bbShip.fromDict,
                        "weapon": bbWeapon.fromDict,
                        "module": bbModuleFactory.fromDict,
                        "turret": bbTurret.fromDict}
    newItem = itemConstructors[itemType](itemDict)

    requestedUser.getInactivesByName(itemType).addItem(newItem)

    await message.channel.send(":white_check_mark: Given one '" + newItem.name + "' to **" + lib.discordUtil.userOrMemberName(bbGlobals.client.get_user(requestedUser.id), message.guild) + "**!")

bbCommands.register("give", dev_cmd_give, 2, forceKeepArgsCasing=True)
dmCommands.register("give", dev_cmd_give, 2, forceKeepArgsCasing=True)


async def dev_cmd_del_item(message : discord.Message, args : str, isDM : bool):
    """Delete an item in a requested user's inventory.
    arg 1: user mention or ID
    arg 2: item type (ship/weapon/module/turret)
    arg 3: item number (from $hangar)

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a user mention, an item type and an index number, separated by a single space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 3:
        await message.channel.send(":x: Not enough arguments! Please provide a user, an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar`")
        return
    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! Please only give a user, an item type (ship/weapon/module/turret), and an item number.")
        return

    item = argsSplit[1].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    if not (lib.stringTyping.isInt(argsSplit[0]) or lib.stringTyping.isMention(argsSplit[0])):
        await message.channel.send(":x: Invalid user! ")
        return
    requestedBBUser = bbGlobals.usersDB.getOrAddID(
        int(argsSplit[0].lstrip("<@!").rstrip(">")))

    requestedUser = bbGlobals.client.get_user(requestedBBUser.id)
    if requestedUser is None:
        await message.channel.send(":x: Unrecognised user!")
        return

    itemNum = argsSplit[2]
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)

    userItemInactives = requestedBBUser.getInactivesByName(item)
    if itemNum > userItemInactives.numKeys:
        await message.channel.send(":x: Invalid item number! The user only has " + str(userItemInactives.numKeys) + " " + item + "s.")
        return
    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    requestedItem = userItemInactives[itemNum - 1].item
    itemName = ""
    itemEmbed = None

    if item == "ship":
        itemName = requestedItem.getNameAndNick()
        itemEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[requestedItem.manufacturer] if requestedItem.manufacturer in bbData.factionColours else bbData.factionColours[
            "neutral"], thumb=requestedItem.icon if requestedItem.hasIcon else "")

        if requestedItem is None:
            itemEmbed.add_field(name="Item:",
                                value="None", inline=False)
        else:
            itemEmbed.add_field(name="Item:", value=requestedItem.getNameAndNick(
            ) + "\n" + requestedItem.statsStringNoItems(), inline=False)

            if requestedItem.getMaxPrimaries() > 0:
                itemEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(
                    requestedItem.weapons)) + "/" + str(requestedItem.getMaxPrimaries()) + "*", inline=False)
                for weaponNum in range(1, len(requestedItem.weapons) + 1):
                    itemEmbed.add_field(name=str(weaponNum) + ". " + (requestedItem.weapons[weaponNum - 1].emoji.sendable + " " if requestedItem.weapons[weaponNum - 1].hasEmoji else "") + requestedItem.weapons[weaponNum - 1].name, value=requestedItem.weapons[weaponNum - 1].statsStringShort(), inline=True)

            if requestedItem.getMaxModules() > 0:
                itemEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(
                    requestedItem.modules)) + "/" + str(requestedItem.getMaxModules()) + "*", inline=False)
                for moduleNum in range(1, len(requestedItem.modules) + 1):
                    itemEmbed.add_field(name=str(moduleNum) + ". " + (requestedItem.modules[moduleNum - 1].emoji.sendable + " " if requestedItem.modules[moduleNum - 1].hasEmoji else "") + requestedItem.modules[moduleNum - 1].name, value=requestedItem.modules[moduleNum - 1].statsStringShort(), inline=True)

            if requestedItem.getMaxTurrets() > 0:
                itemEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(
                    requestedItem.turrets)) + "/" + str(requestedItem.getMaxTurrets()) + "*", inline=False)
                for turretNum in range(1, len(requestedItem.turrets) + 1):
                    itemEmbed.add_field(name=str(turretNum) + ". " + (requestedItem.turrets[turretNum - 1].emoji.sendable + " " if requestedItem.turrets[turretNum - 1].hasEmoji else "") + requestedItem.turrets[turretNum - 1].name, value=requestedItem.turrets[turretNum - 1].statsStringShort(), inline=True)

    else:
        itemName = requestedItem.name + "\n" + requestedItem.statsStringShort()

    await message.channel.send(":white_check_mark: One item deleted from " + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "'s inventory: " + itemName, embed=itemEmbed)
    userItemInactives.removeItem(requestedItem)

bbCommands.register("del-item", dev_cmd_del_item, 2)
dmCommands.register("del-item", dev_cmd_del_item, 2)


async def dev_cmd_del_item_key(message : discord.Message, args : str, isDM : bool):
    """Delete ALL of an item in a requested user's inventory.
    arg 1: user mention or ID
    arg 2: item type (ship/weapon/module/turret)
    arg 3: item number (from $hangar)

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a user mention, an item type and an index number, separated by a single space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 3:
        await message.channel.send(":x: Not enough arguments! Please provide a user, an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar`")
        return
    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! Please only give a user, an item type (ship/weapon/module/turret), and an item number.")
        return

    item = argsSplit[1].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    if not (lib.stringTyping.isInt(argsSplit[0]) or lib.stringTyping.isMention(argsSplit[0])):
        await message.channel.send(":x: Invalid user! ")
        return
    requestedBBUser = bbGlobals.usersDB.getOrAddID(
        int(argsSplit[0].lstrip("<@!").rstrip(">")))

    requestedUser = bbGlobals.client.get_user(requestedBBUser.id)
    if requestedUser is None:
        await message.channel.send(":x: Unrecognised user!")
        return

    itemNum = argsSplit[2]
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)

    userItemInactives = requestedBBUser.getInactivesByName(item)
    if itemNum > userItemInactives.numKeys:
        await message.channel.send(":x: Invalid item number! The user only has " + str(userItemInactives.numKeys) + " " + item + "s.")
        return
    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    requestedItem = userItemInactives.keys[itemNum - 1]
    itemName = ""
    itemEmbed = None

    if item == "ship":
        itemName = requestedItem.getNameAndNick()
        itemEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[requestedItem.manufacturer] if requestedItem.manufacturer in bbData.factionColours else bbData.factionColours[
            "neutral"], thumb=requestedItem.icon if requestedItem.hasIcon else "")

        if requestedItem is None:
            itemEmbed.add_field(name="Item:",
                                value="None", inline=False)
        else:
            itemEmbed.add_field(name="Item:", value=requestedItem.getNameAndNick(
            ) + "\n" + requestedItem.statsStringNoItems(), inline=False)

            if requestedItem.getMaxPrimaries() > 0:
                itemEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(
                    requestedItem.weapons)) + "/" + str(requestedItem.getMaxPrimaries()) + "*", inline=False)
                for weaponNum in range(1, len(requestedItem.weapons) + 1):
                    itemEmbed.add_field(name=str(weaponNum) + ". " + (requestedItem.weapons[weaponNum - 1].emoji.sendable + " " if requestedItem.weapons[weaponNum - 1].hasEmoji else "") + requestedItem.weapons[weaponNum - 1].name, value=requestedItem.weapons[weaponNum - 1].statsStringShort(), inline=True)

            if requestedItem.getMaxModules() > 0:
                itemEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(
                    requestedItem.modules)) + "/" + str(requestedItem.getMaxModules()) + "*", inline=False)
                for moduleNum in range(1, len(requestedItem.modules) + 1):
                    itemEmbed.add_field(name=str(moduleNum) + ". " + (requestedItem.modules[moduleNum - 1].emoji.sendable + " " if requestedItem.modules[moduleNum - 1].hasEmoji else "") + requestedItem.modules[moduleNum - 1].name, value=requestedItem.modules[moduleNum - 1].statsStringShort(), inline=True)

            if requestedItem.getMaxTurrets() > 0:
                itemEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(
                    requestedItem.turrets)) + "/" + str(requestedItem.getMaxTurrets()) + "*", inline=False)
                for turretNum in range(1, len(requestedItem.turrets) + 1):
                    itemEmbed.add_field(name=str(turretNum) + ". " + (requestedItem.turrets[turretNum - 1].emoji.sendable + " " if requestedItem.turrets[turretNum - 1].hasEmoji else "") + requestedItem.turrets[turretNum - 1].name, value=requestedItem.turrets[turretNum - 1].statsStringShort(), inline=True)

    else:
        itemName = requestedItem.name + "\n" + requestedItem.statsStringShort()

    if requestedItem not in userItemInactives.items:
        userItemInactives.keys.remove(requestedItem)
        userItemInactives.numKeys -= 1
        await message.channel.send(":white_check_mark: **Erroneous key** deleted from " + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "'s inventory: " + itemName, embed=itemEmbed)
    else:
        itemCount = userItemInactives.items[requestedItem].count
        del userItemInactives.items[requestedItem]
        userItemInactives.keys.remove(requestedItem)
        userItemInactives.numKeys -= 1
        await message.channel.send(":white_check_mark: " + str(itemCount) + " item(s) deleted from " + lib.discordUtil.userOrMemberName(requestedUser, message.guild) + "'s inventory: " + itemName, embed=itemEmbed)

bbCommands.register("del-item-key", dev_cmd_del_item_key, 2)
dmCommands.register("del-item-key", dev_cmd_del_item_key, 2)


async def dev_cmd_setcheckcooldown(message : discord.Message, args : str, isDM : bool):
    """developer command setting the checking cooldown applied to users
    this does not update bbConfig and will be reverted on bot restart

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an integer number of minutes
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a time was requested
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    # verify the requested time is an integer
    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the checking cooldown amount
    bbConfig.checkCooldown["minutes"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)

bbCommands.register("setcheckcooldown", dev_cmd_setcheckcooldown, 2)
dmCommands.register("setcheckcooldown", dev_cmd_setcheckcooldown, 2)


async def dev_cmd_setbountyperiodm(message : discord.Message, args : str, isDM : bool):
    """developer command setting the number of minutes in the new bounty generation period
    this does not update bbConfig and will be reverted on bot restart
    this does not affect the numebr of hours in the new bounty generation period

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an integer number of minutes
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a time was given
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    # verify the given time is an integer
    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the new bounty generation cooldown
    bbConfig.newBountyFixedDelta["minutes"] = int(args)
    bbGlobals.newBountyFixedDeltaChanged = True
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)

bbCommands.register("setbountyperiodm", dev_cmd_setbountyperiodm, 2)
dmCommands.register("setbountyperiodm", dev_cmd_setbountyperiodm, 2)


async def dev_cmd_setbountyperiodh(message : discord.Message, args : str, isDM : bool):
    """developer command setting the number of hours in the new bounty generation period
    this does not update bbConfig and will be reverted on bot restart
    this does not affect the numebr of minutes in the new bounty generation period

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an integer number of hours
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a time was specified
    if args == "":
        await message.channel.send(":x: please give the number of hours!")
        return
    # verify the given time is an integer
    if not lib.stringTyping.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the bounty generation period
    bbGlobals.newBountyFixedDeltaChanged = True
    bbConfig.newBountyFixedDelta["hours"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)

bbCommands.register("setbountyperiodh", dev_cmd_setbountyperiodh, 2)
dmCommands.register("setbountyperiodh", dev_cmd_setbountyperiodh, 2)


async def dev_cmd_resetnewbountycool(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the current bounty generation period,
    instantly generating a new bounty

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guildStr = args

    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    await callingBBGuild.newBountyTT.forceExpire()
    await message.channel.send(":ballot_box_with_check: New bounty cooldown reset for '" + callingBBGuild.dcGuild.name + "'")

bbCommands.register("resetnewbountycool", dev_cmd_resetnewbountycool, 2)
dmCommands.register("resetnewbountycool", dev_cmd_resetnewbountycool, 2)


async def dev_cmd_canmakebounty(message : discord.Message, args : str, isDM : bool):
    """developer command printing whether or not the given faction can accept new bounties
    If no guild ID is given, bounty spawning ability is checked for the calling guild

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a faction followed by optionally a guild ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    newFaction = args.split(" ")[0].lower()
    guildStr = args.split(" ")[1] if len(args.split(" ")) > 1 else ""

    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    # ensure the given faction exists
    if not callingBBGuild.bountiesDB.factionExists(newFaction):
        await message.channel.send("not a faction: '" + newFaction + "'")
    else:
        await message.channel.send(callingBBGuild.bountiesDB.factionCanMakeBounty(newFaction.lower()))

bbCommands.register("canmakebounty", dev_cmd_canmakebounty, 2)
dmCommands.register("canmakebounty", dev_cmd_canmakebounty, 2)


async def dev_cmd_broadcast(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the playChannel of all guilds that have one

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]

                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        if useAnnounceChannel:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasAnnounceChannel():
                    await guild.getAnnounceChannel().send(msgText, embed=broadcastEmbed)
        else:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasPlayChannel():
                    await guild.getPlayChannel().send(msgText, embed=broadcastEmbed)

bbCommands.register("broadcast", dev_cmd_broadcast, 2, forceKeepArgsCasing=True)
dmCommands.register("broadcast", dev_cmd_broadcast, 2, forceKeepArgsCasing=True)


async def dev_cmd_say(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the same channel as the command is called in

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex].replace("{NL}", "\n")
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]
                
                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        await message.channel.send(msgText, embed=broadcastEmbed)

bbCommands.register("say", dev_cmd_say, 2, forceKeepArgsCasing=True)
dmCommands.register("say", dev_cmd_say, 2, forceKeepArgsCasing=True)


async def dev_cmd_make_bounty(message : discord.Message, args : str, isDM : bool):
    """developer command making a new bounty
    args should be separated by a space and then a plus symbol
    if no args are given, generate a new bounty at complete random
    if only one argument is given it is assumed to be a faction, and a bounty is generated for that faction
    otherwise, all 9 arguments required to generate a bounty must be given
    the route should be separated by only commas and no spaces. the endTime should be a UTC timestamp. Any argument can be given as 'auto' to be either inferred or randomly generated
    as such, '!bb make-bounty' is an alias for '!bb make-bounty +auto +auto +auto +auto +auto +auto +auto +auto +auto'

    :param discord.Message message: the discord message calling the command
    :param str args: can be empty, can be '[guild id] +<faction>', or can be '[guild id] +<faction> +<name> +<route> +<start> +<end> +<answer> +<reward> +<endtime> +<icon>'
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guildStr = args.split("+")[0].strip()
    args = args[len(guildStr):].lstrip()
    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    # if no args were given, generate a completely random bounty
    if args == "":
        newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB)
    # if only one argument was given, use it as a faction
    elif len(args.split("+")) == 2:
        newFaction = args.split("+")[1]
        newBounty = bbBounty.Bounty(
            bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction))

    # if all args were given, generate a completely custom bounty
    # 9 args plus account for empty string at the start of the split = split of 10 elements
    elif len(args.split("+")) == 10:
        # track whether a builtIn criminal was requested
        builtIn = False
        builtInCrimObj = None
        # [1:] remove empty string before + splits
        bData = args.split("+")[1:]

        # parse the given faction
        newFaction = bData[0].rstrip(" ")
        if newFaction == "auto":
            newFaction = ""

        # parse the given criminal name
        newName = bData[1].rstrip(" ").title()
        if newName == "Auto":
            newName = ""
        else:
            # if a criminal name was given, see if it corresponds to a builtIn criminal
            for crim in bbData.builtInCriminalObjs.values():
                if crim.isCalled(newName):
                    builtIn = True
                    builtInCrimObj = crim
                    newName = crim.name
                    break

            # if a criminal name was given, ensure it does not already exist as a bounty
            if newName != "" and callingBBGuild.bountiesDB.bountyNameExists(newName):
                await message.channel.send(":x: That pilot is already wanted!")
                return

        # parse the given route
        newRoute = bData[2].rstrip(" ")
        if newRoute == "auto":
            newRoute = []
        else:
            newRoute = bData[2].split(",")
            newRoute[-1] = newRoute[-1].rstrip(" ")

        # parse the given start system
        newStart = bData[3].rstrip(" ")
        if newStart == "auto":
            newStart = ""

        # parse the given end system
        newEnd = bData[4].rstrip(" ")
        if newEnd == "auto":
            newEnd = ""

        # parse the given answer system
        newAnswer = bData[5].rstrip(" ")
        if newAnswer == "auto":
            newAnswer = ""

        # parse the given reward amount
        newReward = bData[6].rstrip(" ")
        if newReward == "auto":
            newReward = -1
        newReward = int(newReward)

        # parse the given end time
        newEndTime = bData[7].rstrip(" ")
        if newEndTime == "auto":
            newEndTime = -1.0
        newEndTime = float(newEndTime)

        # parse the given icon
        newIcon = bData[8].rstrip(" ")
        if newIcon == "auto":
            newIcon = "" if not builtIn else builtInCrimObj.icon

        # special bounty generation for builtIn criminals
        if builtIn:
            newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, criminalObj=builtInCrimObj, config=bbBountyConfig.BountyConfig(
                faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon))
        # normal bounty generation for custom criminals
        else:
            newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute,
                                                                                                start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon))

    # Report an error for invalid command syntax
    else:
        await message.channel.send("incorrect syntax. give +faction +name +route +start +end +answer +reward +endtime +icon")
        return

    # activate and announce the new bounty
    callingBBGuild.bountiesDB.addBounty(newBounty)
    await callingBBGuild.announceNewBounty(newBounty)

bbCommands.register("make-bounty", dev_cmd_make_bounty, 2, forceKeepArgsCasing=True)
dmCommands.register("make-bounty", dev_cmd_make_bounty, 2 , forceKeepArgsCasing=True)


async def dev_cmd_make_player_bounty(message : discord.Message, args : str, isDM : bool):
    """developer command making a new PLAYER bounty
    args should be separated by a space and then a plus symbol
    the first argument should be a user MENTION
    if one arg is given, generate a new bounty at complete random, for the specified user
    if two arguments are given the second is assumed to be a faction, and a bounty is generated for that faction for the specified user
    otherwise, all 9 arguments required to generate a bounty must be given
    the route should be separated by only commas and no spaces. the endTime should be a UTC timestamp. Any argument can be given as 'auto' to be either inferred or randomly generated
    as such, '!bb make-player-bounty <user>' is an alias for '!bb make-bounty +auto +<user> +auto +auto +auto +auto +auto +auto +auto'

    :param discord.Message message: the discord message calling the command
    :param str args: can be empty, can be '[guild id] +<user_mention> +<faction>', or can be '[guild id] +<faction> +<user_mention> +<route> +<start> +<end> +<answer> +<reward> +<endtime> +<icon>'
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guildStr = args.split("+")[0].strip()
    args = args[len(guildStr):].lstrip()
    if guildStr == "":
        if isDM:
            await message.channel.send("Either give a guild id or call from within a guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
        if callingBBGuild.bountiesDisabled:
            await message.channel.send("This guild has bounties disabled.")
            return
    elif lib.stringTyping.isInt(guildStr):
        if not bbGlobals.guildsDB.guildsDB.guildIdExists(int(guildStr)):
            await message.channel.send("Unrecognised guild")
            return
        callingBBGuild = bbGlobals.guildsDB.getGuild(int(guildStr))
        if callingBBGuild.bountiesDisabled:
            await message.channel.send((("'" + callingBBGuild.dcGuild.name + "' ") if callingBBGuild.dcGuild is not None else "The requested guild ") + " has bounties disabled.")
            return
    else:
        await message.channel.send(":x: Unrecognised parameter: " + guildStr)
        return

    # if only one argument is given
    if len(args.split(" ")) == 1:
        # verify the requested user
        requestedID = int(args.lstrip("<@!").rstrip(">"))
        if not lib.stringTyping.isInt(requestedID) or (bbGlobals.client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # create a new bounty at random for the specified user
        newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(
            name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(bbGlobals.client.get_user(requestedID).avatar_url_as(size=64)), aliases=[lib.discordUtil.userTagOrDiscrim(args)]))

    # if the faction is also given
    elif len(args.split("+")) == 2:
        # verify the user
        requestedID = int(args.split(" ")[0].lstrip("<@!").rstrip(">"))
        if not lib.stringTyping.isInt(requestedID) or (bbGlobals.client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # create a bounty at random for the specified user and faction
        newFaction = args.split("+")[1]
        newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(
            bbGlobals.client.get_user(requestedID).avatar_url_as(size=64)), faction=newFaction, aliases=[lib.discordUtil.userTagOrDiscrim(args.split(" ")[0])]))

    # if all arguments are given
    elif len(args.split("+")) == 10:
        # [1:] remove starting empty string before + split
        bData = args.split("+")[1:]

        # parse the requested faction
        newFaction = bData[0].rstrip(" ")
        if newFaction == "auto":
            newFaction = ""

        # parse the requested user ID
        # no auto option!
        newName = bData[1].rstrip(" ").title()
        # verify the requested user
        requestedID = int(newName.lstrip("<@!").rstrip(">"))
        if not lib.stringTyping.isInt(requestedID) or (bbGlobals.client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # ensure no bounty already exists for this user
        if callingBBGuild.bountiesDB.bountyNameExists(newName):
            await message.channel.send(":x: That pilot is already wanted!")
            return

        # parse the requested route
        newRoute = bData[2].rstrip(" ")
        if newRoute == "auto":
            newRoute = []
        else:
            newRoute = bData[2].split(",")
            newRoute[-1] = newRoute[-1].rstrip(" ")

        # parse the requested start system
        newStart = bData[3].rstrip(" ")
        if newStart == "auto":
            newStart = ""

        # parse the requested end system
        newEnd = bData[4].rstrip(" ")
        if newEnd == "auto":
            newEnd = ""

        # parse the requested answer system
        newAnswer = bData[5].rstrip(" ")
        if newAnswer == "auto":
            newAnswer = ""

        # parse the requested reward pool
        newReward = bData[6].rstrip(" ")
        if newReward == "auto":
            newReward = -1
        newReward = int(newReward)

        # parse the requested end time
        newEndTime = bData[7].rstrip(" ")
        if newEndTime == "auto":
            newEndTime = -1.0
        newEndTime = float(newEndTime)

        # parse the requested icon URL
        newIcon = bData[8].rstrip(" ")
        if newIcon == "auto":
            newIcon = str(bbGlobals.client.get_user(
                int(newName.lstrip("<@!").rstrip(">"))).avatar_url_as(size=64))

        # create the bounty object
        newBounty = bbBounty.Bounty(bountyDB=callingBBGuild.bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart,
                                                                                            end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=True, icon=newIcon, aliases=[lib.discordUtil.userTagOrDiscrim(newName)]))

    # print an error for incorrect syntax
    else:
        await message.channel.send("incorrect syntax. give +faction +userTag +route +start +end +answer +reward +endtime +icon")
        return

    # activate and announce the bounty
    callingBBGuild.bountiesDB.addBounty(newBounty)
    await callingBBGuild.announceNewBounty(newBounty)

bbCommands.register("make-player-bounty", dev_cmd_make_player_bounty, 2, forceKeepArgsCasing=True)
dmCommands.register("make-player-bounty", dev_cmd_make_player_bounty, 2, forceKeepArgsCasing=True)


async def dev_cmd_refreshshop(message : discord.Message, args : str, isDM : bool):
    """Refresh the shop stock of the current guild. Does not reset the shop stock cooldown.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    level = -1
    if args != "":
        if not lib.stringTyping.isInt(args) or not int(args) in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1):
            await message.channel.send("Invalid tech level!")
            return
        level = int(args)
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if guild.shopDisabled:
        await message.channel.send(":x: This guild's shop is disabled.")
    else:
        guild.shop.refreshStock(level=level)
        await announceNewShopStock(guild.id)
    # if guild.hasPlayChannel():
    #     await guild.getPlayChannel().send(":arrows_counterclockwise: The shop stock has been refreshed!\n**        **Now at tech level: **" + str(guild.shop.currentTechLevel) + "**")

bbCommands.register("refreshshop", dev_cmd_refreshshop, 2)
dmCommands.register("refreshshop", err_nodm, 2)


async def dev_cmd_setbalance(message : discord.Message, args : str, isDM : bool):
    """developer command setting the requested user's balance.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a user mention and an integer number of credits
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    # verify both a user and a balance were given
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a user mention followed by the new balance!")
        return
    # verify the requested balance is an integer
    if not lib.stringTyping.isInt(argsSplit[1]):
        await message.channel.send(":x: that's not a number!")
        return
    # verify the requested user
    requestedUser = bbGlobals.client.get_user(
        int(argsSplit[0].lstrip("<@!").rstrip(">")))
    if requestedUser is None:
        await message.channel.send(":x: invalid user!!")
        return
    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        requestedBBUser = bbGlobals.usersDB.addUser(requestedUser.id)
    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
    # update the balance
    requestedBBUser.credits = int(argsSplit[1])
    await message.channel.send("Done!")

bbCommands.register("setbalance", dev_cmd_setbalance, 2)
dmCommands.register("setbalance", dev_cmd_setbalance, 2)


async def dev_cmd_debug_hangar(message : discord.Message, args : str, isDM : bool):
    """developer command printing the requested user's hangar, including object memory addresses.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a user mention or ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if not (lib.stringTyping.isInt(args) or lib.stringTyping.isMention(args)):
        await message.channel.send(":x: Invalid user!")
        return

    requestedUser = bbGlobals.client.get_user(int(args.lstrip("<@!").rstrip(">")))
    if requestedUser is None:
        await message.channel.send(":x: Unrecognised user!")
        return

    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        await message.channel.send("User has not played yet!")
        return

    requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
    maxPerPage = bbConfig.maxItemsPerHangarPageAll

    maxPage = requestedBBUser.numInventoryPages("all", maxPerPage)
    if maxPage == 0:
        await message.channel.send(":x: The requested pilot doesn't have any items!")
        return

    itemTypes = ("ship", "weapon", "module", "turret")
    for itemType in itemTypes:
        itemInv = requestedBBUser.getInactivesByName(itemType)
        await message.channel.send(itemType.upper() + " KEYS: " + str(itemInv.keys) + "\n" + itemType.upper() + " LISTINGS: " + str(list(itemInv.items.keys())))

    for page in range(1, maxPage+1):

        hangarEmbed = lib.discordUtil.makeEmbed(titleTxt="Hangar", desc=requestedUser.mention, col=bbData.factionColours["neutral"], footerTxt="All items - page " + str(
            page) + "/" + str(requestedBBUser.numInventoryPages("all", maxPerPage)), thumb=requestedUser.avatar_url_as(size=64))
        firstPlace = maxPerPage * (page - 1) + 1

        for itemType in itemTypes:
            itemInv = requestedBBUser.getInactivesByName(itemType)
            displayedItems = []

            for itemNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage(itemType, page, maxPerPage) + 1):
                if itemNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored " + itemType.title() + "s**__", inline=False)
                currentItem = itemInv.keys[itemNum - 1]
                itemStored = currentItem in itemInv.items
                currentItemCount = itemInv.numStored(
                    currentItem) if itemStored else 0
                displayedItems.append(currentItem)
                if itemType == "ship":
                    currentItemName = currentItem.getNameAndNick()
                else:
                    currentItemName = currentItem.name
                try:
                    hangarEmbed.add_field(name=str(itemNum) + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ". " + ("" if itemStored else "⚠ KEY NOT FOUND IN ITEMS DICT ") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItemName + "\n`" + repr(currentItem) + "`",
                                          value=currentItem.statsStringShort(), inline=False)
                except AttributeError:
                    hangarEmbed.add_field(name=str(itemNum) + ". " + ("" if itemStored else "⚠ KEY NOT FOUND IN ITEMS DICT ") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItemName + "\n`" + repr(currentItem) + "`",
                                          value="unexpected type", inline=False)

            expectedKeys = itemInv.items.keys()
            for itemNum in range(len(expectedKeys)):
                itemKey = itemInv.items.expectedKeys[itemNum]
                if itemKey not in displayedItems:
                    currentItemCount = itemInv.items[itemKey].count
                    displayedItems.append(itemKey)
                    if itemType == "ship":
                        currentItemName = itemKey.getNameAndNick()
                    else:
                        currentItemName = itemKey.name
                    try:
                        hangarEmbed.add_field(name=str(itemNum) + (itemKey.emoji.sendable + " " if itemKey.hasEmoji else "") + ". ⚠ ITEM LISTING NOT FOUND IN KEYS " + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItemName + "\n`" + repr(itemKey) + "`",
                                              value=itemKey.statsStringShort(), inline=False)
                    except AttributeError:
                        hangarEmbed.add_field(name=str(itemNum) + ". ⚠ ITEM LISTING NOT FOUND IN KEYS " + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItemName + "\n`" + repr(itemKey) + "`",
                                              value="unexpected type", inline=False)

        await message.channel.send(embed=hangarEmbed)


bbCommands.register("debug-hangar", dev_cmd_debug_hangar, 2)
dmCommands.register("debug-hangar", dev_cmd_debug_hangar, 2)


async def dev_cmd_reset_transfer_cool(message : discord.Message, args : str, isDM : bool):
    """developer command resetting a user's home guild transfer cooldown.

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string or string containing a user mention or ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).guildTransferCooldownEnd = datetime.utcnow()
    # otherwise get the specified user's discord object and reset their cooldown.
    # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))
                        ).guildTransferCooldownEnd = datetime.utcnow()
    await message.channel.send("Done!")
    

bbCommands.register("reset-transfer-cool", dev_cmd_reset_transfer_cool, 2)
dmCommands.register("reset-transfer-cool", dev_cmd_reset_transfer_cool, 2)



####### MAIN FUNCTIONS #######


@bbGlobals.client.event
async def on_guild_join(guild : discord.Guild):
    """Create a database entry for new guilds when one is joined.
    TODO: Once deprecation databases are implemented, if guilds now store important information consider searching for them in deprecated

    :param discord.Guild guild: the guild just joined.
    """
    guildExists = True
    if not bbGlobals.guildsDB.guildIdExists(guild.id):
        guildExists = False
        bbGlobals.guildsDB.addGuildID(guild.id)
    bbLogger.log("Main", "guild_join", "I joined a new guild! " + guild.name + "#" + str(guild.id) + ("\n -- The guild was added to bbGlobals.guildsDB" if not guildExists else ""),
                 category="guildsDB", eventType="NW_GLD")


@bbGlobals.client.event
async def on_guild_remove(guild : discord.Guild):
    """Remove the database entry for any guilds the bot leaves.
    TODO: Once deprecation databases are implemented, if guilds now store important information consider moving them to deprecated.

    :param discord.Guild guild: the guild just left.
    """
    guildExists = False
    if bbGlobals.guildsDB.guildIdExists(guild.id):
        guildExists = True
        bbGlobals.guildsDB.removeGuildId(guild.id)
    bbLogger.log("Main", "guild_remove", "I left a guild! " + guild.name + "#" + str(guild.id) + ("\n -- The guild was removed from bbGlobals.guildsDB" if guildExists else ""),
                 category="guildsDB", eventType="NW_GLD")


@bbGlobals.client.event
async def on_ready():
    """Bot initialisation (called on bot login) and behaviour loops.
    Currently includes:
    - new bounty spawning
    - shop stock refreshing
    - regular database saving to JSON

    TODO: Add bounty expiry and reaction menu (e.g duel challenges) expiry
    TODO: Implement dynamic timedtask checking period
    TODO: Move item initialization to separate method
    """
    ##### OBJECT SPAWNING #####

    # generate bbCriminal objects from data in bbData
    for criminalDict in bbData.builtInCriminalData.values():
        bbData.builtInCriminalObjs[criminalDict["name"]] = bbCriminal.fromDict(criminalDict)
        bbData.builtInCriminalObjs[criminalDict["name"]].builtIn = True
        bbData.builtInCriminalData[criminalDict["name"]]["builtIn"] = True

    # generate bbSystem objects from data in bbData
    for systemDict in bbData.builtInSystemData.values():
        bbData.builtInSystemObjs[systemDict["name"]] = bbSystem.fromDict(systemDict)
        bbData.builtInSystemData[systemDict["name"]]["builtIn"] = True
        bbData.builtInSystemObjs[systemDict["name"]].builtIn = True

    # generate bbModule objects from data in bbData
    for moduleDict in bbData.builtInModuleData.values():
        bbData.builtInModuleObjs[moduleDict["name"]] = bbModuleFactory.fromDict(moduleDict)
        bbData.builtInModuleData[moduleDict["name"]]["builtIn"] = True
        bbData.builtInModuleObjs[moduleDict["name"]].builtIn = True

    # generate bbWeapon objects from data in bbData
    for weaponDict in bbData.builtInWeaponData.values():
        bbData.builtInWeaponObjs[weaponDict["name"]] = bbWeapon.fromDict(weaponDict)
        bbData.builtInWeaponData[weaponDict["name"]]["builtIn"] = True
        bbData.builtInWeaponObjs[weaponDict["name"]].builtIn = True

    # generate bbUpgrade objects from data in bbData
    for upgradeDict in bbData.builtInUpgradeData.values():
        bbData.builtInUpgradeObjs[upgradeDict["name"]] = bbShipUpgrade.fromDict(upgradeDict)
        bbData.builtInUpgradeData[upgradeDict["name"]]["builtIn"] = True
        bbData.builtInUpgradeObjs[upgradeDict["name"]].builtIn = True

    # generate bbTurret objects from data in bbData
    for turretDict in bbData.builtInTurretData.values():
        bbData.builtInTurretObjs[turretDict["name"]] = bbTurret.fromDict(turretDict)
        bbData.builtInTurretData[turretDict["name"]]["builtIn"] = True
        bbData.builtInTurretObjs[turretDict["name"]].builtIn = True



    ##### ITEM TECHLEVEL AUTO-GENERATION #####

    # Assign each shipDict a techLevel, based on their value
    for shipDict in bbData.builtInShipData.values():
        for tl in range(len(bbConfig.shipMaxPriceTechLevels)):
            if bbConfig.shipMaxPriceTechLevels[tl] >= shipDict["value"]:
                shipDict["techLevel"] = tl + 1
                break



    ##### SORT ITEMS BY TECHLEVEL #####

    # Initialise shipKeysByTL as maxTechLevel empty arrays
    bbData.shipKeysByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]

    # Sort ship keys by tech level
    for currentShipKey in bbData.builtInShipData.keys():
        bbData.shipKeysByTL[bbData.builtInShipData[currentShipKey]["techLevel"] - 1].append(currentShipKey)

    # Sort module objects by tech level
    bbData.moduleObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
    for currentModuleObj in bbData.builtInModuleObjs.values():
        bbData.moduleObjsByTL[currentModuleObj.techLevel - 1].append(currentModuleObj)

    # Sort weapon objects by tech level
    bbData.weaponObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
    for currentWeaponObj in bbData.builtInWeaponObjs.values():
        bbData.weaponObjsByTL[currentWeaponObj.techLevel - 1].append(currentWeaponObj)

    # Sort turret objects by tech level
    bbData.turretObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
    for currentTurretObj in bbData.builtInTurretObjs.values():
        bbData.turretObjsByTL[currentTurretObj.techLevel - 1].append(currentTurretObj)


    print("[bbConfig.init] Ship tech levels generated:")
    for shipTL in range(len(bbData.shipKeysByTL)):
        print("\t• <=" + str(bbConfig.shipMaxPriceTechLevels[shipTL]) + "=TL" + str(shipTL+1) + ":",end="")
        for shipName in bbData.shipKeysByTL[shipTL]:
            print(" " + shipName + ",",end="")
        print()



    ##### MAX SPAWNRATE CALCULATION #####

    for ship in bbData.builtInShipData.values():
        ship["shopSpawnRate"] = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[ship["techLevel"] - 1][ship["techLevel"] - 1] / len(bbData.shipKeysByTL[ship["techLevel"] - 1])) * 100)

    for weapon in bbData.builtInWeaponObjs.values():
        weapon.shopSpawnRate = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[weapon.techLevel - 1][weapon.techLevel - 1] / len(bbData.weaponObjsByTL[weapon.techLevel - 1])) * 100)

    for module in bbData.builtInModuleObjs.values():
        module.shopSpawnRate = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[module.techLevel - 1][module.techLevel - 1] / len(bbData.moduleObjsByTL[module.techLevel - 1])) * 100)

    for turret in bbData.builtInTurretObjs.values():
        turret.shopSpawnRate = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[turret.techLevel - 1][turret.techLevel - 1] / len(bbData.turretObjsByTL[turret.techLevel - 1])) * 100)



    bbGlobals.newBountiesTTDB = TimedTaskHeap.TimedTaskHeap()
    # Databases
    bbGlobals.usersDB = loadUsersDB(bbConfig.userDBPath)
    bbGlobals.guildsDB = loadGuildsDB(bbConfig.guildDBPath)

    for guild in bbGlobals.guildsDB.getGuilds():
        if guild.hasBountyBoardChannel:
            await guild.bountyBoardChannel.init(bbGlobals.client, bbData.bountyFactions)

    # for currentUser in bbGlobals.usersDB.users.values():
    #     currentUser.validateLoadout()

    print('We have logged in as {0.user}'.format(bbGlobals.client))
    await bbGlobals.client.change_presence(activity=discord.Game("Galaxy on Fire 2™ Full HD"))
    # bot is now logged in
    botLoggedIn = True
    
    bbGlobals.shopRefreshTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.shopRefreshStockPeriod), autoReschedule=True, expiryFunction=refreshAndAnnounceAllShopStocks)
    bbGlobals.dbSaveTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.savePeriod), autoReschedule=True, expiryFunction=saveAllDBs)

    bbGlobals.duelRequestTTDB = TimedTaskHeap.TimedTaskHeap()

    if bbConfig.timedTaskCheckingType not in ["fixed", "dynamic"]:
        raise ValueError("bbConfig: Invalid timedTaskCheckingType '" +
                         bbConfig.timedTaskCheckingType + "'")


    bbGlobals.reactionMenusTTDB = TimedTaskHeap.TimedTaskHeap()

    if not path.exists(bbConfig.reactionMenusDBPath):
        try:
            f = open(bbConfig.reactionMenusDBPath, 'x')
            f.write("{}")
            f.close()
        except IOError as e:
            bbLogger.log("main","on_ready","IOError creating reactionMenuDB save file: " + e.__class__.__name__, trace=traceback.format_exc())

    bbGlobals.reactionMenusDB = await loadReactionMenusDB(bbConfig.reactionMenusDBPath)

    # bbGlobals.guildsDB.addGuildID(733652363235033088)

    # TODO: find next closest task with min over heap[0] for all task DBs and delay by that amount
    # newTaskAdded = False
    # nextTask

    # execute regular tasks while the bot is logged in
    while botLoggedIn:
        if bbConfig.timedTaskCheckingType == "fixed":
            await asyncio.sleep(bbConfig.timedTaskLatenessThresholdSeconds)
        # elif bbConfig.timedTaskCheckingType == "dynamic":

        await bbGlobals.shopRefreshTT.doExpiryCheck()

        await bbGlobals.newBountiesTTDB.doTaskChecking()

        await bbGlobals.dbSaveTT.doExpiryCheck()

        await bbGlobals.duelRequestTTDB.doTaskChecking()

        await bbGlobals.reactionMenusTTDB.doTaskChecking()


@bbGlobals.client.event
async def on_message(message : discord.Message):
    """Called every time a message is sent in a server that the bot has joined
    Currently handles:
    - command calling

    :param discord.Message message: The message that triggered this command on sending
    """
    # ignore messages sent by bots
    if message.author.bot:
        return

    try:
        if "bountybot" in message.content or bbGlobals.client.user in message.mentions:
            await message.add_reaction("👀")
        if "<:tex:723331420919169036>" in message.content:
            await message.add_reaction("<:tex:723331420919169036>")
    except discord.Forbidden:
        pass
    except discord.HTTPException:
        pass

    if message.content == "!trade <@!212542588643835905>":
        inv = bbInventory.bbInventory()
        inv.addItem(bbData.builtInModuleObjs["E2 Exoclad"])
        inv.addItem(bbData.builtInModuleObjs["Medium Cabin"])
        menuMsg = await message.channel.send("‎")
        menu = ReactionInventoryPicker.ReactionInventoryPicker(menuMsg, inv, 5, titleTxt="**Niker107's Hangar**", footerTxt="React for your desired item", thumb="https://cdn.discordapp.com/avatars/212542588643835905/a20a7a46f7e3e4889363b14f485a3075.png?size=128")
        await menu.updateMessage()
        bbGlobals.reactionMenusDB[menuMsg.id] = menu


    if message.content == "printreactions":
        await message.channel.send(str(bbGlobals.reactionMenusDB.toDict()))

    # For any messages beginning with bbConfig.commandPrefix
    # New method without space-splitting to allow for prefixes that dont end in a space
    if len(message.content) >= len(bbConfig.commandPrefix) and message.content[0:len(bbConfig.commandPrefix)].lower() == bbConfig.commandPrefix.lower():
        # Old method with space-splitting
        # if message.content.split(" ")[0].lower() == (bbConfig.commandPrefix.rstrip(" ")):
        # replace special apostraphe characters with the universal '
        msgContent = message.content.replace("‘", "'").replace("’", "'")

        # split the message into command and arguments
        if len(msgContent[len(bbConfig.commandPrefix):]) > 0:
            command = msgContent[len(bbConfig.commandPrefix):].split(" ")[
                0]
            args = msgContent[len(
                bbConfig.commandPrefix) + len(command) + 1:]

        # if no command is given, ignore the message
        else:
            return

        # Debug: Print the recognised command args strings
        # print("COMMAND '" + command + "'")
        # print("ARGS '" + args + "'")

        # infer the message author's permissions
        if message.author.id in bbConfig.developers:
            accessLevel = 2
        elif message.author.permissions_in(message.channel).administrator:
            accessLevel = 1
        else:
            accessLevel = 0

        # Chek whether the command was requested in DMs
        isDM = message.channel.type in [
            discord.ChannelType.private, discord.ChannelType.group]

        try:
            # Call the requested command
            if isDM:
                commandFound = await dmCommands.call(command, message, args, accessLevel, isDM=True)
            else:
                commandFound = await bbCommands.call(command, message, args, accessLevel, isDM=False)
        except Exception as e:
            await message.channel.send(":woozy_face: Uh oh, something went wrong! The error has been logged.\nThis command probably won't work until we've looked into it.")
            bbLogger.log("Main", "on_message", "An unexpected error occured when calling command '" +
                            command + "' with args '" + args + "': " + e.__class__.__name__, trace=traceback.format_exc())
            commandFound = True

        # Command not found, send an error message.
        if not commandFound:
            userTitle = bbConfig.accessLevelTitles[accessLevel]
            await message.channel.send(""":question: Can't do that, """ + userTitle + """. Type `""" + bbConfig.commandPrefix + """help` for a list of commands! **o7**""")


@bbGlobals.client.event
async def on_raw_reaction_add(payload : discord.RawReactionActionEvent):
    """Called every time a reaction is added to a message.
    If the message is a reaction menu, and the reaction is an option for that menu, trigger the menu option's behaviour.

    :param discord.RawReactionActionEvent payload: An event describing the message and the reaction added
    """
    if payload.user_id != bbGlobals.client.user.id:
        emoji = lib.emojis.dumbEmojiFromPartial(payload.emoji)
        if emoji.sendable is None:
            return

        message = await bbGlobals.client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
        member = payload.member

        if message.id in bbGlobals.reactionMenusDB and \
                bbGlobals.reactionMenusDB[message.id].hasEmojiRegistered(emoji):
            await bbGlobals.reactionMenusDB[message.id].reactionAdded(emoji, member)
            # await bbGlobals.reactionMenusDB[message.id].updateMessage()


@bbGlobals.client.event
async def on_raw_reaction_remove(payload : discord.RawReactionActionEvent):
    """Called every time a reaction is removed from a message.
    If the message is a reaction menu, and the reaction is an option for that menu, trigger the menu option's behaviour.

    :param discord.RawReactionActionEvent payload: An event describing the message and the reaction removed
    """
    if payload.user_id != bbGlobals.client.user.id:
        emoji = lib.emojis.dumbEmojiFromPartial(payload.emoji)
        if emoji.sendable is None:
            return

        message = await bbGlobals.client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
        member = message.guild.get_member(payload.user_id)

        if message.id in bbGlobals.reactionMenusDB and \
                bbGlobals.reactionMenusDB[message.id].hasEmojiRegistered(emoji):
            await bbGlobals.reactionMenusDB[message.id].reactionRemoved(emoji, member)
            # await bbGlobals.reactionMenusDB[message.id].updateMessage()


@bbGlobals.client.event
async def on_raw_message_delete(payload : discord.RawMessageDeleteEvent):
    """Called every time a message is deleted.
    If the message was a reaction menu, deactivate and unschedule the menu.

    :param discord.RawMessageDeleteEvent payload: An event describing the message deleted.
    """
    if payload.message_id in bbGlobals.reactionMenusDB:
        await bbGlobals.reactionMenusDB[payload.message_id].delete()


@bbGlobals.client.event
async def on_raw_bulk_message_delete(payload : discord.RawBulkMessageDeleteEvent):
    """Called every time a group of messages is deleted.
    If any of the messages were a reaction menus, deactivate and unschedule those menus.

    :param discord.RawBulkMessageDeleteEvent payload: An event describing all messages deleted.
    """
    for msgID in payload.message_ids:
        if msgID in bbGlobals.reactionMenusDB:
            await bbGlobals.reactionMenusDB[msgID].delete()


# Launch the bot!! 🤘🚀
bbGlobals.client.run(bbPRIVATE.botToken)
