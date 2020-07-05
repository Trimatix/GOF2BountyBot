from ..bbObjects import bbUser
from .. import bbUtil

"""
A database of bbUser objects.

"""
class bbUserDB:
    def __init__(self):
        # Store users as a dict of user.id: user
        self.users = {}


    """
    Check if a user is stored in the database with the given ID.

    @param id -- integer discord ID for the bbUser to search for
    @return -- True if id corresponds to a user in the database, false if no user is found with the id
    """
    def userIDExists(self, id):
        return id in self.users.keys()


    """
    Check if a given bbUser object is stored in the database.
    Currently only checks if a user with the same ID is stored in the database, not if the objects are the same.

    @param user -- a bbUser object to check for existence
    @return -- True if a bbUser is found in the database with a matching ID, False otherwise
    """
    def userObjExists(self, user):
        return self.userIDExists(user.id)


    """
    Internal function to assert the type of and, potentially cast, an ID.

    @param ID -- the ID to type check. Can be either int or a string consisting only of digits.
    @throws TypeError -- If the ID does not conform to the above requirements.
    @return -- ID if ID is an int, or int(ID) if ID is a string of digits.
    """
    def validateID(self, id):
        # If ID is a string, ensure it can be casted to an int before casting and returning.
        if type(id) == str:
            if not bbUtil.isInt(id):
                raise TypeError("user ID must be either int or string of digits")
            return int(id)
        # If ID is not a string, nor an int, throw an error.
        elif type(id) != int:
            raise TypeError("user ID must be either int or string of digits")
        # ID must be an int, so return it.
        return id
    

    """
    Reset the stats for the user with the specified ID.

    @param ID -- The ID of the user to reset. Can be integer or a string of digits.
    @throws KeyError -- If no user is found with the requested ID
    """
    def reinitUser(self, id):
        id = self.validateID(id)
        # ensure the ID exists in the database
        if not self.userIDExists(id):
            raise KeyError("user not found: " + str(id))
        # Reset the user
        self.users[id].resetUser()


    """
    Create a new bbUser object with the specified ID and add it to the database

    @param id -- integer discord ID for the user to add
    @throws KeyError -- If a bbUser already exists in the database with the specified ID
    @return -- the newly created bbUser
    """
    def addUser(self, id):
        id = self.validateID(id)
        # Ensure no user exists with the specified ID in the database
        if self.userIDExists(id):
            raise KeyError("Attempted to add a user that is already in this bbUserDB")
        # Create and return a new user
        newUser = bbUser.fromDict(id, bbUser.defaultUserDict)
        self.users[id] = newUser
        return newUser

    """
    Store the given bbUser object in the database

    @param userObj -- bbUser to store
    @throws KeyError -- If a bbUser already exists in the database with the same ID as the given bbUser
    """
    def addUserObj(self, userObj):
        # Ensure no bbUser exists in the db with the same ID as the given bbUser
        if self.userIDExists(userObj.id):
            raise KeyError("Attempted to add a user that is already in this bbUserDB: " + str(userObj))
        # Store the passed bbUser
        self.users[userObj.id] = userObj


    """
    If a bbUser exists in the database with the requested ID, return it. If not, create and store a new bbUser and return it.

    @param id -- integer discord ID for the user to fetch or create
    @return -- the requested/created bbUser
    """
    def getOrAddID(self, id):
        return self.getUser(id) if self.userIDExists(id) else self.addUser(id)

    
    """
    Remove the new bbUser object with the specified ID from the database
    ⚠ The bbUser object is deleted from memory.

    @param id -- integer discord ID for the user to remove
    @throws KeyError -- If no bbUser exists in the database with the specified ID
    """
    def removeUser(self, id):
        id = self.validateID(id)
        if not self.userIDExists(id):
            raise KeyError("user not found: " + str(id))
        del self.users[id]


    """
    Fetch the bbUser from the database with the given ID.

    @param ID -- integer discord ID for the user to fetch
    @return -- the stored bbUser with the given ID
    """
    def getUser(self, id):
        id = self.validateID(id)
        return self.users[id]


    """
    Get a list of all bbUser objects stored in the database

    @return -- list containing all bbUser objects in the db
    """
    def getUsers(self):
        return list(self.users.values())

    
    """
    Get a list of all user IDs stored in the database

    @return -- list containing all int discord IDs for which bbUsers are stored in the database
    """
    def getIds(self):
        return list(self.users.keys())

    
    """
    Serialise this bbUserDB into dictionary format.

    @return -- A dictionary containing all data needed to recreate this bbUserDB
    """
    def toDict(self):
        data = {}
        # Iterate over all user IDs in the database
        for id in self.getIds():
            # Serialise each bbUser in the database and save it, along with its ID to dict 
            # JSON stores properties as strings, so ids must be converted to str first.
            data[str(id)] = self.users[id].toDictNoId()
        return data


    """
    Get summarising information about this bbUserDB in string format.
    Currently only the number of users stored.

    @return -- A string containing summarising info about this db
    """
    def __str__(self):
        return "<bbUserDB: " + str(len(self.users)) + " users>"


"""
Construct a bbUserDB from a dictionary-serialised representation - the reverse of bbUserDB.toDict()

@param userDBDict -- a dictionary-serialised representation of the bbUserDB to construct
@return -- the new bbUserDB
"""
def fromDict(userDBDict):
    # Instance the new bbUserDB
    newDB = bbUserDB()
    # iterate over all user IDs to spawn
    for id in userDBDict.keys():
        # Construct new bbUsers for each ID in the database
        # JSON stores properties as strings, so ids must be converted to int first.
        newDB.addUserObj(bbUser.fromDict(int(id), userDBDict[id]))
    return newDB
