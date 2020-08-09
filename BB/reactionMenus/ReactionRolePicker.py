from . import ReactionMenu
from ..bbConfig import bbConfig
from .. import bbGlobals, bbUtil
from discord import Colour, NotFound, HTTPException, Forbidden
from datetime import datetime
from ..scheduling import TimedTask


async def giveRole(args, reactingUser=None):
    dcGuild = args[0]
    dcMember = dcGuild.get_member(reactingUser.id)
    role = args[1]
    msgID = args[2]

    if role not in dcMember.roles:
        await dcMember.add_roles(role, reason="User requested role toggle via BB reaction menu " + str(msgID))
    return True


async def removeRole(args, reactingUser=None):
    dcGuild = args[0]
    dcMember = dcGuild.get_member(reactingUser.id)
    role = args[1]
    msgID = args[2]

    if role in dcMember.roles:
        await dcMember.remove_roles(role, reason="User requested role toggle via BB reaction menu " + str(msgID))
    return False


class ReactionRolePickerOption(ReactionMenu.ReactionMenuOption):
    def __init__(self, emoji, role, menu):
        self.role = role
        super(ReactionRolePickerOption, self).__init__(self.role.name, emoji, addFunc=giveRole, addArgs=(menu.dcGuild, self.role, menu.msg.id), removeFunc=removeRole, removeArgs=(menu.dcGuild, self.role, menu.msg.id))


    def toDict(self):
        # baseDict = super(ReactionRolePickerOption, self).toDict()
        # baseDict["role"] = self.role.id
        
        # return baseDict

        return {"role": self.role.id}


class ReactionRolePicker(ReactionMenu.ReactionMenu):
    def __init__(self, msg, reactionRoles, dcGuild, titleTxt="", desc="", col=None, footerTxt="", img="", thumb="", icon="", authorName="", timeout=None, targetMember=None, targetRole=None):
        self.dcGuild = dcGuild
        self.msg = msg
        roleOptions = {}
        for reaction in reactionRoles:
            roleOptions[reaction] = ReactionRolePickerOption(reaction, reactionRoles[reaction], self)

        super(ReactionRolePicker, self).__init__(msg, options=roleOptions, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout, targetMember=targetMember, targetRole=targetRole)


    def toDict(self):
        baseDict = super(ReactionRolePicker, self).toDict()
        baseDict["guild"] = self.dcGuild.id
        return baseDict


async def fromDict(rmDict):
    dcGuild = bbGlobals.client.get_guild(rmDict["guild"])
    msg = await dcGuild.get_channel(rmDict["channel"]).fetch_message(rmDict["msg"])

    reactionRoles = {}
    for reaction in rmDict["options"]:
        reactionRoles[bbUtil.dumbEmojiFromStr(reaction)] = dcGuild.get_role(rmDict["options"][reaction]["role"])

    timeoutTT = None
    if "timeout" in rmDict:
        expiryTime = datetime.utcfromtimestamp(rmDict["timeout"])
        bbGlobals.reactionMenusTTDB.scheduleTask(TimedTask.TimedTask(expiryTime=expiryTime, expiryFunction=ReactionMenu.markExpiredMenu, expiryFunctionArgs=msg.id))


    return ReactionRolePicker(msg, reactionRoles, dcGuild,
                                titleTxt=rmDict["titleTxt"] if "titleTxt" in rmDict else "",
                                desc=rmDict["desc"] if "desc" in rmDict else "",
                                col=Colour.from_rgb(rmDict["col"][0], rmDict["col"][1], rmDict["col"][2]) if "col" in rmDict else Colour.default(),
                                footerTxt=rmDict["footerTxt"] if "footerTxt" in rmDict else "",
                                img=rmDict["img"] if "img" in rmDict else "",
                                thumb=rmDict["thumb"] if "thumb" in rmDict else "",
                                icon=rmDict["icon"] if "icon" in rmDict else "",
                                authorName=rmDict["authorName"] if "authorName" in rmDict else "",
                                timeout=timeoutTT,
                                targetMember=dcGuild.get_member(rmDict["targetMember"]) if "targetMember" in rmDict else None,
                                targetRole=dcGuild.get_role(rmDict["targetRole"]) if "targetRole" in rmDict else None)