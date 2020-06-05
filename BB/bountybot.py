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
from .bbObjects import bbBounty, bbBountyConfig
from .bbDatabases import bbBountyDB, bbGuildDB, bbUserDB, HeirarchicalCommandsDB
from . import bbUtil



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

# Do not change this!
botLoggedIn = False



####### UTIL FUNCTIONS #######



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
                # announce to the given channel
                await currentChannel.send(msg, embed=bountyEmbed)
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
            rewardsEmbed = makeEmbed(titleTxt="Bounty Complete!",authorName=criminalNameOrDiscrim(bounty.criminal) + " Arrested",icon=bounty.criminal.icon,col=bbData.factionColours[bounty.faction])
            
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
    # embed.set_image(url=img)
    if thumb != "": embed.set_thumbnail(url=thumb)
    if icon != "": embed.set_author(name=authorName, icon_url=icon)
    return embed



####### USER COMMANDS #######



"""
Print the help strings defined in bbData as an embed
TODO: extend to allow the user to request help for a specific command. Shouold be simple, just use the command as the key for the help strings dict.

@param message -- the discord message calling the command
@param args -- ignored
"""
# @client.command(name='runHelp')
async def cmd_help(message, args):
    helpEmbed = makeEmbed(titleTxt="BountyBot Commands", thumb=client.user.avatar_url_as(size=64))
    for section in bbData.helpDict.keys():
        helpEmbed.add_field(name="‎",value=section, inline=False)
        for currentCommand in bbData.helpDict[section].keys():
            helpEmbed.add_field(name=currentCommand,value=bbData.helpDict[section][currentCommand], inline=False)
    await message.channel.send(bbData.helpIntro, embed=helpEmbed)
    
bbCommands.register("help", cmd_help)


"""
say hello!

@param message -- the discord message calling the command
@param args --ignored
"""
async def cmd_hello(message, args):
    await message.channel.send("Greetings, pilot! **o7**")
    
bbCommands.register("hello", cmd_hello)


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
        if len(args.split(" ")) > 1 or not (args.startswith("<@") and args.endswith(">")) or ("!" in args and not bbUtil.isInt(args[3:-1])) or ("!" not in args and not bbUtil.isInt(args[2:-1])):
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return
        # Get the discord user object for the given tag
        if "!" in args:
            requestedUser = client.get_user(int(args[3:-1]))
        else:
            requestedUser = client.get_user(int(args[2:-1]))
        # ensure that the user is in the users database
        if not usersDB.userIDExists(requestedUser.id):
            usersDB.addUser(requestedUser.id)
        # send the user's balance
        await message.channel.send(":moneybag: **" + requestedUser.name + "** has **" + str(usersDB.getUser(requestedUser.id).credits) + " Credits**.")
    
bbCommands.register("balance", cmd_balance)


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
        if len(args.split(" ")) > 1 or not (args.startswith("<@") and args.endswith(">")) or ("!" in args and not bbUtil.isInt(args[3:-1])) or ("!" not in args and not bbUtil.isInt(args[2:-1])):
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return

        # get the discord user object for the requested user
        requestedUser = client.get_user(int(args[3:-1]))
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


"""
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
            outmsg = ":telescope: **" + message.author.name + "**, you did not find any criminals!"
            # Check if any bounties are close to the requested system in their route, defined by bbConfig.closeBountyThreshold
            for fac in bountiesDB.getFactions():
                for bounty in bountiesDB.getFactionBounties(fac):
                    if requestedSystem in bounty.route:
                        if 0 < bounty.route.index(bounty.answer) - bounty.route.index(requestedSystem) < bbConfig.closeBountyThreshold:
                            # Print any close bounty names
                            outmsg += "\n       • Local security forces spotted **" + criminalNameOrDiscrim(bounty.criminal) + "** here recently. "
            await message.channel.send(outmsg)

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
        await message.channel.send(":stopwatch: **" + message.author.name + "**, your *Khador drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")
    
bbCommands.register("check", cmd_check)


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
                outmessage += "\n • [" + criminalNameOrDiscrim(bounty.criminal) + "]" + " " * (bbData.longestBountyNameLength + 1 - len(criminalNameOrDiscrim(bounty.criminal))) + ": " + str(int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + bbData.numExtensions[int(endTimeStr[1][-1])] + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                if endTimeStr[4] != "00":
                    outmessage += ":" + endTimeStr[4]
                else:
                    outmessage += "   "
                outmessage += " - " + str(len(bounty.route)) + " possible system"
                if len(bounty.route) != 1:
                    outmessage += "s"
            await message.channel.send(outmessage + "```\nTrack down criminals and **win credits** using `" + bbConfig.commandPrefix + "route` and `" + bbConfig.commandPrefix + "check`!")

bbCommands.register("bounties", cmd_bounties)


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
        if requestedBountyName.startswith("<@"):
            outmsg += "\n:warning: **Don't tag users**, use their name and ID number like so: `" + bbConfig.commandPrefix + "route Trimatix#2244`"
        await message.channel.send(outmsg)
    
bbCommands.register("route", cmd_route)


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
    
bbCommands.register("system", cmd_system)


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
    
bbCommands.register("criminal", cmd_criminal)


"""
display leaderboards for different statistics
if no arguments are given, display the local leaderboard for lifetimeCredits
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
    stat = "lifetimeCredits"
    # "global" or the local guild name
    boardScope = message.guild.name
    # user friendly string for the stat
    boardTitle = "Total Credits Earned"
    # units for the stat
    boardUnit = "Credit"
    boardUnits = "Credits"

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
        if "g" in args:
            globalBoard = True
            boardScope = "Global Leaderboard"
        if "c" in args:
            stat = "credits"
            boardTitle = "Current Balance"
            boardUnit = "Credit"
            boardUnits = "Credits"
        elif "s" in args:
            stat = "systemsChecked"
            boardTitle = "Systems Checked"
            boardUnit = "System"
            boardUnits = "Systems"
        elif "w" in args:
            stat = "bountyWins"
            boardTitle = "Bounties Won"
            boardUnit = "Bounty"
            boardUnits = "Bounties"

    # get the requested stats and sort users by the stat
    inputDict = {}
    for user in usersDB.getUsers():
        if (globalBoard and client.get_user(user.id) is not None) or (not globalBoard and message.guild.get_member(user.id) is not None):
            inputDict[user.id] = user.getStatByName(stat)
    sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]

    # build the leaderboard embed
    leaderboardEmbed = makeEmbed(titleTxt=boardTitle, authorName=boardScope, icon=bbData.winIcon, col = bbData.factionColours["neutral"])

    # add all users to the leaderboard embed with places and values
    externalUser = False
    first = True
    for place in range(min(len(sortedUsers), 10)):
        # handling for global leaderboards and users not in the local guild
        if globalBoard and message.guild.get_member(sortedUsers[place][0]) is None:
            leaderboardEmbed.add_field(value="*" + str(place + 1) + ". " + client.get_user(sortedUsers[place][0]).mention, name=("⭐ " if first else "") + str(sortedUsers[place][1]) + " " + (boardUnit if sortedUsers[place][1] == 1 else boardUnits), inline=False)
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


"""
admin command for setting the current guild's play channel

@param message -- the discord message calling the command
@param args -- ignored
"""
async def admin_cmd_set_play_channel(message, args):
    guildsDB.getGuild(message.guild.id).setPlayChannelId(message.channel.id)
    await message.channel.send(":ballot_box_with_check: Bounty play channel set!")
    
bbCommands.register("set-play-channel", admin_cmd_set_play_channel, isAdmin=True)


"""
admin command printing help strings for admin commands as defined in bbData

@param message -- the discord message calling the command
@param args -- ignored
"""
async def admin_cmd_admin_help(message, args):
    helpEmbed = makeEmbed(titleTxt="BB Administrator Commands", thumb=client.user.avatar_url_as(size=64))
    for section in bbData.adminHelpDict.keys():
        helpEmbed.add_field(name="‎",value=section, inline=False)
        for currentCommand in bbData.adminHelpDict[section].keys():
            helpEmbed.add_field(name=currentCommand,value=bbData.adminHelpDict[section][currentCommand], inline=False)
    await message.channel.send(bbData.adminHelpIntro, embed=helpEmbed)
    
bbCommands.register("admin-help", admin_cmd_admin_help, isAdmin=True)



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


"""
developer command printing whether or not the current channel is the current guild's announcements channel

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_is_announce(message, args):
    await message.channel.send(guildsDB.getGuild(message.guild.id).hasAnnounceChannel())
    
bbCommands.register("is-announce", dev_cmd_is_announce, isDev=True)


"""
developer command printing the current guild's announcements channel if one is set

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_get_announce(message, args):
    await message.channel.send("<#" + str(guildsDB.getGuild(message.guild.id).getAnnounceChannelId()) + ">")
    
bbCommands.register("get-announce", dev_cmd_get_announce, isDev=True)


"""
developer command printing whether or not the current channel is the current guild's play channel

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_is_play(message, args):
    await message.channel.send(guildsDB.getGuild(message.guild.id).hasPlayChannel())
    
bbCommands.register("is-play", dev_cmd_is_play, isDev=True)


"""
developer command printing the current guild's play channel if one is set

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_get_play(message, args):
    await message.channel.send("<#" + str(guildsDB.getGuild(message.guild.id).getPlayChannelId()) + ">")
    
bbCommands.register("get-play", dev_cmd_get_play, isDev=True)


"""
developer command clearing all active bounties

@param message -- the discord message calling the command
@param args -- ignored
"""
async def dev_cmd_clear_bounties(message, args):
    bountiesDB.clearBounties()
    await message.channel.send(":ballot_box_with_check: Active bounties cleared!")
    
bbCommands.register("clear-bounties", dev_cmd_clear_bounties, isDev=True)


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
        newIcon = bData[8].rstrip(" ").lower()
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
    
bbCommands.register("make-bounty", dev_cmd_make_bounty, isDev=True)


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
        newIcon = bData[8].rstrip(" ").lower()
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
    
bbCommands.register("make-player-bounty", dev_cmd_make_player_bounty, isDev=True)



####### MAIN FUNCTIONS #######



"""
Bot initialisation (called on bot login) and behaviour loops.
Currently includes:
    - new bounty spawning
    - regular database saving to JSON

TODO: the delays system needs to be completely rewritten.
"""
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    # bot is now logged in
    botLoggedIn = True
    # amount of time waited since last bounty generation
    currentBountyWait = 0
    # amount of time waited since last save
    currentSaveWait = 0
    # new bounty delay period as a datetime.timedelta
    newBountyDelayDelta = None
    # fixed daily time to spawn bounties at as a datetime.timedelta
    newBountyFixedDailyTime = None

    # generate the amount of time to wait until the next bounty generation
    if bbConfig.newBountyDelayType == "random":
        # the amount of time to wait until generating a new bounty
        currentNewBountyDelay = random.randint(bbConfig.newBountyDelayMin, bbConfig.newBountyDelayMax)
    elif bbConfig.newBountyDelayType == "fixed":
        # This system should be changed to isntead generate a currentNewBountyDelay, rather than repeatedly checking against newBountyFixedDailyTime
        currentNewBountyDelay = 0
        newBountyDelayDelta = timedelta(days=bbConfig.newBountyFixedDelta["days"], hours=bbConfig.newBountyFixedDelta["hours"], minutes=bbConfig.newBountyFixedDelta["minutes"], seconds=bbConfig.newBountyFixedDelta["seconds"])
        if bbConfig.newBountyFixedUseDailyTime:
            newBountyFixedDailyTime = timedelta(hours=bbConfig.newBountyFixedDailyTime["hours"], minutes=bbConfig.newBountyFixedDailyTime["minutes"], seconds=bbConfig.newBountyFixedDailyTime["seconds"])
    
    # execute regular tasks while the bot is logged in
    while botLoggedIn:
        # select for bbConfig.delayFactor - should be a factor of all delay times (poor system!)
        await asyncio.sleep(bbConfig.delayFactor)
        # track the time waited
        currentBountyWait += bbConfig.delayFactor
        currentSaveWait += bbConfig.delayFactor
        
        # Make new bounties
        if bbConfig.newBountyDelayReset or (bbConfig.newBountyDelayType == "random" and currentBountyWait >= currentNewBountyDelay) or \
                (bbConfig.newBountyDelayType == "fixed" and timedelta(seconds=currentBountyWait) >= newBountyDelayDelta and ((not bbConfig.newBountyFixedUseDailyTime) or (bbConfig.newBountyFixedUseDailyTime and \
                    datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta - timedelta(minutes=bbConfig.delayFactor) \
                    <= datetime.utcnow() \
                    <= datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta + timedelta(minutes=bbConfig.delayFactor)))):
            # ensure a new bounty can be created
            if bountiesDB.canMakeBounty():
                newBounty = bbBounty.Bounty(bountyDB=bountiesDB)
                # activate and announce the bounty
                bountiesDB.addBounty(newBounty)
                await announceNewBounty(newBounty)

            # reset and regenerate the delay time for this period
            if bbConfig.newBountyDelayType == "random":
                currentNewBountyDelay = random.randint(bbConfig.newBountyDelayMin, bbConfig.newBountyDelayMax)
            else:
                currentNewBountyDelay = newBountyDelayDelta
                if bbConfig.newBountyFixedDeltaChanged:
                    newBountyDelayDelta = timedelta(days=bbConfig.newBountyFixedDelta["days"], hours=bbConfig.newBountyFixedDelta["hours"], minutes=bbConfig.newBountyFixedDelta["minutes"], seconds=bbConfig.newBountyFixedDelta["seconds"])
            currentBountyWait = 0
        # save the database
        if currentSaveWait >= bbConfig.saveDelay:
            saveDB(bbConfig.userDBPath, usersDB)
            saveDB(bbConfig.bountyDBPath, bountiesDB)
            saveDB(bbConfig.guildDBPath, guildsDB)
            print(datetime.now().strftime("%H:%M:%S: Data saved!"))
            currentSaveWait = 0


"""
Called every time a message is sent in a server that the bot has joined
Currently handles:
- random !drink
- command calling

@paran message: The message that triggered this command on sending
"""
@client.event
async def on_message(message):
    # ignore messages sent by BountyBot
    if message.author == client.user:
        return

    # randomly send '!drink' to the same channel
    bbConfig.randomDrinkNum -= 1
    if bbConfig.randomDrinkNum == 0:
        await message.channel.send("!drink")
        bbConfig.randomDrinkNum = random.randint(bbConfig.randomDrinkFactor / 10, bbConfig.randomDrinkFactor)

    # For any messages beginning with bbConfig.commandPrefix
    if message.content.split(" ")[0].lower() == (bbConfig.commandPrefix.rstrip(" ")):
        # replace special apostraphe characters with the universal '
        msgContent = message.content.replace("‘", "'").replace("’","'")

        # split the message into command and arguments
        if len(msgContent.split(" ")) > 1:
            # [!] command and args converted to lower case, watch out
            command = msgContent.split(" ")[1].lower()
            args = msgContent[len(bbConfig.commandPrefix) + len(command) + 1:].lower()

        # if no command is given, call help with no arguments
        else:
            args = ""
            command = "help"

        # infer the message author's permissions
        userIsAdmin = message.author.permissions_in(message.channel).administrator
        userIsDev = message.author.id in bbConfig.developers

        # Call the requested command
        commandFound = await bbCommands.call(command, message, args, isAdmin=userIsAdmin, isDev=userIsDev)

        # Command not found, send an error message.
        if not commandFound:
            userTitle = bbConfig.devTitle if userIsDev else (bbConfig.adminTitle if userIsAdmin else bbConfig.userTitle)
            await message.channel.send(""":question: Can't do that, """ + userTitle + """. Type `""" + bbConfig.commandPrefix + """help` for a list of commands! **o7**""")


client.run(bbPRIVATE.botToken)
