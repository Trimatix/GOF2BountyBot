import random
from .bbObjects.items import bbInventoryListing

# TODO: Would it be possible to import this ore data from bbData rather than hard coding it?
ORE_TYPES = ["Iron Ore", "Doxtrite Ore", "Perrius Ore", "Cesogen Ore", "Hypanium Ore", "Gold Ore", "Sodil Ore", "Pyresium Ore", "Orichalzine Ore", "Titanium Ore", "Void Crystal"]
SCANNER_TIERS = {"Telta Quickscan": 1, "Telta Ecoscan": 2, "Hiroto Proscan": 3, "Hiroto Ultrascan": 4}
asteroid_tiers = ["D", "C", "B", "A", "S"]
risky_aliases = ["risk", "risky", "danger", "dangerous"]
safe_aliases = ["safe", "cautious"]
base_mining_failure_chance = 5
max_ore_per_asteroid_tier = [23, 34, 47, 62]


def pickOre(oreList=ORE_TYPES):
    return random.choice(oreList)


def pickTier(scanner):
    baseTier = random.randint(1,3)
    if scanner is not None:
        baseTier += int(SCANNER_TIERS[scanner.name])
    return int(baseTier)



def tierToLetter(tier):
    if tier < len(asteroid_tiers):
        return asteroid_tiers[tier-1]
    else:
        return asteroid_tiers[len(asteroid_tiers)-1]


def boolRiskArg(arg):
    return arg in risky_aliases


"""
gets result of mining attempt

@param drill -- type of drill being used
@param isRisky -- Choice of taking risk or not
@return -- returns ore type, amount, and if a core was obtained
"""
def mineResult(drill, tier):
    # TODO: move max_ore_per_asteroid_tier to bbConfig
    # fails if exceeds drill handling or doesn't meet minimum requirement
    miningFailed = False
    if base_mining_failure_chance > random.randint(1, 100) or random.randint(1, 100) > drill.handling*100:
        miningFailed = True

    if tier < len(max_ore_per_asteroid_tier):
        minedOre = int(max_ore_per_asteroid_tier[tier-1] * drill.oreYield)
    else:
        minedOre = int(max_ore_per_asteroid_tier[len(max_ore_per_asteroid_tier)-1] * drill.oreYield)

    if not miningFailed:
        if tier > 3:
            return minedOre, tier - 3
        return minedOre, 0

    minedOre = int(minedOre * drill.handling)
    # TODO: Variance should be percentage based
    variance = random.randint(-5, 5)
    return minedOre + variance, 0


def mineAsteroid(user, tier, oreObj, coreObj):
    if user.getDrill() is None:
        return "No drill equipped"
    else:
        results = mineResult(user.getDrill(), tier)
        oreQuantity = results[0]
        coreQuantity = int(results[1])

        remainingSpace = user.activeShip.getCargo() - user.commoditiesCollected
        if oreQuantity > remainingSpace:
            oreQuantity = remainingSpace
            if coreQuantity > 0:
                if oreQuantity >= coreQuantity:
                    oreQuantity -= coreQuantity
                else:
                    coreQuantity = oreQuantity
                    oreQuantity = 0

        minedOre = {oreObj: oreQuantity}

        user.addCommodity(oreObj, oreQuantity)
        if coreQuantity > 0:
            user.addCommodity(coreObj, coreQuantity)
            minedOre[coreObj] = coreQuantity

        return minedOre
