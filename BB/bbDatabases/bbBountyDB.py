from ..bbObjects.bounties import bbBounty
from typing import List

class bbBountyDB:
    """A database of bbObject.bounties.bbBounty. Bounty criminal names and faction names must be unique within the database. Faction names are case sensitive.
    
    . . .
    
    Attributes
    ----------
    bounties : dict
        Dictionary of faction name to list of bounties
    factions : list
        List of str faction names, to be used in self.bounties keys
    maxBountiesPerFaction : int
        Maximum number of bounties that can be contained in each bounty's list in self.bounties[faction]
    latestBounty : bbObjects.bounties.bbBounty.Bounty
        The most recent bounty to be added to this db.
        As of writing, this is only used when scaling new bounty delays by the most recent length

    Methods
    -------
    addFaction(faction)
        Add a new useable faction name to the DB
    removeFaction(faction)
        Remove a faction name from this DB
    clearBounties(faction=None)
        Clear all bounties stored under a faction, or under all factions if none is specified
    getFactions()
        Get the list of useable faction names for this DB
    factionExists(faction)
        Decide whether a given faction name is useable in this DB
    getFactionBounties(faction)
        Get a list of all bbBounty objects stored under a given faction.
    getFactionNumBounties(faction)
        Get the number of bounties stored by a faction.
    getBounty(name, faction=None)
        Get the bbBounty object for a given bbCriminal name or alias.
        This process is much more efficient when given the faction that the criminal is wanted by.
    canMakeBounty()
        Check whether this DB has space for more bounties
    factionCanMakeBounty(faction)
        Check whether a faction has space for more bounties
    bountyNameExists(name, faction=None)
        Check whether a criminal with the given name or alias exists in the DB.
        The process is much more efficient if the faction where the bbCriminal should reside is known.
    bountyObjExists(bounty)
        Check whether a given bbBounty object exists in the DB.
        Existence is checked by the bbBounty __eq__ method, which is currently object equality (i.e physical memory address equality)
    addBounty(bounty)
        Add a given bbBounty object to the database.
        Bounties cannot be added if the bounty.faction does not have space for more bunties.
        Bounties cannot be added if the object or name already exists in the database.
    removeBountyName(name, faction=None)
        Find the bbBounty associated with the given bbCriminal name or alias, and remove it from the database.
        This process is much more efficient if the faction under which the bounty is wanted is given.
    removeBountyObj(bounty)
        Remove a given bbBounty object from the database.
    toDict()
        Serialise the bbBountyDB and all of its bbBounties into dictionary format.
    hasBounties(faction=None)
        Check whether the given faction has any bounties stored, or if ANY faction has bounties stored if none is given.
    __str__()
        Return summarising info about this bbBoutyDB in string format.
        Currently only the number of factions in the DB.
    """


    def __init__(self, factions: str, maxBountiesPerFaction: int):
        """
        Parameters
        ----------
        factions : list
            list of unique faction names useable in this db's bounties
        maxBountiesPerFaction : int
            The maximum number of bounties each faction may store
        """
        # Dictionary of faction name : list of bounties
        # TODO: add bbCriminal.__hash__, and change bbBountyDB.bounties into dict of faction:{criminal:bounty}
        self.bounties = {}

        # Useable faction names for this bbBountyDB
        self.factions = factions
        for fac in factions:
            self.bounties[fac] = []

        # the maximum length a faction's self.bounties dict can be
        self.maxBountiesPerFaction = maxBountiesPerFaction

        self.latestBounty = None


    
    def addFaction(self, faction: str):
        """Add a new useable faction name to the DB

        Parameters
        ----------
        faction : str
            The new name to enable bounty storage under. Must be unique within the db.

        Raises
        ------
        KeyError
            When attempting to add a faction which already exists in this DB
        """
        # Ensure faction name does not already exist
        if self.factionExists(faction):
            raise KeyError("Attempted to add a faction that already exists: " + faction)
        # Initialise faction's database to empty
        self.bounties[faction] = []


    
    def removeFaction(self, faction: str):
        """Remove a faction name from this DB

        Parameters
        ----------
        faction : str
            The faction name to remove. Case sensitive.
        
        Raises
        ------
        KeyError
            When given a faction which does not exist in this DB
        """
        # Ensure the faction name exists
        if not self.factionExists(faction):
            raise KeyError("Unrecognised faction: " + faction)
        # Remove the faction name from the DB
        self.bounties.pop(faction)


    
    def clearBounties(self, faction=None):
        """Clear all bounties stored under a faction, or under all factions if none is specified

        Parameters
        ----------
        faction : str
                The faction whose bounties to clear. All factions' bounties are cleared if None is given. (default None)
        
        Raises
        ------
        KeyError
            When given a faction which does not exist in this DB
        """
        if faction is not None:
            # Ensure the faction name exists
            if not self.factionExists(faction):
                raise KeyError("Unrecognised faction: " + faction)
            # Empty the faction's bounties
            self.bounties[faction] = []
        # If no faction is given
        else:
            # clearBounties for each faction in the DB
            for fac in self.getFactions():
                self.clearBounties(faction=fac)

        self.latestBounty = None

    
    
    def getFactions(self) -> List[bbBounty.Bounty]:
        """Get the list of useable faction names for this DB

        Returns
        -------
        list
            A list containing this DB's useable faction names
        """
        return self.factions


    
    def factionExists(self, faction : str) -> bool:
        """Decide whether a given faction name is useable in this DB

        Parameters
        ----------
        faction : str
            The faction to test for existence. Case sensitive.

        Returns
        -------
        bool
            True if faction is one of this DB's factions, false otherwise.
        """
        return faction in self.getFactions()

    
    
    def getFactionBounties(self, faction : str) -> List[bbBounty.Bounty]:
        """Get a list of all bbBounty objects stored under a given faction.

        Parameters
        ----------
        faction : str
            The faction whose bounties to return. Case sensitive.

        Returns
        -------
        list
            A list containing references to all bbBounties made available by faction. ⚠ Muteable, and can alter the DB!
        """
        return self.bounties[faction]


    
    def getFactionNumBounties(self, faction : str) -> int:
        """Get the number of bounties stored by a faction.

        Parameters
        ----------
        faction : str
            The faction whose bounties to return. Case sensitive.
        
        Returns
        -------
        int
            Integer number of bounties stored by a faction
        """
        return len(self.bounties[faction])


    
    def getBounty(self, name : str, faction=None) -> bbBounty.Bounty:
        """Get the bbBounty object for a given bbCriminal name or alias.
        This process is much more efficient when given the faction that the criminal is wanted by.

        Parameters
        ----------
        name : str
            A name or alias for the bbCriminal whose bbBounty is to be fetched.
        faction : str
            The faction by which the bbCriminal is wanted. Give None if this is not known, to search all factions. (default None)
        
        Returns
        -------
        bbObjects.bounties.bbBounty.Bounty
            the bbBounty object tracking the named criminal

        Raises
        ------
        KeyError
            If the requested criminal name does not exist in this DB
        """
        # If the criminal's faction is known
        if faction is not None:
            # Search the given faction's bounties
            for bounty in self.bounties[faction]:
                # Return the named criminal's bbBounty if the name is found
                if bounty.criminal.isCalled(name):
                    return bounty

        # If the criminal's faction is not known, search all factions
        else:
            for fac in self.getFactions():
                # Return the named criminal's bbBounty if the name is found
                for bounty in self.bounties[fac]:
                    if bounty.criminal.isCalled(name):
                        return bounty
        
        # The criminal was not recognised, raise an error
        raise KeyError("Bounty not found: " + name)


    
    def canMakeBounty(self) -> bbBounty.Bounty:
        """Check whether this DB has space for more bounties

        Returns
        -------
        bool
            True if at least one faction is not at capacity, False if all factions' bounties are full
        """
        # Check all bounties for factionCanMakeBounty
        for fac in self.getFactions():
            if self.factionCanMakeBounty(fac):
                # If a faction can take a bounty, return True
                return True

        # No faction found with space remaining
        return False
    

    
    def factionCanMakeBounty(self, faction : str) -> bool:
        """Check whether a faction has space for more bounties

        Parameters
        ----------
        faction : str
            the faction whose DB space to check
        
        Returns
        -------
        bool
            True if the requested faction has space for more bounties, False otherwise
        """
        return self.getFactionNumBounties(faction) < self.maxBountiesPerFaction


    
    def bountyNameExists(self, name : str, faction=None) -> bool:
        """Check whether a criminal with the given name or alias exists in the DB
        The process is much more efficient if the faction where the bbCriminal should reside is known.

        Parameters
        ----------
        name : str
            The name or alias to check for bbCriminal existence against
        faction : str
            The faction whose bounties to check for the named criminal. Use None if the faction is not known. (default None)
        
        Returns
        -------
        bool
            True if a bbBounty is found for a bbCriminal with the given name, False if the given name does not correspond to an active bounty in this DB
        """
        # Search for a bbBounty object under the given name
        try:
            self.getBounty(name, faction)
        # Return False if the name was not found, True otherwise
        except KeyError:
            return False
        return True

    
    
    def bountyObjExists(self, bounty : bbBounty.Bounty) -> bool:
        """Check whether a given bbBounty object exists in the DB.
        Existence is checked by the bbBounty __eq__ method, which is currently object equality (i.e physical memory address equality)

        Parameters
        ----------
        bounty : str
            The bbBounty object to check for existence in the DB
        
        Returns
        -------
        bool
            True if the given bounty is found within the DB, False otherwise
        """
        return bounty in self.bounties[bounty.faction]


    """Commented out as bounty indices should not be used in the main code, object references should be used instead.

    # def getBountyObjIndex(self, bounty):
    #     return self.bounties[bounty.faction].index(bounty)

    
    # def getBountyNameIndex(self, name, faction=None):
    #     return self.getBountyObjIndex(self.getBounty(name, faction=faction))
    """


    
    def addBounty(self, bounty : bbBounty.Bounty):
        """Add a given bbBounty object to the database.
        Bounties cannot be added if the bounty.faction does not have space for more bounties.
        Bounties cannot be added if the object or name already exists in the database.

        Parameters
        ----------
        bounty : str
            the bbBounty object to add to the database
        
        Raises
        ------
        OverflowError
            if the bounty.faction does not have space for more bounties
        ValueError
            if the requested bounty's name already exists in the database
        """
        # Ensure the DB has space for the bounty
        if not self.factionCanMakeBounty(bounty.faction):
            raise OverflowError("Requested faction's bounty DB is full")

        # ensure the given bounty does not already exist
        if self.bountyNameExists(bounty.criminal.name):
            raise ValueError("Attempted to add a bounty whose name already exists: " + bounty.name)

        # Add the bounty to the database
        self.bounties[bounty.faction].append(bounty)
        self.latestBounty = bounty

    
    
    def removeBountyName(self, name : str, faction=None):
        """Find the bbBounty associated with the given bbCriminal name or alias, and remove it from the database.
        This process is much more efficient if the faction under which the bounty is wanted is given.

        Parameters
        ----------
        name : str
            The name of the bbCriminal to remove
        faction : str
            The faction whose bounties to check for the named criminal. Use None if the faction is not known. (default None)
        """
        self.removeBountyObj(self.getBounty(name, faction=faction))


    
    def removeBountyObj(self, bounty : bbBounty.Bounty):
        """Remove a given bbBounty object from the database.

        Parameters
        ----------
        bounty : str
            the bbBounty object to remove from the database
        """
        if bounty is self.latestBounty:
            self.latestBounty = None
        self.bounties[bounty.faction].remove(bounty)

    
    
    def toDict(self) -> dict:
        """Serialise the bbBountyDB and all of its bbBounties into dictionary format.

        Returns
        -------
        dict
            A dictionary containing all data needed to recreate this bbBountyDB.
        """
        data = {}
        # Serialise all factions into name : list of serialised bbBounty
        for fac in self.getFactions():
            data[fac] = []
            # Serialise all of the current faction's bounties into dictionary
            for bounty in self.getFactionBounties(fac):
                data[fac].append(bounty.toDict())
        return data


    
    def hasBounties(self, faction=None) -> bool:
        """Check whether the given faction has any bounties stored, or if ANY faction has bounties stored if none is given.
        
        Parameters
        ----------
        faction : str
            The faction whose bounties to check. Give None to check all factions for bounties. (default None)
        """
        # If no faction is specified
        if faction is None:
            # Return true if any faction has at least one bounty
            for fac in self.getFactions():
                if self.getFactionNumBounties(fac) != 0:
                    return True

        # If a faction is specified, return true if it has at least one bounty
        else:
            return self.getFactionNumBounties(faction) != 0

        # no bounties found, return false
        return False 


    
    def __str__(self) -> str:
        """Return summarising info about this bbBountyDB in string format.
        Currently: The number of factions in the DB.

        Returns
        -------
        str
            a string summarising this db
        """
        return "<bbBountyDB: " + str(len(self.bounties)) + " factions>"



def fromDict(bountyDBDict : dict, maxBountiesPerFaction : int, dbReload=False) -> bbBountyDB:
    """Build a bbBountyDB object from a serialised dictionary format - the reverse of bbBountyDB.toDict.

    Parameters
    ----------
    bountyDBDict : dict
        a dictionary representation of the bbBountyDB, to convert to an object
    maxBountiesPerFaction : int
        The maximum number of bounties each faction may store
    dbReload : bool
        Whether or not this bbBountyDB is being created during the initial database loading phase of bountybot. This is used to toggle name checking in bbBounty contruction.
    
    Returns
    -------
    bbBountyDB
        The new bbBountyDB object
    """
    # Instanciate a new bbBountyDB
    newDB = bbBountyDB(bountyDBDict.keys(), maxBountiesPerFaction)
    # Iterate over all factions in the DB
    for fac in bountyDBDict.keys():
        # Convert each serialised bbBounty into a bbBounty object
        for bountyDict in bountyDBDict[fac]:
            newDB.addBounty(bbBounty.fromDict(bountyDict, dbReload=dbReload))
    return newDB
