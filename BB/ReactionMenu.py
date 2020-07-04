import inspect


class ReactionMenuOption:
    def __init__(self, emoji, func, args):
        self.emoji = emoji
        self.func = func
        self.args = args
        self.isCoroutine = inspect.iscoroutinefunction(func)
    
    async def call(self):
        return await self.func(self.args) if self.isCoroutine else self.func(self.args)


class ReactionMenu:
    def __init__(self, msgID, options={}):
        msgID = msgID
        # Dict of discord.emoji: ReactionMenuOption
        options = options

    
    def emojiRegistered(self, emoji):
        return emoji in self.options


    async def reactionAdded(self, emoji):
        return await self.options[emoji].call()