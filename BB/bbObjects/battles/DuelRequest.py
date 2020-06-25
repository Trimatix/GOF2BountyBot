class DuelRequest:
    sourceBBUser = None
    targetBBUser = None
    stakes = 0
    duelTimeoutTask = None
    sourceBBGuild = None

    def __init__(self, sourceBBUser, targetBBUser, stakes, duelTimeoutTask, sourceBBGuild):
        self.sourceBBUser = sourceBBUser
        self.targetBBUser = targetBBUser
        self.stakes = stakes
        self.duelTimeoutTask = duelTimeoutTask
        self.sourceBBGuild = sourceBBGuild
