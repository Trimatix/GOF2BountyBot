# Typing imports
from __future__ import annotations
from typing import Dict, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from ...bbDatabases import bbBountyDB

from . import bbBountyConfig
from ...bbConfig import bbData, bbConfig
from . import bbCriminal
from ...baseClasses import bbSerializable


class Bounty(bbSerializable.bbSerializable):
    """A bounty listing for a criminal, to be hunted down by players.

    :var criminal: The criminal who is being hunted
    :vartype criminal: bbCriminal
    :var issueTime: The time at which the bounty was created
    :vartype issueTime: datetime.datetime
    :var route: the names of systems that are in the route
    :vartype route: list[str]
    :var reward: the number of credits available to contributing players
    :vartype reward: int
    :var endTime: the time at which the bounty should automatically expire
    :vartype endTime: datetime.datetime
    :var faction: the faction to which this bounty belongs
    :vartype faction: str
    :var checked: A dictionary tracking which player checked each system. Keys are system names, values are user ids. values for unchecked systems are -1.
    :vartype checked: dict[str, int]
    :var answer: The name of the system where the criminal is located
    :vartype answer: str
    """

    def __init__(self, criminalObj : bbCriminal = None, config : bbBountyConfig = None, bountyDB : bbBountyDB.bbBountyDB = None, dbReload : bool = False):
        """
        :param criminalObj: The criminal to be wanted. Give None to randomly generate a criminal. (Default None)
        :type criminalObj: bbCriminal or None
        :param config: a bountyconfig describing all aspects of this bounty. Give None to randomly generate one. (Default None)
        :type config: bbBountyConfig or None
        :param bountyDB: The database of currenly active bounties. This is required unless dbReload is True. (Default None)
        :type bountyDB: bbBountyDB or None
        :param bool dbReload: Give True if this bounty is being created during bot bootup, False otherwise. This currently toggles whether the passed bounty is checked for existence or not. (Default False)
        :raise ValueError: When dbReload is False but bountyDB is not given
        """
        if not dbReload and bountyDB is None:
            raise ValueError("Bounty constructor: No bounty database given")
        makeFresh = criminalObj is None

        if config is None:
            # generate bounty details and validate given details
            config = bbBountyConfig.BountyConfig() if makeFresh else bbBountyConfig.BountyConfig(faction=criminalObj.faction, name=criminalObj.name)

        if not config.generated:
            config.generate(bountyDB, noCriminal=makeFresh, forceKeepChecked=dbReload, forceNoDBCheck=dbReload)

        if makeFresh:
            if config.builtIn:
                self.criminal = bbData.builtInCriminalObjs[config.name]
            else:
                self.criminal = bbCriminal.Criminal(config.name, config.faction, config.icon, isPlayer=config.isPlayer, aliases=config.aliases, wiki=config.wiki)

        else:
            self.criminal = criminalObj

        if not self.criminal.hasShip:
            # Don't just claim player ships! players could unequip ship items. Take a deep copy of the ship
            if config.isPlayer:
                self.criminal.copyShip(config.activeShip)
            else:
                self.criminal.equipShip(config.activeShip)

        self.faction = self.criminal.faction
        self.issueTime = config.issueTime
        self.endTime = config.endTime
        self.route = config.route
        self.reward = config.reward
        self.rewardPerSys = config.rewardPerSys
        self.checked = config.checked
        self.answer = config.answer
        if self.criminal.techLevel == -1:
            self.criminal.techLevel = config.techLevel

        
    # return 0 => system not in route
    # return 1 => system already checked
    # return 2 => system was unchecked, but is not the answer
    # return 3 => win!
    def check(self, system : str, userID : int) -> int:
        """Check a system along the route.

        :param str system: The name of the system to check
        :param int userID: The id of the user checking the system
        :return: A symbollic integer representing the result of the check. 0 => This system is not in the bounty route. 1 => this system has already been checked. 2 => The system was unchecked, but is not the answer. 3 => answer found.
        :rtype: int
        """
        if system not in self.route:
            return 0
        elif self.systemChecked(system):
            return 1
        else:
            self.checked[system] = userID
            if self.answer == system:
                return 3
            return 2

    def systemChecked(self, system : str) -> bool:
        """Decide whether or not a system has been checked.
        
        :param str system: The system to inspect for checking
        :return: True if system has been checked yet, False otherwise
        :rtype: bool
        """
        return self.checked[system] != -1

    def calcRewards(self) -> Dict[int, Dict[str, Union[int, bool]]]:
        """Calculate the winning user, and how many credits (and, in the future, xp points) to award to which contributing users.

        :return: A dictionary of user IDs to rewards. rewards are given as a dict, giving the number of systems checked, the reward credits, and whether this user ID won or not.
        :rtype: dict[int, dict[str, int or bool]]]
        """
        creditsPool = self.reward
        rewards = {}
        checkedSystems = 0
        rewards = {}
        for system in self.route:
            if self.systemChecked(system):
                checkedSystems += 1
                if self.checked[system] not in rewards:
                    rewards[self.checked[system]] = {"reward":0,"checked":0,"won":False,"xp":0}

        uncheckedSystems = len(self.route) - checkedSystems
        winningUserID = self.checked[self.answer]

        for system in self.route:
            if self.systemChecked(system):
                rewards[self.checked[system]]["checked"] += 1
                if self.checked[system] != winningUserID:
                    # currentReward = int(self.reward / len(self.route))
                    # currentReward = bbConfig.bPointsToCreditsRatio
                    currentReward = self.rewardPerSys
                    rewards[self.checked[system]]["reward"] += currentReward
                    creditsPool -= currentReward

        

        rewards[self.checked[self.answer]]["reward"] = creditsPool
        rewards[self.checked[self.answer]]["won"] = True

        for user in rewards:
            rewards[user]["xp"] = int(rewards[user]["reward"] * bbConfig.bountyRewardToXPGainMult)
            
        return rewards

    def toDict(self, **kwargs) -> dict:
        """Serialize this bounty to dictionary, to be saved to file.

        :return: A dictionary representation of this bounty.
        :rtype: dict
        """
        return {"faction": self.faction, "route": self.route, "answer": self.answer, "checked": self.checked, "reward": self.reward, "issueTime": self.issueTime, "endTime": self.endTime, "criminal": self.criminal.toDict(**kwargs), "rewardPerSys": self.rewardPerSys}


    @classmethod
    def fromDict(cls, bounty : dict, **kwargs) -> Bounty:
        """Factory function constructing a new bbBounty from a dictionary serialized description - the opposite of bbBounty.toDict

        :param dict bounty: Dictionary containing all information needed to construct the desired bbBounty
        :param bool dbReload: Give True if this bounty is being created during bot bootup, False otherwise. This currently toggles whether the passed bounty is checked for existence or not. (Default False)
        """
        dbReload = kwargs["dbReload"] if "dbReload" in kwargs else False
        return Bounty(dbReload=dbReload,
                        criminalObj=bbCriminal.Criminal.fromDict(bounty["criminal"]), 
                        config=bbBountyConfig.BountyConfig(faction=bounty["faction"], route=bounty["route"], answer=bounty["answer"], checked=bounty["checked"], reward=bounty["reward"], rewardPerSys=bounty["rewardPerSys"], issueTime=bounty["issueTime"], endTime=bounty["endTime"]))
