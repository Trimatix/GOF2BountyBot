


####### IMPORTS #######



import discord
from discord.ext import commands

from datetime import datetime, timedelta
import asyncio
import random
# user for leaderboard sorting
import operator

# may replace these imports with a from . import * at some point
from .bbConfig import bbConfig, bbData, bbPRIVATE
from .bbObjects import bbBounty, bbBountyConfig
from .bbDatabases import bbBountyDB, bbGuildDB, bbUserDB
from . import bbUtil



####### DATABASE METHODS #######



def loadUsersDB(filePath):
    return bbUserDB.fromDict(bbUtil.readJSON(filePath))
def loadGuildsDB(filePath):
    return bbGuildDB.fromDict(bbUtil.readJSON(filePath))
def loadBountiesDB(filePath):
    return bbBountyDB.fromDict(bbUtil.readJSON(filePath), bbConfig.maxBountiesPerFaction, dbReload=True)


def saveDB(dbPath, db):
    bbUtil.writeJSON(dbPath, db.toDict())


## Global Variables
client = commands.Bot(command_prefix=bbConfig.commandPrefix)
# client.remove_command("help")

usersDB = loadUsersDB(bbConfig.userDBPath)
guildsDB = loadGuildsDB(bbConfig.guildDBPath)
bountiesDB = loadBountiesDB(bbConfig.bountyDBPath)



####### DISCORD UTIL FUNCTIONS #######



def makeRoute(start, end):
    return bbUtil.bbAStar(start, end, bbData.builtInSystemObjs)


def userTagOrDiscrim(userID):
    userObj = client.get_user(int(userID.lstrip("<@!").rstrip(">")))
    if userObj is not None:
        return userObj.name + "#" + userObj.discriminator
    # Return criminal name as a fall back - might replace this with '#UNKNOWNUSER#' at some point.
    print("USERIDNAMEORDISCRIM UNKNOWN USER")
    return userID


def criminalNameOrDiscrim(criminal):
    if not criminal.isPlayer:
        return criminal.name
    return userTagOrDiscrim(criminal.name)
    


async def announceNewBounty(newBounty):
    bountyEmbed = makeEmbed(titleTxt=criminalNameOrDiscrim(newBounty.criminal), desc="⛓ __New Bounty Available__", col=bbData.factionColours[newBounty.faction], thumb=newBounty.criminal.icon, footerTxt=newBounty.faction.title())
    bountyEmbed.add_field(name="Reward:", value=str(newBounty.reward) + " Credits")
    bountyEmbed.add_field(name="Possible Systems:", value=len(newBounty.route))
    bountyEmbed.add_field(name="See the culprit's route with:", value="`" + bbConfig.commandPrefix + "route " + criminalNameOrDiscrim(newBounty.criminal) + "`", inline=False)
    msg = "A new bounty is now available from **" + newBounty.faction.title() + "** central command:"

    for currentGuild in guildsDB.getGuilds():
        if currentGuild.hasAnnounceChannel():
            currentChannel = client.get_channel(currentGuild.getAnnounceChannelId())
            if currentChannel is not None:
                await currentChannel.send(msg, embed=bountyEmbed)

async def announceBountyWon(bounty, rewards, winningGuildObj, winningUserId):
    for currentGuild in guildsDB.getGuilds():
        if currentGuild.hasPlayChannel():
            rewardsEmbed = makeEmbed(titleTxt="Bounty Complete!",authorName=criminalNameOrDiscrim(bounty.criminal) + " Arrested",icon=bounty.criminal.icon,col=bbData.factionColours[bounty.faction])
            
            if client.get_guild(currentGuild.id).get_member(winningUserId) is None:
                rewardsEmbed.add_field(name="1. Winner, " + str(rewards[winningUserId]["reward"]) + " credits:", value=str(client.get_user(winningUserId)) + " checked " + str(int(rewards[winningUserId]["checked"])) + " system" + ("s" if int(rewards[winningUserId]["checked"]) != 1 else ""), inline=False)
            else:
                rewardsEmbed.add_field(name="1. Winner, " + str(rewards[winningUserId]["reward"]) + " credits:", value="<@" + str(winningUserId) + "> checked " + str(int(rewards[winningUserId]["checked"])) + " system" + ("s" if int(rewards[winningUserId]["checked"]) != 1 else ""), inline=False)
            
            place = 2
            for userID in rewards:
                if not rewards[userID]["won"]:
                    if client.get_guild(currentGuild.id).get_member(userID) is None:
                        rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value=str(client.get_user(userID)) + " checked " + str(int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[userID]["checked"]) != 1 else ""), inline=False)
                    else:
                        rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value="<@" + str(userID) + "> checked " + str(int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[userID]["checked"]) != 1 else ""), inline=False)
                    place += 1
            
            if client.get_channel(currentGuild.getPlayChannelId()) is not None:
                if int(currentGuild.id) == winningGuildObj.id:
                    await client.get_channel(currentGuild.getPlayChannelId()).send(":trophy: **You win!**\n**" + winningGuildObj.get_member(winningUserId).display_name + "** located and EMP'd **" + bounty.criminal.name + "**, who has been arrested by local security forces. :chains:", embed=rewardsEmbed)
                else:
                    await client.get_channel(currentGuild.getPlayChannelId()).send(":trophy: Another server has located **" + bounty.criminal.name + "**!", embed=rewardsEmbed)


def makeEmbed(titleTxt="",desc="",col=discord.Colour.blue(), footerTxt="", img="", thumb="", authorName="", icon=""):
    embed = discord.Embed(title=titleTxt, description=desc, colour=col)
    if footerTxt != "": embed.set_footer(text=footerTxt)
    # embed.set_image(url=img)
    if thumb != "": embed.set_thumbnail(url=thumb)
    if icon != "": embed.set_author(name=authorName, icon_url=icon)
    return embed



####### USER COMMANDS #######



# @client.command(name='runHelp')
async def cmd_help(message, args):
    helpEmbed = makeEmbed(titleTxt="BountyBot Commands", thumb=client.user.avatar_url_as(size=64))
    for section in bbData.helpDict.keys():
        helpEmbed.add_field(name="‎",value=section, inline=False)
        for currentCommand in bbData.helpDict[section].keys():
            helpEmbed.add_field(name=currentCommand,value=bbData.helpDict[section][currentCommand], inline=False)
    await message.channel.send(bbData.helpIntro, embed=helpEmbed)


async def cmd_hello(message, args):
    await message.channel.send("Greetings, pilot! **o7**")


async def cmd_balance(message, args):
    if args == "":
        if not usersDB.userIDExists(message.author.id):
            usersDB.addUser(message.author.id)
        await message.channel.send(":moneybag: **" + message.author.name + "**, you have **" + str(usersDB.getUser(message.author.id).credits) + " Credits**.")
    else:
        if len(args.split(" ")) > 1 or not (args.startswith("<@") and args.endswith(">")) or ("!" in args and not bbUtil.isInt(args[3:-1])) or ("!" not in args and not bbUtil.isInt(args[2:-1])):
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return
        if "!" in args:
            requestedUser = client.get_user(int(args[3:-1]))
        else:
            requestedUser = client.get_user(int(args[2:-1]))
        if not usersDB.userIDExists(requestedUser.id):
            usersDB.addUser(requestedUser.id)
        await message.channel.send(":moneybag: **" + requestedUser.name + "** has **" + str(usersDB.getUser(requestedUser.id).credits) + " Credits**.")


async def cmd_stats(message, args):
    if args == "":
        statsEmbed = makeEmbed(col=bbData.factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=message.author.name, footerTxt="Pilot number #" + message.author.discriminator, thumb=message.author.avatar_url_as(size=64))
        if not usersDB.userIDExists(message.author.id):
            statsEmbed.add_field(name="Credits balance:",value=0, inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=0, inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=0, inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=0, inline=True)
        else:
            userObj = usersDB.getUser(message.author.id)
            statsEmbed.add_field(name="Credits balance:",value=str(userObj.credits), inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=str(userObj.lifetimeCredits), inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=str(userObj.systemsChecked), inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=str(userObj.bountyWins), inline=True)
        await message.channel.send(embed=statsEmbed)
        return
    else:
        if len(args.split(" ")) > 1 or not (args.startswith("<@") and args.endswith(">")) or ("!" in args and not bbUtil.isInt(args[3:-1])) or ("!" not in args and not bbUtil.isInt(args[2:-1])):
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return
        requestedUser = client.get_user(int(args[3:-1]))
        if requestedUser is None:
            await message.channel.send(":x: **Invalid user!** use `" + bbConfig.commandPrefix + "balance` to display your own balance, or `" + bbConfig.commandPrefix + "balance @userTag` to display someone else's balance!")
            return
        statsEmbed = makeEmbed(col=bbData.factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=requestedUser.name, footerTxt="Pilot number #" + requestedUser.discriminator, thumb=requestedUser.avatar_url_as(size=64))
        if not usersDB.userIDExists(requestedUser.id):
            statsEmbed.add_field(name="Credits balance:",value=0, inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=0, inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=0, inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=0, inline=True)
        else:
            userObj = usersDB.getUser(requestedUser.id)
            statsEmbed.add_field(name="Credits balance:",value=str(userObj.credits), inline=True)
            statsEmbed.add_field(name="Lifetime total credits earned:", value=str(userObj.lifetimeCredits), inline=True)
            statsEmbed.add_field(name="‎",value="‎", inline=False)
            statsEmbed.add_field(name="Total systems checked:",value=str(userObj.systemsChecked), inline=True)
            statsEmbed.add_field(name="Total bounties won:", value=str(userObj.bountyWins), inline=True)
        await message.channel.send(embed=statsEmbed)


async def cmd_map(message, args):
    if args == "-g":
        await message.channel.send(bbData.mapImageWithGraphLink)
    else:
        await message.channel.send(bbData.mapImageNoGraphLink)


async def cmd_check(message, args):
    if args == "":
        await message.channel.send(":x: Please provide a system to check! E.g: `" + bbConfig.commandPrefix + "check Pescal Inartu`")
        return
    requestedSystem = args.title()
    systObj = None
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(requestedSystem):
            systObj = bbData.builtInSystemObjs[syst]

    if systObj is None:
        if len(requestedSystem) < 20:
            await message.channel.send(":x: The **" + requestedSystem + "** system is not on my star map! :map:")
        else:
            await message.channel.send(":x: The **" + requestedSystem[0:15] + "**... system is not on my star map! :map:")
        return
    requestedSystem = systObj.name

    if not usersDB.userIDExists(message.author.id):
        usersDB.addUser(message.author.id)
    if datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd) < datetime.utcnow():
        bountyWon = False
        for fac in bountiesDB.getFactions():
            # now list of objects rather than indices
            toPop = []
            for bounty in bountiesDB.getFactionBounties(fac):
                if bounty.check(requestedSystem, message.author.id) == 3:
                    bountyWon = True
                    rewards = bounty.calcRewards()
                    for userID in rewards:
                        usersDB.getUser(userID).credits += rewards[userID]["reward"]
                        usersDB.getUser(userID).lifetimeCredits += rewards[userID]["reward"]
                    toPop += [bounty]
                    await announceBountyWon(bounty, rewards, message.guild, message.author.id)
            for bounty in toPop:
                bountiesDB.removeBountyObj(bounty)
        if bountyWon:
            usersDB.getUser(message.author.id).bountyWins += 1
            await message.channel.send(":moneybag: **" + message.author.name + "**, you now have **" + str(usersDB.getUser(message.author.id).credits) + " Credits!**")
        else:
            outmsg = ":telescope: **" + message.author.name + "**, you did not find any criminals!"
            for fac in bountiesDB.getFactions():
                for bounty in bountiesDB.getFactionBounties(fac):
                    if requestedSystem in bounty.route:
                        if 0 < bounty.route.index(bounty.answer) - bounty.route.index(requestedSystem) < 4:
                            outmsg += "\n       • Local security forces spotted **" + criminalNameOrDiscrim(bounty.criminal) + "** here recently. "
            await message.channel.send(outmsg)

        usersDB.getUser(message.author.id).systemsChecked += 1
        usersDB.getUser(message.author.id).bountyCooldownEnd = (datetime.utcnow() + timedelta(minutes=bbConfig.checkCooldown["minutes"])).timestamp()
    else:
        diff = datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd) - datetime.utcnow()
        minutes = int(diff.total_seconds() / 60)
        seconds = int(diff.total_seconds() % 60)
        await message.channel.send(":stopwatch: **" + message.author.name + "**, your *Khador drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")


async def cmd_bounties(message, args):
    if args == "":
        outmessage = "__**Active Bounties**__\nTimes given in UTC. See more detailed information with `" + bbConfig.commandPrefix + "bounties <faction>`\n```css"
        preLen = len(outmessage)
        for fac in bountiesDB.getFactions():
            if bountiesDB.hasBounties(faction=fac):
                outmessage += "\n • [" + fac.title() + "]: "
                for bounty in bountiesDB.getFactionBounties(fac):
                    outmessage += criminalNameOrDiscrim(bounty.criminal) + ", "
                outmessage = outmessage[:-2]
        if len(outmessage) == preLen:
            outmessage += "\n[  No currently active bounties! Please check back later.  ]"
        await message.channel.send(outmessage + "```")
        return
    requestedFaction = args.lower()
    if requestedFaction not in bbData.bountyFactions:
        if len(requestedFaction) < 20:
            await message.channel.send(":x: Unrecognised faction: **" + requestedFaction + "**")
        else:
            await message.channel.send(":x: Unrecognised faction **" + requestedFaction[0:15] + "**...")
        return
    if not bountiesDB.hasBounties(faction=requestedFaction):
        await message.channel.send(":stopwatch: There are no **" + requestedFaction.title() + "** bounties active currently!")
    else:
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


async def cmd_route(message, args):
    if args == "":
        await message.channel.send(":x: Please provide the criminal name! E.g: `" + bbConfig.commandPrefix + "route Kehnor`")
        return
    requestedBountyName = args
    if bountiesDB.bountyNameExists(requestedBountyName.lower()):
        bounty = bountiesDB.getBounty(requestedBountyName.lower())
        outmessage = "**" + criminalNameOrDiscrim(bounty.criminal) + "**'s current route:\n> "
        for system in bounty.route:
            outmessage += " " + ("~~" if bounty.checked[system] != -1 else "") + system + ("~~" if bounty.checked[system] != -1 else "") + ","
        outmessage = outmessage[:-1] + ". :rocket:"
        await message.channel.send(outmessage)
    else:
        outmsg = ":x: That pilot isn't on any bounty boards! :clipboard:"
        if requestedBountyName.startswith("<@"):
            outmsg += "\n:warning: **Don't tag users**, use their name and ID number like so: `" + bbConfig.commandPrefix + "route Trimatix#2244`"
        await message.channel.send(outmsg)


async def cmd_make_route(message, args):
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
    systemsFound = {requestedStart: False, requestedEnd: False}
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(requestedStart):
            systemsFound[requestedStart] = True
            startSyst = syst
        if bbData.builtInSystemObjs[syst].isCalled(requestedEnd):
            systemsFound[requestedEnd] = True
            endSyst = syst
            
    for syst in [requestedStart, requestedEnd]:
        if not systemsFound[syst]:
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system is not on my star map! :map:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system is not on my star map! :map:")
            return
    for syst in [startSyst, endSyst]:
        if not bbData.builtInSystemObjs[syst].hasJumpGate():
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system does not have a jump gate! :rocket:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system does not have a jump gate! :rocket:")
            return
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


async def cmd_system(message, args):
    if args == "":
        await message.channel.send(":x: Please provide a system! Example: `" + bbConfig.commandPrefix + "system Augmenta`")
        return
    systArg = args.title()
    systObj = None
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(systArg):
            systObj = bbData.builtInSystemObjs[syst]

    if systObj is None:
        if len(systArg) < 20:
            await message.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
        else:
            await message.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
        return

    else:
        neighboursStr = ""
        for x in systObj.neighbours:
            neighboursStr += x + ", "
        if neighboursStr == "":
            neighboursStr = "No Jumpgate"
        else:
            neighboursStr = neighboursStr[:-2]
        
        statsEmbed = makeEmbed(col=bbData.factionColours[systObj.faction], desc="__System Information__", titleTxt=systObj.name, footerTxt=systObj.faction.title(), thumb=bbData.factionIcons[systObj.faction])
        statsEmbed.add_field(name="Security Level:",value=bbData.securityLevels[systObj.security].title())
        statsEmbed.add_field(name="Neighbour Systems:", value=neighboursStr)
        if len(systObj.aliases) > 1:
            aliasStr = ""
            for alias in systObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if systObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + systObj.wiki + ")", inline=False)
        await message.channel.send(embed=statsEmbed)


async def cmd_criminal(message, args):
    if args == "":
        await message.channel.send(":x: Please provide a criminal! Example: `" + bbConfig.commandPrefix + "criminal Toma Prakupy`")
        return
    criminalName = args.title()
    criminalObj = None
    for crim in bbData.builtInCriminalObjs.keys():
        if bbData.builtInCriminalObjs[crim].isCalled(criminalName):
            criminalObj = bbData.builtInCriminalObjs[crim]

    if criminalObj is None:
        if len(criminalName) < 20:
            await message.channel.send(":x: **" + criminalName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + criminalName[0:15] + "**... is not in my database! :detective:")
        return

    else:
        statsEmbed = makeEmbed(col=bbData.factionColours[criminalObj.faction], desc="__Criminal File__", titleTxt=criminalObj.name, thumb=criminalObj.icon)
        statsEmbed.add_field(name="Wanted By:",value=criminalObj.faction.title() + "s")
        if len(criminalObj.aliases) > 1:
            aliasStr = ""
            for alias in criminalObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
        if criminalObj.hasWiki:
            statsEmbed.add_field(name="‎", value="[Wiki](" + criminalObj.wiki + ")", inline=False)
        await message.channel.send(embed=statsEmbed)


async def cmd_leaderboard(message, args):
    globalBoard = False
    stat = "lifetimeCredits"
    boardScope = message.guild.name
    boardTitle = "Total Credits Earned"
    boardUnit = "Credit"
    boardUnits = "Credits"

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

    inputDict = {}
    for user in usersDB.getUsers():
        if (globalBoard and client.get_user(user.id) is not None) or (not globalBoard and message.guild.get_member(user.id) is not None):
            inputDict[user.id] = user.getStatByName(stat)
    sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]

    leaderboardEmbed = makeEmbed(titleTxt=boardTitle, authorName=boardScope, icon=bbData.winIcon, col = bbData.factionColours["neutral"])

    externalUser = False
    first = True
    for place in range(min(len(sortedUsers), 10)):
        if globalBoard and message.guild.get_member(sortedUsers[place][0]) is None:
            leaderboardEmbed.add_field(value="*" + str(place + 1) + ". " + client.get_user(sortedUsers[place][0]).mention, name=("⭐ " if first else "") + str(sortedUsers[place][1]) + " " + (boardUnit if sortedUsers[place][1] == 1 else boardUnits), inline=False)
            externalUser = True
            if first: first = False
        else:
            leaderboardEmbed.add_field(value=str(place + 1) + ". " + message.guild.get_member(sortedUsers[place][0]).mention, name=("⭐ " if first else "") + str(sortedUsers[place][1]) + " " + (boardUnit if sortedUsers[place][1] == 1 else boardUnits), inline=False)
            if first: first = False
    if externalUser:
        leaderboardEmbed.set_footer(text="An `*` indicates a user that is from another server.")
    await message.channel.send(embed=leaderboardEmbed)


async def admin_cmd_set_announce_channel(message, args):
    guildsDB.getGuild(message.guild.id).setAnnounceChannelId(message.channel.id)
    await message.channel.send(":ballot_box_with_check: Announcements channel set!")


async def admin_cmd_set_play_channel(message, args):
    guildsDB.getGuild(message.guild.id).setPlayChannelId(message.channel.id)
    await message.channel.send(":ballot_box_with_check: Bounty play channel set!")


async def admin_cmd_admin_help(message, args):
    helpEmbed = makeEmbed(titleTxt="BB Administrator Commands", thumb=client.user.avatar_url_as(size=64))
    for section in bbData.adminHelpDict.keys():
        helpEmbed.add_field(name="‎",value=section, inline=False)
        for currentCommand in bbData.adminHelpDict[section].keys():
            helpEmbed.add_field(name=currentCommand,value=bbData.adminHelpDict[section][currentCommand], inline=False)
    await message.channel.send(bbData.adminHelpIntro, embed=helpEmbed)



####### DEVELOPER COMMANDS #######



async def dev_cmd_sleep(message, args):
    await message.channel.send("zzzz....")
    bbConfig.botLoggedIn = False
    await client.logout()
    saveDB(bbConfig.userDBPath, usersDB)
    saveDB(bbConfig.bountyDBPath, bountiesDB)
    saveDB(bbConfig.guildDBPath, guildsDB)
    print(datetime.now().strftime("%H:%M:%S: Data saved!"))


async def dev_cmd_save(message, args):
    saveDB(bbConfig.userDBPath, usersDB)
    saveDB(bbConfig.bountyDBPath, bountiesDB)
    saveDB(bbConfig.guildDBPath, guildsDB)
    print(datetime.now().strftime("%H:%M:%S: Data saved manually!"))
    await message.channel.send("saved!")


async def dev_cmd_is_announce(message, args):
    await message.channel.send(guildsDB.getGuild(message.guild.id).hasAnnounceChannel())


async def dev_cmd_get_announce(message, args):
    await message.channel.send("<#" + str(guildsDB.getGuild(message.guild.id).getAnnounceChannelId()) + ">")


async def dev_cmd_is_play(message, args):
    await message.channel.send(guildsDB.getGuild(message.guild.id).hasPlayChannel())


async def dev_cmd_get_play(message, args):
    await message.channel.send("<#" + str(guildsDB.getGuild(message.guild.id).getPlayChannelId()) + ">")


async def dev_cmd_clear_bounties(message, args):
    bountiesDB.clearBounties()
    await message.channel.send(":ballot_box_with_check: Active bounties cleared!")


async def dev_cmd_get_cooldown(message, args):
    diff = datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd) - datetime.utcnow()
    minutes = int(diff.total_seconds() / 60)
    seconds = int(diff.total_seconds() % 60)
    await message.channel.send(str(usersDB.getUser(message.author.id).bountyCooldownEnd) + " = " + str(minutes) + "m, " + str(seconds) + "s.")
    await message.channel.send(datetime.utcfromtimestamp(usersDB.getUser(message.author.id).bountyCooldownEnd).strftime("%Hh%Mm%Ss"))
    await message.channel.send(datetime.utcnow().strftime("%Hh%Mm%Ss"))


async def dev_cmd_reset_cool(message, args):
    if args == "":
        usersDB.getUser(message.author.id).bountyCooldownEnd = datetime.utcnow().timestamp()
    else:
        if "!" in args:
            requestedUser = client.get_user(int(args[2:-1]))
        else:
            requestedUser = client.get_user(int(args[1:-1]))
        usersDB.getUser(requestedUser).bountyCooldownEnd = datetime.utcnow().timestamp()
    await message.channel.send("Done!")


async def dev_cmd_setcheckcooldown(message, args):
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    if not bbUtil.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    bbConfig.checkCooldown["minutes"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)


async def dev_cmd_setbountyperiodm(message, args):
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    if not bbUtil.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    bbConfig.newBountyFixedDelta["minutes"] = int(args)
    bbConfig.newBountyFixedDeltaChanged = True
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)


async def dev_cmd_setbountyperiodh(message, args):
    if args == "":
        await message.channel.send(":x: please give the number of minutes!")
        return
    if not bbUtil.isInt(args):
        await message.channel.send(":x: that's not a number!")
        return
    bbConfig.newBountyFixedDeltaChanged = True
    bbConfig.newBountyFixedDelta["hours"] = int(args)
    await message.channel.send("Done! *you still need to update the file though* " + message.author.mention)


async def dev_cmd_resetnewbountycool(message, args):
    bbConfig.newBountyDelayReset = True
    await message.channel.send(":ballot_box_with_check: New bounty cooldown reset!")


async def dev_cmd_canmakebounty(message, args):
    newFaction = args.lower()
    if not bountiesDB.factionExists(newFaction):
        await message.channel.send("not a faction: '" + newFaction + "'")
    else:
        await message.channel.send(bountiesDB.factionCanMakeBounty(newFaction.lower()))


async def dev_cmd_make_bounty(message, args):
    if args == "":
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB)
    elif len(args.split("+")) == 2:
        newFaction = args.split("+")[1]
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction))
    # 9 args plus account for empty string at the start of the split
    elif len(args.split("+")) == 10:
        builtIn = False
        builtInCrimObj = None
        # [1:] remove empty string before + splits 
        bData = args.split("+")[1:]
        newFaction = bData[0].rstrip(" ")
        if newFaction == "auto":
            newFaction = ""
        newName = bData[1].rstrip(" ").title()
        if newName == "Auto":
            newName = ""
        else:
            for crim in bbData.builtInCriminalObjs.values():
                if crim.isCalled(newName):
                    builtIn = True
                    builtInCrimObj = crim
                    newName = crim.name
                    break
            
            if newName != "" and bountiesDB.bountyNameExists(newName):
                await message.channel.send(":x: That pilot is already wanted!")
                return
        newRoute = bData[2].rstrip(" ")
        if newRoute == "auto":
            newRoute = []
        else:
            newRoute = bData[2].split(",")
            newRoute[-1] = newRoute[-1].rstrip(" ")
        newStart = bData[3].rstrip(" ")
        if newStart == "auto":
            newStart = ""
        newEnd = bData[4].rstrip(" ")
        if newEnd == "auto":
            newEnd = ""
        newAnswer = bData[5].rstrip(" ")
        if newAnswer == "auto":
            newAnswer = ""
        newReward = bData[6].rstrip(" ")
        if newReward == "auto":
            newReward = -1
        newReward = int(newReward)
        newEndTime = bData[7].rstrip(" ")
        if newEndTime == "auto":
            newEndTime = -1.0
        newEndTime = float(newEndTime)
        newIcon = bData[8].rstrip(" ").lower()
        if newIcon == "auto":
            newIcon = "" if not builtIn else builtInCrimObj.icon
        if builtIn:
            newBounty = bbBounty.Bounty(bountyDB=bountiesDB, criminalObj=builtInCrimObj, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon))
        else:
            newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon))
    else:
        await message.channel.send("incorrect syntax. give +faction +name +route +start +end +answer +reward +endtime +icon")
    bountiesDB.addBounty(newBounty)
    await announceNewBounty(newBounty)


async def dev_cmd_make_player_bounty(message, args):
    if len(args.split(" ")) == 1:
        requestedID = int(args.lstrip("<@!").rstrip(">"))
        if not bbUtil.isInt(requestedID) or (client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(client.get_user(requestedID).avatar_url_as(size=64)), aliases=[userTagOrDiscrim(args)]))
    elif len(args.split("+")) == 2:
        requestedID = int(args.split(" ")[0].lstrip("<@!").rstrip(">"))
        if not bbUtil.isInt(requestedID) or (client.get_user(int(requestedID))) is None:
            await message.channel.send(":x: Player not found!")
            return
        newFaction = args.split("+")[1]
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(client.get_user(requestedID).avatar_url_as(size=64)), faction=newFaction, aliases=[userTagOrDiscrim(args.split(" ")[0])]))
    elif len(args.split("+")) == 10:
        # [1:] remove starting empty string before + split
        bData = args.split("+")[1:]
        newFaction = bData[0].rstrip(" ")
        if newFaction == "auto":
            newFaction = ""
        newName = bData[1].rstrip(" ").title()
        if newName == "Auto":
            newName = ""
        else:
            requestedID = int(newName.lstrip("<@!").rstrip(">"))
            if not bbUtil.isInt(requestedID) or (client.get_user(int(requestedID))) is None:
                await message.channel.send(":x: Player not found!")
                return
        newRoute = bData[2].rstrip(" ")
        if newRoute == "auto":
            newRoute = []
        else:
            newRoute = bData[2].split(",")
            newRoute[-1] = newRoute[-1].rstrip(" ")
        newStart = bData[3].rstrip(" ")
        if newStart == "auto":
            newStart = ""
        newEnd = bData[4].rstrip(" ")
        if newEnd == "auto":
            newEnd = ""
        newAnswer = bData[5].rstrip(" ")
        if newAnswer == "auto":
            newAnswer = ""
        newReward = bData[6].rstrip(" ")
        if newReward == "auto":
            newReward = -1
        newReward = int(newReward)
        newEndTime = bData[7].rstrip(" ")
        if newEndTime == "auto":
            newEndTime = -1.0
        newEndTime = float(newEndTime)
        newIcon = bData[8].rstrip(" ").lower()
        if newIcon == "auto":
            newIcon = str(client.get_user(int(newName.lstrip("<@!").rstrip(">"))).avatar_url_as(size=64))
        newBounty = bbBounty.Bounty(bountyDB=bountiesDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=True, icon=newIcon, aliases=[userTagOrDiscrim(newName)]))
    else:
        await message.channel.send("incorrect syntax. give +faction +userTag +route +start +end +answer +reward +endtime +icon")
    bountiesDB.addBounty(newBounty)
    await announceNewBounty(newBounty)



####### COMMANDS DATABASES #######



userCommands = {"help":cmd_help, "hello":cmd_hello, "balance":cmd_balance, "stats":cmd_stats,
                    "map":cmd_map, "check":cmd_check, "bounties":cmd_bounties, "route":cmd_route,
                    "make-route":cmd_make_route, "system":cmd_system, "criminal":cmd_criminal,
                    "leaderboard":cmd_leaderboard}

adminCommands = {"set-announce-channel":admin_cmd_set_announce_channel, "set-play-channel":admin_cmd_set_play_channel,
                    "admin-help":admin_cmd_admin_help}

devCommands = {"sleep":dev_cmd_sleep, "save":dev_cmd_save, "is-announce":dev_cmd_is_announce, "get-announce":dev_cmd_get_announce,
                    "is-play":dev_cmd_is_play, "get-play":dev_cmd_get_play, "clear-bounties":dev_cmd_clear_bounties,
                    "get-cool":dev_cmd_get_cooldown, "reset-cool":dev_cmd_reset_cool, "setcheckcooldown":dev_cmd_setcheckcooldown,
                    "setbountyperiodm":dev_cmd_setbountyperiodm, "setbountyperiodh":dev_cmd_setbountyperiodh,
                    "resetnewbountycool":dev_cmd_resetnewbountycool, "canmakebounty":dev_cmd_canmakebounty, "make-bounty":dev_cmd_make_bounty,
                    "make-player-bounty":dev_cmd_make_player_bounty}



####### MAIN FUNCTIONS #######



@client.event
async def on_ready():
    # This function accesses global variable "client"

    print('We have logged in as {0.user}'.format(client))
    bbConfig.botLoggedIn = True
    currentBountyWait = 0
    currentSaveWait = 0
    newBountyDelayDelta = None
    newBountyFixedDailyTime = None

    if bbConfig.newBountyDelayType == "random":
        currentNewBountyDelay = random.randint(bbConfig.newBountyDelayMin, bbConfig.newBountyDelayMax)
    elif bbConfig.newBountyDelayType == "fixed":
        currentNewBountyDelay = 0
        newBountyDelayDelta = timedelta(days=bbConfig.newBountyFixedDelta["days"], hours=bbConfig.newBountyFixedDelta["hours"], minutes=bbConfig.newBountyFixedDelta["minutes"], seconds=bbConfig.newBountyFixedDelta["seconds"])
        if bbConfig.newBountyFixedUseDailyTime:
            newBountyFixedDailyTime = timedelta(hours=bbConfig.newBountyFixedDailyTime["hours"], minutes=bbConfig.newBountyFixedDailyTime["minutes"], seconds=bbConfig.newBountyFixedDailyTime["seconds"])
    
    while bbConfig.botLoggedIn:
        await asyncio.sleep(bbConfig.delayFactor)
        currentBountyWait += bbConfig.delayFactor
        currentSaveWait += bbConfig.delayFactor
        
        # Make new bounties
        if bbConfig.newBountyDelayReset or (bbConfig.newBountyDelayType == "random" and currentBountyWait >= currentNewBountyDelay) or \
                (bbConfig.newBountyDelayType == "fixed" and timedelta(seconds=currentBountyWait) >= newBountyDelayDelta and ((not bbConfig.newBountyFixedUseDailyTime) or (bbConfig.newBountyFixedUseDailyTime and \
                    datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta - timedelta(minutes=bbConfig.delayFactor) \
                    <= datetime.utcnow() \
                    <= datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta + timedelta(minutes=bbConfig.delayFactor)))):
            if bountiesDB.canMakeBounty():
                newBounty = bbBounty.Bounty(bountyDB=bountiesDB)
                bountiesDB.addBounty(newBounty)
                await announceNewBounty(newBounty)

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


@client.event
async def on_message(message):
    # The global "client" variable is accessed within this function.
    if message.author == client.user:
        return

    bbConfig.randomDrinkNum -= 1
    if bbConfig.randomDrinkNum == 0:
        await message.channel.send("!drink")
        bbConfig.randomDrinkNum = random.randint(bbConfig.randomDrinkFactor / 10, bbConfig.randomDrinkFactor)

    if message.content.split(" ")[0].lower() == (bbConfig.commandPrefix.rstrip(" ")):
        msgContent = message.content.replace("‘", "'").replace("’","'")
        if len(msgContent.split(" ")) > 1:
            # [!] command and args converted to lower case, watch out
            command = msgContent.split(" ")[1].lower()
            args = msgContent[len(bbConfig.commandPrefix) + len(command) + 1:].lower()
        else:
            args = ""
            command = "help"

        try:
            await userCommands[command](message, args)
        except KeyError:
            if message.author.id in bbConfig.developers or message.author.permissions_in(message.channel).administrator:
                try:
                    await adminCommands[command](message, args)
                except KeyError:
                    if message.author.id in bbConfig.developers:
                        try:
                            await devCommands[command](message, args)
                        except KeyError:
                            await message.channel.send(""":question: Can't do that, officer. Type `""" + bbConfig.commandPrefix + """help` for a list of commands! **o7**""")
                    else:
                        await message.channel.send(""":question: Can't do that, commander. Type `""" + bbConfig.commandPrefix + """help` for a list of commands! **o7**""")
            else:
                await message.channel.send(""":question: Can't do that, pilot. Type `""" + bbConfig.commandPrefix + """help` for a list of commands! **o7**""")


client.run(bbPRIVATE.botToken)
