import bbBountyConfig
import bbdata
import bbCriminal

class Bounty:
    criminal = None
    builtIn = False
    issueTime = -1
    route = []
    reward = 0.0
    endTime = -1
    faction = ""
    checked = {}
    answer = ""

    def __init__(self, criminalObj=None, config=None, bountyDB=None, dbReload=False):
        if not dbReload and bountyDB is None:
            raise ValueError("Bounty constructor: No bounty database given")
        makeFresh = criminalObj is None

        if makeFresh and config is None:
            config = bbBountyConfig.BountyConfig()

        if not config.generated:
            config.generate(bountyDB, noCriminal=makeFresh, forceKeepChecked=dbReload, forceNoDBCheck=dbReload)

        if makeFresh:
            if config.builtIn:
                self.criminal = bbdata.criminals[config.name]
            else:
                self.criminal = bbCriminal.Criminal(config.name, config.faction, config.icon)
        
        else:
            if bountyDB.bountyNameExists(criminalObj.name):
                raise IndexError("Bounty constructor: attempted to create pre-existing bounty: " + criminalObj.name)
            
            config.builtIn = not criminalObj.isPlayer and criminalObj.name in bbdata.bountyNames
            self.criminal = criminalObj

        
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
                    rewards[self.checked[system]]["reward"] += (self.reward / len(self.route)) * (uncheckedSystems + 1)
                    rewards[self.checked[system]]["won"] = True
                else:
                    rewards[self.checked[system]]["reward"] += self.reward / len(self.route)
        return rewards

    def toDict(self):
        data = {"faction": self.faction, "route": self.route, "answer": self.answer, "checked": self.checked, "reward": self.reward, "issueTime": self.issueTime, "endTime": self.endTime}
        if self.builtIn:
            print("BUILT IN")
            data["criminal"] = {"builtIn":True, "name":self.criminal.name}
        else:
            print("NOT BUILT IN")
            data["criminal"] = {"builtIn":False, "isPlayer": self.criminal.isPlayer, "name":self.criminal.name, "icon":self.criminal.icon}
        return data



def fromDict(bounty, dbReload=False):
    return Bounty(dbReload=dbReload, \
                    criminalObj=bbCriminal.fromDict(bounty["criminal"]), \
                    config=bbBountyConfig.bbconfig(faction=bounty["faction"], route=bounty["route"], answer=bounty["answer"], checked=bounty["checked"], reward=bounty["reward"], issueTime=bounty["issueTime"], endTime=bounty["endTime"]))
