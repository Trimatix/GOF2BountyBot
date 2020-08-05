import discord
from discord import Embed, HTTPException, Forbidden, NotFound
from ....bbConfig import bbData, bbConfig
from .... import bbUtil
from .. import bbCriminal
from ....logging import bbLogger

def makeBountyEmbed(bounty):
    embed = Embed(title=bounty.criminal.name, colour=bbData.factionColours[bounty.faction] if bounty.faction in bbData.factionColours else bbData.factionColours["neutral"])
    embed.set_footer(text=bounty.faction.title())
    embed.set_thumbnail(url=bounty.criminal.icon)
    embed.add_field(name="**Reward:**", value=bbUtil.commaSplitNum(str(bounty.reward)) + " Credits")
    routeStr = ""
    for system in bounty.route:
        if bounty.systemChecked(system):
            routeStr += "~~"
            if 0 < bounty.route.index(bounty.answer) - bounty.route.index(system) < bbConfig.closeBountyThreshold:
                routeStr += "**" + system + "**"
            else:
                routeStr += system
            routeStr += "~~"
        else:
            routeStr += system
        routeStr += ", "
    
    embed.add_field(name="**Difficulty:**", value=str(bounty.criminal.techLevel))
    embed.add_field(name="**See the culprit's loadout with:**", value="`" + bbConfig.commandPrefix + "loadout criminal " + bounty.criminal.name + "`")
    embed.add_field(name="**Route:**", value=routeStr[:-2], inline=False)
    embed.add_field(name="-", value="> ~~Already checked systems~~\n> **Criminal spotted here recently**")
    return embed

noBountiesEmbed = Embed(description='> Please check back later, or use the `$notify bounties` command to be notified when they spawn!', colour=discord.Colour.dark_orange())
noBountiesEmbed.set_author(name='No Bounties Available', icon_url='https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/stopwatch_23f1.png')

class BountyBoardChannel:
    def __init__(self, channelIDToBeLoaded, messagesToBeLoaded, noBountiesMsg):
        self.messagesToBeLoaded = messagesToBeLoaded
        self.channelIDToBeLoaded = channelIDToBeLoaded
        self.noBountiesMsgToBeLoaded = noBountiesMsg

        # dict of "faction": {criminal: int message ID}
        self.bountyMessages = {}
        # discord message object to be filled when no bounties exist
        self.noBountiesMessage = None
        # discord channel object
        self.channel = None


    async def init(self, client, factions):
        for fac in factions:
            self.bountyMessages[fac] = {}

        self.channel = client.get_channel(self.channelIDToBeLoaded)

        for id in self.messagesToBeLoaded:
            criminal = bbCriminal.fromDict(self.messagesToBeLoaded[id])

            try:
                msg = await self.channel.fetch_message(id)
                self.bountyMessages[criminal.faction][criminal] = msg
            except HTTPException:
                bbLogger.log("BBC", "init", "HTTPException thrown when fetching listing for criminal: " + criminal.name, category='bountyBoards', eventType="LISTING_LOAD-HTTPERR")
            except Forbidden:
                bbLogger.log("BBC", "init", "Forbidden exception thrown when fetching listing for criminal: " + criminal.name, category='bountyBoards', eventType="LISTING_LOAD-FORBIDDENERR")
            except NotFound:
                bbLogger.log("BBC", "init", "Listing message for criminal no longer exists: " + criminal.name, category='bountyBoards', eventType="LISTING_LOAD-NOT_FOUND")

        if self.noBountiesMsgToBeLoaded == -1:
            self.noBountiesMessage = None
            
        else:
            try:
                self.noBountiesMessage = await self.channel.fetch_message(self.noBountiesMsgToBeLoaded)
            except HTTPException:
                bbLogger.log("BBC", "init", "HTTPException thrown when fetching no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-HTTPERR")
            except Forbidden:
                bbLogger.log("BBC", "init", "Forbidden exception thrown when fetching no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-FORBIDDENERR")
            except NotFound:
                bbLogger.log("BBC", "init", "No bounties message no longer exists", category='bountyBoards', eventType="NOBTYMSG_LOAD-NOT_FOUND")
                self.noBountiesMessage = None
        # del self.messagesToBeLoaded
        # del self.channelIDToBeLoaded
        # del self.noBountiesMsgToBeLoaded


    def hasMessageForBounty(self, bounty):
        return bounty.criminal in self.bountyMessages[bounty.criminal.faction]


    def getMessageForBounty(self, bounty):
        return self.bountyMessages[bounty.criminal.faction][bounty.criminal]


    def isEmpty(self):
        for faction in self.bountyMessages:
            if bool(self.bountyMessages[faction]):
                return False
        return True

    
    async def addBounty(self, bounty, message):
        removeMsg = False
        if self.isEmpty():
            removeMsg = True

        if self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-ADD-BNTY_EXSTS: Attempted to add a bounty to a bountyboardchannel, but the bounty is already listed")
            bbLogger.log("BBC", "addBty", "Attempted to add a bounty to a bountyboardchannel, but the bounty is already listed: " + bounty.criminal.name, category='bountyBoards', eventType="LISTING_ADD-EXSTS")
        self.bountyMessages[bounty.criminal.faction][bounty.criminal] = message

        if removeMsg:
            try:
                await self.noBountiesMessage.delete()
            except HTTPException:
                print("addBounty HTTPException")
            except Forbidden:
                print("addBounty Forbidden")
            except AttributeError:
                print("addBounty no message")
    

    async def removeBounty(self, bounty):
        if not self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-REM-BNTY_NOT_EXST: Attempted to remove a bounty from a bountyboardchannel, but the bounty is not listed")
            bbLogger.log("BBC", "remBty", "Attempted to remove a bounty from a bountyboardchannel, but the bounty is not listed: " + bounty.criminal.name, category='bountyBoards', eventType="LISTING_REM-NO_EXST")
        del self.bountyMessages[bounty.criminal.faction][bounty.criminal]

        if self.isEmpty():
            try:
                # self.noBountiesMessage = await self.channel.send(bbConfig.bbcNoBountiesMsg)
                self.noBountiesMessage = await self.channel.send(embed=noBountiesEmbed)

            except HTTPException:
                bbLogger.log("BBC", "remBty", "HTTPException thrown when sending no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-HTTPERR")
                self.noBountiesMessage = None
            except Forbidden:
                bbLogger.log("BBC", "remBty", "Forbidden exception thrown when sending no bounties message", category='bountyBoards', eventType="NOBTYMSG_LOAD-FORBIDDENERR")
                self.noBountiesMessage = None


    async def updateBountyMessage(self, bounty):
        if not self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-UPD-BNTY_NOT_EXST: Attempted to update a BBC message for a criminal that is not listed")
            bbLogger.log("BBC", "remBty", "Attempted to update a BBC message for a criminal that is not listed: " + bounty.criminal.name, category='bountyBoards', eventType="LISTING_UPD-NO_EXST")

        content = self.bountyMessages[bounty.criminal.faction][bounty.criminal].content
        try:
            await self.bountyMessages[bounty.criminal.faction][bounty.criminal].edit(content=content, embed=makeBountyEmbed(bounty))
        except HTTPException:
            bbLogger.log("BBC", "updBtyMsg", "HTTPException thrown when updating bounty listing for criminal: " + bounty.criminal.name, category='bountyBoards', eventType="UPD_LSTING-HTTPERR")
        except Forbidden:
            bbLogger.log("BBC", "updBtyMsg", "Forbidden exception thrown when updating bounty listing for criminal: " + bounty.criminal.name, category='bountyBoards', eventType="UPD_LSTING-FORBIDDENERR")
        except NotFound:
            bbLogger.log("BBC", "updBtyMsg", "Bounty listing message no longer exists, BBC entry removed: " + bounty.criminal.name, category='bountyBoards', eventType="UPD_LSTING-NOT_FOUND")
            await self.removeBounty(bounty)


    def toDict(self):
        # dict of message id: criminal dict
        listings = {}
        for fac in self.bountyMessages:
            for crim in self.bountyMessages[fac]:
                listings[self.bountyMessages[fac][crim].id] = crim.toDict()
        return {"channel":self.channel.id, "listings":listings, "noBountiesMsg": self.noBountiesMessage.id if self.noBountiesMessage is not None else -1}


def fromDict(BBCDict):
    if BBCDict is None:
        return None
    return BountyBoardChannel(BBCDict["channel"], BBCDict["listings"], BBCDict["noBountiesMsg"] if "noBountiesMsg" in BBCDict else -1)
