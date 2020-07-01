import random

# TODO: Would it be possible to import this ore data from bbData rather than hard coding it?
#       the only issue is that void and novanium would be in the data, even though mining those would have prereqs
ORE_TYPES = ["Iron Ore", "Doxtrite Ore", "Perrius Ore", "Cesogen Ore", "Hypanium Ore", "Gold Ore", "Sodil Ore", "Pyresium Ore", "Orichalzine Ore", "Titanium Ore",]
asteroid_tiers = ["D", "C", "B", "A"]
risky_aliases = ["risk", "risky", "danger", "dangerous"]
safe_aliases = ["safe", "cautious"]
risky_mining_failure_chance = 5
max_ore_per_asteroid_tier = [23, 34, 47, 62]


def pickOre(oreList=ORE_TYPES):
    return random.choice(oreList)


def pickTier():
    return random.randint(1,4)


def tierToLetter(tier):
    return asteroid_tiers[tier-1]


def boolRiskArg(arg):
    return arg in risky_aliases


"""
gets result of mining attempt

@param drill -- type of drill being used
@param isRisky -- Choice of taking risk or not
@return -- returns ore type, amount, and if a core was obtained
"""
def mineResult(drill, isRisky, tier):
    # TODO: move max_ore_per_asteroid_tier to bbConfig
    # fails if exceeds drill handling or doesn't meet minimum requirement
    if isRisky and (risky_mining_failure_chance > random.randint(1,100) or random.randint(1,100) > drill.handling*100):
        return 0, 0

    minedOre = max_ore_per_asteroid_tier[tier-1] * drill.oreYield

    if isRisky:
        if tier == 4:
            return int(minedOre), True
        return int(minedOre), False

    minedOre = minedOre * drill.handling
    variance = random.randint(-5, 5)
    return int(minedOre + variance), False


def mineAsteroid(user, tier, oreType, isRisky, oreObj, coreObj):
    if user.getDrill() is None:
        return "No drill equipped"
    else:
        returnMessage = ""
        results = mineResult(user.getDrill(), isRisky, tier)
        oreQuantity = results[0]
        gotCore = results[1]
        user.addCommodity(oreObj, oreQuantity)
        remainingSpace = user.activeShip.cargo - user.commoditiesCollected
        if oreQuantity > remainingSpace:
            oreQuantity = remainingSpace
            if gotCore:
                oreQuantity -= 1
        if oreQuantity > 0:
            returnMessage += ("You mined a class " + tierToLetter(tier) + " " + oreType + " asteroid yielding " + str(oreQuantity) + " ore")
            if gotCore:
                user.addCommodity(coreObj, 1)
                returnMessage += " and 1 core"
        else:
            returnMessage = "Asteroid mining failed"
        return returnMessage
