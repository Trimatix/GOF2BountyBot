# CURRENTLY UNUSED FILE
from ....bbDatabases import bbBountyDB
from ....baseClasses import bbSerializable


class BountyBoard(bbSerializable.bbSerializable):
    """A single message that acts as a duplicate of the output of $bounties, except it is continuously updated with new and completed bounties.

    :var msgID: The id of the message to continuously update
    :vartype msgID: int
    :var bountiesDB: The database to pull active bounties from
    :vartype bountiesDB: bbBountyDB
    """

    def __init__(self, msgID : int, bountiesDB : bbBountyDB.bbBounty):
        """
        :param int msgID: The id of the message to continuously update
        :param bbBountyDB bountiesDB: The database to pull active bounties from
        """
        self.msgID = msgID
        self.bountiesDB = bountiesDB

    
    def toDict(self) -> dict:
        """Serialise this BountyBoard into dictionary format for saving to file

        :return: A dictionary containing all data needed to reload this BountyBoard
        :rtype: dict
        """
        return {"msgID": self.msgID}


def fromDict(bountyBoardDict : dict) -> BountyBoard:
    """Factory function constructing a BountyBoard from the data contained in the given dictionary. The opposite of BountyBoard.toDict

    :param dict bountyBoardDict: A dict containing all information needed to reconstruct the desired BountyBoard
    :return: The new BountyBoard object
    :rtype: BountyBoard
    """
    return BountyBoard(bountyBoardDict["msgID"])