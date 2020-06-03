import discord
from datetime import datetime, timedelta
import asyncio
import random
import operator

# may replace these imports with a from . import * at some point
from .bbConfig import bbConfig, bbData, bbPRIVATE
from .bbObjects import bbBounty, bbBountyConfig
from .bbDatabases import bbBountyDB, bbGuildDB, bbUserDB
from . import bbUtil


def criminalNameOrDiscrim(client, criminal):
    if not criminal.isPlayer:
        return criminal.name

    userID = int(criminal.name.lstrip("<@!").rstrip(">"))
    if client.get_user(userID) is not None:
        return str(client.get_user(userID))

    # Return criminal name as a fall back - might replace this with '#UNKNOWNUSER#' at some point.    
    return criminal.name


def makeRoute(start, end):
    return bbUtil.bbAStar(start, end, bbData.builtInSystemObjs)





def loadDB(DCClient):
    db = bbUtil.readJDB("BBDB.json")
    if "announceChannel" in db:
        bbConfig.announceChannel = db["announceChannel"]
    if "playChannel" in db:
        bbConfig.playChannel = db["playChannel"]
    if "bounties" in db:
        for fac in db["bounties"]:
            currentBounties = []
            for bounty in db["bounties"][fac]:
                currentBounties.append(bbBounty.fromDict(bounty, dbReload=True))
            db["bounties"][fac] = currentBounties
    return db


def saveDB(db):
    BBDB["announceChannel"] = bbConfig.announceChannel
    BBDB["playChannel"] = bbConfig.playChannel
    bounties = {}
    for fac in bbData.bountyFactions:
        bounties[fac] = []
    if "bounties" in db:
        for fac in db["bounties"]:
            currentBounties = []
            for bounty in db["bounties"][fac]:
                bounties[fac].append(bounty)
                currentBounties.append(bounty.toDict())
            db["bounties"][fac] = currentBounties
    bbUtil.writeJDB("BBDB.json", db)
    db["bounties"] = bounties
    print(datetime.now().strftime("%H:%M:%S: Data saved!"))


client = discord.Client()
usersDB = loadUsersDB()
guildsDB = loadGuildsDB()
bounties = loadBountiesDB()
BBDB = loadDB(client)
factionColours = {"terran":discord.Colour.gold(), "vossk":discord.Colour.dark_green(), "midorian":discord.Colour.dark_red(), "nivelian":discord.Colour.teal(), "neutral":discord.Colour.purple()}


async def announceNewBounty(client, newBounty):
    bountyEmbed = makeEmbed(titleTxt=criminalNameOrDiscrim(client, newBounty.criminal), desc="⛓ __New Bounty Available__", col=factionColours[newBounty.faction], thumb=newBounty.criminal.icon, footerTxt=newBounty.faction.title())
    bountyEmbed.add_field(name="Reward:", value=str(newBounty.reward) + " Credits")
    bountyEmbed.add_field(name="Possible Systems:", value=len(newBounty.route))
    bountyEmbed.add_field(name="See the culprit's route with:", value="`!bb route " + criminalNameOrDiscrim(client, newBounty.criminal) + "`", inline=False)
    for currentGuild in bbConfig.announceChannel:
        if client.get_channel(bbConfig.announceChannel[str(currentGuild)]) is not None:
            await client.get_channel(bbConfig.announceChannel[str(currentGuild)]).send("A new bounty is now available from **" + newBounty.faction.title() + "** central command:", embed=bountyEmbed)

async def announceBountyWon(bounty, rewards, winningGuild, winningUser):
    for currentGuild in bbConfig.playChannel:
        rewardsEmbed = makeEmbed(titleTxt="Bounty Complete!",authorName=criminalNameOrDiscrim(client, bounty.criminal) + " Arrested",icon=bounty.criminal.icon,col=factionColours[bounty.faction])
        if client.get_channel(bbConfig.playChannel[str(currentGuild)]).guild.get_member(winningUser) is None:
            rewardsEmbed.add_field(name="1. Winner, " + str(rewards[winningUser]["reward"]) + " credits:", value=str(client.get_user(winningUser)) + " checked " + str(int(rewards[winningUser]["checked"])) + " system" + ("s" if int(rewards[winningUser]["checked"]) != 1 else ""), inline=False)
        else:
            rewardsEmbed.add_field(name="1. Winner, " + str(rewards[winningUser]["reward"]) + " credits:", value="<@" + str(winningUser) + "> checked " + str(int(rewards[winningUser]["checked"])) + " system" + ("s" if int(rewards[winningUser]["checked"]) != 1 else ""), inline=False)
        place = 2
        for userID in rewards:
            if not rewards[userID]["won"]:
                if client.get_channel(bbConfig.playChannel[str(currentGuild)]).guild.get_member(userID) is None:
                    rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value=str(client.get_user(userID)) + " checked " + str(int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[userID]["checked"]) != 1 else ""), inline=False)
                else:
                    rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value="<@" + str(userID) + "> checked " + str(int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[userID]["checked"]) != 1 else ""), inline=False)
                place += 1
        if client.get_channel(bbConfig.playChannel[str(currentGuild)]) is not None:
            if int(currentGuild) == winningGuild.id:
                await client.get_channel(bbConfig.playChannel[str(currentGuild)]).send(":trophy: **You win!**\n**" + winningGuild.get_member(winningUser).display_name + "** located and EMP'd **" + bounty.criminal.name + "**, who has been arrested by local security forces. :chains:", embed=rewardsEmbed)
            else:
                await client.get_channel(bbConfig.playChannel[str(currentGuild)]).send(":trophy: Another server has located **" + bounty.criminal.name + "**!", embed=rewardsEmbed)


def makeEmbed(titleTxt="",desc="",col=discord.Colour.blue(), footerTxt="", img="", thumb="", authorName="", icon=""):
    embed = discord.Embed(title=titleTxt, description=desc, colour=col)
    if footerTxt != "": embed.set_footer(text=footerTxt)
    # embed.set_image(url=img)
    if thumb != "": embed.set_thumbnail(url=thumb)
    if icon != "": embed.set_author(name=authorName, icon_url=icon)
    return embed


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
            if canMakeBounty():
                newBounty = bbBounty.Bounty(bountyDB=BBDB)
                BBDB["bounties"][newBounty.faction].append(newBounty) # addBounty implmeneted
                await announceNewBounty(client, newBounty)
            if bbConfig.newBountyDelayType == "random":
                currentNewBountyDelay = random.randint(bbConfig.newBountyDelayMin, bbConfig.newBountyDelayMax)
            else:
                currentNewBountyDelay = newBountyDelayDelta
                if bbConfig.newBountyFixedDeltaChanged:
                    newBountyDelayDelta = timedelta(days=bbConfig.newBountyFixedDelta["days"], hours=bbConfig.newBountyFixedDelta["hours"], minutes=bbConfig.newBountyFixedDelta["minutes"], seconds=bbConfig.newBountyFixedDelta["seconds"])
            currentBountyWait = 0
        # save the database
        if currentSaveWait >= bbConfig.saveDelay:
            saveDB(BBDB)
            currentSaveWait = 0


@client.event
async def on_message(message):
    # The global "client" variable is accessed within this function.

    bbConfig.randomDrinkNum -= 1
    if bbConfig.randomDrinkNum == 0:
        await message.channel.send("!drink")
        bbConfig.randomDrinkNum = random.randint(bbConfig.randomDrinkFactor / 10, bbConfig.randomDrinkFactor)
    
    if message.author == client.user:
        return

    if message.content.split(" ")[0].lower() == ('!bb'):
        msgContent = message.content.replace("‘", "'").replace("’","'")
        if len(msgContent.split(" ")) > 1:
            command = msgContent.split(" ")[1].lower()
        else:
            command = "help"
        if command == 'help':
            helpEmbed = makeEmbed(titleTxt="BountyBot Commands", thumb=client.user.avatar_url_as(size=64))
            for section in bbData.helpDict.keys():
                helpEmbed.add_field(name="‎",value=section, inline=False)
                for currentCommand in bbData.helpDict[section].keys():
                    helpEmbed.add_field(name=currentCommand,value=bbData.helpDict[section][currentCommand], inline=False)
            await message.channel.send(bbData.helpIntro, embed=helpEmbed)
        elif command == "hello":
            await message.channel.send("Greetings, pilot! **o7**")
        elif command == "balance":
            if len(msgContent.split(" ")) < 3:
                if str(message.author.id) not in BBDB["users"]:
                    initializeUser(message.author.id)
                await message.channel.send(":moneybag: **" + message.author.name + "**, you have **" + str(int(BBDB["users"][str(message.author.id)]["credits"])) + " Credits**.")
            else:
                if len(msgContent.split(" ")) > 3 or not (msgContent.split(" ")[2].startswith("<@") and msgContent.split(" ")[2].endswith(">")) or ("!" in msgContent.split(" ")[2] and not bbUtil.isInt(msgContent.split(" ")[2][3:-1])) or ("!" not in msgContent.split(" ")[2] and not bbUtil.isInt(msgContent.split(" ")[2][2:-1])):
                    await message.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                if "!" in msgContent.split(" ")[2]:
                    requestedUser = client.get_user(int(msgContent.split(" ")[2][3:-1]))
                else:
                    requestedUser = client.get_user(int(msgContent.split(" ")[2][2:-1]))
                if str(requestedUser.id) not in BBDB["users"]:
                    initializeUser(requestedUser.id)
                await message.channel.send(":moneybag: **" + requestedUser.name + "** has **" + str(int(BBDB["users"][str(requestedUser.id)]["credits"])) + " Credits**.")
        elif command == "stats":
            if len(msgContent.split(" ")) < 3:
                statsEmbed = makeEmbed(col=factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=message.author.name, footerTxt="Pilot number #" + message.author.discriminator, thumb=message.author.avatar_url_as(size=64))
                if str(message.author.id) not in BBDB["users"]:
                    statsEmbed.add_field(name="Credits balance:",value=0, inline=True)
                    statsEmbed.add_field(name="Lifetime total credits earned:", value=0, inline=True)
                    statsEmbed.add_field(name="‎",value="‎", inline=False)
                    statsEmbed.add_field(name="Total systems checked:",value=0, inline=True)
                    statsEmbed.add_field(name="Total bounties won:", value=0, inline=True)
                else:
                    statsEmbed.add_field(name="Credits balance:",value=str(int(BBDB["users"][str(message.author.id)]["credits"])), inline=True)
                    statsEmbed.add_field(name="Lifetime total credits earned:", value=str(int(BBDB["users"][str(message.author.id)]["lifetimeCredits"])), inline=True)
                    statsEmbed.add_field(name="‎",value="‎", inline=False)
                    statsEmbed.add_field(name="Total systems checked:",value=str(BBDB["users"][str(message.author.id)]["systemsChecked"]), inline=True)
                    statsEmbed.add_field(name="Total bounties won:", value=str(BBDB["users"][str(message.author.id)]["wins"]), inline=True)
                await message.channel.send(embed=statsEmbed)
                return
            else:
                if len(msgContent.split(" ")) > 3 or not (msgContent.split(" ")[2].startswith("<@") and msgContent.split(" ")[2].endswith(">")) or ("!" in msgContent.split(" ")[2] and not bbUtil.isInt(msgContent.split(" ")[2][3:-1])) or ("!" not in msgContent.split(" ")[2] and not bbUtil.isInt(msgContent.split(" ")[2][2:-1])):
                    await message.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                requestedUser = client.get_user(int(msgContent.split(" ")[2][3:-1]))
                if requestedUser is None:
                    await message.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                userID = str(requestedUser.id)
                statsEmbed = makeEmbed(col=factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=requestedUser.name, footerTxt="Pilot number #" + requestedUser.discriminator, thumb=requestedUser.avatar_url_as(size=64))
                if userID not in BBDB["users"]:
                    statsEmbed.add_field(name="Credits balance:",value=0, inline=True)
                    statsEmbed.add_field(name="Lifetime total credits earned:", value=0, inline=True)
                    statsEmbed.add_field(name="‎",value="‎", inline=False)
                    statsEmbed.add_field(name="Total systems checked:",value=0, inline=True)
                    statsEmbed.add_field(name="Total bounties won:", value=0, inline=True)
                else:
                    statsEmbed.add_field(name="Credits balance:",value=str(int(BBDB["users"][str(requestedUser.id)]["credits"])), inline=True)
                    statsEmbed.add_field(name="Lifetime total credits earned:", value=str(int(BBDB["users"][str(requestedUser.id)]["lifetimeCredits"])), inline=True)
                    statsEmbed.add_field(name="‎",value="‎", inline=False)
                    statsEmbed.add_field(name="Total systems checked:",value=str(BBDB["users"][str(requestedUser.id)]["systemsChecked"]), inline=True)
                    statsEmbed.add_field(name="Total bounties won:", value=str(BBDB["users"][str(requestedUser.id)]["wins"]), inline=True)
                await message.channel.send(embed=statsEmbed)
        elif command == "map":
            if len(msgContent.split(" ")) > 2 and msgContent.split(" ")[2] == "-g":
                await message.channel.send(bbData.mapImageWithGraphLink)
            else:
                await message.channel.send(bbData.mapImageNoGraphLink)
        elif command == "check":
            if len(msgContent.split(" ")) < 3:
                await message.channel.send(":x: Please provide a system to check! E.g: `!bb check Pescal Inartu`")
                return
            requestedSystem = msgContent[10:].title()
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

            if str(message.author.id) not in BBDB["users"]:
                initializeUser(message.author.id)
            if datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) < datetime.utcnow():
                bountyWon = False
                for fac in BBDB["bounties"]:
                    toPop = []
                    for bountyIndex in range(len(BBDB["bounties"][fac])):
                        if BBDB["bounties"][fac][bountyIndex].check(requestedSystem, message.author.id) == 3:
                            bountyWon = True
                            bounty = BBDB["bounties"][fac][bountyIndex]
                            rewards = bounty.calcRewards()
                            for userID in rewards:
                                BBDB["users"][str(userID)]["credits"] += rewards[userID]["reward"]
                                BBDB["users"][str(userID)]["lifetimeCredits"] += rewards[userID]["reward"]
                            toPop += [bountyIndex]
                            await announceBountyWon(bounty, rewards, message.guild, message.author.id)
                    for bountyIndex in toPop:
                        BBDB["bounties"][fac].pop(bountyIndex)
                if bountyWon:
                    BBDB["users"][str(message.author.id)]["wins"] += 1
                    await message.channel.send(":moneybag: **" + message.author.name + "**, you now have **" + str(int(BBDB["users"][str(message.author.id)]["credits"])) + " Credits!**")
                else:
                    outmsg = ":telescope: **" + message.author.name + "**, you did not find any criminals!"
                    for fac in BBDB["bounties"]:
                        for bounty in BBDB["bounties"][fac]:
                            if requestedSystem in bounty.route:
                                if 0 < bounty.route.index(bounty.answer) - bounty.route.index(requestedSystem) < 4:
                                    outmsg += "\n       • Local security forces spotted **" + criminalNameOrDiscrim(client, bounty.criminal) + "** here recently. "
                    await message.channel.send(outmsg)

                BBDB["users"][str(message.author.id)]["systemsChecked"] += 1
                BBDB["users"][str(message.author.id)]["bountyCooldownEnd"] = (datetime.utcnow() + timedelta(minutes=bbConfig.checkCooldown["minutes"])).timestamp()
            else:
                diff = datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) - datetime.utcnow()
                minutes = int(diff.total_seconds() / 60)
                seconds = int(diff.total_seconds() % 60)
                await message.channel.send(":stopwatch: **" + message.author.name + "**, your *Khador drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")
        elif command == "bounties":
            if len(msgContent.split(" ")) == 2:
                outmessage = "__**Active Bounties**__\nTimes given in UTC. See more detailed information with `!bb bounties <faction>`\n```css"
                preLen = len(outmessage)
                for fac in BBDB["bounties"]:
                    if len(BBDB["bounties"][fac]) != 0:
                        outmessage += "\n • [" + fac.title() + "]: "
                        for bounty in BBDB["bounties"][fac]:
                            outmessage += criminalNameOrDiscrim(client, bounty.criminal) + ", "
                        outmessage = outmessage[:-2]
                if len(outmessage) == preLen:
                    outmessage += "\n[  No currently active bounties! Please check back later.  ]"
                await message.channel.send(outmessage + "```")
                return
            requestedFaction = msgContent[13:].lower()
            if requestedFaction not in bbData.bountyFactions:
                if len(requestedFaction) < 20:
                    await message.channel.send(":x: Unrecognised faction: **" + requestedFaction + "**")
                else:
                    await message.channel.send(":x: Unrecognised faction **" + requestedFaction[0:15] + "**...")
                return
            if len(BBDB["bounties"][requestedFaction]) == 0:
                await message.channel.send(":stopwatch: There are no **" + requestedFaction.title() + "** bounties active currently!")
            else:
                outmessage = "__**Active " + requestedFaction.title() + " Bounties**__\nTimes given in UTC.```css"
                for bounty in BBDB["bounties"][requestedFaction]:
                    endTimeStr = datetime.utcfromtimestamp(bounty.endTime).strftime("%B %d %H %M %S").split(" ")
                    try:
                        outmessage += "\n • [" + criminalNameOrDiscrim(client, bounty.criminal) + "]" + " " * (bbData.longestBountyNameLength + 1 - len(criminalNameOrDiscrim(client, bounty.criminal))) + ": " + str(int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + bbData.numExtensions[int(endTimeStr[1][-1])] + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                    except Exception:
                        print("ERROR ON:",endTimeStr)
                        print("0:",endTimeStr[0])
                        print("1:",endTimeStr[1])
                        print("1,-1:",endTimeStr[1][-1])
                        print("2:",endTimeStr[2])
                        print("3:",endTimeStr[3])
                        outmessage += "\n • [" + criminalNameOrDiscrim(client, bounty.criminal) + "]" + " " * (bbData.longestBountyNameLength + 1 - len(criminalNameOrDiscrim(client, bounty.criminal))) + ": " + str(int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + bbData.numExtensions[int(endTimeStr[1][-1])] + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                    if endTimeStr[4] != "00":
                        outmessage += ":" + endTimeStr[4]
                    else:
                        outmessage += "   "
                    outmessage += " - " + str(len(bounty.route)) + " possible system"
                    if len(bounty.route) != 1:
                        outmessage += "s"
                await message.channel.send(outmessage + "```\nTrack down criminals and **win credits** using `!bb route` and `!bb check`!")
        elif command == "route":
            if len(msgContent.split(" ")) < 3:
                await message.channel.send(":x: Please provide the criminal name! E.g: `!bb route Kehnor`")
                return
            requestedBountyName = msgContent[10:]
            for fac in BBDB["bounties"]:
                for bounty in BBDB["bounties"][fac]:
                    if bounty.criminal.isCalled(requestedBountyName.lower()):
                        outmessage = "**" + criminalNameOrDiscrim(client, bounty.criminal) + "**'s current route:\n> "
                        for system in bounty.route:
                            outmessage += " " + ("~~" if bounty.checked[system] != -1 else "") + system + ("~~" if bounty.checked[system] != -1 else "") + ","
                        outmessage = outmessage[:-1] + ". :rocket:"
                        await message.channel.send(outmessage)
                        return
            outmsg = ":x: That pilot isn't on any bounty boards! :clipboard:"
            if requestedBountyName.startswith("<@"):
                outmsg += "\n:warning: **Don't tag users**, use their name and ID number like so: `!bb route Trimatix#2244`"
            await message.channel.send(outmsg)

        elif command == "make-route":
            if len(msgContent.split(" ")) <= 3 or "," not in msgContent or len(msgContent[10:msgContent.index(",")]) < 1 or len(msgContent[msgContent.index(","):]) < 2:
                await message.channel.send(":x: Please provide source and destination systems, separated with a comma and space.\nFor example: `!bb make-route Pescal Inartu, Loma`")
                return
            if msgContent.count(",") > 1:
                await message.channel.send(":x: Please only provide **two** systems!")
                return
            startSyst = msgContent[15:].split(",")[0].title()
            endSyst = msgContent[15:].split(",")[1][1:].title()
            for criminalName in [startSyst, endSyst]:
                if criminalName not in bbData.builtInSystemObjs:
                    if len(criminalName) < 20:
                        await message.channel.send(":x: The **" + criminalName + "** system is not on my star map! :map:")
                    else:
                        await message.channel.send(":x: The **" + criminalName[0:15] + "**... system is not on my star map! :map:")
                    return
                if not bbData.builtInSystemObjs[criminalName].hasJumpGate():
                    if len(criminalName) < 20:
                        await message.channel.send(":x: The **" + criminalName + "** system does not have a jump gate! :rocket:")
                    else:
                        await message.channel.send(":x: The **" + criminalName[0:15] + "**... system does not have a jump gate! :rocket:")
                    return
            routeStr = ""
            for currentSyst in bbUtil.bbAStar(startSyst, endSyst, bbData.builtInSystemObjs):
                routeStr += currentSyst + ", "
            if routeStr.startswith("#"):
                await message.channel.send(":x: ERR: Processing took too long! :stopwatch:")
            elif routeStr.startswith("!"):
                await message.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
            elif startSyst == endSyst:
                await message.channel.send(":thinking: You're already there, pilot!")
            else:
                await message.channel.send("Here's the shortest route from **" + startSyst + "** to **" + endSyst + "**:\n> " + routeStr[:-2] + " :rocket:")
        elif command == "system":
            if len(msgContent.split(" ")) < 3:
                await message.channel.send(":x: Please provide a system! Example: `!bb system Augmenta`")
                return
            systArg = msgContent[11:].title()
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
                
                statsEmbed = makeEmbed(col=factionColours[systObj.faction], desc="__System Information__", titleTxt=systObj.name, footerTxt=systObj.faction.title(), thumb=factionIcons[systObj.faction])
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
        elif command == "criminal":
            if len(msgContent.split(" ")) < 3:
                await message.channel.send(":x: Please provide a criminal! Example: `!bb criminal Toma Prakupy`")
                return
            criminalName = msgContent[13:].title()
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
                statsEmbed = makeEmbed(col=factionColours[criminalObj.faction], desc="__Criminal File__", titleTxt=criminalObj.name, thumb=criminalObj.icon)
                statsEmbed.add_field(name="Wanted By:",value=criminalObj.faction.title() + "s")
                if len(criminalObj.aliases) > 1:
                    aliasStr = ""
                    for alias in criminalObj.aliases:
                        aliasStr += alias + ", "
                    statsEmbed.add_field(name="Aliases:", value=aliasStr[:-2], inline=False)
                if criminalObj.hasWiki:
                    statsEmbed.add_field(name="‎", value="[Wiki](" + criminalObj.wiki + ")", inline=False)
                await message.channel.send(embed=statsEmbed)
        elif command == "leaderboard":
            globalBoard = False
            stat = "lifetimeCredits"
            boardScope = message.guild.name
            boardTitle = "Total Credits Earned"
            boardUnit = "Credit"
            boardUnits = "Credits"

            if len(msgContent.split(" ")) > 2:
                args = msgContent.split(" ")[2].lower()
                if not args.startswith("-"):
                    await message.channel.send(":x: Please prefix your arguments with a dash! E.g: `!bb leaderboard -gc`")
                    return
                args = args[1:]
                if ("g" not in args and len(args) > 2) or ("g" in args and len(args) > 3):
                    await message.channel.send(":x: Too many arguments! Please only specify one leaderboard. E.g: `!bb leaderboard -gc`")
                    return
                for arg in args:
                    if arg not in "gcsw":
                        await message.channel.send(":x: Unknown argument: '**" + arg + "**'. Please refer to `!bb help leaderboard`")
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
                    stat = "wins"
                    boardTitle = "Bounties Won"
                    boardUnit = "Bounty"
                    boardUnits = "Bounties"

            inputDict = {}
            for userID in BBDB["users"]:
                if (globalBoard and client.get_user(int(userID)) is not None) or (not globalBoard and message.guild.get_member(int(userID)) is not None):
                    inputDict[userID] = BBDB["users"][userID][stat]
            sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]

            leaderboardEmbed = makeEmbed(titleTxt=boardTitle, authorName=boardScope, icon=bbData.winIcon, col = factionColours["neutral"])

            externalUser = False
            first = True
            for place in range(min(len(sortedUsers), 10)):
                if globalBoard and message.guild.get_member(int(sortedUsers[place][0])) is None:
                    leaderboardEmbed.add_field(value="*" + str(place + 1) + ". " + client.get_user(int(sortedUsers[place][0])).mention, name=("⭐ " if first else "") + str(int(sortedUsers[place][1])) + " " + (boardUnit if int(sortedUsers[place][1]) == 1 else boardUnits), inline=False)
                    externalUser = True
                    if first: first = False
                else:
                    leaderboardEmbed.add_field(value=str(place + 1) + ". " + message.guild.get_member(int(sortedUsers[place][0])).mention, name=("⭐ " if first else "") + str(int(sortedUsers[place][1])) + " " + (boardUnit if int(sortedUsers[place][1]) == 1 else boardUnits), inline=False)
                    if first: first = False
            if externalUser:
                leaderboardEmbed.set_footer(text="An `*` indicates a user that is from another server.")
            await message.channel.send(embed=leaderboardEmbed)
        else:
            if message.author.id == 188618589102669826 or message.author.permissions_in(message.channel).administrator:
                if command == "set-announce-channel":
                    bbConfig.announceChannel[str(message.guild.id)] = message.channel.id
                    await message.channel.send(":ballot_box_with_check: Announcements channel set!")
                elif command == "set-play-channel":
                    bbConfig.playChannel[str(message.guild.id)] = message.channel.id
                    await message.channel.send(":ballot_box_with_check: Bounty play channel set!")
                elif command == "admin-help":
                    helpEmbed = makeEmbed(titleTxt="BB Administrator Commands", thumb=client.user.avatar_url_as(size=64))
                    for section in bbData.adminHelpDict.keys():
                        helpEmbed.add_field(name="‎",value=section, inline=False)
                        for currentCommand in bbData.adminHelpDict[section].keys():
                            helpEmbed.add_field(name=currentCommand,value=bbData.adminHelpDict[section][currentCommand], inline=False)
                    await message.channel.send(bbData.adminHelpIntro, embed=helpEmbed)
                elif message.author.id == 188618589102669826:
                    if command == "sleep":
                        await message.channel.send("zzzz....")
                        bbConfig.botLoggedIn = False
                        await client.logout()
                        saveDB(BBDB)
                    elif command == "save":
                        saveDB(BBDB)
                        await message.channel.send("saved!")
                    elif command == "anchset?":
                        await message.channel.send(str(message.guild.id) in bbConfig.announceChannel)
                    elif command == "printanch":
                        await message.channel.send(bbConfig.announceChannel[str(message.guild.id)])
                    elif command == "plchset?":
                        await message.channel.send(str(message.guild.id) in bbConfig.playChannel)
                    elif command == "printplch":
                        await message.channel.send(bbConfig.playChannel[str(message.guild.id)])
                    elif command == "stations":
                        await message.channel.send(bbData.builtInSystemObjs)
                    elif command == "clear":
                        for fac in bbData.bountyFactions:
                            BBDB["bounties"][fac] = []
                        await message.channel.send(":ballot_box_with_check: Active bounties cleared!")
                    elif command == "cooldown":
                        diff = datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) - datetime.utcnow()
                        minutes = int(diff.total_seconds() / 60)
                        seconds = int(diff.total_seconds() % 60)
                        await message.channel.send(str(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) + " = " + str(minutes) + "m, " + str(seconds) + "s.")
                        await message.channel.send(datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]).strftime("%Hh%Mm%Ss"))
                        await message.channel.send(datetime.utcnow().strftime("%Hh%Mm%Ss"))
                    elif command == "resetcool":
                        if len(msgContent.split(" ")) < 3:
                            BBDB["users"][str(message.author.id)]["bountyCooldownEnd"] = datetime.utcnow().timestamp()
                        else:
                            if "!" in msgContent.split(" ")[2]:
                                requestedUser = client.get_user(int(msgContent[17:-1]))
                            else:
                                requestedUser = client.get_user(int(msgContent[16:-1]))
                            BBDB["users"][str(requestedUser.id)]["bountyCooldownEnd"] = datetime.utcnow().timestamp()
                        await message.channel.send("Done!")
                    elif command == "setCheckCooldown":
                        if len(msgContent.split(" ")) != 3:
                            await message.channel.send(":x: please give the number of minutes!")
                            return
                        if not bbUtil.isInt(msgContent.split(" ")[2]):
                            await message.channel.send(":x: that's not a number!")
                            return
                        bbConfig.checkCooldown["minutes"] = int(msgContent.split(" ")[2])
                        await message.channel.send("Done! *you still need to update the file though* <@188618589102669826>")
                    elif command == "setBountyPeriodM":
                        if len(msgContent.split(" ")) != 3:
                            await message.channel.send(":x: please give the number of minutes!")
                            return
                        if not bbUtil.isInt(msgContent.split(" ")[2]):
                            await message.channel.send(":x: that's not a number!")
                            return
                        bbConfig.newBountyFixedDelta["minutes"] = int(msgContent.split(" ")[2])
                        bbConfig.newBountyFixedDeltaChanged = True
                        await message.channel.send("Done! *you still need to update the file though* <@188618589102669826>")
                    elif command == "setBountyPeriodH":
                        if len(msgContent.split(" ")) != 3:
                            await message.channel.send(":x: please give the number of minutes!")
                            return
                        if not bbUtil.isInt(msgContent.split(" ")[2]):
                            await message.channel.send(":x: that's not a number!")
                            return
                        bbConfig.newBountyFixedDeltaChanged = True
                        bbConfig.newBountyFixedDelta["hours"] = int(msgContent.split(" ")[2])
                        await message.channel.send("Done! *you still need to update the file though* <@188618589102669826>")
                    elif command == "resetNewBountyCool":
                        bbConfig.newBountyDelayReset = True
                        await message.channel.send(":ballot_box_with_check: New bounty cooldown reset!")
                    elif command == "make-bounty":
                        if len(msgContent.split(" ")) < 3:
                            newBounty = bbBounty.Bounty(bountyDB=BBDB)
                        elif len(msgContent[16:].split("+")) == 1:
                            newFaction = msgContent[16:]
                            newBounty = bbBounty.Bounty(bountyDB=BBDB, config=bbBountyConfig.BountyConfig(faction=newFaction))
                        elif len(msgContent[16:].split("+")) == 9:
                            bData = msgContent[16:].split("+")
                            newFaction = bData[0].rstrip(" ")
                            if newFaction == "auto":
                                newFaction = ""
                            newName = bData[1].rstrip(" ").title()
                            if newName == "Auto":
                                newName = ""
                            else:
                                nameFound = False
                                for fac in BBDB["bounties"]:
                                    if bountyObjExists(newName, BBDB["bounties"][fac]):
                                        nameFound = True
                                        break
                                if nameFound:
                                    await message.channel.send(":x: That pilot is already on the " + fac.title() + " bounty board!")
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
                                newIcon = ""
                            newBounty = bbBounty.Bounty(bountyDB=BBDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon))
                        BBDB["bounties"][newBounty.faction].append(newBounty)
                        await announceNewBounty(client, newBounty)
                    elif command == "make-player-bounty":
                        if len(msgContent.split(" ")) < 4:
                            requestedID = int(msgContent.split(" ")[2].lstrip("<@!").rstrip(">"))
                            if not bbUtil.isInt(requestedID) or (client.get_user(int(requestedID))) is None:
                                await message.channel.send(":x: Player not found!")
                                return
                            newBounty = bbBounty.Bounty(bountyDB=BBDB, config=bbBountyConfig.BountyConfig(name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(client.get_user(requestedID).avatar_url_as(size=64))))
                        elif len(msgContent[23:].split("+")) == 1:
                            newFaction = msgContent[23:]
                            newBounty = bbBounty.Bounty(bountyDB=BBDB, config=bbBountyConfig.BountyConfig(faction=newFaction))
                        elif len(msgContent[23:].split("+")) == 9:
                            bData = msgContent[23:].split("+")
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
                            newBounty = bbBounty.Bounty(bountyDB=BBDB, config=bbBountyConfig.BountyConfig(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=True, icon=newIcon))
                        BBDB["bounties"][newBounty.faction].append(newBounty)
                        await announceNewBounty(client, newBounty)
                    else:
                        await message.channel.send(""":question: Can't do that, commander. Type `!bb help` for a list of commands! **o7**""")
                else:
                    await message.channel.send(""":question: Can't do that, commander. Type `!bb help` for a list of commands! **o7**""")
            else:
                await message.channel.send(""":question: Can't do that, pilot. Type `!bb help` for a list of commands! **o7**""")
        
client.run(bbPRIVATE.botToken)
