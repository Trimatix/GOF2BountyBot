import random

from BB.bbConfig import bbData
from BB.bountybot import usersDB, bbCommands

# TODO: add delay between mining attempts
# TODO: add functions to users: getDrill, addCommodity
# TODO: add data to user: defaultMineRisky, Commodities

ORE_TYPES = {"Iron", "Doxtrite", "Perrius", "Cesogen", "Hypanium", "Golden", "Sodil", "Pyresium", "Orichalzine", "Titanium"}

def pickOre():
    numAsteroids = len(ORE_TYPES)
    choice = random.random() % numAsteroids
    return ORE_TYPES[int(choice)]

def pickTier():
    return int(random.random() % 4) + 1

def tierToLetter(tier):
    if tier == 1:
        return "D"
    if tier == 2:
        return "C"
    if tier == 3:
        return "B"
    if tier == 4:
        return "A"

def boolRiskArg(arg):
    if arg.lower() == "risk" or "risky" or "danger" or "dangerous":
        return True
    return False

"""
gets result of mining attempt

@param drill -- type of drill being used
@param isRisky -- Choice of taking risk or not
@return -- returns ore type, amount, and if a core was obtained
"""

def mineResult(drill, isRisky, tier):
    if isRisky:
        if 5 > (random.random() % 100) > drill.handling:
            return 0, 0
    tierValue = [62, 47, 34, 23]
    minedOre = tierValue[tier] * drill.efficiency / 100
    if isRisky:
        if tier == 4:
            return minedOre, True
        return minedOre, False
    minedOre = minedOre * drill.handling / 100
    variance = (random.random() % 10) - 5
    return minedOre + variance, False

def mineAsteroid(user, tier, oreType, isRisky):
    returnMessage = ""
    if user.getDrill() is not None:
        results = mineResult(user.getDrill(), isRisky, tier)
        oreQuantity = results[0]
        gotCore = results[1]
        user.addCommodity(oreType, oreQuantity)
        if oreQuantity > 0:
            returnMessage += ("You mined a class " + tierToLetter(tier) + " " + str(oreType) + " asteroid yielding " + str(oreQuantity) + " ore")
            if gotCore:
                user.Commodity(str(oreType) + " Core", 1)
                returnMessage += " and 1 core"
        else:
            returnMessage = "Asteroid mining failed"
    else:
        returnMessage = "No drill equipped"
    return returnMessage

def setRisky(message, isRisky):
    usersDB.getUser(message.author.id).defaultMineRisky = isRisky
    return

async def cmd_setRisk(message, args):
    user = usersDB.getUser(message.author.id)
    arg = args[0]
    if arg.lower() is not "risky" or "dangerous" or "safe" or "cautious":
        message.channel.send("Please enter valid option")
        message.channel.send("valid options are \"risky\" \"dangerous\" \"safe\" or \"cautious\"")
    elif arg.lower() == "risky" or "dangerous":
        user.defaultMineRisky = True
    else:
        user.defaultMineRisky = False

bbCommands.register("setMineRisk", cmd_setRisk)
bbCommands.register("setRisk", cmd_setRisk)

async def cmd_mining(message, args):
    user = usersDB.getUser(message.author.id)
    tier = pickTier()
    oreType = pickOre()
    if args[0] is not None:
        risk = args[0]
        if risk.lower() == "risk" or "risky":
            isRisky = True
        else:
            isRisky = False
    else:
        isRisky = user.defaultMineRisky
    sendMessage = mineAsteroid(user, tier, oreType, isRisky)
    message.channel.send(sendMessage)

bbCommands.register("mine", cmd_mining)
