import discord

from . import commandsDB as bbCommands
from ..bbConfig import bbData, bbConfig
from .. import lib
from ..bbObjects.items import bbShip

async def cmd_map(message : discord.Message, args : str, isDM : bool):
    """send the image of the GOF2 starmap. If -g is passed, send the grid image

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain -g
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # If -g is specified, send the image with grid overlay
    if args == "-g":
        await message.channel.send(bbData.mapImageWithGraphLink)
    # otherwise, send the image with no grid overlay
    else:
        await message.channel.send(bbData.mapImageNoGraphLink)

bbCommands.register("map", cmd_map, 0, aliases=["starmap"], allowDM=True)


async def cmd_make_route(message : discord.Message, args : str, isDM : bool):
    """display the shortest route between two systems

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the start and end systems, separated by a comma and a space
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify two systems are given separated by a comma and a space
    if args == "" or "," not in args or len(args[:args.index(",")]) < 1 or len(args[args.index(","):]) < 2:
        await message.channel.send(":x: Please provide source and destination systems, separated with a comma and space.\nFor example: `" + bbConfig.commandPrefix + "make-route Pescal Inartu, Loma`")
        return
    if args.count(",") > 1:
        await message.channel.send(":x: Please only provide **two** systems!")
        return

    requestedStart = args.split(",")[0].title()
    requestedEnd = args.split(",")[1][1:].title()
    startSyst = ""
    endSyst = ""

    # attempt to look up the requested systems in the built in systems database
    systemsFound = {requestedStart: False, requestedEnd: False}
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(requestedStart):
            systemsFound[requestedStart] = True
            startSyst = syst
        if bbData.builtInSystemObjs[syst].isCalled(requestedEnd):
            systemsFound[requestedEnd] = True
            endSyst = syst

    # report any unrecognised systems
    for syst in [requestedStart, requestedEnd]:
        if not systemsFound[syst]:
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system is not on my star map! :map:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system is not on my star map! :map:")
            return

    # report any systems that were recognised, but do not have any neighbours
    for syst in [startSyst, endSyst]:
        if not bbData.builtInSystemObjs[syst].hasJumpGate():
            if len(syst) < 20:
                await message.channel.send(":x: The **" + syst + "** system does not have a jump gate! :rocket:")
            else:
                await message.channel.send(":x: The **" + syst[0:15] + "**... system does not have a jump gate! :rocket:")
            return

    # build and print the route, reporting any errors in the route generation process
    routeStr = ""
    for currentSyst in lib.pathfinding.makeRoute(startSyst, endSyst):
        routeStr += currentSyst + ", "
    if routeStr.startswith("#"):
        await message.channel.send(":x: ERR: Processing took too long! :stopwatch:")
    elif routeStr.startswith("!"):
        await message.channel.send(":x: ERR: No route found! :triangular_flag_on_post:")
    elif startSyst == endSyst:
        await message.channel.send(":thinking: You're already there, pilot!")
    else:
        await message.channel.send("Here's the shortest route from **" + startSyst + "** to **" + endSyst + "**:\n> " + routeStr[:-2] + " :rocket:")

bbCommands.register("make-route", cmd_make_route, 0, allowDM=True)


async def cmd_system(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified system

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a system in the GOF2 starmap
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a systemw as specified
    if args == "":
        await message.channel.send(":x: Please provide a system! Example: `" + bbConfig.commandPrefix + "system Augmenta`")
        return

    # attempt to look up the specified system
    systArg = args.title()
    systObj = None
    for syst in bbData.builtInSystemObjs.keys():
        if bbData.builtInSystemObjs[syst].isCalled(systArg):
            systObj = bbData.builtInSystemObjs[syst]

    # report unrecognised systems
    if systObj is None:
        if len(systArg) < 20:
            await message.channel.send(":x: The **" + systArg + "** system is not on my star map! :map:")
        else:
            await message.channel.send(":x: The **" + systArg[0:15] + "**... system is not on my star map! :map:")
    else:
        # build the neighbours statistic into a string
        neighboursStr = ""
        for x in systObj.neighbours:
            neighboursStr += x + ", "
        if neighboursStr == "":
            neighboursStr = "No Jumpgate"
        else:
            neighboursStr = neighboursStr[:-2]

        # build the statistics embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[systObj.faction], desc="__System Information__",
                               titleTxt=systObj.name, footerTxt=systObj.faction.title(), thumb=bbData.factionIcons[systObj.faction])
        statsEmbed.add_field(
            name="Security Level:", value=bbData.securityLevels[systObj.security].title())
        statsEmbed.add_field(name="Neighbour Systems:", value=neighboursStr)

        # list the system's aliases as a string
        if len(systObj.aliases) > 1:
            aliasStr = ""
            for alias in systObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        # list the system's wiki if one exists
        if systObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + systObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-system", 0, cmd_system)


async def cmd_criminal(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt criminal

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a criminal name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a criminal was given
    if args == "":
        await message.channel.send(":x: Please provide a criminal! Example: `" + bbConfig.commandPrefix + "criminal Toma Prakupy`")
        return

    # look up the criminal object
    criminalName = args.title()
    criminalObj = None
    for crim in bbData.builtInCriminalObjs.keys():
        if bbData.builtInCriminalObjs[crim].isCalled(criminalName):
            criminalObj = bbData.builtInCriminalObjs[crim]

    # report unrecognised criminal names
    if criminalObj is None:
        if len(criminalName) < 20:
            await message.channel.send(":x: **" + criminalName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + criminalName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[criminalObj.faction],
                               desc="__Criminal File__", titleTxt=criminalObj.name, thumb=criminalObj.icon)
        statsEmbed.add_field(
            name="Wanted By:", value=criminalObj.faction.title() + "s")
        # include the criminal's aliases and wiki if they exist
        if len(criminalObj.aliases) > 1:
            aliasStr = ""
            for alias in criminalObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if criminalObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + criminalObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-criminal", 0, cmd_criminal)


async def cmd_ship(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt ship

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")
        return

    # look up the ship object
    itemName = args.title()
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

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Ship File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        statsEmbed.add_field(name="Value:", value=lib.stringTyping.commaSplitNum(
            str(itemObj.getValue(shipUpgradesOnly=True))) + " Credits")
        statsEmbed.add_field(name="Armour:", value=str(itemObj.getArmour()))
        statsEmbed.add_field(name="Cargo:", value=str(itemObj.getCargo()))
        statsEmbed.add_field(
            name="Handling:", value=str(itemObj.getHandling()))
        statsEmbed.add_field(name="Max Primaries:",
                             value=str(itemObj.getMaxPrimaries()))
        if len(itemObj.weapons) > 0:
            weaponStr = "*["
            for weapon in itemObj.weapons:
                weaponStr += weapon.name + ", "
            statsEmbed.add_field(name="Equipped Primaries:",
                                 value=weaponStr[:-2] + "]*")
        statsEmbed.add_field(name="Max Secondaries:",
                             value=str(itemObj.getNumSecondaries()))
        # if len(itemObj.secondaries) > 0:
        #     secondariesStr = "*["
        #     for secondary in itemObj.secondaries:
        #         secondariesStr += secondary.name + ", "
        #     statsEmbed.add_field(name="Equipped Secondaries",value=secondariesStr[:-2] + "]*")
        statsEmbed.add_field(name="Turret Slots:",
                             value=str(itemObj.getMaxTurrets()))
        if len(itemObj.turrets) > 0:
            turretsStr = "*["
            for turret in itemObj.turrets:
                turretsStr += turret.name + ", "
            statsEmbed.add_field(name="Equipped Turrets:",
                                 value=turretsStr[:-2] + "]*")
        statsEmbed.add_field(name="Modules Slots:",
                             value=str(itemObj.getMaxModules()))
        if len(itemObj.modules) > 0:
            modulesStr = "*["
            for module in itemObj.modules:
                modulesStr += module.name + ", "
            statsEmbed.add_field(name="Equipped Modules:",
                                 value=modulesStr[:-2] + "]*")
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-ship", 0, cmd_ship)


async def cmd_weapon(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt weapon

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a weapon name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a weapon! Example: `" + bbConfig.commandPrefix + "weapon Nirai Impulse EX 1`")
        return

    # look up the weapon object
    itemName = args.title()
    itemObj = None
    for weap in bbData.builtInWeaponObjs.keys():
        if bbData.builtInWeaponObjs[weap].isCalled(itemName):
            itemObj = bbData.builtInWeaponObjs[weap]

    # report unrecognised weapon names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Weapon File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:", value=str(itemObj.dps))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-weapon", 0, cmd_weapon)


async def cmd_module(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt module

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a module name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a module! Example: `" + bbConfig.commandPrefix + "module Groza Mk II`")
        return

    # look up the module object
    itemName = args.title()
    itemObj = None
    for module in bbData.builtInModuleObjs.keys():
        if bbData.builtInModuleObjs[module].isCalled(itemName):
            itemObj = bbData.builtInModuleObjs[module]

    # report unrecognised module names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Module File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="Stats:", value=str(
            itemObj.statsStringShort()))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-module", 0, cmd_module)


async def cmd_turret(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt turret

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a turret name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a turret! Example: `" + bbConfig.commandPrefix + "turret Groza Mk II`")
        return

    # look up the turret object
    itemName = args.title()
    itemObj = None
    for turr in bbData.builtInTurretObjs.keys():
        if bbData.builtInTurretObjs[turr].isCalled(itemName):
            itemObj = bbData.builtInTurretObjs[turr]

    # report unrecognised turret names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(col=bbData.factionColours[itemObj.manufacturer] if itemObj.manufacturer in bbData.factionColours else bbData.factionColours["neutral"],
                               desc="__Turret File__", titleTxt=itemObj.name, thumb=itemObj.icon if itemObj.hasIcon else bbData.rocketIcon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(name="Value:", value=str(itemObj.value))
        statsEmbed.add_field(name="DPS:", value=str(itemObj.dps))
        statsEmbed.add_field(name="Max Shop Spawn Chance:",
                             value=str(itemObj.shopSpawnRate) + "%\nFor shop level " + str(itemObj.techLevel))
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-turret", 0, cmd_turret)


async def cmd_commodity(message : discord.Message, args : str, isDM : bool):
    """return statistics about a specified inbuilt commodity

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a commodity name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("Commodity items have not been implemented yet!")
    return

    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a commodity! Example: `" + bbConfig.commandPrefix + "commodity Groza Mk II`")
        return

    # look up the commodity object
    itemName = args.title()
    itemObj = None
    for crim in bbData.builtInCommodityObjs.keys():
        if bbData.builtInCommodityObjs[crim].isCalled(itemName):
            itemObj = bbData.builtInCommodityObjs[crim]

    # report unrecognised commodity names
    if itemObj is None:
        if len(itemName) < 20:
            await message.channel.send(":x: **" + itemName + "** is not in my database! :detective:")
        else:
            await message.channel.send(":x: **" + itemName[0:15] + "**... is not in my database! :detective:")

    else:
        # build the stats embed
        statsEmbed = lib.discordUtil.makeEmbed(
            col=bbData.factionColours[itemObj.faction], desc="__Item File__", titleTxt=itemObj.name, thumb=itemObj.icon)
        if itemObj.hasTechLevel:
            statsEmbed.add_field(name="Tech Level:", value=itemObj.techLevel)
        statsEmbed.add_field(
            name="Wanted By:", value=itemObj.faction.title() + "s")
        # include the item's aliases and wiki if they exist
        if len(itemObj.aliases) > 1:
            aliasStr = ""
            for alias in itemObj.aliases:
                aliasStr += alias + ", "
            statsEmbed.add_field(
                name="Aliases:", value=aliasStr[:-2], inline=False)
        if itemObj.hasWiki:
            statsEmbed.add_field(
                name="‎", value="[Wiki](" + itemObj.wiki + ")", inline=False)
        # send the embed
        await message.channel.send(embed=statsEmbed)

# bbCommands.register("info-commodity", 0, cmd_commodity)


async def cmd_info(message : discord.Message, args : str, isDM : bool):
    """Return statistics about a named game object, of a specified type.
    The named used to reference the object may be an alias.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an object type, followed by a space, followed by the object name. For example, 'criminal toma prakupy'
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send(":x: Please give an object type to look up! (system/criminal/ship/weapon/module/turret/commodity)")
        return

    argsSplit = args.split(" ")
    if argsSplit[0] not in ["system", "criminal", "ship", "weapon", "module", "turret", "commodity"]:
        await message.channel.send(":x: Invalid object type! (system/criminal/ship/weapon/module/turret/commodity)")
        return

    if argsSplit[0] == "system":
        await cmd_system(message, args[7:], isDM)
    elif argsSplit[0] == "criminal":
        await cmd_criminal(message, args[9:], isDM)
    elif argsSplit[0] == "ship":
        await cmd_ship(message, args[5:], isDM)
    elif argsSplit[0] == "weapon":
        await cmd_weapon(message, args[7:], isDM)
    elif argsSplit[0] == "module":
        await cmd_module(message, args[7:], isDM)
    elif argsSplit[0] == "turret":
        await cmd_turret(message, args[7:], isDM)
    elif argsSplit[0] == "commodity":
        await cmd_commodity(message, args[10:], isDM)
    else:
        await message.channel.send(":x: Unknown object type! (system/criminal/ship/weapon/module/turret/commodity)")

bbCommands.register("info", cmd_info, 0, allowDM=True)