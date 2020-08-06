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
    def __init__(self, msg, options={}, 
                    titleTxt="", desc="", col=Embed.Empty, footerTxt="", img="", thumb="", icon="", authorName=""):
        # discord.message
        self.msg = msg
        # Dict of discord.emoji: ReactionMenuOption
        self.options = options

        self.titleTxt = titleTxt
        self.desc = desc
        self.col = col if col is not None else Embed.Empty
        self.footerTxt = footerTxt
        self.img = img
        self.thumb = thumb
        self.icon = icon
        self.authorName = authorName


    
    def hasEmojiRegistered(self, emoji):
        return emoji in self.options


    async def reactionAdded(self, emoji):
        return await self.options[emoji].call()


    async def getMenuEmbed(self):
        menuEmbed = Embed(title=self.titleTxt, description=self.desc, colour=self.col)
        if self.footerTxt != "": menuEmbed.set_footer(text=self.footerTxt)
        menuEmbed.set_image(url=self.img)
        if self.thumb != "": menuEmbed.set_thumbnail(url=self.thumb)
        if self.icon != "": menuEmbed.set_author(name=self.authorName, icon_url=self.icon)

        for option in self.options:
            menuEmbed.add_field(name=option + " : " + self.options[option].name, value="‎", inline=False)

        return menuEmbed
    
    async def updateMessage(self):
        await self.msg.clear_reactions()
        await self.msg.edit(embed=await self.getMenuEmbed())
        for option in self.options:
            await self.msg.add_reaction(option) 
            