import discord

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig
from ..logging import bbLogger
from ..bbObjects import kaamoShop


bbCommands.addHelpSection(0, "kaamo club")


async def cmd_kaamo_get(message : discord.Message, args : str, isDM : bool):
    """Move the item of the given item type, at the given index, from the user's Kaamo Club storage into their hangar.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    # if bbConfig.calculateUserBountyHuntingLevel(requestedBBUser.bountyHuntingXP) >= 10:
    #     await message.channel.send(":x: This command can only be used by level 10 bounty hunters!")
    #     return

    if requestedBBUser.kaamo is None or requestedBBUser.kaamo.totalItems == 0:
        await message.channel.send(":x: There are no items stored in your Kaamo Club!")
    else:
        argsSplit = args.split(" ")
        if len(argsSplit) < 2:
            await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret/tool) and an item number from `" + bbConfig.commandPrefix + "kaamo`")
            return
        if len(argsSplit) > 2:
            await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret/tool), and an item number from `" + bbConfig.commandPrefix + "kaamo`")
            return

        item = argsSplit[0].rstrip("s")
        if item == "all" or item not in bbConfig.validItemNames:
            await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module, turret or tool.")
            return

        itemNum = argsSplit[1]
        
        if not lib.stringTyping.isInt(itemNum):
            await message.channel.send(":x: Invalid item number!")
            return
        itemNum = int(itemNum)

        shopItemStock = requestedBBUser.kaamo.getStockByName(item)
        if itemNum > shopItemStock.numKeys:
            if shopItemStock.numKeys == 0:
                await message.channel.send(":x: There are no " + item + "s in your Kaamo Club!")
            else:
                await message.channel.send(":x: Invalid item number! Your Kaamo Club has " + str(shopItemStock.numKeys) + " " + item + "(s).")
            return

        if itemNum < 1:
            await message.channel.send(":x: Invalid item number! Must be at least 1.")
            return

        requestedItem = shopItemStock[itemNum - 1].item

        if item in ["ship", "weapon", "module", "turret", "tool"]:
            if item == "ship":
                requestedBBUser.kaamo.userBuyShipObj(requestedBBUser, requestedItem)
            elif item == "weapon":
                requestedBBUser.kaamo.userBuyWeaponObj(requestedBBUser, requestedItem)
            elif item == "turret":
                requestedBBUser.kaamo.userBuyTurretObj(requestedBBUser, requestedItem)
            elif item == "module":
                requestedBBUser.kaamo.userBuyModuleObj(requestedBBUser, requestedItem)
            elif item == "tool":
                requestedBBUser.kaamo.userBuyToolObj(requestedBBUser, requestedItem)

            await message.channel.send(":outbox_tray: The **" + requestedItem.name + "** was moved to your hangar.")
        else:
            raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("kaamo get", cmd_kaamo_get, 0, helpSection="kaamo club", allowDM=True, signatureStr="**kaamo get <item-type> <item-number>**", shortHelp="Transfer items from the Kaamo Club to your hangar. This command can only be used by level 10 bounty hunters.")


async def cmd_kaamo_store(message : discord.Message, args : str, isDM : bool):
    """Transfer the item of the given item type, at the given index, from the user's inactive items, to their kaamo club shop.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing an item type and an index number
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    # if bbConfig.calculateUserBountyHuntingLevel(requestedBBUser.bountyHuntingXP) >= 10:
    #     await message.channel.send(":x: This command can only be used by level 10 bounty hunters!")
    #     return
        
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send(":x: Not enough arguments! Please provide both an item type (ship/weapon/module/turret/tool) and an item number from `" + bbConfig.commandPrefix + "kaamo`")
        return
    if len(argsSplit) > 3:
        await message.channel.send(":x: Too many arguments! Please only give an item type (ship/weapon/module/turret/tool) and an item number from `" + bbConfig.commandPrefix + "kaamo`")
        return

    item = argsSplit[0].rstrip("s")
    if item == "all" or item not in bbConfig.validItemNames:
        await message.channel.send(":x: Invalid item name! Please choose from: ship, weapon, module, turret or tool.")
        return

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

    if requestedBBUser.kaamo is None:
        requestedBBUser.kaamo = kaamoShop.KaamoShop()

    requestedItem = userItemInactives[itemNum - 1].item

    if item in ["ship", "weapon", "module", "turret", "tool"]:
        {"weapon":      requestedBBUser.kaamo.userSellWeaponObj,
            "module":   requestedBBUser.kaamo.userSellModuleObj,
            "turret":   requestedBBUser.kaamo.userSellTurretObj,
            "tool":     requestedBBUser.kaamo.userSellToolObj,
            "ship":     requestedBBUser.kaamo.userSellShipObj}[item](requestedBBUser, requestedItem)

        await message.channel.send(":inbox_tray: The **" + requestedItem.name + "** was moved to Kaamo Club storage.")

    else:
        raise NotImplementedError("Valid but unsupported item name: " + item)

bbCommands.register("kaamo store", cmd_kaamo_store, 0, helpSection="kaamo club", allowDM=True, signatureStr="**kaamo store <item-type> <item-number>**", shortHelp="Transfer items from your hangar to the Kaamo Club. This command can only be used by level 10 bounty hunters.")


async def cmd_kaamo(message : discord.Message, args : str, isDM : bool):
    """list the items currently stored in the user's kaamo club.
    Can specify an item type to list. TODO: Make specified item listings more detailed as in !bb bounties

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string, or one of bbConfig.validItemNames
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args.startswith("store"):
        await cmd_kaamo_store(message, args[5:].lstrip(" "), isDM)
        return
    elif args.startswith("get"):
        await cmd_kaamo_get(message, args[3:].lstrip(" "), isDM)
        return

    item = "all"
    if args.rstrip("s") in bbConfig.validItemNames:
        item = args.rstrip("s")
    elif args != "":
        await message.channel.send(":x: Invalid item type! (ship/weapon/module/turret/tool/all)")
        return

    sendChannel = None
    sendDM = False
    callingBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)

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

    shopEmbed = lib.discordUtil.makeEmbed(titleTxt="Kaamo Club Storage", desc=message.author.mention + "\n*" + (str(callingBBUser.kaamo.totalItems) if callingBBUser.kaamo is not None else "0") + "/" + str(bbConfig.kaamoMaxCapacity) + " items*",
                          footerTxt="All items" if item == "all" else (
                              item + "s").title(),
                          thumb=message.author.avatar_url_as(size=64))

    if callingBBUser.kaamo is None or callingBBUser.kaamo.totalItems == 0:
        shopEmbed.add_field(name="‎", value="No items stored.")
    else:
        for currentItemType in ["ship", "weapon", "module", "turret", "tool"]:
            if item in ["all", currentItemType]:
                currentStock = callingBBUser.kaamo.getStockByName(currentItemType)
                for itemNum in range(1, currentStock.numKeys + 1):
                    if itemNum == 1:
                        shopEmbed.add_field(
                            name="‎", value="__**" + currentItemType.title() + "s**__", inline=False)

                    try:
                        currentItem = currentStock[itemNum - 1].item
                    except KeyError:
                        try:
                            bbLogger.log("Main", "cmd_kaamo", "Requested " + currentItemType + " '" + currentStock.keys[itemNum-1].name + "' (index " + str(itemNum-1) + "), which was not found in the shop stock",
                                        category="shop", eventType="UNKWN_KEY")
                        except IndexError:
                            break
                        except AttributeError as e:
                            keysStr = ""
                            for item in currentStock.items:
                                keysStr += str(item) + ", "
                            bbLogger.log("Main", "cmd_kaamo", "Unexpected type in " + currentItemType + "sStock KEYS, index " + str(itemNum-1) + ". Got " + type(currentStock.keys[itemNum-1]).__name__ + ".\nInventory keys: " + keysStr[:-2],
                                        category="shop", eventType="INVTY_KEY_TYPE")
                            shopEmbed.add_field(name=str(itemNum) + ". **⚠ #INVALID-ITEM# '" + currentStock.keys[itemNum-1] + "'",
                                                value="Do not attempt to get. Could cause issues.", inline=True)
                            continue
                        shopEmbed.add_field(name=str(itemNum) + ". **⚠ #INVALID-ITEM# '" + currentStock.keys[itemNum-1].name + "'",
                                            value="Do not attempt to get. Could cause issues.", inline=True)
                        continue

                    currentItemCount = currentStock.items[currentItem].count
                    shopEmbed.add_field(name=str(itemNum) + ". " + (currentItem.emoji.sendable + " " if currentItem.hasEmoji else "") + ((" `(" + str(currentItemCount) + ")` ") if currentItemCount > 1 else "") + "**" + currentItem.name + "**",
                                        value=lib.stringTyping.commaSplitNum(str(currentItem.value)) + " Credits\n" + currentItem.statsStringShort(), inline=True)

    try:
        await sendChannel.send(embed=shopEmbed)
    except discord.Forbidden:
        await message.channel.send(":x: I can't DM you, " + message.author.display_name + "! Please enable DMs from users who are not friends.")
        return
    if sendDM:
        await message.add_reaction(bbConfig.dmSentEmoji.sendable)

bbCommands.register("kaamo", cmd_kaamo, 0, allowDM=True, helpSection="kaamo club", signatureStr="**kaamo** *[item-type]*", shortHelp="List all items in your Kaamo Club storage. Kaamo has a max capacity of " + str(bbConfig.kaamoMaxCapacity) + " items, including items on ships.", longHelp="List all items in your Kaamo Club storage. Kaamo has a max capacity of " + str(bbConfig.kaamoMaxCapacity) + " items, including items on ships. Give an item type (ship/weapon/turret/module/tool) to only list items of that type.\n\n⚠ Please be aware that `kaamo store` and `kaamo get` can only be used be level 10 bounty hunters.")
