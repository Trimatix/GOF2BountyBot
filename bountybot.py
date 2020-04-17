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
    BBDB["users"][str(userID)] = {"credits":0, "bountyCooldownEnd":0}


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
        self.faction = faction
        self.name = name
        self.route = route
        self.answer = answer
        self.checked = checked
        self.reward = reward
        self.issueTime = issueTime
        self.endTime = endTime

        if faction == "":
            self.faction = random.choice(bbdata.bountyFactions)
        elif faction not in bbdata.bountyFactions:
            raise RuntimeError("Bounty constructor: Invalid faction requested '" + faction + "'")
    
        if route == []:
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
            for system in route:
                if system not in bbdata.systems:
                    raise RuntimeError("Bounty constructor: Invalid system in route '" + system + "'")
        if answer == "":
            self.answer = random.choice(self.route)
        elif answer not in bbdata.systems:
            raise RuntimeError("Bounty constructor: Invalid answer requested '" + answer + "'")
        if name == "":
            self.name = random.choice(bbdata.bountyNames[self.faction])
        if reward == -1.0:
            self.reward = len(self.route) * 100
        elif reward < 0:
            raise RuntimeError("Bounty constructor: Invalid reward requested '" + str(reward) + "'")
        if issueTime == -1.0:
            self.issueTime = datetime.utcnow().timestamp()
        if endTime == -1.0:
            self.endTime = (datetime.utcfromtimestamp(self.issueTime) + timedelta(days=len(self.route))).timestamp()

        if checked == {}:
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
    if "bounties" in db:
        for fac in db["bounties"]:
            currentBounties = []
            for bounty in db["bounties"][fac]:
                currentBounties.append(bounty.toDict())
            db["bounties"][fac] = currentBounties
    bbutil.writeJDB("BBDB.json", db)

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
    currentNewBountyDelay = random.randint(bbconfig.newBountyDelayMin, bbconfig.newBountyDelayMax)
    while bbconfig.botLoggedIn:
        await asyncio.sleep(bbconfig.delayFactor)
        currentBountyWait += bbconfig.delayFactor
        currentSaveWait += bbconfig.delayFactor
        # Make new bounties
        if currentBountyWait >= currentNewBountyDelay:
            if canMakeBounty():
                newBounty = Bounty()
                BBDB["bounties"][newBounty.faction].append(newBounty)
                for currentGuild in bbconfig.sendChannel:
                    if currentGuild != 0:
                        await client.get_channel(bbconfig.sendChannel[currentGuild]).send("New " + newBounty.faction + " bounty: " + newBounty.name)
            currentNewBountyDelay = random.randint(bbconfig.newBountyDelayMin, bbconfig.newBountyDelayMax)
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
            await message.channel.send("Hello!")
        elif command == "balance":
            if len(message.content.split(" ")) < 3:
                if str(message.author.id) not in BBDB["users"]:
                    initializeUser(message.author.id)
                await message.channel.send(message.author.name + ", you have " + str(int(BBDB["users"][str(message.author.id)]["credits"])) + " credits.")
            else:
                if len(message.content.split(" ")) > 3 or not (message.content.split(" ")[2].startswith("<@") and message.content.split(" ")[2].endswith(">")) or ("!" in message.content.split(" ")[2] and not isInt(message.content.split(" ")[2][3:-1])) or ("!" not in message.content.split(" ")[2] and not isInt(message.content.split(" ")[2][2:-1])):
                    await message.channel.send("Invalid user! use `!bb balance` to display your own balance, or `!bb balance @userTag` to display someone else's balance!")
                    return
                if "!" in message.content.split(" ")[2]:
                    requestedUser = client.get_user(int(message.content.split(" ")[2][3:-1]))
                else:
                    requestedUser = client.get_user(int(message.content.split(" ")[2][2:-1]))
                if str(requestedUser.id) not in BBDB["users"]:
                    initializeUser(requestedUser.id)
                await message.channel.send(requestedUser.name + " has " + str(int(BBDB["users"][str(requestedUser.id)]["credits"])) + " credits.")
        elif command == "map":
            if len(message.content.split(" ")) > 2 and message.content.split(" ")[2] == "-g":
                await message.channel.send(bbdata.mapImageWithGraphLink)
            else:
                await message.channel.send(bbdata.mapImageNoGraphLink)
        elif command == "check":
            if len(message.content.split(" ")) < 3:
                await message.channel.send("Please provide a system to check!")
                return
            requestedSystem = message.content[10:].title()
            if requestedSystem not in bbdata.systems:
                if len(requestedSystem) < 20:
                    await message.channel.send("The " + requestedSystem + " system is not on my star map!")
                else:
                    await message.channel.send("The " + requestedSystem[0:15] + "... system is not on my star map!")
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
                            outStr = "You win!\n" + message.author.name + " located and EMP'd " + bounty.name + ", who has been arrested by local securty forces."
                            rewards = bounty.calcRewards()
                            for userID in rewards:
                                if rewards[userID]["won"]:
                                    outStr += "\n <@" + str(userID) + "> was awarded " + str(int(rewards[userID]["reward"])) + " credits for tracking down the culprit after checking " + str(rewards[userID]["checked"]) + " stations."
                                    BBDB["users"][str(userID)]["credits"] += rewards[userID]["reward"]
                            for userID in rewards:
                                if not rewards[userID]["won"]:
                                    outStr += "\n <@" + str(userID) + "> was awarded " + str(int(rewards[userID]["reward"])) + " credits for aiding the search, checking " + str(rewards[userID]["checked"]) + " stations."
                                    BBDB["users"][str(userID)]["credits"] += rewards[userID]["reward"]
                            BBDB["bounties"][fac].pop(bountyIndex)
                            await message.channel.send(outStr)
                if bountyWon:
                    await message.channel.send(message.author.name + ", you now have " + str(int(BBDB["users"][str(message.author.id)]["credits"])) + " credits!")
                else:
                    await message.channel.send(message.author.name + ", you did not find any criminals!")
                BBDB["users"][str(message.author.id)]["bountyCooldownEnd"] = (datetime.utcnow() + timedelta(hours=1,minutes=5)).timestamp()
            else:
                diff = datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) - datetime.utcnow()
                minutes = int(diff.total_seconds() / 60)
                seconds = int(diff.total_seconds() % 60)
                await message.channel.send(message.author.name + ", your Khador drive is still charging! please wait " + str(minutes) + "m " + str(seconds) + "s.")
        elif len(message.content.split(" ")) > 2 and command == "bounties" and message.content[13:] in bbdata.bountyFactions:
            requestedFaction = message.content[13:]
            if len(BBDB["bounties"][requestedFaction]) == 0:
                await message.channel.send("There are no " + requestedFaction + " bounties active currently!")
            else:
                outmessage = "active " + requestedFaction + " bounties:"
                for bounty in BBDB["bounties"][requestedFaction]:
                    outmessage += "\n - " + bounty.name + ": " + str(int(bounty.reward)) + " credits, issued: " + datetime.utcfromtimestamp(bounty.issueTime).strftime("%B-%d %H:%M:%S") + ", ending: " + datetime.utcfromtimestamp(bounty.endTime).strftime("%B-%d %H:%M:%S")
                await message.channel.send(outmessage)
        elif len(message.content.split(" ")) > 3 and command in bbdata.bountyFactions and message.content.split(" ")[2].lower() == "route":
            requestedBountyName = ""
            for section in message.content.split(" ")[3:]:
                requestedBountyName += " " + section.title()
            if len(requestedBountyName) > 0:
                requestedBountyName = requestedBountyName[1:]
            requestedFaction = command
            bountyFound = False
            for bounty in BBDB["bounties"][requestedFaction]:
                if bounty.name == requestedBountyName:
                    bountyFound = True
                    outmessage = requestedBountyName + "'s current routce:"
                    for system in bounty.route:
                        outmessage += " " + system + ","
                    outmessage = outmessage[:-1] + "."
                    await message.channel.send(outmessage)
            if (not bountyFound):
                await message.channel.send("That pilot is not on the " + requestedFaction + " bounty board!")
        elif command == "route":
            if len(message.content.split(" ")) <= 3 or "," not in message.content or len(message.content[10:message.content.index(",")]) < 1 or len(message.content[message.content.index(","):]) < 2:
                await message.channel.send("Please provide source and destination systems, separated with a comma and space.\nFor example: `!bb route Pescal Inartu, Loma`")
                return
            if message.content.count(",") > 1:
                await message.channel.send("Please only provide two systems!")
                return
            startSyst = message.content[10:].split(",")[0].title()
            endSyst = message.content[10:].split(",")[1][1:].title()
            for systArg in [startSyst, endSyst]:
                if systArg not in bbdata.systems:
                    if len(systArg) < 20:
                        await message.channel.send("The " + systArg + " system is not on my star map!")
                    else:
                        await message.channel.send("The " + systArg[0:15] + "... system is not on my star map!")
                    return
                if not bbdata.systems[systArg].hasJumpGate():
                    if len(systArg) < 20:
                        await message.channel.send("The " + systArg + " system does not have a jump gate!")
                    else:
                        await message.channel.send("The " + systArg[0:15] + "... system does not have a jump gate!")
                    return
            routeStr = ""
            for currentSyst in bbutil.bbAStar(startSyst, endSyst, bbdata.systems):
                routeStr += currentSyst + ", "
            if routeStr.startswith("#"):
                await message.channel.send(":x: ERR: Processing took too long! :stopwatch:")
            elif routeStr.startswith("!"):
                await message.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
            else:
                await message.channel.send("Here's the shortest route from " + startSyst + " to " + endSyst + ":\n> " + routeStr[:-2] + " :rocket:")
        elif command == "system-info":
            if len(message.content.split(" ")) < 3:
                await message.channel.send("Please provide a system! Example: `!bb system-info Augmenta`")
            systArg = message.content[16:].title()
            if systArg not in bbdata.systems:
                if len(systArg) < 20:
                    await message.channel.send("The " + systArg + " system is not on my star map!")
                else:
                    await message.channel.send("The " + systArg[0:15] + "... system is not on my star map!")
                return
            else:
                systObj = bbdata.systems[systArg]
                neighboursStr = ""
                for x in systObj.neighbours:
                    neighboursStr += x + ", "
                neighboursStr = neighboursStr[:-2]
                
                await message.channel.send("```xml\n<name " + systObj.name + ">\n"
                                            + "<faction " + systObj.faction + ">\n"
                                            + "<neighbours " + neighboursStr + ">\n"
                                            + "<security_level " + bbdata.securityLevels[systObj.security].title() + ">```")
        elif command == "leaderboard":
            inputDict = {}
            for userID in BBDB["users"]:
                inputDict[userID] = BBDB["users"][userID]["credits"]
            sortedUsers = sorted(inputDict.items(), key=operator.itemgetter(1))[::-1]
            outStr = "```--= CREDITS LEADERBOARD =--"
            for place in range(min(len(sortedUsers), 10)):
                outStr += "\n " + str(place + 1) + ". " + client.get_user(int(sortedUsers[place][0])).name + " - " + str(int(sortedUsers[place][1])) + " credits"
            outStr += "```"
            await message.channel.send(outStr)
        else:
            if message.author.id == 188618589102669826:
                if command == "s":
                    await message.channel.send("zzzz....")
                    bbconfig.botLoggedIn = False
                    await client.logout()
                    # bbutil.writeJDB("BBDB.json", BBDB)
                    saveDB(BBDB)
                elif command == "save":
                    saveDB(BBDB)
                    await message.channel.send("saved!")
                elif command == "setchannel":
                    bbconfig.sendChannel[str(message.guild.id)] = message.channel.id
                    await message.channel.send("Set!")
                elif command == "chset?":
                    await message.channel.send(str(message.guild.id) in bbconfig.sendChannel)
                elif command == "printch":
                    await message.channel.send(bbconfig.sendChannel[str(message.guild.id)])
                elif command == "stations":
                    await message.channel.send(bbdata.systems)
                elif command == "clear":
                    for fac in bbdata.bountyFactions:
                        BBDB["bounties"][fac] = []
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
                        BBDB["users"][str(client.get_user(int(message.content[17:-1])).id)]["bountyCooldownEnd"] = datetime.utcnow().timestamp()
                    await message.channel.send("Done!")
                elif command == "make-bounty":
                    if len(message.content.split(" ")) < 3:
                        newFaction = ""
                    else:
                        newFaction = message.content[16:]
                    newBounty = Bounty(faction=newFaction)
                    BBDB["bounties"][newBounty.faction].append(newBounty)
                    if str(message.guild.id) in bbconfig.sendChannel and bbconfig.sendChannel[str(message.guild.id)] != 0:
                        await client.get_channel(bbconfig.sendChannel[str(message.guild.id)]).send("New " + newBounty.faction + " bounty: " + newBounty.name)
                else:
                    await message.channel.send("""Can't do that, pilot. Type "!bb help" for a list of commands! o7""")
            else:
                await message.channel.send("""Can't do that, pilot. Type "!bb help" for a list of commands! o7""")
        
client.run(bbPRIVATE.botToken)
