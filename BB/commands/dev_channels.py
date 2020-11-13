import discord

from . import commandsDB as bbCommands
from .. import bbGlobals


async def dev_cmd_has_announce(message : discord.Message, args : str, isDM : bool):
    """developer command printing whether or not the current guild has an announcements channel set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    await message.channel.send(":x: Unknown guild!" if guild is None else guild.hasAnnounceChannel())

bbCommands.register("has-announce", dev_cmd_has_announce, 2, allowDM=False)


async def dev_cmd_get_announce(message : discord.Message, args : str, isDM : bool):
    """developer command printing the current guild's announcements channel if one is set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("<#" + str(bbGlobals.guildsDB.getGuild(message.guild.id).getAnnounceChannel().id) + ">")

bbCommands.register("get-announce", dev_cmd_get_announce, 2, allowDM=False)


async def dev_cmd_has_play(message : discord.Message, args : str, isDM : bool):
    """developer command printing whether or not the current guild has a play channel set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    guild = bbGlobals.guildsDB.getGuild(message.guild.id)
    await message.channel.send(":x: Unknown guild!" if guild is None else guild.hasPlayChannel())

bbCommands.register("has-play", dev_cmd_has_play, 2, allowDM=False)


async def dev_cmd_get_play(message : discord.Message, args : str, isDM : bool):
    """developer command printing the current guild's play channel if one is set

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: Whether or not the command is being called from a DM channel
    """
    await message.channel.send("<#" + str(bbGlobals.guildsDB.getGuild(message.guild.id).getPlayChannel().id) + ">")

bbCommands.register("get-play", dev_cmd_get_play, 2, allowDM=False)