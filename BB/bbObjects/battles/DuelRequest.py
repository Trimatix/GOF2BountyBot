"""
A duel challenge for stakes credits, issued by sourceBBUser to targetBBUser in sourceBBGuild, and expiring with duelTimeoutTask.

@param sourceBBUser -- The bbUser who issued the duel challenge
@param targetBBUser -- The bbUser to accept/reject the challenge
@param stakes -- The amount of credits to move from the winner to the loser
@param duelTimeoutTask -- the TimedTask responsible for expiring this challenge
@param sourceBBGuild -- The bbGuild from which the challenge was issued
"""
class DuelRequest:
    def __init__(self, sourceBBUser, targetBBUser, stakes, duelTimeoutTask, sourceBBGuild):
        self.sourceBBUser = sourceBBUser
        self.targetBBUser = targetBBUser
        self.stakes = stakes
        self.duelTimeoutTask = duelTimeoutTask
        self.sourceBBGuild = sourceBBGuild
