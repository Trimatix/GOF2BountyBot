# Amount of time to wait between refreshing stock of all shops
shopRefreshStockPeriod = {"days":1, "hours":0, "minutes":0, "seconds":0}

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

"""
# DEPRECATED
# the number of seconds to wait in between each save
saveDelay = 30 * 60
"""

# The time to wait inbetween database autosaves.
savePeriod = {"hours":1}


"""
# DEPRACATED
# the number of seconds to wait before checking if a delay time is passed. should be a factor all delays given.
delayFactor = 5
"""

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
developers = [188618589102669826]

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
turretSpawnProbability = 33

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