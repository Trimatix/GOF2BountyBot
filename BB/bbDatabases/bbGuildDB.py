from ..bbObjects import bbGuild
from typing import List


class bbGuildDB:
    """A database of bbGuilds.
    
    . . .

    Attributes
    ----------
    guilds : dict
        Dictionary of guild.id to guild, where guild is a bbGuild

    Methods
    -------
    getIDs()
        Get a list of all guild IDs in the database.
    getGuilds()
        Get a list of all bbGuilds in the database.
    getGuild(id)
        Get the bbGuild object with the specified ID.
    guildIdExists(id)
        Check whether a bbGuild with a given ID exists in the database.
    guildObjExists(guild)
        Check whether a bbGuild object exists in the database.
        Existence checking is currently handled by checking if a guild with the requested ID is stored.
    addGuildObj(guild)
        Add a given bbGuild object to the database.
    addGuildID(id)
        Add a bbGuild object with the requested ID to the database
    removeGuildId(id)
        Remove the bbGuild with the requested ID from the database.
    removeGuildObj(guild)
        Remove the given bbGuild object from the database
        Currently removes any bbGuild sharing the given guild's ID, even if it is a different object.
    refreshAllShopStocks()
        Generate new stock for all shops belonging to the stored bbGuilds
    toDict()
        Serialise this bbGuildDB into dictionary format
    __str__()
        Fetch summarising information about the database, as a string
        Currently only the number of guilds stored
    """

    def __init__(self):
        # Store guilds as a dict of guild.id: guild
        self.guilds = {}


    
    def getIDs(self) -> List[int]:
        """Get a list of all guild IDs in the database.

        Returns
        -------
        list
            A list containing all guild IDs (ints) stored in the database.
        """
        return list(self.guilds.keys())


    
    def getGuilds(self) -> List[bbGuild.bbGuild]:
        """Get a list of all bbGuilds in the database.

        Returns
        -------
        list
            A list containing all bbGuild objects stored in the database
        """
        return list(self.guilds.values())


    
    def getGuild(self, id : int) -> bbGuild.bbGuild:
        """Get the bbGuild object with the specified ID.

        Parameters
        ----------
        id : str
            integer discord ID for the requested guild
        
        Returns
        -------
        bbGuild
            bbGuild having the requested ID
        """
        return self.guilds[id]


    
    def guildIdExists(self, id : int) -> bool:
        """Check whether a bbGuild with a given ID exists in the database.
        
        Parameters
        ----------
        id : int
            integer discord ID to check for existence
        
        Returns
        -------
        bool
            True if a bbGuild is stored in the database with the requested ID, False otherwise
        """
        # Search the DB for the requested ID
        try:
            self.getGuild(id)
        # No bbGuild found, return False
        except KeyError:
            return False
        # Return True otherwise
        return True

    
    
    def guildObjExists(self, guild : bbGuild.bbGuild) -> bool:
        """Check whether a bbGuild object exists in the database.
        Existence checking is currently handled by checking if a guild with the requested ID is stored.

        Parameters
        ----------
        guild : bbGuild
            bbGuild object to check for existence

        Returns
        -------
        bool
            True if the exact bbGuild exists in the DB, False otherwise
        """
        return self.guildIdExists(guild.id)


    
    def addGuildObj(self, guild : bbGuild.bbGuild):
        """Add a given bbGuild object to the database.

        Parameters
        ----------
        guild : bbGuild
            the bbGuild object to store
        
        Raises
        ------
        KeyError
            If the the guild is already in the database
        """
        # Ensure guild is not yet in the database
        if self.guildObjExists(guild):
            raise KeyError("Attempted to add a guild that already exists: " + guild.id)
        self.guilds[guild.id] = guild

    
    
    def addGuildID(self, id: int) -> bbGuild.bbGuild:
        """Add a bbGuild object with the requested ID to the database

        Parameters
        ----------
        id : int
            integer discord ID to create and store a bbGuild for
        
        Raises
        ------
        KeyError
            If a bbGuild is already stored for the requested ID
        
        Returns
        -------
        bbGuild
            the new bbGuild object
        """
        # Ensure the requested ID does not yet exist in the database
        if self.guildIdExists(id):
            raise KeyError("Attempted to add a guild that already exists: " + id)
        # Create and return a bbGuild for the requested ID
        self.guilds[id] = bbGuild.bbGuild(id)
        return self.guilds[id]

    
    
    def removeGuildId(self, id : int):
        """Remove the bbGuild with the requested ID from the database.
        
        Parameters
        ----------
        id : int
            integer discord ID to remove from the database
        """
        self.guilds.pop(id)


    
    def removeGuildObj(self, guild : bbGuild.bbGuild):
        """Remove the given bbGuild object from the database
        Currently removes any bbGuild sharing the given guild's ID, even if it is a different object.

        Parameters
        ----------
        guild : bbGuild
            the guild object to remove from the database
        """
        self.removeGuildId(guild.id)

    
    
    def refreshAllShopStocks(self):
        """Generate new stock for all shops belonging to the stored bbGuilds
        """
        for guild in self.guilds.values():
            guild.shop.refreshStock()

    
    
    def toDict(self) -> dict:
        """Serialise this bbGuildDB into dictionary format

        Returns
        -------
        dict
            A dictionary containing all data needed to recreate this bbGuildDB
        """
        data = {}
        # Iterate over all stored guilds
        for guild in self.getGuilds():
            # Serialise and then store each guild
            # JSON stores properties as strings, so ids must be converted to str first.
            data[str(guild.id)] = guild.toDictNoId()
        return data


    
    def __str__(self) -> str:
        """Fetch summarising information about the database, as a string
        Currently only the number of guilds stored

        Returns
        -------
        str
            A string summarising this db
        """
        return "<bbGuildDB: " + str(len(self.guilds)) + " guilds>"



def fromDict(guildsDBDict : dict) -> bbGuildDB:
    """Construct a bbGuildDB object from dictionary-serialised format; the reverse of bbGuildDB.todict()

    Parameters
    ----------
    bountyDBDict : dict
        The dictionary representation of the bbGuildDB to create
    
    Returns
    -------
    bbGuildDB
        The new bbGuildDB
    """
    # Instance the new bbGuildDB
    newDB = bbGuildDB()
    # Iterate over all IDs to add to the DB
    for id in guildsDBDict.keys():
        # Instance new bbGuilds for each ID, with the provided data
        # JSON stores properties as strings, so ids must be converted to int first.
        newDB.addGuildObj(bbGuild.fromDict(int(id), guildsDBDict[id]))
    return newDB
