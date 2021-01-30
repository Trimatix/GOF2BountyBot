from __future__ import annotations
from ..gameObjects import bbUser
from .. import lib
from ..logging import bbLogger
import traceback
from typing import List
from ..baseClasses import serializable


class bbUserDB(serializable.Serializable):
    """A database of bbUser objects.
    
    :var users: Dictionary of users in the database, where values are the bbUser objects and keys are the ids of their respective bbUser
    :vartype users: dict[int, bbUser]
    """

    def __init__(self):
        # Store users as a dict of user.id: user
        self.users = {}


    def userIDExists(self, id : int) -> bool:
        """Check if a user is stored in the database with the given ID.

        :param int id: integer discord ID for the bbUser to search for
        :return: True if id corresponds to a user in the database, false if no user is found with the id
        :rtype: bool
        """
        return id in self.users.keys()


    def userObjExists(self, user : bbUser.bbUser) -> bool:
        """Check if a given bbUser object is stored in the database.
        Currently only checks if a user with the same ID is stored in the database, not if the objects are the same.

        :param bbUser user: a bbUser object to check for existence
        :return: True if a bbUser is found in the database with a matching ID, False otherwise
        :rtype: bool
        """
        return self.userIDExists(user.id)


    def validateID(self, id : int) -> int:
        """Internal function to assert the type of and, potentially cast, an ID.

        :param int ID: the ID to type check. Can be either int or a string consisting only of digits.
        :raise TypeError: If the ID does not conform to the above requirements.
        :return: ID if ID is an int, or int(ID) if ID is a string of digits.
        :rtype: int
        """
        # If ID is a string, ensure it can be casted to an int before casting and returning.
        if type(id) == str:
            if not lib.stringTyping.isInt(id):
                raise TypeError("user ID must be either int or string of digits")
            return int(id)
        # If ID is not a string, nor an int, throw an error.
        elif type(id) != int:
            raise TypeError("user ID must be either int or string of digits")
        # ID must be an int, so return it.
        return id
    

    def reinitUser(self, id : int):
        """Reset the stats for the user with the specified ID.

        :param int ID: The ID of the user to reset. Can be integer or a string of digits.
        :raise KeyError: If no user is found with the requested ID
        """
        id = self.validateID(id)
        # ensure the ID exists in the database
        if not self.userIDExists(id):
            raise KeyError("user not found: " + str(id))
        # Reset the user
        self.users[id].resetUser()


    def addUser(self, id : int) -> bbUser.bbUser:
        """
        Create a new bbUser object with the specified ID and add it to the database

        :param int id: integer discord ID for the user to add
        :raise KeyError: If a bbUser already exists in the database with the specified ID
        :return: the newly created bbUser
        :rtype: bbUser
        """
        id = self.validateID(id)
        # Ensure no user exists with the specified ID in the database
        if self.userIDExists(id):
            raise KeyError("Attempted to add a user that is already in this bbUserDB")
        # Create and return a new user
        newUser = bbUser.bbUser.fromDict(bbUser.defaultUserDict, id=id)
        self.users[id] = newUser
        return newUser

    def addUserObj(self, userObj : bbUser.bbUser):
        """Store the given bbUser object in the database

        :param bbUser userObj: bbUser to store
        :raise KeyError: If a bbUser already exists in the database with the same ID as the given bbUser
        """
        # Ensure no bbUser exists in the db with the same ID as the given bbUser
        if self.userIDExists(userObj.id):
            raise KeyError("Attempted to add a user that is already in this bbUserDB: " + str(userObj))
        # Store the passed bbUser
        self.users[userObj.id] = userObj


    def getOrAddID(self, id : int) -> bbUser.bbUser:
        """If a bbUser exists in the database with the requested ID, return it. If not, create and store a new bbUser and return it.

        :param int id: integer discord ID for the user to fetch or create
        :return: the requested/created bbUser
        :rtype: int
        """
        return self.getUser(id) if self.userIDExists(id) else self.addUser(id)

    
    def removeUser(self, id : int):
        """Remove the new bbUser object with the specified ID from the database
        ⚠ The bbUser object is deleted from memory.

        :param int id: integer discord ID for the user to remove
        :raise KeyError: If no bbUser exists in the database with the specified ID
        """
        id = self.validateID(id)
        if not self.userIDExists(id):
            raise KeyError("user not found: " + str(id))
        del self.users[id]

    
    def getUser(self, id : int) -> bbUser.bbUser:
        """Fetch the bbUser from the database with the given ID.

        :param int ID: integer discord ID for the user to fetch
        :return: the stored bbUser with the given ID
        :rtype: bbUser
        """
        id = self.validateID(id)
        return self.users[id]


    def getUsers(self) -> List[bbUser.bbUser]:
        """Get a list of all bbUser objects stored in the database

        :return: list containing all bbUser objects in the db
        :rtype: list[bbUser]
        """
        return list(self.users.values())

    
    def getIds(self) -> List[int]:
        """Get a list of all user IDs stored in the database

        :return: list containing all int discord IDs for which bbUsers are stored in the database
        :rtype: list[int]
        """
        return list(self.users.keys())

    
    def toDict(self, **kwargs) -> dict:
        """Serialise this bbUserDB into dictionary format.

        :return: A dictionary containing all data needed to recreate this bbUserDB
        :rtype: dict
        """
        data = {}
        # Iterate over all user IDs in the database
        for id in self.getIds():
            # Serialise each bbUser in the database and save it, along with its ID to dict 
            # JSON stores properties as strings, so ids must be converted to str first.
            try:
                data[str(id)] = self.users[id].toDict(**kwargs)
            except Exception as e:
                bbLogger.log("UserDB", "toDict", "Error serialising bbUser: " + type(e).__name__, trace=traceback.format_exc(), eventType="USERERR")
        return data

    
    def __str__(self) -> str:
        """Get summarising information about this bbUserDB in string format.
        Currently only the number of users stored.

        :return: A string containing summarising info about this db
        :rtype: str
        """
        return "<bbUserDB: " + str(len(self.users)) + " users>"


    @classmethod
    def fromDict(cls, userDBDict : dict, **kwargs) -> bbUserDB:
        """Construct a bbUserDB from a dictionary-serialised representation - the reverse of bbUserDB.toDict()

        :param dict userDBDict: a dictionary-serialised representation of the bbUserDB to construct
        :return: the new bbUserDB
        :rtype: bbUserDB
        """
        # Instance the new bbUserDB
        newDB = bbUserDB()
        # iterate over all user IDs to spawn
        for id in userDBDict.keys():
            # Construct new bbUsers for each ID in the database
            # JSON stores properties as strings, so ids must be converted to int first.
            newDB.addUserObj(bbUser.bbUser.fromDict(userDBDict[id], id=int(id)))
        return newDB
