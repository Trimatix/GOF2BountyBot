import random
from datetime import datetime, timedelta

from ..bbConfig import bbData, bbConfig
from .. import bbUtil

class BountyConfig:
    faction = ""
    name = ""
    isPlayer = ""
    route = []
    start = ""
    end = ""
    answer = ""
    checked = {}
    reward = -1.0
    issueTime = -1.0
    endTime = -1.0
    icon = ""
    builtIn = False
    generated = False

    def __init__(self, faction="", name="", isPlayer=None, route=[], start="", end="", answer="", checked={}, reward=-1.0, issueTime=-1.0, endTime=-1.0, icon=""):
        self.faction = faction.lower()
        self.name = name.title()
        self.isPlayer = False if isPlayer is None else isPlayer
        self.route = []
        for system in route:
            self.route.append(system.title())

        self.start = start.title()
        self.end = end.title()
        self.answer = answer.title()
        self.checked = checked
        self.reward = reward
        if type(reward) == float:
            self.reward = int(reward)
        self.issueTime = issueTime
        self.endTime = endTime
        self.icon = icon
        self.generated = False
        self.builtIn = False

        # if isPlayer and client is None:
        #     raise ValueError("BOUCONF_CONS_NOCLIENT: Attempted to make player bounty but didn't provide client '" + name + "'")
        
    
    def generate(self, bountyDB, noCriminal=True, forceKeepChecked=False, forceNoDBCheck=False):
        doDBCheck = not forceNoDBCheck
        if noCriminal:
            if self.name in bbData.bountyNames:
                self.builtIn = True
            else:
                if self.faction == "":
                    self.faction = random.choice(bbData.bountyFactions)
                    while doDBCheck and not bountyDB.factionCanMakeBounty(self.faction):
                        self.faction = random.choice(bbData.bountyFactions)

                else:
                    if self.faction not in bbData.bountyFactions:
                        raise ValueError("BOUCONF_CONS_INVFAC: Invalid faction requested '" + self.faction + "'")
                    if doDBCheck and not bountyDB.factionCanMakeBounty(self.faction):
                        raise IndexError("BOUCONF_CONS_FACDBFULL: Attempted to generate new bounty config when no slots are available for faction: '" + self.faction + "'")

                if self.name == "":
                    self.builtIn = True
                    self.name = random.choice(bbData.bountyNames[self.faction])
                    while doDBCheck and bountyDB.bountyNameExists(self.name):
                        name = random.choice(bbData.bountyNames[self.faction])
                else:
                    if doDBCheck and bountyDB.bountyNameExists(self.name):
                        raise KeyError("BountyConfig: attempted to create config for pre-existing bounty: " + name)
                    
                    if self.icon == "":
                        self.icon = bbData.rocketIcon
        
        else:
            if doDBCheck and not bountyDB.factionCanMakeBounty(self.faction):
                raise IndexError("BOUCONF_CONS_FACDBFULL: Attempted to generate new bounty config when no slots are available for faction: '" + self.faction + "'")
        
        if self.route == []:
            if self.start == "":
                self.start = random.choice(list(bbData.builtInSystemObjs.keys()))
                while self.start == self.end or not bbData.builtInSystemObjs[self.start].hasJumpGate():
                    self.start = random.choice(list(bbData.builtInSystemObjs.keys()))
            elif self.start not in bbData.builtInSystemObjs:
                raise KeyError("BountyConfig: Invalid start system requested '" + self.start + "'")
            if self.end == "":
                self.end = random.choice(list(bbData.builtInSystemObjs.keys()))
                while self.start == self.end or not bbData.builtInSystemObjs[self.end].hasJumpGate():
                    self.end = random.choice(list(bbData.builtInSystemObjs.keys()))
            elif self.end not in bbData.builtInSystemObjs:
                raise KeyError("BountyConfig: Invalid end system requested '" + self.end + "'")
            # self.route = makeRoute(self.start, self.end)
            self.route = bbUtil.bbAStar(self.start, self.end, bbData.builtInSystemObjs)
        else:
            for system in self.route:
                if system not in bbData.builtInSystemObjs:
                    raise KeyError("BountyConfig: Invalid system in route '" + system + "'")
        if self.answer == "":
            self.answer = random.choice(self.route)
        elif self.answer not in bbData.builtInSystemObjs:
            raise KeyError("Bounty constructor: Invalid answer requested '" + self.answer + "'")
        
        if self.reward == -1.0:
            self.reward = len(self.route) * bbConfig.bPointsToCreditsRatio
        elif self.reward < 0:
            raise ValueError("Bounty constructor: Invalid reward requested '" + str(self.reward) + "'")
        if self.issueTime == -1.0:
            self.issueTime = datetime.utcnow().replace(second=0).timestamp()
        if self.endTime == -1.0:
            self.endTime = (datetime.utcfromtimestamp(self.issueTime) + timedelta(days=len(self.route))).timestamp()

        if not forceKeepChecked:
            self.checked = {}
        for station in self.route:
            if (not forceKeepChecked) or station not in self.checked or self.checked == {}:
                self.checked[station] = -1

        self.generated = True
        
