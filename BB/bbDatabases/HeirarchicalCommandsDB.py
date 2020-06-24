"""
Class that stores, categorises, and calls commands based on a text name and caller permissions.
TODO: Change to a single dict of {accessLevel: {}} where the internal {} is as userCommands etc currently are, and accessLevel is int
"""
class HeirarchicalCommandsDB:
    userCommands = {}
    adminCommands = {}
    devCommands = {}


    def __init__(self):
        self.userCommands = {}
        self.adminCommands = {}
        self.devCommands = {}


    """
    Register a command in the database.

    @param command -- the text name users should call the function by. Commands are case sensitive.
    @param function -- reference to the function that should be called
    @param isAdmin -- whether the caller requires admin privilages to call the command. Default: False
    @param isDev -- whether the caller requires developer privilages to call the command. Default: False  
    """
    def register(self, command, function, isAdmin=False, isDev=False, forceKeepArgsCasing=False, forceKeepCommandCasing = False):
        if isDev:
            self.devCommands[command if forceKeepCommandCasing else command.lower()] = (function, forceKeepArgsCasing, forceKeepCommandCasing)
        elif isAdmin:
            self.adminCommands[command if forceKeepCommandCasing else command.lower()] = (function, forceKeepArgsCasing, forceKeepCommandCasing)
        else:
            self.userCommands[command if forceKeepCommandCasing else command.lower()] = (function, forceKeepArgsCasing, forceKeepCommandCasing)

    """
    Call a command or send an error message.

    @param command -- the text name of the command to attempt to call. Commands are case sensitive
    @param message -- the discord message calling the command. This is required for referencing the author and sending responses
    @param args -- string containing arguments to pass to the command
    @param isAdmin -- whether the calling user has admin privilages. Default: False
    @param isDev -- whether the calling user has developer privilages. Default: False
    @return -- True if the command call was successful, False otherwise
    """
    async def call(self, command, message, args, isAdmin=False, isDev=False):
        # First search user commands
        if command in self.userCommands and self.userCommands[command][2]:
            await self.userCommands[command][0](message, args if self.userCommands[command][1] else args.lower())
            return True
        elif command.lower() in self.userCommands and not self.userCommands[command.lower()][2]:
            await self.userCommands[command.lower()][0](message, args if self.userCommands[command.lower()][1] else args.lower())
            return True
        else:
            # Then search admin commands (if privilages are present)
            if isAdmin or isDev:
                if command in self.adminCommands and self.adminCommands[command][2]:
                    await self.adminCommands[command][0](message, args if self.adminCommands[command][1] else args.lower())
                    return True
                elif command.lower() in self.adminCommands and not self.adminCommands[command.lower()][2]:
                    await self.adminCommands[command.lower()][0](message, args if self.adminCommands[command.lower()][1] else args.lower())
                    return True
                else:
                    # Finally, search developer commands (if privilages are present)
                    if isDev:
                        if command in self.devCommands and self.devCommands[command][2]:
                            await self.devCommands[command][0](message, args if self.devCommands[command][1] else args.lower())
                            return True
                        elif command.lower() in self.devCommands and not self.devCommands[command.lower()][2]:
                            await self.devCommands[command.lower()][0](message, args if self.devCommands[command.lower()][1] else args.lower())
                            return True
            # command not found
            return False
