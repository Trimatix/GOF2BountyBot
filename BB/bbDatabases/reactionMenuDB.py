from ..reactionMenus import ReactionMenu, ReactionRolePicker, ReactionInventoryPicker

class ReactionMenuDB(dict):
    def toDict(self):
        data = {}
        for msgID in self:
            data[msgID] = self[msgID].toDict()
        return data


async def fromDict(dbDict):
    newDB = ReactionMenuDB()

    for msgID in dbDict:
        if "type" in dbDict[msgID]:
            if dbDict[msgID]["type"] == "ReactionInventoryPicker":
                newDB[int(msgID)] = ReactionInventoryPicker.fromDict(dbDict[msgID])
                
            elif dbDict[msgID]["type"] == "ReactionRolePicker":
                newDB[int(msgID)] = await ReactionRolePicker.fromDict(dbDict[msgID])

            else:
                newDB[int(msgID)] = ReactionMenu.fromDict(dbDict[msgID])
    
    return newDB