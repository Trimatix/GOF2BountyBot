from ..bbObjects import bbGuild

"""
A database of bbGuilds.

"""
class bbGuildDB:
    def __init__(self):
        # Store guilds as a dict of guild.id: guild
        self.guilds = {}


    """
    Get a list of all guild IDs in the database.

    @return -- A list containing all guild IDs (ints) stored in the database.
    """
    def getIDs(self):
        return list(self.guilds.keys())


    """
    Get a list of all bbGuilds in the database.

    @return -- A list containing all bbGuild objects stored in the database
    """
    def getGuilds(self):
        return list(self.guilds.values())


    """
    Get the bbGuild object with the specified ID.

    @param id -- integer discord ID for the requested guild
    @return -- bbGuild having the requested ID
    """
    def getGuild(self, id):
        return self.guilds[id]


    """
    Check whether a bbGuild with a given ID exists in the database.

    @param id -- integer discord ID to check for existence
    @return -- True if a bbGuild is stored in the database with the requested ID, False otherwise
    """
    def guildIdExists(self, id):
        # Search the DB for the requested ID
        try:
            self.getGuild(id)
        # No bbGuild found, return False
        except KeyError:
            return False
        # Return True otherwise
        return True

    
    """
    Check whether a bbGuild object exists in the database.
    Existence checking is currently handled by checking if a guild with the requested ID is stored.

    @param guild -- bbGuild object to check for existence
    @return -- True if the exact bbGuild exists in the DB, False otherwise
    """
    def guildObjExists(self, guild):
        return self.guildIdExists(guild.id)


    """
    Add a given bbGuild object to the database.

    @param guild -- the bbGuild object to store
    @throws KeyError - If the the guild is already in the database
    """
    def addGuildObj(self, guild):
        # Ensure guild is not yet in the database
        if self.guildObjExists(guild):
            raise KeyError("Attempted to add a guild that already exists: " + guild.id)
        self.guilds[guild.id] = guild

    
    """
    Add a bbGuild object with the requested ID to the database

    @param id -- integer discord ID to create and store a bbGuild for
    @throws KeyError -- If a bbGuild is already stored for the requested ID
    @return -- the new bbGuild object
    """
    def addGuildID(self, id):
        # Ensure the requested ID does not yet exist in the database
        if self.guildIdExists(id):
            raise KeyError("Attempted to add a guild that already exists: " + id)
        # Create and return a bbGuild for the requested ID
        self.guilds[id] = bbGuild.bbGuild(id)
        return self.guilds[id]

    
    """
    Remove the bbGuild with the requested ID from the database.

    @param id -- integer discord ID to remove from the database
    """
    def removeGuildId(self, id):
        self.guilds.pop(id)


    """
    Remove the given bbGuild object from the database
    Currently removes any bbGuild sharing the given guild's ID, even if it is a different object.

    @param guild -- the guild object to remove from the database
    """
    def removeGuildObj(self, guild):
        self.removeGuildId(guild.id)

    
    """
    Generate new stock for all shops belonging to the stored bbGuilds

    """
    def refreshAllShopStocks(self):
        for guild in self.guilds.values():
            guild.shop.refreshStock()

    
    """
    Serialise this bbGuildDB into dictionary format

    @return -- A dictionary containing all data needed to recreate this bbGuildDB
    """
    def toDict(self):
        data = {}
        # Iterate over all stored guilds
        for guild in self.getGuilds():
            # Serialise and then store each guild
            # JSON stores properties as strings, so ids must be converted to str first.
            data[str(guild.id)] = guild.toDictNoId()
        return data


    """
    Fetch summarising information about the database, as a string
    Currently only the number of guilds stored

    @return -- A string summarising this db
    """
    def __str__(self):
        return "<bbGuildDB: " + str(len(self.guilds)) + " guilds>"


"""
Construct a bbGuildDB object from dictionary-serialised format; the reverse of bbGuildDB.todict()

@param bountyDBDict -- The dictionary representation of the bbGuildDB to create
@return -- The new bbGuildDB
"""
def fromDict(bountyDBDict):
    # Instance the new bbGuildDB
    newDB = bbGuildDB()
    # Iterate over all IDs to add to the DB
    for id in bountyDBDict.keys():
        # Instance new bbGuilds for each ID, with the provided data
        # JSON stores properties as strings, so ids must be converted to int first.
        newDB.addGuildObj(bbGuild.fromDict(int(id), bountyDBDict[id]))
    return newDB
