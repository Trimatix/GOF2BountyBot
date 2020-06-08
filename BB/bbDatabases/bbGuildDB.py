from ..bbObjects import bbGuild

class bbGuildDB:
    guilds = {}


    def getIDs(self):
        return self.guilds.keys()


    def getGuilds(self):
        return self.guilds.values()


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

    
    def refreshAllShopStocks(self):
        for guild in self.guilds:
            guild.shop.refreshStock()

    
    def toDict(self):
        data = {}
        for guild in self.getGuilds():
            # JSON stores properties as strings, so ids must be converted to str first.
            data[str(guild.id)] = guild.toDictNoId()
        return data


    def __str__(self):
        return "<bbGuildDB: " + str(len(self.guilds)) + " guilds>"

    
def fromDict(bountyDBDict):
    newDB = bbGuildDB()
    for id in bountyDBDict.keys():
        # JSON stores properties as strings, so ids must be converted to int first.
        newDB.addGuildObj(bbGuild.fromDict(int(id), bountyDBDict[id]))
    return newDB
