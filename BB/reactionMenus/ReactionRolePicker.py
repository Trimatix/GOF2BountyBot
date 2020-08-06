from . import ReactionMenu
from ..bbConfig import bbConfig


async def toggleRole(args, reactingUser=None):
    dcGuild = args[0]
    dcMember = dcGuild.get_member(reactingUser.id)
    role = args[1]
    msgID = args[2]

    if role in dcMember.roles:
        await dcMember.remove_roles(role, reason="User requested role toggle via BB reaction menu " + str(msgID))
        return False
    else:
        await dcMember.add_roles(role, reason="User requested role toggle via BB reaction menu " + str(msgID))
        return True


class ReactionRolePicker(ReactionMenu.ReactionMenu):
    def __init__(self, msg, reactionRoles, dcGuild, titleTxt="", desc="", col=None, footerTxt="", img="", thumb="", icon="", authorName="", timeout=None):
        roleOptions = {}
        for reaction in reactionRoles:
            roleOptions[reaction] = ReactionMenu.ReactionMenuOption(reactionRoles[reaction].name, reaction, addFunc=toggleRole, addArgs=(dcGuild, reactionRoles[reaction], msg.id), removeFunc=toggleRole, removeArgs=(dcGuild, reactionRoles[reaction], msg.id))

        super(ReactionRolePicker, self).__init__(msg, options=roleOptions, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout)


    def toDict(self):
        baseDict = super(ReactionRolePicker, self).toDict()
