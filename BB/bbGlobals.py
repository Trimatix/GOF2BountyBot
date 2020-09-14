# Discord
client = None
botLoggedIn = False


# Databases
usersDB = None
bountiesDB = None
guildsDB = None


# Timed tasks
newBountyTT = None

shopRefreshTT = None
dbSaveTT = None

duelRequestTTDB = None


# Reaction Menus
reactionMenusDB = None
reactionMenusTTDB = None


# Scheduling overrides
newBountyDelayReset = False
newBountyFixedDeltaChanged = False