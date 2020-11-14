from ..bbDatabases import HeirarchicalCommandsDB
from ..bbConfig import bbConfig
import importlib

commandsDB = HeirarchicalCommandsDB.HeirarchicalCommandsDB(bbConfig.numCommandAccessLevels)

def loadCommands():
    global commandsDB
    commandsDB.clear()

    for modName in bbConfig.includedCommandModules:
        try:
            importlib.import_module(("" if modName.startswith(".") else ".") + modName, "BB.commands")
        except ImportError:
            raise ImportError("Unrecognised commands module in bbConfig.includedCommandModules. Please ensure the file exists, and spelling/capitalization are correct: '" + modName + "'")
    
    return commandsDB