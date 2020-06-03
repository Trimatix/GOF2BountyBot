from ..bbObjects import bbUser
from .. import bbUtil

class bbUserDB:
    users = {}

    def validateID(self, id):
        if type(id) == str:
            if not bbUtil.isInt(id):
                raise TypeError("user ID must be either int or string of digits")
            return int(id)
        elif type(id) != int:
            raise TypeError("user ID must be either int or string of digits")
        return id
    

    def initUser(self, id):
        id = self.validateID
        if not id in self.users:
            raise KeyError("user not found: " + str(id))
        self.users[id].resetUser()


    def addUser(self, id):
        id = self.validateID
        if id in self.users:
            raise KeyError("Attempted to add a user that is already in this bbUserDB")
        self.users[id] = bbUser.fromDict(id, {"credits":0, "bountyCooldownEnd":0, "totalCredits":0, "systemsChecked":0, "wins":0})

    
    def addUserObj(self, userObj):
        if userObj.id in self.users:
            raise KeyError("Attempted to add a user that is already in this bbUserDB: " + str(userObj))
        self.users[userObj.id] = userObj

    
    def removeUser(self, id):
        id = self.validateID
        if not id in self.users:
            raise KeyError("user not found: " + str(id))
        del self.users[id]


    def getUser(self, id):
        id = self.validateID
        if not id in self.users:
            raise KeyError("user not found: " + str(id))
        return self.users[id]

    
    def toDict(self):
        data = {}
        for id in self.users.keys():
            data[id] = self.users[id].toDictNoId()
        return data


    def fullDump(self):
        data = "bbUserDB FULL DUMP:\n"
        place = 0
        for id in self.users.keys():
            data += str(place) + "- " + str(self.users[id]) + "\n"
            place += 1
        return data[:-1]

    
    def idsDump(self):
        data = "bbUserDB IDs DUMP:\n"
        place = 0
        for id in self.users.keys():
            data += str(place) + "- " + str(id) + "\n"
            place += 1
        return data[:-1]


    def __str__(self):
        return "<bbUserDB: " + str(len(self.users)) + " users>"

    
def fromDict(userDBDict):
    newDB = bbUserDB()
    for id in userDBDict.keys():
        newDB.addUserObj(bbUser.fromDict(id, userDBDict[id]))
