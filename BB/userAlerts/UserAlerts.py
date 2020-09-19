from discord import utils
from abc import ABC, abstractmethod

class UABase(ABC):
    @abstractmethod
    async def toggle(self, dcGuild, bbGuild, dcMember):
        # TODO: Stop requesting bbGuild, look it up from bbGlobals using dcGuild
        pass


    @abstractmethod
    def getState(self, dcGuild, bbGuild, dcMember):
        # TODO: Stop requesting bbGuild, look it up from bbGlobals using dcGuild
        pass


    @abstractmethod
    async def setState(self, dcGuild, bbGuild, dcMember, newState):
        # TODO: Stop requesting bbGuild, look it up from bbGlobals using dcGuild
        pass


class StateUserAlert(UABase):
    def __init__(self, state):
        super(StateUserAlert, self).__init__()
        self.state = state

    
    async def toggle(self, dcGuild, bbGuild, dcMember):
        self.state = not self.state
        return self.state


    def getState(self, dcGuild, bbGuild, dcMember):
        return self.state

    
    async def setState(self, dcGuild, bbGuild, dcMember, newState):
        self.state = newState
        return newState


class GuildRoleUserAlert(UABase):
    def __init__(self):
        super(GuildRoleUserAlert, self).__init__()


    async def toggle(self, dcGuild, bbGuild, dcMember):
        alertRole = utils.get(dcGuild.roles, id=bbGuild.getUserAlertRoleID(userAlertsTypesIDs[type(self)]))
        if alertRole is None:
            raise ValueError("Requested guild does not have a role set for the requested alert: " + userAlertsTypesIDs[type(self)])
        if alertRole in dcMember.roles:
            await dcMember.remove_roles(alertRole, reason="User unsubscribed from " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return False
        else:
            await dcMember.add_roles(alertRole, reason="User subscribed to " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return True


    def getState(self, dcGuild, bbGuild, dcMember):
        alertRole = utils.get(dcGuild.roles, id=bbGuild.getUserAlertRoleID(userAlertsTypesIDs[type(self)]))
        return alertRole in dcMember.roles


    async def setState(self, dcGuild, bbGuild, dcMember, newState):
        alertRole = utils.get(dcGuild.roles, id=bbGuild.getUserAlertRoleID(userAlertsTypesIDs[type(self)]))
        if alertRole in dcMember.roles and not newState:
            await dcMember.remove_roles(alertRole, reason="User unsubscribed from " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return False
        elif alertRole not in dcMember.roles and newState:
            await dcMember.add_roles(alertRole, reason="User subscribed to " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return True



class UA_Shop_Refresh(GuildRoleUserAlert):
    def __init__(self, state):
        super(UA_Shop_Refresh, self).__init__()

class UA_Bounties(GuildRoleUserAlert):
    def __init__(self, state):
        super(UA_Bounties, self).__init__()


class UA_Duels_Challenge_Incoming_New(StateUserAlert):
    def __init__(self, state):
        super(UA_Duels_Challenge_Incoming_New, self).__init__(state)
        
class UA_Duels_Challenge_Incoming_Cancel(StateUserAlert):
    def __init__(self, state):
        super(UA_Duels_Challenge_Incoming_Cancel, self).__init__(state)


class UA_System_Updates_Major(GuildRoleUserAlert):
    def __init__(self, state):
        super(UA_System_Updates_Major, self).__init__()

class UA_System_Updates_Minor(GuildRoleUserAlert):
    def __init__(self, state):
        super(UA_System_Updates_Minor, self).__init__()

class UA_System_Misc(GuildRoleUserAlert):
    def __init__(self, state):
        super(UA_System_Misc, self).__init__()


userAlertsIDsTypes = {  "bounties_new": UA_Bounties,
                        
                        "shop_refresh": UA_Shop_Refresh,

                        "duels_challenge_incoming_new": UA_Duels_Challenge_Incoming_New,
                        "duels_challenge_incoming_cancel": UA_Duels_Challenge_Incoming_Cancel,
                        
                        "system_updates_major": UA_System_Updates_Major,
                        "system_updates_minor": UA_System_Updates_Minor,
                        "system_misc": UA_System_Misc}

userAlertsTypesIDs = {  UA_Bounties: "bounties_new",
                        
                        UA_Shop_Refresh: "shop_refresh",

                        UA_Duels_Challenge_Incoming_New: "duels_challenge_incoming_new",
                        UA_Duels_Challenge_Incoming_Cancel: "duels_challenge_incoming_cancel",
                        
                        UA_System_Updates_Major: "system_updates_major",
                        UA_System_Updates_Minor: "system_updates_minor",
                        UA_System_Misc: "system_misc"}

userAlertsTypesNames = {UA_Bounties: "new bounties",
    
                        UA_Shop_Refresh: "new shop stock",

                        UA_Duels_Challenge_Incoming_New: "new duel challenges",
                        UA_Duels_Challenge_Incoming_Cancel: "cancelled duel challenges",
                        
                        UA_System_Updates_Major: "BountyBot major updates",
                        UA_System_Updates_Minor: "BountyBot minor updates",
                        UA_System_Misc: "BountyBot misc. announcements"}