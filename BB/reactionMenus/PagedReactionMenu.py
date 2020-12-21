from ..bbObjects import bbUser
from .import ReactionMenu
from discord import Message, Colour, Member, Role, Embed, Forbidden, HTTPException, NotFound
from .. import lib, bbGlobals
from typing import Dict
from ..scheduling import TimedTask
from ..bbConfig import bbConfig


async def expireHelpMenu(menuID: int):
    """Expire a reaction help menu, and mark it so in the discord message.
    Reset the owning user's helpMenuOwned tracker.
    """
    menu = bbGlobals.reactionMenusDB[menuID]
    menu.owningBBUser.helpMenuOwned = False
    await ReactionMenu.markExpiredMenuAndRemoveOptions(menuID)


async def menuJumpToPage(data : dict):
    await bbGlobals.reactionMenusDB[data["menuID"]].jumpToPage(data["pageNum"])


class PagedReactionMenu(ReactionMenu.ReactionMenu):
    """A reaction menu that, instead of taking a list of options, takes a list of pages of options.
    """
    def __init__(self, msg : Message, pages : Dict[Embed, Dict[lib.emojis.dumbEmoji, ReactionMenu.ReactionMenuOption]] = {}, 
                    timeout : TimedTask.TimedTask = None, targetMember : Member = None, targetRole : Role = None, owningBBUser : bbUser.bbUser = None):
        """
        :param discord.Message msg: the message where this menu is embedded
        :param pages: A dictionary associating embeds with pages, where each page is a dictionary storing all options on that page and their behaviour (Default {})
        :type pages: dict[Embed, dict[lib.emojis.dumbEmoji, ReactionMenuOption]]
        :param TimedTask timeout: The TimedTask responsible for expiring this menu (Default None)
        :param discord.Member targetMember: The only discord.Member that is able to interact with this menu. All other reactions are ignored (Default None)
        :param discord.Role targetRole: In order to interact with this menu, users must possess this role. All other reactions are ignored (Default None)
        :param bbUser owningBBUser: The user who initiated this menu. No built in behaviour. (Default None)
        """

        self.pages = pages
        self.msg = msg
        self.currentPageNum = 0
        self.currentPage = None
        self.currentPageControls = {}
        self.timeout = timeout
        self.targetMember = targetMember
        self.targetRole = targetRole
        self.owningBBUser = owningBBUser

        nextOption = ReactionMenu.NonSaveableReactionMenuOption("Next Page", bbConfig.defaultNextEmoji, self.nextPage, None)
        prevOption = ReactionMenu.NonSaveableReactionMenuOption("Previous Page", bbConfig.defaultPreviousEmoji, self.previousPage, None)
        cancelOption = ReactionMenu.NonSaveableReactionMenuOption("Close Menu", bbConfig.defaultCancelEmoji, self.delete, None)

        self.firstPageControls = {  bbConfig.defaultCancelEmoji:    cancelOption,
                                    bbConfig.defaultNextEmoji:      nextOption}

        self.midPageControls = {    bbConfig.defaultCancelEmoji:    cancelOption,
                                    bbConfig.defaultNextEmoji:      nextOption,
                                    bbConfig.defaultPreviousEmoji:  prevOption}

        self.lastPageControls = {   bbConfig.defaultCancelEmoji:    cancelOption,
                                    bbConfig.defaultPreviousEmoji:  prevOption}

        self.onePageControls = {    bbConfig.defaultCancelEmoji:    cancelOption}

        if len(self.pages) == 1:
            self.currentPageControls = self.onePageControls
        self.updateCurrentPage()


    def getMenuEmbed(self) -> Embed:
        """Generate the discord.Embed representing the reaction menu, and that
        should be embedded into the menu's message.
        This will usually contain a short description of the menu, its options, and its expiry time.

        :return: A discord.Embed representing the menu and its options
        :rtype: discord.Embed 
        """
        return self.currentPage


    def updateCurrentPage(self):
        self.currentPage = list(self.pages.keys())[self.currentPageNum]
        self.options = list(self.pages.values())[self.currentPageNum]

        if len(self.pages) > 1:
            if self.currentPageNum == len(self.pages) - 1:
                self.currentPageControls = self.lastPageControls
            elif self.currentPageNum == 0:
                self.currentPageControls = self.firstPageControls
            else:
                self.currentPageControls = self.midPageControls

        for optionEmoji in self.currentPageControls:
            self.options[optionEmoji] = self.currentPageControls[optionEmoji]


    async def nextPage(self):
        if self.currentPageNum == len(self.pages) - 1:
            raise RuntimeError("Attempted to nextPage while on the last page")
        self.currentPageNum += 1
        self.updateCurrentPage()
        await self.updateMessage(noRefreshOptions=True)
        if self.currentPageNum == len(self.pages) - 1:
            self.msg = await self.msg.channel.fetch_message(self.msg.id)
            await self.msg.remove_reaction(bbConfig.defaultNextEmoji.sendable, bbGlobals.client.user)
        if self.currentPageNum == 1:
            await self.msg.add_reaction(bbConfig.defaultPreviousEmoji.sendable)


    async def previousPage(self):
        if self.currentPageNum == 0:
            raise RuntimeError("Attempted to previousPage while on the first page")
        self.currentPageNum -= 1
        self.updateCurrentPage()
        await self.updateMessage(noRefreshOptions=True)
        if self.currentPageNum == 0:
            self.msg = await self.msg.channel.fetch_message(self.msg.id)
            await self.msg.remove_reaction(bbConfig.defaultPreviousEmoji.sendable, bbGlobals.client.user)
        if self.currentPageNum == len(self.pages) - 2:
            await self.msg.add_reaction(bbConfig.defaultNextEmoji.sendable)

    
    async def jumpToPage(self, pageNum : int):
        if pageNum < 0 or pageNum > len(self.pages) - 1:
            raise IndexError("Page number out of range: " + str(pageNum))
        if pageNum != self.currentPageNum:
            self.currentPageNum = pageNum
            self.updateCurrentPage()
            await self.updateMessage(noRefreshOptions=True)
            if len(self.pages) > 1:
                if self.currentPageNum == 0:
                    self.msg = await self.msg.channel.fetch_message(self.msg.id)
                    await self.msg.remove_reaction(bbConfig.defaultPreviousEmoji.sendable, bbGlobals.client.user)
                if self.currentPageNum != len(self.pages) - 1:
                    await self.msg.add_reaction(bbConfig.defaultNextEmoji.sendable)