import discord
import os
import asyncio

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig, bbData
from ..userAlerts import UserAlerts
from ..scheduling import TimedTask
from ..reactionMenus import ReactionRolePicker, ReactionSkinRegionPicker
from ..bbObjects.items import bbShip
from ..logging import bbLogger
from ..shipRenderer import shipRenderer


CWD = os.getcwd()


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

    args must contain a menu subject and new line, followed by a newline-separated list of emoji-option pairs, where each pair is separated with a space.
    For example: 'Number Roles\n0️⃣ @Role-1\n1️⃣ @Role-2\n2️⃣ @Role-3' will produce three options:
    - Toggling the 0️⃣ reaction will toggle user ownership of @Role-1
    - Toggling the 1️⃣ reaction will toggle user ownership of @Role-2
    - Toggling the 2️⃣ reaction will toggle user ownership of @Role-3
    Where the subject of the menu is 'Number Roles'.
    The menu subject is optional. To not provide a subject, simply start args with a new line.

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
    kwArgs = {}

    argsSplit = args.split("\n")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Invalid arguments! Please provide your menu title, followed by a new line, then a new line-separated series of options.\nFor more info, see `" + bbConfig.commandPrefix + "admin-help`")
        return
    menuSubject = argsSplit[0]
    argPos = 0

    for arg in argsSplit[1:]:
        if arg == "":
            continue
        argPos += 1
        try:
            roleStr, dumbReact = arg.strip(" ").split(" ")[1], lib.emojis.dumbEmojiFromStr(arg.strip(" ").split(" ")[0])
        except (ValueError, IndexError):
            for kwArg in ["target=", "days=", "hours=", "seconds=", "minutes=", "multiplechoice="]:
                if arg.lower().startswith(kwArg):
                    kwArgs[kwArg[:-1]] = arg[len(kwArg):]
                    break
        # except lib.emojis.UnrecognisedCustomEmoji:
            # await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
            # return
        else:
            if dumbReact.sendable == "None":
                await message.channel.send(":x: I don't know your " + str(argPos) + lib.stringTyping.getNumExtension(argPos) + " emoji!\nYou can only use built in emojis, or custom emojis that are in this server.")
                return
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
    if "target" in kwArgs:
        if lib.stringTyping.isRoleMention(kwArgs["target"]):
            targetRole = message.guild.get_role(int(kwArgs["target"].lstrip("<@&").rstrip(">")))
            if targetRole is None:
                await message.channel.send(":x: Unknown target role!")
                return
        
        elif lib.stringTyping.isMention(kwArgs["target"]):
            targetMember = message.guild.get_member(int(kwArgs["target"].lstrip("<@!").rstrip(">")))
            if targetMember is None:
                await message.channel.send(":x: Unknown target user!")
                return

        else:
            await message.channel.send(":x: Invalid target role/user!")
            return
    
    timeoutDict = {}

    for timeName in ["days", "hours", "minutes", "seconds"]:
        if timeName in kwArgs:
            if kwArgs[timeName].lower() == "off":
                timeoutDict[timeName] = -1
            else:
                if not lib.stringTyping.isInt(kwArgs[timeName]) or int(kwArgs[timeName]) < 1:
                    await message.channel.send(":x: Invalid number of " + timeName + " before timeout!")
                    return

                timeoutDict[timeName] = int(kwArgs[timeName])


    multipleChoice = True

    if "multiplechoice" in kwArgs:
        if kwArgs["multiplechoice"].lower() in ["off", "no", "false", "single", "one"]:
            multipleChoice = False
        elif kwArgs["multiplechoice"].lower() not in ["on", "yes", "true", "multiple", "many"]:
            await message.channel.send("Invalid `multiplechoice` argument '" + kwArgs["multiplechoice"] + "'! Please use either `multiplechoice=yes` or `multiplechoice=no`")
            return

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

    menu = ReactionRolePicker.ReactionRolePicker(menuMsg, reactionRoles, message.guild, targetRole=targetRole, targetMember=targetMember, timeout=timeoutTT, titleTxt=menuSubject)
    await menu.updateMessage()
    bbGlobals.reactionMenusDB[menuMsg.id] = menu

bbCommands.register("make-role-menu", admin_cmd_make_role_menu, 1, forceKeepArgsCasing=True)


async def admin_cmd_showmeHD(message : discord.Message, args : str, isDM : bool):
    """Render the attached image file onto the specified ship, in high definition.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")
        return

    full = False
    if args.endswith("-full"):
        args = args.split("-full")[0]
        full = True
    
    # look up the ship object
    itemName = args.rstrip(" ").title()
    itemObj = None
    for ship in bbData.builtInShipData.values():
        shipObj = bbShip.fromDict(ship)
        if shipObj.isCalled(itemName):
            itemObj = shipObj

    # report unrecognised ship names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")
        return

    shipData = bbData.builtInShipData[itemObj.name]
    if not shipData["skinnable"]:
        await message.channel.send(":x: That ship is not skinnable!")
        return

    if len(bbGlobals.currentRenders) >= bbConfig.maxConcurrentRenders:
        await message.channel.send(":x: My rendering queue is full currently. Please try this command again once someone else's render has completed.")
        return
    if itemObj.name in bbGlobals.currentRenders:
        await message.channel.send(":x: Someone else is currently rendering this ship! Please use this command again once my other " + itemObj.name + " render has completed.")
        return
        
    bbGlobals.currentRenders.append(itemObj.name)

    if len(message.attachments) < 1:
        await message.channel.send(":x: Please attach a 2048x2048 jpg to render.")
        bbGlobals.currentRenders.remove(itemObj.name)
        return
    skinFile = message.attachments[0]
    if (not skinFile.filename.lower().endswith(".jpg")) or not (skinFile.width == 2048 and skinFile.height == 2048):
        await message.channel.send(":x: Please attach a 2048x2048 jpg to render.")
        bbGlobals.currentRenders.remove(itemObj.name)
        return
    try:
        await skinFile.save(CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_0.jpg")
    except (discord.HTTPException, discord.NotFound):
        await message.channel.send(":x: I couldn't download your skin file. Did you delete it?")
        bbGlobals.currentRenders.remove(itemObj.name)
        return

    skinPaths = {0:CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_0.jpg"}
    disabledLayers = []

    if not full:
        layerIndices = [i for i in range(1, shipData["textureRegions"] + 1)]

        layersPickerMsg = await message.channel.send("** **")
        layersPickerMenu = ReactionSkinRegionPicker.ReactionSkinRegionPicker(layersPickerMsg, message.author, bbConfig.skinApplyConfirmTimeoutSeconds, numRegions=shipData["textureRegions"])
        pickedLayers = []
        menuOutput = await layersPickerMenu.doMenu()
        if bbConfig.spiralEmoji in menuOutput:
            pickedLayers = layerIndices
        elif bbConfig.defaultCancelEmoji in menuOutput:
            await message.channel.send("🛑 Skin render cancelled.")
            for skinPath in skinPaths.values():
                os.remove(skinPath)
            bbGlobals.currentRenders.remove(itemObj.name)
            return
        else:
            for react in menuOutput:
                try:
                    pickedLayers.append(bbConfig.numberEmojis.index(react))
                except ValueError:
                    pass
        
        remainingIndices = [i for i in layerIndices if i not in pickedLayers]

        if remainingIndices:
            disabledLayersPickerMenu = ReactionSkinRegionPicker.ReactionSkinRegionPicker(layersPickerMsg, message.author, bbConfig.skinApplyConfirmTimeoutSeconds, possibleRegions=remainingIndices, desc="Would you like to disable any regions?")
            menuOutput = await disabledLayersPickerMenu.doMenu()
            if bbConfig.spiralEmoji in menuOutput:
                disabledLayers = remainingIndices
            elif bbConfig.defaultCancelEmoji in menuOutput:
                await message.channel.send("🛑 Skin render cancelled.")
                for skinPath in skinPaths.values():
                    os.remove(skinPath)
                bbGlobals.currentRenders.remove(itemObj.name)
                return
            else:
                for react in menuOutput:
                    try:
                        disabledLayers.append(bbConfig.numberEmojis.index(react))
                    except ValueError:
                        pass
        
        def showmeAdditionalMessageCheck(newMessage):
            return newMessage.author is message.author and (newMessage.content.lower().startswith(bbConfig.commandPrefix + "cancel") or len(newMessage.attachments) > 0)

        for regionNum in pickedLayers:
            nextLayerMsg = await message.channel.send("Please send your image for texture region #" + str(regionNum) + ", or `" + bbConfig.commandPrefix + "cancel` to cancel the render, within " + str(bbConfig.skinApplyConfirmTimeoutSeconds) + " seconds.")
            try:
                imgMsg = await bbGlobals.client.wait_for("message", check=showmeAdditionalMessageCheck, timeout=bbConfig.skinApplyConfirmTimeoutSeconds)
            except asyncio.TimeoutError:
                await nextLayerMsg.edit(content="This menu has now expired. Please try the command again.")
            else:
                if imgMsg.content.lower().startswith(bbConfig.commandPrefix + "cancel"):
                    await message.channel.send("🛑 Skin render cancelled.")
                    for skinPath in skinPaths.values():
                        os.remove(skinPath)
                    bbGlobals.currentRenders.remove(itemObj.name)
                    return
                nextLayer = imgMsg.attachments[0]
                if (not nextLayer.filename.lower().endswith(".jpg")) or not (nextLayer.width == 2048 and nextLayer.height == 2048):
                    await message.channel.send(":x: Please only give 2048x2048 jpgs!\n🛑 Skin render cancelled.")
                    for skinPath in skinPaths.values():
                        os.remove(skinPath)
                    bbGlobals.currentRenders.remove(itemObj.name)
                    return
                try:
                    await nextLayer.save(CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_" + str(regionNum) + ".jpg")
                except (discord.HTTPException, discord.NotFound):
                    await message.channel.send(":x: I couldn't download your skin file. Did you delete it?\n🛑 Skin render cancelled.")
                    for skinPath in skinPaths.values():
                        os.remove(skinPath)
                    bbGlobals.currentRenders.remove(itemObj.name)
                    return
                skinPaths[regionNum] = CWD + os.sep + bbConfig.tempRendersDir + os.sep + str(message.id) + "_" + str(regionNum) + ".jpg"

    waitMsg = await message.channel.send("🤖 Render started! I'll ping you when I'm done.")
    
    renderPath = shipData["path"] + os.sep + "skins" + os.sep + str(message.id) + "-RENDER.png"
    outSkinPath = shipData["path"] + os.sep + "skins" + os.sep + str(message.id) + ".jpg"

    await lib.discordUtil.startLongProcess(waitMsg)
    try:
        await shipRenderer.renderShip(str(message.id), shipData["path"], shipData["model"], skinPaths, disabledLayers, bbConfig.skinRenderShowmeHDResolution[0], bbConfig.skinRenderShowmeHDResolution[1], full=full)
    except shipRenderer.RenderFailed:
        await message.channel.send(message.author.mention + "\n🥺 Render failed! The error has been logged, please try a different ship.")
        bbLogger.log("Main", "admin_cmd_showmeHD", "HD ship render failed with args: '" + args + "'")
    else:
        with open(renderPath, "rb") as f:
            imageEmbedMsg = await bbGlobals.client.get_channel(bbConfig.showmeSkinRendersChannel).send("HD-u" + str(message.author.id) + "g" + ("DM" if message.channel.type in [discord.ChannelType.private, discord.ChannelType.group] else str(message.guild.id)) + "c" + str(message.channel.id) + "m" + str(message.id), file=discord.File(f))
            renderEmbed = lib.discordUtil.makeEmbed(col=lib.discordUtil.randomColour(), img=imageEmbedMsg.attachments[0].url, authorName="Skin Render Complete!", icon="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/robot_1f916.png", footerTxt="Custom skinned " + itemObj.name.capitalize())
            await message.channel.send(message.author.mention, embed=renderEmbed)
    
    bbGlobals.currentRenders.remove(itemObj.name)

    try:
        os.remove(renderPath)
    except FileNotFoundError:
        pass
    
    for skinPath in skinPaths.values():
        os.remove(skinPath)
    
    try:
        os.remove(outSkinPath)
    except FileNotFoundError:
        pass

    await lib.discordUtil.endLongProcess(waitMsg)
    return
    

bbCommands.register("showmehd", admin_cmd_showmeHD, 1, allowDM=False)
bbCommands.register("showmehd", admin_cmd_showmeHD, 2, allowDM=True)