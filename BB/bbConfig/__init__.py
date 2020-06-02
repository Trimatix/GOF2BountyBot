# from . import *

from . import bbData
from ..bbObjects import bbCriminal, bbSystem

for criminalDict in bbData.builtInCriminalData:
    bbData.builtInCriminalObjs[criminalDict["name"]] = bbCriminal.fromDict(criminalDict)

for systemDict in bbData.builtInSystemData:
    bbData.builtInSystemObjs[systemDict["name"]] = bbSystem.fromDict(systemDict)
