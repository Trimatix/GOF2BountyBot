from . import bbShop
from ..bbDatabases import bbBountyDB
from .bounties.bountyBoards import BountyBoardChannel
from ..userAlerts import UserAlerts
from discord import channel, Client
from typing import List
from ..bbConfig import bbConfig, bbData

class bbGuild:
    """A class representing a guild in discord, and storing extra BountyBot-related information about it. 
    
    :var id: The ID of the guild, directly corresponding to a discord guild's ID.
    :vartype id: int
    :var announceChannel: The ID of this guild's announcements chanel. -1 when no announce channel is set for this guild.
    :vartype announceChannel: int
    :var playChannel: The ID of this guild's bounty playing chanel. -1 when no bounty playing channel is set for this guild.
    :vartype playChannel: int
    :var shop: This guild's bbShop object
    :vartype shop: bbShop
    :var alertRoles: A dictionary of user alert IDs to guild role IDs.
    :vartype alertRoles: dict[str, int]
    :var bountyBoardChannel: A BountyBoardChannel object implementing this guild's bounty board channel if it has one, None otherwise.
    :vartype bountyBoardChannel: BountyBoardChannel
    :var hasBountyBoardChannel: Whether this guild has a bounty board channel or not
    :vartype hasBountyBoardChannel: bool
    :var ownedRoleMenus: The number of ReactionRolePickers present in this guild
    :vartype ownedRoleMenus: int
    :var bountiesDB: This guild's active bounties
    :vartype bountiesDB: bbBountyDB.bbBountyDB
    """

    def __init__(self, id : int, bountiesDB: bbBountyDB.bbBountyDB, announceChannel=-1, playChannel=-1, shop=None, bountyBoardChannel=None, alertRoles={}, ownedRoleMenus=0):
        """
        :param int id: The ID of the guild, directly corresponding to a discord guild's ID.
        :param bbBountyDB.bbBountyDB bountiesDB: This guild's active bounties
        :param int announceChannel: The ID of this guild's announcements chanel. -1 when no announce channel is set for this guild.
        :param int playChannel: The ID of this guild's bounty playing chanel. -1 when no bounty playing channel is set for this guild.
        :param bbShop shop: This guild's bbShop object
        :param dict[str, int] alertRoles: A dictionary of user alert IDs to guild role IDs.
        :param BoardBoardChannel bountyBoardChannel: A BountyBoardChannel object implementing this guild's bounty board channel if it has one, None otherwise.
        :param int ownedRoleMenus: The number of ReactionRolePickers present in this guild
        :raise TypeError: When given an incompatible argument type
        """
        if type(id) == float:
            id = int(id)
        elif type(id) != int:
            raise TypeError("id must be int, given " + str(type(id)))

        if type(announceChannel) == float:
            announceChannel = int(announceChannel)
        elif type(announceChannel) != int:
            raise TypeError("announceChannel must be int, given " + str(type(announceChannel)))

        if type(playChannel) == float:
            playChannel = int(playChannel)
        elif type(playChannel) != int:
            raise TypeError("playChannel must be int, given " + str(type(playChannel)))
        
        if shop is not None and type(shop) != bbShop.bbShop:
            raise TypeError("shop must be bbShop, given " + str(type(shop)))

        self.id = id
        self.announceChannel = announceChannel
        self.playChannel = playChannel

        self.shop = bbShop.bbShop() if shop is None else shop
        
        self.alertRoles = {}
        for alertID in UserAlerts.userAlertsIDsTypes.keys():
            if issubclass(UserAlerts.userAlertsIDsTypes[alertID], UserAlerts.GuildRoleUserAlert):
                self.alertRoles[alertID] = alertRoles[alertID] if alertID in alertRoles else -1
        
        self.bountyBoardChannel = bountyBoardChannel
        self.hasBountyBoardChannel = bountyBoardChannel is not None
        self.ownedRoleMenus = ownedRoleMenus
        self.bountiesDB = bountiesDB


    def getAnnounceChannelId(self) -> int:
        """Get the discord channel ID of the guild's announcements channel.

        :return: the ID of the guild's announcements channel
        :rtype: int
        :raise ValueError: If this guild does not have an announcements channel
        """
        if not self.hasAnnounceChannel():
            raise ValueError("This guild has no announce channel set")
        return self.announceChannel


    def getPlayChannelId(self) -> int:
        """Get the discord channel ID of the guild's bounty playing channel.

        :return: the ID of the guild's bounty playing channel
        :raise ValueError: If this guild does not have a play channel
        :rtype: int
        """
        if not self.hasPlayChannel():
            raise ValueError("This guild has no play channel set")
        return self.playChannel


    def setAnnounceChannelId(self, announceChannelId : int):
        """Set the discord channel ID of the guild's announcements channel.

        :param int announceChannelId: The ID of the guild's new announcements channel
        """
        self.announceChannel = announceChannelId


    def setPlayChannelId(self, playChannelId : int):
        """Set the discord channel ID of the guild's bounty playing channel.

        :param int announceChannelId: The ID of the guild's new bounty playing channel
        """
        self.playChannel = playChannelId
    

    def hasAnnounceChannel(self) -> bool:
        """Whether or not this guild has an announcements channel

        :return: True if this guild has a announcements channel, False otherwise
        :rtype bool:
        """
        return self.announceChannel != -1


    def hasPlayChannel(self) -> bool:
        """Whether or not this guild has a play channel

        :return: True if this guild has a play channel, False otherwise
        :rtype bool:
        """
        return self.playChannel != -1


    def removePlayChannel(self):
        """Remove and deactivate this guild's announcements channel.

        :raise ValueError: If this guild does not have a play channel
        """
        if not self.hasPlayChannel():
            raise ValueError("Attempted to remove play channel on a bbGuild that has no playChannel")
        self.playChannel = -1

    
    def removeAnnounceChannel(self):
        """Remove and deactivate this guild's play channel.

        :raise ValueError: If this guild does not have an announcements channel
        """
        if not self.hasAnnounceChannel():
            raise ValueError("Attempted to remove announce channel on a bbGuild that has no announceChannel")
        self.announceChannel = -1



    def getUserAlertRoleID(self, alertID : str) -> int:
        """Get the ID of this guild's alerts role for the given alert ID.

        :param str alertID: The alert ID for which the role ID should be fetched
        :return: The ID of the discord role that this guild mentions for the given alert ID.
        :rtype: int
        """
        return self.alertRoles[alertID]


    def setUserAlertRoleID(self, alertID : str, roleID : int):
        """Set the ID of this guild's alerts role for the given alert ID.

        :param str alertID: The alert ID for which the role ID should be set
        :param int roleID: The ID of the role which this guild should mention when alerting alertID
        """
        self.alertRoles[alertID] = roleID


    def removeUserAlertRoleID(self, alertID : str):
        """Remove the stored role and deactivate alerts for the given alertID

        :param str alertID: The alert ID for which the role ID should be removed
        """
        self.alertRoles[alertID] = -1

    
    def hasUserAlertRoleID(self, alertID : str) -> bool:
        """Decide whether or not this guild has a role set for the given alert ID.

        :param str alertID: The alert ID for which the role existence should be tested
        :return: True if this guild has a role set to mention for alertID
        :rtype: bool
        :raise KeyError: If given an unrecognised alertID
        """
        if alertID in self.alertRoles:
            return self.alertRoles[alertID] != -1
        raise KeyError("Unknown GuildRoleUserAlert ID: " + alertID)


    
    async def addBountyBoardChannel(self, channel : channel, client : Client, factions : List[str]):
        """Set this guild's bounty board channel.

        :param discord.Channel channel: The channel where bounty listings should be posted
        :param discord.Client client: A logged in client used to fetch the channel and any existing listings.
        :param list[str] factions: A list of faction names with which bounty listings can be associated
        :raise RuntimeError: If the guild already has an active BountyBoardChannel
        """
        if self.hasBountyBoardChannel:
            raise RuntimeError("Attempted to assign a bountyboard channel for guild " + str(self.id) + " but one is already assigned")
        self.bountyBoardChannel = BountyBoardChannel.BountyBoardChannel(channel.id, {}, -1)
        await self.bountyBoardChannel.init(client, factions)
        self.hasBountyBoardChannel = True

    
    def removeBountyBoardChannel(self):
        """Deactivate this guild's BountyBoardChannel. This does not remove any active bounty listing messages.

        :raise RuntimeError: If this guild does not have an active BountyBoardChannel.
        """
        if not self.hasBountyBoardChannel:
            raise RuntimeError("Attempted to remove a bountyboard channel for guild " + str(self.id) + " but none is assigned")
        self.bountyBoardChannel = None
        self.hasBountyBoardChannel = False


    def toDictNoId(self) -> dict:
        """Serialize this bbGuild into dictionary format to be saved to file.

        :return: A dictionary containing all information needed to reconstruct this bbGuild
        :rtype: dict
        """
        return {"announceChannel":self.announceChannel, "playChannel":self.playChannel, 
                "bountyBoardChannel": self.bountyBoardChannel.toDict() if self.hasBountyBoardChannel else None,
                "alertRoles": self.alertRoles,
                "shop": self.shop.toDict(),
                "ownedRoleMenus": self.ownedRoleMenus,
                "bountiesDB": self.bountiesDB.toDict()
                }


def fromDict(id : int, guildDict : dict, dbReload=False) -> bbGuild:
    """Factory function constructing a new bbGuild object from the information in the provided guildDict - the opposite of bbGuild.toDictNoId

    :param int id: The discord ID of the guild
    :param dict guildDict: A dictionary containing all information required to build the bbGuild object
    :param bool dbReload: Whether or not this guild is being created during the initial database loading phase of bountybot. This is used to toggle name checking in bbBounty contruction.
    :return: A bbGuild according to the information in guildDict
    :rtype: bbGuild
    """
    if "bountiesDB" in guildDict:
        bountiesDB = bbBountyDB.fromDict(guildDict["bountiesDB"], bbConfig.maxBountiesPerFaction, dbReload=dbReload)
    else:
        bountiesDB = bbBountyDB.bbBountyDB(bbData.bountyFactions, bbConfig.maxBountiesPerFaction)

    return bbGuild(id, bountiesDB, announceChannel=guildDict["announceChannel"], playChannel=guildDict["playChannel"],
                    shop=bbShop.fromDict(guildDict["shop"]) if "shop" in guildDict else bbShop.bbShop(),
                    bountyBoardChannel=BountyBoardChannel.fromDict(guildDict["bountyBoardChannel"]) if "bountyBoardChannel" in guildDict and guildDict["bountyBoardChannel"] != -1 else None,
                    alertRoles=guildDict["alertRoles"] if "alertRoles" in guildDict else {}, ownedRoleMenus=guildDict["ownedRoleMenus"] if "ownedRoleMenus" in guildDict else 0)
