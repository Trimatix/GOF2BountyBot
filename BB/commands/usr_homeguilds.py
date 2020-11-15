import discord
import asyncio
from datetime import datetime

from . import commandsDB as bbCommands
from .. import bbGlobals, lib
from ..bbConfig import bbConfig


bbCommands.addHelpSection(0, "home servers")


async def cmd_transfer(message : discord.Message, args : str, isDM : bool):
    """Transfer the calling user's home guild to the guild where the message was sent.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBUser = bbGlobals.usersDB.getOrAddID(message.author.id)
    if message.guild.id == requestedBBUser.homeGuildID:
        await message.channel.send(":x: This is already your home server!")
    elif not requestedBBUser.canTransferGuild():
        await message.channel.send(":x: This command is still on cooldown. (" + lib.timeUtil.td_format_noYM(requestedBBUser.guildTransferCooldownEnd - datetime.utcnow()) + " left)")
    else:
        confirmEmbed = lib.discordUtil.makeEmbed(desc="This command's cooldown is " + lib.timeUtil.td_format_noYM(lib.timeUtil.timeDeltaFromDict(bbConfig.homeGuildTransferCooldown)) + ".", footerTxt="This menu will expire in " + str(bbConfig.homeGuildTransferConfirmTimeoutSeconds) + " seconds.")
        confirmEmbed.add_field(name=bbConfig.defaultAcceptEmoji.sendable + " : Confirm transfer", value="‎", inline=False)
        confirmEmbed.add_field(name=bbConfig.defaultRejectEmoji.sendable + " : Cancel transfer", value="‎", inline=False)
        confirmMsg = await message.channel.send("Move your home server to '" + message.guild.name + "'?\n", embed=confirmEmbed)

        for optionReact in [bbConfig.defaultAcceptEmoji, bbConfig.defaultRejectEmoji]:
            await confirmMsg.add_reaction(optionReact.sendable)

        def homeGuildTransferConfirmCheck(reactPL):
            return reactPL.message_id == confirmMsg.id and reactPL.user_id == message.author.id and lib.emojis.dumbEmojiFromPartial(reactPL.emoji) in [bbConfig.defaultAcceptEmoji, bbConfig.defaultRejectEmoji]

        try:
            reactPL = await bbGlobals.client.wait_for("raw_reaction_add", check=homeGuildTransferConfirmCheck, timeout=bbConfig.homeGuildTransferConfirmTimeoutSeconds)
            confirmEmbed.set_footer(text="This menu has now expired.")
            await confirmMsg.edit(embed=confirmEmbed)
        except asyncio.TimeoutError:
            await confirmMsg.edit(content="This menu has now expired. Please try the command again.")
        else:
            react = lib.emojis.dumbEmojiFromPartial(reactPL.emoji)
            if react == bbConfig.defaultAcceptEmoji:
                await requestedBBUser.transferGuild(message.guild)
                await message.channel.send(":airplane_arriving: You transferred your home server to " + message.guild.name + "!")
            else:
                await message.channel.send("🛑 Home guild transfer cancelled.")

bbCommands.register("transfer", cmd_transfer, 0, allowDM=False, helpSection="home servers", signatureStr="**transfer**", shortHelp="Change your home server. This command has a long cooldown!", longHelp="Transfer your home server to the one where you sent this command. You will be asked for confirmation first, since this command has a long cooldown!")


async def cmd_home(message : discord.Message, args : str, isDM : bool):
    """Display the name of the calling user's home guild, if they have one.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    if bbGlobals.usersDB.userIDExists(message.author.id):
        requestedBBUser = bbGlobals.usersDB.getUser(message.author.id)
        if message.guild is not None and message.guild.id == requestedBBUser.homeGuildID:
            await message.channel.send("🌍 This is your home server.")
            return
        elif requestedBBUser.hasHomeGuild() and bbGlobals.client.get_guild(requestedBBUser.homeGuildID) is not None:
            await message.channel.send("🪐 Your home server is '" + bbGlobals.client.get_guild(requestedBBUser.homeGuildID).name + "'.")
            return
    await message.channel.send("🌑 Your home server has not yet been set.\nSet your home server by using the shop or bounty board, or with the `" + bbConfig.commandPrefix + "transfer` command.")

bbCommands.register("home", cmd_home, 0, allowDM=True, helpSection="home servers", signatureStr="**home**", shortHelp="Get the name of your home server, if one is set.", longHelp="Get the name of your home server, if one is set. This is the the only server where you may use certain commands, such as buying items from the shop, or fighting bounties.")