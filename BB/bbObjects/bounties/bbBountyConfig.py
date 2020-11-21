# Typing imports
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict
if TYPE_CHECKING:
    from ...bbDatabases import bbBountyDB
    from ..items import bbShip

import random
from datetime import datetime, timedelta

from ...bbConfig import bbData, bbConfig
from ... import lib
from ..items import bbShip
from ..items.modules import bbArmourModule, bbShieldModule

class BountyConfig:
    """
    Configurator class describing all attributes needed for a bbBounty object.

    :var faction: The faction owning this bounty
    :vartype faction: str
    :var name: The name of the wanted criminal. If this is a player bounty, name should be the player mention.
    :vartype name: str
    :var isPlayer: Whether or not the target criminal is a player or an npc
    :vartype isPlayer: bool
    :var route: the names of systems in this bounty's route
    :vartype route: list[str]
    :var start: The name of the system at the start of the route
    :vartype start: str
    :var end: The name of the system at the end of the route
    :vartype end: str
    :var answer: The name of the system where the criminal is located
    :vartype answer: str
    :var checked: Dictionary of system names to user IDs, where the id corresponds to the user who checked that system, or -1 if the system is unchecked.
    :vartype checked: dict[str, int]
    :var reward: Prize pool of credits to award to contributing users
    :vartype reward: int
    :var issueTime: A utc timestamp representing the time at which the bounty was issued
    :vartype issueTime: float
    :var endTime: A utc timestamp representing the time at which the bounty should automatically expire
    :vartype endTime: flaot
    :var icon: A URL directly linking to an image to use as the criminal's icon
    :vartype icon: str
    :var aliases: Aliases that can be used to refer to this criminal
    :vartype aliases: list[str]
    :var wiki: The page to link to as the criminal's wiki, in their info embed
    :vartype wiki: str
    :var builtIn: whether or not this is a built in npc criminal
    :vartype builtIn: bool
    :var generated: whether or not this config is ready to be used. The config must verify and generate its attributes before they can be used in a bbBounty.
    :vartype generated: bool
    :var activeShip: The bbShip this criminal should equip
    :vartype activeShip: bbShip
    """

    def __init__(self, faction : str = "", name : str = "", isPlayer : bool = None,
                    route : List[str] = [], start : str = "", end : str = "",
                    answer : str = "", checked : Dict[str, int] = {}, reward : int = -1,
                    issueTime : float = -1.0, endTime : float = -1.0, icon : str = "",
                    aliases : List[str] = [], wiki : str = "", ship : bbShip.bbShip = None,
                    activeShip : bbShip.bbShip = None, techLevel : int = -1, rewardPerSys : int = -1):
        """All parameters are optional. If a parameter is not given, it will be randomly generated.

        :param faction: The faction owning this bounty
        :type faction: str
        :param name: The name of the wanted criminal. If this is a player bounty, name should be the player mention.
        :type name: str
        :param isPlayer: Whether or not the target criminal is a player or an npc
        :type isPlayer: bool
        :param route: the names of systems in this bounty's route
        :type route: list[str]
        :param start: The name of the system at the start of the route
        :type start: str
        :param end: The name of the system at the end of the route
        :type end: str
        :param answer: The name of the system where the criminal is located
        :type answer: str
        :param checked: Dictionary of system names to user IDs, where the id corresponds to the user who checked that system, or -1 if the system is unchecked.
        :type checked: dict[str, int]
        :param reward: Prize pool of credits to award to contributing users
        :type reward: int
        :param issueTime: A utc timestamp representing the time at which the bounty was issued
        :type issueTime: float
        :param endTime: A utc timestamp representing the time at which the bounty should automatically expire
        :type endTime: flaot
        :param icon: A URL directly linking to an image to use as the criminal's icon
        :type icon: str
        :param aliases: Aliases that can be used to refer to this criminal
        :type aliases: list[str]
        :param wiki: The page to link to as the criminal's wiki, in their info embed
        :type wiki: str
        :param activeShip: The bbShip this criminal should equip
        :type activeShip: bbShip
        """
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
        self.rewardPerSys = rewardPerSys
        if type(rewardPerSys) == float:
            self.rewardPerSys = int(rewardPerSys)
        if type(reward) == float:
            self.reward = int(reward)
        self.issueTime = issueTime
        self.endTime = endTime
        self.icon = icon
        self.generated = False
        self.builtIn = False

        self.aliases = aliases
        self.wiki = wiki

        self.activeShip = activeShip
        self.techLevel = techLevel
        
    
    def generate(self, bountyDB : bbBountyDB.bbBountyDB, noCriminal : bool = True, forceKeepChecked : bool = False, forceNoDBCheck : bool = False):
        """Validate all given config data, and randomly generate missing data.

        :param bbBountyDB bountyDB: Database containing all currently active bounties. When forceNoDBCheck is True, this is ignored.
        :param bool noCriminal: If this is True, randomly generate a bbCriminal object. (Default True)
        :param bool forceKeepChecked: If this is False, a blank checked dictionary will be used. This should only be set to be True when using a pre-made checked dictionary; e.g for custom bounties or for bounties loaded from file. (Default False)
        :param bool forceNoDBCheck: If this is False, do not check if the bounty already exists. This should only be used as a performance and compatibility measure when loading in a bounty from file. (Default False)
        :raise ValueError: When requesting an invalid faction, or when requesting an invalid reward amount
        :raise IndexError: When no space is available for a new bounty
        :raise KeyError: When the requested criminal name already exists in a bounty, or when requesting an unknown system name
        """
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
                    while doDBCheck and bountyDB.bountyNameExists(self.name, noEscapedCrim=False):
                        self.name = random.choice(bbData.bountyNames[self.faction])
                else:
                    if doDBCheck and bountyDB.bountyNameExists(self.name, noEscapedCrim=False):
                        raise KeyError("BountyConfig: attempted to create config for pre-existing bounty: " + self.name)
                    
                    if self.icon == "":
                        self.icon = bbData.rocketIcon
        
        else:
            if doDBCheck and not bountyDB.factionCanMakeBounty(self.faction):
                raise IndexError("BOUCONF_CONS_FACDBFULL: Attempted to generate new bounty config when no slots are available for faction: '" + self.faction + "'")
        
        if self.techLevel == -1:
            self.techLevel = bbConfig.pickRandomCriminalTL()

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
            self.route = lib.pathfinding.bbAStar(self.start, self.end, bbData.builtInSystemObjs)
        else:
            for system in self.route:
                if system not in bbData.builtInSystemObjs:
                    raise KeyError("BountyConfig: Invalid system in route '" + system + "'")
        if self.answer == "":
            self.answer = random.choice(self.route)
        elif self.answer not in bbData.builtInSystemObjs:
            raise KeyError("Bounty constructor: Invalid answer requested '" + self.answer + "'")

        if self.activeShip is None:
            if self.isPlayer:
                raise ValueError("Attempted to generate a player bounty without providing the activeShip")
            
            # tech leve 0 = guaranteed lowest difficulty loadout
            if self.techLevel == 0:
                self.activeShip = bbShip.fromDict(bbConfig.level0CrimLoadout)
            # Otherwise, generate one based on difficulty
            else:
                itemTL = self.techLevel - 1
                if len(bbData.shipKeysByTL[itemTL]) < 1:
                    raise RuntimeError("Attempted to spawn a bounty at level " + str(self.techLevel) + ", but no ships exist at this level")
                shipWithPrimaryExists = False
                for shipKey in bbData.shipKeysByTL[itemTL]:
                    shipData = bbData.builtInShipData[shipKey]
                    if "maxPrimaries" in shipData and shipData["maxPrimaries"] > 0:
                        shipWithPrimaryExists = True
                        break

                if shipWithPrimaryExists:
                    shipHasPrimary = False
                    shipKey = ""
                    while not shipHasPrimary:
                        shipKey = random.choice(bbData.shipKeysByTL[itemTL])
                        shipHasPrimary = "maxPrimaries" in bbData.builtInShipData[shipKey] and bbData.builtInShipData[shipKey]["maxPrimaries"] > 0

                    if shipHasPrimary:
                        self.activeShip = bbShip.fromDict(bbData.builtInShipData[shipKey])
                    else:
                        self.activeShip = bbShip.fromDict(bbData.builtInShipData[random.choice(bbData.shipKeysByTL[itemTL])])

                    # if self.techLevel < self.activeShip.maxPrimaries:
                    #     numWeapons = random.randint(self.techLevel, self.activeShip.maxPrimaries)
                    # else:
                    #     numWeapons = self.activeShip.maxPrimaries
                    numWeapons = random.randint(max(1, self.activeShip.maxPrimaries - 1), self.activeShip.maxPrimaries)
                    for i in range(numWeapons):
                        self.activeShip.equipWeapon(random.choice(bbData.weaponObjsByTL[itemTL]))
                
                else:
                    self.activeShip = bbShip.fromDict(bbData.builtInShipData[random.choice(bbData.shipKeysByTL[itemTL])])

                armourEquipped = True
                shieldEquipped = True
                reservedSlots = 0
                # ensure criminals above TL 1 have armour
                if self.techLevel > 1:
                    armourEquipped = False
                    reservedSlots += 1
                # ensure criminals above TL 3 have shield
                if self.techLevel > 3:
                    shieldEquipped = False
                    reservedSlots += 1

                while not armourEquipped:
                    armourTL = -1
                    itemTLHasArmour = False
                    while not itemTLHasArmour:
                        armourTL = bbConfig.pickRandomItemTL(self.techLevel) - 1
                        for item in bbData.moduleObjsByTL[armourTL]:
                            if isinstance(item, bbArmourModule.bbArmourModule):
                                itemTLHasArmour = True
                                break

                    itemToEquip = random.choice(bbData.moduleObjsByTL[armourTL])
                    while not isinstance(itemToEquip, bbArmourModule.bbArmourModule):
                        itemToEquip = random.choice(bbData.moduleObjsByTL[armourTL])
                        
                    self.activeShip.equipModule(itemToEquip)
                    armourEquipped = True

                while not shieldEquipped:
                    shieldTL = -1
                    itemTLHasShield = False
                    while not itemTLHasShield:
                        shieldTL = bbConfig.pickRandomItemTL(self.techLevel) - 1
                        for item in bbData.moduleObjsByTL[shieldTL]:
                            if isinstance(item, bbShieldModule.bbShieldModule):
                                itemTLHasShield = True
                                break

                    itemToEquip = random.choice(bbData.moduleObjsByTL[shieldTL])
                    while not isinstance(itemToEquip, bbShieldModule.bbShieldModule):
                        itemToEquip = random.choice(bbData.moduleObjsByTL[shieldTL])
                        
                    self.activeShip.equipModule(itemToEquip)
                    shieldEquipped = True

                if self.activeShip.maxModules > reservedSlots:
                    for i in range(random.randint(1, self.activeShip.maxModules - reservedSlots)):
                        # itemTL = self.techLevel - 1
                        moduleTL = bbConfig.pickRandomItemTL(self.techLevel) - 1
                        tries = 5
                        while len(bbData.moduleObjsByTL[moduleTL]) == 0:
                            moduleTL = bbConfig.pickRandomItemTL(self.techLevel) - 1
                            tries -= 1
                            if tries == 0:
                                break
                        if tries == 0:
                                break
                        newModule = random.choice(bbData.moduleObjsByTL[moduleTL])
                        if self.activeShip.canEquipModuleType(type(newModule)):
                            self.activeShip.equipModule(newModule)

                for i in range(self.activeShip.maxTurrets):
                    equipTurret = random.randint(1,100)
                    if equipTurret <= bbConfig.criminalEquipTurretChance:
                        # turretTL = self.techLevel - 1
                        turretTL = bbConfig.pickRandomItemTL(self.techLevel) - 1
                        tries = 5
                        while len(bbData.turretObjsByTL[turretTL]) == 0:
                            turretTL = bbConfig.pickRandomItemTL(self.techLevel) - 1
                            tries -= 1
                            if tries == 0:
                                break
                        if tries == 0:
                                break
                        self.activeShip.equipTurret(random.choice(bbData.turretObjsByTL[turretTL]))

            # Purely random loadout generation
            # self.activeShip = bbShip.fromDict(random.choice(list(bbData.builtInShipData.values())))
            # for i in range(self.activeShip.maxPrimaries):
            #     self.activeShip.equipWeapon(random.choice(list(bbData.builtInWeaponObjs.values())))
            # for i in range(random.randint(1, self.activeShip.maxModules)):
            #     moduleNotFound = True
            #     while moduleNotFound:
            #         try:
            #             self.activeShip.equipModule(random.choice(list(bbData.builtInModuleObjs.values())))
            #             moduleNotFound = False
            #         except ValueError:
            #             pass
            # for i in range(self.activeShip.maxTurrets):
            #     equipTurret = random.randint(1,100)
            #     if equipTurret <= 30:
            #         turretNotFound = True
            #         while turretNotFound:
            #             try:
            #                 self.activeShip.equipTurret(random.choice(list(bbData.builtInTurretObjs.values())))
            #                 turretNotFound = False
            #             except ValueError:
            #                 pass
        
        if self.reward == -1:
            # self.reward = int(len(self.route) * bbConfig.bPointsToCreditsRatio + self.activeShip.getValue() * bbConfig.shipValueRewardPercentage)
            self.rewardPerSys = bbConfig.rewardPerSysCheck(self.techLevel, self.activeShip.getValue())
            self.reward = self.rewardPerSys * len(self.route)
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
        
