# CURRENTLY UNUSED FILE

class BountyBoard:
    msgID = -1
    bountiesDB = None

    def __init__(self, msgID, bountiesDB):
        self.msgID = msgID
        self.bountiesDB = bountiesDB

    

    def toDict(self):
        return {"msgID": self.msgID}


def fromDict(bountyBoardDict):
    return BountyBoard(bountyBoardDict["msgID"])