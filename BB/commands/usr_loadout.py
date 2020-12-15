import discord

from . import commandsDB as bbCommands
from .. import lib, bbGlobals
from ..bbConfig import bbConfig, bbData
from ..bbObjects import bbUser
from ..bbObjects.items import bbShip


bbCommands.addHelpSection(0, "loadout")


async def cmd_hangar(message : discord.Message, args : str, isDM : bool):
    """return a page listing the calling user's items. Administrators may view the hangar of any user.
    can apply to a specified user, or the calling user if none is specified.
    can apply to a type of item (ships, modules, turrets or weapons), or all items if none is specified.
    can apply to a page, or the first page if none is specified.
    Arguments can be given in any order, and must be separated by a single space.

    TODO: try displaying as a discord message rather than embed?
    TODO: add icons for ships and items!?

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the arguments as specified above
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")

    requestedUser = message.author
    item = "all"
    page = 1

    foundUser = False
    foundItem = False
    foundPage = False

    useDummyData = False

    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! I can only take a target user, an item type (ship/weapon/module), and a page number!")
        return

    if args != "":
        argNum = 1
        for arg in argsSplit:
            if arg != "":
                if lib.discordUtil.getMemberByRefOverDB(arg, dcGuild=message.guild) is not None:
                    if foundUser:
                        await message.channel.send(":x: I can only take one user!")
                        return
                    else:
                        requestedUser = lib.discordUtil.getMemberByRefOverDB(arg, dcGuild=message.guild)
                        foundUser = True

                elif arg.rstrip("s") in bbConfig.validItemNames:
                    if foundItem:
                        await message.channel.send(":x: I can only take one item type (ship/weapon/module/turret)!")
                        return
                    else:
                        item = arg.rstrip("s")
                        foundItem = True

                elif lib.stringTyping.isInt(arg):
                    if foundPage:
                        await message.channel.send(":x: I can only take one page number!")
                        return
                    else:
                        page = int(arg)
                        foundPage = True
                else:
                    await message.channel.send(":x: " + str(argNum) + lib.stringTyping.getNumExtension(argNum) + " argument invalid! I can only take a target user, an item type (ship/weapon/module/turret), and a page number!")
                    return
                argNum += 1

    if requestedUser is None:
        await message.channel.send(":x: Unrecognised user!")
        return

    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        if not foundUser:
            bbGlobals.usersDB.addUser(requestedUser.id)
        else:
            useDummyData = True

    sendChannel = None
    sendDM = False

    if item == "all":
        if message.author.dm_channel is None:
            await message.author.create_dm()
        if message.author.dm_channel is None:
            sendChannel = message.channel
        else:
            sendChannel = message.author.dm_channel
            sendDM = True
    else:
        sendChannel = message.channel

    if useDummyData:
        if page > 1:
            await message.channel.send(":x: " + ("The requested pilot" if foundUser else "You") + " only " + ("has" if foundUser else "have") + " one page of items. Showing page one:")
            page = 1
        elif page < 1:
            await message.channel.send(":x: Invalid page number. Showing page one:")
            page = 1

        hangarEmbed = lib.discordUtil.makeEmbed(titleTxt="Hangar", desc=requestedUser.mention, col=bbData.factionColours["neutral"], footerTxt="All items" if item == "all" else item.rstrip(
            "s").title() + "s - page " + str(page), thumb=requestedUser.avatar_url_as(size=64))

        hangarEmbed.add_field(name="No Stored Items", value="‎", inline=False)
        await message.channel.send(embed=hangarEmbed)
        return

    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)

        if item == "all":
            maxPerPage = bbConfig.maxItemsPerHangarPageAll
        else:
            maxPerPage = bbConfig.maxItemsPerHangarPageIndividual

        if page < 1:
            await message.channel.send(":x: Invalid page number. Showing page one:")
            page = 1
        else:
            maxPage = requestedBBUser.numInventoryPages(item, maxPerPage)
            if maxPage == 0:
                await message.channel.send(":x: " + ("The requested pilot doesn't" if foundUser else "You don't") + " have any " + ("items" if item == "all" else "of that item") + "!")
                return
            elif page > maxPage:
                await message.channel.send(":x: " + ("The requested pilot" if foundUser else "You") + " only " + ("has " if foundUser else "have ") + str(maxPage) + " page(s) of items. Showing page " + str(maxPage) + ":")
                page = maxPage

        hangarEmbed = lib.discordUtil.makeEmbed(titleTxt="Hangar", desc=requestedUser.mention, col=bbData.factionColours["neutral"], footerTxt=("All item" if item == "all" else item.rstrip(
            "s").title()) + "s - page " + str(page) + "/" + str(requestedBBUser.numInventoryPages(item, maxPerPage)), thumb=requestedUser.avatar_url_as(size=64))
        firstPlace = maxPerPage * (page - 1) + 1

        if item in ["all", "ship"]:
            for shipNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("ship", page, maxPerPage) + 1):
                if shipNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Ships**__", inline=False)
                currentItem = requestedBBUser.inactiveShips[shipNum - 1].item
                currentItemCount = requestedBBUser.inactiveShips.items[currentItem].count
                hangarEmbed.add_field(name=str(shipNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") +
                                      currentItem.getNameAndNick(), value=currentItem.statsStringShort(), inline=False)

        if item in ["all", "weapon"]:
            for weaponNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("weapon", page, maxPerPage) + 1):
                if weaponNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Weapons**__", inline=False)
                currentItem = requestedBBUser.inactiveWeapons[weaponNum - 1].item
                currentItemCount = requestedBBUser.inactiveWeapons.items[currentItem].count
                hangarEmbed.add_field(name=str(weaponNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") +
                                      currentItem.name, value=currentItem.statsStringShort(), inline=False)

        if item in ["all", "module"]:
            for moduleNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("module", page, maxPerPage) + 1):
                if moduleNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Modules**__", inline=False)
                currentItem = requestedBBUser.inactiveModules[moduleNum - 1].item
                currentItemCount = requestedBBUser.inactiveModules.items[currentItem].count
                hangarEmbed.add_field(name=str(moduleNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItem.name,
                                      value=currentItem.statsStringShort(), inline=False)

        if item in ["all", "turret"]:
            for turretNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("turret", page, maxPerPage) + 1):
                if turretNum == firstPlace:
                    hangarEmbed.add_field(
                        name="‎", value="__**Stored Turrets**__", inline=False)
                currentItem = requestedBBUser.inactiveTurrets[turretNum - 1].item
                currentItemCount = requestedBBUser.inactiveTurrets.items[currentItem].count
                hangarEmbed.add_field(name=str(turretNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItem.name,
                                      value=currentItem.statsStringShort(), inline=False)

        if item in ["all", "tool"]:	
            for toolNum in range(firstPlace, requestedBBUser.lastItemNumberOnPage("tool", page, maxPerPage) + 1):	
                if toolNum == firstPlace:	
                    hangarEmbed.add_field(	
                        name="‎", value="__**Stored Tools**__", inline=False)	
                currentItem = requestedBBUser.inactiveTools[toolNum - 1].item	
                currentItemCount = requestedBBUser.inactiveTools.items[currentItem].count	
                hangarEmbed.add_field(name=str(toolNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + currentItem.name,	
                                      value=currentItem.statsStringShort(), inline=False)

        try:
            await sendChannel.send(embed=hangarEmbed)
            if sendDM:
                await message.add_reaction(bbConfig.dmSentEmoji.sendable)
        except discord.Forbidden:
            await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")

bbCommands.register("hangar", cmd_hangar, 0, aliases=["hanger"], forceKeepArgsCasing=True, allowDM=True, helpSection="loadout", signatureStr="**hangar** *[item-type]*", longHelp="Display the items stored in your hangar. Give an item type (ship/weapon/turret/module) to only list items of that type.")
bbCommands.register("hangar", cmd_hangar, 1, aliases=["hanger"], forceKeepArgsCasing=True, allowDM=True, signatureStr="**hangar** *[user]* *[item-type]*", shortHelp="Administrators have permission to view the hangars of other users.", longHelp="Display the items stored in your hangar. Give an item type (ship/weapon/turret/module) to only list items of that type.\nAdministrators have permission to view the hangars of other users.")


async def cmd_loadout(message : discord.Message, args : str, isDM : bool):
    """list the requested user's currently equipped items.

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string, or a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedUser = message.author
    useDummyData = False
    userFound = False

    if len(args.split(" ")) > 1:
        await message.channel.send(":x: Too many arguments! I can only take a target user!")
        return

    if args != "":
        requestedUser = lib.discordUtil.getMemberByRefOverDB(args, dcGuild=message.guild)
        if requestedUser is None:
            await message.channel.send(":x: Invalid user requested! Please either ping them, or give their ID!")
            return

    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        if not userFound:
            bbGlobals.usersDB.addUser(requestedUser.id)
        else:
            useDummyData = True

    if useDummyData:
        activeShip = bbShip.bbShip.fromDict(bbUser.defaultShipLoadoutDict)
        loadoutEmbed = lib.discordUtil.makeEmbed(titleTxt="Loadout", desc=requestedUser.mention, col=bbData.factionColours[activeShip.manufacturer] if activeShip.manufacturer in bbData.factionColours else bbData.factionColours[
                                 "neutral"], thumb=activeShip.icon if activeShip.hasIcon else requestedUser.avatar_url_as(size=64))
        loadoutEmbed.add_field(name="Active Ship:", value=activeShip.name +
                               "\n" + activeShip.statsStringNoItems(), inline=False)

        loadoutEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(
            activeShip.weapons)) + "/" + str(activeShip.getMaxPrimaries()) + ("(+)" if activeShip.getMaxPrimaries(shipUpgradesOnly=True) > activeShip.maxPrimaries else "") + "*", inline=False)
        for weaponNum in range(1, len(activeShip.weapons) + 1):
            loadoutEmbed.add_field(name=str(weaponNum) + ". " + (activeShip.weapons[weaponNum - 1].emoji.sendable + " " if activeShip.weapons[weaponNum - 1].hasEmoji else "") + activeShip.weapons[weaponNum - 1].name, value=activeShip.weapons[weaponNum - 1].statsStringShort(), inline=True)

        loadoutEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(
            activeShip.modules)) + "/" + str(activeShip.getMaxModules()) + ("(+)" if activeShip.getMaxModules(shipUpgradesOnly=True) > activeShip.maxModules else "") + "*", inline=False)
        for moduleNum in range(1, len(activeShip.modules) + 1):
            loadoutEmbed.add_field(name=str(moduleNum) + ". " + (activeShip.modules[moduleNum - 1].emoji.sendable + " " if activeShip.modules[moduleNum - 1].hasEmoji else "") + activeShip.modules[moduleNum - 1].name, value=activeShip.modules[moduleNum - 1].statsStringShort(), inline=True)

        loadoutEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(
            activeShip.turrets)) + "/" + str(activeShip.getMaxTurrets()) + ("(+)" if activeShip.getMaxTurrets(shipUpgradesOnly=True) > activeShip.maxTurrets else "") + "*", inline=False)
        for turretNum in range(1, len(activeShip.turrets) + 1):
            loadoutEmbed.add_field(name=str(turretNum) + ". " + (activeShip.turrets[turretNum - 1].emoji.sendable + " " if activeShip.turrets[turretNum - 1].hasEmoji else "") + activeShip.turrets[turretNum - 1].name, value=activeShip.turrets[turretNum - 1].statsStringShort(), inline=True)

        await message.channel.send(embed=loadoutEmbed)
        return

    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
        activeShip = requestedBBUser.activeShip
        loadoutEmbed = lib.discordUtil.makeEmbed(titleTxt="Loadout", desc=requestedUser.mention, col=bbData.factionColours[activeShip.manufacturer] if activeShip.manufacturer in bbData.factionColours else bbData.factionColours[
                                 "neutral"], thumb=activeShip.icon if activeShip.hasIcon else requestedUser.avatar_url_as(size=64))

        if activeShip is None:
            loadoutEmbed.add_field(name="Active Ship:",
                                   value="None", inline=False)
        else:
            loadoutEmbed.add_field(name="Active Ship:", value=activeShip.getNameAndNick(
            ) + "\n" + activeShip.statsStringNoItems(), inline=False)

            if activeShip.getMaxPrimaries() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Weapons**__ *" + str(len(
                    activeShip.weapons)) + "/" + str(activeShip.getMaxPrimaries()) + ("(+)" if activeShip.getMaxPrimaries(shipUpgradesOnly=True) > activeShip.maxPrimaries else "") + "*", inline=False)
                for weaponNum in range(1, len(activeShip.weapons) + 1):
                    loadoutEmbed.add_field(name=str(weaponNum) + ". " + (activeShip.weapons[weaponNum - 1].emoji.sendable + " " if activeShip.weapons[weaponNum - 1].hasEmoji else "") + activeShip.weapons[weaponNum - 1].name, value=activeShip.weapons[weaponNum - 1].statsStringShort(), inline=True)

            if activeShip.getMaxModules() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Modules**__ *" + str(len(
                    activeShip.modules)) + "/" + str(activeShip.getMaxModules()) + ("(+)" if activeShip.getMaxModules(shipUpgradesOnly=True) > activeShip.maxModules else "") + "*", inline=False)
                for moduleNum in range(1, len(activeShip.modules) + 1):
                    loadoutEmbed.add_field(name=str(moduleNum) + ". " + (activeShip.modules[moduleNum - 1].emoji.sendable + " " if activeShip.modules[moduleNum - 1].hasEmoji else "") + activeShip.modules[moduleNum - 1].name, value=activeShip.modules[moduleNum - 1].statsStringShort(), inline=True)

            if activeShip.getMaxTurrets() > 0:
                loadoutEmbed.add_field(name="‎", value="__**Equipped Turrets**__ *" + str(len(
                    activeShip.turrets)) + "/" + str(activeShip.getMaxTurrets()) + ("(+)" if activeShip.getMaxTurrets(shipUpgradesOnly=True) > activeShip.maxTurrets else "") + "*", inline=False)
                for turretNum in range(1, len(activeShip.turrets) + 1):
                    loadoutEmbed.add_field(name=str(turretNum) + ". " + (activeShip.turrets[turretNum - 1].emoji.sendable + " " if activeShip.turrets[turretNum - 1].hasEmoji else "") + activeShip.turrets[turretNum - 1].name, value=activeShip.turrets[turretNum - 1].statsStringShort(), inline=True)

        await message.channel.send(embed=loadoutEmbed)

bbCommands.register("loadout", cmd_loadout, 0, forceKeepArgsCasing=True, allowDM=True, helpSection="loadout", signatureStr="**loadout** *[user]*", shortHelp="Display your current ship and the items equipped onto it, or those equipped by another player.")


async def cmd_equip(message : discord.Message, args : str, isDM : bool):
    """Equip the item of the given item type, at the given index, from the user's inactive items.
    if "transfer" is specified, the new ship's items are cleared, and the old ship's items attempt to fill new ship.
    "transfer" is only valid when equipping a ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number, and optionally "transfer", separated by a single space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar`")
        return
    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `transfer` when equipping a ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item in ["all", "tool"] or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module or turret.")
        return

    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)

    itemNum = argsSplit[1]
    if not lib.stringTyping.isInt(itemNum):
        await message.channel.send(":x: Invalid item number!")
        return
    itemNum = int(itemNum)

    userItemInactives = requestedBBUser.getInactivesByName(item)
    if itemNum > userItemInactives.numKeys:
        await message.channel.send(":x: Invalid item number! You have " + str(userItemInactives.numKeys) + " " + item + "s.")
        return
    if itemNum < 1:
        await message.channel.send(":x: Invalid item number! Must be at least 1.")
        return

    transferItems = False
    if len(argsSplit) == 3:
        if argsSplit[2] == "transfer":
            if item != "ship":
                await message.channel.send(":x: `transfer` can only be used when equipping a ship!")
                return
            transferItems = True
        else:
            await message.channel.send(":x: Invalid argument! Please only give an item type (ship/weapon/module/turret), an item number, and optionally `transfer` when equipping a ship.")
            return

    requestedItem = userItemInactives[itemNum - 1].item

    if item == "ship":
        activeShip = requestedBBUser.activeShip
        if transferItems:
            requestedBBUser.unequipAll(requestedItem)
            requestedBBUser.activeShip.transferItemsTo(requestedItem)
            requestedBBUser.unequipAll(activeShip)

        requestedBBUser.equipShipObj(requestedItem)

        outStr = ":rocket: You switched to the **" + requestedItem.getNameOrNick() + \
            "**."
        if transferItems:
            outStr += "\nItems thay could not fit in your new ship can be found in the hangar."
        await message.channel.send(outStr)

    elif item == "weapon":
        if not requestedBBUser.activeShip.canEquipMoreWeapons():
            await message.channel.send(":x: Your active ship does not have any free weapon slots!")
            return

        requestedBBUser.activeShip.equipWeapon(requestedItem)
        requestedBBUser.inactiveWeapons.removeItem(requestedItem)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    elif item == "module":
        if not requestedBBUser.activeShip.canEquipMoreModules():
            await message.channel.send(":x: Your active ship does not have any free module slots!")
            return

        if not requestedBBUser.activeShip.canEquipModuleType(requestedItem.getType()):
            await message.channel.send(":x: You already have the max of this type of module equipped!")
            return

        requestedBBUser.activeShip.equipModule(requestedItem)
        requestedBBUser.inactiveModules.removeItem(requestedItem)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    elif item == "turret":
        if not requestedBBUser.activeShip.canEquipMoreTurrets():
            await message.channel.send(":x: Your active ship does not have any free turret slots!")
            return

        requestedBBUser.activeShip.equipTurret(requestedItem)
        requestedBBUser.inactiveTurrets.removeItem(requestedItem)

        await message.channel.send(":wrench: You equipped the **" + requestedItem.name + "**.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("equip", cmd_equip, 0, allowDM=True, helpSection="loadout", signatureStr="**equip <item-type> <item-num>** *[transfer]*", shortHelp="Equip the requested item from your hangar onto your active ship. Item numbers can be gotten from `$COMMANDPREFIX$hangar`.", longHelp="Equip the requested item from your hangar onto your active ship. Item numbers are shown next to items in your `$COMMANDPREFIX$hangar`. When equipping a ship, specify `transfer` to move all items to the new ship.")


async def cmd_unequip(message : discord.Message, args : str, isDM : bool):
    """Unequip the item of the given item type, at the given index, from the user's active ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing either "all", or (an item type and either an index number or "all", separated by a single space)
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    unequipAllItems = len(argsSplit) > 0 and argsSplit[0] == "all"

    if not unequipAllItems and len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (all/weapon/module/turret) and an item number from `" + bbConfig.commandPrefix + "hangar` or `all`.")
        return
    if len(argsSplit) > 2:
        await message.channel.send(":x: Too many arguments! Please only give an item type (all/weapon/module/turret), an item number or `all`.")
        return

    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)

    if unequipAllItems:
        requestedBBUser.unequipAll(requestedBBUser.activeShip)

        await message.channel.send(":wrench: You unequipped **all items** from your ship.")
        return

    item = argsSplit[0].rstrip("s")
    if item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: weapon, module or turret.")
        return
    if item == "ship":
        await message.channel.send(":x: You can't go without a ship! Instead, switch to another one.")
        return

    unequipAll = argsSplit[1] == "all"
    if not unequipAll:
        itemNum = argsSplit[1]
        if not lib.stringTyping.isInt(itemNum):
            await message.channel.send(":x: Invalid item number!")
            return
        itemNum = int(itemNum)
        if itemNum > len(requestedBBUser.activeShip.getActivesByName(item)):
            await message.channel.send(":x: Invalid item number! Your ship has " + str(len(requestedBBUser.activeShip.getActivesByName(item))) + " " + item + "s.")
            return
        if itemNum < 1:
            await message.channel.send(":x: Invalid item number! Must be at least 1.")
            return
    else:
        itemNum = None

    if item == "weapon":
        if not requestedBBUser.activeShip.hasWeaponsEquipped():
            await message.channel.send(":x: Your active ship does not have any weapons equipped!")
            return
        if unequipAll:
            for weapon in requestedBBUser.activeShip.weapons:
                requestedBBUser.inactiveWeapons.addItem(weapon)
                requestedBBUser.activeShip.unequipWeaponObj(weapon)

            await message.channel.send(":wrench: You unequipped all **weapons**.")
        else:
            requestedItem = requestedBBUser.activeShip.weapons[itemNum - 1]
            requestedBBUser.inactiveWeapons.addItem(requestedItem)
            requestedBBUser.activeShip.unequipWeaponIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    elif item == "module":
        if not requestedBBUser.activeShip.hasModulesEquipped():
            await message.channel.send(":x: Your active ship does not have any modules equipped!")
            return
        if unequipAll:
            for module in requestedBBUser.activeShip.modules:
                requestedBBUser.inactiveModules.addItem(module)
                requestedBBUser.activeShip.unequipModuleObj(module)

            await message.channel.send(":wrench: You unequipped all **modules**.")
        else:
            requestedItem = requestedBBUser.activeShip.modules[itemNum - 1]
            requestedBBUser.inactiveModules.addItem(requestedItem)
            requestedBBUser.activeShip.unequipModuleIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    elif item == "turret":
        if not requestedBBUser.activeShip.hasTurretsEquipped():
            await message.channel.send(":x: Your active ship does not have any turrets equipped!")
            return
        if unequipAll:
            for turret in requestedBBUser.activeShip.turrets:
                requestedBBUser.inactiveTurrets.addItem(turret)
                requestedBBUser.activeShip.unequipTurretObj(turret)

            await message.channel.send(":wrench: You unequipped all **turrets**.")
        else:
            requestedItem = requestedBBUser.activeShip.turrets[itemNum - 1]
            requestedBBUser.inactiveTurrets.addItem(requestedItem)
            requestedBBUser.activeShip.unequipTurretIndex(itemNum - 1)

            await message.channel.send(":wrench: You unequipped the **" + requestedItem.name + "**.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("unequip", cmd_unequip, 0, allowDM=True, helpSection="loadout", signatureStr="**unequip <item-type> <item-num>**", shortHelp="Move an item from your active ship to your hangar. Item numbers can be gotten from `$COMMANDPREFIX$loadout`.", longHelp="Unequip the requested item from your active ship, into your hangar. Item numbers are shown next to items in your `$COMMANDPREFIX$loadout`.")


async def cmd_nameship(message : discord.Message, args : str, isDM : bool):
    """Set the nickname of the active ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the new nickname.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if bbGlobals.usersDB.userIDExists(message.author.id):
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        requestedBBUser = bbGlobals.usersDB.addUser(message.author.id)

    if requestedBBUser.activeShip is None:
        await message.channel.send(":x: You do not have a ship equipped!")
        return

    if args == "":
        await message.channel.send(":x: Not enough arguments. Please give the new nickname!")
        return

    if (message.author.id not in bbConfig.developers and len(args) > bbConfig.maxShipNickLength) or len(args) > bbConfig.maxDevShipNickLength:
        await message.channel.send(":x: Nicknames must be " + str(bbConfig.maxShipNickLength) + " characters or less!")
        return

    requestedBBUser.activeShip.changeNickname(args)
    await message.channel.send(":pencil: You named your " + requestedBBUser.activeShip.name + ": **" + args + "**.")

bbCommands.register("nameship", cmd_nameship, 0, forceKeepArgsCasing=True, allowDM=True, helpSection="loadout", signatureStr="**nameShip <nickname>**", shortHelp="Give your active ship a nickname!", longHelp="Give your active ship a nickname! The character limit for ship nicknames is 30.")


async def cmd_unnameship(message : discord.Message, args : str, isDM : bool):
    """Remove the nickname of the active ship.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if bbGlobals.usersDB.userIDExists(message.author.id):
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
    else:
        requestedBBUser = bbGlobals.usersDB.addUser(message.author.id)

    if requestedBBUser.activeShip is None:
        await message.channel.send(":x: You do not have a ship equipped!")
        return

    if not requestedBBUser.activeShip.hasNickname:
        await message.channel.send(":x: Your active ship does not have a nickname!")
        return

    requestedBBUser.activeShip.removeNickname()
    await message.channel.send(":pencil: You reset your **" + requestedBBUser.activeShip.name + "**'s nickname.")

bbCommands.register("unnameship", cmd_unnameship, 0, allowDM=True, helpSection="loadout", signatureStr="**unnameShip**", shortHelp="Reset your active ship's nickname.")