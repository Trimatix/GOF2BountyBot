# Typing imports
from types import FunctionType
from discord import Message
from typing import List


class IncorrectCommandCallContext(Exception):
    """Exception used to indicate when a non-DMable command is called from DMs.
    May be used in the future to indicate the opposite; a command that can only be called from DMs is called from outside of DMs.
    """
    pass


class CommandRegistry:
    """Represents a registration of a command in a HeirarchicalCommandsDB.
    TODO: Make allowDM so we dont have to make two HeirarchicalCommandsDBs to handle DM commands

    :var ident: The string command name by which this command is identified and called
    :type ident: str
    :var func: A reference to the function to call upon calling this CommandRegistry
    :type func: FunctionType
    :var forceKeepArgsCasing: Whether to pass arguments to the function with their original casing. If False, arguments will be transformed to lower case before passing.
    :type forceKeepArgsCasing: bool
    :var forceKeepCommandCasing: Whether the command must be called with exactly the correct casing
    :type forceKeepCommandCasing: bool
    :var allowDM: Allow calling of this command from DMs.
    :type allowDM: bool
    """
    def __init__(self, ident : str, func: FunctionType, forceKeepArgsCasing : bool, forceKeepCommandCasing : bool, allowDM : bool):
        """
        :param str ident: The string command name by which this command is identified and called
        :param FunctionType func: A reference to the function to call upon calling this CommandRegistry
        :param bool forceKeepArgsCasing: Whether to pass arguments to the function with their original casing. If False, arguments will be transformed to lower case before passing.
        :param bool forceKeepCommandCasing: Whether the command must be called with exactly the correct casing
        :param bool allowDM: Allow calling of this command from DMs
        """
        self.ident = ident
        self.func = func
        self.forceKeepArgsCasing = forceKeepArgsCasing
        self.forceKeepCommandCasing = forceKeepCommandCasing
        self.allowDM = allowDM


    async def call(self, message : Message, args : str, isDM : bool):
        """Call this command.

        :param discord.message message: the discord message calling the command. This is required for referencing the author and sending responses
        :param str args: string containing arguments to pass to the command
        :param bool isDM: Whether the command was called from DMs or not
        :raise IncorrectCommandCallContext: When attempting to call a non-DMable command from DMs
        """
        if isDM and not self.allowDM:
            raise IncorrectCommandCallContext("Attempted to call command '" + self.ident + "' from DMs, but command is not allowed in DMs.")
        await self.func(message, args if self.forceKeepArgsCasing else args.lower(), isDM)


class HeirarchicalCommandsDB:
    """Class that stores, categorises, and calls commands based on a text name and caller permissions.
    
    :var numAccessLevels: The number of command access levels registerable and callable in this database
    :type numAccessLevels: int
    :var commands: A list, where the index in the list corresponds to the access level requirement. Each index in the list is a dictionary mapping a command identifier string to a command registry.
    :type commands: List[Dict[str, CommandRegistry]]
    """

    def __init__(self, numAccessLevels : int):
        if numAccessLevels < 1:
            raise ValueError("Cannot create a HeirarchicalCommandsDB with less than one access level")
        self.numAccessLevels = numAccessLevels
        self.clear()

    
    def register(self, command : str, function : FunctionType, accessLevel : int, aliases : List[str] = [], forceKeepArgsCasing : bool = False, forceKeepCommandCasing : bool = False, allowDM : bool = True):
        """Register a command in the database.

        :param str command: the text name users should call the function by. Commands are case sensitive.
        :param FunctionType function: reference to the function that should be called
        :param int accessLevel: The level of access required to call this command
        :param List[str] aliases: List of alternative commands which may be used to call this one. The same accessLevel will be required for all aliases. (Default []) 
        :param bool forceKeepArgsCasing: Whether to pass arguments to the function with their original casing. If False, arguments will be transformed to lower case before passing. (Default False)
        :param bool forceKeepCommandCasing: Whether the command must be called with exactly the correct casing (Default False)
        :param bool allowDM: Allow calling of this command from DMs. (Default True)
        :raise IndexError: When attempting to register at an unsupported access level
        :raise NameError: When attempting to register a command identifier or alias that already exists at the requested access level
        """
        # Validate accessLevel
        if accessLevel < 0 or accessLevel > self.numAccessLevels - 1:
            raise IndexError("Access level out of range. Minimum: 0, maximum: " + str(self.numAccessLevels - 1) + ", given: " + str(accessLevel))
        
        # Generate a list of all command identifiers with respect to forceKeepCommandCasing
        cmdIdent = command if forceKeepCommandCasing else command.lower()
        allIdents = [cmdIdent]
        for alias in aliases:
            allIdents.append(alias if forceKeepCommandCasing else alias.lower())
        
        # Validate command identifiers for existence at the given accessLevel
        for currentIdent in allIdents:
            if currentIdent in self.commands[accessLevel]:
                raise NameError("A command at access level " + str(accessLevel) + " already exists with the name " + currentIdent)
        
        # Register all identifiers for this command to the same command registry
        newRegistry = CommandRegistry(cmdIdent, function, forceKeepArgsCasing, forceKeepCommandCasing, allowDM)
        for currentIdent in allIdents:
            self.commands[accessLevel][currentIdent] = newRegistry

    
    async def call(self, command : str, message : Message, args : str, accessLevel : int, isDM : bool = False):
        """Call a command or send an error message.

        :param str command: the text name of the command to attempt to call. Commands may be case sensitive, depending on their forceKeepCommandCasing option
        :param discord.message message: the discord message calling the command. This is required for referencing the author and sending responses
        :param str args: string containing arguments to pass to the command. May be transformed to lower case before passing, depending on the commands forceKeepArgsCasing option
        :param bool isDM: Whether the command was called from DMs or not (Default False)
        :return: True if the command call was successful, False otherwise
        :rtype: bool
        """
        commandLower = command.lower()
        # Search upper access levels first
        for requiredAccess in range(accessLevel, -1, -1):
            # Search casing matches (forceKeepCommandCasing) first
            if command in self.commands[requiredAccess]:
                await self.commands[requiredAccess][command].call(message, args, isDM)
                # Return true if a command was found
                return True
            elif commandLower in self.commands[requiredAccess]:
                await self.commands[requiredAccess][commandLower].call(message, args, isDM)
                return True
        # Return false if no command could be matched
        return False


    def clear(self):
        """Remove all command registrations from the database.
        """
        self.commands = [{} for i in range(self.numAccessLevels)]
