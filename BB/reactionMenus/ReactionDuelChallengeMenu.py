from __future__ import annotations
from . import ReactionMenu
from ..bbConfig import bbConfig
from .. import bbGlobals, lib
from discord import Colour, Message, Embed, Member, Role
from datetime import datetime
from ..scheduling import TimedTask
from..gameObjects.battles import DuelRequest


class ReactionDuelChallengeMenu(ReactionMenu.ReactionMenu):
    """A ReactionMenu allowing the recipient of a duel challenge to accept or reject the challenge through reactions.
    TODO: Make this an inline reaction menu (base class in another branch currently)

    :var duelChallenge: The DuelRequest that this menu controls
    :vartype duelChallenge: DuelRequest
    """
    def __init__(self, msg : Message, duelChallenge : DuelRequest, titleTxt : str = "", desc : str = "",
            col : Colour = None, timeout : TimedTask.TimedTask = None,
            footerTxt : str = "", img : str = "", thumb : str = "",
            icon : str = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/crossed-swords_2694.png",
            authorName : str = "", targetMember : Member = None, targetRole : Role = None):
        """
        :param discord.Message msg: The discord message where this menu should be embedded
        :param DuelRequest duelChallenge: The DuelRequest that this menu controls
        :param str titleTxt: The content of the embed title (Default "")
        :param str desc: The content of the embed description; appears at the top below the title (Default "")
        :param discord.Colour col: The colour of the embed's side strip (Default None)
        :param TimedTask timeout: The TimedTask responsible for expiring this menu (Default None)
        :param str footerTxt: Secondary description appearing in darker font at the bottom of the embed (Default "")
        :param str img: URL to a large icon appearing as the content of the embed, left aligned like a field (Default "")
        :param str thumb: URL to a larger image appearing to the right of the title (Default "")
        :param str authorName: Secondary, smaller title for the embed (Default "")
        :param str icon: URL to a smaller image to the left of authorName. AuthorName is required for this to be displayed. (Default "")
        :param discord.Member targetMember: The only discord.Member that is able to interact with this menu. All other reactions are ignored (Default None)
        :param discord.Role targetRole: In order to interact with this menu, users must possess this role. All other reactions are ignored (Default None)
        """
        
        # if desc == "":
        #     desc = bbGlobals.client.get_user(duelChallenge.sourceBBUser.id).mention + " challenged " + bbGlobals.client.get_user(duelChallenge.targetBBUser.id).mention + " to a duel!"
        
        if targetMember is None:
            targetMember = msg.guild.get_member(duelChallenge.targetBBUser.id)

        self.duelChallenge = duelChallenge

        options = {bbConfig.emojis.accept: ReactionMenu.NonSaveableReactionMenuOption("Accept", bbConfig.emojis.accept, addFunc=self.acceptChallenge),
                    bbConfig.emojis.reject: ReactionMenu.NonSaveableReactionMenuOption("Reject", bbConfig.emojis.reject, addFunc=self.rejectChallenge)}

        super(ReactionDuelChallengeMenu, self).__init__(msg, options=options, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout, targetMember=targetMember, targetRole=targetRole)


    def getMenuEmbed(self) -> Embed:
        """Generate this menu's Embed, containing all required information, instructions, restrictions, and options.

        :return: The embed to display in this menu's message
        :rtype: discord.Embed
        """
        baseEmbed = super(ReactionDuelChallengeMenu, self).getMenuEmbed()
        baseEmbed.add_field(name="Stakes:", value=str(self.duelChallenge.stakes) + " Credits")

        return baseEmbed


    async def acceptChallenge(self):
        """Accept a duel challenge on behalf of a user.
        This method is called when the challenge recipient adds the 'accept' reaction to this menu.
        """
        if self.duelChallenge.sourceBBUser.credits < self.duelChallenge.stakes:
            await self.msg.channel.send(":x: You do not have enough credits to accept this duel request! (" + str(self.duelChallenge.stakes) + ")")
            return
        if self.duelChallenge.targetBBUser.credits < self.duelChallenge.stakes:
            await self.msg.channel.send(":x:" + bbGlobals.client.get_user(self.duelChallenge.sourceBBUser.id).display_name + " does not have enough credits to fight this duel! (" + str(self.duelChallenge.stakes) + ")")
            return
            
        await DuelRequest.fightDuel(bbGlobals.client.get_user(self.duelChallenge.sourceBBUser.id), bbGlobals.client.get_user(self.duelChallenge.targetBBUser.id), self.duelChallenge, self.msg)


    async def rejectChallenge(self):
        """Reject a duel challenge on behalf of a user.
        This method is called when the challenge recipient adds the 'reject' reaction to this menu.
        """
        await DuelRequest.rejectDuel(self.duelChallenge, self.msg, bbGlobals.client.get_user(self.duelChallenge.sourceBBUser.id), bbGlobals.client.get_user(self.duelChallenge.targetBBUser.id))


    def toDict(self, **kwargs) -> dict:
        """⚠ ReactionDuelChallengeMenus are not currently saveable. Do not use this method.
        Dummy method, once implemented this method will serialize this reactionMenu to dictionary format.

        :return: A dummy dictionary containing basic information about the menu, but not all information needed to reconstruct the menu.
        :rtype: dict
        :raise NotImplementedError: Always.
        """
        raise NotImplementedError("Attempted to call toDict on a non-saveable reaction menu")
        baseDict = super(ReactionDuelChallengeMenu, self).toDict(**kwargs)
        return baseDict

    
    @classmethod
    def fromDict(cls, data: dict, **kwargs) -> ReactionDuelChallengeMenu:
        raise NotImplementedError("Attempted to call fromDict on a non-saveable reaction menu")
