# Discord
client = None
botLoggedIn = False


# Databases
usersDB = None
guildsDB = None


# Timed tasks
escapedBountiesRespawnTTDB = None
newBountiesTTDB = None

shopRefreshTT = None
dbSaveTT = None

duelRequestTTDB = None


# Reaction Menus
reactionMenusDB = None
reactionMenusTTDB = None


# Scheduling overrides
newBountyFixedDeltaChanged = False


# Names of ships currently being rendered
currentRenders = []

shutdown = False