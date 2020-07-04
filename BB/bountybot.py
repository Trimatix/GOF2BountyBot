### Discord Imports

import discord
from discord.ext import commands

### Utility Imports

from datetime import datetime, timedelta
import asyncio
import random
# user for leaderboard sorting
import operator

### BountyBot Imports

# may replace these imports with a from . import * at some point
from .bbConfig import bbConfig, bbData, bbPRIVATE
from .bbObjects import bbUser
from .bbObjects.bounties import bbBounty, bbBountyConfig
from .bbObjects.items import bbShip
from .bbObjects.battles import ShipFight, DuelRequest
from .scheduling import TimedTask
from .bbDatabases import bbBountyDB, bbGuildDB, bbUserDB, HeirarchicalCommandsDB
from .scheduling import TimedTaskHeap
from . import bbUtil, ActiveTimedTasks



####### DATABASE METHODS #######


"""
Build a bbUserDB from the specified JSON file.

@param filePath -- path to the JSON file to load. Theoretically, this can be absolute or relative.
"""
def loadUsersDB(filePath):
    return bbUserDB.fromDict(bbUtil.readJSON(filePath))


"""
Build a bbGuildDB from the specified JSON file.

@param filePath -- path to the JSON file to load. Theoretically, this can be absolute or relative.
"""
def loadGuildsDB(filePath):
    return bbGuildDB.fromDict(bbUtil.readJSON(filePath))


"""
Build a bbBountyDB from the specified JSON file.

@param filePath -- path to the JSON file to load. Theoretically, this can be absolute or relative.
"""
def loadBountiesDB(filePath):
    return bbBountyDB.fromDict(bbUtil.readJSON(filePath), bbConfig.maxBountiesPerFaction, dbReload=True)


"""
Save a database object to the specified JSON file.
TODO: child database classes to a single ABC, and type check to that ABC here before saving

@param dbPath -- path to the JSON file to save to. Theoretically, this can be absolute or relative.
@param db -- the database object to save
"""
def saveDB(dbPath, db):
    bbUtil.writeJSON(dbPath, db.toDict())



####### GLOBAL VARIABLES #######


# interface into the discord servers
client = commands.Bot(command_prefix=bbConfig.commandPrefix)
# TODO: This will be needed once discord command decorators are in use
# client.remove_command("help")

# Databases
usersDB = loadUsersDB(bbConfig.userDBPath)
guildsDB = loadGuildsDB(bbConfig.guildDBPath)
bountiesDB = loadBountiesDB(bbConfig.bountyDBPath)

# BountyBot commands DB
bbCommands = HeirarchicalCommandsDB.HeirarchicalCommandsDB()
# Commands usable in DMs
dmCommands = HeirarchicalCommandsDB.HeirarchicalCommandsDB()

# Do not change these!
botLoggedIn = False



####### UTIL FUNCTIONS #######



"""
Get the proper name of a system from a an argument passed by a user

@param arg -- arg passed from user
"""
def getSystemProperName(arg):
    for system in bbData.builtInSystemObjs:
        if arg in system.aliases or arg == system.name.lower():
            return system.name.title()
    return ":x:System not found:x:"



"""
Find the shortest route between two systems.

@param start -- string name of the starting system. Must exist in bbData.builtInSystemObjs
@param end -- string name of the target system. Must exist in bbData.builtInSystemObjs
@return -- list of string system names where the first element is start, the last element is end, and all intermediary systems are adjacent
"""
def makeRoute(start, end):
    return bbUtil.bbAStar(start, end, bbData.builtInSystemObjs)


"""
If a passed userID is valid and shares a common server with the bot,
return the user's name and discriminator.
Otherwise, return the passed userID.

@param userID -- ID to attempt to convert to name and discrim
@return -- The user's name and discriminator if the user is reachable, userID otherwise
"""
def userTagOrDiscrim(userID):
    userObj = client.get_user(int(userID.lstrip("<@!").rstrip(">")))
    if userObj is not None:
        return userObj.name + "#" + userObj.discriminator
    # Return criminal name as a fall back - might replace this with '#UNKNOWNUSER#' at some point.
    print("USERIDNAMEORDISCRIM UNKNOWN USER")
    return userID


"""
If a passed criminal is a player, attempt to return the user's name and discriminator.
Otherwise, return the passed criminal's name.

@param criminal -- criminal whose name to attempt to convert to name and discrim
@return -- The user's name and discriminator if the criminal is a player, criminal.name otherwise

"""
def criminalNameOrDiscrim(criminal):
    if not criminal.isPlayer:
        return criminal.name
    return userTagOrDiscrim(criminal.name)
    

"""
Announce the creation of a new bounty across all joined servers
Messages will be sent to the announceChannels of all guilds in the guildsDB, if they have one

@param newBounty -- the bounty to announce
"""
async def announceNewBounty(newBounty):
    # Create the announcement embed
    bountyEmbed = makeEmbed(titleTxt=criminalNameOrDiscrim(newBounty.criminal), desc="⛓ __New Bounty Available__", col=bbData.factionColours[newBounty.faction], thumb=newBounty.criminal.icon, footerTxt=newBounty.faction.title())
    bountyEmbed.add_field(name="Reward:", value=str(newBounty.reward) + " Credits")
    bountyEmbed.add_field(name="Possible Systems:", value=len(newBounty.route))
    bountyEmbed.add_field(name="See the culprit's route with:", value="`" + bbConfig.commandPrefix + "route " + criminalNameOrDiscrim(newBounty.criminal) + "`", inline=False)
    # Create the announcement text
    msg = "A new bounty is now available from **" + newBounty.faction.title() + "** central command:"

    # Loop over all guilds in the database
    for currentGuild in guildsDB.getGuilds():
        # If the guild has an announceChannel
        if currentGuild.hasAnnounceChannel():
            # ensure the announceChannel is valid
            currentChannel = client.get_channel(currentGuild.getAnnounceChannelId())
            if currentChannel is not None:
                try:
                    if currentGuild.hasBountyNotifyRoleId():
                        # announce to the given channel
                        await currentChannel.send("<@&" + str(currentGuild.getBountyNotifyRoleId()) + "> " + msg, embed=bountyEmbed)
                    else:
                        await currentChannel.send(msg, embed=bountyEmbed)
                except discord.Forbidden:
                    print("FAILED TO ANNOUNCE BOUNTY TO GUILD " + client.get_guild(currentGuild.id).name + " IN CHANNEL " + currentChannel.name)

            # TODO: may wish to add handling for invalid announceChannels - e.g remove them from the bbGuild object


"""
Announce the completion of a bounty across all joined servers
Messages will be sent to the playChannels of all guilds in the guildsDB, if they have one

@param bounty -- the bounty to announce
@param rewards -- the rewards dictionary as defined by bbBounty.calculateRewards
@param winningGuildObj -- the discord Guild object of the guild containing the winning user
@param winningUserId -- the user ID of the discord user that won the bounty
"""
async def announceBountyWon(bounty, rewards, winningGuildObj, winningUserId):
    # Loop over all guilds in the database that have playChannels
    for currentGuild in guildsDB.getGuilds():
        if currentGuild.hasPlayChannel():
            # Create the announcement embed
            rewardsEmbed = makeEmbed(titleTxt="Bounty Complete!",authorName=criminalNameOrDiscrim(bounty.criminal) + " Arrested",icon=bounty.criminal.icon,col=bbData.factionColours[bounty.faction], desc="`Suspect located in '" + bounty.answer + "'`")
            
            # Add the winning user to the embed
            # If the winning user is not in the current guild, use the user's name and discriminator
            if client.get_guild(currentGuild.id).get_member(winningUserId) is None:
                rewardsEmbed.add_field(name="1. Winner, " + str(rewards[winningUserId]["reward"]) + " credits:", value=str(client.get_user(winningUserId)) + " checked " + str(int(rewards[winningUserId]["checked"])) + " system" + ("s" if int(rewards[winningUserId]["checked"]) != 1 else ""), inline=False)
            # If the winning user is in the current guild, use the user's mention
            else:
                rewardsEmbed.add_field(name="1. Winner, " + str(rewards[winningUserId]["reward"]) + " credits:", value="<@" + str(winningUserId) + "> checked " + str(int(rewards[winningUserId]["checked"])) + " system" + ("s" if int(rewards[winningUserId]["checked"]) != 1 else ""), inline=False)
            
            # The index of the current user in the embed
            place = 2
            # Loop over all non-winning users in the rewards dictionary
            for userID in rewards:
                if not rewards[userID]["won"]:
                    # If the current user is not in the current guild, use the user's name and discriminator
                    if client.get_guild(currentGuild.id).get_member(userID) is None:
                        rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value=str(client.get_user(userID)) + " checked " + str(int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[userID]["checked"]) != 1 else ""), inline=False)
                    # Otherwise, use the user's mention
                    else:
                        rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value="<@" + str(userID) + "> checked " + str(int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[userID]["checked"]) != 1 else ""), inline=False)
                    place += 1
            
            # Send the announcement to the current guild's playChannel
            # If this is the winning guild, send a special message!
            if currentGuild.id == winningGuildObj.id:
                await client.get_channel(currentGuild.getPlayChannelId()).send(":trophy: **You win!**\n**" + winningGuildObj.get_member(winningUserId).display_name + "** located and EMP'd **" + bounty.criminal.name + "**, who has been arrested by local security forces. :chains:", embed=rewardsEmbed)
            else:
                await client.get_channel(currentGuild.getPlayChannelId()).send(":trophy: Another server has located **" + bounty.criminal.name + "**!", embed=rewardsEmbed)


"""
Announce the refreshing of shop stocks to all guilds.
Messages will be sent to the playChannels of all guilds in the guildsDB, if they have one
"""
async def announceNewShopStock():
    # loop over all guilds
    for guild in guildsDB.guilds.values():
        # ensure guild has a valid playChannel
        if guild.hasPlayChannel():
            playCh = client.get_channel(guild.getPlayChannelId())
            if playCh is not None:
                # send the announcement
                await playCh.send(":arrows_counterclockwise: The shop stock has been refreshed!")


"""
Build a simple discord embed.

@param titleTxt -- The title of the embed
@param desc -- The description of the embed; appears at the top below the title
@param col -- The colour of the side strip of the embed
@param footerTxt -- Secondary description appearing at the bottom of the embed
@param img -- Smaller image appearing to the left of the title
@param thumb -- larger image appearing to the right of the title
@param authorName -- Secondary title for the embed
@param icon -- another image
TODO: Correct these descriptions for images, can't remember which is which right now
@return -- the created discord embed
"""
def makeEmbed(titleTxt="",desc="",col=discord.Colour.blue(), footerTxt="", img="", thumb="", authorName="", icon=""):
    embed = discord.Embed(title=titleTxt, description=desc, colour=col)
    if footerTxt != "": embed.set_footer(text=footerTxt)
    embed.set_image(url=img)
    if thumb != "": embed.set_thumbnail(url=thumb)
    if icon != "": embed.set_author(name=authorName, icon_url=icon)
    return embed


"""
Construct a datetime.timedelta from a dictionary,
transforming keys into keyword arguments fot the timedelta constructor.

@param timeDict -- dictionary containing measurements for each time interval. i.e weeks, days, hours, minutes, seconds, microseconds and milliseconds. all are optional and case sensitive.
@return -- a timedelta with all of the attributes requested in the dictionary.
"""
def timeDeltaFromDict(timeDict):
    return timedelta(   weeks=timeDict["weeks"] if "weeks" in timeDict else 0,
                        days=timeDict["days"] if "days" in timeDict else 0,
                        hours=timeDict["hours"] if "hours" in timeDict else 0,
                        minutes=timeDict["minutes"] if "minutes" in timeDict else 0,
                        seconds=timeDict["seconds"] if "seconds" in timeDict else 0,
                        microseconds=timeDict["microseconds"] if "microseconds" in timeDict else 0,
                        milliseconds=timeDict["milliseconds"] if "milliseconds" in timeDict else 0)


"""
Return the string extension for an integer, e.g 'th' or 'rd'.

@param num -- The integer to find the extension for
@return -- string containing a number extension from bbData.numExtensions
"""
def getNumExtension(num):
    return bbData.numExtensions[int(str(num)[-1])] if not (num > 10 and num < 20) else "th"


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


def getFixedDelay(delayDict):
    return timeDeltaFromDict(delayDict)


def getFixedDailyTime(delayDict):
    return (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timeDeltaFromDict(delayDict)) - datetime.utcnow()


# TODO: Convert to random across two dicts
def getRandomDelaySeconds(minmaxDict):
    return timedelta(seconds=random.randint(minmaxDict["min"], minmaxDict["max"]))


async def refreshAndAnnounceAllShopStocks():
    guildsDB.refreshAllShopStocks()
    await announceNewShopStock()


async def spawnAndAnnounceRandomBounty():
    # ensure a new bounty can be created
    if bountiesDB.canMakeBounty():
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB)
        # activate and announce the bounty
        bountiesDB.addBounty(newBounty)
        await announceNewBounty(newBounty)


def saveAllDBs():
    saveDB(bbConfig.userDBPath, usersDB)
    saveDB(bbConfig.bountyDBPath, bountiesDB)
    saveDB(bbConfig.guildDBPath, guildsDB)
    print(datetime.now().strftime("%H:%M:%S: Data saved!"))


async def expireAndAnnounceDuelReq(duelReqDict):
    duelReq = duelReqDict["duelReq"]
    await duelReq.duelTimeoutTask.forceExpire(callExpiryFunc=False)
    if duelReq.sourceBBGuild.hasPlayChannel():
        playCh = client.get_channel(duelReq.sourceBBGuild.getPlayChannelId())
        if playCh is not None:
            await playCh.send(":stopwatch: <@" + str(duelReq.sourceBBUser.id) + ">, your duel challenge for **" + str(client.get_user(duelReq.targetBBUser.id)) + "** has now expired.")
    duelReq.sourceBBUser.removeDuelChallengeObj(duelReq)


def findBBUserDCGuild(user):
    if user.hasLastSeenGuildId:
        lastSeenGuild = client.get_guild(user.lastSeenGuildId)
        if lastSeenGuild is None or lastSeenGuild.get_member(user.id) is None:
            user.hasLastSeenGuildId = False
        else:
            return lastSeenGuild

    if not user.hasLastSeenGuildId:
        for guild in guildsDB.guilds.values():
            lastSeenGuild = client.get_guild(guild.id)
            if lastSeenGuild is not None and lastSeenGuild.get_member(user.id) is not None:
                user.lastSeenGuildId = guild.id
                user.hasLastSeenGuildId = True
                return lastSeenGuild
    
    return None


####### SYSTEM COMMANDS #######



"""
Print an error message when a command is requested that cannot function outside of a guild
"""
async def err_nodm(message, args):
    await message.channel.send(":x: This command can only be used from inside of a server!")



####### USER COMMANDS #######



"""
Print the help strings defined in bbData as an embed.
If a command is provided in args, the associated help string for just that command is printed.

@param message -- the discord message calling the command
@param args -- empty, or a single command name
"""
# @client.command(name='runHelp')
async def cmd_help(message, args):
    helpEmbed = makeEmbed(titleTxt="BountyBot Commands", thumb=client.user.avatar_url_as(size=64))
    page = 0
    maxPage = len(bbData.helpDict)

    if args != "":
        if bbUtil.isInt(args):
            page = int(args)
            if page > maxPage:
                await message.channel.send(":x: There are only " + str(maxPage) + " help pages! Showing page " + str(maxPage) + ":")
                page = maxPage
        elif args.title() in bbData.helpDict.keys():
            page = list(bbData.helpDict.keys()).index(args.title()) + 1
        elif args != "all":
            for section in bbData.helpDict.keys():
                if args in bbData.helpDict[section]:
                    helpEmbed.add_field(name="‎",value="__" + section + "__", inline=False)
                    helpEmbed.add_field(name=bbData.helpDict[section][args][0],value=bbData.helpDict[section][args][1].replace("$COMMANDPREFIX$",bbConfig.commandPrefix), inline=False)
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

    if page == 0:
        helpEmbed.set_footer(text="All Pages")
        for section in bbData.helpDict.keys():
        # section = list(bbData.helpDict.keys())[page - 1]
            helpEmbed.add_field(name="‎",value="__" + section + "__", inline=False)
            for currentCommand in bbData.helpDict[section].values():
                helpEmbed.add_field(name=currentCommand[0],value=currentCommand[1].replace("$COMMANDPREFIX$",bbConfig.commandPrefix), inline=False)

    else:
        helpEmbed.set_footer(text="Page " + str(page) + "/" + str(maxPage))
        section = list(bbData.helpDict.keys())[page - 1]
        helpEmbed.add_field(name="‎",value="__" + section + "__", inline=False)
        for currentCommand in bbData.helpDict[section].values():
            helpEmbed.add_field(name=currentCommand[0],value=currentCommand[1].replace("$COMMANDPREFIX$",bbConfig.commandPrefix), inline=False)
    
    try:
        await sendChannel.send(bbData.helpIntro.replace("$COMMANDPREFIX$",bbConfig.commandPrefix) if page == 1 else "", embed=helpEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.name + "! Please enable DMs from users who are not friends.")
        return

    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji)

bbCommands.register("help", cmd_help)
dmCommands.register("help", cmd_help)


"""
Print a short guide, teaching users how to play bounties.

@param message -- the discord message calling the command
@param args -- ignored
"""
async def cmd_how_to_play(message, args):
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
        if message.guild is None:
            isDM = True
        else:
            isDM = False
            if guildsDB.guildIdExists(message.guild.id):
                requestedBBGuild = guildsDB.getGuild(message.guild.id)
            else:
                requestedBBGuild = guildsDB.addGuildID(message.guild.id)

        howToPlayEmbed = makeEmbed(titleTxt='**How To Play**', desc="This game is based on the *'Most Wanted'* system from Galaxy on Fire 2. If you have played the Supernova addon, this should be familiar!\n\nIf at any time you would like information about a command, use the `" + bbConfig.commandPrefix + "help [command]` command. To see all commands, just use `" + bbConfig.commandPrefix + "help`.\n‎", footerTxt="Have fun! 🚀", thumb='https://cdn.discordapp.com/avatars/699740424025407570/1bfc728f46646fa964c6a77fc0cf2335.webp')
        howToPlayEmbed.add_field(name="1. New Bounties", value="Every 15m - 1h (randomly), bounties are announced" + ((" in <#" + str(requestedBBGuild.getAnnounceChannelId()) + ">.") if not isDM and requestedBBGuild.hasAnnounceChannel() else ".") + "\n• Use `" + bbConfig.commandPrefix + "bounties` to see the currently active bounties.\n• Criminals spawn in a system somewhere on the `" + bbConfig.commandPrefix + "map`.\n• To view a criminal's current route *(possible systems)*, use `" + bbConfig.commandPrefix + "route [criminal]`.\n‎", inline=False)
        howToPlayEmbed.add_field(name="2. System Checking", value="Now that we know where our criminal could be, we can check a system with `" + bbConfig.commandPrefix + "check [system]`.\nThis system will now be crossed out in the criminal's `" + bbConfig.commandPrefix + "route`, so we know not to check there.\n\n> Didn't win the bounty? No worries!\nYou will be awarded credits for helping *narrow down the search*.\n‎", inline=False)
        howToPlayEmbed.add_field(name="3. Items", value="Now that you've got some credits, try customising your `" + bbConfig.commandPrefix + "loadout`!\n• You can see your inventory of inactive items in the `" + bbConfig.commandPrefix + "hangar`.\n• You can `" + bbConfig.commandPrefix + "buy` more items from the `" + bbConfig.commandPrefix + "shop`.\n‎", inline=False)
        howToPlayEmbed.add_field(name="Extra Notes/Tips", value="• Bounties are shared across all servers, everyone is competing to find them!\n• Each server has its own `" + bbConfig.commandPrefix + "shop`. The shops refresh every *12 hours.*\n• Is a criminal, item or system name too long? Use an alias instead! You can see aliases with `" + bbConfig.commandPrefix + "info`.\n• Having trouble getting to new bounties in time? Try out the new `" + bbConfig.commandPrefix + "notify bounties` command!", inline=False)

        await sendChannel.send(embed=howToPlayEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.name + "! Please enable DMs from users who are not friends.")
        return

    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji)

bbCommands.register("how-to-play", cmd_how_to_play)
dmCommands.register("how-to-play", cmd_how_to_play)


"""
say hello!

@param message -- the discord message calling the command
@param args --ignored
"""
async def cmd_hello(message, args):
    await message.channel.send("Greetings, pilot! **o7**")
    
bbCommands.register("hello", cmd_hello)
dmCommands.register("hello", cmd_hello)


"""
print the balance of the specified user, use the calling user if no user is specified.

@param message -- the discord message calling the command
@param args -- string, can be empty or contain a user mention
"""
async def cmd_balance(message, args):
    # If no user is specified, send the balance of the calling user
    if args == "":
        if not usersDB.userIDExists(message.author.id):
            usersDB.addUser(message.author.id)
        await message.channel.send(":moneybag: **" + message.author.name + "**, you have **" + str(usersDB.getUser(message.author.id).credits) + " Credits**.")
    
    # If a user is specified
    else:
        # Verify the passed user tag
        if not bbUtil.isMention(args) and not bbUtil.isInt(args):
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return
        if bbUtil.isMention(args):
            # Get the discord user object for the given tag
            requestedUser = client.get_user(int(args.lstrip("<@!").rstrip(">")))
        else:
            requestedUser = client.get_user(int(args))
        if requestedUser is None:
            await message.channel.send(":x: Unknown user!")
            return
        # ensure that the user is in the users database
        if not usersDB.userIDExists(requestedUser.id):
            usersDB.addUser(requestedUser.id)
        # send the user's balance
        await message.channel.send(":moneybag: **" + requestedUser.name + "** has **" + str(usersDB.getUser(requestedUser.id).credits) + " Credits**.")
    
bbCommands.register("balance", cmd_balance)
bbCommands.register("bal", cmd_balance)
bbCommands.register("credits", cmd_balance)

dmCommands.register("balance", cmd_balance)
dmCommands.register("bal", cmd_balance)
dmCommands.register("credits", cmd_balance)


"""
print the stats of the specified user, use the calling user if no user is specified.

@param message -- the discord message calling the command
@param args -- string, can be empty or contain a user mention
"""
async def cmd_stats(message, args):
    # if no user is specified
    if args == "":
        # create the embed
        statsEmbed = makeEmbed(col=bbData.factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=message.author.name, footerTxt="Pilot number #" + message.author.discriminator, thumb=message.author.avatar_url_as(size=64))
        # If the calling user is not in the database, don't bother adding them just print zeroes.
        if not usersDB.userIDExists(message.author.id):
            statsEmbed.add_field(name="Credits balance:",value=0, inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=0, inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=0, inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=0, inline=True)
        # If the calling user is in the database, print the stats stored in the user's database entry
        else:
            userObj = usersDB.getUser(message.author.id)
            statsEmbed.add_field(name="Credits balance:",value=str(userObj.credits), inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=str(userObj.lifetimeCredits), inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=str(userObj.systemsChecked), inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=str(userObj.bountyWins), inline=True)

        # send the stats embed
        await message.channel.send(embed=statsEmbed)
        return
    
    # If a user is specified
    else:
        # verify the user mention
        if not bbUtil.isMention(args) and not bbUtil.isInt(args):
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return

        if bbUtil.isMention(args):
            # Get the discord user object for the given tag
            requestedUser = client.get_user(int(args.lstrip("<@!").rstrip(">")))
        else:
            requestedUser = client.get_user(int(args))
        # ensure the mentioned user could be found
        if requestedUser is None:
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return

        # create the stats embed
        statsEmbed = makeEmbed(col=bbData.factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=requestedUser.name, footerTxt="Pilot number #" + requestedUser.discriminator, thumb=requestedUser.avatar_url_as(size=64))
        # If the requested user is not in the database, don't bother adding them just print zeroes
        if not usersDB.userIDExists(requestedUser.id):
            statsEmbed.add_field(name="Credits balance:",value=0, inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=0, inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=0, inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=0, inline=True)
        # Otherwise, print the stats stored in the user's database entry
        else:
            userObj = usersDB.getUser(requestedUser.id)
            statsEmbed.add_field(name="Credits balance:",value=str(userObj.credits), inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=str(userObj.lifetimeCredits), inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=str(userObj.systemsChecked), inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=str(userObj.bountyWins), inline=True)
        
        # send the stats embed
        await message.channel.send(embed=statsEmbed)
    
bbCommands.register("stats", cmd_stats)
dmCommands.register("stats", cmd_stats)


"""
send the image of the GOF2 starmap. If -g is passed, send the grid image

@param message -- the discord message calling the command
@param args -- string, can be empty or contain -g
"""
async def cmd_map(message, args):
    # If -g is specified, send the image with grid overlay
    if args == "-g":
        await message.channel.send(bbData.mapImageWithGraphLink)
    # otherwise, send the image with no grid overlay
    else:
        await message.channel.send(bbData.mapImageNoGraphLink)
    
bbCommands.register("map", cmd_map)
dmCommands.register("map", cmd_map)


"""
⚠ WARNING: MARKED FOR CHANGE ⚠
The following function is provisional and marked as planned for overhaul.
Details: Criminal fights are to switch algorithm, using bbObjects.items.battles as a base. Criminals are to be assigned
         Procedurally generated ships based on a difficulty rating (by direct extension of the items' rarity rankings from bbConfig.__init__)

Check a system for bounties and handle rewards

@param message -- the discord message calling the command
@param args -- string containing one system to check
"""
async def cmd_check(message, args):
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

    # ensure the calling user is in the users database
    if not usersDB.userIDExists(message.author.id):
        usersDB.addUser(message.author.id)
    
    if not usersDB.getUser(message.author.id).activeShip.hasWeaponsEquipped():
        await message.channel.send(":x: Your ship has no weapons equipped!")
        return

    # ensure the calling user is not on checking cooldown
    if datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd) < datetime.utcnow():
        bountyWon = False
        # Loop over all bounties in the database
        for fac in bountiesDB.getFactions():
            # list of completed bounties to remove from the bounties database
            toPop = []
            for bounty in bountiesDB.getFactionBounties(fac):

                # Check the passed system in current bounty
                # If current bounty resides in the requested system
                if bounty.check(requestedSystem, message.author.id) == 3:
                    bountyWon = True
                    # reward all contributing users
                    rewards = bounty.calcRewards()
                    for userID in rewards:
                        usersDB.getUser(userID).credits += rewards[userID]["reward"]
                        usersDB.getUser(userID).lifetimeCredits += rewards[userID]["reward"]
                    # add this bounty to the list of bounties to be removed
                    toPop += [bounty]
                    # Announce the bounty has ben completed
                    await announceBountyWon(bounty, rewards, message.guild, message.author.id)

            # remove all completed bounties
            for bounty in toPop:
                bountiesDB.removeBountyObj(bounty)

        # If a bounty was won, print a congratulatory message
        if bountyWon:
            usersDB.getUser(message.author.id).bountyWins += 1
            await message.channel.send(":moneybag: **" + message.author.name + "**, you now have **" + str(usersDB.getUser(message.author.id).credits) + " Credits!**")
        # If no bounty was won, print an error message
        else:
            outmsg = ":telescope: **" + message.author.name + "**, you did not find any criminals in **" + getSystemProperName(args) + "**!"
            # Check if any bounties are close to the requested system in their route, defined by bbConfig.closeBountyThreshold
            for fac in bountiesDB.getFactions():
                for bounty in bountiesDB.getFactionBounties(fac):
                    if requestedSystem in bounty.route:
                        if 0 < bounty.route.index(bounty.answer) - bounty.route.index(requestedSystem) < bbConfig.closeBountyThreshold:
                            # Print any close bounty names
                            outmsg += "\n       • Local security forces spotted **" + criminalNameOrDiscrim(bounty.criminal) + "** here recently. "
            for currentGuild in guildsDB.getGuilds():
                await client.get_channel(currentGuild.getPlayChannelId()).send(outmsg)

        # Increment the calling user's systemsChecked statistic
        usersDB.getUser(message.author.id).systemsChecked += 1
        # Put the calling user on checking cooldown
        usersDB.getUser(message.author.id).bountyCooldownEnd = (datetime.utcnow() + timedelta(minutes=bbConfig.checkCooldown["minutes"])).timestamp()
    
    # If the calling user is on checking cooldown
    else:
        # Print an error message with the remaining time on the calling user's cooldown
        diff = datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd) - datetime.utcnow()
        minutes = int(diff.total_seconds() / 60)
        seconds = int(diff.total_seconds() % 60)
        await message.channel.send(":stopwatch: **" + message.author.name + "**, your *Khador Drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")
    
bbCommands.register("check", cmd_check)
bbCommands.register("search", cmd_check)
dmCommands.register("check", err_nodm)
dmCommands.register("search", err_nodm)


"""
List a summary of all currently active bounties.
If a faction is specified, print a more detailed summary of that faction's active bounties

@param message -- the discord message calling the command
@param args -- string, can be empty or contain a faction
"""
async def cmd_bounties(message, args):
    # If no faction is specified
    if args == "":
        outmessage = "__**Active Bounties**__\nTimes given in UTC. See more detailed information with `" + bbConfig.commandPrefix + "bounties <faction>`\n```css"
        preLen = len(outmessage)
        # Collect and print summaries of all active bounties
        for fac in bountiesDB.getFactions():
            if bountiesDB.hasBounties(faction=fac):
                outmessage += "\n • [" + fac.title() + "]: "
                for bounty in bountiesDB.getFactionBounties(fac):
                    outmessage += criminalNameOrDiscrim(bounty.criminal) + ", "
                outmessage = outmessage[:-2]
        # If no active bounties were found, print an error
        if len(outmessage) == preLen:
            outmessage += "\n[  No currently active bounties! Please check back later.  ]"
        await message.channel.send(outmessage + "```")
    
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
        if not bountiesDB.hasBounties(faction=requestedFaction):
            await message.channel.send(":stopwatch: There are no **" + requestedFaction.title() + "** bounties active currently!")
        else:
            # Collect and print summaries of the requested faction's active bounties
            outmessage = "__**Active " + requestedFaction.title() + " Bounties**__\nTimes given in UTC.```css"
            for bounty in bountiesDB.getFactionBounties(requestedFaction):
                endTimeStr = datetime.utcfromtimestamp(bounty.endTime).strftime("%B %d %H %M %S").split(" ")
                outmessage += "\n • [" + criminalNameOrDiscrim(bounty.criminal) + "]" + " " * (bbData.longestBountyNameLength + 1 - len(criminalNameOrDiscrim(bounty.criminal))) + ": " + str(int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + getNumExtension(int(endTimeStr[1])) + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                if endTimeStr[4] != "00":
                    outmessage += ":" + endTimeStr[4]
                else:
                    outmessage += "   "
                outmessage += " - " + str(len(bounty.route)) + " possible system"
                if len(bounty.route) != 1:
                    outmessage += "s"
            await message.channel.send(outmessage + "```\nTrack down criminals and **win credits** using `" + bbConfig.commandPrefix + "route` and `" + bbConfig.commandPrefix + "check`!")

bbCommands.register("bounties", cmd_bounties)
dmCommands.register("bounties", cmd_bounties)


"""
Display the current route of the requested criminal

@param message -- the discord message calling the command
@param args -- string containing a criminal name or alias
"""
async def cmd_route(message, args):
    # verify a criminal was specified
    if args == "":
        await message.channel.send(":x: Please provide the criminal name! E.g: `" + bbConfig.commandPrefix + "route Kehnor`")
        return

    requestedBountyName = args
    # if the named criminal is wanted
    if bountiesDB.bountyNameExists(requestedBountyName.lower()):
        # display their route
        bounty = bountiesDB.getBounty(requestedBountyName.lower())
        outmessage = "**" + criminalNameOrDiscrim(bounty.criminal) + "**'s current route:\n> "
        for system in bounty.route:
            outmessage += " " + ("~~" if bounty.checked[system] != -1 else "") + system + ("~~" if bounty.checked[system] != -1 else "") + ","
        outmessage = outmessage[:-1] + ". :rocket:"
        await message.channel.send(outmessage)
    # if the named criminal is not wanted
    else:
        # display an error
        outmsg = ":x: That pilot isn't on any bounty boards! :clipboard:"
        # accept user name + discrim instead of tags to avoid mention spam
        if bbUtil.isMention(requestedBountyName):
            outmsg += "\n:warning: **Don't tag users**, use their name and ID number like so: `" + bbConfig.commandPrefix + "route Trimatix#2244`"
        await message.channel.send(outmsg)
    
bbCommands.register("route", cmd_route)
dmCommands.register("route", cmd_route)


"""
display the shortest route between two systems

@param message -- the discord message calling the command
@param args -- string containing the start and end systems, separated by a comma and a space
"""
async def cmd_make_route(message, args):
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
    for currentSyst in makeRoute(startSyst, endSyst):
        routeStr += currentSyst + ", "
    if routeStr.startswith("#"):
        await message.channel.send(":x: ERR: Processing took too long! :stopwatch:")
    elif routeStr.startswith("!"):
        await message.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
    elif startSyst == endSyst:
        await message.channel.send(":thinking: You're already there, pilot!")
    else:
        await message.channel.send("Here's the shortest route from **" + startSyst + "** to **" + endSyst + "**:\n> " + routeStr[:-2] + " :rocket:")
    
bbCommands.register("make-route", cmd_make_route)
dmCommands.register("make-route", cmd_make_route)


"""
return statistics about a specified system

@param message -- the discord message calling the command
@param args -- string containing a system in the GOF2 starmap
"""
async def cmd_system(message, args):
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
        statsEmbed = makeEmbed(col=bbData.factionColours[systObj.faction], desc="__System Information__", titleTxt=systObj.name, footerTxt=systObj.faction.title(), thumb=bbData.factionIcons[systObj.faction])
        statsEmbed.add_field(name="Security Level:",value=bbData.securityLevels[systObj.security].title())
        statsEmbed.add_field(name="Neighbour Systems:", value=neighboursStr)
        # list the system's aliases as a string
        if len(systObj.aliases) > 1:
            aliasStr = ""
            for alias in systObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        # list the system's wiki if one exists
        if systObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + systObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)
    
# bbCommands.register("system", cmd_system)


"""
return statistics about a specified inbuilt criminal

@param message -- the discord message calling the command
@param args -- string containing a criminal name
"""
async def cmd_criminal(message, args):
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
        statsEmbed = makeEmbed(col=bbData.factionColours[criminalObj.faction], desc="__Criminal File__", titleTxt=criminalObj.name, thumb=criminalObj.icon)
        statsEmbed.add_field(name="Wanted By:",value=criminalObj.faction.title() + "s")
        # include the criminal's aliases and wiki if they exist
        if len(criminalObj.aliases) > 1:
            aliasStr = ""
            for alias in criminalObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if criminalObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + criminalObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)
    
# bbCommands.register("criminal", cmd_criminal)


"""
return statistics about a specified inbuilt ship

@param message -- the discord message calling the command
@param args -- string containing a ship name
"""
async def cmd_ship(message, args):
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
        statsEmbed = makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"], desc="__Ship File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        statsEmbed.add_field(name="Ship Base Value",value=commaSplitNum(str(itemObj.getValue(shipUpgradesOnly=True))) + " Credits")
        statsEmbed.add_field(name="Armour",value=str(itemObj.getArmour()))
        statsEmbed.add_field(name="Cargo",value=str(itemObj.getCargo()))
        statsEmbed.add_field(name="Handling",value=str(itemObj.getHandling()))
        statsEmbed.add_field(name="Max Primaries",value=str(itemObj.getMaxPrimaries()))
        if len(itemObj.weapons) > 0:
            weaponStr = "*["
            for weapon in itemObj.weapons:
                weaponStr += weapon.name + ", "
            statsEmbed.add_field(name="Equipped Primaries",value=weaponStr[:-2] + "]*")
        statsEmbed.add_field(name="Max Secondaries",value=str(itemObj.getNumSecondaries()))
        # if len(itemObj.secondaries) > 0:
        #     secondariesStr = "*["
        #     for secondary in itemObj.secondaries:
        #         secondariesStr += secondary.name + ", "
        #     statsEmbed.add_field(name="Equipped Secondaries",value=secondariesStr[:-2] + "]*")
        statsEmbed.add_field(name="Turret Slots",value=str(itemObj.getMaxTurrets()))
        if len(itemObj.turrets) > 0:
            turretsStr = "*["
            for turret in itemObj.turrets:
                turretsStr += turret.name + ", "
            statsEmbed.add_field(name="Equipped Turrets",value=turretsStr[:-2] + "]*")
        statsEmbed.add_field(name="Modules Slots",value=str(itemObj.getMaxModules()))
        if len(itemObj.modules) > 0:
            modulesStr = "*["
            for module in itemObj.modules:
                modulesStr += module.name + ", "
            statsEmbed.add_field(name="Equipped Modules",value=modulesStr[:-2] + "]*")
        statsEmbed.add_field(name="Shop Spawn Rate",value=str(itemObj.shopSpawnRate) + "%")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)
    
# bbCommands.register("ship", cmd_ship)


"""
return statistics about a specified inbuilt weapon

@param message -- the discord message calling the command
@param args -- string containing a weapon name
"""
async def cmd_weapon(message, args):
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
        statsEmbed = makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"], desc="__Weapon File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        statsEmbed.add_field(name="Value:",value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:",value=str(itemObj.dps))
        statsEmbed.add_field(name="Shop Spawn Rate",value=str(itemObj.shopSpawnRate) + "%")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)
    
# bbCommands.register("weapon", cmd_weapon)


"""
return statistics about a specified inbuilt module

@param message -- the discord message calling the command
@param args -- string containing a module name
"""
async def cmd_module(message, args):
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
        statsEmbed = makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"], desc="__Module File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        statsEmbed.add_field(name="Value:",value=str(itemObj.value))
        statsEmbed.add_field(name="Stats:",value=str(itemObj.statsStringShort()))
        statsEmbed.add_field(name="Shop Spawn Rate",value=str(itemObj.shopSpawnRate) + "%")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)
    
# bbCommands.register("module", cmd_module)


"""
return statistics about a specified inbuilt turret

@param message -- the discord message calling the command
@param args -- string containing a turret name
"""
async def cmd_turret(message, args):
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
        statsEmbed = makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"], desc="__Turret File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        statsEmbed.add_field(name="Value:",value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:",value=str(itemObj.dps))
        statsEmbed.add_field(name="Shop Spawn Rate",value=str(itemObj.shopSpawnRate) + "%")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)
    
# bbCommands.register("turret", cmd_turret)


"""
return statistics about a specified inbuilt commodity

@param message -- the discord message calling the command
@param args -- string containing a commodity name
"""
async def cmd_commodity(message, args):
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
        statsEmbed = makeEmbed(col=bbData.factionColours[itemObj.faction], desc="__Item File__", titleTxt=itemObj.name, thumb=itemObj.icon)
        statsEmbed.add_field(name="Wanted By:",value=itemObj.faction.title() + "s")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)
    
# bbCommands.register("commodity", cmd_commodity)


async def cmd_info(message, args):
    if args == "":
        await message.channel.send(":x: Please give an object type to look up! (system/criminal/ship/weapon/module/turret/commodity)")
        return
    
    argsSplit = args.split(" ")
    if argsSplit[0] not in ["system","criminal","ship","weapon","module","turret","commodity"]:
        await message.channel.send(":x: Invalid object type! (system/criminal/ship/weapon/module/turret/commodity)")
        return
    
    if argsSplit[0] == "system":
        await cmd_system(message, args[7:])
    elif argsSplit[0] == "criminal":
        await cmd_criminal(message, args[9:])
    elif argsSplit[0] == "ship":
        await cmd_ship(message, args[5:])
    elif argsSplit[0] == "weapon":
        await cmd_weapon(message, args[7:])
    elif argsSplit[0] == "module":
        await cmd_module(message, args[7:])
    elif argsSplit[0] == "turret":
        await cmd_turret(message, args[7:])
    elif argsSplit[0] == "commodity":
        await cmd_commodity(message, args[10:])
    else:
        await message.channel.send(":x: Unknown object type! (system/criminal/ship/weapon/module/turret/commodity)")

bbCommands.register("info", cmd_info)
dmCommands.register("info", cmd_info)


"""
display leaderboards for different statistics
if no arguments are given, display the local leaderboard for pilot value (value of loadout, hangar and balance, summed)
if -g is given, display the appropriate leaderbaord across all guilds
if -c is given, display the leaderboard for current balance
if -s is given, display the leaderboard for systems checked
if -w is given, display the leaderboard for bounties won

@param message -- the discord message calling the command
@param args -- string containing the arguments the user passed to the command
"""
async def cmd_leaderboard(message, args):
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
    for user in usersDB.getUsers():
        if (globalBoard and client.get_user(user.id) is not None) or (not globalBoard and message.guild.get_member(user.id) is not None):
            inputDict[user.id] = user.getStatByName(stat)
    sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]

    # build the leaderboard embed
    leaderboardEmbed = makeEmbed(titleTxt=boardTitle, authorName=boardScope, icon=bbData.winIcon, col = bbData.factionColours["neutral"], desc=boardDesc)

    # add all users to the leaderboard embed with places and values
    externalUser = False
    first = True
    for place in range(min(len(sortedUsers), 10)):
        # handling for global leaderboards and users not in the local guild
        if globalBoard and message.guild.get_member(sortedUsers[place][0]) is None:
            leaderboardEmbed.add_field(value="*" + str(place + 1) + ". " + str(client.get_user(sortedUsers[place][0])), name=("⭐ " if first else "") + str(sortedUsers[place][1]) + " " + (boardUnit if sortedUsers[place][1] == 1 else boardUnits), inline=False)
            externalUser = True
            if first: first = False
        else:
            leaderboardEmbed.add_field(value=str(place + 1) + ". " + message.guild.get_member(sortedUsers[place][0]).mention, name=("⭐ " if first else "") + str(sortedUsers[place][1]) + " " + (boardUnit if sortedUsers[place][1] == 1 else boardUnits), inline=False)
            if first: first = False
    # If at least one external use is on the leaderboard, give a key
    if externalUser:
        leaderboardEmbed.set_footer(text="An `*` indicates a user that is from another server.")
    # send the embed
    await message.channel.send(embed=leaderboardEmbed)
    
bbCommands.register("leaderboard", cmd_leaderboard)
dmCommands.register("leaderboard", err_nodm)


"""
return a page listing the target user's items.
can apply to a specified user, or the calling user if none is specified.
can apply to a type of item (ships, modules, turrets or weapons), or all items if none is specified.
can apply to a page, or the first page if none is specified.
Arguments can be given in any order, and must be separated by a single space.

TODO: try displaying as a discord message rather than embed?
TODO: add icons for ships and items!?

@param message -- the discord message calling the command
@param args -- string containing the arguments as specified above
"""
async def cmd_hangar(message, args):
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
                if bbUtil.isMention(arg):
                    if foundUser:
                        await message.channel.send(":x: I can only take one user!")
                        return
                    else:
                        requestedUser = client.get_user(int(arg.lstrip("<@!")[:-1]))
                        foundUser = True
                        
                elif arg in bbConfig.validItemNames:
                    if foundItem:
                        await message.channel.send(":x: I can only take one item type (ship/weapon/module/turret)!")
                        return
                    else:
                        item = arg.rstrip("s")
                        foundItem = True

                elif bbUtil.isInt(arg):
                    if client.get_user(int(arg)) is not None and not foundUser:
                        requestedUser = client.get_user(int(args))
                        continue
                    if foundPage:
                        await message.channel.send(":x: I can only take one page number!")
                        return
                    else:
                        page = int(arg)
                        foundPage = True
                else:
                    await message.channel.send(":x: " + str(argNum) + getNumExtension(argNum) + " argument invalid! I can only take a target user, an item type (ship/weapon/module/turret), and a page number!")
                    return
                argNum += 1
    
    if requestedUser is None:
        await message.channel.send(":x: Unrecognised user!")
        return

    if not usersDB.userIDExists(requestedUser.id):
        if not foundUser:
            usersDB.addUser(requestedUser.id)
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

        hangarEmbed = makeEmbed(titleTxt="Hangar", desc=requestedUser.mention, col=bbData.factionColours["neutral"], footerTxt="All items" if item == "all" else item.rstrip("s").title() + "s - page " + str(page), thumb=requestedUser.avatar_url_as(size=64))
        
        hangarEmbed.add_field(name="No Stored Items", value="‎", inline=False)
        await message.channel.send(embed=hangarEmbed)
        return

    else:
        requestedBBUser = usersDB.getUser(requestedUser.id)

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
                await message.channel.send(":x: " + ("The requested pilot" if foundUser else "You") + " only " + ("has" if foundUser else "have") + str(maxPage) + " page(s) of items. Showing page " + str(maxPage) + ":")
                page = maxPage
        
        hangarEmbed = makeEmbed(titleTxt="Hangar", desc=requestedUser.mention, col=bbData.factionColours["neutral"], footerTxt=("All item" if item == "all" else item.rstrip("s").title()) + "s - page " + str(page) + "/" + str(requestedBBUser.numInventoryPages(item, maxPerPage)), thumb=requestedUser.avatar_url_as(size=64))
        firstPlace = maxPerPage * (page - 1) + 1

        if item in ["all", "ship"]:
            for shipNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("ship", page, maxPerPage) + 1):
                if shipNum == firstPlace:
                    hangarEmbed.add_field(name="‎", value="__**Stored Ships**__", inline=False)
                hangarEmbed.add_field(name=str(shipNum) + ". " + requestedBBUser.inactiveShips[shipNum - 1].getNameAndNick(), value=(requestedBBUser.inactiveShips[shipNum - 1].emoji if requestedBBUser.inactiveShips[shipNum - 1].hasEmoji else "") + requestedBBUser.inactiveShips[shipNum - 1].statsStringShort(), inline=False)
        
        if item in ["all", "weapon"]:
            for weaponNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("weapon", page, maxPerPage) + 1):
                if weaponNum == firstPlace:
                    hangarEmbed.add_field(name="‎", value="__**Stored Weapons**__", inline=False)
                hangarEmbed.add_field(name=str(weaponNum) + ". " + requestedBBUser.inactiveWeapons[weaponNum - 1].name, value=(requestedBBUser.inactiveWeapons[weaponNum - 1].emoji if requestedBBUser.inactiveWeapons[weaponNum - 1].hasEmoji else "") + requestedBBUser.inactiveWeapons[weaponNum - 1].statsStringShort(), inline=False)

        if item in ["all", "module"]:
            for moduleNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("module", page, maxPerPage) + 1):
                if moduleNum == firstPlace:
                    hangarEmbed.add_field(name="‎", value="__**Stored Modules**__", inline=False)
                hangarEmbed.add_field(name=str(moduleNum) + ". " + requestedBBUser.inactiveModules[moduleNum - 1].name, value=(requestedBBUser.inactiveModules[moduleNum - 1].emoji if requestedBBUser.inactiveModules[moduleNum - 1].hasEmoji else "") + requestedBBUser.inactiveModules[moduleNum - 1].statsStringShort(), inline=False)

        if item in ["all", "turret"]:
            for turretNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("turret", page, maxPerPage) + 1):
                if turretNum == firstPlace:
                    hangarEmbed.add_field(name="‎", value="__**Stored Turrets**__", inline=False)
                hangarEmbed.add_field(name=str(turretNum) + ". " + requestedBBUser.inactiveTurrets[turretNum - 1].name, value=(requestedBBUser.inactiveTurrets[turretNum - 1].emoji if requestedBBUser.inactiveTurrets[turretNum - 1].hasEmoji else "") + requestedBBUser.inactiveTurrets[turretNum - 1].statsStringShort(), inline=False)

        try:
            await sendChannel.send(embed=hangarEmbed)
            if sendDM:
                await message.add_reaction(bbConfig.dmSentEmoji)
        except discord.Forbidden:
            await message.channel.send(":x: I can't DM you, " + message.author.name + "! Please enable DMs from users who are not friends.")

bbCommands.register("hangar", cmd_hangar)
bbCommands.register("hanger", cmd_hangar)

dmCommands.register("hangar", cmd_hangar)
dmCommands.register("hanger", cmd_hangar)


"""
list the current stock of the bbShop owned by the guild containing the sent message.
Can specify an item type to list. TODO: Make specified item listings more detailed as in !bb bounties

@param message -- the discord message calling the command
@param args -- either empty string, or one of bbConfig.validItemNames
"""
async def cmd_shop(message, args):
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

    requestedShop = guildsDB.getGuild(message.guild.id).shop
    shopEmbed = makeEmbed(titleTxt="Shop", desc=message.guild.name, footerTxt="All items" if item == "all" else (item + "s").title(), thumb="https://cdn.discordapp.com/icons/" + str(message.guild.id) + "/" + message.guild.icon + ".png?size=64")

    if item in ["all", "ship"]:
        for shipNum in range(1, len(requestedShop.shipsStock) + 1):
            if shipNum == 1:
                shopEmbed.add_field(name="‎", value="__**Ships**__", inline=False)
            shopEmbed.add_field(value=(requestedShop.shipsStock[shipNum - 1].emoji if requestedShop.shipsStock[shipNum - 1].hasEmoji else "") + " " + commaSplitNum(str(requestedShop.shipsStock[shipNum - 1].getValue())) + " Credits\n" + requestedShop.shipsStock[shipNum - 1].statsStringShort(), name=str(shipNum) + ". " + "**" + requestedShop.shipsStock[shipNum - 1].getNameAndNick() + "**", inline=True)

    if item in ["all", "weapon"]:
        for weaponNum in range(1, len(requestedShop.weaponsStock) + 1):
            if weaponNum == 1:
                shopEmbed.add_field(name="‎", value="__**Weapons**__", inline=False)
            shopEmbed.add_field(value=(requestedShop.weaponsStock[weaponNum - 1].emoji if requestedShop.weaponsStock[weaponNum - 1].hasEmoji else "") + " " + commaSplitNum(str(requestedShop.weaponsStock[weaponNum - 1].value)) + " Credits\n" + requestedShop.weaponsStock[weaponNum - 1].statsStringShort(), name=str(weaponNum) + ". " + "**" + requestedShop.weaponsStock[weaponNum - 1].name + "**", inline=True)

    if item in ["all", "module"]:
        for moduleNum in range(1, len(requestedShop.modulesStock) + 1):
            if moduleNum == 1:
                shopEmbed.add_field(name="‎", value="__**Modules**__", inline=False)
            shopEmbed.add_field(value=(requestedShop.modulesStock[moduleNum - 1].emoji if requestedShop.modulesStock[moduleNum - 1].hasEmoji else "") + " " + commaSplitNum(str(requestedShop.modulesStock[moduleNum - 1].value)) + " Credits\n" + requestedShop.modulesStock[moduleNum - 1].statsStringShort(), name=str(moduleNum) + ". " + "**" + requestedShop.modulesStock[moduleNum - 1].name + "**", inline=True)

    if item in ["all", "turret"]:
        for turretNum in range(1, len(requestedShop.turretsStock) + 1):
            if turretNum == 1:
                shopEmbed.add_field(name="‎", value="__**Turrets**__", inline=False)
            shopEmbed.add_field(value=(requestedShop.turretsStock[turretNum - 1].emoji if requestedShop.turretsStock[turretNum - 1].hasEmoji else "") + " " + commaSplitNum(str(requestedShop.turretsStock[turretNum - 1].value)) + " Credits\n" + requestedShop.turretsStock[turretNum - 1].statsStringShort(), name=str(turretNum) + ". " + "**" + requestedShop.turretsStock[turretNum - 1].name + "**", inline=True)

    try:
        await sendChannel.send(embed=shopEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.name + "! Please enable DMs from users who are not friends.")
        return
    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji)

bbCommands.register("shop", cmd_shop)
bbCommands.register("store", cmd_shop)

dmCommands.register("shop", err_nodm)
dmCommands.register("store", err_nodm)


"""
list the requested user's currently equipped items.

@param message -- the discord message calling the command
@param args -- either empty string, or a user mention
"""
async def cmd_loadout(message, args):
    requestedUser = message.author
    useDummyData = False
    userFound = False

    if len(args.split(" ")) > 1:
        await message.channel.send(":x: Too many arguments! I can only take a target user!")
        return
    
    if bbUtil.isMention(args) or bbUtil.isInt(args):
        if bbUtil.isMention(args):
            # Get the discord user object for the given tag
            requestedUser = client.get_user(int(args.lstrip("<@!").rstrip(">")))
        else:
            requestedUser = client.get_user(int(args))
        if requestedUser is None:
            await message.channel.send(":x: Unrecognised user!")
            return

    if not usersDB.userIDExists(requestedUser.id):
        if not userFound:
            usersDB.addUser(requestedUser.id)
        else:
            useDummyData = True

    if useDummyData:
        activeShip = bbShip.fromDict(bbUser.defaultShipLoadoutDict)
        loadoutEmbed = makeEmbed(titleTxt="Loadout", desc=requestedUser.mention, col=bbData.factionColours[activeShip.manufacturer] if activeShip.manufacturer in bbData.factionColours else bbData.factionColours["neutral"], thumb=activeShip.icon if activeShip.hasIcon else requestedUser.avatar_url_as(size=64))
        loadoutEmbed.add_field(name="Active Ship:", value=activeShip.name + "\n" + activeShip.statsStringNoItems(), inline=False)
        
        loadoutEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(activeShip.weapons)) + "/" + str(activeShip.getMaxPrimaries()) + "*", inline=False)
        for weaponNum in range(1, len(activeShip.weapons) + 1):
            loadoutEmbed.add_field(name=str(weaponNum) + ". " + activeShip.weapons[weaponNum - 1].name, value=(activeShip.weapons[weaponNum - 1].emoji if activeShip.weapons[weaponNum - 1].hasEmoji else "") + activeShip.weapons[weaponNum - 1].statsStringShort(), inline=True)


        loadoutEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(activeShip.modules)) + "/" + str(activeShip.getMaxModules()) + "*", inline=False)
        for moduleNum in range(1, len(activeShip.modules) + 1):
            loadoutEmbed.add_field(name=str(moduleNum) + ". " + activeShip.modules[moduleNum - 1].name, value=(activeShip.modules[moduleNum - 1].emoji if activeShip.modules[moduleNum - 1].hasEmoji else "") + activeShip.modules[moduleNum - 1].statsStringShort(), inline=True)
        
        
        loadoutEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(activeShip.turrets)) + "/" + str(activeShip.getMaxTurrets()) + "*", inline=False)
        for turretNum in range(1, len(activeShip.turrets) + 1):
            loadoutEmbed.add_field(name=str(turretNum) + ". " + activeShip.turrets[turretNum - 1].name, value=(activeShip.turrets[turretNum - 1].emoji if activeShip.turrets[turretNum - 1].hasEmoji else "") + activeShip.turrets[turretNum - 1].statsStringShort(), inline=True)
        
        await message.channel.send(embed=loadoutEmbed)
        return

    else:
        requestedBBUser = usersDB.getUser(requestedUser.id)
        activeShip = requestedBBUser.activeShip
        loadoutEmbed = makeEmbed(titleTxt="Loadout", desc=requestedUser.mention, col=bbData.factionColours[activeShip.manufacturer] if activeShip.manufacturer in bbData.factionColours else bbData.factionColours["neutral"], thumb=activeShip.icon if activeShip.hasIcon else requestedUser.avatar_url_as(size=64))

        if activeShip is None:
            loadoutEmbed.add_field(name="Active Ship:", value="None", inline=False)
        else:
            loadoutEmbed.add_field(name="Active Ship:", value=activeShip.getNameAndNick() + "\n" + activeShip.statsStringNoItems(), inline=False)

            if activeShip.getMaxPrimaries() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(activeShip.weapons)) + "/" + str(activeShip.getMaxPrimaries()) + "*", inline=False)
                for weaponNum in range(1, len(activeShip.weapons) + 1):
                    loadoutEmbed.add_field(name=str(weaponNum) + ". " + activeShip.weapons[weaponNum - 1].name, value=(activeShip.weapons[weaponNum - 1].emoji if activeShip.weapons[weaponNum - 1].hasEmoji else "") + activeShip.weapons[weaponNum - 1].statsStringShort(), inline=True)

            if activeShip.getMaxModules() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(activeShip.modules)) + "/" + str(activeShip.getMaxModules()) + "*", inline=False)
                for moduleNum in range(1, len(activeShip.modules) + 1):
                    loadoutEmbed.add_field(name=str(moduleNum) + ". " + activeShip.modules[moduleNum - 1].name, value=(activeShip.modules[moduleNum - 1].emoji if activeShip.modules[moduleNum - 1].hasEmoji else "") + activeShip.modules[moduleNum - 1].statsStringShort(), inline=True)
            
            if activeShip.getMaxTurrets() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(activeShip.turrets)) + "/" + str(activeShip.getMaxTurrets()) + "*", inline=False)
                for turretNum in range(1, len(activeShip.turrets) + 1):
                    loadoutEmbed.add_field(name=str(turretNum) + ". " + activeShip.turrets[turretNum - 1].name, value=(activeShip.turrets[turretNum - 1].emoji if activeShip.turrets[turretNum - 1].hasEmoji else "") + activeShip.turrets[turretNum - 1].statsStringShort(), inline=True)
        
        await message.channel.send(embed=loadoutEmbed)

bbCommands.register("loadout", cmd_loadout)
dmCommands.register("loadout", cmd_loadout)


"""
Buy the item of the given item type, at the given index, from the guild's shop.
if "transfer" is specified, the new ship's items are unequipped, and the old ship's items attempt to fill the new ship.
any items left unequipped are added to the user's inactive items lists.
if "sell" is specified, the user's old activeShip is stripped of items and sold to the shop.
"transfer" and "sell" are only valid when buying a ship.

@param message -- the discord message calling the command
@param args -- string containing an item type and an index number, and optionally "transfer", and optionally "sell" separated by a single space
"""
async def cmd_shop_buy(message, args):
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
    requestedShop = guildsDB.getGuild(message.guild.id).shop
    if not bbUtil.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)
    if itemNum > len(requestedShop.getStockByName(item)):
        if len(requestedShop.getStockByName(item)) == 0:
            await message.channel.send(":x: This shop has no " + item + "s in stock!")
        else:
            await message.channel.send(":x: Invalid item number! This shop has " + str(len(requestedShop.getStockByName(item))) + " " + item + "(s).")
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

    if usersDB.userIDExists(message.author.id):
        requestedBBUser = usersDB.getUser(message.author.id)
    else:
        requestedBBUser = usersDB.addUser(message.author.id)

    if item == "ship":
        requestedShip = requestedShop.shipsStock[itemNum - 1]
        newShipValue = requestedShip.getValue()
        activeShip = requestedBBUser.activeShip

        # Check the item can be afforded
        if (not sellOldShip and not requestedShop.userCanAffordShipObj(requestedBBUser, requestedShip)) or \
                (sellOldShip and not requestedShop.amountCanAffordShipObj(requestedBBUser.credits + requestedBBUser.activeShip.getValue(shipUpgradesOnly=transferItems), requestedShip)):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedShip.getValue()) + ")")
            return

        requestedBBUser.inactiveShips.append(requestedShip)
        
        if transferItems:
            requestedBBUser.unequipAll(requestedShip)
            activeShip.transferItemsTo(requestedShip)
            requestedBBUser.unequipAll(activeShip)

        if sellOldShip:
            # TODO: move to a separate sellActiveShip function
            oldShipValue = activeShip.getValue(shipUpgradesOnly=transferItems)
            requestedBBUser.credits += oldShipValue
            requestedBBUser.unequipAll(activeShip)
            requestedShop.shipsStock.append(activeShip)
        
        requestedBBUser.equipShipObj(requestedShip, noSaveActive=sellOldShip)
        requestedBBUser.credits -= newShipValue
        requestedShop.shipsStock.remove(requestedShip)
        
        outStr = ":moneybag: Congratulations on your new **" + requestedShip.name + "**!"
        if sellOldShip:
            outStr += "\nYou received **" + str(oldShipValue) + " credits** for your old **" + str(activeShip.name) + "**."
        else:
            outStr += " Your old **" + activeShip.name + "** can be found in the hangar."
        if transferItems:
            outStr += "\nItems thay could not fit in your new ship can be found in the hangar."
        outStr += "\n\nYour balance is now: **" + str(requestedBBUser.credits) + " credits**."

        await message.channel.send(outStr)

    elif item == "weapon":
        requestedWeapon = requestedShop.weaponsStock[itemNum - 1]
        if not requestedShop.userCanAffordWeaponObj(requestedBBUser, requestedWeapon):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedWeapon.value) + ")")
            return
        
        requestedBBUser.credits -= requestedWeapon.value
        requestedBBUser.inactiveWeapons.append(requestedWeapon)
        requestedShop.weaponsStock.remove(requestedWeapon)

        await message.channel.send(":moneybag: Congratulations on your new **" + requestedWeapon.name + "**! \n\nYour balance is now: **" + str(requestedBBUser.credits) + " credits**.")

    elif item == "module":
        requestedModule = requestedShop.modulesStock[itemNum - 1]
        if not requestedShop.userCanAffordModuleObj(requestedBBUser, requestedModule):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedModule.value) + ")")
            return
        
        requestedBBUser.credits -= requestedModule.value
        requestedBBUser.inactiveModules.append(requestedModule)
        requestedShop.modulesStock.remove(requestedModule)

        await message.channel.send(":moneybag: Congratulations on your new **" + requestedModule.name + "**! \n\nYour balance is now: **" + str(requestedBBUser.credits) + " credits**.")

    elif item == "turret":
        requestedTurret = requestedShop.turretsStock[itemNum - 1]
        if not requestedShop.userCanAffordTurretObj(requestedBBUser, requestedTurret):
            await message.channel.send(":x: You can't afford that item! (" + str(requestedTurret.value) + ")")
            return
        
        requestedBBUser.credits -= requestedTurret.value
        requestedBBUser.inactiveTurrets.append(requestedTurret)
        requestedShop.turretsStock.remove(requestedTurret)

        await message.channel.send(":moneybag: Congratulations on your new **" + requestedTurret.name + "**! \n\nYour balance is now: **" + str(requestedBBUser.credits) + " credits**.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("buy", cmd_shop_buy)
dmCommands.register("buy", err_nodm)


"""
Sell the item of the given item type, at the given index, from the user's inactive items, to the guild's shop.
if "clear" is specified, the ship's items are unequipped before selling.
"clear" is only valid when selling a ship.

@param message -- the discord message calling the command
@param args -- string containing an item type and an index number, and optionally "clear", separated by a single space
"""
async def cmd_shop_sell(message, args):
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

    if usersDB.userIDExists(message.author.id):
        requestedBBUser = usersDB.getUser(message.author.id)
    else:
        requestedBBUser = usersDB.addUser(message.author.id)

    itemNum = argsSplit[1]
    if not bbUtil.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)
    if itemNum > len(requestedBBUser.getInactivesByName(item)):
        await message.channel.send(":x: Invalid item number! You have " + str(len(requestedBBUser.getInactivesByName(item))) + " " + item + "s.")
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

    requestedShop = guildsDB.getGuild(message.guild.id).shop

    if item == "ship":
        requestedShip = requestedBBUser.inactiveShips[itemNum - 1]
        if clearItems:
            requestedBBUser.unequipAll(requestedShip)
        
        requestedBBUser.credits += requestedShip.getValue()
        requestedBBUser.inactiveShips.remove(requestedShip)
        requestedShop.shipsStock.append(requestedShip)

        outStr = ":moneybag: You sold your **" + requestedShip.getNameOrNick() + "** for **" + str(requestedShip.getValue()) + " credits**!"
        if clearItems:
            outStr += "\nItems removed from the ship can be found in the hangar."
        await message.channel.send(outStr)
    
    elif item == "weapon":
        requestedWeapon = requestedBBUser.inactiveWeapons[itemNum - 1]
        requestedBBUser.credits += requestedWeapon.value
        requestedBBUser.inactiveWeapons.remove(requestedWeapon)
        requestedShop.weaponsStock.append(requestedWeapon)

        await message.channel.send(":moneybag: You sold your **" + requestedWeapon.name + "** for **" + str(requestedWeapon.value) + " credits**!")

    elif item == "module":
        requestedModule = requestedBBUser.inactiveModules[itemNum - 1]
        requestedBBUser.credits += requestedModule.value
        requestedBBUser.inactiveModules.remove(requestedModule)
        requestedShop.modulesStock.append(requestedModule)

        await message.channel.send(":moneybag: You sold your **" + requestedModule.name + "** for **" + str(requestedModule.value) + " credits**!")

    elif item == "turret":
        requestedTurret = requestedBBUser.inactiveTurrets[itemNum - 1]
        requestedBBUser.credits += requestedTurret.value
        requestedBBUser.inactiveTurrets.remove(requestedTurret)
        requestedShop.turretsStock.append(requestedTurret)

        await message.channel.send(":moneybag: You sold your **" + requestedTurret.name + "** for **" + str(requestedTurret.value) + " credits**!")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("sell", cmd_shop_sell)
dmCommands.register("sell", err_nodm)


"""
Equip the item of the given item type, at the given index, from the user's inactive items.
if "transfer" is specified, the new ship's items are cleared, and the old ship's items attempt to fill new ship.
"transfer" is only valid when equipping a ship.

@param message -- the discord message calling the command
@param args -- string containing an item type and an index number, and optionally "transfer", separated by a single space
"""
async def cmd_equip(message, args):
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

    if usersDB.userIDExists(message.author.id):
        requestedBBUser = usersDB.getUser(message.author.id)
    else:
        requestedBBUser = usersDB.addUser(message.author.id)

    itemNum = argsSplit[1]
    if not bbUtil.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)
    if itemNum > len(requestedBBUser.getInactivesByName(item)):
        await message.channel.send(":x: Invalid item number! You have " + str(len(requestedBBUser.getInactivesByName(item))) + " " + item + "s.")
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

    if item == "ship":
        requestedShip = requestedBBUser.inactiveShips[itemNum - 1]
        activeShip = requestedBBUser.activeShip
        if transferItems:
            requestedBBUser.unequipAll(requestedShip)
            requestedBBUser.activeShip.transferItemsTo(requestedShip)
            requestedBBUser.unequipAll(activeShip)
        
        requestedBBUser.equipShipObj(requestedShip)

        outStr = ":rocket: You switched to the **" + requestedShip.getNameOrNick() + "**."
        if transferItems:
            outStr += "\nItems thay could not fit in your new ship can be found in the hangar."
        await message.channel.send(outStr)
    
    elif item == "weapon":
        if not requestedBBUser.activeShip.canEquipMoreWeapons():
            await message.channel.send(":x: Your active ship does not have any free weapon slots!")
            return
        requestedItem = requestedBBUser.inactiveWeapons[itemNum - 1]
        requestedBBUser.activeShip.equipWeapon(requestedItem)
        requestedBBUser.inactiveWeapons.pop(itemNum - 1)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    elif item == "module":
        if not requestedBBUser.activeShip.canEquipMoreModules():
            await message.channel.send(":x: Your active ship does not have any free module slots!")
            return

        requestedItem = requestedBBUser.inactiveModules[itemNum - 1]

        if not requestedBBUser.activeShip.canEquipModuleType(requestedItem.getType()):
            await message.channel.send(":x: You already have the max of this type of module equipped!")
            return

        requestedBBUser.activeShip.equipModule(requestedItem)
        requestedBBUser.inactiveModules.pop(itemNum - 1)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    elif item == "turret":
        if not requestedBBUser.activeShip.canEquipMoreTurrets():
            await message.channel.send(":x: Your active ship does not have any free turret slots!")
            return
        requestedItem = requestedBBUser.inactiveTurrets[itemNum - 1]
        requestedBBUser.activeShip.equipTurret(requestedItem)
        requestedBBUser.inactiveTurrets.pop(itemNum - 1)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("equip", cmd_equip)
dmCommands.register("equip", cmd_equip)


"""
Unequip the item of the given item type, at the given index, from the user's active ship.

@param message -- the discord message calling the command
@param args -- string containing either "all", or (an item type and either an index number or "all", separated by a single space)
"""
async def cmd_unequip(message, args):
    argsSplit = args.split(" ")
    unequipAllItems = len(argsSplit) > 0 and argsSplit[0] == "all"

    if not unequipAllItems and len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (all/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar` or `all`.")
        return
    if len(argsSplit) > 2:
        await message.channel.send(":x: Too many arguments! Please only give an item type (all/weapon/module/turret), an item number or `all`.")
        return

    if usersDB.userIDExists(message.author.id):
        requestedBBUser = usersDB.getUser(message.author.id)
    else:
        requestedBBUser = usersDB.addUser(message.author.id)

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
        if not bbUtil.isInt(itemNum):
            await message.channel.send(":x: Invalid item number!")
            return
        itemNum = int(itemNum)
        if itemNum > len(requestedBBUser.activeShip.getActivesByName(item)):
            await message.channel.send(":x: Invalid item number! Your ship has " + str(len(requestedBBUser.activeShip.getActivesByName(item))) + " " + item + "s.")
            return
        if itemNum < 1:
            await message.channel.send(":x: Invalid item number! Must be at least 1.")
            return

    if item == "weapon":
        if not requestedBBUser.activeShip.hasWeaponsEquipped():
            await message.channel.send(":x: Your active ship does not have any weapons equipped!")
            return
        if unequipAll:
            for weapon in requestedBBUser.activeShip.weapons:
                requestedBBUser.inactiveWeapons.append(weapon)
                requestedBBUser.activeShip.unequipWeaponObj(weapon)

            await message.channel.send(":wrench: You unequipped all **weapons**.")
        else:
            requestedItem = requestedBBUser.activeShip.weapons[itemNum - 1]
            requestedBBUser.inactiveWeapons.append(requestedItem)
            requestedBBUser.activeShip.unequipWeaponIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    elif item == "module":
        if not requestedBBUser.activeShip.hasModulesEquipped():
            await message.channel.send(":x: Your active ship does not have any modules equipped!")
            return
        if unequipAll:
            for module in requestedBBUser.activeShip.modules:
                requestedBBUser.inactiveModules.append(module)
                requestedBBUser.activeShip.unequipModuleObj(module)

            await message.channel.send(":wrench: You unequipped all **modules**.")
        else:
            requestedItem = requestedBBUser.activeShip.modules[itemNum - 1]
            requestedBBUser.inactiveModules.append(requestedItem)
            requestedBBUser.activeShip.unequipModuleIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    elif item == "turret":
        if not requestedBBUser.activeShip.hasTurretsEquipped():
            await message.channel.send(":x: Your active ship does not have any turrets equipped!")
            return
        if unequipAll:
            for turret in requestedBBUser.activeShip.turrets:
                requestedBBUser.inactiveTurrets.append(turret)
                requestedBBUser.activeShip.unequipTurretObj(turret)

            await message.channel.send(":wrench: You unequipped all **turrets**.")
        else:
            requestedItem = requestedBBUser.activeShip.turrets[itemNum - 1]
            requestedBBUser.inactiveTurrets.append(requestedItem)
            requestedBBUser.activeShip.unequipTurretIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("unequip", cmd_unequip)
dmCommands.register("unequip", cmd_unequip)


"""
Set the nickname of the active ship.

@param message -- the discord message calling the command
@param args -- string containing the new nickname.
"""
async def cmd_nameship(message, args):
    if usersDB.userIDExists(message.author.id):
        requestedBBUser = usersDB.getUser(message.author.id)
    else:
        requestedBBUser = usersDB.addUser(message.author.id)

    if requestedBBUser.activeShip is None:
        await message.channel.send(":x: You do not have a ship equipped!")
        return

    if args == "":
        await message.channel.send(":x: Not enough arguments. Please give the new nickname!")
        return

    if len(args) > bbConfig.maxShipNickLength:
        await message.channel.send(":x: Nicknames must be " + str(bbConfig.maxShipNickLength) + " characters or less!")
        return

    requestedBBUser.activeShip.changeNickname(args)
    await message.channel.send(":pencil: You named your " + requestedBBUser.activeShip.name + ": **" + args + "**.")

bbCommands.register("nameship", cmd_nameship, forceKeepArgsCasing=True)
dmCommands.register("nameship", cmd_nameship, forceKeepArgsCasing=True)


"""
Remove the nickname of the active ship.

@param message -- the discord message calling the command
@param args -- ignored
"""
async def cmd_unnameship(message, args):
    if usersDB.userIDExists(message.author.id):
        requestedBBUser = usersDB.getUser(message.author.id)
    else:
        requestedBBUser = usersDB.addUser(message.author.id)

    if requestedBBUser.activeShip is None:
        await message.channel.send(":x: You do not have a ship equipped!")
        return

    if not requestedBBUser.activeShip.hasNickname:
        await message.channel.send(":x: Your active ship does not have a nickname!")
        return

    requestedBBUser.activeShip.removeNickname()
    await message.channel.send(":pencil: You reset your **" + requestedBBUser.activeShip.name + "**'s nickname.")

bbCommands.register("unnameship", cmd_unnameship)
dmCommands.register("unnameship", cmd_unnameship)


async def cmd_pay(message, args):
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a target user and an amount!")
        return
    if not bbUtil.isMention(argsSplit[0]) and not bbUtil.isInt(argsSplit[0]):
        await message.channel.send(":x: Invalid user tag!")
        return
    if not bbUtil.isInt(argsSplit[1]):
        await message.channel.send(":x: Invalid amount!")
        return

    if bbUtil.isMention(argsSplit[0]):
        # Get the discord user object for the given tag
        requestedUser = client.get_user(int(argsSplit[0].lstrip("<@!").rstrip(">")))
    else:
        requestedUser = client.get_user(int(argsSplit[0]))
    if requestedUser is None:
        await message.channel.send(":x: Unknown user!")
        return

    amount = int(argsSplit[1])
    if amount < 1:
        await message.channel.send(":x: You have to pay at least 1 credit!")
        return

    if usersDB.userIDExists(message.author.id):
        sourceBBUser = usersDB.getUser(message.author.id)
    else:
        sourceBBUser = usersDB.addUser(message.author.id)

    if not sourceBBUser.credits >= amount:
        await message.channel.send(":x: You don't have that many credits!")
        return

    if usersDB.userIDExists(requestedUser.id):
        targetBBUser = usersDB.getUser(requestedUser.id)
    else:
        targetBBUser = usersDB.addUser(requestedUser.id)

    sourceBBUser.credits -= amount
    targetBBUser.credits += amount

    await message.channel.send(":moneybag: You paid " + requestedUser.name + " **" + str(amount) + "** credits!")

bbCommands.register("pay", cmd_pay)
dmCommands.register("pay", cmd_pay)


"""
⚠ WARNING: MARKED FOR CHANGE ⚠
The following function is provisional and marked as planned for overhaul.
Details: Notifications for shop items have yet to be implemented.

Allow a user to subscribe and unsubscribe from pings when certain events occur.
Currently only new bounty notifications are implemented, but more are planned.
For example, a ping when a requested item is in stock in the guild's shop.

@param message -- the discord message calling the command
@param args -- the notification type (e.g ship), possibly followed by a specific notification (e.g groza mk II), separated by a single space.
"""
async def cmd_notify(message, args):
    if not message.guild.me.guild_permissions.manage_roles:
        await message.channel.send(":x: I do not have the 'Manage Roles' permission in this server! Please contact an admin :robot:")
        return
    if args == "":
        await message.channel.send(":x: Please name what you would like to be notified for! E.g `" + bbConfig.commandPrefix + "notify bounties`")
        return
    argsSplit = args.split(" ")
    if argsSplit[0] in ["bounty", "bounties"]:
        requestedBBGuild = guildsDB.getGuild(message.guild.id)
        if requestedBBGuild.hasBountyNotifyRoleId():
            notifyRole = discord.utils.get(message.guild.roles, id=requestedBBGuild.getBountyNotifyRoleId())
            try:
                if notifyRole in message.author.roles:
                    await message.author.remove_roles(notifyRole, reason="User has unsubscribed from new bounty notifications.")
                    await message.channel.send(":white_check_mark: You have unsubscribed from new bounty notifications!")
                else:
                    await message.author.add_roles(notifyRole, reason="User has subscribed to new bounty notifications.")
                    await message.channel.send(":white_check_mark: You have subscribed to new bounty notifications!")
            except discord.Forbidden:
                await message.channel.send(":woozy_face: I don't have permission to do that! Please ensure the requested role is beneath the BountyBot role.")
            except discord.HTTPException:
                await message.channel.send(":woozy_face: Something went wrong! Please contact an admin or try again later.")
        else:
            await message.channel.send(":x: This server does not have a role for new bounty notifications. :robot:")
    elif argsSplit[0] in bbConfig.validItemNames and argsSplit[0] != "all":
        await message.channel.send("Item notifications have not been implemented yet! \:(")
    else:
        await message.channel.send(":x: Unknown notification type - only `bounties` is currently supported!")

bbCommands.register("notify", cmd_notify)
dmCommands.register("notify", err_nodm)


"""
⚠ WARNING: MARKED FOR CHANGE ⚠
The following function is provisional and marked as planned for overhaul.
Details: The command output is finalised. However, the inner workings of the command are to be replaced with attribute getters.
         It is inefficient to calculate total value measurements on every call, so current totals should be cached in class attributes whenever modified.

print the total value of the specified user, use the calling user if no user is specified.

@param message -- the discord message calling the command
@param args -- string, can be empty or contain a user mention or ID
"""
async def cmd_total_value(message, args):
    # If no user is specified, send the balance of the calling user
    if args == "":
        if not usersDB.userIDExists(message.author.id):
            usersDB.addUser(message.author.id)
        await message.channel.send(":moneybag: **" + message.author.name + "**, your items and balance are worth a total of **" + str(usersDB.getUser(message.author.id).getStatByName("value")) + " Credits**.")
    
    # If a user is specified
    else:
        # Verify the passed user tag
        if not bbUtil.isMention(args) and not bbUtil.isInt(args):
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "total-value` to display your own total value, or `" + bbConfig.commandPrefix + "total-value @userTag` to display someone else's total value!")
            return
        if bbUtil.isMention(args):
            # Get the discord user object for the given tag
            requestedUser = client.get_user(int(args.lstrip("<@!").rstrip(">")))
        else:
            requestedUser = client.get_user(int(args))
        if requestedUser is None:
            await message.channel.send(":x: Unknown user!")
            return
        # ensure that the user is in the users database
        if not usersDB.userIDExists(requestedUser.id):
            usersDB.addUser(requestedUser.id)
        # send the user's balance
        await message.channel.send(":moneybag: **" + requestedUser.name + "**'s items and balance have a total value of **" + str(usersDB.getUser(requestedUser.id).getStatByName("value")) + " Credits**.")
    
bbCommands.register("total-value", cmd_total_value)
dmCommands.register("total-value", cmd_total_value)


"""
⚠ WARNING: MARKED FOR CHANGE ⚠
The following function is provisional and marked as planned for overhaul.
Details: Overhaul is part-way complete, with a few fighting algorithm provided in bbObjects.items.battles. However, printing the fight details is yet to be implemented.
         This is planned to be done using simple message editing-based animation of player ships and progress bars for health etc.
         This command is functional for now, but the output is subject to change.

Challenge another player to a duel, with an amount of credits as the stakes.
The winning user is given stakes credits, the loser has stakes credits taken away.
give 'challenge' to create a new duel request.
give 'cancel' to cancel an existing duel request.
give 'accept' to accept another user's duel request targetted at you.

@param message -- the discord message calling the command
@param args -- string containing the action (challenge/cancel/accept), a target user (mention or ID), and the stakes (int amount of credits). stakes are only required when "challenge" is specified.
"""
async def cmd_duel(message, args):
    argsSplit = args.split(" ")
    if len(argsSplit) == 0:
        await message.channel.send(":x: Please provide an action (`challenge`/`cancel`/`accept`/`reject`), a user, and the stakes (an amount of credits)!")
        return
    action = argsSplit[0]
    if action not in ["challenge", "cancel", "accept", "reject"]:
        await message.channel.send(":x: Invalid action! please choose from `challenge`, `cancel`, `reject` or `accept`.")
        return
    if action == "challenge":
        if len(argsSplit) < 3:
            await message.channel.send(":x: Please provide a user and the stakes (an amount of credits)!")
            return
    else:
        if len(argsSplit) < 2:
            await message.channel.send(":x: Please provide a user!")
            return
    if not bbUtil.isMention(argsSplit[1]) and not bbUtil.isInt(argsSplit[1]):
        await message.channel.send(":x: Invalid user!")
        return
    if bbUtil.isMention(argsSplit[1]):
        requestedUser = client.get_user(int(argsSplit[1].strip("<@!").rstrip(">")))
    else:
        requestedUser = client.get_user(int(argsSplit[1]))
    if requestedUser is None:
        await message.channel.send(":x: User not found!")
        return
    if requestedUser.id == message.author.id:
        await message.channel.send(":x: You can't challenge yourself!")
        return
    if action == "challenge" and (not bbUtil.isInt(argsSplit[2]) or int(argsSplit[2]) < 0):
        await message.channel.send(":x: Invalid stakes (amount of credits)!")
        return

    sourceBBUser = usersDB.getOrAddID(message.author.id)
    targetBBUser = usersDB.getOrAddID(requestedUser.id)

    if action == "challenge":
        stakes = int(argsSplit[2])
        if sourceBBUser.hasDuelChallengeFor(targetBBUser):
            await message.channel.send(":x: You already have a duel challenge pending for " + requestedUser.name + "! To make a new one, cancel it first. (see `" + bbConfig.commandPrefix + "help duel`)")
            return

        try:
            newDuelReq = DuelRequest.DuelRequest(sourceBBUser, targetBBUser, stakes, None, guildsDB.getGuild(message.guild.id))
            duelTT = TimedTask.TimedTask(expiryDelta=timeDeltaFromDict(bbConfig.duelReqExpiryTime), expiryFunction=expireAndAnnounceDuelReq, expiryFunctionArgs={"duelReq":newDuelReq})
            newDuelReq.duelTimeoutTask = duelTT
            ActiveTimedTasks.duelRequestTTDB.scheduleTask(duelTT)
            sourceBBUser.addDuelChallenge(newDuelReq)
            # print("Duelreq added to " + str(sourceBBUser.id) + " from " + str(newDuelReq.sourceBBGuild.id) + " to " + str(newDuelReq.targetBBUser.id))
        except KeyError:
            await message.channel.send(":x: User not found! Did they leave the server?")
            return
        except Exception:
            await message.channel.send(":woozy_face: An unexpected error occurred! Tri, what did you do...")
            return

        expiryTimesSplit = duelTT.expiryTime.strftime("%d %B %H %M").split(" ")
        duelExpiryTimeString = "This duel request will expire on the **" + expiryTimesSplit[0].lstrip('0') + getNumExtension(int(expiryTimesSplit[0])) + "** of **" + expiryTimesSplit[1] + "**, at **" + expiryTimesSplit[2] + ":" + expiryTimesSplit[3] + "** CST."

        if message.guild.get_member(requestedUser.id) is None:
            targetUserDCGuild = findBBUserDCGuild(targetBBUser)
            if targetUserDCGuild is None:
                await message.channel.send(":x: User not found! Did they leave the server?")
                return
            else:
                targetUserBBGuild = guildsDB.getGuild(targetUserDCGuild.id)
                if targetUserBBGuild.hasPlayChannel():
                    await client.get_channel(targetUserBBGuild.getPlayChannelId()).send(":crossed_swords: **" + str(message.author) + "** challenged " + requestedUser.mention + " to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString)
            await message.channel.send(":crossed_swords: " + message.author.mention + " challenged **" + str(requestedUser) + "** to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString)
        else:
            await message.channel.send(":crossed_swords: " + message.author.mention + " challenged " + requestedUser.mention + " to duel for **" + str(stakes) + " Credits!**\nType `" + bbConfig.commandPrefix + "duel accept " + str(message.author.id) + "` (or `" + bbConfig.commandPrefix + "duel accept @" + message.author.name + "` if you're in the same server) To accept the challenge!\n" + duelExpiryTimeString)
    
    elif action == "cancel":
        if not sourceBBUser.hasDuelChallengeFor(targetBBUser):
            await message.channel.send(":x: You do not have an active duel challenge for this user! Did it already expire?")
            return
        
        await sourceBBUser.duelRequests[targetBBUser].duelTimeoutTask.forceExpire(callExpiryFunc=False)
        sourceBBUser.removeDuelChallengeTarget(targetBBUser)
        await message.channel.send(":white_check_mark: You have cancelled your duel challenge for **" + str(requestedUser) + "**.")

    elif action == "reject":
        if not targetBBUser.hasDuelChallengeFor(sourceBBUser):
            await message.channel.send(":x: This user does not have an active duel challenge for you! Did it expire?")
            return
        
        await targetBBUser.duelRequests[sourceBBUser].duelTimeoutTask.forceExpire(callExpiryFunc=False)
        targetBBUser.removeDuelChallengeTarget(sourceBBUser)

        await message.channel.send(":white_check_mark: You have rejected **" + str(requestedUser) + "**'s duel challenge.")
        if message.guild.get_member(targetBBUser.id) is None:
            targetDCGuild = findBBUserDCGuild(targetBBUser)
            if targetDCGuild is not None:
                targetBBGuild = guildsDB.getGuild(targetDCGuild.id)
                if targetBBGuild.hasPlayChannel():
                    await client.get_channel(targetBBGuild.getPlayChannelId()).send(":-1: <@" + str(targetBBUser.id) + ">, **" + str(message.author) + "** has rejected your duel request!")
    
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
        
        # fight = ShipFight.ShipFight(sourceBBUser.activeShip, targetBBUser.activeShip)
        # duelResults = fight.fightShips(bbConfig.duelVariancePercent)
        duelResults = bbUtil.fightShips(sourceBBUser.activeShip, targetBBUser.activeShip, bbConfig.duelVariancePercent)
        winningShip = duelResults["winningShip"]

        if winningShip is sourceBBUser.activeShip:
            winningBBUser = sourceBBUser
            losingBBUser = targetBBUser
        elif winningShip is targetBBUser.activeShip:
            winningBBUser = targetBBUser
            losingBBUser = sourceBBUser
        else:
            winningBBUser = None
            losingBBUser = None

        # battleMsg = 

        # winningBBUser = sourceBBUser if winningShip is sourceBBUser.activeShip else (targetBBUser if winningShip is targetBBUser.activeShip else None)
        # losingBBUser = None if winningBBUser is None else (sourceBBUser if winningBBUser is targetBBUser else targetBBUser)

        if winningBBUser is None:
            await message.channel.send(":crossed_swords: **Stalemate!** " + str(requestedUser) + " and " + message.author.mention + " drew in a duel!")
            if message.guild.get_member(requestedUser.id) is None:
                targetDCGuild = findBBUserDCGuild(targetBBUser)
                if targetDCGuild is not None:
                    targetBBGuild = guildsDB.getGuild(targetDCGuild.id)
                    if targetBBGuild.hasPlayChannel():
                        await client.get_channel(targetBBGuild.getPlayChannelId()).send(":crossed_swords: **Stalemate!** " + targetDCGuild.get_member(requestedUser.id).mention + " and " + str(message.author) + " drew in a duel!")
            else:
                await message.channel.send(":crossed_swords: **Stalemate!** " + requestedUser.mention + " and " + message.author.mention + " drew in a duel!")
        else:
            winningBBUser.duelWins += 1
            losingBBUser.duelLosses += 1
            winningBBUser.duelCreditsWins += requestedDuel.stakes
            losingBBUser.duelCreditsLosses += requestedDuel.stakes

            winningBBUser.credits += requestedDuel.stakes
            losingBBUser.credits -= requestedDuel.stakes
            creditsMsg = "The stakes were **" + str(requestedDuel.stakes) + "** credit" + ("s" if requestedDuel.stakes != 1 else "") + ".\n**" + client.get_user(winningBBUser.id).name + "** now has **" + str(winningBBUser.credits) + " credits**.\n**" +  client.get_user(losingBBUser.id).name + "** now has **" + str(losingBBUser.credits) + " credits**."
            # statsMsg = "**" + message.author.name + "** had " + (str(duelResults["ship1"]["DPS"]["varied"]) if duelResults["ship1"]["DPS"]["varied"] != -1 else "inf.") + " DPS and " + (str(duelResults["ship1"]["health"]["varied"]) if duelResults["ship1"]["health"]["varied"] != -1 else "inf.") + " health." \
            #             + "**" + requestedUser.name + "** had " + (str(duelResults["ship2"]["DPS"]["varied"]) if duelResults["ship2"]["DPS"]["varied"] != -1 else "inf.") + " DPS and " + (str(duelResults["ship2"]["health"]["varied"]) if duelResults["ship2"]["health"]["varied"] != -1 else "inf.") + " health." \
            #             + "**" + message.author.name + "** had " + (str(duelResults["ship1"]["TTK"]) if duelResults["ship1"]["TTK"] != -1 else "inf.") + "s time to kill." \
            #             + "**" + requestedUser.name + "** had " + (str(duelResults["ship2"]["TTK"]) if duelResults["ship2"]["TTK"] != -1 else "inf.") + "s time to kill."
            statsEmbed = makeEmbed(authorName="**Duel Stats**")
            statsEmbed.add_field(name="DPS (" + str(bbConfig.duelVariancePercent * 100) + "% RNG)",value=message.author.mention + ": " + str(round(duelResults["ship1"]["DPS"]["varied"], 2)) + "\n" + requestedUser.mention + ": " + str(round(duelResults["ship2"]["DPS"]["varied"], 2)))
            statsEmbed.add_field(name="Health (" + str(bbConfig.duelVariancePercent * 100) + "% RNG)",value=message.author.mention + ": " + str(round(duelResults["ship1"]["health"]["varied"])) + "\n" + requestedUser.mention + ": " + str(round(duelResults["ship2"]["health"]["varied"], 2)))
            statsEmbed.add_field(name="Time To Kill",value=message.author.mention + ": " + (str(round(duelResults["ship1"]["TTK"], 2)) if duelResults["ship1"]["TTK"] != -1 else "inf.") + "s\n" + requestedUser.mention + ": " + (str(round(duelResults["ship2"]["TTK"], 2)) if duelResults["ship2"]["TTK"] != -1 else "inf.") + "s")

            if message.guild.get_member(winningBBUser.id) is None:
                await message.channel.send(":crossed_swords: **Fight!** " + str(client.get_user(winningBBUser.id)) + " beat " + client.get_user(losingBBUser.id).mention + " in a duel!\n" + creditsMsg,embed=statsEmbed)
                winnerDCGuild = findBBUserDCGuild(winningBBUser)
                if winnerDCGuild is not None:
                    winnerBBGuild = guildsDB.getGuild(winnerDCGuild.id)
                    if winnerBBGuild.hasPlayChannel():
                        await client.get_channel(winnerBBGuild.getPlayChannelId()).send(":crossed_swords: **Fight!** " + winnerDCGuild.get_member(winningBBUser.id).mention + " beat " + str(client.get_user(losingBBUser.id)) + " in a duel!\n" + creditsMsg,embed=statsEmbed)
            else:
                if message.guild.get_member(losingBBUser.id) is None:
                    await message.channel.send(":crossed_swords: **Fight!** " + client.get_user(winningBBUser.id).mention + " beat " + str(client.get_user(losingBBUser.id)) + " in a duel!\n" + creditsMsg,embed=statsEmbed)
                    loserDCGuild = findBBUserDCGuild(losingBBUser)
                    if loserDCGuild is not None:
                        loserBBGuild = guildsDB.getGuild(loserDCGuild.id)
                        if loserBBGuild.hasPlayChannel():
                            await client.get_channel(loserBBGuild.getPlayChannelId()).send(":crossed_swords: **Fight!** " + str(client.get_user(winningBBUser.id)) + " beat " + loserDCGuild.get_member(losingBBUser.id).mention + " in a duel!\n" + creditsMsg,embed=statsEmbed)
                else:
                    await message.channel.send(":crossed_swords: **Fight!** " + client.get_user(winningBBUser.id).mention + " beat " + client.get_user(losingBBUser.id).mention + " in a duel!\n" + creditsMsg,embed=statsEmbed)

        await targetBBUser.duelRequests[sourceBBUser].duelTimeoutTask.forceExpire(callExpiryFunc=False)
        targetBBUser.removeDuelChallengeObj(requestedDuel)
        # logStr = ""
        # for s in duelResults["battleLog"]:
        #     logStr += s.replace("{PILOT1NAME}",message.author.name).replace("{PILOT2NAME}",requestedUser.name) + "\n"
        # await message.channel.send(logStr)

bbCommands.register("duel", cmd_duel)
dmCommands.register("duel", err_nodm)

        
            


####### ADMINISTRATOR COMMANDS #######



"""
admin command for setting the current guild's announcements channel

@param message -- the discord message calling the command
@param args -- ignored
"""
async def admin_cmd_set_announce_channel(message, args):
    guildsDB.getGuild(message.guild.id).setAnnounceChannelId(message.channel.id)
    await message.channel.send(":ballot_box_with_check: Announcements channel set!")
    
bbCommands.register("set-announce-channel", admin_cmd_set_announce_channel, isAdmin=True)
dmCommands.register("set-announce-channel", err_nodm, isAdmin=True)


"""
admin command for setting the current guild's play channel

@param message -- the discord message calling the command
@param args -- ignored
"""
async def admin_cmd_set_play_channel(message, args):
    guildsDB.getGuild(message.guild.id).setPlayChannelId(message.channel.id)
    await message.channel.send(":ballot_box_with_check: Bounty play channel set!")
    
bbCommands.register("set-play-channel", admin_cmd_set_play_channel, isAdmin=True)
dmCommands.register("set-play-channel", err_nodm, isAdmin=True)


"""
admin command printing help strings for admin commands as defined in bbData

@param message -- the discord message calling the command
@param args -- ignored
"""
async def admin_cmd_admin_help(message, args):
    sendChannel = None
    sendDM = False

    if message.author.dm_channel is None:
        await message.author.create_dm()
    if message.author.dm_channel is None:
        sendChannel = message.channel
    else:
        sendChannel = message.author.dm_channel
        sendDM = True

    helpEmbed = makeEmbed(titleTxt="BB Administrator Commands", thumb=client.user.avatar_url_as(size=64))
    for section in bbData.adminHelpDict.keys():
        helpEmbed.add_field(name="‎",value="__" + section + "__", inline=False)
        for currentCommand in bbData.adminHelpDict[section].values():
            helpEmbed.add_field(name=currentCommand[0],value=currentCommand[1].replace("$COMMANDPREFIX$",bbConfig.commandPrefix), inline=False)
    
    try:
        await sendChannel.send(bbData.adminHelpIntro.replace("$COMMANDPREFIX$",bbConfig.commandPrefix), embed=helpEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.name + "! Please enable DMs from users who are not friends.")
        return
    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji)

bbCommands.register("admin-help", admin_cmd_admin_help, isAdmin=True)
dmCommands.register("admin-help", err_nodm, isAdmin=True)


"""
For the current guild, set a role to mention when new bounties are spawned.
can take either a role mention or ID.

@param message -- the discord message calling the command
@param args -- either a role mention or a role ID
"""
async def admin_cmd_set_bounty_notify_role(message, args):
    if args == "":
        await message.channel.send(":x: Please provide either a role mention or ID!")
        return
    if not (bbUtil.isInt(args) or bbUtil.isRoleMention(args)):
        await message.channel.send(":x: Invalid role! Please give either a role mention or ID!")
        return
    
    if bbUtil.isRoleMention(args):
        requestedRole = message.guild.get_role(int(args[3:-1]))
    else:
        requestedRole = message.guild.get_role(int(args))
    
    if requestedRole is None:
        await message.channel.send(":x: Role not found!")
        return

    guildsDB.getGuild(message.guild.id).setBountyNotifyRoleId(requestedRole.id)
    await message.channel.send(":white_check_mark: Bounty notify role set!")

bbCommands.register("set-bounty-notify-role", admin_cmd_set_bounty_notify_role, isAdmin=True)
dmCommands.register("set-bounty-notify-role", err_nodm)


"""
For the current guild, remove the role to mention when new bounties are spawned.

@param message -- the discord message calling the command
@param args -- ignored
"""
async def admin_cmd_remove_bounty_notify_role(message, args):
    requestedBBGuild = guildsDB.getGuild(message.guild.id)

    if not requestedBBGuild.hasBountyNotifyRoleId():
        await message.channel.send(":x: This server does not have a bounty notify role set!")
        return
    
    requestedBBGuild.removeBountyNotifyRoleId()
    await message.channel.send(":white_check_mark: Bounty notify role removed!")

bbCommands.register("remove-bounty-notify-role", admin_cmd_remove_bounty_notify_role, isAdmin=True)
dmCommands.register("remove-bounty-notify-role", err_nodm)



####### DEVELOPER COMMANDS #######



"""
developer command saving all data to JSON and then shutting down the bot

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_sleep(message, args):
    await message.channel.send("zzzz....")
    botLoggedIn = False
    await client.logout()
    saveDB(bbConfig.userDBPath, usersDB)
    saveDB(bbConfig.bountyDBPath, bountiesDB)
    saveDB(bbConfig.guildDBPath, guildsDB)
    print(datetime.now().strftime("%H:%M:%S: Data saved!"))
    
bbCommands.register("sleep", dev_cmd_sleep, isDev=True)
dmCommands.register("sleep", dev_cmd_sleep, isDev=True)


"""
developer command saving all databases to JSON

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_save(message, args):
    saveDB(bbConfig.userDBPath, usersDB)
    saveDB(bbConfig.bountyDBPath, bountiesDB)
    saveDB(bbConfig.guildDBPath, guildsDB)
    print(datetime.now().strftime("%H:%M:%S: Data saved manually!"))
    await message.channel.send("saved!")
    
bbCommands.register("save", dev_cmd_save, isDev=True)
dmCommands.register("save", dev_cmd_save, isDev=True)


"""
developer command printing whether or not the current guild has an announcements channel set

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_has_announce(message, args):
    guild = guildsDB.getGuild(message.guild.id)
    await message.channel.send(":x: Unknown guild!" if guild is None else guild.hasAnnounceChannel())
    
bbCommands.register("has-announce", dev_cmd_has_announce, isDev=True)
dmCommands.register("has-announce", err_nodm, isDev=True)


"""
developer command printing the current guild's announcements channel if one is set

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_get_announce(message, args):
    await message.channel.send("<#" + str(guildsDB.getGuild(message.guild.id).getAnnounceChannelId()) + ">")
    
bbCommands.register("get-announce", dev_cmd_get_announce, isDev=True)
dmCommands.register("get-announce", err_nodm, isDev=True)


"""
developer command printing whether or not the current guild has a play channel set

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_has_play(message, args):
    guild = guildsDB.getGuild(message.guild.id)
    await message.channel.send(":x: Unknown guild!" if guild is None else guild.hasPlayChannel())
    
bbCommands.register("has-play", dev_cmd_has_play, isDev=True)
dmCommands.register("has-play", err_nodm, isDev=True)


"""
developer command printing the current guild's play channel if one is set

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_get_play(message, args):
    await message.channel.send("<#" + str(guildsDB.getGuild(message.guild.id).getPlayChannelId()) + ">")
    
bbCommands.register("get-play", dev_cmd_get_play, isDev=True)
dmCommands.register("get-play", err_nodm, isDev=True)


"""
developer command clearing all active bounties

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_clear_bounties(message, args):
    bountiesDB.clearBounties()
    await message.channel.send(":ballot_box_with_check: Active bounties cleared!")
    
bbCommands.register("clear-bounties", dev_cmd_clear_bounties, isDev=True)
dmCommands.register("clear-bounties", dev_cmd_clear_bounties, isDev=True)


"""
developer command printing the calling user's checking cooldown

@param message -- the discord message calling the command
@param args -- ignore
"""
async def dev_cmd_get_cooldown(message, args):
    diff = datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd) - datetime.utcnow()
    minutes = int(diff.total_seconds() / 60)
    seconds = int(diff.total_seconds() % 60)
    await message.channel.send(str(usersDB.getUser(message.author.id).bountyCooldownEnd) + " = " + str(minutes) + "m, " + str(seconds) + "s.")
    await message.channel.send(datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd).strftime("%Hh%Mm%Ss"))
    await message.channel.send(datetime.utcnow().strftime("%Hh%Mm%Ss"))
    
bbCommands.register("get-cool ", dev_cmd_get_cooldown, isDev=True)
dmCommands.register("get-cool ", dev_cmd_get_cooldown, isDev=True)


"""
developer command resetting the checking cooldown of the calling user, or the specified user if one is given

@param message -- the discord message calling the command
@param args -- string, can be empty or contain a user mention
"""
async def dev_cmd_reset_cooldown(message, args):
    # reset the calling user's cooldown if no user is specified
    if args == "":
        usersDB.getUser(message.author.id).bountyCooldownEnd = datetime.utcnow().timestamp()
    # otherwise get the specified user's discord object and reset their cooldown.
    # [!] no validation is done.
    else:
        if "!" in args:
            requestedUser = client.get_user(int(args[2:-1]))
        else:
            requestedUser = client.get_user(int(args[1:-1]))
        usersDB.getUser(requestedUser).bountyCooldownEnd = datetime.utcnow().timestamp()
    await message.channel.send("Done!")
    
bbCommands.register("reset-cool", dev_cmd_reset_cooldown, isDev=True)
dmCommands.register("reset-cool", dev_cmd_reset_cooldown, isDev=True)


"""
developer command setting the checking cooldown applied to users
this does not update bbConfig and will be reverted on bot restart

@param message -- the discord message calling the command
@param args -- string containing an integer number of minutes
"""
async def dev_cmd_setcheckcooldown(message, args):
    # verify a time was requested
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    # verify the requested time is an integer
    if not bbUtil.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the checking cooldown amount
    bbConfig.checkCooldown["minutes"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)
    
bbCommands.register("setcheckcooldown", dev_cmd_setcheckcooldown, isDev=True)
dmCommands.register("setcheckcooldown", dev_cmd_setcheckcooldown, isDev=True)


"""
developer command setting the number of minutes in the new bounty generation period
this does not update bbConfig and will be reverted on bot restart
this does not affect the numebr of hours in the new bounty generation period

@param message -- the discord message calling the command
@param args -- string containing an integer number of minutes
"""
async def dev_cmd_setbountyperiodm(message, args):
    # verify a time was given
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    # verify the given time is an integer
    if not bbUtil.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the new bounty generation cooldown
    bbConfig.newBountyFixedDelta["minutes"] = int(args)
    bbConfig.newBountyFixedDeltaChanged = True
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)
    
bbCommands.register("setbountyperiodm", dev_cmd_setbountyperiodm, isDev=True)
dmCommands.register("setbountyperiodm", dev_cmd_setbountyperiodm, isDev=True)


"""
developer command setting the number of hours in the new bounty generation period
this does not update bbConfig and will be reverted on bot restart
this does not affect the numebr of minutes in the new bounty generation period

@param message -- the discord message calling the command
@param args -- string containing an integer number of hours
"""
async def dev_cmd_setbountyperiodh(message, args):
    # verify a time was specified
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    # verify the given time is an integer
    if not bbUtil.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    # update the bounty generation period
    bbConfig.newBountyFixedDeltaChanged = True
    bbConfig.newBountyFixedDelta["hours"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)
    
bbCommands.register("setbountyperiodh", dev_cmd_setbountyperiodh, isDev=True)
dmCommands.register("setbountyperiodh", dev_cmd_setbountyperiodh, isDev=True)


"""
developer command resetting the current bounty generation period,
instantly generating a new bounty

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_resetnewbountycool(message, args):
    bbConfig.newBountyDelayReset = True
    await message.channel.send(":ballot_box_with_check: New bounty cooldown reset!")
    
bbCommands.register("resetnewbountycool", dev_cmd_resetnewbountycool, isDev=True)
dmCommands.register("resetnewbountycool", dev_cmd_resetnewbountycool, isDev=True)


"""
developer command printing whether or not the given faction can accept new bounties

@param message -- the discord message calling the command
@param args -- string containing a faction
"""
async def dev_cmd_canmakebounty(message, args):
    newFaction = args.lower()
    # ensure the given faction exists
    if not bountiesDB.factionExists(newFaction):
        await message.channel.send("not a faction: '" + newFaction + "'")
    else:
        await message.channel.send(bountiesDB.factionCanMakeBounty(newFaction.lower()))
    
bbCommands.register("canmakebounty", dev_cmd_canmakebounty, isDev=True)
dmCommands.register("canmakebounty", dev_cmd_canmakebounty, isDev=True)


"""
developer command sending a message to the playChannel of all guilds that have one

@param message -- the discord message calling the command
@param args -- string containing the message to broadcast
"""
async def dev_cmd_broadcast(message, args):
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
            msg = msg[embedIndex:]
            titleTxt=""
            desc=""
            footerTxt=""
            thumb=""
            img=""
            authorName=""
            icon=""

            try:
                startIndex=msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex=startIndex + msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("desc='")+len("desc=")+1
                endIndex=startIndex + msg[msg.index("desc='")+len("desc='"):].index("'")
                desc=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex=startIndex + msg[msg.index("footerTxt='")+len("footerTxt='"):].index("'")
                footerTxt=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("thumb='")+len("thumb=")+1
                endIndex=startIndex + msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("img='")+len("img=")+1
                endIndex=startIndex + msg[msg.index("img='")+len("img='"):].index("'")
                img=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("authorName='")+len("authorName=")+1
                endIndex=startIndex + msg[msg.index("authorName='")+len("authorName='"):].index("'")
                authorName=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("icon='")+len("icon=")+1
                endIndex=startIndex + msg[msg.index("icon='")+len("icon='"):].index("'")
                icon=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt, thumb=thumb, img=img, authorName=authorName, icon=icon)
            
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
                
                if fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace("{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace("{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        if useAnnounceChannel:
            for guild in guildsDB.guilds.values():
                if guild.hasAnnounceChannel():
                    await client.get_channel(guild.getAnnounceChannelId()).send(msgText, embed=broadcastEmbed)
        else:
            for guild in guildsDB.guilds.values():
                if guild.hasPlayChannel():
                    await client.get_channel(guild.getPlayChannelId()).send(msgText, embed=broadcastEmbed)

bbCommands.register("broadcast", dev_cmd_broadcast, isDev=True, forceKeepArgsCasing=True)
dmCommands.register("broadcast", dev_cmd_broadcast, isDev=True, forceKeepArgsCasing=True)


"""
developer command sending a message to the same channel as the command is called in

@param message -- the discord message calling the command
@param args -- string containing the message to broadcast
"""
async def dev_cmd_say(message, args):
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
            msg = msg[embedIndex:]
            titleTxt=""
            desc=""
            footerTxt=""
            thumb=""
            img=""
            authorName=""
            icon=""

            try:
                startIndex=msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex=startIndex + msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("desc='")+len("desc=")+1
                endIndex=startIndex + msg[msg.index("desc='")+len("desc='"):].index("'")
                desc=msg[startIndex:endIndex].replace("{NL}","\n")
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex=startIndex + msg[msg.index("footerTxt='")+len("footerTxt='"):].index("'")
                footerTxt=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("thumb='")+len("thumb=")+1
                endIndex=startIndex + msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("img='")+len("img=")+1
                endIndex=startIndex + msg[msg.index("img='")+len("img='"):].index("'")
                img=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("authorName='")+len("authorName=")+1
                endIndex=startIndex + msg[msg.index("authorName='")+len("authorName='"):].index("'")
                authorName=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex=msg.index("icon='")+len("icon=")+1
                endIndex=startIndex + msg[msg.index("icon='")+len("icon='"):].index("'")
                icon=msg[startIndex:endIndex]
                msg=msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt, thumb=thumb, img=img, authorName=authorName, icon=icon)
            
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
                
                if fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace("{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace("{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        await message.channel.send(msgText, embed=broadcastEmbed)

bbCommands.register("say", dev_cmd_say, isDev=True, forceKeepArgsCasing=True)
dmCommands.register("broadcast", dev_cmd_broadcast, isDev=True, forceKeepArgsCasing=True)


"""
developer command making a new bounty
args should be separated by a space and then a plus symbol
if no args are given, generate a new bounty at complete random
if only one argument is given it is assumed to be a faction, and a bounty is generated for that faction
otherwise, all 9 arguments required to generate a bounty must be given
the route should be separated by only commas and no spaces. the endTime should be a UTC timestamp. Any argument can be given as 'auto' to be either inferred or randomly generated
as such, '!bb make-bounty' is an alias for '!bb make-bounty +auto +auto +auto +auto +auto +auto +auto +auto +auto'

@param message -- the discord message calling the command
@param args -- can be empty, can be '+<faction>', or can be '+<faction> +<name> +<route> +<start> +<end> +<answer> +<reward> +<endtime> +<icon>'
"""
async def dev_cmd_make_bounty(message, args):
    # if no args were given, generate a completely random bounty
    if args == "":
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB)
    # if only one argument was given, use it as a faction
    elif len(args.split("+")) == 2:
        newFaction = args.split("+")[1]
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction))

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
            if newName != "" and bountiesDB.bountyNameExists(newName):
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
            newBounty = bbBounty.Bounty(bountyDB=bountiesDB, criminalObj=builtInCrimObj, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon))
        # normal bounty generation for custom criminals
        else:
            newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon))
    
    # Report an error for invalid command syntax
    else:
        await message.channel.send("incorrect syntax. give +faction +name +route +start +end +answer +reward +endtime +icon")

    # activate and announce the new bounty
    bountiesDB.addBounty(newBounty)
    await announceNewBounty(newBounty)
    
bbCommands.register("make-bounty", dev_cmd_make_bounty, isDev=True, forceKeepArgsCasing=True)
dmCommands.register("make-bounty", dev_cmd_make_bounty, isDev=True, forceKeepArgsCasing=True)


"""
developer command making a new PLAYER bounty
args should be separated by a space and then a plus symbol
the first argument should be a user MENTION
if one arg is given, generate a new bounty at complete random, for the specified user
if two arguments are given the second is assumed to be a faction, and a bounty is generated for that faction for the specified user
otherwise, all 9 arguments required to generate a bounty must be given
the route should be separated by only commas and no spaces. the endTime should be a UTC timestamp. Any argument can be given as 'auto' to be either inferred or randomly generated
as such, '!bb make-player-bounty <user>' is an alias for '!bb make-bounty +auto +<user> +auto +auto +auto +auto +auto +auto +auto'

@param message -- the discord message calling the command
@param args -- can be empty, can be '+<user_mention> +<faction>', or can be '+<faction> +<user_mention> +<route> +<start> +<end> +<answer> +<reward> +<endtime> +<icon>'
"""
async def dev_cmd_make_player_bounty(message, args):
    # if only one argument is given
    if len(args.split(" ")) == 1:
        # verify the requested user
        requestedID = int(args.lstrip("<@!").rstrip(">"))
        if not bbUtil.isInt(requestedID) or (client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # create a new bounty at random for the specified user
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(client.get_user(requestedID).avatar_url_as(size=64)), aliases=[userTagOrDiscrim(args)]))
    
    # if the faction is also given
    elif len(args.split("+")) == 2:
        # verify the user
        requestedID = int(args.split(" ")[0].lstrip("<@!").rstrip(">"))
        if not bbUtil.isInt(requestedID) or (client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # create a bounty at random for the specified user and faction
        newFaction = args.split("+")[1]
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(client.get_user(requestedID).avatar_url_as(size=64)), faction=newFaction, aliases=[userTagOrDiscrim(args.split(" ")[0])]))
    
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
        if not bbUtil.isInt(requestedID) or (client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        # ensure no bounty already exists for this user
        if bountiesDB.bountyNameExists(newName):
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
            newIcon = str(client.get_user(int(newName.lstrip("<@!").rstrip(">"))).avatar_url_as(size=64))

        # create the bounty object
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=True, icon=newIcon, aliases=[userTagOrDiscrim(newName)]))
    
    # print an error for incorrect syntax
    else:
        await message.channel.send("incorrect syntax. give +faction +userTag +route +start +end +answer +reward +endtime +icon")

    # activate and announce the bounty
    bountiesDB.addBounty(newBounty)
    await announceNewBounty(newBounty)
    
bbCommands.register("make-player-bounty", dev_cmd_make_player_bounty, isDev=True, forceKeepArgsCasing=True)
dmCommands.register("make-player-bounty", dev_cmd_make_player_bounty, isDev=True, forceKeepArgsCasing=True)


"""
Refresh the shop stock of the current guild. Does not reset the shop stock cooldown.

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_refreshshop(message, args):
    guild = guildsDB.getGuild(message.guild.id)
    guild.shop.refreshStock()
    if guild.hasPlayChannel():
        await client.get_channel(guild.getPlayChannelId()).send(":arrows_counterclockwise: The shop stock has been refreshed!")

bbCommands.register("refreshshop",dev_cmd_refreshshop, isDev=True)
dmCommands.register("refreshshop",err_nodm, isDev=True)


"""
developer command setting the requested user's balance.

@param message -- the discord message calling the command
@param args -- string containing a user mention and an integer number of credits
"""
async def dev_cmd_setbalance(message, args):
    argsSplit = args.split(" ")
    # verify both a user and a balance were given
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a user mention followed by the new balance!")
        return
    # verify the requested balance is an integer
    if not bbUtil.isInt(argsSplit[1]):
        await message.channel.send(":x: that's not a number!")
        return
    # verify the requested user
    requestedUser = client.get_user(int(argsSplit[0].lstrip("<@!").rstrip(">")))
    if requestedUser is None:
        await message.channel.send(":x: invalid user!!")
        return
    if not usersDB.userIDExists(requestedUser.id):
        requestedBBUser = usersDB.addUser(requestedUser.id)
    else:
        requestedBBUser = usersDB.getUser(requestedUser.id)
    # update the balance
    requestedBBUser.credits = int(argsSplit[1])
    await message.channel.send("Done!")
    
bbCommands.register("setbalance", dev_cmd_setbalance, isDev=True)
dmCommands.register("setbalance", dev_cmd_setbalance, isDev=True)



####### MAIN FUNCTIONS #######



"""
Create a database entry for new guilds when one is joined.
TODO: Once deprecation databases are implemented, if guilds now store important information consider searching for them in deprecated

@param guild -- the guild just joined.
"""
@client.event
async def on_guild_join(guild):
    print(datetime.now().strftime("[%H:%M:%S]") +  " I joined a new guild! '" + guild.name + "' [" + str(guild.id) + "]",end="")
    if not guildsDB.guildIdExists(guild.id):
        guildsDB.addGuildID(guild.id)
        print(" -- The guild was added to guildsDB.",end="")
    print()


"""
Remove the database entry for any guilds the bot leaves.
TODO: Once deprecation databases are implemented, if guilds now store important information consider moving them to deprecated.

@param guild -- the guild just left.
"""
@client.event
async def on_guild_remove(guild):
    print(datetime.now().strftime("[%H:%M:%S]") +  " I left a guild! '" + guild.name + "' [" + str(guild.id) + "]",end="")
    if guildsDB.guildIdExists(guild.id):
        guildsDB.removeGuildId(guild.id)
        print(" -- The guild was removed from guildsDB.",end="")
    print()


"""
Bot initialisation (called on bot login) and behaviour loops.
Currently includes:
    - new bounty spawning
    - shop stock refreshing
    - regular database saving to JSON

TODO: Add bounty expiry and reaction menu (e.g duel challenges) expiry
TODO: Implement dynamic timedtask checking period
"""
@client.event
async def on_ready():
    for currentUser in usersDB.users.values():
        currentUser.validateLoadout()

    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game("Galaxy on Fire 2™ Full HD"))
    # bot is now logged in
    botLoggedIn = True

    bountyDelayGenerators = {"fixed":getFixedDelay, "random":getRandomDelaySeconds}
    bountyDelayGeneratorArgs = {"fixed":bbConfig.newBountyFixedDelta, "random":{"min": bbConfig.newBountyDelayMin, "max": bbConfig.newBountyDelayMax}}

    try:
        ActiveTimedTasks.newBountyTT = TimedTask.DynamicRescheduleTask(bountyDelayGenerators[bbConfig.newBountyDelayType], delayTimeGeneratorArgs=bountyDelayGeneratorArgs[bbConfig.newBountyDelayType], autoReschedule=True, expiryFunction=spawnAndAnnounceRandomBounty)
    except KeyError:
        raise ValueError("bbConfig: Unrecognised newBountyDelayType '" + bbConfig.newBountyDelayType + "'")
    
    ActiveTimedTasks.shopRefreshTT = TimedTask.DynamicRescheduleTask(getFixedDelay, delayTimeGeneratorArgs=bbConfig.shopRefreshStockPeriod, autoReschedule=True, expiryFunction=refreshAndAnnounceAllShopStocks)
    ActiveTimedTasks.dbSaveTT = TimedTask.DynamicRescheduleTask(getFixedDelay, delayTimeGeneratorArgs=bbConfig.savePeriod, autoReschedule=True, expiryFunction=saveAllDBs)

    ActiveTimedTasks.duelRequestTTDB = TimedTaskHeap.TimedTaskHeap()

    if bbConfig.timedTaskCheckingType not in ["fixed", "dynamic"]:
        raise ValueError("bbConfig: Invalid timedTaskCheckingType '" + bbConfig.timedTaskCheckingType + "'")

    # TODO: find next closest task with min over heap[0] for all task DBs and delay by that amount
    # newTaskAdded = False
    # nextTask
    
    # execute regular tasks while the bot is logged in
    while botLoggedIn:
        if bbConfig.timedTaskCheckingType == "fixed":
            await asyncio.sleep(bbConfig.timedTaskLatenessThresholdSeconds)
        # elif bbConfig.timedTaskCheckingType == "dynamic":

        await ActiveTimedTasks.shopRefreshTT.doExpiryCheck()

        if bbConfig.newBountyDelayReset:
            await ActiveTimedTasks.newBountyTT.forceExpire()
            bbConfig.newBountyDelayReset = False
        else:
            await ActiveTimedTasks.newBountyTT.doExpiryCheck()
        
        await ActiveTimedTasks.dbSaveTT.doExpiryCheck()

        await ActiveTimedTasks.duelRequestTTDB.doTaskChecking()


"""
Called every time a message is sent in a server that the bot has joined
Currently handles:
- random !drink
- command calling

@paran message: The message that triggered this command on sending
"""
@client.event
async def on_message(message):
    
    # ignore messages sent by BountyBot and DMs
    if message.author == client.user:
        return

    # if not guildsDB.guildIdExists(message.guild.id):
    #     guildsDB.addGuildID(message.guild.id)

    # x = await message.channel.fetch_message(723205500887498784)
    # await x.delete()

    # if message.channel.type == discord.ChannelType.private:
    #     return

    if message.author.id in bbConfig.developers or message.guild is None or not message.guild.id in bbConfig.disabledServers:

        """
        # randomly send '!drink' to the same channel
        bbConfig.randomDrinkNum -= 1
        if bbConfig.randomDrinkNum == 0:
            await message.channel.send("!drink")
            bbConfig.randomDrinkNum = random.randint(bbConfig.randomDrinkFactor / 10, bbConfig.randomDrinkFactor)
        """

        # For any messages beginning with bbConfig.commandPrefix
        # New method without space-splitting to allow for prefixes that dont end in a space
        if len(message.content) >= len(bbConfig.commandPrefix) and message.content[0:len(bbConfig.commandPrefix)].lower() == bbConfig.commandPrefix.lower():
        # Old method with space-splitting
        # if message.content.split(" ")[0].lower() == (bbConfig.commandPrefix.rstrip(" ")):
            # replace special apostraphe characters with the universal '
            msgContent = message.content.replace("‘", "'").replace("’","'")

            # split the message into command and arguments
            if len(msgContent[len(bbConfig.commandPrefix):]) > 0:
                command = msgContent[len(bbConfig.commandPrefix):].split(" ")[0]
                args = msgContent[len(bbConfig.commandPrefix) + len(command) + 1:]

            # if no command is given, call help with no arguments
            else:
                args = ""
                command = "help"

            # Debug: Print the recognised command args strings
            # print("COMMAND '" + command + "'")
            # print("ARGS '" + args + "'")
            
            # infer the message author's permissions
            userIsDev = message.author.id in bbConfig.developers
            # if message.channel.type == discord.ChannelType.text:

            # infer the message author's permissions
            userIsAdmin = message.author.permissions_in(message.channel).administrator

            # Call the requested command
            if message.channel.type in [discord.ChannelType.private, discord.ChannelType.group]:
                commandFound = await dmCommands.call(command, message, args, isAdmin=userIsAdmin, isDev=userIsDev)
            else:
                commandFound = await bbCommands.call(command, message, args, isAdmin=userIsAdmin, isDev=userIsDev)

            # elif message.channel.type == discord.ChannelType.private:
            #     # Call the requested command
            #     commandFound = await dmCommands.call(command, message, args, isAdmin=False, isDev=userIsDev)
            

            # Command not found, send an error message.
            if not commandFound:
                userTitle = bbConfig.devTitle if userIsDev else (bbConfig.adminTitle if userIsAdmin else bbConfig.userTitle)
                await message.channel.send(""":question: Can't do that, """ + userTitle + """. Type `""" + bbConfig.commandPrefix + """help` for a list of commands! **o7**""")


client.run(bbPRIVATE.botToken)