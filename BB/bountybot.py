# Discord Imports

import discord
from discord.ext.commands import Bot as ClientBaseClass

# Utility Imports

from datetime import datetime
import asyncio
import traceback
import os

# BountyBot Imports

from .bbConfig import bbConfig, bbData, bbPRIVATE
from .bbObjects import bbShipSkin
from .bbObjects.bounties import bbCriminal, bbSystem
from .bbObjects.items import bbModuleFactory, bbShipUpgrade, bbTurret, bbWeapon
from .bbObjects.items.tools import bbShipSkinTool, bbToolItemFactory
from .scheduling import TimedTask
from .bbDatabases import bbGuildDB, bbUserDB, HeirarchicalCommandsDB, reactionMenuDB
from .scheduling import TimedTaskHeap
from . import lib, bbGlobals
from .logging import bbLogger



class bbClient(ClientBaseClass):
    """A minor extension to discord.ext.commands.Bot to include database saving and extended shutdown procedures.

    A command_prefix is assigned to this bot, but no commands are registered to it, so this is effectively meaningless.
    I chose to assign a zero-width character, as this is unlikely to ever be chosen as the bot's actual command prefix, minimising erroneous commands.Bot command recognition. 
    
    :var bb_loggedIn: Tracks whether or not the bot is currently logged in
    :type bb_loggedIn: bool
    """
    def __init__(self):
        super().__init__(command_prefix="‎")
        self.bb_loggedIn = False

    
    def bb_saveAllDBs(self):
        """Save all of the bot's savedata to file.
        This currently saves:
        - the users database
        - the bounties database
        - the guilds database
        - the reaction menus database
        """
        lib.jsonHandler.saveDB(bbConfig.userDBPath, bbGlobals.usersDB)
        lib.jsonHandler.saveDB(bbConfig.guildDBPath, bbGlobals.guildsDB)
        lib.jsonHandler.saveDB(bbConfig.reactionMenusDBPath, bbGlobals.reactionMenusDB)
        bbLogger.save()
        print(datetime.now().strftime("%H:%M:%S: Data saved!"))


    async def bb_shutdown(self):
        """Cleanly prepare for, and then perform, shutdown of the bot.

        This currently:
        - expires all non-saveable reaction menus
        - logs out of discord
        - saves all savedata to file
        """
        menus = list(bbGlobals.reactionMenusDB.values())
        for menu in menus:
            if not menu.saveable:
                await menu.delete()
        self.bb_loggedIn = False
        await self.logout()
        self.bb_saveAllDBs()
        print(datetime.now().strftime("%H:%M:%S: Data saved!"))



####### GLOBAL VARIABLES #######

# interface into the discord servers
bbGlobals.client = bbClient()

# BountyBot commands DB
from . import commands
bbCommands = commands.loadCommands()

CWD = os.getcwd()



####### DATABASE FUNCTIONS #####

def loadUsersDB(filePath : str) -> bbUserDB.bbUserDB:
    """Build a bbUserDB from the specified JSON file.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a bbUserDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return bbUserDB.fromDict(lib.jsonHandler.readJSON(filePath))


def loadGuildsDB(filePath : str, dbReload : bool = False) -> bbGuildDB.bbGuildDB:
    """Build a bbGuildDB from the specified JSON file.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :param bool dbReload: Whether or not this DB is being created during the initial database loading phase of bountybot. This is used to toggle name checking in bbBounty contruction.
    :return: a bbGuildDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return bbGuildDB.fromDict(lib.jsonHandler.readJSON(filePath), dbReload=dbReload)


async def loadReactionMenusDB(filePath : str) -> reactionMenuDB.ReactionMenuDB:
    """Build a reactionMenuDB from the specified JSON file.
    This method must be called asynchronously, to allow awaiting of discord message fetching functions.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a reactionMenuDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return await reactionMenuDB.fromDict(lib.jsonHandler.readJSON(filePath))



####### UTIL FUNCTIONS #######

async def announceNewShopStock(guildID : int = -1):
    """Announce the refreshing of shop stocks to one or all joined guilds.
    Messages will be sent to the playChannels of all guilds in the bbGlobals.guildsDB, if they have one

    :param int guildID: The guild to announce to. If guildID is -1, the shop refresh will be announced to all joined guilds. (Default -1)
    """
    if guildID == -1:
        # loop over all guilds
        for guild in bbGlobals.guildsDB.guilds.values():
            # ensure guild has a valid playChannel
            if not guild.shopDisabled:
                await guild.announceNewShopStock()
    else:
        guild = bbGlobals.guildsDB.getGuild(guildID)
        # ensure guild has a valid playChannel
        if not guild.shopDisabled:
            await guild.announceNewShopStock()


async def refreshAndAnnounceAllShopStocks():
    """Generate new tech levels and inventories for the shops of all joined guilds,
    and announce the stock refresh to those guilds.
    """
    bbGlobals.guildsDB.refreshAllShopStocks()
    await announceNewShopStock()



####### SYSTEM COMMANDS #######

async def err_nodm(message : discord.Message, args : str, isDM : bool):
    """Send an error message when a command is requested that cannot function outside of a guild

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: ignored
    """
    await message.channel.send(":x: This command can only be used from inside of a server!")


async def dummy_command(message : discord.Message, args : str, isDM : bool):
    """Dummy command doing nothing at all.
    Useful when waiting for commands with client.wait_for from a non-blocking process.

    :param discord.Message message: ignored
    :param str args: ignored
    :param bool isDM: ignored
    """
    pass

bbCommands.register("cancel", dummy_command, 0, allowDM=True, noHelp=True)



####### MAIN FUNCTIONS #######

@bbGlobals.client.event
async def on_guild_join(guild : discord.Guild):
    """Create a database entry for new guilds when one is joined.
    TODO: Once deprecation databases are implemented, if guilds now store important information consider searching for them in deprecated

    :param discord.Guild guild: the guild just joined.
    """
    guildExists = True
    if not bbGlobals.guildsDB.guildIdExists(guild.id):
        guildExists = False
        bbGlobals.guildsDB.addGuildID(guild.id)
    bbLogger.log("Main", "guild_join", "I joined a new guild! " + guild.name + "#" + str(guild.id) + ("\n -- The guild was added to bbGlobals.guildsDB" if not guildExists else ""),
                 category="guildsDB", eventType="NW_GLD")


@bbGlobals.client.event
async def on_guild_remove(guild : discord.Guild):
    """Remove the database entry for any guilds the bot leaves.
    TODO: Once deprecation databases are implemented, if guilds now store important information consider moving them to deprecated.

    :param discord.Guild guild: the guild just left.
    """
    guildExists = False
    if bbGlobals.guildsDB.guildIdExists(guild.id):
        guildExists = True
        bbGlobals.guildsDB.removeGuildId(guild.id)
    bbLogger.log("Main", "guild_remove", "I left a guild! " + guild.name + "#" + str(guild.id) + ("\n -- The guild was removed from bbGlobals.guildsDB" if guildExists else ""),
                 category="guildsDB", eventType="NW_GLD")


@bbGlobals.client.event
async def on_ready():
    """Bot initialisation (called on bot login) and behaviour loops.
    Currently includes:
    - new bounty spawning
    - shop stock refreshing
    - regular database saving to JSON

    TODO: Add bounty expiry and reaction menu (e.g duel challenges) expiry
    TODO: Implement dynamic timedtask checking period
    TODO: Move item initialization to separate method
    """
    ##### EMOJI INITIALIZATION #####

    # Iterate over uninitiaizedEmoji attributes in bbConfig
    for varName, varValue in vars(bbConfig).items():
        if isinstance(varValue, lib.emojis.UninitializedDumbEmoji):
            uninitEmoji = varValue.value
            # Create dumbEmoji instances based on the type of the uninitialized value
            if isinstance(uninitEmoji, int):
                setattr(bbConfig, varName, lib.emojis.dumbEmoji(id=uninitEmoji))
            elif isinstance(uninitEmoji, str):
                setattr(bbConfig, varName, lib.emojis.dumbEmojiFromStr(uninitEmoji))
            elif isinstance(uninitEmoji, dict):
                setattr(bbConfig, varName, lib.emojis.dumbEmojiFromDict(uninitEmoji))
            # Unrecognised uninitialized value
            else:
                raise ValueError("Unrecognised UninitializedDumbEmoji value type. Expecting int, str or dict, given '" + uninitEmoji.__class__.__name__ + "'")
    
    # Ensure all emojis have been initialized
    for varName, varValue in vars(bbConfig).items():
        if isinstance(varValue, lib.emojis.UninitializedDumbEmoji):
            raise RuntimeError("Uninitialized emoji still remains in bbConfig after emoji initialization: '" + varName + "'")


    ##### OBJECT SPAWNING #####

    # generate bbCriminal objects from data in bbData
    for criminalDict in bbData.builtInCriminalData.values():
        bbData.builtInCriminalObjs[criminalDict["name"]] = bbCriminal.fromDict(criminalDict)
        bbData.builtInCriminalObjs[criminalDict["name"]].builtIn = True
        bbData.builtInCriminalData[criminalDict["name"]]["builtIn"] = True

    # generate bbSystem objects from data in bbData
    for systemDict in bbData.builtInSystemData.values():
        bbData.builtInSystemObjs[systemDict["name"]] = bbSystem.fromDict(systemDict)
        bbData.builtInSystemData[systemDict["name"]]["builtIn"] = True
        bbData.builtInSystemObjs[systemDict["name"]].builtIn = True

    # generate bbModule objects from data in bbData
    for moduleDict in bbData.builtInModuleData.values():
        bbData.builtInModuleObjs[moduleDict["name"]] = bbModuleFactory.fromDict(moduleDict)
        bbData.builtInModuleData[moduleDict["name"]]["builtIn"] = True
        bbData.builtInModuleObjs[moduleDict["name"]].builtIn = True

    # generate bbWeapon objects from data in bbData
    for weaponDict in bbData.builtInWeaponData.values():
        bbData.builtInWeaponObjs[weaponDict["name"]] = bbWeapon.fromDict(weaponDict)
        bbData.builtInWeaponData[weaponDict["name"]]["builtIn"] = True
        bbData.builtInWeaponObjs[weaponDict["name"]].builtIn = True

    # generate bbUpgrade objects from data in bbData
    for upgradeDict in bbData.builtInUpgradeData.values():
        bbData.builtInUpgradeObjs[upgradeDict["name"]] = bbShipUpgrade.fromDict(upgradeDict)
        bbData.builtInUpgradeData[upgradeDict["name"]]["builtIn"] = True
        bbData.builtInUpgradeObjs[upgradeDict["name"]].builtIn = True

    # generate bbTurret objects from data in bbData
    for turretDict in bbData.builtInTurretData.values():
        bbData.builtInTurretObjs[turretDict["name"]] = bbTurret.fromDict(turretDict)
        bbData.builtInTurretData[turretDict["name"]]["builtIn"] = True
        bbData.builtInTurretObjs[turretDict["name"]].builtIn = True



    ##### ITEM TECHLEVEL AUTO-GENERATION #####

    # Assign each shipDict a techLevel, based on their value
    for shipDict in bbData.builtInShipData.values():
        for tl in range(len(bbConfig.shipMaxPriceTechLevels)):
            if bbConfig.shipMaxPriceTechLevels[tl] >= shipDict["value"]:
                shipDict["techLevel"] = tl + 1
                break


    ##### SHIP SKIN GENERATION #####

    # generate bbShipSkin objects from data stored on file
    for subdir, dirs, files in os.walk(bbData.skinsDir):
        for dirname in dirs:
            dirpath = subdir + os.sep + dirname

            if dirname.lower().endswith(".bbshipskin"):
                skinData = lib.jsonHandler.readJSON(dirpath + os.sep + "META.json")
                skinData["path"] = CWD + os.sep + dirpath
                bbData.builtInShipSkins[skinData["name"].lower()] = bbShipSkin.fromDict(skinData)

    # generate bbToolItem objects from data stored on file
    for toolDict in bbData.builtInToolData.values():
        bbData.builtInToolObjs[toolDict["name"]] = bbToolItemFactory.fromDict(toolDict)
        bbData.builtInToolData[toolDict["name"]]["builtIn"] = True
        bbData.builtInToolObjs[toolDict["name"]].builtIn = True
    
    # generate bbShipSkinTool objects for each bbShipSkin
    for shipSkin in bbData.builtInShipSkins.values():
        # if len(shipSkin.compatibleShips) > 0:
        toolName = lib.stringTyping.shipSkinNameToToolName(shipSkin.name)
        if toolName not in bbData.builtInToolObjs:
            bbData.builtInToolObjs[toolName] = bbShipSkinTool.bbShipSkinTool(shipSkin, value=bbConfig.shipSkinValueForTL(shipSkin.averageTL), builtIn=True)


    ##### SORT ITEMS BY TECHLEVEL #####

    # Initialise shipKeysByTL as maxTechLevel empty arrays
    bbData.shipKeysByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]

    # Sort ship keys by tech level
    for currentShipKey in bbData.builtInShipData.keys():
        bbData.shipKeysByTL[bbData.builtInShipData[currentShipKey]["techLevel"] - 1].append(currentShipKey)

    # Sort module objects by tech level
    bbData.moduleObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
    for currentModuleObj in bbData.builtInModuleObjs.values():
        bbData.moduleObjsByTL[currentModuleObj.techLevel - 1].append(currentModuleObj)

    # Sort weapon objects by tech level
    bbData.weaponObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
    for currentWeaponObj in bbData.builtInWeaponObjs.values():
        bbData.weaponObjsByTL[currentWeaponObj.techLevel - 1].append(currentWeaponObj)

    # Sort turret objects by tech level
    bbData.turretObjsByTL = [[] for currentTL in range(bbConfig.minTechLevel, bbConfig.maxTechLevel + 1)]
    for currentTurretObj in bbData.builtInTurretObjs.values():
        bbData.turretObjsByTL[currentTurretObj.techLevel - 1].append(currentTurretObj)


    print("[bbConfig.init] Ship tech levels generated:")
    for shipTL in range(len(bbData.shipKeysByTL)):
        print("\t• <=" + str(bbConfig.shipMaxPriceTechLevels[shipTL]) + "=TL" + str(shipTL+1) + ":",end="")
        for shipName in bbData.shipKeysByTL[shipTL]:
            print(" " + shipName + ",",end="")
        print()



    ##### MAX SPAWNRATE CALCULATION #####

    for ship in bbData.builtInShipData.values():
        ship["shopSpawnRate"] = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[ship["techLevel"] - 1][ship["techLevel"] - 1] / len(bbData.shipKeysByTL[ship["techLevel"] - 1])) * 100)

    for weapon in bbData.builtInWeaponObjs.values():
        weapon.shopSpawnRate = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[weapon.techLevel - 1][weapon.techLevel - 1] / len(bbData.weaponObjsByTL[weapon.techLevel - 1])) * 100)

    for module in bbData.builtInModuleObjs.values():
        module.shopSpawnRate = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[module.techLevel - 1][module.techLevel - 1] / len(bbData.moduleObjsByTL[module.techLevel - 1])) * 100)

    for turret in bbData.builtInTurretObjs.values():
        turret.shopSpawnRate = bbConfig.truncToRes((bbConfig.itemTLSpawnChanceForShopTL[turret.techLevel - 1][turret.techLevel - 1] / len(bbData.turretObjsByTL[turret.techLevel - 1])) * 100)



    # bbGlobals.newBountiesTTDB = TimedTaskHeap.TimedTaskHeap()
    # Databases
    bbGlobals.usersDB = loadUsersDB(bbConfig.userDBPath)
    bbGlobals.guildsDB = loadGuildsDB(bbConfig.guildDBPath, dbReload=True)

    for guild in bbGlobals.guildsDB.getGuilds():
        if guild.hasBountyBoardChannel:
            if bbGlobals.client.get_channel(guild.bountyBoardChannel.channelIDToBeLoaded) is None:
                guild.removeBountyBoardChannel()
            else:
                await guild.bountyBoardChannel.init(bbGlobals.client, bbData.bountyFactions)

    # Set help embed thumbnails
    for levelSection in bbCommands.helpSectionEmbeds:
        for helpSection in levelSection.values():
            for embed in helpSection:
                embed.set_thumbnail(url=bbGlobals.client.user.avatar_url_as(size=64))

    # for currentUser in bbGlobals.usersDB.users.values():
    #     currentUser.validateLoadout()

    print('We have logged in as {0.user}'.format(bbGlobals.client))
    await bbGlobals.client.change_presence(activity=discord.Game("Galaxy on Fire 2™ Full HD"))
    # bot is now logged in
    bbGlobals.client.bb_loggedIn = True
    
    # bbGlobals.shopRefreshTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.shopRefreshStockPeriod), autoReschedule=True, expiryFunction=refreshAndAnnounceAllShopStocks)
    bbGlobals.dbSaveTT = TimedTask.TimedTask(expiryDelta=lib.timeUtil.timeDeltaFromDict(bbConfig.savePeriod), autoReschedule=True, expiryFunction=bbGlobals.client.bb_saveAllDBs)

    # bbGlobals.duelRequestTTDB = TimedTaskHeap.TimedTaskHeap()

    if bbConfig.timedTaskCheckingType not in ["fixed", "dynamic"]:
        raise ValueError("bbConfig: Invalid timedTaskCheckingType '" +
                         bbConfig.timedTaskCheckingType + "'")


    bbGlobals.reactionMenusTTDB = TimedTaskHeap.TimedTaskHeap()

    if not os.path.exists(bbConfig.reactionMenusDBPath):
        try:
            f = open(bbConfig.reactionMenusDBPath, 'x')
            f.write("{}")
            f.close()
        except IOError as e:
            bbLogger.log("main","on_ready","IOError creating reactionMenuDB save file: " + e.__class__.__name__, trace=traceback.format_exc())

    bbGlobals.reactionMenusDB = await loadReactionMenusDB(bbConfig.reactionMenusDBPath)


    # TODO: find next closest task with min over heap[0] for all task DBs and delay by that amount
    # newTaskAdded = False
    # nextTask

    # execute regular tasks while the bot is logged in
    while bbGlobals.client.bb_loggedIn:
        if bbConfig.timedTaskCheckingType == "fixed":
            await asyncio.sleep(bbConfig.timedTaskLatenessThresholdSeconds)
        # elif bbConfig.timedTaskCheckingType == "dynamic":

        # await bbGlobals.shopRefreshTT.doExpiryCheck()

        # await bbGlobals.newBountiesTTDB.doTaskChecking()

        await bbGlobals.dbSaveTT.doExpiryCheck()

        # await bbGlobals.duelRequestTTDB.doTaskChecking()

        await bbGlobals.reactionMenusTTDB.doTaskChecking()


@bbGlobals.client.event
async def on_message(message : discord.Message):
    """Called every time a message is sent in a server that the bot has joined
    Currently handles:
    - command calling

    :param discord.Message message: The message that triggered this command on sending
    """
    # ignore messages sent by bots
    if message.author.bot:
        return

    try:
        if "bountybot" in message.content or bbGlobals.client.user in message.mentions:
            await message.add_reaction("👀")
        if "<:tex:723331420919169036>" in message.content:
            await message.add_reaction("<:tex:723331420919169036>")
    except discord.Forbidden:
        pass
    except discord.HTTPException:
        pass

    # For any messages beginning with bbConfig.commandPrefix
    if message.content.startswith(bbConfig.commandPrefix) and len(message.content) > len(bbConfig.commandPrefix):
        # replace special apostraphe characters with the universal '
        msgContent = message.content.replace("‘", "'").replace("’", "'")

        # split the message into command and arguments
        if len(msgContent[len(bbConfig.commandPrefix):]) > 0:
            command = msgContent[len(bbConfig.commandPrefix):].split(" ")[
                0]
            args = msgContent[len(
                bbConfig.commandPrefix) + len(command) + 1:]

        # if no command is given, ignore the message
        else:
            return

        # infer the message author's permissions
        if message.author.id in bbConfig.developers:
            accessLevel = 2
        elif message.author.permissions_in(message.channel).administrator:
            accessLevel = 1
        else:
            accessLevel = 0

        # Chek whether the command was requested in DMs
        isDM = message.channel.type in [
            discord.ChannelType.private, discord.ChannelType.group]

        try:
            # Call the requested command
            commandFound = await bbCommands.call(command, message, args, accessLevel, isDM=isDM)
        except HeirarchicalCommandsDB.IncorrectCommandCallContext:
            await err_nodm(message, "", isDM)
            return
        except Exception as e:
            await message.channel.send(":woozy_face: Uh oh, something went wrong! The error has been logged.\nThis command probably won't work until we've looked into it.")
            bbLogger.log("Main", "on_message", "An unexpected error occured when calling command '" +
                            command + "' with args '" + args + "': " + e.__class__.__name__, trace=traceback.format_exc())
            commandFound = True

        # Command not found, send an error message.
        if not commandFound:
            userTitle = bbConfig.accessLevelTitles[accessLevel]
            await message.channel.send(""":question: Can't do that, """ + userTitle + """. Type `""" + bbConfig.commandPrefix + """help` for a list of commands! **o7**""")


@bbGlobals.client.event
async def on_raw_reaction_add(payload : discord.RawReactionActionEvent):
    """Called every time a reaction is added to a message.
    If the message is a reaction menu, and the reaction is an option for that menu, trigger the menu option's behaviour.

    :param discord.RawReactionActionEvent payload: An event describing the message and the reaction added
    """
    if payload.user_id != bbGlobals.client.user.id:
        emoji = lib.emojis.dumbEmojiFromPartial(payload.emoji)
        if emoji.sendable is None:
            return

        guild = bbGlobals.client.get_guild(payload.guild_id)
        if guild is None:
            message = await bbGlobals.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        else:
            message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if message is None:
            return
        
        if guild is None:
            member = bbGlobals.client.get_user(payload.user_id)
        else:
            member = payload.member
        if member is None:
            return

        if message.id in bbGlobals.reactionMenusDB and \
                bbGlobals.reactionMenusDB[message.id].hasEmojiRegistered(emoji):
            await bbGlobals.reactionMenusDB[message.id].reactionAdded(emoji, member)


@bbGlobals.client.event
async def on_raw_reaction_remove(payload : discord.RawReactionActionEvent):
    """Called every time a reaction is removed from a message.
    If the message is a reaction menu, and the reaction is an option for that menu, trigger the menu option's behaviour.

    :param discord.RawReactionActionEvent payload: An event describing the message and the reaction removed
    """
    if payload.user_id != bbGlobals.client.user.id:
        emoji = lib.emojis.dumbEmojiFromPartial(payload.emoji)
        if emoji.sendable is None:
            return

        guild = bbGlobals.client.get_guild(payload.guild_id)
        if guild is None:
            message = await bbGlobals.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        else:
            message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if message is None:
            return
        
        if guild is None:
            member = bbGlobals.client.get_user(payload.user_id)
        else:
            member = message.guild.get_member(payload.user_id)
        if member is None:
            return

        if message.id in bbGlobals.reactionMenusDB and \
                bbGlobals.reactionMenusDB[message.id].hasEmojiRegistered(emoji):
            await bbGlobals.reactionMenusDB[message.id].reactionRemoved(emoji, member)


@bbGlobals.client.event
async def on_raw_message_delete(payload : discord.RawMessageDeleteEvent):
    """Called every time a message is deleted.
    If the message was a reaction menu, deactivate and unschedule the menu.

    :param discord.RawMessageDeleteEvent payload: An event describing the message deleted.
    """
    if payload.message_id in bbGlobals.reactionMenusDB:
        await bbGlobals.reactionMenusDB[payload.message_id].delete()


@bbGlobals.client.event
async def on_raw_bulk_message_delete(payload : discord.RawBulkMessageDeleteEvent):
    """Called every time a group of messages is deleted.
    If any of the messages were a reaction menus, deactivate and unschedule those menus.

    :param discord.RawBulkMessageDeleteEvent payload: An event describing all messages deleted.
    """
    for msgID in payload.message_ids:
        if msgID in bbGlobals.reactionMenusDB:
            await bbGlobals.reactionMenusDB[msgID].delete()


# Launch the bot!! 🤘🚀
bbGlobals.client.run(bbPRIVATE.botToken)
