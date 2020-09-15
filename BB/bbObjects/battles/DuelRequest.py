from ... import bbUtil, bbGlobals
from ...bbConfig import bbConfig
from discord import Embed, User, Message
from .. import bbUser
from ...scheduling import TimedTask
from .. import bbGuild


def makeDuelStatsEmbed(duelResults : dict, targetUser : bbUser.bbUser, sourceUser : bbUser.bbUser) -> Embed:
    """Build a discord.Embed displaying the statistics of a completed duel.

    :param dict duelResults: A dictionary describing the results of the duel TODO: This is to be changed to a data class, or a ShipFight
    :param bbUser targetUser: The bbUser that the duel challenged was directed at
    :param bbUser sourceUser: The bbUser that issued the challenge
    :return: A discord.Embed displaying the information described in duelResults
    :rtype: discord.Embed
    """
    statsEmbed = Embed()
    statsEmbed.set_author(name="Duel Stats")

    statsEmbed.add_field(name="DPS (" + str(bbConfig.duelVariancePercent * 100) + "% RNG)", value=sourceUser.mention + ": " + str(round(
        duelResults["ship1"]["DPS"]["varied"], 2)) + "\n" + targetUser.mention + ": " + str(round(duelResults["ship2"]["DPS"]["varied"], 2)))
    statsEmbed.add_field(name="Health (" + str(bbConfig.duelVariancePercent * 100) + "% RNG)", value=sourceUser.mention + ": " + str(round(
        duelResults["ship1"]["health"]["varied"])) + "\n" + targetUser.mention + ": " + str(round(duelResults["ship2"]["health"]["varied"], 2)))
    statsEmbed.add_field(name="Time To Kill", value=sourceUser.mention + ": " + (str(round(duelResults["ship1"]["TTK"], 2)) if duelResults["ship1"]["TTK"] != -1 else "inf.") + "s\n" + targetUser.mention + ": " + (
        str(round(duelResults["ship2"]["TTK"], 2)) if duelResults["ship2"]["TTK"] != -1 else "inf.") + "s")

    return statsEmbed


class DuelRequest:
    """A duel challenge for stakes credits, issued by sourceBBUser to targetBBUser in sourceBBGuild, and expiring with duelTimeoutTask.

    :var sourceBBUser: The bbUser that issued this challenge
    :vartype sourceBBUser: bbUser
    :var targetBBUser: The bbUser that this challenge was targetted towards
    :vartype targetBBUser: bbUser
    :var stakes: The amount of credits to award the winner of the duel, and take from the loser
    :vartype stakes: int
    :var duelTimeoutTask: The TimedTask responsible for expiring this duel challenge
    :vartype duelTimeoutTask: TimedTask
    :var sourceBBGuild: The bbGuild in which this challenge was issued
    :vartype sourceBBGuild: bbGuild
    :var menus: A list of ReactionDuelChallengeMenu, each of which may trigger, or be removed by, the expiry or completion of this duel request
    :vartype menus: ReactionDuelChallengeMenu
    """
    def __init__(self, sourceBBUser : bbUser.bbUser, targetBBUser : bbUser.bbUser, stakes : int, duelTimeoutTask : TimedTask.TimedTask, sourceBBGuild : bbGuild.bbGuild):
        """
        :param bbUser sourceBBUser: -- The bbUser who issued the duel challenge
        :param bbUser targetBBUser: -- The bbUser to accept/reject the challenge
        :param int stakes: -- The amount of credits to move from the winner to the loser
        :param TimedTask duelTimeoutTask: -- the TimedTask responsible for expiring this challenge
        :param bbGuild sourceBBGuild: -- The bbGuild from which the challenge was issued
        """
        self.sourceBBUser = sourceBBUser
        self.targetBBUser = targetBBUser
        self.stakes = stakes
        self.duelTimeoutTask = duelTimeoutTask
        self.sourceBBGuild = sourceBBGuild
        self.menus = []


# ⚠⚠⚠ THIS FUNCTION IS MARKED FOR CHANGE
async def fightDuel(sourceUser : User, targetUser : User, duelReq : DuelRequest, acceptMsg : Message) -> dict:
    """Simulate a duel between two users.
    Returns a dictionary containing statistics about the duel, as well as references to the winning and losing bbUsers. 

    :param bbUser sourceUser: The bbUser that issued this challenge 
    :param bbUser targetUser: The bbUser that this challenge was targetted towards 
    :param DuelRequest duelReq: The duel request that this duel simulation satisfies
    :param discord.message acceptMsg: The message tha triggered this duel simulation
    :return: A dictionary containing statistics about the duel, as well as references to the winning and losing bbUsers
    :rtype: dict
    """
    for menu in duelReq.menus:
        await menu.delete()

    sourceBBUser = duelReq.targetBBUser
    targetBBUser = duelReq.sourceBBUser

    # fight = ShipFight.ShipFight(sourceBBUser.activeShip, targetBBUser.activeShip)
    # duelResults = fight.fightShips(bbConfig.duelVariancePercent)
    duelResults = bbUtil.fightShips(
        sourceBBUser.activeShip, targetBBUser.activeShip, bbConfig.duelVariancePercent)
    winningShip = duelResults["winningShip"]

    if winningShip is sourceBBUser.activeShip:
        winningBBUser = sourceBBUser
        losingBBUser = targetBBUser
    elif winningShip is targetBBUser.activeShip:
        winningBBUser = targetBBUser
        losingBBUser = sourceBBUser
    else:
        winningBBUser = None
        losingBBUser = None

    # battleMsg =

    # winningBBUser = sourceBBUser if winningShip is sourceBBUser.activeShip else (targetBBUser if winningShip is targetBBUser.activeShip else None)
    # losingBBUser = None if winningBBUser is None else (sourceBBUser if winningBBUser is targetBBUser else targetBBUser)

    if winningBBUser is None:
        await acceptMsg.channel.send(":crossed_swords: **Stalemate!** " + str(targetUser) + " and " + sourceUser.mention + " drew in a duel!")
        if acceptMsg.guild.get_member(targetUser.id) is None:
            targetDCGuild = bbUtil.findBBUserDCGuild(targetBBUser)
            if targetDCGuild is not None:
                targetBBGuild = bbGlobals.guildsDB.getGuild(targetDCGuild.id)
                if targetBBGuild.hasPlayChannel():
                    await bbGlobals.client.get_channel(targetBBGuild.getPlayChannelId()).send(":crossed_swords: **Stalemate!** " + targetDCGuild.get_member(targetUser.id).mention + " and " + str(sourceUser) + " drew in a duel!")
        else:
            await acceptMsg.channel.send(":crossed_swords: **Stalemate!** " + targetUser.mention + " and " + sourceUser.mention + " drew in a duel!")
    else:
        winningBBUser.duelWins += 1
        losingBBUser.duelLosses += 1
        winningBBUser.duelCreditsWins += duelReq.stakes
        losingBBUser.duelCreditsLosses += duelReq.stakes

        winningBBUser.credits += duelReq.stakes
        losingBBUser.credits -= duelReq.stakes
        creditsMsg = "The stakes were **" + \
            str(duelReq.stakes) + "** credit" + \
            ("s" if duelReq.stakes != 1 else "") + ":"

        # Only display the new player balances if the duel stakes are greater than zero.
        if duelReq.stakes > 0:
            creditsMsg += ".\n**" + bbGlobals.client.get_user(winningBBUser.id).name + "** now has **" + str(winningBBUser.credits) + " credits**.\n**" + \
                bbGlobals.client.get_user(losingBBUser.id).name + "** now has **" + \
                str(losingBBUser.credits) + " credits**."

        # statsMsg = "**" + sourceUser.name + "** had " + (str(duelResults["ship1"]["DPS"]["varied"]) if duelResults["ship1"]["DPS"]["varied"] != -1 else "inf.") + " DPS and " + (str(duelResults["ship1"]["health"]["varied"]) if duelResults["ship1"]["health"]["varied"] != -1 else "inf.") + " health." \
        #             + "**" + targetUser.name + "** had " + (str(duelResults["ship2"]["DPS"]["varied"]) if duelResults["ship2"]["DPS"]["varied"] != -1 else "inf.") + " DPS and " + (str(duelResults["ship2"]["health"]["varied"]) if duelResults["ship2"]["health"]["varied"] != -1 else "inf.") + " health." \
        #             + "**" + sourceUser.name + "** had " + (str(duelResults["ship1"]["TTK"]) if duelResults["ship1"]["TTK"] != -1 else "inf.") + "s time to kill." \
        #             + "**" + targetUser.name + "** had " + (str(duelResults["ship2"]["TTK"]) if duelResults["ship2"]["TTK"] != -1 else "inf.") + "s time to kill."
        
        statsEmbed = makeDuelStatsEmbed(duelResults, sourceUser, targetUser)

        if acceptMsg.guild.get_member(winningBBUser.id) is None:
            await acceptMsg.channel.send(":crossed_swords: **Fight!** " + str(bbGlobals.client.get_user(winningBBUser.id)) + " beat " + bbGlobals.client.get_user(losingBBUser.id).mention + " in a duel!\n" + creditsMsg, embed=statsEmbed)
            winnerDCGuild = bbUtil.findBBUserDCGuild(winningBBUser)
            if winnerDCGuild is not None:
                winnerBBGuild = bbGlobals.guildsDB.getGuild(winnerDCGuild.id)
                if winnerBBGuild.hasPlayChannel():
                    await bbGlobals.client.get_channel(winnerBBGuild.getPlayChannelId()).send(":crossed_swords: **Fight!** " + winnerDCGuild.get_member(winningBBUser.id).mention + " beat " + str(bbGlobals.client.get_user(losingBBUser.id)) + " in a duel!\n" + creditsMsg, embed=statsEmbed)
        else:
            if acceptMsg.guild.get_member(losingBBUser.id) is None:
                await acceptMsg.channel.send(":crossed_swords: **Fight!** " + bbGlobals.client.get_user(winningBBUser.id).mention + " beat " + str(bbGlobals.client.get_user(losingBBUser.id)) + " in a duel!\n" + creditsMsg, embed=statsEmbed)
                loserDCGuild = bbUtil.findBBUserDCGuild(losingBBUser)
                if loserDCGuild is not None:
                    loserBBGuild = bbGlobals.guildsDB.getGuild(loserDCGuild.id)
                    if loserBBGuild.hasPlayChannel():
                        await bbGlobals.client.get_channel(loserBBGuild.getPlayChannelId()).send(":crossed_swords: **Fight!** " + str(bbGlobals.client.get_user(winningBBUser.id)) + " beat " + loserDCGuild.get_member(losingBBUser.id).mention + " in a duel!\n" + creditsMsg, embed=statsEmbed)
            else:
                await acceptMsg.channel.send(":crossed_swords: **Fight!** " + bbGlobals.client.get_user(winningBBUser.id).mention + " beat " + bbGlobals.client.get_user(losingBBUser.id).mention + " in a duel!\n" + creditsMsg, embed=statsEmbed)

    await targetBBUser.duelRequests[sourceBBUser].duelTimeoutTask.forceExpire(callExpiryFunc=False)
    targetBBUser.removeDuelChallengeObj(duelReq)
    # logStr = ""
    # for s in duelResults["battleLog"]:
    #     logStr += s.replace("{PILOT1NAME}",sourceUser.name).replace("{PILOT2NAME}",targetUser.name) + "\n"
    # await acceptMsg.channel.send(logStr)


# ⚠⚠⚠ THIS FUNCTION IS MARKED FOR CHANGE
async def rejectDuel(duelReq : DuelRequest, rejectMsg : Message, challenger : User, recipient : User):
    """
    Reject a duel request, including expiring the DuelReq object and its TimedTask, announcing the request cancellation to both participants, and expiring all related ReactionDuelChallengeMenus.

    :param DuelRequest duelReq: The duel request associated with this duel
    :param discord.message rejectMsg: The message that triggered the rejection of this duel challenge
    :param discord.User challenger: The user or member that issued this challenge 
    :param discord.User recipient: The user or member that this challenge was targetted towards 
    """
    for menu in duelReq.menus:
        await menu.delete()

    await duelReq.duelTimeoutTask.forceExpire(callExpiryFunc=False)
    duelReq.sourceBBUser.removeDuelChallengeTarget(duelReq.targetBBUser)

    await rejectMsg.channel.send(":white_check_mark: You have rejected **" + str(challenger) + "**'s duel challenge.")
    if rejectMsg.guild.get_member(duelReq.sourceBBUser.id) is None:
        targetDCGuild = bbUtil.findBBUserDCGuild(duelReq.sourceBBUser.id)
        if targetDCGuild is not None:
            targetBBGuild = bbGlobals.guildsDB.getGuild(targetDCGuild.id)
            if targetBBGuild.hasPlayChannel():
                await bbGlobals.client.get_channel(targetBBGuild.getPlayChannelId()).send(":-1: <@" + str(duelReq.sourceBBUser.id) + ">, **" + str(recipient) + "** has rejected your duel request!")