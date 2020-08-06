from ..reactionMenus import *

class ReactionMenuDB(dict):
    def toDict(self):
        data = {}
        for msgID in self:
            data[msgID] = self[msgID].toDict()
        return data


def fromDict(dbDict):
    newDB = ReactionMenuDB()

    for msgID in dbDict:
        if "type" in dbDict:
            if dbDict[msgID]["type"] == "ReactionInventoryPicker":
                newDB[msgID] = ReactionMenuInventoryPicker.fromDict(dbDict[msgID])
                
            elif dbDict[msgID]["type"] == "ReactionRoleMenu":
                newDB[msgID] = ReactionRoleMenu.fromDict(dbDict[msgID])

            else:
                newDB[msgID] = ReactionMenu.fromDict(dbDict[msgID])
    
    return newDB