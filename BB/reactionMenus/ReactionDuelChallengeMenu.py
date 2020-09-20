from . import ReactionMenu
from ..bbConfig import bbConfig
from .. import bbGlobals, bbUtil
from discord import Colour, NotFound, HTTPException, Forbidden, Message
from datetime import datetime
from ..scheduling import TimedTask
from..bbObjects.battles import DuelRequest


class ReactionDuelChallengeMenu(ReactionMenu.ReactionMenu):
    """A ReactionMenu allowing the recipient of a duel challenge to accept or reject the challenge through reactions.

    :var duelChallenge: The DuelRequest that this menu controls
    :vartype duelChallenge: DuelRequest
    """
    def __init__(self, msg : Message, duelChallenge : DuelRequest, titleTxt="", desc="", col=None, timeout=None, footerTxt="", img="", thumb="", icon="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/crossed-swords_2694.png", authorName="", targetMember=None, targetRole=None):
        """
        par
        """
        
        # if desc == "":
        #     desc = bbGlobals.client.get_user(duelChallenge.sourceBBUser.id).mention + " challenged " + bbGlobals.client.get_user(duelChallenge.targetBBUser.id).mention + " to a duel!"
        
        if targetMember is None:
            targetMember = msg.guild.get_member(duelChallenge.targetBBUser.id)

        self.duelChallenge = duelChallenge

        options = {bbConfig.defaultAcceptEmoji: ReactionMenu.NonSaveableReactionMenuOption("Accept", bbConfig.defaultAcceptEmoji, addFunc=self.acceptChallenge),
                    bbConfig.defaultRejectEmoji: ReactionMenu.NonSaveableReactionMenuOption("Reject", bbConfig.defaultRejectEmoji, addFunc=self.rejectChallenge)}

        super(ReactionDuelChallengeMenu, self).__init__(msg, options=options, titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt, img=img, thumb=thumb, icon=icon, authorName=authorName, timeout=timeout, targetMember=targetMember, targetRole=targetRole)


    def getMenuEmbed(self):
        baseEmbed = super(ReactionDuelChallengeMenu, self).getMenuEmbed()
        baseEmbed.add_field(name="Stakes:", value=str(self.duelChallenge.stakes) + " Credits")

        return baseEmbed


    async def acceptChallenge(self):
        if self.duelChallenge.sourceBBUser.credits < self.duelChallenge.stakes:
            await self.msg.channel.send(":x: You do not have enough credits to accept this duel request! (" + str(self.duelChallenge.stakes) + ")")
            return
        if self.duelChallenge.targetBBUser.credits < self.duelChallenge.stakes:
            await self.msg.channel.send(":x:" + bbGlobals.client.get_user(self.duelChallenge.sourceBBUser.id).display_name + " does not have enough credits to fight this duel! (" + str(self.duelChallenge.stakes) + ")")
            return
            
        await DuelRequest.fightDuel(bbGlobals.client.get_user(self.duelChallenge.sourceBBUser.id), bbGlobals.client.get_user(self.duelChallenge.targetBBUser.id), self.duelChallenge, self.msg)


    async def rejectChallenge(self):
        await DuelRequest.rejectDuel(self.duelChallenge, self.msg, bbGlobals.client.get_user(self.duelChallenge.sourceBBUser.id), bbGlobals.client.get_user(self.duelChallenge.targetBBUser.id))


    def toDict(self):
        baseDict = super(ReactionDuelChallengeMenu, self).toDict()
        return baseDict


async def fromDict(rmDict):
    dcGuild = bbGlobals.client.get_guild(rmDict["guild"])
    msg = await dcGuild.get_channel(rmDict["channel"]).fetch_message(rmDict["msg"])

    reactionRoles = {}
    for reaction in rmDict["options"]:
        reactionRoles[bbUtil.dumbEmojiFromStr(reaction)] = dcGuild.get_role(rmDict["options"][reaction]["role"])

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