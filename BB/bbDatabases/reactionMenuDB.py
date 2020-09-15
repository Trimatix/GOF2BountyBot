from ..reactionMenus import ReactionMenu, ReactionRolePicker, ReactionInventoryPicker, ReactionDuelChallengeMenu, ReactionPollMenu

# ReactionMenu subclasses that cannot be saved to dictionary
# TODO: change to a class-variable reference e.g menu.__class__.SAVEABLE
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

            elif dbDict[msgID]["type"] == "ReactionPollMenu":
                newDB[int(msgID)] = await ReactionPollMenu.fromDict(dbDict[msgID])

            else:
                newDB[int(msgID)] = ReactionMenu.fromDict(dbDict[msgID])
    
    return newDB