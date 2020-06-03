# from . import *

from . import bbData
from ..bbObjects import bbCriminal, bbSystem

for criminalDict in bbData.builtInCriminalData.values():
    bbData.builtInCriminalObjs[criminalDict["name"]] = bbCriminal.fromDict(criminalDict)
    bbData.builtInCriminalObjs[criminalDict["name"]].builtIn = True

for systemDict in bbData.builtInSystemData.values():
    bbData.builtInSystemObjs[systemDict["name"]] = bbSystem.fromDict(systemDict)
