import discord

from . import commandsDB as bbCommands
from .. import bbGlobals
from ..bbConfig import bbConfig, bbData

bbCommands.addHelpSection(1, "channels")
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

bbCommands.register("set-announce-channel", admin_cmd_set_announce_channel, 1, allowDM=False, helpSection="channels", signatureStr="**set-announce-channel** *[off]*", longHelp="Set the channel where BountyBot will send announcements (e.g new bounties)\n> Use `$COMMANDPREFIX$set-announce-channel off` to disable announcements.")


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

bbCommands.register("set-play-channel", admin_cmd_set_play_channel, 1, allowDM=False, helpSection="channels", signatureStr="**set-play-channel** *[off]*", longHelp="Set the channel where BountyBot will send info about completed bounties\n> Use `$COMMANDPREFIX$set-play-channel off` to disable completed bounty announcements.")


async def admin_cmd_set_renders_channel(message : discord.Message, args : str, isDM : bool):
    """admin command for setting the current guild's autoskin renders channel

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    requestedBBGuild = bbGlobals.guildsDB.getGuild(message.guild.id)
    if args == "off":
        if requestedBBGuild.hasRendersChannel():
            requestedBBGuild.removeRendersChannel()
            await message.reply(":ballot_box_with_check: Renders channel removed!",
                                mention_author=False)
        else:
            await message.reply(":x: This server has no renders channel set!",
                                mention_author=False)
    elif args != "":
        await message.reply(":x: Invalid arguments! Can only be `off` to disable this server's renders channel, " \
                                    + "or no args to use this channel as the renders channel.",
                            mention_author=False)
    else:
        requestedBBGuild.setRendersChannel(message.channel)
        await message.reply(":ballot_box_with_check: Renders channel set!",
                            mention_author=False)


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


# bbCommands.register("set-bounty-board-channel", admin_cmd_set_bounty_board_channel, 1, allowDM=False, helpSection="channels", signatureStr="**set-bounty-board-channel**", longHelp="Send from within a channel to set that channel as a *bountyboard*.\nBountyBoard channels show *all* information about active bounties, continuously update their listings (e.g cross through checked systems), and only show *active* bounties (listings for located bounties are removed).")
bbCommands.register("set-bounty-board-channel", util_tempdisabled.err_tempDisabled, 1, allowDM=False, helpSection="channels", signatureStr="**set-bounty-board-channel**", longHelp="Send from within a channel to set that channel as a *bountyboard*.\nBountyBoard channels show *all* information about active bounties, continuously update their listings (e.g cross through checked systems), and only show *active* bounties (listings for located bounties are removed).")


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

bbCommands.register("remove-bounty-board-channel", admin_cmd_remove_bounty_board_channel, 1, allowDM=False, helpSection="channels", signatureStr="**remove-bounty-board-channel**", shortHelp="Send from any channel to remove the server's bountyboard channel, if one is set.")