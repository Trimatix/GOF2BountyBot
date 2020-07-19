from discord import Embed, utils
from ....bbConfig import bbData, bbConfig
from .... import bbUtil
from .. import bbCriminal

def makeBountyEmbed(bounty):
    embed = Embed(title=bounty.criminal.name, colour=bbData.factionColours[bounty.faction] if bounty.faction in bbData.factionColours else bbData.factionColours["neutral"])
    embed.set_footer(text=bounty.faction.title())
    embed.set_thumbnail(url=bounty.criminal.icon)
    embed.add_field(name="**Reward:**", value=bbUtil.commaSplitNum(str(bounty.reward)) + " Credits")
    routeStr = ""
    for system in bounty.route:
        if bounty.systemChecked(system):
            routeStr += "~~" + system + "~~"
            if 0 < bounty.route.index(bounty.answer) - bounty.route.index(system) < bbConfig.closeBountyThreshold:
                routeStr += "\*"
        else:
            routeStr += system
        routeStr += ", "
    # embed.add_field(value="`Stars indicate systems where the criminal has recently been spotted.`", name="`Crossed-through systems have already been checked.`")
    embed.add_field(name="**Difficulty:**", value=str(bounty.criminal.techLevel))
    # embed = bbUtil.fillLoadoutEmbed(bounty.criminal.activeShip, embed, shipEmoji=True)
    embed.add_field(name="**See the culprit's loadout with:**", value="`" + bbConfig.commandPrefix + "loadout criminal " + bounty.criminal.name + "`")
    embed.add_field(name="**Route:**", value=routeStr[:-2], inline=False)
    embed.add_field(name="-", value="> ~~Already checked systems~~\n> Criminal spotted here recently**\***")
    return embed


class BountyBoardChannel:
    def __init__(self, channelIDToBeLoaded, messagesToBeLoaded):
        self.messagesToBeLoaded = messagesToBeLoaded
        self.channelIDToBeLoaded = channelIDToBeLoaded

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
            msg = await self.channel.fetch_message(id)
            criminal = bbCriminal.fromDict(self.messagesToBeLoaded[id])
            self.bountyMessages[criminal.faction][criminal] = msg
        # del self.messagesToBeLoaded
        # del self.channelIDToBeLoaded


    def hasMessageForBounty(self, bounty):
        return bounty.criminal in self.bountyMessages[bounty.criminal.faction]


    def getMessageForBounty(self, bounty):
        return self.bountyMessages[bounty.criminal.faction][bounty.criminal]


    def isEmpty(self):
        return not bool(self.bountyMessages)

    
    async def addBounty(self, bounty, message):
        # if len(self.bountyMessages) == 0:
        #     await self.noBountiesMessage.delete()

        if self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-ADD-BNTY_EXSTS: Attempted to add a bounty to a bountyboardchannel, but the bounty is already listed")
        self.bountyMessages[bounty.criminal.faction][bounty.criminal] = message
    

    async def removeBounty(self, bounty):
        # if len(self.bountyMessages) == 1:
        #     self.noBountiesMessage = await self.channel.send(bbConfig.bbcNoBountiesMsg)

        if not self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-REM-BNTY_NOT_EXST: Attempted to remove a bounty from a bountyboardchannel, but the bounty is not listed")
        del self.bountyMessages[bounty.criminal.faction][bounty.criminal]


    async def updateBountyMessage(self, bounty):
        if not self.hasMessageForBounty(bounty):
            raise KeyError("BNTY_BRD_CH-UPD-BNTY_NOT_EXST: Attempted to add a bounty to a bountyboardchannel, but the bounty is already listed")
        content = self.bountyMessages[bounty.criminal.faction][bounty.criminal].content
        await self.bountyMessages[bounty.criminal.faction][bounty.criminal].edit(content=content, embed=makeBountyEmbed(bounty))


    def toDict(self):
        # dict of message id: criminal dict
        listings = {}
        for fac in self.bountyMessages:
            for crim in self.bountyMessages[fac]:
                listings[self.bountyMessages[fac][crim].id] = crim.toDict()
        return {"channel":self.channel.id, "listings":listings}


def fromDict(BBCDict):
    if BBCDict is None:
        return None
    return BountyBoardChannel(BBCDict["channel"], BBCDict["listings"])
