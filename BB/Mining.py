import random

from BB.bbConfig import bbData
from BB.bountybot import usersDB, bbCommands

# TODO: add delay between mining attempts

ORE_TYPES = ["Iron", "Doxtrite", "Perrius", "Cesogen", "Hypanium", "Golden", "Sodil", "Pyresium", "Orichalzine", "Titanium"]

def pickOre(oreList=ORE_TYPES):
    numAsteroids = len(oreList)
    choice = random.random() % numAsteroids
    return oreList[int(choice)]

def pickTier():
    return random.randint(1,4)

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
        # TODO: remove magic 5 with value in bbConfig
        # fails if exceeds drill handling or doesn't meet minimum requirement
        if 5 > random.randint(0,100) > (drill.handling*100):
            return 0, 0
    tierValue = [62, 47, 34, 23]
    minedOre = tierValue[tier] * drill.oreYield
    if isRisky:
        if tier == 4:
            return minedOre, True
        return minedOre, False
    minedOre = minedOre * drill.handling
    variance = (random.random() % 10) - 5
    return minedOre + variance, False

def mineAsteroid(user, tier, oreType, isRisky):
    returnMessage = ""
    if user.getDrill() is not None:
        results = mineResult(user.getDrill(), isRisky, tier)
        oreQuantity = results[0]
        gotCore = results[1]
        user.addCommodity(oreType, oreQuantity)
        remainingSpace = user.activeShip.cargo - user.commoditiesCollected
        if oreQuantity > remainingSpace:
            oreQuantity = remainingSpace
            if gotCore:
                oreQuantity -= 1
        if oreQuantity > 0:
            returnMessage += ("You mined a class " + tierToLetter(tier) + " " + str(oreType) + " asteroid yielding " + str(oreQuantity) + " ore")
            if gotCore:
                user.commodity(str(oreType) + " Core", 1)
                returnMessage += " and 1 core"
        else:
            returnMessage = "Asteroid mining failed"
    else:
        returnMessage = "No drill equipped"
    return returnMessage

def setRisky(message, isRisky):
    usersDB.getUser(message.author.id).defaultMineIsRisky = isRisky
    return

async def cmd_setRisk(message, args):
    user = usersDB.getUser(message.author.id)
    argsSplit = args.split(" ")
    arg = argsSplit[0]
    if arg.lower() is not "risky" or "dangerous" or "safe" or "cautious":
        message.channel.send("Please enter valid option")
        message.channel.send("valid options are \"risky\" \"dangerous\" \"safe\" or \"cautious\"")
    elif arg.lower() == "risky" or "dangerous":
        user.defaultMineIsRisky = True
    else:
        user.defaultMineIsRisky = False

bbCommands.register("setMineRisk", cmd_setRisk)
bbCommands.register("setRisk", cmd_setRisk)

async def cmd_mining(message, args):
    argsSplit = args.split(" ")
    user = usersDB.getUser(message.author.id)
    if user.commoditiesCollected >= user.activeShip.cargo:
        message.channel.send("You have exceeded your ship's cargo capacity")
    tier = pickTier()
    oreType = pickOre()
    if argsSplit[0] is not None:
        risk = argsSplit[0]
        if risk.lower() == "risk" or "risky":
            isRisky = True
        else:
            isRisky = False
    else:
        isRisky = user.defaultMineIsRisky
    sendMessage = mineAsteroid(user, tier, oreType, isRisky)
    message.channel.send(sendMessage)

bbCommands.register("mine", cmd_mining)
