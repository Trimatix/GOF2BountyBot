import discord
from datetime import datetime, timedelta
import asyncio
import random
# from bbdata import System, factions, bountyNames, securityLevels, systems
import bbdata
import bbutil
import bbPRIVATE
import bbconfig


def initializeUser(userID):
    BBDB["users"][str(userID)] = {"credits":0, "bountyCooldown":0}


def makeRoute(start, end):
    return bbutil.bbAStar(start, end, bbdata.systems)


class Bounty:
    issueTime = -1
    name = ""
    route = []
    reward = 0.0
    endTime = -1
    faction = ""
    visited = {}
    answer = ""

    def __init__(self, faction="", issueTime=-1.0, name="", route=[], end="", answer="", reward=-1.0, endTime=-1.0, start=""):
        self.issueTime = issueTime
        self.name = name
        self.route = route
        self.reward = reward
        self.endTime = endTime
        self.faction = faction
        self.answer = answer

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
            self.name = random.choice(bbdata.bountyNames[faction])
        elif name not in bbdata.bountyNames:
            raise RuntimeError("Bounty constructor: Invalid name requested '" + name + "'")
        if reward == -1.0:
            self.reward = len(self.route) * 10
        elif reward < 0:
            raise RuntimeError("Bounty constructor: Invalid reward requested '" + str(reward) + "'")
        if issueTime == -1.0:
            self.issueTime = datetime.utcnow().timestamp()
        if endTime == -1.0:
            self.endTime = (self.issueTime + timedelta(days=len(self.route))).timestamp()
            
        for station in self.route:
            self.visited[station] = -1

    def check(self, system, userID):
        if system not in self.route:
            return 0
        elif self.systemChecked(system):
            return 1
        else:
            self.visited[system] = userID
            return self.visited

    def systemChecked(self, system):
        return self.visited[system] != -1

    def calcRewards(self):
        rewards = {}
        checkedSystems = 0
        for system in self.route:
            if self.systemChecked(system):
                checkedSystems += 1
                rewards[self.visited[system]] = {"reward":0,"checked":0,"won":False}

        uncheckedSystems = len(self.route) - checkedSystems

        for system in self.route:
            if self.systemChecked(system):
                if self.answer == system:
                    rewards[self.visited[system]]["reward"] += (self.reward / len(self.route)) * (uncheckedSystems + 1)
                    rewards[self.visited[system]]["checked"] += 1
                    rewards[self.visited[system]]["won"] = True
                else:
                    rewards[self.visited[system]]["reward"] += self.reward / len(self.route)
                    rewards[self.visited[system]]["checked"] += 1
        return rewards


def makeBounty(faction="", bountyName="", start="", end=""):
    if faction == "":
        faction = random.choice(bbdata.bountyFactions)
    if faction not in bbdata.bountyFactions:
        raise RuntimeError("makeBounty: Invalid faction requested '" + faction + "'")
    
    # route = random.choice(bbconfig.bountyRoutes)
    # if random.choice([True, False]):
    #     route = route[::-1]

    if start == "":
        start = random.choice(list(bbdata.systems.keys()))
        while start == end or not bbdata.systems[start].hasJumpGate():
            start = random.choice(list(bbdata.systems.keys()))
    if end == "":
        end = random.choice(list(bbdata.systems.keys()))
        while start == end or not bbdata.systems[end].hasJumpGate():
            end = random.choice(list(bbdata.systems.keys()))
    route = bbutil.bbAStar(start, end, bbdata.systems)

    if bountyName == "":
        bountyName = random.choice(bbdata.bountyNames[faction])
    reward = len(route) * 100
    issue = datetime.utcnow()
    due = issue + timedelta(days=len(route))
    return faction, {"issueTime": issue.timestamp(), "name": bountyName, "route": route, "answer": answer, "reward": reward, "endTime": due.timestamp()}


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


BBDB = bbutil.readJDB("BBDB.json")
client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    bbconfig.botLoggedIn = True
    while bbconfig.botLoggedIn:
        await asyncio.sleep(bbconfig.newBountyDelay)
        # Make new bounties
        if canMakeBounty():
            newFaction = random.choice(bbdata.bountyFactions)
            while len(BBDB["bounties"][newFaction]) >= bbconfig.maxBountiesPerFaction:
                newFaction = random.choice(bbdata.bountyFactions)
            newName = random.choice(bbdata.bountyNames[newFaction])
            while bountyNameExists(BBDB["bounties"][newFaction], newName): 
                newName = random.choice(bbdata.bountyNames[newFaction])
            newBounty = makeBounty(faction=newFaction, bountyName=newName)[1]
            BBDB["bounties"][newFaction].append(newBounty)
            if bbconfig.sendChannel != 0:
                await client.get_channel(bbconfig.sendChannel).send("New " + newFaction + " bounty: " + newName)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.split(" ")[0] == ('!bb'):
        if len(message.content.split(" ")) > 1:
            command = message.content.split(" ")[1].lower()
        else:
            command = "help"
        if command == 'hello':
            await message.channel.send('Hello!')
        elif command == "map":
            if len(message.content.split(" ")) > 2 and message.content.split(" ")[2] == "-g":
                await message.channel.send('https://cdn.discordapp.com/attachments/700683544103747594/700683693215318076/gof2_coords.png')
            else:
                await message.channel.send('https://cdn.discordapp.com/attachments/700683544103747594/700683699334807612/Gof2_supernova_map.png')
        elif command == "setchannel":
            bbconfig.sendChannel = message.channel.id
        elif command == "check":
            if str(message.author.id) not in BBDB["users"]:
                initializeUser(message.author.id)
            if datetime.utcfromtimestamp(BBDB["users"][str(message.author.id)]["bountyCooldownEnd"]) < datetime.utcnow():
                await message.channel.send("<@" + str(message.author.id) + ">, you now have " + str(BBDB["users"][str(message.author.id)]["credits"]) + " credits!")
        elif len(message.content.split(" ")) == 2 and command in bbdata.bountyFactions:
            requestedFaction = command
            if len(BBDB["bounties"][requestedFaction]) == 0:
                await message.channel.send("There are no " + requestedFaction + " bounties active currently!")
            else:
                outmessage = "active " + requestedFaction + " bounties:"
                for bounty in BBDB["bounties"][requestedFaction]:
                    outmessage += "\n - " + bounty["name"] + ": " + str(bounty["reward"]) + " credits, issued: " + datetime.utcfromtimestamp(bounty["issueTime"]).strftime("%B-%d %H:%M:%S") + ", ending: " + datetime.utcfromtimestamp(bounty["endTime"]).strftime("%B-%d %H:%M:%S")
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
                if bounty["name"] == requestedBountyName:
                    bountyFound = True
                    outmessage = requestedBountyName + "'s current route:"
                    for system in bounty["route"]:
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
            await message.channel.send("Here's the shortest route from " + startSyst + " to " + endSyst + ":\n> " + routeStr[:-2] + " :rocket:")
        else:
            if message.author.id == 188618589102669826:
                if command == "s":
                    bbconfig.botLoggedIn = False
                    await client.logout()
                    bbutil.writeJDB("BBDB.json", BBDB)
                elif command == "stations":
                    await message.channel.send(bbdata.systems)
                elif command == "clear":
                    for fac in bbdata.bountyFactions:
                        BBDB["bounties"][fac] = []
                elif command == "make-bounty":
                    if len(message.content.split(" ")) < 3:
                        newFaction = random.choice(bbdata.bountyFactions)
                        while len(BBDB["bounties"][newFaction]) >= bbconfig.maxBountiesPerFaction:
                            newFaction = random.choice(bbdata.bountyFactions)
                    else:
                        newFaction = message.content.split(" ")[2]
                    newName = random.choice(bbdata.bountyNames[newFaction])
                    while bountyNameExists(BBDB["bounties"][newFaction], newName): 
                        newName = random.choice(bbdata.bountyNames[newFaction])
                    newBounty = makeBounty(faction=newFaction, bountyName=newName)[1]
                    BBDB["bounties"][newFaction].append(newBounty)
                    if bbconfig.sendChannel != 0:
                        await client.get_channel(bbconfig.sendChannel).send("New " + newFaction + " bounty: " + newName)
                else:
                    await message.channel.send("""Can't do that, pilot. Type "!bb help" for a list of commands! o7""")
            else:
                await message.channel.send("""Can't do that, pilot. Type "!bb help" for a list of commands! o7""")
        
client.run(bbPRIVATE.botToken)
