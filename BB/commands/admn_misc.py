import discord

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig, bbData
from ..userAlerts import UserAlerts
from ..scheduling import TimedTask
from ..reactionMenus import ReactionRolePicker


async def admin_cmd_admin_help(message : discord.Message, args : str, isDM : bool):
    """admin command printing help strings for admin commands as defined in bbData

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    sendChannel = None
    sendDM = False

    if message.author.dm_channel is None:
        await message.author.create_dm()
    if message.author.dm_channel is None:
        sendChannel = message.channel
    else:
        sendChannel = message.author.dm_channel
        sendDM = True

    helpEmbed = lib.discordUtil.makeEmbed(titleTxt="BB Administrator Commands",
                          thumb=bbGlobals.client.user.avatar_url_as(size=64))
    for section in bbData.adminHelpDict.keys():
        helpEmbed.add_field(name="‎", value="__" +
                            section + "__", inline=False)
        for currentCommand in bbData.adminHelpDict[section].values():
            helpEmbed.add_field(name=currentCommand[0], value=currentCommand[1].replace(
                "$COMMANDPREFIX$", bbConfig.commandPrefix), inline=False)

    try:
        await sendChannel.send(bbData.adminHelpIntro.replace("$COMMANDPREFIX$", bbConfig.commandPrefix), embed=helpEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return
    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji.sendable)

bbCommands.register("admin-help", admin_cmd_admin_help, 1)


async def admin_cmd_config(message : discord.Message, args : str, isDM : bool):
    """Apply various bountybot configuration settings for the calling guild.
    TODO: Refactor!

    :param discord.Message message: the discord message calling the command
    :param str args: A string containing a config setting id followed by a value
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")

    if len(argsSplit) < 2 or not (argsSplit[0] and argsSplit[1]):
        await message.channel.send(":x: Please provide both a setting and a value! e.g: `" + bbConfig.commandPrefix + "config bounties enable`")
        return

    setting, value = argsSplit[0], " ".join(argsSplit[1:])

    trueStrings = ["yes","true","on","enable","enabled"]
    falseStrings = ["no","false","off","disable","disabled"]
    callingBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)

    if setting in ["bounty","bounties"]:
        if value in trueStrings:
            if not callingBBGuild.bountiesDisabled:
                await message.channel.send(":x: Bounties are already enabled in this server!")
            else:
                callingBBGuild.enableBounties()
                await message.channel.send(":white_check_mark: Bounties are now enabled on this server!")
        elif value in falseStrings:
            if callingBBGuild.bountiesDisabled:
                await message.channel.send(":x: Bounties are already disabled in this server!")
            else:
                callingBBGuild.disableBounties()
                await message.channel.send(":white_check_mark: Bounties are now disabled on this server!")
        else:
            await message.channel.send(":x: Unknown value!")
    elif setting in ["shop", "shops"]:
        if value in trueStrings:
            if not callingBBGuild.shopDisabled:
                await message.channel.send(":x: The shop is already enabled in this server!")
            else:
                callingBBGuild.enableShop()
                await message.channel.send(":white_check_mark: The shop is now enabled on this server!")
        elif value in falseStrings:
            if callingBBGuild.shopDisabled:
                await message.channel.send(":x: The shop is already disabled in this server!")
            else:
                callingBBGuild.disableShop()
                await message.channel.send(":white_check_mark: The shop is now disabled on this server!")
        else:
            await message.channel.send(":x: Unknown value!")
    else:
        await message.channel.send(":x: Unknown setting!")


bbCommands.register("config", admin_cmd_config, 1)


async def admin_cmd_del_reaction_menu(message : discord.Message, args : str, isDM : bool):
    """Force the expiry of the specified reaction menu message, regardless of reaction menu type.

    :param discord.Message message: the discord message calling the command
    :param str args: A string containing the message ID of an active reaction menu.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    msgID = int(args)
    if msgID in bbGlobals.reactionMenusDB:
        await bbGlobals.reactionMenusDB[msgID].delete()
    else:
        await message.channel.send(":x: Unrecognised reaction menu!")


bbCommands.register("del-reaction-menu", admin_cmd_del_reaction_menu, 1)


async def admin_cmd_set_notify_role(message : discord.Message, args : str, isDM : bool):
    """For the current guild, set a role to mention when certain events occur.

    can take either a role mention or ID.

    :param discord.Message message: the discord message calling the command
    :param str args: the notfy role type, and either a role mention or a role ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please provide both a notification type, and either a role mention or ID!")
        return
    if not (lib.stringTyping.isInt(argsSplit[-1]) or lib.stringTyping.isRoleMention(argsSplit[-1])):
        await message.channel.send(":x: Invalid role! Please give either a role mention or ID!")
        return

    alertsToSet = UserAlerts.getAlertIDFromHeirarchicalAliases(argsSplit)
    if alertsToSet[0] == "ERR":
        await message.channel.send(alertsToSet[1])
        return

    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if lib.stringTyping.isRoleMention(argsSplit[-1]):
        requestedRole = message.guild.get_role(int(argsSplit[-1][3:-1]))
    else:
        requestedRole = message.guild.get_role(int(argsSplit[-1]))

    if requestedRole is None:
        await message.channel.send(":x: Role not found!")
        return

    for alertID in alertsToSet:
        alertType = UserAlerts.userAlertsIDsTypes[alertID]
        requestedBBGuild.setUserAlertRoleID(alertID, requestedRole.id)
        await message.channel.send(":white_check_mark: Role set for " + UserAlerts.userAlertsTypesNames[alertType] + " notifications!")

bbCommands.register("set-notify-role", admin_cmd_set_notify_role, 1)


async def admin_cmd_remove_notify_role(message : discord.Message, args : str, isDM : bool):
    """For the current guild, remove role mentioning when certain events occur.
    Takes only a UserAlert ID.

    :param discord.Message message: the discord message calling the command
    :param str args: the notfy role type, and either a role mention or a role ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send(":x: Please provide both a notification type!")
        return

    alertsToSet = UserAlerts.getAlertIDFromHeirarchicalAliases(args)
    if alertsToSet[0] == "ERR":
        await message.channel.send(alertsToSet[1])
        return

    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)

    for alertID in alertsToSet:
        alertType = UserAlerts.userAlertsIDsTypes[alertID]
        requestedBBGuild.removeUserAlertRoleID(alertID)
        await message.channel.send(":white_check_mark: Role pings disabled for " + UserAlerts.userAlertsTypesNames[alertType] + " notifications.")

bbCommands.register("remove-notify-role", admin_cmd_remove_notify_role, 1)


async def admin_cmd_make_role_menu(message : discord.Message, args : str, isDM : bool):
    """Create a reaction role menu, allowing users to self-assign or remove roles by adding and removing reactions.
    Each guild may have a maximum of bbConfig.maxRoleMenusPerGuild role menus active at any one time.
    Option reactions must be either unicode, or custom to the server where the menu is being created.

    args must contain a comma-separated list of emoji-option pairs, where each pair is separated with a space.
    For example: '0️⃣ @Role-1, 1️⃣ @Role-2, 2️⃣ @Role-3' will produce three options:
    - Toggling the 0️⃣ reaction will toggle user ownership of @Role-1
    - Toggling the 1️⃣ reaction will toggle user ownership of @Role-2
    - Toggling the 2️⃣ reaction will toggle user ownership of @Role-3

    args may also optionally contain the following keyword arguments, given as argname=value
    - target         : A role or user to restrict participants by. Must be a user or role mention, not ID.
    - days           : The number of days that the menu should run for. Must be at least one, or unspecified.
    - hours          : The number of hours that the menu should run for. Must be at least one, or unspecified.
    - minutes        : The number of minutes that the menu should run for. Must be at least one, or unspecified.
    - seconds        : The number of seconds that the menu should run for. Must be at least one, or unspecified.

    Reaction menus can be forced to run forever. To do this, specify ALL run time kwargs as 'off'.

    TODO: Change options list formatting from comma separated to new line separated
    TODO: Support target IDs
    TODO: Implement single choice/grouped roles
    TODO: Change non-expiring menu specification from all kwargs 'off' to a special kwarg 'on'

    :param discord.Message message: the discord message calling the command
    :param str args: A comma-separated list of space-separated emoji-option pairs, and optionally any kwargs as specified in this function's docstring
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if requestedBBGuild.ownedRoleMenus >= bbConfig.maxRoleMenusPerGuild:
        await message.channel.send(":x: Guilds can have at most " + str(bbConfig.maxRoleMenusPerGuild) + " role menus!")
        return
    requestedBBGuild.ownedRoleMenus += 1

    botRole = None
    potentialRoles = []
    for currRole in message.guild.me.roles:
        if currRole.name == message.guild.me.name and currRole.managed:
            potentialRoles.append(currRole)
    
    if potentialRoles == []:
        await message.channel.send(":x: I can't find my '" + message.guild.me.name + "' role! Have you renamed it?")
        return
    botRole = potentialRoles[-1]

    reactionRoles = {}

    argsSplit = args.split(",")
    argPos = 0
    arg = ""
    for arg in argsSplit:
        argPos += 1
        roleStr, dumbReact = arg.strip(" ").split(" ")[1], lib.emojis.dumbEmojiFromStr(arg.strip(" ").split(" ")[0])
        if dumbReact is None:
            await message.channel.send(":x: Invalid emoji: " + arg.strip(" ").split(" ")[1])
            return
        elif dumbReact.isID:
            localEmoji = False
            for localEmoji in message.guild.emojis:
                if localEmoji.id == dumbReact.id:
                    localEmoji = True
                    break
            if not localEmoji:
                await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
                return
            
        if dumbReact in reactionRoles:
            await message.channel.send(":x: Cannot use the same emoji for two options!")
            return


        role = message.guild.get_role(int(roleStr.lstrip("<@&").rstrip(">")))
        if role is None:
            await message.channel.send(":x: Unrecognised role: " + roleStr)
            return
        elif role.position > botRole.position:
            await message.channel.send(":x: I can't grant the **" + role.name + "** role!\nMake sure it's below my '" + botRole.name + "' role in the server roles list.")
        reactionRoles[dumbReact] = role

    if len(reactionRoles) == 0:
        await message.channel.send(":x: No roles given!")
        return

    targetRole = None
    targetMember = None
    if "target=" in arg:
        argIndex = arg.lower().index("target=") + len("target=")
        try:
            arg[argIndex:].lower().index(" ")
        except ValueError:
            endIndex = len(arg)
        else:
            endIndex = arg[argIndex:].index(" ") + argIndex + 1

        targetStr = arg[argIndex:endIndex]

        if lib.stringTyping.isRoleMention(targetStr):
            targetRole = message.guild.get_role(int(targetStr.lstrip("<@&").rstrip(">")))
            if targetRole is None:
                await message.channel.send(":x: Unknown target role!")
                return
        
        elif lib.stringTyping.isMention(targetStr):
            targetMember = message.guild.get_member(int(targetStr.lstrip("<@!").rstrip(">")))
            if targetMember is None:
                await message.channel.send(":x: Unknown target user!")
                return

        else:
            await message.channel.send(":x: Invalid target role/user!")
            return
    
    timeoutDict = {}

    for timeName in ["days", "hours", "minutes", "seconds"]:
        if timeName + "=" in arg.lower():
            argIndex = arg.lower().index(timeName + "=") + len(timeName + "=")
            try:
                arg[argIndex:].index(" ")
            except ValueError:
                endIndex = len(arg)
            else:
                endIndex = arg[argIndex:].index(" ") + argIndex + 1

            targetStr = arg[argIndex:endIndex]

            if targetStr == "off":
                timeoutDict[timeName] = -1
            else:
                if not lib.stringTyping.isInt(targetStr) or int(targetStr) < 1:
                    await message.channel.send(":x: Invalid number of " + timeName + " before timeout!")
                    return

                timeoutDict[timeName] = int(targetStr)

    timeoutExists = False
    for timeName in timeoutDict:
        if timeoutDict[timeName] != -1:
            timeoutExists = True
    timeoutExists = timeoutExists or timeoutDict == {}
    
    menuMsg = await message.channel.send("‎")

    if timeoutExists:
        timeoutDelta = lib.timeUtil.timeDeltaFromDict(bbConfig.roleMenuDefaultTimeout if timeoutDict == {} else timeoutDict)
        timeoutTT = TimedTask.TimedTask(expiryDelta=timeoutDelta, expiryFunction=ReactionRolePicker.markExpiredRoleMenu, expiryFunctionArgs=menuMsg.id)
        bbGlobals.reactionMenusTTDB.scheduleTask(timeoutTT)
    
    else:
        timeoutTT = None

    menu = ReactionRolePicker.ReactionRolePicker(menuMsg, reactionRoles, message.guild, targetRole=targetRole, targetMember=targetMember, timeout=timeoutTT)
    await menu.updateMessage()
    bbGlobals.reactionMenusDB[menuMsg.id] = menu

bbCommands.register("make-role-menu", admin_cmd_make_role_menu, 1, forceKeepArgsCasing=True)
