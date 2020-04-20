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


class Bounty:
    issueTime = -1
    name = ""
    route = []
    reward = 0.0
    endTime = -1
    faction = ""
    checked = {}
    answer = ""
    

    def __init__(self, faction="", name="", route=[], start="", end="", answer="", checked={}, reward=-1.0, issueTime=-1.0, endTime=-1.0):
        self.faction = faction.lower()
        self.name = name
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
        if self.reward == -1.0:
            self.reward = len(self.route) * bbconfig.bPointsToCreditsRatio
        elif self.reward < 0:
            raise RuntimeError("Bounty constructor: Invalid reward requested '" + str(reward) + "'")
        if self.issueTime == -1.0:
            self.issueTime = datetime.utcnow().replace(second=0).timestamp()
        if self.endTime == -1.0:
            self.endTime = (datetime.utcfromtimestamp(self.issueTime) + timedelta(days=len(self.route))).timestamp()

        if self.checked == {}:
            for station in self.route:
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
        return {"faction": self.faction, "name": self.name, "route": self.route, "answer": self.answer, "checked": self.checked, "reward": self.reward, "issueTime": self.issueTime, "endTime": self.endTime}


def makeBounty(faction="", bountyName="", start="", end=""):
    return Bounty(faction=faction, name=bountyName, start=start, end=end)


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


def loadDB():
    db = bbutil.readJDB("BBDB.json")
    if "sendChannel" in db:
        bbconfig.sendChannel = db["sendChannel"]
    if "bounties" in db:
        for fac in db["bounties"]:
            currentBounties = []
            for bounty in db["bounties"][fac]:
                currentBounties.append(Bounty(faction=bounty["faction"], name=bounty["name"], route=bounty["route"], answer=bounty["answer"], checked=bounty["checked"], reward=bounty["reward"], issueTime=bounty["issueTime"], endTime=bounty["endTime"]))
            db["bounties"][fac] = currentBounties
    return db

def saveDB(db):
    BBDB["sendChannel"] = bbconfig.sendChannel
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

BBDB = loadDB()
client = discord.Client()


def isInt(x):
    try:
        int(x)
    except TypeError:
        return False
    except ValueError:
        return False
    return True


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
        if (bbconfig.newBountyDelayType == "random" and currentBountyWait >= currentNewBountyDelay) or \
                (bbconfig.newBountyDelayType == "fixed" and timedelta(seconds=currentBountyWait) >= newBountyDelayDelta and ((not bbconfig.newBountyFixedUseDailyTime) or (bbconfig.newBountyFixedUseDailyTime and \
                    datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta - timedelta(minutes=bbconfig.delayFactor) \
                    <= datetime.utcnow() \
                    <= datetime.utcnow().replace(hour=0, minute=0, second=0) + newBountyDelayDelta + timedelta(minutes=bbconfig.delayFactor)))):
            if canMakeBounty():
                newBounty = Bounty()
                BBDB["bounties"][newBounty.faction].append(newBounty)
                for currentGuild in bbconfig.sendChannel:
                    if currentGuild != 0:
                        await client.get_channel(bbconfig.sendChannel[currentGuild]).send("```** New " + newBounty.faction + " Bounty Available```New " + newBounty.faction + " bounty: **" + newBounty.name + "**.\nSee the culprit's route with `!bb bounty-route " + newBounty.faction + " " + newBounty.name + "`")
            if bbconfig.newBountyDelayType == "random":
                currentNewBountyDelay = random.randint(bbconfig.newBountyDelayMin, bbconfig.newBountyDelayMax)
            else:
                currentNewBountyDelay = newBountyDelayDelta
            currentBountyWait = 0
        # save the database
        if currentSaveWait >= bbconfig.saveDelay:
            saveDB(BBDB)
            currentSaveWait = 0


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.split(" ")[0].lower() == ('!bb'):
        if len(message.content.split(" ")) > 1:
            command = message.content.split(" ")[1].lower()
        else:
            command = "help"
        if command == 'help':
            await message.channel.send(bbdata.helpStr)
        elif command == "hello":
            await message.channel.send("Greetings, pilot! **o7**")
        elif command == "balance":
            if len(message.content.split(" ")) < 3:
                if str(message.author.id) not in BBDB["users"]:
                    initializeUser(message.author.id)
                await message.channel.send(":moneybag: **" + message.author.name + "**, you have **" + str(int(BBDB["users"][str(message.author.id)]["credits"])) + " Credits**.")
            else:
                if len(message.content.split(" ")) > 3 or not (message.content.split(" ")[2].startswith("<@") and message.content.split(" ")[2].endswith(">")) or ("!" in message.content.split(" ")[2] and not isInt(message.content.split(" ")[2][3:-1])) or ("!" not in message.content.split(" ")[2] and not isInt(message.content.split(" ")[2][2:-1])):
                    await message.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                if "!" in message.content.split(" ")[2]:
                    requestedUser = client.get_user(int(message.content.split(" ")[2][3:-1]))
                else:
                    requestedUser = client.get_user(int(message.content.split(" ")[2][2:-1]))
                if str(requestedUser.id) not in BBDB["users"]:
                    initializeUser(requestedUser.id)
                await message.channel.send(":moneybag: **" + requestedUser.name + "** has **" + str(int(BBDB["users"][str(requestedUser.id)]["credits"])) + " Credits**.")
        elif command == "stats":
            if len(message.content.split(" ")) < 3:
                if str(message.author.id) not in BBDB["users"]:
                    await message.channel.send("```yaml\n--=- PILOT STATS: " + str(message.author).upper() + " -=--\n • Credits_balance: 0\n • Lifetime_total_credits_earned: 0\n • Total_systems_checked_for_bounties: 0\n • Total_bounties_won: 0" + "```")
                return
            else:
                if len(message.content.split(" ")) > 3 or not (message.content.split(" ")[2].startswith("<@") and message.content.split(" ")[2].endswith(">")) or ("!" in message.content.split(" ")[2] and not isInt(message.content.split(" ")[2][3:-1])) or ("!" not in message.content.split(" ")[2] and not isInt(message.content.split(" ")[2][2:-1])):
                    await message.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                requestedUser = client.get_user(int(message.content.split(" ")[2][3:-1]))
                if requestedUser is None:
                    await message.channel.send(":x: **Invalid user!** use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                userID = str(requestedUser.id)
                if userID not in BBDB["users"]:
                    await message.channel.send("```yaml\n--=- PILOT STATS: " + str(requestedUser).upper() + " -=--\n • Credits_balance: 0\n • Lifetime_total_credits_earned: 0\n • Total_systems_checked_for_bounties: 0\n • Total_bounties_won: 0" + "```")
                    return
                # userName = requestedUser.name
            await message.channel.send("```yaml\n--=- PILOT STATS: " + str(requestedUser).upper() + " -=--\n • Credits_balance: " + str(BBDB["users"][userID]["credits"]) + "\n • Lifetime_total_credits_earned: " + str(BBDB["users"][userID]["totalCredits"]) + "\n • Total_systems_checked_for_bounties: " + str(BBDB["users"][userID]["systemsChecked"]) + "\n • Total_bounties_won: " + str(BBDB["users"][userID]["wins"]) + "```")
        elif command == "map":
            if len(message.content.split(" ")) > 2 and message.content.split(" ")[2] == "-g":
                await message.channel.send(bbdata.mapImageWithGraphLink)
            else:
                await message.channel.send(bbdata.mapImageNoGraphLink)
        elif command == "check":
            if len(message.content.split(" ")) < 3:
                await message.channel.send(":x: Please provide a system to check! E.g: `!bb check Pescal Inartu`")
                return
            requestedSystem = message.content[10:].title()
            if requestedSystem not in bbdata.systems:
                if len(requestedSystem) < 20:
                    await message.channel.send(":x: The **" + requestedSystem + "** system is not on my star map! :map:")
                else:
                    await message.channel.send(":x: The **" + requestedSystem[0:15] + "**... system is not on my star map! :map:")
                return
            if str(message.author.id) not in BBDB["users"]:
                initializeUser(message.author.id)
            if datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) < datetime.utcnow():
                bountyWon = False
                for fac in BBDB["bounties"]:
                    for bountyIndex in range(len(BBDB["bounties"][fac])):
                        if BBDB["bounties"][fac][bountyIndex].check(requestedSystem, message.author.id) == 3:
                            bountyWon = True
                            bounty = BBDB["bounties"][fac][bountyIndex]
                            outStr = ":trophy: **You win!**\n**" + message.author.name + "** located and EMP'd **" + bounty.name + "**, who has been arrested by local security forces. :chains:"
                            rewards = bounty.calcRewards()
                            place = 1
                            for userID in rewards:
                                if rewards[userID]["won"]:
                                    outStr += "\n> " + str(place) + ". <@" + str(userID) + "> was awarded **" + str(int(rewards[userID]["reward"])) + " Credits** for tracking down the culprit after checking **" + str(rewards[userID]["checked"]) + " systems**."
                                    BBDB["users"][str(userID)]["credits"] += rewards[userID]["reward"]
                                    BBDB["users"][str(userID)]["totalCredits"] += rewards[userID]["reward"]
                                    place += 1
                            for userID in rewards:
                                if not rewards[userID]["won"]:
                                    outStr += "\n> " + str(place) + ". <@" + str(userID) + "> was awarded **" + str(int(rewards[userID]["reward"])) + " Credits** for aiding the search, checking **" + str(rewards[userID]["checked"]) + " systems**."
                                    BBDB["users"][str(userID)]["credits"] += rewards[userID]["reward"]
                                    BBDB["users"][str(userID)]["totalCredits"] += rewards[userID]["reward"]
                                    place += 1
                            BBDB["bounties"][fac].pop(bountyIndex)
                            await message.channel.send(outStr)
                if bountyWon:
                    BBDB["users"][str(message.author.id)]["wins"] += 1
                    BBDB["users"][str(message.author.id)]["systemsChecked"] += 1
                    await message.channel.send(":moneybag: **" + message.author.name + "**, you now have **" + str(int(BBDB["users"][str(message.author.id)]["credits"])) + " Credits!**")
                else:
                    BBDB["users"][str(message.author.id)]["wins"] += 1
                    BBDB["users"][str(message.author.id)]["systemsChecked"] += 1
                    await message.channel.send(":telescope: **" + message.author.name + "**, you did not find any criminals!")
                BBDB["users"][str(message.author.id)]["bountyCooldownEnd"] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
            else:
                diff = datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) - datetime.utcnow()
                minutes = int(diff.total_seconds() / 60)
                seconds = int(diff.total_seconds() % 60)
                await message.channel.send(":stopwatch: **" + message.author.name + ", your *Khador drive* is still charging! please wait **" + str(minutes) + "m " + str(seconds) + "s.**")
        elif command == "bounties":
            if len(message.content.split(" ")) < 2:
                await message.channel.send(":x: Provide a faction to check the bounty board of! E.g: `!bounties Terran`")
                return
            requestedFaction = message.content[13:].lower()
            if requestedFaction not in bbdata.bountyFactions:
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
                    outmessage += "\n • [" + bounty.name + "]" + " " * (bbdata.longestBountyNameLength + 1 - len(bounty.name)) + ": " + str(int(bounty.reward)) + " Credits - Ending " + endTimeStr[0] + " " + endTimeStr[1] + bbdata.numExtensions[int(endTimeStr[1][-1])] + " at :" + endTimeStr[2] + ":" + endTimeStr[3]
                    if endTimeStr[4] != "00":
                        outmessage += ":" + endTimeStr[4]
                    else:
                        outmessage += "   "
                    outmessage += " - " + str(len(bounty.route)) + " possible system"
                    if len(bounty.route) != 1:
                        outmessage += "s"
                await message.channel.send(outmessage + "```\nTrack down criminals and **win credits** using `!bb bounty-route` and `!bb check`!")
        elif command == "bounty-route":
            if len(message.content.split(" ")) < 4:
                await message.channel.send(":x: Please provide the bounty board and criminal name! E.g: `!bb bounty-route Terran Kehnor`")
                return
            if message.content.split(" ")[2].lower() not in bbdata.bountyFactions:
                await message.channel.send(":x: Invalid faction, please choose from: Terran, Vossk, Nivelian, or Midorian.")
            requestedFaction = message.content.split(" ")[2].lower()
            requestedBountyName = ""
            for section in message.content.split(" ")[3:]:
                requestedBountyName += " " + section.title()
            if len(requestedBountyName) > 0:
                requestedBountyName = requestedBountyName[1:]
            bountyFound = False
            for bounty in BBDB["bounties"][requestedFaction]:
                if bounty.name == requestedBountyName:
                    bountyFound = True
                    outmessage = "**" + requestedBountyName + "**'s current route:"
                    for system in bounty.route:
                        outmessage += " " + system + ","
                    outmessage = outmessage[:-1] + ". :rocket:"
                    await message.channel.send(outmessage)
            if (not bountyFound):
                await message.channel.send(":x: That pilot is not on the **" + requestedFaction + "** bounty board! :clipboard:")
        elif command == "route":
            if len(message.content.split(" ")) <= 3 or "," not in message.content or len(message.content[10:message.content.index(",")]) < 1 or len(message.content[message.content.index(","):]) < 2:
                await message.channel.send(":x: Please provide source and destination systems, separated with a comma and space.\nFor example: `!bb route Pescal Inartu, Loma`")
                return
            if message.content.count(",") > 1:
                await message.channel.send(":x: Please only provide **two** systems!")
                return
            startSyst = message.content[10:].split(",")[0].title()
            endSyst = message.content[10:].split(",")[1][1:].title()
            for systArg in [startSyst, endSyst]:
                if systArg not in bbdata.systems:
                    if len(systArg) < 20:
                        await message.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
                    else:
                        await message.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
                    return
                if not bbdata.systems[systArg].hasJumpGate():
                    if len(systArg) < 20:
                        await message.channel.send(":x: The **" + systArg + "** system does not have a jump gate! :rocket:")
                    else:
                        await message.channel.send(":x: The **" + systArg[0:15] + "**... system does not have a jump gate! :rocket:")
                    return
            routeStr = ""
            for currentSyst in bbutil.bbAStar(startSyst, endSyst, bbdata.systems):
                routeStr += currentSyst + ", "
            if routeStr.startswith("#"):
                await message.channel.send(":x: ERR: Processing took too long! :stopwatch:")
            elif routeStr.startswith("!"):
                await message.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
            elif startSyst == endSyst:
                await message.channel.send(":thinking: You're already there, pilot!")
            else:
                await message.channel.send("Here's the shortest route from **" + startSyst + "** to **" + endSyst + "**:\n> " + routeStr[:-2] + " :rocket:")
        elif command == "system-info":
            if len(message.content.split(" ")) < 3:
                await message.channel.send(":x: Please provide a system! Example: `!bb system-info Augmenta`")
            systArg = message.content[16:].title()
            if systArg not in bbdata.systems:
                if len(systArg) < 20:
                    await message.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
                else:
                    await message.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
                return
            else:
                systObj = bbdata.systems[systArg]
                neighboursStr = ""
                for x in systObj.neighbours:
                    neighboursStr += x + ", "
                if neighboursStr == "":
                    neighboursStr = ""
                else:
                    neighboursStr = neighboursStr[:-2]
                
                await message.channel.send("```xml\n<____System_Name____: " + systObj.name + " >\n"
                                            + "<______Faction______: " + systObj.faction.title() + " >\n"
                                            + "<_Neighbour_Systems_: " + neighboursStr + " >\n"
                                            + "<__Security_Level___: " + bbdata.securityLevels[systObj.security].title() + " >```")
        elif command == "leaderboard":
            globalBoard = False
            stat = "totalCredits"
            boardPrefix = ""
            boardTitle = "TOTAL CREDITS EARNED"
            boardUnit = "Credits"

            if len(message.content.split(" ")) > 2:
                args = message.content.split(" ")[2].lower()
                if not args.startswith("-"):
                    await message.channel.send(":x: Please prefix your arguments with a dash! E.g: `!bb leaderboard -gc`")
                    return
                if ("g" not in args and len(args) > 2) or ("g" in args and len(args) > 3):
                    await message.channel.send(":x: Too many arguments! Please only specify one leaderboard. E.g: `!bb leaderboard -gc`")
                    return
                if "g" in args:
                    globalBoard = True
                    boardPrefix = "GLOBAL "
                if "c" in args:
                    stat = "credits"
                    boardTitle = "CURRENT BALANCE"
                    boardUnit = "Credits"
                elif "s" in args:
                    stat = "systemsChecked"
                    boardTitle = "SYSTEMS CHECKED"
                    boardUnit = "Systems"
                elif "w" in args:
                    stat = "wins"
                    boardTitle = "BOUNTIES WON"
                    boardUnit = "Bounties"

            inputDict = {}
            for userID in BBDB["users"]:
                if client.get_user(userID) is not None and globalBoard or message.guild.get_user(userID) is not None:
                    inputDict[userID] = BBDB["users"][userID][stat]
            sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]
            outStr = "```--= " + boardPrefix + "LEADERBOARD: " + boardTitle + "=--"
            externalUser = False
            for place in range(min(len(sortedUsers), 10)):
                if globalBoard and message.guild.get_user(int(sortedUsers[place][0])) is None:
                    outStr += "\n " + str(place + 1) + ". " + client.get_user(int(sortedUsers[place][0])).name + "* - " + str(int(sortedUsers[place][1])) + " " + boardUnit
                    externalUser = True
                else:
                    outStr += "\n " + str(place + 1) + ". " + client.get_user(int(sortedUsers[place][0])).name + " - " + str(int(sortedUsers[place][1])) + " " + boardUnit
            if externalUser:
                outStr = "*(An `*` indicates a user that is from another server.)*\n" + outStr
            outStr += "```"
            await message.channel.send(outStr)
        elif command == "make-bounty":
            if len(message.content.split(" ")) < 3:
                newFaction = ""
            elif len(message.content[16:].split("+")) == 1:
                newFaction = message.content[16:]
                newBounty = Bounty(faction=newFaction)
            elif len(message.content[16:].split("+")) == 8:
                bData = message.content[16:].split("+")
                newFaction = bData[0].rstrip(" ")
                if newFaction == "auto":
                    newFaction = ""
                newName = bData[1].rstrip(" ")
                if newName == "auto":
                    newName = ""
                newRoute = list(bData[2].rstrip(" "))
                if newRoute == ['a', 'u', 't', 'o']:
                    newRoute = []
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
                newBounty = Bounty(faction=newFaction, name=newName, route=newRoute, start=newStart, end=newEnd, answer=newAnswer, reward=newReward, endTime=newEndTime)
            BBDB["bounties"][newBounty.faction].append(newBounty)
            if str(message.guild.id) in bbconfig.sendChannel and bbconfig.sendChannel[str(message.guild.id)] != 0:
                await client.get_channel(bbconfig.sendChannel[str(message.guild.id)]).send("```** New " + newBounty.faction.title() + " Bounty Available```\n:chains: A new bounty has been published by " + newBounty.faction.title() + " central command: **" + newBounty.name + "**!\n> See the culprit's route with `!bb route " + newBounty.faction.title() + " " + newBounty.name + "` :rocket:")
        else:
            if message.author.id == 188618589102669826 or message.author.administrator:
                if command == "setchannel":
                    bbconfig.sendChannel[str(message.guild.id)] = message.channel.id
                    await message.channel.send(":ballot_box_with_check: Announcements channel set!")
                elif command == "admin-help":
                    await message.channel.send(bbdata.adminHelpStr)
                # elif command == "bounty-cooldown":
                #     diff =  - datetime.utcnow()
                #     minutes = int(diff.total_seconds() / 60)
                #     seconds = int(diff.total_seconds() % 60)
                #     await message.channel.send("There is " + + "left until a new bounty is added.")
                elif message.author.id == 188618589102669826:
                    if command == "sleep":
                        await message.channel.send("zzzz....")
                        bbconfig.botLoggedIn = False
                        await client.logout()
                        # bbutil.writeJDB("BBDB.json", BBDB)
                        saveDB(BBDB)
                    elif command == "save":
                        saveDB(BBDB)
                        await message.channel.send("saved!")
                    elif command == "chset?":
                        await message.channel.send(str(message.guild.id) in bbconfig.sendChannel)
                    elif command == "printch":
                        await message.channel.send(bbconfig.sendChannel[str(message.guild.id)])
                    elif command == "stations":
                        await message.channel.send(bbdata.systems)
                    elif command == "clear":
                        for fac in bbdata.bountyFactions:
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
                        if len(message.content.split(" ")) < 3:
                            BBDB["users"][str(message.author.id)]["bountyCooldownEnd"] = datetime.utcnow().timestamp()
                        else:
                            if "!" in message.content.split(" ")[2]:
                                requestedUser = client.get_user(int(message.content[17:-1]))
                            else:
                                requestedUser = client.get_user(int(message.content[16:-1]))
                            BBDB["users"][str(requestedUser.id)]["bountyCooldownEnd"] = datetime.utcnow().timestamp()
                        await message.channel.send("Done!")
                    # elif command == "make-bounty":
                    #     if len(message.content.split(" ")) < 3:
                    #         newFaction = ""
                    #     else:
                    #         newFaction = message.content[16:]
                    #     newBounty = Bounty(faction=newFaction)
                    #     BBDB["bounties"][newBounty.faction].append(newBounty)
                    #     if str(message.guild.id) in bbconfig.sendChannel and bbconfig.sendChannel[str(message.guild.id)] != 0:
                    #         await client.get_channel(bbconfig.sendChannel[str(message.guild.id)]).send("```** New " + newBounty.faction + " Bounty Available```New " + newBounty.faction + " bounty: **" + newBounty.name + "**.\nSee the culprit's route with `!bb route " + newBounty.faction + " " + newBounty.name + "`")
                    else:
                        await message.channel.send(""":question: Can't do that, pilot. Type `!bb help` for a list of commands! **o7**""")
                else:
                    await message.channel.send(""":question: Can't do that, pilot. Type `!bb help` for a list of commands! **o7**""")
            else:
                await message.channel.send(""":question: Can't do that, pilot. Type `!bb help` for a list of commands! **o7**""")
        
client.run(bbPRIVATE.botToken)
