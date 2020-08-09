import inspect
from discord import Embed, Colour, NotFound, HTTPException, Forbidden
from ..bbConfig import bbConfig
from .. import bbGlobals, bbUtil
from abc import ABC, abstractmethod


async def deleteReactionMenu(menuID):
    menu = bbGlobals.reactionMenusDB[menuID]
    await menu.msg.delete()
    del bbGlobals.reactionMenusDB[menu.msg.id]


async def removeEmbedAndOptions(menuID):
    menu = bbGlobals.reactionMenusDB[menuID]
    for react in menu.options:
        await menu.msg.remove_reaction(react.sendable, menu.msg.guild.me)
    await menu.msg.edit(suppress=True)
    del bbGlobals.reactionMenusDB[menu.msg.id]


async def markExpiredMenu(menuID):
    menu = bbGlobals.reactionMenusDB[menuID]
    try:
        await menu.msg.edit(content=bbConfig.expiredMenuMsg)
    except NotFound:
        pass
    except HTTPException:
        pass
    except Forbidden:
        pass
    if menuID in bbGlobals.reactionMenusDB:
        del bbGlobals.reactionMenusDB[menuID]


class ReactionMenuOption:
    def __init__(self, name, emoji, addFunc=None, addArgs=None, removeFunc=None, removeArgs=None):
        self.name = name
        self.emoji = emoji
        
        self.addFunc = addFunc
        self.addArgs = addArgs
        self.addIsCoroutine = addFunc is not None and inspect.iscoroutinefunction(addFunc)
        self.addIncludeUser = addFunc is not None and 'reactingUser' in inspect.signature(addFunc).parameters
        self.addHasArgs = addFunc is not None and len(inspect.signature(addFunc).parameters) != (1 if self.addIncludeUser else 0)

        self.removeFunc = removeFunc
        self.removeArgs = removeArgs
        self.removeIsCoroutine = removeFunc is not None and inspect.iscoroutinefunction(removeFunc)
        self.removeIncludeUser = removeFunc is not None and 'reactingUser' in inspect.signature(addFunc).parameters
        self.removeHasArgs = removeFunc is not None and len(inspect.signature(removeFunc).parameters) != (1 if self.removeIncludeUser else 0)
    

    async def add(self, member):
        if self.addFunc is not None:
            if self.addIncludeUser:
                if self.addHasArgs:
                    return await self.addFunc(self.addArgs, reactingUser=member) if self.addIsCoroutine else self.addFunc(self.addArgs, reactingUser=member)
                return await self.addFunc(reactingUser=member) if self.addIsCoroutine else self.addFunc(reactingUser=member)
            if self.addHasArgs:
                return await self.addFunc(self.addArgs) if self.addIsCoroutine else self.addFunc(self.addArgs)
            return await self.addFunc() if self.addIsCoroutine else self.addFunc()


    async def remove(self, member):
        if self.removeFunc is not None:
            if self.removeIncludeUser:
                if self.removeHasArgs:
                    return await self.removeFunc(self.removeArgs, reactingUser=member) if self.removeIsCoroutine else self.removeFunc(self.removeArgs, reactingUser=member)
                return await self.removeFunc(reactingUser=member) if self.removeIsCoroutine else self.removeFunc(reactingUser=member)
            if self.removeHasArgs:
                return await self.removeFunc(self.removeArgs) if self.removeIsCoroutine else self.removeFunc(self.removeArgs)
            return await self.removeFunc() if self.removeIsCoroutine else self.removeFunc()


    def __hash__(self):
        return hash(repr(self)) 


    @abstractmethod
    def toDict(self):
        return {"name":self.name, "emoji": self.emoji.toDict()}


class NonSaveableReactionMenuOption(ReactionMenuOption):
    def __init__(self, name, emoji, addFunc=None, addArgs=None, removeFunc=None, removeArgs=None):
        super(NonSaveableReactionMenuOption, self).__init__(name, emoji, addFunc=addFunc, addArgs=addArgs, removeFunc=removeFunc, removeArgs=removeArgs)


    def toDict(self):
        return super(NonSaveableReactionMenuOption, self).toDict()

        
class DummyReactionMenuOption(ReactionMenuOption):
    def __init__(self, name, emoji):
        super(DummyReactionMenuOption, self).__init__(name, emoji)


    def toDict(self):
        return super(DummyReactionMenuOption, self).toDict()


class ReactionMenu:
    def __init__(self, msg, options={}, 
                    titleTxt="", desc="", col=None, timeout=None, footerTxt="", img="", thumb="", icon="", authorName="", targetMember=None, targetRole=None):
        if footerTxt == "" and timeout is not None:
            footerTxt = "This menu will expire in " + bbUtil.td_format_noYM(timeout.expiryDelta) + "."
        
        # discord.message
        self.msg = msg
        # Dict of bbUtil.dumbEmoji: ReactionMenuOption
        self.options = options

        self.titleTxt = titleTxt
        self.desc = desc
        self.col = col if col is not None else Colour.default()
        self.footerTxt = footerTxt
        self.img = img
        self.thumb = thumb
        self.icon = icon
        self.authorName = authorName
        self.timeout = timeout
        self.targetMember = targetMember
        self.targetRole = targetRole
        self.saveable = False

    
    def hasEmojiRegistered(self, emoji):
        return emoji in self.options


    async def reactionAdded(self, emoji, member):
        if self.targetMember is not None:
            if member != self.targetMember:
                return
        if self.targetRole is not None:
            if self.targetRole not in member.roles:
                return
                
        return await self.options[emoji].add(member)

    
    async def reactionRemoved(self, emoji, member):
        if self.targetMember is not None:
            if member != self.targetMember:
                return
        if self.targetRole is not None:
            if self.targetRole not in member.roles:
                return
                
        return await self.options[emoji].remove(member)


    def getMenuEmbed(self):
        menuEmbed = Embed(title=self.titleTxt, description=self.desc, colour=self.col)
        if self.footerTxt != "": menuEmbed.set_footer(text=self.footerTxt)
        menuEmbed.set_image(url=self.img)
        if self.thumb != "": menuEmbed.set_thumbnail(url=self.thumb)
        if self.icon != "": menuEmbed.set_author(name=self.authorName, icon_url=self.icon)

        for option in self.options:
            menuEmbed.add_field(name=option.sendable + " : " + self.options[option].name, value="‎", inline=False)

        return menuEmbed
    
    async def updateMessage(self):
        await self.msg.clear_reactions()
        await self.msg.edit(embed=self.getMenuEmbed())
        for option in self.options:
            await self.msg.add_reaction(option.sendable)


    async def delete(self):
        if self.timeout is None:
            await deleteReactionMenu(self.msg.id)
        else:
            await self.timeout.forceExpire()


    def toDict(self):
        optionsDict = {}
        for reaction in self.options:
            optionsDict[reaction.sendable] = self.options[reaction].toDict()

        data = {"channel": self.msg.channel.id, "msg": self.msg.id, "options": optionsDict, "type": self.__class__.__name__}
        
        if self.titleTxt != "":
            data["titleTxt"] = self.titleTxt

        if self.desc != "":
            data["desc"] = self.desc

        if self.col != Colour.default():
            data["col"] = self.col.to_rgb()

        if self.footerTxt != "":
            data["footerTxt"] = self.footerTxt

        if self.img != "":
            data["img"] = self.img

        if self.thumb != "":
            data["thumb"] = self.thumb

        if self.icon != "":
            data["icon"] = self.icon

        if self.authorName != "":
            data["authorName"] = self.authorName

        if self.timeout != None:
            data["timeout"] = self.timeout.expiryTime.timestamp()

        if self.targetMember is not None:
            data["targetMember"] = self.targetMember.id

        if self.targetRole is not None:
            data["targetRole"] = self.targetRole.id
        
        return data

class CancellableReactionMenu(ReactionMenu):
    def __init__(self, msg, options={}, cancelEmoji=bbConfig.defaultCancelEmoji,
                    titleTxt="", desc="", col=Embed.Empty, timeout=None, footerTxt="", img="", thumb="", icon="", authorName="", targetMember=None, targetRole=None):
        self.cancelEmoji = cancelEmoji
        options[cancelEmoji] = NonSaveableReactionMenuOption("cancel", cancelEmoji, self.delete, None)
        super(CancellableReactionMenu, self).__init__(msg, options=options, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout, targetMember=targetMember, targetRole=targetRole)


    def toDict(self):
        baseDict = super(CancellableReactionMenu, self).toDict()
        del baseDict["options"][self.cancelEmoji.sendable]

        return baseDict

