import operator, pprint

from . import bbData, bbConfig
from ..bbObjects.bounties import bbCriminal, bbSystem
from ..bbObjects.items import bbShip, bbModuleFactory, bbWeapon, bbShipUpgrade, bbTurret



##### OBJECT SPAWNING #####

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



##### ITEM TECHLEVEL AUTO-GENERATION #####

# Assign each shipDict a techLevel, based on their value
for shipDict in bbData.builtInShipData.values():
    for tl in range(len(bbConfig.shipMaxPriceTechLevels)):
        if bbConfig.shipMaxPriceTechLevels[tl] >= shipDict["value"]:
            shipDict["techLevel"] = tl + 1
            break



##### SORT ITEMS BY TECHLEVEL #####

# Initialise shipKeysByTL as maxTechLevel empty arrays
bbData.shipKeysByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]

# Sort ship keys by tech level
for currentShipKey in bbData.builtInShipData.keys():
    bbData.shipKeysByTL[bbData.builtInShipData[currentShipKey]["techLevel"] - 1].append(currentShipKey)

# Sort module objects by tech level
bbData.moduleObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
for currentModuleObj in bbData.builtInModuleObjs.values():
    bbData.moduleObjsByTL[currentModuleObj.techLevel - 1].append(currentModuleObj)

# Sort weapon objects by tech level
bbData.weaponObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
for currentWeaponObj in bbData.builtInWeaponObjs.values():
    bbData.weaponObjsByTL[currentWeaponObj.techLevel - 1].append(currentWeaponObj)

# Sort turret objects by tech level
bbData.turretObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
for currentTurretObj in bbData.builtInTurretObjs.values():
    bbData.turretObjsByTL[currentTurretObj.techLevel - 1].append(currentTurretObj)



##### MAX SPAWNRATE CALCULATION #####

for ship in bbData.builtInShipData.values():
    ship["shopSpawnRate"] = bbConfig.truncToRes(bbConfig.itemTLSpawnChanceForShopTL[ship["techLevel"] - 1][ship["techLevel"] - 1] / len(bbData.shipKeysByTL[ship["techLevel"] - 1]))

for weapon in bbData.builtInWeaponObjs.values():
    weapon.shopSpawnRate = bbConfig.truncToRes(bbConfig.itemTLSpawnChanceForShopTL[weapon.techLevel - 1][weapon.techLevel - 1] / len(bbData.weaponObjsByTL[weapon.techLevel - 1]))

for module in bbData.builtInModuleObjs.values():
    module.shopSpawnRate = bbConfig.truncToRes(bbConfig.itemTLSpawnChanceForShopTL[module.techLevel - 1][module.techLevel - 1] / len(bbData.moduleObjsByTL[module.techLevel - 1]))

for turret in bbData.builtInTurretObjs.values():
    turret.shopSpawnRate = bbConfig.truncToRes(bbConfig.itemTLSpawnChanceForShopTL[turret.techLevel - 1][turret.techLevel - 1] / len(bbData.turretObjsByTL[turret.techLevel - 1]))
