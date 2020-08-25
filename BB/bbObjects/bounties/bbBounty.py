from . import bbBountyConfig
from ...bbConfig import bbData, bbConfig
from . import bbCriminal

class Bounty:
    def __init__(self, criminalObj=None, config=None, bountyDB=None, dbReload=False):
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
        self.checked = config.checked
        self.answer = config.answer
        if self.criminal.techLevel == -1:
            self.criminal.techLevel = config.techLevel

        
    # return 0 => system not in route
    # return 1 => system already checked
    # return 2 => system was unchecked, but is not the answer
    # return 3 => win!
    def check(self, system, userID):
        if system not in self.route:
            return 0
        elif self.systemChecked(system):
            return 1
        else:
            self.checked[system] = userID
            if self.answer == system:
                return 3
            return 2

    def systemChecked(self, system):
        return self.checked[system] != -1

    def calcRewards(self):
        creditsPool = self.reward
        
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
                    currentReward = bbConfig.bPointsToCreditsRatio
                    rewards[self.checked[system]]["reward"] += currentReward
                    creditsPool -= currentReward

        

        rewards[self.checked[self.answer]]["reward"] = creditsPool
        rewards[self.checked[self.answer]]["won"] = True

        for user in rewards:
            rewards[user]["xp"] = int(rewards[user]["reward"] * bbConfig.bountyRewardToXPGainMult)
            
        return rewards

    def toDict(self):
        return {"faction": self.faction, "route": self.route, "answer": self.answer, "checked": self.checked, "reward": self.reward, "issueTime": self.issueTime, "endTime": self.endTime, "criminal": self.criminal.toDict()}



def fromDict(bounty, dbReload=False):
    return Bounty(dbReload=dbReload,
                    criminalObj=bbCriminal.fromDict(bounty["criminal"]), 
                    config=bbBountyConfig.BountyConfig(faction=bounty["faction"], route=bounty["route"], answer=bounty["answer"], checked=bounty["checked"], reward=bounty["reward"], issueTime=bounty["issueTime"], endTime=bounty["endTime"]))
