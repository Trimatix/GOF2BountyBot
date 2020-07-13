import inspect
from discord import Embed


class ReactionMenuOption:
    def __init__(self, emoji, func, args, name):
        self.emoji = emoji
        self.func = func
        self.args = args
        self.isCoroutine = inspect.iscoroutinefunction(func)
        self.name = name
    
    async def call(self):
        return await self.func(self.args) if self.isCoroutine else self.func(self.args)


class ReactionMenu:
    def __init__(self, msg, options={}):
        # discord.message
        self.msg = msg
        # Dict of discord.emoji: ReactionMenuOption
        self.options = options

    
    def emojiRegistered(self, emoji):
        return emoji in self.options


    async def reactionAdded(self, emoji):
        return await self.options[emoji].call()


    def getMenuEmbed(self):
        menuEmbed = Embed()

    
    def updateMessage(self):
        msg.edit(embed=Embed())