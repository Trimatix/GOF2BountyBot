from ..bbObjects import bbGuild

class bbGuildDB:
    guilds = {}


    def getGuild(self, id):
        return self.guilds[id]


    def guildIdExists(self, id):
        try:
            self.getGuild(id)
        except KeyError:
            return False
        return True

    
    def guildObjExists(self, guild):
        return self.guildIdExists(guild.id)


    def addGuildObj(self, guild):
        if self.guildObjExists(guild):
            raise KeyError("Attempted to add a guild that already exists: " + guild.id)
        self.guilds[guild.id] = guild

    
    def addGuildID(self, id):
        if self.guildIdExists(id):
            raise KeyError("Attempted to add a guild that already exists: " + id)
        self.guilds[id] = bbGuild.bbGuild(id)

    
    def removeGuildId(self, id):
        self.guilds.pop(id)


    def removeGuildObj(self, guild):
        self.removeGuildId(guild.id)

    
    def toDict(self):
        data = {}
        for guild in self.guilds.keys():
            data[guild.id] = guild.toDictNoId()
        return data


    def __str__(self):
        return "<bbGuildDB: " + str(len(self.guilds)) + " guilds>"

    
def fromDict(bountyDBDict):
    newDB = bbGuildDB()
    for id in bountyDBDict.keys():
        newDB.addGuildObj(bbGuild.fromDict(id, bountyDBDict[id]))
    return newDB
