from . import commandsDB
import discord

async def test(message : discord.Message, args : str, isDM : bool):
    """Send an error message when a command is requested that cannot function outside of a guild

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: ignored
    """
    await message.channel.send("success!")

commandsDB.register("test", test, 0, allowDM=True)