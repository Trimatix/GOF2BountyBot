import discord
from datetime import datetime, timedelta
import asyncio
import random
import operator
import bbdata
import bbutil
import bbPRIVATE
import bbconfig


def initializeUser(userID):
    BBDB["users"][str(userID)] = {"credits":0, "bountyCooldownEnd":0, "totalCredits":0, "systemsChecked":0, "wins":0}


def makeRoute(start, end):
    return bbutil.bbAStar(start, end, bbdata.systems)


def bountyObjExists(name, factionBounties):
    for bounty in factionBounties:
        if bounty.name == name:
            return True
    return False

def bountyDictExists(name, factionBounties):
    for bounty in factionBounties:
        if bounty["name"] == name:
            return True
    return False


class Bounty:
    issueTime = -1
    name = ""
    route = []
    reward = 0.0
    endTime = -1
    faction = ""
    checked = {}
    answer = ""
    icon = ""
    

    def __init__(self, BBDB=None, faction="", name="", isPlayer=None, route=[], start="", end="", answer="", checked={}, reward=-1.0, issueTime=-1.0, endTime=-1.0, icon="", client=None):
        self.faction = faction.lower()
        self.name = name
        self.isPlayer = False if isPlayer is None else isPlayer
        self.route = route
        for i in range(len(route)):
            route[i] = route[i].title()
        start = start.title()
        end = end.title()
        self.answer = answer.title()
        self.checked = checked
        self.reward = reward
        self.issueTime = issueTime
        self.endTime = endTime
        self.icon = icon
        if isPlayer and client is None:
            raise RuntimeError("Bounty constructor: Attempted to make player bounty but didn't provide client '" + name + "'")
        self.client = client

        if self.faction == "":
            self.faction = random.choice(bbdata.bountyFactions)
        elif self.faction not in bbdata.bountyFactions:
            raise RuntimeError("Bounty constructor: Invalid faction requested '" + faction + "'")
    
        if self.route == []:
            if start == "":
                start = random.choice(list(bbdata.systems.keys()))
                while start == end or not bbdata.systems[start].hasJumpGate():
                    start = random.choice(list(bbdata.systems.keys()))
            elif start not in bbdata.systems:
                raise RuntimeError("Bounty constructor: Invalid start requested '" + start + "'")
            if end == "":
                end = random.choice(list(bbdata.systems.keys()))
                while start == end or not bbdata.systems[end].hasJumpGate():
                    end = random.choice(list(bbdata.systems.keys()))
            elif end not in bbdata.systems:
                raise RuntimeError("Bounty constructor: Invalid end requested '" + end + "'")
            self.route = makeRoute(start, end)
        else:
            for system in self.route:
                if system not in bbdata.systems:
                    raise RuntimeError("Bounty constructor: Invalid system in route '" + system + "'")
        if self.answer == "":
            self.answer = random.choice(self.route)
        elif self.answer not in bbdata.systems:
            raise RuntimeError("Bounty constructor: Invalid answer requested '" + answer + "'")
        if self.name == "":
            self.name = random.choice(bbdata.bountyNames[self.faction])
            if BBDB is not None:
                while bountyObjExists(self.name, BBDB["bounties"][self.faction]):
                    self.name = random.choice(bbdata.bountyNames[self.faction])
        elif BBDB is not None:
            for fac in BBDB["bounties"]:
                if bountyObjExists(self.name, BBDB["bounties"][fac]):
                    raise RuntimeError("Bounty constructor: attempted to create a bounty with a pre-existing name: " + self.name)
        if self.icon == "":
            if self.name in bbdata.bountyNames[self.faction]:
                self.icon = bbdata.bountyIcons[self.name]
            else:
                self.icon = bbdata.rocketIcon
        if self.reward == -1.0:
            self.reward = len(self.route) * bbconfig.bPointsToCreditsRatio
        elif self.reward < 0:
            raise RuntimeError("Bounty constructor: Invalid reward requested '" + str(reward) + "'")
        if self.issueTime == -1.0:
            self.issueTime = datetime.utcnow().replace(second=0).timestamp()
        if self.endTime == -1.0:
            self.endTime = (datetime.utcfromtimestamp(self.issueTime) + timedelta(days=len(self.route))).timestamp()

        for station in self.route:
            if station not in self.checked or checked == {}:
                self.checked[station] = -1

    # return 0 => system not in route
    # return 1 => system already checked
    # return 2 => system was unchecked, but is not the answer
    # return 3 => win!
    def check(self, system, userID):
        if system not in self.route:
            return 0
        elif self.systemChecked(system):
            return 1
        else:
            self.checked[system] = userID
            if self.answer == system:
                return 3
            return 2

    def systemChecked(self, system):
        return self.checked[system] != -1

    def calcRewards(self):
        rewards = {}
        checkedSystems = 0
        for system in self.route:
            if self.systemChecked(system):
                checkedSystems += 1
                rewards[self.checked[system]] = {"reward":0,"checked":0,"won":False}

        uncheckedSystems = len(self.route) - checkedSystems

        for system in self.route:
            if self.systemChecked(system):
                if self.answer == system:
                    rewards[self.checked[system]]["reward"] += (self.reward / len(self.route)) * (uncheckedSystems + 1)
                    rewards[self.checked[system]]["checked"] += 1
                    rewards[self.checked[system]]["won"] = True
                else:
                    rewards[self.checked[system]]["reward"] += self.reward / len(self.route)
                    rewards[self.checked[system]]["checked"] += 1
        return rewards

    def toDict(self):
        return {"faction": self.faction, "name": self.name, "route": self.route, "answer": self.answer, "checked": self.checked, "reward": self.reward, "issueTime": self.issueTime, "endTime": self.endTime, "isPlayer": self.isPlayer, "icon": self.icon}

    def getCodeNameTag(self): 
        if not self.isPlayer:
            return self.name
        userID = int(self.name.lstrip("<@!").rstrip(">"))
        if self.client.get_user(userID) is not None:
            return str(self.client.get_user(userID))
        return self.name


def bountyNameExists(bountiesList, nameToFind):
    for bounty in bountiesList:
        if bounty["name"] == nameToFind:
            return True
    return False


def canMakeBounty():
    for fac in bbdata.bountyFactions:
        if len(BBDB["bounties"][fac]) < bbconfig.maxBountiesPerFaction:
            return True
    return False


def loadDB(DCClient):
    db = bbutil.readJDB("BBDB.json")
    if "announceChannel" in db:
        bbconfig.announceChannel = db["announceChannel"]
    if "playChannel" in db:
        bbconfig.playChannel = db["playChannel"]
    if "bounties" in db:
        for fac in db["bounties"]:
            currentBounties = []
            for bounty in db["bounties"][fac]:
                currentBounties.append(Bounty(faction=bounty["faction"], name=bounty["name"], route=bounty["route"], answer=bounty["answer"], checked=bounty["checked"], reward=bounty["reward"], issueTime=bounty["issueTime"], endTime=bounty["endTime"], isPlayer=bounty["isPlayer"], icon=bounty["icon"], client=(DCClient if bounty["isPlayer"] else None)))
            db["bounties"][fac] = currentBounties
    return db


def saveDB(db):
    BBDB["announceChannel"] = bbconfig.announceChannel
    BBDB["playChannel"] = bbconfig.playChannel
    bounties = {}
    for fac in bbdata.bountyFactions:
        bounties[fac] = []
    if "bounties" in db:
        for fac in db["bounties"]:
            currentBounties = []
            for bounty in db["bounties"][fac]:
                bounties[fac].append(bounty)
                currentBounties.append(bounty.toDict())
            db["bounties"][fac] = currentBounties
    bbutil.writeJDB("BBDB.json", db)
    db["bounties"] = bounties
    print(datetime.now().strftime("%H:%M:%S: Data saved!"))


client = discord.Client()

BBDB = loadDB(client)
factionColours = {"terran":discord.Colour.gold(), "vossk":discord.Colour.dark_green(), "midorian":discord.Colour.dark_red(), "nivelian":discord.Colour.teal(), "neutral":discord.Colour.purple()}
factionIcons = {"terran":bbdata.terranIcon, "vossk":bbdata.vosskIcon, "midorian":bbdata.midorianIcon, "nivelian":bbdata.nivelianIcon, "neutral":bbdata.neutralIcon}


def isInt(x):
    try:
        int(x)
    except TypeError:
        return False
    except ValueError:
        return False
    return True


async def announceNewBounty(newBounty):
    bountyEmbed = makeEmbed(titleTxt=newBounty.getCodeNameTag(), desc="⛓ __New Bounty Available__", col=factionColours[newBounty.faction], thumb=newBounty.icon, footerTxt=newBounty.faction.title())
    bountyEmbed.add_field(name="Reward:", value=str(newBounty.reward) + " Credits")
    bountyEmbed.add_field(name="Possible Systems:", value=len(newBounty.route))
    bountyEmbed.add_field(name="See the culprit's route with:", value="`!bb route " + newBounty.getCodeNameTag() + "`", inline=False)
    for currentGuild in bbconfig.announceChannel:
        if client.get_channel(bbconfig.announceChannel[str(currentGuild)]) is not None:
            await client.get_channel(bbconfig.announceChannel[str(currentGuild)]).send("A new bounty is now available from **" + newBounty.faction.title() + "** central command:", embed=bountyEmbed)

async def announceBountyWon(bounty, rewards, winningGuild, winningUser):
    rewardsEmbed = makeEmbed(titleTxt="Bounty Complete!",authorName=bounty.getCodeNameTag() + " Arrested",icon=bounty.icon,col=factionColours[bounty.faction])
    rewardsEmbed.add_field(name="1. Winner, " + str(rewards[winningUser]["reward"]) + " credits:", value="<@" + str(winningUser) + "> checked " + str(int(rewards[winningUser]["checked"])) + " system" + ("s" if int(rewards[winningUser]["checked"]) != 1 else ""), inline=False)
    place = 2
    for userID in rewards:
        if not rewards[userID]["won"]:
            rewardsEmbed.add_field(name=str(place) + ". " + str(rewards[userID]["reward"]) + " credits:", value="<@" + str(userID) + "> checked " + str(int(rewards[userID]["checked"])) + " system" + ("s" if int(rewards[winningUser]["checked"]) != 1 else ""), inline=False)
            place += 1
    for currentGuild in bbconfig.playChannel:
        if client.get_channel(bbconfig.playChannel[str(currentGuild)]) is not None:
            if int(currentGuild) == winningGuild.id:
                await client.get_channel(bbconfig.playChannel[str(currentGuild)]).send(":trophy: **You win!**\n**" + winningGuild.get_member(winningUser).display_name + "** located and EMP'd **" + bounty.name + "**, who has been arrested by local security forces. :chains:", embed=rewardsEmbed)
            else:
                await client.get_channel(bbconfig.playChannel[str(currentGuild)]).send(":trophy: Another server has located **" + bounty.name + "**!", embed=rewardsEmbed)


def makeEmbed(titleTxt="",desc="",col=discord.Colour.blue(), footerTxt="", img="", thumb="", authorName="", icon=""):
    embed = discord.Embed(title=titleTxt, description=desc, colour=col)
    if footerTxt != "": embed.set_footer(text=footerTxt)
    # embed.set_image(url=img)
    if thumb != "": embed.set_thumbnail(url=thumb)
    if icon != "": embed.set_author(name=authorName, icon_url=icon)
    return embed


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    bbconfig.botLoggedIn = True
    currentBountyWait = 0
    currentSaveWait = 0
    newBountyDelayDelta = None
    newBountyFixedDailyTime = None
    if bbconfig.newBountyDelayType == "random":
        currentNewBountyDelay = random.randint(bbconfig.newBountyDelayMin, bbconfig.newBountyDelayMax)
    elif bbconfig.newBountyDelayType == "fixed":
        currentNewBountyDelay = 0
        newBountyDelayDelta = timedelta(days=bbconfig.newBountyFixedDelta["days"], hours=bbconfig.newBountyFixedDelta["hours"], minutes=bbconfig.newBountyFixedDelta["minutes"], seconds=bbconfig.newBountyFixedDelta["seconds"])
        if bbconfig.newBountyFixedUseDailyTime:
            newBountyFixedDailyTime = timedelta(hours=bbconfig.newBountyFixedDailyTime["hours"], minutes=bbconfig.newBountyFixedDailyTime["minutes"], seconds=bbconfig.newBountyFixedDailyTime["seconds"])
    while bbconfig.botLoggedIn:
        await asyncio.sleep(bbconfig.delayFactor)
        currentBountyWait += bbconfig.delayFactor
        currentSaveWait += bbconfig.delayFactor
        # Make new bounties
        if bbconfig.newBountyDelayReset or (bbconfig.newBountyDelayType == "random" and currentBountyWait >= currentNewBountyDelay) or \
                (bbconfig.newBountyDelayType == "fixed" and timedelta(seconds=currentBountyWait) >= newBountyDelayDelta and ((not bbconfig.newBountyFixedUseDailyTime) or (bbconfig.newBountyFixedUseDailyTime and \
                    datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta - timedelta(minutes=bbconfig.delayFactor) \
                    <= datetime.utcnow() \
                    <= datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta + timedelta(minutes=bbconfig.delayFactor)))):
            if canMakeBounty():
                newBounty = Bounty(BBDB=BBDB)
                BBDB["bounties"][newBounty.faction].append(newBounty)
                await announceNewBounty(newBounty)
            if bbconfig.newBountyDelayType == "random":
                currentNewBountyDelay = random.randint(bbconfig.newBountyDelayMin, bbconfig.newBountyDelayMax)
            else:
                currentNewBountyDelay = newBountyDelayDelta
                if bbconfig.newBountyFixedDeltaChanged:
                    newBountyDelayDelta = timedelta(days=bbconfig.newBountyFixedDelta["days"], hours=bbconfig.newBountyFixedDelta["hours"], minutes=bbconfig.newBountyFixedDelta["minutes"], seconds=bbconfig.newBountyFixedDelta["seconds"])
            currentBountyWait = 0
        # save the database
        if currentSaveWait >= bbconfig.saveDelay:
            saveDB(BBDB)
            currentSaveWait = 0


@client.event
async def on_message(message):
    bbconfig.randomDrinkNum -= 1
    if bbconfig.randomDrinkNum == 0:
        await message.channel.send("!drink")
        bbconfig.randomDrinkNum = random.randint(bbconfig.randomDrinkFactor / 10, bbconfig.randomDrinkFactor)
    
    if message.author == client.user:
        return

    if message.content.split(" ")[0].lower() == ('!bb'):
        msg = message.replace("‘", "'")
        if len(msg.content.split(" ")) > 1:
            command = msg.content.split(" ")[1].lower()
        else:
            command = "help"
        if command == 'help':
            helpEmbed = makeEmbed(titleTxt="BountyBot Commands", thumb=client.user.avatar_url_as(size=64))
            for section in bbdata.helpDict.keys():
                helpEmbed.add_field(name="‎",value=section, inline=False)
                for currentCommand in bbdata.helpDict[section].keys():
                    helpEmbed.add_field(name=currentCommand,value=bbdata.helpDict[section][currentCommand], inline=False)
            await msg.channel.send(bbdata.helpIntro, embed=helpEmbed)
        elif command == "hello":
            await msg.channel.send("Greetings, pilot! **o7**")
        elif command == "balance":
            if len(msg.content.split(" ")) < 3:
                if str(msg.author.id) not in BBDB["users"]:
                    initializeUser(msg.author.id)
                await msg.channel.send(":moneybag: **" + msg.author.name + "**, you have **" + str(int(BBDB["users"][str(msg.author.id)]["credits"])) + " Credits**.")
            else:
                if len(msg.content.split(" ")) > 3 or not (msg.content.split(" ")[2].startswith("<@") and msg.content.split(" ")[2].endswith(">")) or ("!" in msg.content.split(" ")[2] and not isInt(msg.content.split(" ")[2][3:-1])) or ("!" not in msg.content.split(" ")[2] and not isInt(msg.content.split(" ")[2][2:-1])):
                    await msg.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                if "!" in msg.content.split(" ")[2]:
                    requestedUser = client.get_user(int(msg.content.split(" ")[2][3:-1]))
                else:
                    requestedUser = client.get_user(int(msg.content.split(" ")[2][2:-1]))
                if str(requestedUser.id) not in BBDB["users"]:
                    initializeUser(requestedUser.id)
                await msg.channel.send(":moneybag: **" + requestedUser.name + "** has **" + str(int(BBDB["users"][str(requestedUser.id)]["credits"])) + " Credits**.")
        elif command == "stats":
            if len(msg.content.split(" ")) < 3:
                statsEmbed = makeEmbed(col=factionColours["neutral"], desc="__Pilot Statistics__", titleTxt=msg.author.name, footerTxt="Pilot number #" + msg.author.discriminator, thumb=msg.author.avatar_url_as(size=64))
                if str(msg.author.id) not in BBDB["users"]:
                    statsEmbed.add_field(name="Credits balance:",value=0, inline=True)
                    statsEmbed.add_field(name="Lifetime total credits earned:", value=0, inline=True)
                    statsEmbed.add_field(name="‎",value="‎", inline=False)
                    statsEmbed.add_field(name="Total systems checked:",value=0, inline=True)
                    statsEmbed.add_field(name="Total bounties won:", value=0, inline=True)
                else:
                    statsEmbed.add_field(name="Credits balance:",value=str(int(BBDB["users"][str(msg.author.id)]["credits"])), inline=True)
                    statsEmbed.add_field(name="Lifetime total credits earned:", value=str(int(BBDB["users"][str(msg.author.id)]["totalCredits"])), inline=True)
                    statsEmbed.add_field(name="‎",value="‎", inline=False)
                    statsEmbed.add_field(name="Total systems checked:",value=str(BBDB["users"][str(msg.author.id)]["systemsChecked"]), inline=True)
                    statsEmbed.add_field(name="Total bounties won:", value=str(BBDB["users"][str(msg.author.id)]["wins"]), inline=True)
                await msg.channel.send(embed=statsEmbed)
                return
            else:
                if len(msg.content.split(" ")) > 3 or not (msg.content.split(" ")[2].startswith("<@") and msg.content.split(" ")[2].endswith(">")) or ("!" in msg.content.split(" ")[2] and not isInt(msg.content.split(" ")[2][3:-1])) or ("!" not in msg.content.split(" ")[2] and not isInt(msg.content.split(" ")[2][2:-1])):
                    await msg.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                requestedUser = client.get_user(int(msg.content.split(" ")[2][3:-1]))
                if requestedUser is None:
                    await msg.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
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
                    statsEmbed.add_field(name="Lifetime total credits earned:", value=str(int(BBDB["users"][str(requestedUser.id)]["totalCredits"])), inline=True)
                    statsEmbed.add_field(name="‎",value="‎", inline=False)
                    statsEmbed.add_field(name="Total systems checked:",value=str(BBDB["users"][str(requestedUser.id)]["systemsChecked"]), inline=True)
                    statsEmbed.add_field(name="Total bounties won:", value=str(BBDB["users"][str(requestedUser.id)]["wins"]), inline=True)
                await msg.channel.send(embed=statsEmbed)
        elif command == "map":
            if len(msg.content.split(" ")) > 2 and msg.content.split(" ")[2] == "-g":
                await msg.channel.send(bbdata.mapImageWithGraphLink)
            else:
                await msg.channel.send(bbdata.mapImageNoGraphLink)
        elif command == "check":
            if len(msg.content.split(" ")) < 3:
                await msg.channel.send(":x: Please provide a system to check! E.g: `!bb check Pescal Inartu`")
                return
            requestedSystem = msg.content[10:].title()
            if requestedSystem not in bbdata.systems:
                if len(requestedSystem) < 20:
                    await msg.channel.send(":x: The **" + requestedSystem + "** system is not on my star map! :map:")
                else:
                    await msg.channel.send(":x: The **" + requestedSystem[0:15] + "**... system is not on my star map! :map:")
                return
            if str(msg.author.id) not in BBDB["users"]:
                initializeUser(msg.author.id)
            if datetime.utcfromtimestamp(BBDB["users"][str(msg.author.id)]["bountyCooldownEnd"]) < datetime.utcnow():
                bountyWon = False
                for fac in BBDB["bounties"]:
                    toPop = []
                    for bountyIndex in range(len(BBDB["bounties"][fac])):
                        if BBDB["bounties"][fac][bountyIndex].check(requestedSystem, msg.author.id) == 3:
                            bountyWon = True
                            bounty = BBDB["bounties"][fac][bountyIndex]
                            rewards = bounty.calcRewards()
                            for userID in rewards:
                                BBDB["users"][str(userID)]["credits"] += rewards[userID]["reward"]
                                BBDB["users"][str(userID)]["totalCredits"] += rewards[userID]["reward"]
                            toPop += [bountyIndex]
                            await announceBountyWon(bounty, rewards, msg.guild, msg.author.id)
                    for bountyIndex in toPop:
                        BBDB["bounties"][fac].pop(bountyIndex)
                if bountyWon:
                    BBDB["users"][str(msg.author.id)]["wins"] += 1
                    await msg.channel.send(":moneybag: **" + msg.author.name + "**, you now have **" + str(int(BBDB["users"][str(msg.author.id)]["credits"])) + " Credits!**")
                else:
                    outmsg = ":telescope: **" + msg.author.name + "**, you did not find any criminals!"
                    for fac in BBDB["bounties"]:
                        for bounty in BBDB["bounties"][fac]:
                            if requestedSystem in bounty.route:
                                if 0 < bounty.route.index(bounty.answer) - bounty.route.index(requestedSystem) < 4:
                                    outmsg += "\n       • Local security forces spotted **" + bounty.getCodeNameTag()+ "** here recently. "
                    await msg.channel.send(outmsg)

                BBDB["users"][str(msg.author.id)]["systemsChecked"] += 1
                BBDB["users"][str(msg.author.id)]["bountyCooldownEnd"] = (datetime.utcnow() + timedelta(minutes=bbconfig.checkCooldown["minutes"])).timestamp()
            else:
                diff = datetime.utcfromtimestamp(BBDB["users"][str(msg.author.id)]["bountyCooldownEnd"]) - datetime.utcnow()
                minutes = int(diff.total_seconds() / 60)
                seconds = int(diff.total_seconds() % 60)
                await msg.channel.send(":stopwatch: **" + msg.author.name + "**, your *Khador drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")
        elif command == "bounties":
            if len(msg.content.split(" ")) == 2:
                outmessage = "__**Active Bounties**__\nTimes given in UTC. See more detailed information with `!bb bounties <faction>`\n```css"
                preLen = len(outmessage)
                for fac in BBDB["bounties"]:
                    if len(BBDB["bounties"][fac]) != 0:
                        outmessage += "\n • [" + fac.title() + "]: "
                        for bounty in BBDB["bounties"][fac]:
                            outmessage += bounty.getCodeNameTag() + ", "
                        outmessage = outmessage[:-2]
                if len(outmessage) == preLen:
                    outmessage += "\n[  No currently active bounties! Please check back later.  ]"
                await msg.channel.send(outmessage + "```")
                return
            requestedFaction = msg.content[13:].lower()
            if requestedFaction not in bbdata.bountyFactions:
                if len(requestedFaction) < 20:
                    await msg.channel.send(":x: Unrecognised faction: **" + requestedFaction + "**")
                else:
                    await msg.channel.send(":x: Unrecognised faction **" + requestedFaction[0:15] + "**...")
                return
            if len(BBDB["bounties"][requestedFaction]) == 0:
                await msg.channel.send(":stopwatch: There are no **" + requestedFaction.title() + "** bounties active currently!")
            else:
                outmessage = "__**Active " + requestedFaction.title() + " Bounties**__\nTimes given in UTC.```css"
                for bounty in BBDB["bounties"][requestedFaction]:
                    endTimeStr = datetime.utcfromtimestamp(bounty.endTime).strftime("%B %d %H %M %S").split(" ")
                    try:
                        outmessage += "\n • [" + bounty.getCodeNameTag() + "]" + " " * (bbdata.longestBountyNameLength + 1 - len(bounty.getCodeNameTag())) + ": " + str(int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + bbdata.numExtensions[int(endTimeStr[1][-1])] + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                    except Exception:
                        print("ERROR ON:",endTimeStr)
                        print("0:",endTimeStr[0])
                        print("1:",endTimeStr[1])
                        print("1,-1:",endTimeStr[1][-1])
                        print("2:",endTimeStr[2])
                        print("3:",endTimeStr[3])
                        outmessage += "\n • [" + bounty.getCodeNameTag() + "]" + " " * (bbdata.longestBountyNameLength + 1 - len(bounty.getCodeNameTag())) + ": " + str(int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + bbdata.numExtensions[int(endTimeStr[1][-1])] + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                    if endTimeStr[4] != "00":
                        outmessage += ":" + endTimeStr[4]
                    else:
                        outmessage += "   "
                    outmessage += " - " + str(len(bounty.route)) + " possible system"
                    if len(bounty.route) != 1:
                        outmessage += "s"
                await msg.channel.send(outmessage + "```\nTrack down criminals and **win credits** using `!bb route` and `!bb check`!")
        elif command == "route":
            if len(msg.content.split(" ")) < 3:
                await msg.channel.send(":x: Please provide the criminal name! E.g: `!bb route Kehnor`")
                return
            requestedBountyName = msg.content[10:]
            for fac in BBDB["bounties"]:
                for bounty in BBDB["bounties"][fac]:
                    if bounty.getCodeNameTag().lower() == requestedBountyName.lower():
                        outmessage = "**" + bounty.getCodeNameTag() + "**'s current route:\n> "
                        for system in bounty.route:
                            outmessage += " " + ("~~" if bounty.checked[system] != -1 else "") + system + ("~~" if bounty.checked[system] != -1 else "") + ","
                        outmessage = outmessage[:-1] + ". :rocket:"
                        await msg.channel.send(outmessage)
                        return
            outmsg = ":x: That pilot isn't on any bounty boards! :clipboard:"
            if requestedBountyName.startswith("<@"):
                outmsg += "\n:warning: **Don't tag users**, use their name and ID number like so: `!bb route Trimatix#2244`"
            await msg.channel.send(outmsg)

        elif command == "make-route":
            if len(msg.content.split(" ")) <= 3 or "," not in msg.content or len(msg.content[10:msg.content.index(",")]) < 1 or len(msg.content[msg.content.index(","):]) < 2:
                await msg.channel.send(":x: Please provide source and destination systems, separated with a comma and space.\nFor example: `!bb make-route Pescal Inartu, Loma`")
                return
            if msg.content.count(",") > 1:
                await msg.channel.send(":x: Please only provide **two** systems!")
                return
            startSyst = msg.content[15:].split(",")[0].title()
            endSyst = msg.content[15:].split(",")[1][1:].title()
            for systArg in [startSyst, endSyst]:
                if systArg not in bbdata.systems:
                    if len(systArg) < 20:
                        await msg.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
                    else:
                        await msg.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
                    return
                if not bbdata.systems[systArg].hasJumpGate():
                    if len(systArg) < 20:
                        await msg.channel.send(":x: The **" + systArg + "** system does not have a jump gate! :rocket:")
                    else:
                        await msg.channel.send(":x: The **" + systArg[0:15] + "**... system does not have a jump gate! :rocket:")
                    return
            routeStr = ""
            for currentSyst in bbutil.bbAStar(startSyst, endSyst, bbdata.systems):
                routeStr += currentSyst + ", "
            if routeStr.startswith("#"):
                await msg.channel.send(":x: ERR: Processing took too long! :stopwatch:")
            elif routeStr.startswith("!"):
                await msg.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
            elif startSyst == endSyst:
                await msg.channel.send(":thinking: You're already there, pilot!")
            else:
                await msg.channel.send("Here's the shortest route from **" + startSyst + "** to **" + endSyst + "**:\n> " + routeStr[:-2] + " :rocket:")
        elif command == "system":
            if len(msg.content.split(" ")) < 3:
                await msg.channel.send(":x: Please provide a system! Example: `!bb system Augmenta`")
            systArg = msg.content[11:].title()
            if systArg not in bbdata.systems:
                if len(systArg) < 20:
                    await msg.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
                else:
                    await msg.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
                return
            else:
                systObj = bbdata.systems[systArg]
                neighboursStr = ""
                for x in systObj.neighbours:
                    neighboursStr += x + ", "
                if neighboursStr == "":
                    neighboursStr = "No Jumpgate"
                else:
                    neighboursStr = neighboursStr[:-2]
                
                statsEmbed = makeEmbed(col=factionColours[systObj.faction], desc="__System Information__", titleTxt=systObj.name, footerTxt=systObj.faction.title(), thumb=factionIcons[systObj.faction])
                statsEmbed.add_field(name="Security Level:",value=bbdata.securityLevels[systObj.security].title())
                statsEmbed.add_field(name="Neighbour Systems:", value=neighboursStr)
                await msg.channel.send(embed=statsEmbed)
        elif command == "leaderboard":
            globalBoard = False
            stat = "totalCredits"
            boardScope = msg.guild.name
            boardTitle = "Total Credits Earned"
            boardUnit = "Credit"
            boardUnits = "Credits"

            if len(msg.content.split(" ")) > 2:
                args = msg.content.split(" ")[2].lower()
                if not args.startswith("-"):
                    await msg.channel.send(":x: Please prefix your arguments with a dash! E.g: `!bb leaderboard -gc`")
                    return
                args = args[1:]
                if ("g" not in args and len(args) > 2) or ("g" in args and len(args) > 3):
                    await msg.channel.send(":x: Too many arguments! Please only specify one leaderboard. E.g: `!bb leaderboard -gc`")
                    return
                for arg in args:
                    if arg not in "gcsw":
                        await msg.channel.send(":x: Unknown argument: '**" + arg + "**'. Please refer to `!bb help leaderboard`")
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
                if (globalBoard and client.get_user(int(userID)) is not None) or (not globalBoard and msg.guild.get_member(int(userID)) is not None):
                    inputDict[userID] = BBDB["users"][userID][stat]
            sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]

            leaderboardEmbed = makeEmbed(titleTxt=boardTitle, authorName=boardScope, icon=bbdata.winIcon, col = factionColours["neutral"])

            externalUser = False
            first = True
            for place in range(min(len(sortedUsers), 10)):
                if globalBoard and msg.guild.get_member(int(sortedUsers[place][0])) is None:
                    leaderboardEmbed.add_field(value="*" + str(place + 1) + ". " + client.get_user(int(sortedUsers[place][0])).mention, name=("⭐ " if first else "") + str(int(sortedUsers[place][1])) + " " + (boardUnit if int(sortedUsers[place][1]) == 1 else boardUnits), inline=False)
                    externalUser = True
                    if first: first = False
                else:
                    leaderboardEmbed.add_field(value=str(place + 1) + ". " + msg.guild.get_member(int(sortedUsers[place][0])).mention, name=("⭐ " if first else "") + str(int(sortedUsers[place][1])) + " " + (boardUnit if int(sortedUsers[place][1]) == 1 else boardUnits), inline=False)
                    if first: first = False
            if externalUser:
                leaderboardEmbed.set_footer(text="An `*` indicates a user that is from another server.")
            await msg.channel.send(embed=leaderboardEmbed)
        else:
            if msg.author.id == 188618589102669826 or msg.author.permissions_in(msg.channel).administrator:
                if command == "set-announce-channel":
                    bbconfig.announceChannel[str(msg.guild.id)] = msg.channel.id
                    await msg.channel.send(":ballot_box_with_check: Announcements channel set!")
                elif command == "set-play-channel":
                    bbconfig.playChannel[str(msg.guild.id)] = msg.channel.id
                    await msg.channel.send(":ballot_box_with_check: Bounty play channel set!")
                elif command == "admin-help":
                    helpEmbed = makeEmbed(titleTxt="BB Administrator Commands", thumb=client.user.avatar_url_as(size=64))
                    for section in bbdata.adminHelpDict.keys():
                        helpEmbed.add_field(name="‎",value=section, inline=False)
                        for currentCommand in bbdata.adminHelpDict[section].keys():
                            helpEmbed.add_field(name=currentCommand,value=bbdata.adminHelpDict[section][currentCommand], inline=False)
                    await msg.channel.send(bbdata.adminHelpIntro, embed=helpEmbed)
                elif msg.author.id == 188618589102669826:
                    if command == "sleep":
                        await msg.channel.send("zzzz....")
                        bbconfig.botLoggedIn = False
                        await client.logout()
                        saveDB(BBDB)
                    elif command == "save":
                        saveDB(BBDB)
                        await msg.channel.send("saved!")
                    elif command == "anchset?":
                        await msg.channel.send(str(msg.guild.id) in bbconfig.announceChannel)
                    elif command == "printanch":
                        await msg.channel.send(bbconfig.announceChannel[str(msg.guild.id)])
                    elif command == "plchset?":
                        await msg.channel.send(str(msg.guild.id) in bbconfig.playChannel)
                    elif command == "printplch":
                        await msg.channel.send(bbconfig.playChannel[str(msg.guild.id)])
                    elif command == "stations":
                        await msg.channel.send(bbdata.systems)
                    elif command == "clear":
                        for fac in bbdata.bountyFactions:
                            BBDB["bounties"][fac] = []
                        await msg.channel.send(":ballot_box_with_check: Active bounties cleared!")
                    elif command == "cooldown":
                        diff = datetime.utcfromtimestamp(BBDB["users"][str(msg.author.id)]["bountyCooldownEnd"]) - datetime.utcnow()
                        minutes = int(diff.total_seconds() / 60)
                        seconds = int(diff.total_seconds() % 60)
                        await msg.channel.send(str(BBDB["users"][str(msg.author.id)]["bountyCooldownEnd"]) + " = " + str(minutes) + "m, " + str(seconds) + "s.")
                        await msg.channel.send(datetime.utcfromtimestamp(BBDB["users"][str(msg.author.id)]["bountyCooldownEnd"]).strftime("%Hh%Mm%Ss"))
                        await msg.channel.send(datetime.utcnow().strftime("%Hh%Mm%Ss"))
                    elif command == "resetcool":
                        if len(msg.content.split(" ")) < 3:
                            BBDB["users"][str(msg.author.id)]["bountyCooldownEnd"] = datetime.utcnow().timestamp()
                        else:
                            if "!" in msg.content.split(" ")[2]:
                                requestedUser = client.get_user(int(msg.content[17:-1]))
                            else:
                                requestedUser = client.get_user(int(msg.content[16:-1]))
                            BBDB["users"][str(requestedUser.id)]["bountyCooldownEnd"] = datetime.utcnow().timestamp()
                        await msg.channel.send("Done!")
                    elif command == "setCheckCooldown":
                        if len(msg.content.split(" ")) != 3:
                            await msg.channel.send(":x: please give the number of minutes!")
                            return
                        if not isInt(msg.content.split(" ")[2]):
                            await msg.channel.send(":x: that's not a number!")
                            return
                        bbconfig.checkCooldown["minutes"] = int(msg.content.split(" ")[2])
                        await msg.channel.send("Done! *you still need to update the file though* <@188618589102669826>")
                    elif command == "setBountyPeriodM":
                        if len(msg.content.split(" ")) != 3:
                            await msg.channel.send(":x: please give the number of minutes!")
                            return
                        if not isInt(msg.content.split(" ")[2]):
                            await msg.channel.send(":x: that's not a number!")
                            return
                        bbconfig.newBountyFixedDelta["minutes"] = int(msg.content.split(" ")[2])
                        bbconfig.newBountyFixedDeltaChanged = True
                        await msg.channel.send("Done! *you still need to update the file though* <@188618589102669826>")
                    elif command == "setBountyPeriodH":
                        if len(msg.content.split(" ")) != 3:
                            await msg.channel.send(":x: please give the number of minutes!")
                            return
                        if not isInt(msg.content.split(" ")[2]):
                            await msg.channel.send(":x: that's not a number!")
                            return
                        bbconfig.newBountyFixedDeltaChanged = True
                        bbconfig.newBountyFixedDelta["hours"] = int(msg.content.split(" ")[2])
                        await msg.channel.send("Done! *you still need to update the file though* <@188618589102669826>")
                    elif command == "resetNewBountyCool":
                        bbconfig.newBountyDelayReset = True
                        await msg.channel.send(":ballot_box_with_check: New bounty cooldown reset!")
                    elif command == "make-bounty":
                        if len(msg.content.split(" ")) < 3:
                            newBounty = Bounty(BBDB=BBDB)
                        elif len(msg.content[16:].split("+")) == 1:
                            newFaction = msg.content[16:]
                            newBounty = Bounty(BBDB=BBDB, faction=newFaction)
                        elif len(msg.content[16:].split("+")) == 9:
                            bData = msg.content[16:].split("+")
                            newFaction = bData[0].rstrip(" ")
                            if newFaction == "auto":
                                newFaction = ""
                            newName = bData[1].rstrip(" ").title()
                            if newName == "Auto":
                                newName = ""
                            else:
                                nameFound = False
                                for fac in BBDB["bounties"]:
                                    for bounty in BBDB["bounties"][fac]:
                                        if bounty.name == newName:
                                            nameFound = True
                                            break
                                    if nameFound:
                                        break
                                if nameFound:
                                    await msg.channel.send(":x: That pilot is already on the " + fac.title() + " bounty board!")
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
                            newBounty = Bounty(BBDB=BBDB, faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=False, icon=newIcon)
                        BBDB["bounties"][newBounty.faction].append(newBounty)
                        await announceNewBounty(newBounty)
                    elif command == "make-player-bounty":
                        if len(msg.content.split(" ")) < 4:
                            requestedID = int(msg.content.split(" ")[2].lstrip("<@!").rstrip(">"))
                            if not isInt(requestedID) or (client.get_user(int(requestedID))) is None:
                                await msg.channel.send(":x: Player not found!")
                                return
                            newBounty = Bounty(BBDB=BBDB, name="<@" + str(requestedID) + ">", isPlayer=True, icon=str(client.get_user(requestedID).avatar_url_as(size=64)), client=client)
                        elif len(msg.content[23:].split("+")) == 1:
                            newFaction = msg.content[23:]
                            newBounty = Bounty(BBDB=BBDB, faction=newFaction)
                        elif len(msg.content[23:].split("+")) == 9:
                            bData = msg.content[23:].split("+")
                            newFaction = bData[0].rstrip(" ")
                            if newFaction == "auto":
                                newFaction = ""
                            newName = bData[1].rstrip(" ").title()
                            if newName == "Auto":
                                newName = ""
                            else:
                                requestedID = int(newName.lstrip("<@!").rstrip(">"))
                                if not isInt(requestedID) or (client.get_user(int(requestedID))) is None:
                                    await msg.channel.send(":x: Player not found!")
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
                            newBounty = Bounty(BBDB=BBDB, client=client, faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime, isPlayer=True, icon=newIcon)
                        BBDB["bounties"][newBounty.faction].append(newBounty)
                        await announceNewBounty(newBounty)
                    else:
                        await msg.channel.send(""":question: Can't do that, commander. Type `!bb help` for a list of commands! **o7**""")
                else:
                    await msg.channel.send(""":question: Can't do that, commander. Type `!bb help` for a list of commands! **o7**""")
            else:
                await msg.channel.send(""":question: Can't do that, pilot. Type `!bb help` for a list of commands! **o7**""")
        
client.run(bbPRIVATE.botToken)
