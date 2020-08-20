from ..bbObjects.bounties import bbBounty, bbCriminal


"""
A database of bbObject.bounties.bbBounty.
Bounty criminal names and faction names must be unique within the database.
Faction names are case sensitive.

@param factions -- list of unique faction names useable in this db's bounties
@param maxBountiesPerFaction -- The maximum number of bounties each faction may store
"""
class bbBountyDB:
    def __init__(self, factions, maxBountiesPerFaction):
        # Dictionary of faction name : list of bounties
        # TODO: add bbCriminal.__hash__, and change bbBountyDB.bounties into dict of faction:{criminal:bounty}
        self.bounties = {}

        # Useable faction names for this bbBountyDB
        self.factions = factions
        # the maximum length a faction's self.bounties dict can be
        self.maxBountiesPerFaction = maxBountiesPerFaction
        # dictionary of faction: list of bbCriminals which should not be spawned.
        # Currently used for escaped criminals
        self.escapedCriminals = {}
        # dictionary of bbCriminal: number of minutes until the bounty should respawn.
        # Currently used only for saving.
        self.escapedCriminalTimeouts = {}

        for fac in factions:
            self.bounties[fac] = []
            self.escapedCriminals[fac] = []

        self.latestBounty = None


    """
    Add a criminal to the record of escaped criminals.
    crim must not yet be recorded in the escaped criminals database.

    @param crim -- The criminal to record
    @param time -- Integer number of minutes used for scheduling this criminal's respawn
    """
    def addEscapedCriminal(self, crim, time):
        if crim in self.escapedCriminals[crim.faction]:
            raise KeyError("criminal already on record: " + crim.name)
        self.escapedCriminalTimeouts[crim] = time
        self.escapedCriminals[crim.faction].append(crim)

    
    """
    Remove a criminal from the record of escaped criminals.
    crim must already be recorded in the escaped criminals database.

    @param crim -- The criminal to remove from the record
    """
    def removeEscapedCriminal(self, crim):
        if crim not in self.escapedCriminals[crim.faction]:
            raise KeyError("criminal not found: " + crim.name)
        self.escapedCriminals[crim.faction].remove(crim)
        del self.escapedCriminalTimeouts[crim]


    """
    Decide whether a bbCriminal is recorded in the escaped criminals database.

    @param crim -- The bbCriminal to check for existence
    @return -- True if crim is in this database's escaped criminals record, False otherwise
    """
    def escapedCriminalExists(self, crim):
        return crim in self.escapedCriminals[crim.faction]

        self.latestBounty = None


    """
    Add a new useable faction name to the DB

    @param faction -- The new name to enable bounty storage under. Must be unique within the db.
    @throws KeyError -- When attempting to add a faction which already exists in this DB
    """
    def addFaction(self, faction):
        # Ensure faction name does not already exist
        if self.factionExists(faction):
            raise KeyError("Attempted to add a faction that already exists: " + faction)
        # Initialise faction's database to empty
        self.bounties[faction] = []
        self.escapedCriminals[faction] = []


    """
    Remove a faction name from this DB

    @param faction -- The faction name to remove. Case sensitive.
    @throws KeyError -- When given a faction which does not exist in this DB
    """
    def removeFaction(self, faction):
        # Ensure the faction name exists
        if not self.factionExists(faction):
            raise KeyError("Unrecognised faction: " + faction)
        # Remove the faction name from the DB
        del self.bounties[faction]
        del self.escapedCriminals[faction]


    """
    Clear all bounties stored under a faction, or under all factions if none is specified
    Also clears the criminals in ignoredCriminals

    @param faction -- The faction whose bounties to clear. All factions' bounties are cleared if None is given. Default: None
    @throws KeyError -- When given a faction which does not exist in this DB
    """
    def clearBounties(self, faction=None):
        if faction is not None:
            # Ensure the faction name exists
            if not self.factionExists(faction):
                raise KeyError("Unrecognised faction: " + faction)
            # Empty the faction's bounties
            self.bounties[faction] = []
            self.escapedCriminals[faction] = []
        # If no faction is given
        else:
            # clearBounties for each faction in the DB
            for fac in self.getFactions():
                self.clearBounties(faction=fac)

        self.latestBounty = None

    
    """
    Get the list of useable faction names for this DB

    @return -- A list containing this DB's useable faction names
    """
    def getFactions(self):
        return self.factions


    """
    Decide whether a given faction name is useable in this DB

    @param faction -- The faction to test for existence. Case sensitive.
    @return -- True if faction is one of this DB's factions, false otherwise.
    """
    def factionExists(self, faction):
        return faction in self.getFactions()

    
    """
    Get a list of all bbBounty objects stored under a given faction.

    @param faction -- The faction whose bounties to return. Case sensitive.
    @return -- A list containing references to all bbBounties made available by faction. ⚠ Muteable, and can alter the DB!
    """
    def getFactionBounties(self, faction):
        return self.bounties[faction]


    """
    Get the number of bounties stored by a faction.

    @param faction -- The faction whose bounties to return. Case sensitive.
    @return -- Integer number of bounties stored by a faction
    """
    def getFactionNumBounties(self, faction):
        return len(self.bounties[faction])


    """
    Get the bbBounty object for a given bbCriminal name or alias.
    This process is much more efficient when given the faction that the criminal is wanted by.

    @param name -- A name or alias for the bbCriminal whose bbBounty is to be fetched.
    @param faction -- The faction by which the bbCriminal is wanted. Give None if this is not known, to search all factions. Default: None
    @return -- the bbBounty object tracking the named criminal
    @throws KeyError -- If the requested criminal name does not exist in this DB
    """
    def getBounty(self, name, faction=None):
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

    
    """
    Get the bbCriminal object for a given name or alias, from the list of escaped criminals.
    This process is much more efficient when given the faction that the criminal is wanted by.

    @param name -- A name or alias for the bbCriminal to be fetched.
    @param faction -- The faction by which the bbCriminal is wanted. Give None if this is not known, to search all factions. Default: None
    @return -- the the named bbCriminal
    @throws KeyError -- If the requested criminal name does not exist in the escapedCriminals list
    """
    def getEscapedCriminal(self, name, faction=None):
        # If the criminal's faction is known
        if faction is not None:
            # Search the given faction's bounties
            for crim in self.escapedCriminals[faction]:
                # Return the named criminal's bbBounty if the name is found
                if crim.isCalled(name):
                    return crim

        # If the criminal's faction is not known, search all factions
        else:
            for fac in self.getFactions():
                # Return the named criminal's bbBounty if the name is found
                for crim in self.escapedCriminals[fac]:
                    if crim.isCalled(name):
                        return crim
        
        # The criminal was not recognised, raise an error
        raise KeyError("Bounty not found: " + name)


    """
    Check whether this DB has space for more bounties

    @return -- True if at least one faction is not at capacity, False if all factions' bounties are full
    """
    def canMakeBounty(self):
        # Check all bounties for factionCanMakeBounty
        for fac in self.getFactions():
            if self.factionCanMakeBounty(fac):
                # If a faction can take a bounty, return True
                return True

        # No faction found with space remaining
        return False
    

    """
    Check whether a faction has space for more bounties

    @param faction -- the faction whose DB space to check
    @return -- True if the requested faction has space for more bounties, False otherwise
    """
    def factionCanMakeBounty(self, faction):
        return (self.getFactionNumBounties(faction) - len(self.escapedCriminals[faction])) < self.maxBountiesPerFaction


    """
    Check whether a criminal with the given name or alias exists in the DB
    The process is much more efficient if the faction where the bbCriminal should reside is known.

    @param name -- The name or alias to check for bbCriminal existence against
    @param faction -- The faction whose bounties to check for the named criminal. Use None if the faction is not known. Default: None
    @return -- True if a bbBounty is found for a bbCriminal with the given name, False if the given name does not correspond to an active bounty in this DB
    """
    def bountyNameExists(self, name, faction=None, noEscapedCrim=True):
        # Search for a bbBounty object under the given name
        try:
            self.getBounty(name, faction)
        # Return False if the name was not found, True otherwise
        except KeyError:
            if not noEscapedCrim:
                try:
                    self.getEscapedCriminal(name, faction)
                except KeyError:
                    return False
            else:
                return False
        return True

    
    """
    Check whether a given bbBounty object exists in the DB.
    Existence is checked by the bbBounty __eq__ method, which is currently object equality (i.e physical memory address equality)

    @param bounty -- The bbBounty object to check for existence in the DB
    @return -- True if the given bounty is found within the DB, False otherwise
    """
    def bountyObjExists(self, bounty):
        return bounty in self.bounties[bounty.faction]


    """Commented out as bounty indices should not be used in the main code, object references should be used instead.

    # def getBountyObjIndex(self, bounty):
    #     return self.bounties[bounty.faction].index(bounty)

    
    # def getBountyNameIndex(self, name, faction=None):
    #     return self.getBountyObjIndex(self.getBounty(name, faction=faction))
    """


    """
    Add a given bbBounty object to the database.
    Bounties cannot be added if the bounty.faction does not have space for more bounties.
    Bounties cannot be added if the object or name already exists in the database.

    @param bounty -- the bbBounty object to add to the database
    @throws OverflowError -- if the bounty.faction does not have space for more bounties
    @throws ValueError -- if the requested bounty's name already exists in the database
    """
    def addBounty(self, bounty):
        # Ensure the DB has space for the bounty
        if not self.factionCanMakeBounty(bounty.faction):
            raise OverflowError("Requested faction's bounty DB is full")

        # ensure the given bounty does not already exist
        if self.bountyNameExists(bounty.criminal.name, noEscapedCrim=False):
            raise ValueError("Attempted to add a bounty whose name already exists: " + bounty.criminal.name)

        # Add the bounty to the database
        self.bounties[bounty.faction].append(bounty)
        self.latestBounty = bounty

    
    """
    Find the bbBounty associated with the given bbCriminal name or alias, and remove it from the database.
    This process is much more efficient if the faction under which the bounty is wanted is given.

    @param name -- The name of the bbCriminal to remove
    @param faction -- The faction whose bounties to check for the named criminal. Use None if the faction is not known. Default: None
    """
    def removeBountyName(self, name, faction=None):
        self.removeBountyObj(self.getBounty(name, faction=faction))


    """
    Remove a given bbBounty object from the database.

    @param bounty -- the bbBounty object to remove from the database
    """
    def removeBountyObj(self, bounty):
        if bounty is self.latestBounty:
            self.latestBounty = None
        self.bounties[bounty.faction].remove(bounty)

    
    """
    Serialise the bbBountyDB and all of its bbBounties into dictionary format.

    @return -- A dictionary containing all data needed to recreate this bbBountyDB.
    """
    def toDict(self):
        data = {"escapedCriminals": []}
        # Serialise all factions into name : list of serialised bbBounty
        for fac in self.getFactions():
            data[fac] = []
            # Serialise all of the current faction's bounties into dictionary
            for bounty in self.getFactionBounties(fac):
                data[fac].append(bounty.toDict())

            for crim in self.escapedCriminals[fac]:
                data["escapedCriminals"].append([crim.toDict(), self.escapedCriminalTimeouts[crim]])
        return data


    """
    Check whether the given faction has any bounties stored, or if ANY faction has bounties stored if none is given.

    @param faction -- The faction whose bounties to check. Give None to check all factions for bounties. Default: None
    """
    def hasBounties(self, faction=None):
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


    """
    Return summarising info about this bbBountyDB in string format.
    Currently: The number of factions in the DB.

    @return -- a string summarising this db
    """
    def __str__(self):
        return "<bbBountyDB: " + str(len(self.bounties)) + " factions>"


"""
Build a bbBountyDB object from a serialised dictionary format - the reverse of bbBountyDB.toDict.

@param bountyDBDict -- a dictionary representation of the bbBountyDB, to convert to an object
@param maxBountiesPerFaction -- The maximum number of bounties each faction may store
@param dbReload -- Whether or not this bbBountyDB is being created during the initial database loading phase of bountybot. This is used to toggle name checking in bbBounty contruction.
@return -- The new bbBountyDB object
"""
def fromDict(bountyDBDict, maxBountiesPerFaction, dbReload=False):
    # Instanciate a new bbBountyDB
    newDB = bbBountyDB(bountyDBDict.keys(), maxBountiesPerFaction)
    # Iterate over all factions in the DB
    for fac in bountyDBDict.keys():
        if fac == "escapedCriminals":
            for crim in bountyDBDict[fac]:
                newDB.addEscapedCriminal(bbCriminal.fromDict(crim[0]), crim[1])
        else:
            # Convert each serialised bbBounty into a bbBounty object
            for bountyDict in bountyDBDict[fac]:
                newDB.addBounty(bbBounty.fromDict(bountyDict, dbReload=dbReload))
    return newDB
