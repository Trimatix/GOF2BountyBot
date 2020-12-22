from ..reactionMenus import ReactionMenu, ReactionRolePicker, ReactionInventoryPicker, ReactionDuelChallengeMenu, ReactionPollMenu
from .. import bbGlobals
from ..logging import bbLogger


class ReactionMenuDB(dict):
    """A database of ReactionMenu instances.
    Currently just an extension of dict to add toDict()."""

    def toDict(self, **kwargs) -> str:
        """Serialise all saveable ReactionMenus in this DB into a single dictionary.

        :return: A dictionary containing full dictionary descriptions of all saveable ReactionMenu instances in this database
        :rtype: dict
        """
        data = {}
        for msgID in self:
            if ReactionMenu.isSaveableMenuInstance(self[msgID]):
                data[msgID] = self[msgID].toDict(**kwargs)
        return data


async def fromDict(dbDict : dict) -> ReactionMenuDB:
    """Factory function constructing a new ReactionMenuDB from dictionary-serialized format; the opposite of ReactionMenuDB.toDict

    :param dict dbDict: A dictionary containing all info needed to reconstruct a ReactionMenuDB, in accordance with ReactionMenuDB.toDict
    :return: A new ReactionMenuDB instance as described by dbDict
    :rtype: ReactionMenuDB
    """
    newDB = ReactionMenuDB()
    requiredAttrs = ["type", "guild", "channel"]

    for msgID in dbDict:
        menuData = dbDict[msgID]

        for attr in requiredAttrs:
            if attr not in menuData:
                bbLogger.log("reactionMenuDB", "fromDict", "Invalid menu dict (missing " + attr + "), ignoring and removing. " + " ".join(foundAttr + "=" + menuData[foundAttr] for foundAttr in requiredAttrs if foundAttr in menuData), category="reactionMenus", eventType="dictNo" + attr.capitalize)

        menuDescriptor = menuData["type"] + "(" + "/".join(str(id) for id in [menuData["guild"], menuData["channel"], msgID]) + ")"

        dcGuild = bbGlobals.client.get_guild(menuData["guild"])
        if dcGuild is None:
            dcGuild = await bbGlobals.client.fetch_guild(menuData["guild"])
            if dcGuild is None:
                bbLogger.log("reactionMenuDB", "fromDict", "Unrecognised guild in menu dict, ignoring and removing: " + menuDescriptor, category="reactionMenus", eventType="unknGuild")
                continue

        menuChannel = dcGuild.get_channel(menuData["channel"])
        if menuChannel is None:
            menuChannel = await dcGuild.fetch_channel(menuData["channel"])
            if menuChannel is None:
                bbLogger.log("reactionMenuDB", "fromDict", "Unrecognised channel in menu dict, ignoring and removing: " + menuDescriptor, category="reactionMenus", eventType="unknChannel")
                continue

        msg = await menuChannel.fetch_message(menuData["msg"])
        if msg is None:
            bbLogger.log("reactionMenuDB", "fromDict", "Unrecognised message in menu dict, ignoring and removing: " + menuDescriptor, category="reactionMenus", eventType="unknMsg")
            continue

        if menuData["type"] in ReactionMenu.saveableNameMenuTypes:
            newDB[int(msgID)] = ReactionMenu.saveableNameMenuTypes[menuData["type"]].fromDict(menuData, msg=msg)
        else:
            bbLogger.log("reactionMenuDB", "fromDict", "Attempted to fromDict a non-saveable menu type, ignoring and removing. msg #" + str(msgID) + ", type " + menuData["type"], category="reactionMenus", eventType="dictUnsaveable")
    
    return newDB