import discord

from . import commandsDB as bbCommands
from .. import bbGlobals
from ..bbConfig import bbConfig, bbData

from . import util_tempdisabled


async def admin_cmd_set_announce_channel(message : discord.Message, args : str, isDM : bool):
    """admin command for setting the current guild's announcements channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if args == "off":
        if requestedBBGuild.hasAnnounceChannel():
            requestedBBGuild.removeAnnounceChannel()
            await message.channel.send(":ballot_box_with_check: Announcements channel removed!")
        else:
            await message.channel.send(":x: This server has no announce channel set!")
    elif args != "":
        await message.channel.send(":x: Invalid arguments! Can only be `off` to disable this server's announce channel, or no args to use this channel as the announce channel.")
    else:
        requestedBBGuild.setAnnounceChannel(message.channel)
        await message.channel.send(":ballot_box_with_check: Announcements channel set!")

bbCommands.register("set-announce-channel", admin_cmd_set_announce_channel, 1)


async def admin_cmd_set_bounty_board_channel(message : discord.Message, args : str, isDM : bool):
    """
    admin command for setting the current guild's bounty board channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if guild.hasBountyBoardChannel:
        await message.channel.send(":x: This server already has a bounty board channel! Use `" + bbConfig.commandPrefix + "remove-bounty-board-channel` to remove it.")
        return
    await guild.addBountyBoardChannel(message.channel, bbGlobals.client, bbData.bountyFactions)
    await message.channel.send(":ballot_box_with_check: Bounty board channel set!")

# bbCommands.register("set-bounty-board-channel", admin_cmd_set_bounty_board_channel, 1)
bbCommands.register("set-bounty-board-channel", util_tempdisabled.err_tempDisabled, 1)


async def admin_cmd_remove_bounty_board_channel(message : discord.Message, args : str, isDM : bool):
    """admin command for removing the current guild's bounty board channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if guild.hasBountyBoardChannel:
        guild.removeBountyBoardChannel()
        await message.channel.send(":ballot_box_with_check: Bounty board channel removed!")
    else:
        await message.channel.send(":x: This is not a bounty board channel!")

bbCommands.register("remove-bounty-board-channel", admin_cmd_remove_bounty_board_channel, 1)


async def admin_cmd_set_play_channel(message : discord.Message, args : str, isDM : bool):
    """admin command for setting the current guild's play channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if args == "off":
        if requestedBBGuild.hasPlayChannel():
            requestedBBGuild.removePlayChannel()
            await message.channel.send(":ballot_box_with_check: Bounty play channel removed!")
        else:
            await message.channel.send(":x: This server has no play channel set!")
    elif args != "":
        await message.channel.send(":x: Invalid arguments! Can only be `off` to disable this server's play channel, or no args to use this channel as the play channel.")
    else:
        requestedBBGuild.setPlayChannel(message.channel)
        await message.channel.send(":ballot_box_with_check: Bounty play channel set!")

bbCommands.register("set-play-channel", admin_cmd_set_play_channel, 1)