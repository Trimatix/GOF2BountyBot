import inspect
from discord import Embed, Colour, NotFound, HTTPException, Forbidden, Member, Message
from ..bbConfig import bbConfig
from .. import bbGlobals, bbUtil
from abc import ABC, abstractmethod


async def deleteReactionMenu(menuID : int):
    """Delete the currently active reaction menu and its message entirely, with the given message ID

    :param int menuID: The ID of the menu, corresponding with the discord ID of the menu's message
    """
    menu = bbGlobals.reactionMenusDB[menuID]
    await menu.msg.delete()
    del bbGlobals.reactionMenusDB[menu.msg.id]


async def removeEmbedAndOptions(menuID : int):
    """Delete the currently active menu with the given ID, removing its embed and option reactions, but
    leaving the corresponding message intact.

    :param int menuID: The ID of the menu, corresponding with the discord ID of the menu's message
    """
    if menuID in bbGlobals.reactionMenusDB:
        menu = bbGlobals.reactionMenusDB[menuID]
        await menu.msg.edit(suppress=True)
        
        for react in menu.options:
            await menu.msg.remove_reaction(react.sendable, menu.msg.guild.me)
        
        del bbGlobals.reactionMenusDB[menu.msg.id]


async def markExpiredMenu(menuID : int):
    """Replace the message content of the given menu with bbConfig.expiredMenuMsg, and remove 
    the menu from the active reaction menus DB.

    :param int menuID: The ID of the menu, corresponding with the discord ID of the menu's message
    """
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
    """An abstract class representing an option in a reaction menu.
    Reaction menu options must have a name and emoji. They may optionally have a function to call when added,
    a function to call when removed, and arguments for each.
    If either function has a keyword argument called 'reactingUser', the user who added/removed the reaction will
    be passed there.

    :var name: The name of this option, as displayed in the menu embed.
    :vartype name: str
    :var emoji: The emoji that a user must react with to trigger this option
    :vartype emoji: bbUtil.dumbEmoji
    :var addFunc: The function to call when this option is added by a user
    :vartype addFunc: function
    :var removeFunc: The function to call when this option is removed by a user
    :vartype removeFunc: function
    :var addArgs: The arguments to pass to addFunc. No type checking is done on this parameter, but a dict is recommended as a close alternative to keyword args.
    :var removeArgs: The arguments to pass to removeFunc.
    :var addIsCoroutine: Whether or not addFuc is a coroutine and must be awaited
    :vartype addIsCoroutine: bool
    :var addIncludeUser: Whether or not to give the reacting user as a keyword argument to addFunc
    :vartype addIncludeUser: bool
    :var addHasArgs: Whether addFunc takes arguments, and addArgs should be attempt to be passed
    :vartype addHasArgs: bool
    :var removeIsCoroutine: Whether or not removeFuc is a coroutine and must be awaited
    :vartype removeIsCoroutine: bool
    :var removeIncludeUser: Whether or not to give the reacting user as a keyword argument to removeFunc
    :vartype removeIncludeUser: bool
    :var removeHasArgs: Whether removeFunc takes arguments, and removeArgs should be attempt to be passed
    :vartype removeHasArgs: bool
    """

    def __init__(self, name : str, emoji : bbUtil.dumbEmoji, addFunc=None, addArgs=None, removeFunc=None, removeArgs=None):
        """
        :param str name: The name of this option, as displayed in the menu embed.
        :param bbUtil.dumbEmoji emoji: The emoji that a user must react with to trigger this option
        :param function addFunc: The function to call when this option is added by a user
        :param function removeFunc: The function to call when this option is removed by a user
        :param addArgs: The arguments to pass to addFunc. No type checking is done on this parameter, but a dict is recommended as a close alternative to keyword args.
        :param removeArgs: The arguments to pass to removeFunc.
        """
        
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
    

    async def add(self, member : Member):
        """
        This method is called by the owning reaction menu whenever this option is added by any user
        that matches the menu's restrictions, if any apply (e.g targetMember, targetRole)
        """
        if self.addFunc is not None:
            if self.addIncludeUser:
                if self.addHasArgs:
                    return await self.addFunc(self.addArgs, reactingUser=member) if self.addIsCoroutine else self.addFunc(self.addArgs, reactingUser=member)
                return await self.addFunc(reactingUser=member) if self.addIsCoroutine else self.addFunc(reactingUser=member)
            if self.addHasArgs:
                return await self.addFunc(self.addArgs) if self.addIsCoroutine else self.addFunc(self.addArgs)
            return await self.addFunc() if self.addIsCoroutine else self.addFunc()


    async def remove(self, member : Member):
        if self.removeFunc is not None:
            if self.removeIncludeUser:
                if self.removeHasArgs:
                    return await self.removeFunc(self.removeArgs, reactingUser=member) if self.removeIsCoroutine else self.removeFunc(self.removeArgs, reactingUser=member)
                return await self.removeFunc(reactingUser=member) if self.removeIsCoroutine else self.removeFunc(reactingUser=member)
            if self.removeHasArgs:
                return await self.removeFunc(self.removeArgs) if self.removeIsCoroutine else self.removeFunc(self.removeArgs)
            return await self.removeFunc() if self.removeIsCoroutine else self.removeFunc()


    def __hash__(self) -> int:
        return hash(repr(self)) 


    @abstractmethod
    def toDict(self) -> dict:
        return {"name":self.name, "emoji": self.emoji.toDict()}


class NonSaveableReactionMenuOption(ReactionMenuOption):
    def __init__(self, name : str, emoji : bbUtil.dumbEmoji, addFunc=None, addArgs=None, removeFunc=None, removeArgs=None):
        super(NonSaveableReactionMenuOption, self).__init__(name, emoji, addFunc=addFunc, addArgs=addArgs, removeFunc=removeFunc, removeArgs=removeArgs)


    def toDict(self) -> dict:
        return super(NonSaveableReactionMenuOption, self).toDict()

        
class DummyReactionMenuOption(ReactionMenuOption):
    def __init__(self, name : str, emoji : bbUtil.dumbEmoji):
        super(DummyReactionMenuOption, self).__init__(name, emoji)


    def toDict(self) -> dict:
        return super(DummyReactionMenuOption, self).toDict()


class ReactionMenu:
    def __init__(self, msg : Message, options={}, 
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

    
    def hasEmojiRegistered(self, emoji : bbUtil.dumbEmoji) -> bool:
        return emoji in self.options


    async def reactionAdded(self, emoji : bbUtil.dumbEmoji, member : Member):
        if self.targetMember is not None:
            if member != self.targetMember:
                return
        if self.targetRole is not None:
            if self.targetRole not in member.roles:
                return
                
        return await self.options[emoji].add(member)

    
    async def reactionRemoved(self, emoji : bbUtil.dumbEmoji, member : Member):
        if self.targetMember is not None:
            if member != self.targetMember:
                return
        if self.targetRole is not None:
            if self.targetRole not in member.roles:
                return
                
        return await self.options[emoji].remove(member)


    def getMenuEmbed(self) -> Embed:
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


    def toDict(self) -> dict:
        optionsDict = {}
        for reaction in self.options:
            optionsDict[reaction.sendable] = self.options[reaction].toDict()

        data = {"channel": self.msg.channel.id, "msg": self.msg.id, "options": optionsDict, "type": self.__class__.__name__, "guild": self.msg.channel.guild.id}
        
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
    def __init__(self, msg : Message, options={}, cancelEmoji=bbConfig.defaultCancelEmoji,
                    titleTxt="", desc="", col=Embed.Empty, timeout=None, footerTxt="", img="", thumb="", icon="", authorName="", targetMember=None, targetRole=None):
        self.cancelEmoji = cancelEmoji
        options[cancelEmoji] = NonSaveableReactionMenuOption("cancel", cancelEmoji, self.delete, None)
        super(CancellableReactionMenu, self).__init__(msg, options=options, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout, targetMember=targetMember, targetRole=targetRole)


    def toDict(self) -> dict:
        baseDict = super(CancellableReactionMenu, self).toDict()
        del baseDict["options"][self.cancelEmoji.sendable]

        return baseDict

