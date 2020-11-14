from discord import Message


async def err_tempDisabled(message : Message, args : str, isDM : bool):
    """Send an error message when a bounties command is requested - all bounty and shop related behaviour is currently disabled.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: ignored
    """
    await message.channel.send(":x: All bounty/shop behaviour is currently disabled while I work on new features \:)")


async def err_tempPerfDisabled(message : Message, args : str, isDM : bool):
    """Send an error message when a command is requested that is disabled for perfornance reasons.

    :param discord.Message message: the discord message calling the command
    :param str args: ignored
    :param bool isDM: ignored
    """
    await message.channel.send(":x: This command has been temporarily disabled as it requires too much processing power. It may return in the future once hosting hardware has been upgraded! \:)")