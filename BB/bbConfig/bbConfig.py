import math, random, pprint
from ..bbUtil import dumbEmoji

##### UTIL #####

# Number of decimal places to calculate itemTLSpawnChanceForShopTL values to
tl_resolution = 3

def truncToRes(num):
    return math.trunc(num * math.pow(10, tl_resolution)) / math.pow(10, tl_resolution)



##### DUELS #####

# Amount of time before a duel request expires
duelReqExpiryTime = {"days":1}
# duelReqExpiryTime as a user-friendly string for printing
duelReqExpiryTimeStr = "1 day"
# The amount to vary ship stats (+-) by before executing a duel
duelVariancePercent = 0.05

# Max number of entries that can be printed for a duel log
duelLogMaxLength = 10

# Percentage probability of a user envoking a cloak module in a given timeStep, should they have one equipped
duelCloakChance = 20



##### SHOPS #####

# Amount of time to wait between refreshing stock of all shops
shopRefreshStockPeriod = {"days":0, "hours":0, "minutes":15, "seconds":0}

# The number of ranks to use when randomly picking shop stock
numShipRanks = 10
numWeaponRanks = 10
numModuleRanks = 7
numTurretRanks = 3

# The default number of items shops should generate every shopRefreshStockPeriod
shopDefaultShipsNum = 5
shopDefaultWeaponsNum = 5
shopDefaultModulesNum = 5
shopDefaultTurretsNum = 2

# bbTurret is the only item that has a probability not to be spawned. This metric indicates the percentage chance of turrets being stocked on a given day
turretSpawnProbability = 45

# The range of valid tech levels a shop may spawn at
minTechLevel = 1
maxTechLevel = 10

# The probability of a shop spawning with a given tech level. Tech level = index + 1
cumulativeShopTLChance = [0 for tl in range(minTechLevel, maxTechLevel + 1)]
shopTLChance = [0 for tl in range(minTechLevel, maxTechLevel + 1)]

itemChanceSum = 0

# Calculate spawn chance for each shop TL
for shopTL in range(minTechLevel, maxTechLevel + 1):
    itemChance = truncToRes(1 - math.exp((shopTL - 10.5) / 5))
    cumulativeShopTLChance[shopTL - 1] = itemChance
    itemChanceSum += itemChance

# Scale shop TL probabilities so that they add up to 1
for shopTL in range(minTechLevel, maxTechLevel + 1):
    currentChance = cumulativeShopTLChance[shopTL - 1]
    if currentChance != 0:
        cumulativeShopTLChance[shopTL - 1] = truncToRes(currentChance / itemChanceSum)

# Save non-cumulative probabilities
for i in range(len(cumulativeShopTLChance)):
    shopTLChance[i] = cumulativeShopTLChance

# Sum probabilities to give cumulative scale
currentSum = 0
for shopTL in range(minTechLevel, maxTechLevel + 1):
    currentChance = cumulativeShopTLChance[shopTL - 1]
    if currentChance != 0:
        cumulativeShopTLChance[shopTL - 1] = truncToRes(currentSum + currentChance)
        currentSum += currentChance


def pickRandomShopTL():
    tlChance = random.randint(1, 10 ** tl_resolution) / 10 ** tl_resolution
    for shopTL in range(len(cumulativeShopTLChance)):
        if cumulativeShopTLChance[shopTL] >= tlChance:
            return shopTL + 1
    return maxTechLevel

# Price ranges by which ships should be ranked into tech levels. 0th index = tech level 1
shipMaxPriceTechLevels = [50000, 100000, 200000, 500000, 1000000, 2000000, 5000000, 7000000, 7500000, 999999999]

# CUMULATIVE probabilities of items of a given tech level spawning in a shop of a given tech level
# Outer dimension is shop tech level
# Inner dimension is item tech level
itemTLSpawnChanceForShopTL = [[0 for i in range(minTechLevel, maxTechLevel + 1)] for i in range(minTechLevel, maxTechLevel + 1)]
cumulativeItemTLSpawnChanceForShopTL = [[0 for i in range(minTechLevel, maxTechLevel + 1)] for i in range(minTechLevel, maxTechLevel + 1)]

# Parameters for itemTLSpawnChanceForShopTL values, using quadratic function: https://www.desmos.com/calculator/n2xfxf8taj
# u function: https://www.desmos.com/calculator/orct5tkn9x
# Original u function by Novahkiin22: https://www.desmos.com/calculator/tnldodey5u
# Original function by Novahkiin22: https://www.desmos.com/calculator/nrshikfmxc
tl_s = 7
tl_o = 2.3

"""def tl_u(x, t):
    h = t - tl_s
    tl_n = (x - tl_o - h) / tl_s
    mid = tl_n * (1 - math.pow(tl_n, 4))
    outer = tl_s * mid - (h / 2)
    return truncToRes(outer if outer > 0 else 0)"""

def tl_u(x, t):
    chance = truncToRes(1 - math.pow((x - t)/1.4,2))
    return chance if chance > 0 else 0

# Loop through shop TLs
for shopTL in range(minTechLevel, maxTechLevel + 1):
    tl_h = shopTL - tl_s
    itemChanceSum = 0

    # Calculate spawn chance for each item TL in this shop TL
    for itemTL in range(minTechLevel, maxTechLevel + 1):
        itemChance = tl_u(itemTL, shopTL)
        cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1] = itemChance
        itemChanceSum += itemChance
    
    # Scale item TLs so that they add up to 1
    for itemTL in range(minTechLevel, maxTechLevel + 1):
        currentChance = cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1]
        if currentChance != 0:
            cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1] = truncToRes(currentChance / itemChanceSum)

    # Save non-cumulative probabilities
    for i in range(len(cumulativeItemTLSpawnChanceForShopTL[shopTL - 1])):
        itemTLSpawnChanceForShopTL[shopTL - 1][i] = cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][i]

    # Sum probabilities to give cumulative scale
    currentSum = 0
    for itemTL in range(minTechLevel, maxTechLevel + 1):
        currentChance = cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1]
        if currentChance != 0:
            cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL - 1] = truncToRes(currentSum + currentChance)
            currentSum += currentChance

print("[bbConfig] Item rarities generated:")
for shopTL in range(len(itemTLSpawnChanceForShopTL)):
    print("\t• shop TL" + str(shopTL+1) + ": itemTL",end="")
    for itemTL in range(len((itemTLSpawnChanceForShopTL[shopTL]))):
        if itemTLSpawnChanceForShopTL[shopTL][itemTL] != 0:
            print(" " + str(itemTL + 1) + "=" + str(truncToRes(itemTLSpawnChanceForShopTL[shopTL][itemTL]*100)),end="% ")
    print()


def pickRandomItemTL(shopTL):
    tlChance = random.randint(1, 10 ** tl_resolution) / 10 ** tl_resolution
    for itemTL in range(len(cumulativeItemTLSpawnChanceForShopTL[shopTL - 1])):
        if cumulativeItemTLSpawnChanceForShopTL[shopTL - 1][itemTL] >= tlChance:
            return itemTL + 1
    return maxTechLevel



##### BOUNTIES #####

maxBountiesPerFaction = 5

# The maximum number of bounties a player is allowed to win each day
maxDailyBountyWins = 10

# can be "fixed" or "random"
newBountyDelayType = "random-routeScale"

### fixed delay config
# only spawn bounties at this time
newBountyFixedDailyTime = {"hours":18, "minutes":40, "seconds":0}
# use the above, or just spawn after every newBountyFixedDelta
newBountyFixedUseDailyTime = False

# time to wait inbetween spawning bounties
# when using fixed-routeScale generation, use this for bounties of route length 1
newBountyFixedDelta = {"days":0, "hours":0, "minutes":1, "seconds":0}

### random delay config
# when using random delay generation, use these min and max points
# when using random-routeScale generation, use these min and max points for bounties of route length 1
newBountyDelayRandomRange = {"min": 5 * 60, "max": 7 * 60}

### routeScale config
newBountyDelayRouteScaleCoefficient = 1
fallbackRouteScale = 5


# The number of credits to award for each bPoint (each system in a criminal route)
bPointsToCreditsRatio = 1000

# The percentage of a criminal's ship value to award to the winner
shipValueRewardPercentage = 0.05

# time to put users on cooldown between using !bb check
checkCooldown = {"minutes":3}

# number of bounties ahead of a checked system in a route to report a recent criminal spotting (+1)
closeBountyThreshold = 4

# The probability of a criminal equipping a turret, should their ship have space for one
criminalEquipTurretChance = 30

# The maximum total-value a player may have before being disallowed from hunting a tech-level of bounty. 0th index = tech level 1
# I.e, to hunt level 1 bounties, a player must be worth no more than bountyTLMaxPlayerValues[0] credits.
bountyTLMaxPlayerValues = [50000, 75000, 100000, 200000, 450000, 600000, 800000, 1000000, 2000000, 3000000, 999999999]

# The probability of a shop spawning with a given tech level. Tech level = index + 1
cumulativeCriminalTLChance = [0 for tl in range(minTechLevel-1, maxTechLevel + 1)]
criminalTLChance = [0 for tl in range(minTechLevel-1, maxTechLevel + 1)]

itemChanceSum = 0



# Calculate spawn chance for each criminal TL
for criminalTL in range(minTechLevel-1, maxTechLevel + 1):
    itemChance = truncToRes(1 - math.exp((criminalTL - 10.5) / 5))
    cumulativeCriminalTLChance[criminalTL - 1] = itemChance
    itemChanceSum += itemChance

# Scale criminal TL probabilities so that they add up to 1
for criminalTL in range(minTechLevel-1, maxTechLevel + 1):
    currentChance = cumulativeCriminalTLChance[criminalTL - 1]
    if currentChance != 0:
        cumulativeCriminalTLChance[criminalTL - 1] = truncToRes(currentChance / itemChanceSum)

# Save non-cumulative probabilities
for i in range(len(cumulativeCriminalTLChance)):
    criminalTLChance[i] = cumulativeCriminalTLChance

# Sum probabilities to give cumulative scale
currentSum = 0
for criminalTL in range(minTechLevel-1, maxTechLevel + 1):
    currentChance = cumulativeCriminalTLChance[criminalTL - 1]
    if currentChance != 0:
        cumulativeCriminalTLChance[criminalTL - 1] = truncToRes(currentSum + currentChance)
        currentSum += currentChance

def pickRandomCriminalTL():
    tlChance = random.randint(1, 10 ** tl_resolution) / 10 ** tl_resolution
    for criminalTL in range(len(cumulativeCriminalTLChance)):
        if cumulativeCriminalTLChance[criminalTL] >= tlChance:
            return criminalTL
    return maxTechLevel
    
# Text to send to a BountyBoardChannel when no bounties are currently active
bbcNoBountiesMsg = "```css\n[ NO ACTIVE BOUNTIES ]\n\nThere are currently no active bounty listings.\nPlease check back later, or use [ $notify bounties ] to be pinged when new ones become available!\n```"

level0CrimLoadout = {"name": "Betty", "builtIn":True,
                    "weapons":[{"name": "Nirai Impulse EX 1", "builtIn": True}],
                    "modules":[{"name": "Telta Quickscan", "builtIn": True}, {"name": "ZMI Optistore", "builtIn": True}, {"name": "IMT Extract 2.7", "builtIn": True}]}



##### SAVING #####

# The time to wait inbetween database autosaves.
savePeriod = {"hours":1}

# path to JSON files for database saves
userDBPath = "saveData/users.json"
guildDBPath = "saveData/guilds.json"
bountyDBPath = "saveData/bounties.json"
reactionMenusDBPath = "saveData/reactionMenus.json"

# path to folder to save log txts to
loggingFolderPath = "saveData/logs"



##### SCHEDULING #####

# Whether to execute timedtask checks every timedTaskLatenessThresholdSeconds ("fixed"), or to calculate the delay to wait until the next TimedTask is schedule to expire ("dynamic")
timedTaskCheckingType = "fixed"

# How late a timed task may acceptably be in seconds.
# I.e a scheduled task may expire up to timedTaskLatenessThresholdSeconds seconds after their intended expiration time.
# replaces the depracated 'delayFactor' variable
timedTaskLatenessThresholdSeconds = 10



##### MISC #####

# prefix for bot commands. dont forget a space if you want one!
commandPrefix = "$"

# When a user message prompts a DM to be sent, this emoji will be added to the message reactions.
dmSentEmoji = dumbEmoji(unicode="📬")

# max number of characters accepted by nameShip
maxShipNickLength = 30

# max number of characters accepted by nameShip, when called by a developer
maxDevShipNickLength = 100

# The default emojis to list in a reaction menu
numberEmojis = [dumbEmoji(unicode="0️⃣"), dumbEmoji(unicode="1️⃣"), dumbEmoji(unicode="2️⃣"), dumbEmoji(unicode="3️⃣"), dumbEmoji(unicode="4️⃣"), dumbEmoji(unicode="5️⃣"), dumbEmoji(unicode="6️⃣"), dumbEmoji(unicode="7️⃣"), dumbEmoji(unicode="8️⃣"), dumbEmoji(unicode="9️⃣"), dumbEmoji(unicode="🔟")]
defaultMenuEmojis = numberEmojis
defaultCancelEmoji = dumbEmoji(unicode="🇽")
defaultErrEmoji = dumbEmoji(unicode="❓")
defaultAcceptEmoji = dumbEmoji(unicode="👍")
defaultRejectEmoji = dumbEmoji(unicode="👎")



##### ADMINISTRATION #####

# discord user IDs of all developers
developers = [188618589102669826, 448491245296418817]

# titles to give each type of user when reporting error messages etc
devTitle = "officer"
adminTitle = "commander"
userTitle = "pilot"

# Servers where bountyBot commands are disabled. Currently this is just the emoji servers:
disabledServers = [723704980246233219, 723702782640783361, 723708988830515231, 723704665560055848, 723705817764986900, 723703454635393056, 723708655031156742, 723706906517962814, 723704087962583131, 723704350131748935]



##### HANGARS #####

# The maximum number of items that will be displayed per page of a user's hangar, when all item types are requested
maxItemsPerHangarPageAll = 3
# The maximum number of items that will be displayed per page of a user's hangar, when a single item type is requested
maxItemsPerHangarPageIndividual = 5

# Names to be used when checking input to !bb hangar and bbUser.numInventoryPages
validItemNames = ["ship", "weapon", "module", "turret", "all"]



##### USERS #####

userAlertsIDsDefaults = {   "bounties_new": False,
    
                            "shop_refresh": False,

                            "duels_challenge_incoming_new": True,
                            "duels_challenge_incoming_cancel": False,
                            
                            "system_updates_major": False,
                            "system_updates_minor": False,
                            "system_misc": False}



##### REACTION MENUS #####

roleMenuDefaultTimeout = {"days": 1}
duelChallengeMenuDefaultTimeout = {"hours": 2}
pollMenuDefaultTimeout = {"hours": 2}
expiredMenuMsg = "😴 This role menu has now expired."
pollMenuResultsBarLength = 10



##### INTERNAL #####
# Do not touch these!
newBountyDelayReset = False
newBountyFixedDeltaChanged = False
