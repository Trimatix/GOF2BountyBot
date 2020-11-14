import discord

from . import commandsDB as bbCommands
from ..bbConfig import bbConfig, bbData
from ..bbObjects.items import bbShip
from .. import lib, bbGlobals


async def dev_cmd_addSkin(message : discord.Message, args : str, isDM : bool):
    """Make the specified ship compatible with the specified skin.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name and a skin, prefaced with a + character.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")
        return

    if "+" in args:
        if len(args.split("+")) > 2:
            await message.channel.send(":x: Please only provide one skin, with one `+`!")
            return
        args, skin = args.split("+")
    else:
        skin = ""

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

    if skin != "":
        skin = skin.lstrip(" ").lower()
        if skin not in bbData.builtInShipSkins:
            if len(skin) < 20:
                await message.channel.send(":x: The **" + skin + "** skin is not in my database! :detective:")
            else:
                await message.channel.send(":x: The **" + skin[0:15] + "**... skin is not in my database! :detective:")

        elif skin in bbData.builtInShipData[itemObj.name]["compatibleSkins"]:
            await message.channel.send(":x: That skin is already compatible with the **" + itemObj.name + "**!")
        
        else:
            await lib.discordUtil.startLongProcess(message)
            await bbData.builtInShipSkins[skin].addShip(itemObj.name, bbGlobals.client.get_guild(bbConfig.mediaServer).get_channel(bbConfig.skinRendersChannel))
            await lib.discordUtil.endLongProcess(message)
            await message.channel.send("Done!")

    else:
        await message.channel.send(":x: Please provide a skin, prefaced by a `+`!")

bbCommands.register("addSkin", dev_cmd_addSkin, 2)


async def dev_cmd_delSkin(message : discord.Message, args : str, isDM : bool):
    """Remove the specified ship's compatibility with the specified skin.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name and a skin, prefaced with a + character.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")
        return

    if "+" in args:
        if len(args.split("+")) > 2:
            await message.channel.send(":x: Please only provide one skin, with one `+`!")
            return
        args, skin = args.split("+")
    else:
        skin = ""

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

    if skin != "":
        skin = skin.lstrip(" ").lower()
        if skin not in bbData.builtInShipSkins:
            if len(skin) < 20:
                await message.channel.send(":x: The **" + skin + "** skin is not in my database! :detective:")
            else:
                await message.channel.send(":x: The **" + skin[0:15] + "**... skin is not in my database! :detective:")

        elif skin not in bbData.builtInShipData[itemObj.name]["compatibleSkins"]:
            await message.channel.send(":x: That skin is already incompatible with the **" + itemObj.name + "**!")
        
        else:
            await bbData.builtInShipSkins[skin].removeShip(itemObj.name, bbGlobals.client.get_guild(bbConfig.mediaServer).get_channel(bbConfig.skinRendersChannel))
            await message.channel.send("Done!")

    else:
        await message.channel.send(":x: Please provide a skin, prefaced by a `+`!")

bbCommands.register("delSkin", dev_cmd_delSkin, 2)


async def dev_cmd_makeSkin(message : discord.Message, args : str, isDM : bool):
    """Make the specified ship compatible with the specified skin.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a ship name and a skin, prefaced with a + character.
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a ship! Example: `" + bbConfig.commandPrefix + "ship Groza Mk II`")
        return

    if "+" in args:
        if len(args.split("+")) > 2:
            await message.channel.send(":x: Please only provide one skin, with one `+`!")
            return
        args, skin = args.split("+")
    else:
        skin = ""

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

    if skin != "":
        skin = skin.lstrip(" ").lower()
        if skin not in bbData.builtInShipSkins:
            if len(skin) < 20:
                await message.channel.send(":x: The **" + skin + "** skin is not in my database! :detective:")
            else:
                await message.channel.send(":x: The **" + skin[0:15] + "**... skin is not in my database! :detective:")

        elif skin in bbData.builtInShipData[itemObj.name]["compatibleSkins"]:
            await message.channel.send(":x: That skin is already compatible with the **" + itemObj.name + "**!")
        
        else:
            await bbData.builtInShipSkins[skin].addShip(itemObj.name, bbGlobals.client.get_guild(bbConfig.mediaServer).get_channel(bbConfig.skinRendersChannel))
            await message.channel.send("Done!")

    else:
        await message.channel.send(":x: Please provide a skin, prefaced by a `+`!")

bbCommands.register("makeSkin", dev_cmd_makeSkin, 2)


async def dev_cmd_applySkin(message : discord.Message, args : str, isDM : bool):
    """Apply the specified ship skin to the equipped ship.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a skin name
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # verify a item was given
    if args == "":
        await message.channel.send(":x: Please provide a skin!")
        return

    activeShip = bbGlobals.usersDB.getOrAddID(message.author.id).activeShip
    if activeShip.isSkinned:
        await message.channel.send(":x: Your ship already has a skin applied!")
        return

    if args != "":
        skin = args.lower()
        if skin not in bbData.builtInShipSkins:
            if len(skin) < 20:
                await message.channel.send(":x: The **" + skin + "** skin is not in my database! :detective:")
            else:
                await message.channel.send(":x: The **" + skin[0:15] + "**... skin is not in my database! :detective:")

        elif skin not in bbData.builtInShipData[activeShip.name]["compatibleSkins"]:
            await message.channel.send(":x: That skin is incompatible with your active ship! (" + activeShip.name + ")")
        
        else:
            activeShip.applySkin(bbData.builtInShipSkins[skin])
            await message.channel.send("Done!")

bbCommands.register("applySkin", dev_cmd_applySkin, 2)


async def dev_cmd_unapplySkin(message : discord.Message, args : str, isDM : bool):
    """Remove the applied skin from the active ship.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """

    activeShip = bbGlobals.usersDB.getOrAddID(message.author.id).activeShip
    if not activeShip.isSkinned:
        await message.channel.send(":x: Your ship has no skin applied!")
    elif not activeShip.builtIn:
        await message.channel.send(":x: Your ship is not built in, so the original icon cannot be recovered.")
    else:
        activeShip.icon = bbData.builtInShipData[activeShip.name]["icon"]
        activeShip.skin = ""
        activeShip.isSkinned = False
        await message.channel.send("Done!")

bbCommands.register("unApplySkin", dev_cmd_unapplySkin, 2)