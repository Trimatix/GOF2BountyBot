from ..reactionMenus import ReactionMenu, ReactionRolePicker, ReactionInventoryPicker, ReactionDuelChallengeMenu

unsaveableMenuTypes = ["ReactionDuelChallengeMenu"]

class ReactionMenuDB(dict):
    def toDict(self):
        data = {}
        for msgID in self:
            menuData = self[msgID].toDict()
            if menuData["type"] not in unsaveableMenuTypes:
                data[msgID] = menuData
        return data


async def fromDict(dbDict):
    newDB = ReactionMenuDB()

    for msgID in dbDict:
        if "type" in dbDict[msgID]:
            if dbDict[msgID]["type"] == "ReactionInventoryPicker":
                newDB[int(msgID)] = ReactionInventoryPicker.fromDict(dbDict[msgID])
                
            elif dbDict[msgID]["type"] == "ReactionRolePicker":
                newDB[int(msgID)] = await ReactionRolePicker.fromDict(dbDict[msgID])

            elif dbDict[msgID]["type"] == "ReactionDuelChallengeMenu":
                continue

            else:
                newDB[int(msgID)] = ReactionMenu.fromDict(dbDict[msgID])
    
    return newDB