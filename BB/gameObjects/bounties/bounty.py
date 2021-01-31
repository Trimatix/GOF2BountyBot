# Typing imports
from __future__ import annotations
from typing import Dict, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from ...bbDatabases import bountyDB

from . import bountyConfig
from ...bbConfig import bbData
from . import criminal
from ...baseClasses import serializable


class Bounty(serializable.Serializable):
    """A bounty listing for a criminal, to be hunted down by players.

    :var criminal: The criminal who is being hunted
    :vartype criminal: criminal
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

    def __init__(self, criminalObj : criminal = None, config : bountyConfig = None, bountyDB : bountyDB.BountyDB = None, dbReload : bool = False):
        """
        :param criminalObj: The criminal to be wanted. Give None to randomly generate a criminal. (Default None)
        :type criminalObj: criminal or None
        :param config: a bountyconfig describing all aspects of this bounty. Give None to randomly generate one. (Default None)
        :type config: bountyConfig or None
        :param bountyDB: The database of currenly active bounties. This is required unless dbReload is True. (Default None)
        :type bountyDB: bountyDB or None
        :param bool dbReload: Give True if this bounty is being created during bot bootup, False otherwise. This currently toggles whether the passed bounty is checked for existence or not. (Default False)
        :raise ValueError: When dbReload is False but bountyDB is not given
        """
        if not dbReload and bountyDB is None:
            raise ValueError("Bounty constructor: No bounty database given")
        makeFresh = criminalObj is None

        if config is None:
            # generate bounty details and validate given details
            config = bountyConfig.BountyConfig() if makeFresh else bountyConfig.BountyConfig(faction=criminalObj.faction, name=criminalObj.name)

        if not config.generated:
            config.generate(bountyDB, noCriminal=makeFresh, forceKeepChecked=dbReload, forceNoDBCheck=dbReload)

        if makeFresh:
            if config.builtIn:
                self.criminal = bbData.builtInCriminalObjs[config.name]
                # builtIn criminals cannot be players, so just equip the ship
                # self.criminal.equipShip(config.ship)
            else:
                self.criminal = criminal.Criminal(config.name, config.faction, config.icon, isPlayer=config.isPlayer, aliases=config.aliases, wiki=config.wiki)
                # Don't just claim player ships! players could unequip ship items. Take a deep copy of the ship
                if config.isPlayer:
                    self.criminal.copyShip(config.ship)

        else:
            self.criminal = criminalObj

        self.faction = self.criminal.faction
        self.issueTime = config.issueTime
        self.endTime = config.endTime
        self.route = config.route
        self.reward = config.reward
        self.checked = config.checked
        self.answer = config.answer

        
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
        rewards = {}
        checkedSystems = 0
        for system in self.route:
            if self.systemChecked(system):
                checkedSystems += 1
                if self.checked[system] not in rewards:
                    rewards[self.checked[system]] = {"reward":0,"checked":0,"won":False}

        uncheckedSystems = len(self.route) - checkedSystems

        for system in self.route:
            if self.systemChecked(system):
                rewards[self.checked[system]]["checked"] += 1
                if self.answer == system:
                    rewards[self.checked[system]]["reward"] += int(self.reward / len(self.route)) * (uncheckedSystems + 1)
                    rewards[self.checked[system]]["won"] = True
                else:
                    rewards[self.checked[system]]["reward"] += int(self.reward / len(self.route))
        return rewards

    def toDict(self, **kwargs) -> dict:
        """Serialize this bounty to dictionary, to be saved to file.

        :return: A dictionary representation of this bounty.
        :rtype: dict
        """
        return {"faction": self.faction, "route": self.route, "answer": self.answer, "checked": self.checked, "reward": self.reward, "issueTime": self.issueTime, "endTime": self.endTime, "criminal": self.criminal.toDict(**kwargs)}


    @classmethod
    def fromDict(cls, bounty : dict, **kwargs) -> Bounty:
        """Factory function constructing a new bounty from a dictionary serialized description - the opposite of bounty.toDict

        :param dict bounty: Dictionary containing all information needed to construct the desired bounty
        :param bool dbReload: Give True if this bounty is being created during bot bootup, False otherwise. This currently toggles whether the passed bounty is checked for existence or not. (Default False)
        """
        dbReload = kwargs["dbReload"] if "dbReload" in kwargs else False
        return Bounty(dbReload=dbReload,
                        criminalObj=criminal.Criminal.fromDict(bounty["criminal"]), 
                        config=bountyConfig.BountyConfig(faction=bounty["faction"], route=bounty["route"], answer=bounty["answer"], checked=bounty["checked"], reward=bounty["reward"], issueTime=bounty["issueTime"], endTime=bounty["endTime"]))
