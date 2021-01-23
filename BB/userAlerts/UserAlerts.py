# Typing imports
from typing import TYPE_CHECKING, Union, List
if TYPE_CHECKING:
    from ..gameObjects import bbGuild

from discord import utils, Guild, Member
from abc import ABC, abstractmethod
from ..bbConfig import bbConfig

class UABase(ABC):
    """A base class representing a subscription to a single type of
    alert (UserAlert) - for example, a ping or DM when a certain event occurs.
    This class does not differenciate or implement any method of issueing alerts.
    UserAlerts have a state (off/on), a toggle method (switches state), and a setState method (switches to the specified state).
    The state is not necessarily stored in an object attribute.
    A UserAlert may not necessarily depend on the guild in which it was set.
    """

    @abstractmethod
    async def toggle(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member) -> bool:
        # TODO: Stop requesting bbGuild, look it up from bbGlobals using dcGuild
        """Invert the alert's state (i.e if currently off, switch to on, and vice versa) for the given member in the given guild.

        :param discord.Guild dcGuild: The guild in which to toggle the alert. Some UserAlert implementations ignore this parameter.
        :param bbGuild bbGuild: The bbGuild corresponding to dcGuild. Parameter is marked for removal from this method's signature.
        :param discord.Member dcMember: The member for which the alert should be toggled.
        :return: The new state of the alert.
        :rtype: bool
        """
        pass


    @abstractmethod
    def getState(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member) -> bool:
        # TODO: Stop requesting bbGuild, look it up from bbGlobals using dcGuild
        """Get the state of the alert for the given member in the given guild.

        :param discord.Guild dcGuild: The guild in which to get the alert state. Some UserAlert implementations ignore this parameter.
        :param bbGuild bbGuild: The bbGuild corresponding to dcGuild. Parameter is marked for removal from this method's signature.
        :param discord.Member dcMember: The member for whom to get the alert state of.
        :return: The current state of the alert.
        :rtype: bool
        """
        pass


    @abstractmethod
    async def setState(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member, newState : bool) -> bool:
        # TODO: Stop requesting bbGuild, look it up from bbGlobals using dcGuild
        """Set the alert's state for the given member in the given guild, to the given state.

        :param discord.Guild dcGuild: The guild in which to set the alert state. Some UserAlert implementations ignore this parameter.
        :param bbGuild bbGuild: The bbGuild corresponding to dcGuild. Parameter is marked for removal from this method's signature.
        :param discord.Member dcMember: The member for which the alert should be set.
        :param bool newState: The desired new state of the alert.
        :return: The new state of the alert.
        :rtype: bool
        """
        pass


class StateUserAlert(UABase):
    """A simple toggle-switch based UserAlert implementation that does not interface with discord or the rest of BountyBot in any way. Essentially acts as a boolean variable.
    In all methods, the given guild and member are ignored.

    :var state: The state of the alert subscription (enabled/disabled).
    :vartype state: bool
    """

    def __init__(self, state):
        """
        :param bool state: The initial state of the alert (enabled/disabled)
        """
        super(StateUserAlert, self).__init__()
        self.state = state

    
    async def toggle(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member) -> bool:
        """Invert the alert's state (i.e if currently off, switch to on, and vice versa).

        :param discord.Guild dcGuild: Ignored
        :param bbGuild bbGuild: Ignored
        :param discord.Member dcMember: Ignored
        :return: The new state of the alert.
        :rtype: bool
        """
        self.state = not self.state
        return self.state


    def getState(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member) -> bool:
        """Get the state of the alert.

        :param discord.Guild dcGuild: Ignored
        :param bbGuild bbGuild: Ignored
        :param discord.Member dcMember: Ignored
        :return: The current state of the alert.
        :rtype: bool
        """
        return self.state

    
    async def setState(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member, newState : bool) -> bool:
        """Set the alert's state.

        :param discord.Guild dcGuild: Ignored
        :param bbGuild bbGuild: Ignored
        :param discord.Member dcMember: Ignored
        :param bool newState: The desired new state of the alert.
        :return: The new state of the alert.
        :rtype: bool
        """
        self.state = newState
        return newState


class GuildRoleUserAlert(UABase):
    """A UserAlert whose state is determined by the owning user holding a certain role in a guild.
    By design, the UA object holds no knowledge of its own state, as a user's holding of a role may change
    outside of the UA's discression. The UA also does not hold knowledge of the role to toggle, allowing different guilds
    to use different roles for the same UA.
    """

    def __init__(self):
        super(GuildRoleUserAlert, self).__init__()


    async def toggle(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member) -> bool:
        """Invert the alert's state (i.e if currently off, switch to on, and vice versa) of the alert,
        by fetching the role that the given guild has selected for this alert, and granting/removing it to the given member.

        :param discord.Guild dcGuild: The guild in which to toggle the alert.
        :param bbGuild bbGuild: The bbGuild corresponding to dcGuild. Parameter is marked for removal from this method's signature.
        :param discord.Member dcMember: The member for which the alert should be toggled.
        :return: The new state of the alert.
        :rtype: bool
        """
        alertRole = utils.get(dcGuild.roles, id=bbGuild.getUserAlertRoleID(userAlertsTypesIDs[type(self)]))
        if alertRole is None:
            raise ValueError("Requested guild does not have a role set for the requested alert: " + userAlertsTypesIDs[type(self)])
        if alertRole in dcMember.roles:
            await dcMember.remove_roles(alertRole, reason="User unsubscribed from " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return False
        else:
            await dcMember.add_roles(alertRole, reason="User subscribed to " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return True


    def getState(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member) -> bool:
        """Get the state of the alert for the given member in the given guild, by deciding the member's ownership of the role bbGuild
        has selected for this alert type.

        :param discord.Guild dcGuild: The guild in which to get the alert state.
        :param bbGuild bbGuild: The bbGuild corresponding to dcGuild. Parameter is marked for removal from this method's signature.
        :param discord.Member dcMember: The member for whom to get the alert state of.
        :return: The current state of the alert.
        :rtype: bool
        """
        alertRole = utils.get(dcGuild.roles, id=bbGuild.getUserAlertRoleID(userAlertsTypesIDs[type(self)]))
        return alertRole in dcMember.roles


    async def setState(self, dcGuild : Guild, bbGuild : 'bbGuild.bbGuild', dcMember : Member, newState : bool) -> bool:
        """Set the alert's state for the given member in the given guild, to the given state, granting the guild's selected role
        where newState is True, and taking the guild's selected role where newState is False.

        :param discord.Guild dcGuild: The guild in which to set the alert state.
        :param bbGuild bbGuild: The bbGuild corresponding to dcGuild. Parameter is marked for removal from this method's signature.
        :param discord.Member dcMember: The member for which the alert should be set.
        :param bool newState: The desired new state of the alert.
        :return: The new state of the alert.
        :rtype: bool
        """
        alertRole = utils.get(dcGuild.roles, id=bbGuild.getUserAlertRoleID(userAlertsTypesIDs[type(self)]))
        if alertRole in dcMember.roles and not newState:
            await dcMember.remove_roles(alertRole, reason="User unsubscribed from " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return False
        elif alertRole not in dcMember.roles and newState:
            await dcMember.add_roles(alertRole, reason="User subscribed to " + userAlertsTypesNames[type(self)] + " notifications via BB command")
            return True



class UA_Shop_Refresh(GuildRoleUserAlert):
    """Alert users when the guild's shop refreshes using a role.
    """

    def __init__(self, state):
        """
        :param state: Ignored
        """
        super(UA_Shop_Refresh, self).__init__()

class UA_Bounties(GuildRoleUserAlert):
    """Alert a guild's members when a new bounty spawns, using a role.
    """

    def __init__(self, state):
        """
        :param state: Ignored
        """
        super(UA_Bounties, self).__init__()


class UA_Duels_Challenge_Incoming_New(StateUserAlert):
    """Alert a user, independant of guild, when a user challenges them to a duel.
    """

    def __init__(self, state):
        """
        :param state: The initial state of the alert (enabled/disabled)
        """
        super(UA_Duels_Challenge_Incoming_New, self).__init__(state)
        

class UA_Duels_Challenge_Incoming_Cancel(StateUserAlert):
    """Alert a user, independant of guild, when a user cancels a duel they issued to the user.
    """

    def __init__(self, state):
        """
        :param state: The initial state of the alert (enabled/disabled)
        """
        super(UA_Duels_Challenge_Incoming_Cancel, self).__init__(state)


class UA_System_Updates_Major(GuildRoleUserAlert):
    """Alert a guild's members when a new major bot update is released, using a role mention.
    """

    def __init__(self, state):
        """
        :param state: Ignored
        """
        super(UA_System_Updates_Major, self).__init__()


class UA_System_Updates_Minor(GuildRoleUserAlert):
    """Alert a guild's members when a new minor bot update is released, using a role mention.
    """

    def __init__(self, state):
        """
        :param state: Ingored
        """
        super(UA_System_Updates_Minor, self).__init__()


class UA_System_Misc(GuildRoleUserAlert):
    """Alert a guild's members for bot global announcements/broadcasts, using a role mention.
    """

    def __init__(self, state):
        """
        :param state: Ignored
        """
        super(UA_System_Misc, self).__init__()


# Translate UA ID strings into types
userAlertsIDsTypes = {  "bounties_new": UA_Bounties,
                        
                        "shop_refresh": UA_Shop_Refresh,

                        "duels_challenge_incoming_new": UA_Duels_Challenge_Incoming_New,
                        "duels_challenge_incoming_cancel": UA_Duels_Challenge_Incoming_Cancel,
                        
                        "system_updates_major": UA_System_Updates_Major,
                        "system_updates_minor": UA_System_Updates_Minor,
                        "system_misc": UA_System_Misc}

# Translate UA types into ID strings
userAlertsTypesIDs = {  UA_Bounties: "bounties_new",
                        
                        UA_Shop_Refresh: "shop_refresh",

                        UA_Duels_Challenge_Incoming_New: "duels_challenge_incoming_new",
                        UA_Duels_Challenge_Incoming_Cancel: "duels_challenge_incoming_cancel",
                        
                        UA_System_Updates_Major: "system_updates_major",
                        UA_System_Updates_Minor: "system_updates_minor",
                        UA_System_Misc: "system_misc"}

# Translate UA types into user-friendly alert name strings
userAlertsTypesNames = {UA_Bounties: "new bounties",
    
                        UA_Shop_Refresh: "new shop stock",

                        UA_Duels_Challenge_Incoming_New: "new duel challenges",
                        UA_Duels_Challenge_Incoming_Cancel: "cancelled duel challenges",
                        
                        UA_System_Updates_Major: "BountyBot major updates",
                        UA_System_Updates_Minor: "BountyBot minor updates",
                        UA_System_Misc: "BountyBot misc. announcements"}


def getAlertIDFromHeirarchicalAliases(alertName : Union[str, List[str]]) -> List[str]:
    """Look up a given multi-levelled alert reference, and return a list of associated UserAlert IDs.
    This function implements:
    - user friendly alert names
    - user alert heirarchical referencing
    - multi-alert references TODO: Currently unused and/or broken. Implement bot updates all
    - aliases at every level of the alert reference

    ⚠ If the given string could not be deferenced to UserAlerts, then the 0th element of the returned list
    will be 'ERR'. Before handling the returned list, check to make sure this is not the case.

    TODO: Replace with a LUT implementation

    # :param alertName: A reference to an alert. Heirarchy levels can be given as a space-separated string, or ordered list elements. E.g: 'bot patches major' or ['bot', 'patches', 'major']
    :type alertName: list[str] or str
    :return: A list of UserAlert IDs in accordance with UserAlerts.userAlertsIDsTypes, that are associated with the requested alert reference.
    :rtype: list[str]
    """
    if type(alertName) != list:
        alertName = alertName.split(" ")

    if alertName[0] in ["bounty", "bounties"]:
        return ["bounties_new"]

    elif alertName[0] in ["duel", "duels", "fight", "fights"]:
        if len(alertName) < 2:
            return ["ERR", ":x: Please provide the type of duel notification you would like. E.g: `duels new`"]
        if alertName[1] in ["new", "challenge", "me", "incoming"]:
            return ["duels_challenge_incoming_new"]
        elif alertName[1] in ["cancel", "cancelled", "expire", "expired", "end", "ended"]:
            return ["duels_challenge_incoming_cancel"]
        else:
            return ["ERR", ":x: Unknown duel notification type! Valid types include `new` or `cancel`."]

    elif alertName[0] in ["shop", "shops"]:
        if len(alertName) < 2:
            return ["ERR", ":x: Please provide the type of shop notification you would like. E.g: `shop refresh`"]
        if alertName[1] in ["refresh", "new", "reset", "stock"]:
            return ["shop_refresh"]
        else:
            return ["ERR", ":x: Unknown shop notification type! Valid types include `refresh`."]

    elif alertName[0] in ["bot", "system", "sys"]:
        if len(alertName) < 2:
            return ["ERR", ":x: Please provide the type of system notification you would like. E.g: `bot updates major`"]
        if alertName[1] in ["update", "updates", "patch", "patches", "version", "versions"]:
            if len(alertName) < 3:
                return ["ERR", ":x: Please provide the type of updates pings you would like! Valid types include `major` and `minor`."]
            elif alertName[2] in ["major", "big", "large"]:
                return ["system_updates_major"]
            elif alertName[2] in ["minor", "small", "bug", "fix"]:
                return ["system_updates_minor"]
            else:
                return ["ERR", ":x: Unknown system updates notification type! Valid types include `major` and `minor`."]

        elif alertName[1] in ["misc", "misc.", "announce", "announcement", "announcements", "announces", "miscellaneous"]:
            return ["system_misc"]
        else:
            return ["ERR", ":x: Unknown system notification type! Valid types include `updates` and `misc`."]

    # elif alertName[0] in bbConfig.validItemNames and alertName[0] != "all":
    #     return ["ERR", "Item notifications have not been implemented yet! \:("]
    else:
        return ["ERR", ":x: Unknown notification type! Please refer to `" + bbConfig.commandPrefix + "help notify`"]