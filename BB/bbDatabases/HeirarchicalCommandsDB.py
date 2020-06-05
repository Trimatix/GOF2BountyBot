"""
Class that stores, categorises, and calls commands based on a text name and caller permissions.
"""
class HeirarchicalCommandsDB:
    userCommands = {}
    adminCommands = {}
    devCommands = {}

    """
    Register a command in the database.

    @param command -- the text name users should call the function by. Commands are case sensitive.
    @param function -- reference to the function that should be called
    @param isAdmin -- whether the caller requires admin privilages to call the command. Default: False
    @param isDev -- whether the caller requires developer privilages to call the command. Default: False  
    """
    def register(self, command, function, isAdmin=False, isDev=False):
        if isDev:
            self.devCommands[command] = function
        elif isAdmin:
            self.adminCommands[command] = function
        else:
            self.userCommands[command] = function

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
        try:
            await self.userCommands[command](message, args)
            return True
        except KeyError:
            # Then search admin commands (if privilages are present)
            if isAdmin or isDev:
                try:
                    await self.adminCommands[command](message, args)
                    return True
                except KeyError:
                    # Finally, search developer commands (if privilages are present)
                    if isDev:
                        try:
                            await self.devCommands[command](message, args)
                            return True
                        except KeyError:
                            pass
            # command not found
            return False
