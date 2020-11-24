from . import ReactionMenu
from ..bbConfig import bbConfig
from .. import bbGlobals, lib
from discord import Colour, Message, Embed, Member, Role
from datetime import datetime
from ..scheduling import TimedTask
from..bbObjects.battles import DuelRequest


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

        options = {bbConfig.defaultAcceptEmoji: ReactionMenu.NonSaveableReactionMenuOption("Accept", bbConfig.defaultAcceptEmoji, addFunc=self.acceptChallenge),
                    bbConfig.defaultRejectEmoji: ReactionMenu.NonSaveableReactionMenuOption("Reject", bbConfig.defaultRejectEmoji, addFunc=self.rejectChallenge)}

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


async def fromDict(rmDict : dict) -> ReactionDuelChallengeMenu:
    """⚠ ReactionDuelChallengeMenus are not currently saveable. Do not use this method.
    When implemented, this function will construct a new ReactionDuelChallengeMenu from a dictionary-serialized representation - The opposite of ReactionDuelChallengeMenu.toDict.

    :param dict rmDict: A dictionary containg all information needed to construct the required ReactionDuelChallengeMenu
    :raise NotImplementedError: Always.
    """
    raise NotImplementedError("Attempted to call fromDict on a non-saveable reaction menu")
    dcGuild = bbGlobals.client.get_guild(rmDict["guild"])
    msg = await dcGuild.get_channel(rmDict["channel"]).fetch_message(rmDict["msg"])

    reactionRoles = {}
    for reaction in rmDict["options"]:
        reactionRoles[lib.emojis.dumbEmojiFromStr(reaction)] = dcGuild.get_role(rmDict["options"][reaction]["role"])

    timeoutTT = None
    if "timeout" in rmDict:
        expiryTime = datetime.utcfromtimestamp(rmDict["timeout"])
        bbGlobals.reactionMenusTTDB.scheduleTask(TimedTask.TimedTask(expiryTime=expiryTime, expiryFunction=ReactionMenu.removeEmbedAndOptions, expiryFunctionArgs=msg.id))


    return ReactionDuelChallengeMenu(msg, reactionRoles, dcGuild,
                                titleTxt=rmDict["titleTxt"] if "titleTxt" in rmDict else "",
                                desc=rmDict["desc"] if "desc" in rmDict else "",
                                col=Colour.from_rgb(rmDict["col"][0], rmDict["col"][1], rmDict["col"][2]) if "col" in rmDict else Colour.default(),
                                footerTxt=rmDict["footerTxt"] if "footerTxt" in rmDict else "",
                                img=rmDict["img"] if "img" in rmDict else "",
                                thumb=rmDict["thumb"] if "thumb" in rmDict else "",
                                icon=rmDict["icon"] if "icon" in rmDict else "",
                                authorName=rmDict["authorName"] if "authorName" in rmDict else "",
                                timeout=timeoutTT,
                                targetMember=dcGuild.get_member(rmDict["targetMember"]) if "targetMember" in rmDict else None,
                                targetRole=dcGuild.get_role(rmDict["targetRole"]) if "targetRole" in rmDict else None)