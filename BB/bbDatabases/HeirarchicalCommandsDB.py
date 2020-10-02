# Typing imports
from types import FunctionType
from discord import Message

class HeirarchicalCommandsDB:
    """Class that stores, categorises, and calls commands based on a text name and caller permissions.
    TODO: Change to a single list of [{}] where the internal {} is as userCommands etc currently are, and its index in the outer list corresponds to command access level
    
    :var userCommands: Dictionary of commands to tuples containing a function reference to call on call of that command, a boolean representing whether args should be converted to lower case before passing, and a boolean representing whether the function name is case-sensitive
    :vartype userCommands: dict[str, tuple[builtin_function_or_method, bool, bool]]
    :var adminCommands: Dictionary of commands to tuples containing a function reference to call on call of that command, a boolean representing whether args should be converted to lower case before passing, and a boolean representing whether the function name is case-sensitive
    :vartype adminCommands: dict[str, tuple[builtin_function_or_method, bool, bool]]
    :var devCommands: Dictionary of commands to tuples containing a function reference to call on call of that command, a boolean representing whether args should be converted to lower case before passing, and a boolean representing whether the function name is case-sensitive
    :vartype devCommands: dict[str, tuple[builtin_function_or_method, bool, bool]]
    """

    def __init__(self):
        self.userCommands = {}
        self.adminCommands = {}
        self.devCommands = {}

    
    def register(self, command : str, function : FunctionType, isAdmin=False, isDev=False, forceKeepArgsCasing=False, forceKeepCommandCasing=False):
        """Register a command in the database.

        :param str command: the text name users should call the function by. Commands are case sensitive.
        :param builtin_function_or_method function: reference to the function that should be called
        :param bool isAdmin: whether the caller requires admin privilages to call the command. (Default False)
        :param bool isDev: whether the caller requires developer privilages to call the command. (Default False)  
        """
        if isDev:
            self.devCommands[command if forceKeepCommandCasing else command.lower()] = (function, forceKeepArgsCasing, forceKeepCommandCasing)
        elif isAdmin:
            self.adminCommands[command if forceKeepCommandCasing else command.lower()] = (function, forceKeepArgsCasing, forceKeepCommandCasing)
        else:
            self.userCommands[command if forceKeepCommandCasing else command.lower()] = (function, forceKeepArgsCasing, forceKeepCommandCasing)

    
    async def call(self, command : str, message : Message, args : str, isAdmin=False, isDev=False, isDM=False):
        """Call a command or send an error message.

        :param str command: the text name of the command to attempt to call. Commands are case sensitive
        :param discord.message message: the discord message calling the command. This is required for referencing the author and sending responses
        :param str args: string containing arguments to pass to the command
        :param bool isAdmin: whether the calling user has admin privilages. (Default False)
        :param bool isDev: whether the calling user has developer privilages. (Default False)
        :param bool isDM: Whether the command was called from DMs or not
        :return: True if the command call was successful, False otherwise
        :rtype: bool
        """
        # First search user commands
        if command in self.userCommands and self.userCommands[command][2]:
            await self.userCommands[command][0](message, args if self.userCommands[command][1] else args.lower(), isDM)
            return True
        elif command.lower() in self.userCommands and not self.userCommands[command.lower()][2]:
            await self.userCommands[command.lower()][0](message, args if self.userCommands[command.lower()][1] else args.lower(), isDM)
            return True
        else:
            # Then search admin commands (if privilages are present)
            if isAdmin or isDev:
                if command in self.adminCommands and self.adminCommands[command][2]:
                    await self.adminCommands[command][0](message, args if self.adminCommands[command][1] else args.lower(), isDM)
                    return True
                elif command.lower() in self.adminCommands and not self.adminCommands[command.lower()][2]:
                    await self.adminCommands[command.lower()][0](message, args if self.adminCommands[command.lower()][1] else args.lower(), isDM)
                    return True
                else:
                    # Finally, search developer commands (if privilages are present)
                    if isDev:
                        if command in self.devCommands and self.devCommands[command][2]:
                            await self.devCommands[command][0](message, args if self.devCommands[command][1] else args.lower(), isDM)
                            return True
                        elif command.lower() in self.devCommands and not self.devCommands[command.lower()][2]:
                            await self.devCommands[command.lower()][0](message, args if self.devCommands[command.lower()][1] else args.lower(), isDM)
                            return True
            # command not found
            return False
