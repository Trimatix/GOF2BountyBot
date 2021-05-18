import discord
import traceback
from datetime import datetime

from . import commandsDB as bbCommands
from .. import bbGlobals, lib

from . import util_help


async def dev_cmd_dev_help(message : discord.Message, args : str, isDM : bool):
    """dev command printing help strings for dev commands as defined in bbData

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await util_help.util_autohelp(message, args, isDM, 2)

bbCommands.register("dev-help", dev_cmd_dev_help, 2, signatureStr="**dev-help** *[page number, section or command]*", shortHelp="Display information about developer-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info.", longHelp="Display information about developer-only commands.\nGive a specific command for detailed info about it, or give a page number or give a section name for brief info about a set of commands. These are the currently valid section names:\n- Bounties\n- Miscellaneous\n- Items\n- Channels\n- Skins")



async def dev_cmd_sleep(message : discord.Message, args : str, isDM : bool):
    """developer command saving all data to JSON and then shutting down the bot

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if len(bbGlobals.currentRenders) > 0 and "-f" not in args:
        await message.channel.send(":x: A render is currently in progress!")	
    else:
        await bbGlobals.client.bb_shutdown()
        await message.channel.send("zzzz....")

bbCommands.register("sleep", dev_cmd_sleep, 2, allowDM=True, useDoc=True)


async def dev_cmd_save(message : discord.Message, args : str, isDM : bool):
    """developer command saving all databases to JSON

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    try:
        bbGlobals.client.bb_saveAllDBs()
    except Exception as e:
        print("SAVING ERROR", e.__class__.__name__)
        print(traceback.format_exc())
        await message.channel.send("failed!")
        return
    print(datetime.now().strftime("%H:%M:%S: Data saved manually!"))
    await message.channel.send("saved!")

bbCommands.register("save", dev_cmd_save, 2, allowDM=True, useDoc=True)


async def dev_cmd_reset_has_poll(message : discord.Message, args : str, isDM : bool):
    """developer command resetting the poll ownership of the calling user, or the specified user if one is given.

    :param discord.Message message: the discord message calling the command
    :param str args: string, can be empty or contain a user mention
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).pollOwned = False
        # otherwise get the specified user's discord object and reset their cooldown.
        # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))).pollOwned = False
    await message.channel.send("Done!")

bbCommands.register("reset-has-poll", dev_cmd_reset_has_poll, 2, allowDM=True, useDoc=True)


async def dev_cmd_broadcast(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the playChannel of all guilds that have one

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]

                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        if useAnnounceChannel:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasAnnounceChannel():
                    await guild.getAnnounceChannel().send(msgText, embed=broadcastEmbed)
        else:
            for guild in bbGlobals.guildsDB.guilds.values():
                if guild.hasPlayChannel():
                    await guild.getPlayChannel().send(msgText, embed=broadcastEmbed)

bbCommands.register("broadcast", dev_cmd_broadcast, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_say(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the same channel as the command is called in

    :param discord.Message message: the discord message calling the command
    :param str args: string containing the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if args == "":
        await message.channel.send("provide a message!")
    else:
        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex].replace("{NL}", "\n")
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]
                
                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        await message.channel.send(msgText, embed=broadcastEmbed)

bbCommands.register("say", dev_cmd_say, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_setbalance(message : discord.Message, args : str, isDM : bool):
    """developer command setting the requested user's balance.

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a user mention and an integer number of credits
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    # verify both a user and a balance were given
    if len(argsSplit) < 2:
        await message.channel.send(":x: Please give a user mention followed by the new balance!")
        return
    # verify the requested balance is an integer
    if not lib.stringTyping.isInt(argsSplit[1]):
        await message.channel.send(":x: that's not a number!")
        return
    # verify the requested user
    requestedUser = bbGlobals.client.get_user(
        int(argsSplit[0].lstrip("<@!").rstrip(">")))
    if requestedUser is None:
        await message.channel.send(":x: invalid user!!")
        return
    if not bbGlobals.usersDB.userIDExists(requestedUser.id):
        requestedBBUser = bbGlobals.usersDB.addUser(requestedUser.id)
    else:
        requestedBBUser = bbGlobals.usersDB.getUser(requestedUser.id)
    # update the balance
    requestedBBUser.credits = int(argsSplit[1])
    await message.channel.send("Done!")

bbCommands.register("setbalance", dev_cmd_setbalance, 2, allowDM=True, useDoc=True)


async def dev_cmd_reset_transfer_cool(message : discord.Message, args : str, isDM : bool):
    """developer command resetting a user's home guild transfer cooldown.

    :param discord.Message message: the discord message calling the command
    :param str args: either empty string or string containing a user mention or ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    # reset the calling user's cooldown if no user is specified
    if args == "":
        bbGlobals.usersDB.getUser(
            message.author.id).guildTransferCooldownEnd = datetime.utcnow()
    # otherwise get the specified user's discord object and reset their cooldown.
    # [!] no validation is done.
    else:
        bbGlobals.usersDB.getUser(int(args.lstrip("<@!").rstrip(">"))
                        ).guildTransferCooldownEnd = datetime.utcnow()
    await message.channel.send("Done!")
    

bbCommands.register("reset-transfer-cool", dev_cmd_reset_transfer_cool, 2, allowDM=True, useDoc=True)


async def dev_cmd_sayin(message : discord.Message, args : str, isDM : bool):
    """developer command sending a message to the channel of the specified ID, or to the mentioned user

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a channel ID or user mentioned, followed by a space, followed by the message to broadcast
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) < 2:
        await message.channel.send("provide a channel ID or user mention, then the message!")
    else:
        sendChannel = None
        chanSpecifier = argsSplit[0]
        if lib.stringTyping.isMention(chanSpecifier):
            uID = int(chanSpecifier.lstrip("<@!").rstrip(">"))
            if not (sendChannel := (bbGlobals.client.get_user(uID) or await bbGlobals.client.fetch_user(uID))):
                await message.reply(f"Couldnt find user with ID {uID}")
                return
        elif lib.stringTyping.isInt(chanSpecifier):
            chID = int(chanSpecifier)
            if not (sendChannel := (bbGlobals.client.get_channel(chID) or await bbGlobals.client.fetch_channel(chID))):
                await message.reply(f"Couldnt find channel with ID {chID}")
                return
        else:
            await message.reply("Your first argument doesnt look like a user mention or channel ID. To send to this channel, use `say`.")
            return

        useAnnounceChannel = False
        broadcastEmbed = None
        msg = args
        if args.split(" ")[0].lower() == "announce-channel":
            useAnnounceChannel = True
            msg = args[17:]

        try:
            embedIndex = msg.index("embed=")
        except ValueError:
            embedIndex = -1

        if embedIndex != -1:
            msgText = msg[:embedIndex]
        else:
            msgText = msg

        if embedIndex != -1:
            msg = msg[embedIndex+len("embed="):]
            titleTxt = ""
            desc = ""
            footerTxt = ""
            thumb = ""
            img = ""
            authorName = ""
            icon = ""

            try:
                startIndex = msg.index("titleTxt='")+len("titleTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("titleTxt='")+len("titleTxt='"):].index("'")
                titleTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("desc='")+len("desc=")+1
                endIndex = startIndex + \
                    msg[msg.index("desc='")+len("desc='"):].index("'")
                desc = msg[startIndex:endIndex].replace("{NL}", "\n")
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("footerTxt='")+len("footerTxt=")+1
                endIndex = startIndex + \
                    msg[msg.index("footerTxt='") +
                        len("footerTxt='"):].index("'")
                footerTxt = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("thumb='")+len("thumb=")+1
                endIndex = startIndex + \
                    msg[msg.index("thumb='")+len("thumb='"):].index("'")
                thumb = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("img='")+len("img=")+1
                endIndex = startIndex + \
                    msg[msg.index("img='")+len("img='"):].index("'")
                img = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("authorName='")+len("authorName=")+1
                endIndex = startIndex + \
                    msg[msg.index("authorName='") +
                        len("authorName='"):].index("'")
                authorName = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            try:
                startIndex = msg.index("icon='")+len("icon=")+1
                endIndex = startIndex + \
                    msg[msg.index("icon='")+len("icon='"):].index("'")
                icon = msg[startIndex:endIndex]
                msg = msg[endIndex+2:]
            except ValueError:
                pass

            broadcastEmbed = lib.discordUtil.makeEmbed(titleTxt=titleTxt, desc=desc, footerTxt=footerTxt,
                                       thumb=thumb, img=img, authorName=authorName, icon=icon)

            try:
                msg.index('\n')
                fieldsExist = True
            except ValueError:
                fieldsExist = False
            while fieldsExist:
                nextNL = msg.index('\n')
                try:
                    closingNL = nextNL + msg[nextNL+1:].index('\n')
                except ValueError:
                    fieldsExist = False
                else:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:closingNL+1].replace("{NL}", "\n"), inline=False)
                    msg = msg[closingNL+2:]
                
                if not fieldsExist:
                    broadcastEmbed.add_field(name=msg[:nextNL].replace(
                        "{NL}", "\n"), value=msg[nextNL+1:].replace("{NL}", "\n"), inline=False)

        await sendChannel.send(msgText, embed=broadcastEmbed)

bbCommands.register("sayin", dev_cmd_say, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_delmsg(message : discord.Message, args : str, isDM : bool):
    """developer command deleting the message with the given ID in the channel with the given ID or DMs with the mentioned user

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a channel ID or user mention followed by a message ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) != 2:
        await message.channel.send("provide a channel ID then message ID!")
    else:
        targetChannel = None
        chanSpecifier, msgSpecifier = argsSplit
        if lib.stringTyping.isMention(chanSpecifier):
            uID = int(chanSpecifier.lstrip("<@!").rstrip(">"))
            if not (targetChannel := (bbGlobals.client.get_user(uID) or await bbGlobals.client.fetch_user(uID))):
                await message.reply(f"Couldnt find user with ID {uID}")
                return
        elif lib.stringTyping.isInt(chanSpecifier):
            chID = int(chanSpecifier)
            if not (targetChannel := (bbGlobals.client.get_channel(chID) or await bbGlobals.client.fetch_channel(chID))):
                await message.reply(f"Couldnt find channel with ID {chID}")
                return
        else:
            await message.reply("Your first argument doesnt look like a user mention or channel ID. To send to this channel, use `say`.")
            return
        
        if not lib.stringTyping.isInt(msgSpecifier):
            await message.reply("Your second argument doesnt look like a message ID.")
        else:
            mID = int(msgSpecifier)
            if not (targetMessage := (targetChannel.get_message(mID) or await targetChannel.fetch_message(mID))):
                await message.reply(f"Couldnt find a message with ID {mID} in the {targetChannel.mention} channel")
            else:
                try:
                    await targetMessage.delete()
                except (discord.NotFound, discord.HTTPException, discord.Forbidden) as e:
                    await message.reply(f"Delete failed: {e}")

bbCommands.register("delmsg", dev_cmd_delmsg, 2, forceKeepArgsCasing=False, allowDM=True, useDoc=True)


async def dev_cmd_reacttomsg(message : discord.Message, args : str, isDM : bool):
    """developer command reacting to the message in the given channel (channel ID or user mention) with the given emoji (unicode or ID)

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a channel ID or user mention followed by a message ID followed by a unicode emoji or emoji ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) != 3:
        await message.channel.send("provide a channel ID then message ID then emoji/emoji ID!")
    else:
        targetChannel = None
        chanSpecifier, msgSpecifier, emojiSpecifier = argsSplit
        if lib.stringTyping.isMention(chanSpecifier):
            uID = int(chanSpecifier.lstrip("<@!").rstrip(">"))
            if not (targetChannel := (bbGlobals.client.get_user(uID) or await bbGlobals.client.fetch_user(uID))):
                await message.reply(f"Couldnt find user with ID {uID}")
                return
        elif lib.stringTyping.isInt(chanSpecifier):
            chID = int(chanSpecifier)
            if not (targetChannel := (bbGlobals.client.get_channel(chID) or await bbGlobals.client.fetch_channel(chID))):
                await message.reply(f"Couldnt find channel with ID {chID}")
                return
        else:
            await message.reply("Your first argument doesnt look like a user mention or channel ID. To send to this channel, use `say`.")
            return
        
        if not lib.stringTyping.isInt(msgSpecifier):
            await message.reply("Your second argument doesnt look like a message ID.")
        else:
            mID = int(msgSpecifier)
            if not (targetMessage := (targetChannel.get_message(mID) or await targetChannel.fetch_message(mID))):
                await message.reply(f"Couldnt find a message with ID {mID} in the {targetChannel.mention} channel")
            else:
                try:
                    targetEmoji = lib.emojis.dumbEmojiFromStr(emojiSpecifier)
                except Exception as e:
                    await message.reply(f"Failed to construct emoji from \"{emojiSpecifier}\": {e}")
                else:
                    try:
                        await targetMessage.add_reaction(targetEmoji.sendable)
                    except (discord.NotFound, discord.HTTPException, discord.Forbidden, discord.InvalidArgument) as e:
                        await message.reply(f"React add failed: {e}")

bbCommands.register("reactToMsg", dev_cmd_reacttomsg, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)


async def dev_cmd_removereact(message : discord.Message, args : str, isDM : bool):
    """developer command removing the reaction to the message in the given channel (channel ID or user mention) with the given emoji (unicode or ID)

    :param discord.Message message: the discord message calling the command
    :param str args: string containing a channel ID or user mention followed by a message ID followed by a unicode emoji or emoji ID
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    argsSplit = args.split(" ")
    if len(argsSplit) != 3:
        await message.channel.send("provide a channel ID then message ID then emoji/emoji ID!")
    else:
        targetChannel = None
        chanSpecifier, msgSpecifier, emojiSpecifier = argsSplit
        if lib.stringTyping.isMention(chanSpecifier):
            uID = int(chanSpecifier.lstrip("<@!").rstrip(">"))
            if not (targetChannel := (bbGlobals.client.get_user(uID) or await bbGlobals.client.fetch_user(uID))):
                await message.reply(f"Couldnt find user with ID {uID}")
                return
        elif lib.stringTyping.isInt(chanSpecifier):
            chID = int(chanSpecifier)
            if not (targetChannel := (bbGlobals.client.get_channel(chID) or await bbGlobals.client.fetch_channel(chID))):
                await message.reply(f"Couldnt find channel with ID {chID}")
                return
        else:
            await message.reply("Your first argument doesnt look like a user mention or channel ID. To send to this channel, use `say`.")
            return
        
        if not lib.stringTyping.isInt(msgSpecifier):
            await message.reply("Your second argument doesnt look like a message ID.")
        else:
            mID = int(msgSpecifier)
            if not (targetMessage := (targetChannel.get_message(mID) or await targetChannel.fetch_message(mID))):
                await message.reply(f"Couldnt find a message with ID {mID} in the {targetChannel.mention} channel")
            else:
                try:
                    targetEmoji = lib.emojis.dumbEmojiFromStr(emojiSpecifier)
                except Exception as e:
                    await message.reply(f"Failed to construct emoji from \"{emojiSpecifier}\": {e}")
                else:
                    try:
                        await targetMessage.remove_reaction(targetEmoji.sendable, targetChannel.me)
                    except (discord.NotFound, discord.HTTPException, discord.Forbidden, discord.InvalidArgument) as e:
                        await message.reply(f"React remove failed: {e}")

bbCommands.register("removereact", dev_cmd_removereact, 2, forceKeepArgsCasing=True, allowDM=True, useDoc=True)
