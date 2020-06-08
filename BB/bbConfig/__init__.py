import operator

from . import bbData
from . import bbConfig
from ..bbObjects import bbCriminal, bbSystem
from ..bbObjects.items import bbShip, bbModule, bbWeapon, bbShipUpgrade

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
# for shipDict in bbData.builtInShipData.values():
#     bbData.builtInShipObjs[shipDict["name"]] = bbShip.fromDict(shipDict)

# generate bbModule objects from data in bbData
for moduleDict in bbData.builtInModuleData.values():
    bbData.builtInModuleObjs[moduleDict["name"]] = bbModule.fromDict(moduleDict)
    bbData.builtInModuleData[systemDict["name"]]["builtIn"] = True
    bbData.builtInModuleObjs[systemDict["name"]].builtIn = True

# generate bbWeapon objects from data in bbData
for weaponDict in bbData.builtInWeaponData.values():
    bbData.builtInWeaponObjs[weaponDict["name"]] = bbWeapon.fromDict(weaponDict)
    bbData.builtInWeaponData[systemDict["name"]]["builtIn"] = True
    bbData.builtInWeaponObjs[systemDict["name"]].builtIn = True

# generate bbUpgrade objects from data in bbData
for upgradeDict in bbData.builtInUpgradeData.values():
    bbData.builtInUpgradeObjs[upgradeDict["name"]] = bbShipUpgrade.fromDict(upgradeDict)
    bbData.builtInUpgradeData[systemDict["name"]]["builtIn"] = True
    bbData.builtInUpgradeObjs[systemDict["name"]].builtIn = True


# Sort ships by value
unsortedShipKeys = {}
for shipKey in bbData.builtInShipData.keys():
    unsortedShipKeys[shipKey] = bbData.builtInShipData[shipKey].value
sortedShipKeys = sorted(unsortedShipKeys.items(), key=operator.itemgetter(1))[::-1]

# Make a list of ship KEYS ranked by value for random picking
for keyIndex in range(len(sortedShipKeys) - 1, -1, -1):
    # currentShip = bbData.builtInShipObjs[sortedShipKeys[keyIndex][0]]
    currentShip = sortedShipKeys[keyIndex][0]
    for n in range(int(keyIndex / bbConfig.numShipRanks)):
        bbData.rankedShipKeys.append(currentShip)


# Sort weapons by value
unsortedWeaponKeys = {}
for weaponKey in bbData.builtInWeaponObjs.keys():
    unsortedWeaponKeys[weaponKey] = bbData.builtInWeaponObjs[weaponKey].value
sortedWeaponKeys = sorted(unsortedWeaponKeys.items(), key=operator.itemgetter(1))[::-1]

# Make a list of weapons ranked by value for random picking
for keyIndex in range(len(sortedWeaponKeys) - 1, -1, -1):
    currentWeapon = bbData.builtInWeaponObjs[sortedWeaponKeys[keyIndex][0]]
    for n in range(int(keyIndex / bbConfig.numWeaponRanks)):
        bbData.rankedWeaponObjs.append(currentWeapon)


# Sort modules by value
unsortedModuleKeys = {}
for moduleKey in bbData.builtInModuleObjs.keys():
    unsortedModuleKeys[moduleKey] = bbData.builtInModuleObjs[moduleKey].value
sortedModuleKeys = sorted(unsortedModuleKeys.items(), key=operator.itemgetter(1))[::-1]

# Make a list of modules ranked by value for random picking
for keyIndex in range(len(sortedModuleKeys) - 1, -1, -1):
    currentModule = bbData.builtInModuleObjs[sortedModuleKeys[keyIndex][0]]
    for n in range(int(keyIndex / bbConfig.numModuleRanks)):
        bbData.rankedModuleObjs.append(currentModule)
