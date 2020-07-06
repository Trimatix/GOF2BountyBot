"""
⚠ WARNING: MARKED FOR CHANGE ⚠
The following function is provisional and marked as planned for overhaul.
Details: Item rarities are to be overhauled, from a linear scale to exponential. In layman's terms, mid price-range items are to become more common.

"""

import operator

from . import bbData
from . import bbConfig
from ..bbObjects.bounties import bbCriminal, bbSystem
from ..bbObjects.items import bbShip, bbModuleFactory, bbWeapon, bbShipUpgrade, bbTurret

# generate bbCriminal objects from data in bbData
for criminalDict in bbData.builtInCriminalData.values():
    bbData.builtInCriminalObjs[criminalDict["name"]] = bbCriminal.fromDict(criminalDict)
    bbData.builtInCriminalObjs[criminalDict["name"]].builtIn = True
    bbData.builtInCriminalData[criminalDict["name"]]["builtIn"] = True

# generate bbSystem objects from data in bbData
for systemDict in bbData.builtInSystemData.values():
    bbData.builtInSystemObjs[systemDict["name"]] = bbSystem.fromDict(systemDict)
    bbData.builtInSystemData[systemDict["name"]]["builtIn"] = True
    bbData.builtInSystemObjs[systemDict["name"]].builtIn = True

# # generate bbShip objects from data in bbData
# # NOTE: ONLY for use in shop listings - buying of ships should make a deep copy of the object, or 
# # spawn a new one from the data dict
for shipDict in bbData.builtInShipData.values():
    # Assign each shipDict a techLevel, based on their value
    for tl in range(len(bbConfig.shipMaxPriceTechLevels)):
        if bbConfig.shipMaxPriceTechLevels[tl] > shipDict["value"]:
            shipDict["techLevel"] = tl + 1
#     bbData.builtInShipObjs[shipDict["name"]] = bbShip.fromDict(shipDict)

# generate bbModule objects from data in bbData
for moduleDict in bbData.builtInModuleData.values():
    bbData.builtInModuleObjs[moduleDict["name"]] = bbModuleFactory.fromDict(moduleDict)
    bbData.builtInModuleData[moduleDict["name"]]["builtIn"] = True
    bbData.builtInModuleObjs[moduleDict["name"]].builtIn = True

# generate bbWeapon objects from data in bbData
for weaponDict in bbData.builtInWeaponData.values():
    bbData.builtInWeaponObjs[weaponDict["name"]] = bbWeapon.fromDict(weaponDict)
    bbData.builtInWeaponData[weaponDict["name"]]["builtIn"] = True
    bbData.builtInWeaponObjs[weaponDict["name"]].builtIn = True

# generate bbUpgrade objects from data in bbData
for upgradeDict in bbData.builtInUpgradeData.values():
    bbData.builtInUpgradeObjs[upgradeDict["name"]] = bbShipUpgrade.fromDict(upgradeDict)
    bbData.builtInUpgradeData[upgradeDict["name"]]["builtIn"] = True
    bbData.builtInUpgradeObjs[upgradeDict["name"]].builtIn = True

# generate bbTurret objects from data in bbData
for turretDict in bbData.builtInTurretData.values():
    bbData.builtInTurretObjs[turretDict["name"]] = bbTurret.fromDict(turretDict)
    bbData.builtInTurretData[turretDict["name"]]["builtIn"] = True
    bbData.builtInTurretObjs[turretDict["name"]].builtIn = True

bbData.shipKeysByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]

for currentShipKey in bbData.builtInShipData.keys():
    bbData.shipKeysByTL[bbData.builtInShipData[currentShipKey]["techLevel"] - 1].append(currentShipKey)

bbData.moduleObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
for currentModuleObj in bbData.builtInModuleObjs.values():
    bbData.moduleObjsByTL[currentModuleObj.techLevel - 1].append(currentModuleObj)

bbData.weaponObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
for currentWeaponObj in bbData.builtInWeaponObjs.values():
    bbData.weaponObjsByTL[currentWeaponObj.techLevel - 1].append(currentWeaponObj)

bbData.turretObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
for currentTurretObj in bbData.builtInTurretObjs.values():
    bbData.turretObjsByTL[currentTurretObj.techLevel - 1].append(currentTurretObj)


for turret in bbData.builtInTurretObjs.values():
    turret.shopSpawnRate = round(((turretKeysNum[turret.name] / numRankedTurretObjs) * 100) * (bbConfig.turretSpawnProbability / 100), 2)
