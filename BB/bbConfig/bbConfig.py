# Coefficient used when calculating the rarity of item spawns in the shop.
# At the time of writing, the algorithm is rarity = itemRarityCoefficient ^ item cost
itemRarityCoefficient = 2

# Amount of time before a duel request expires
duelReqExpiryTime = {"days":1}
# duelReqExpiryTime as a user-friendly string for printing
duelReqExpiryTimeStr = "1 day"
# The amount to vary ship stats (+-) by before executing a duel
duelVariancePercent = 0.05

# Amount of time to wait between refreshing stock of all shops
shopRefreshStockPeriod = {"days":0, "hours":12, "minutes":0, "seconds":0}

maxBountiesPerFaction = 5

# can be "fixed" or "random"
newBountyDelayType = "random"

# only spawn bounties at this time
newBountyFixedDailyTime = {"hours":18, "minutes":40, "seconds":0}
# use the above, or just spawn after every newBountyFixedDelta
newBountyFixedUseDailyTime = False

# time to wait inbetween spawning bounties
newBountyFixedDelta = {"days":0, "hours":0, "minutes":40, "seconds":0}

# when using random delay generation, use this as the minimum wait time in seconds
newBountyDelayMin = 15 * 60
# when using random delay generation, use this as the maximum wait time in seconds
newBountyDelayMax = 1 * 60 * 60


# The time to wait inbetween database autosaves.
savePeriod = {"hours":1}


# Whether to execute timedtask checks every timedTaskLatenessThresholdSeconds ("fixed"), or to calculate the delay to wait until the next TimedTask is schedule to expire ("dynamic")
timedTaskCheckingType = "fixed"

# How late a timed task acceptably be
# I.e a scheduled task may expire up to timedTaskLatenessThresholdSeconds seconds after their intended expiration time.
# replaces the depracated 'delayFactor' variable
timedTaskLatenessThresholdSeconds = 10

# The number of credits to award for each bPoint (each system in a criminal route)
bPointsToCreditsRatio = 1000

# max number of messages to wait before sending random !drink
randomDrinkFactor = 500
# wait time for initial period
randomDrinkNum = int(randomDrinkFactor / 3)

# time to put users on cooldown between using !bb check
checkCooldown = {"minutes":3}

# path to JSON files for database saves
userDBPath = "saveData/users.json"
guildDBPath = "saveData/guilds.json"
bountyDBPath = "saveData/bounties.json"

# prefix for bot commands. dont forget a space!
commandPrefix = "$"

# discord user IDs of all developers
developers = [188618589102669826, 448491245296418817]

# number of bounties ahead of a checked system in a route to report a recent criminal spotting (+1)
closeBountyThreshold = 4

# titles to give each type of user when reporting error messages etc
devTitle = "officer"
adminTitle = "commander"
userTitle = "pilot"

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

# The maximum number of items that will be displayed per page of a user's hangar, when all item types are requested
maxItemsPerHangarPageAll = 3
# The maximum number of items that will be displayed per page of a user's hangar, when a single item type is requested
maxItemsPerHangarPageIndividual = 5

# Names to be used when checking input to !bb hangar and bbUser.numInventoryPages
validItemNames = ["ship", "weapon", "module", "turret", "all"]

# When a user message prompts a DM to be sent, this emoji will be added to the message reactions.
dmSentEmoji = "📬"

# max number of characters accepted by nameShip
maxShipNickLength = 30

# Do not touch these!
newBountyDelayReset = False
newBountyFixedDeltaChanged = False

# Max number of entries that can be printed for a duel log
duelLogMaxLength = 10

# Percentage probability of a user envoking a cloak module in a given timeStep, should they have one equipped
duelCloakChance = 20

# Servers where bountyBot commands are disabled. Currently this is just the emoji servers:
disabledServers = [723704980246233219, 723702782640783361, 723708988830515231, 723704665560055848, 723705817764986900, 723703454635393056, 723708655031156742, 723706906517962814, 723704087962583131, 723704350131748935]

# the max number of each module type that can be equipped on a ship. This variable is now located in bbObjects.items.bbModuleFactory
# maxModuleTypeEquips = {...}