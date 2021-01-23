# CURRENTLY UNUSED FILE
from __future__ import annotations
from ....bbDatabases import bountyDB
from ....baseClasses import serializable


class BountyBoard(serializable.Serializable):
    """A single message that acts as a duplicate of the output of $bounties, except it is continuously updated with new and completed bounties.

    :var msgID: The id of the message to continuously update
    :vartype msgID: int
    :var bountiesDB: The database to pull active bounties from
    :vartype bountiesDB: bountyDB
    """

    def __init__(self, msgID : int, bountiesDB : bountyDB.bbBounty):
        """
        :param int msgID: The id of the message to continuously update
        :param bountyDB bountiesDB: The database to pull active bounties from
        """
        self.msgID = msgID
        self.bountiesDB = bountiesDB

    
    def toDict(self, **kwargs) -> dict:
        """Serialise this BountyBoard into dictionary format for saving to file

        :return: A dictionary containing all data needed to reload this BountyBoard
        :rtype: dict
        """
        return {"msgID": self.msgID}


    @classmethod
    def fromDict(bountyBoardDict : dict, **kwargs) -> BountyBoard:
        """Factory function constructing a BountyBoard from the data contained in the given dictionary. The opposite of BountyBoard.toDict

        :param dict bountyBoardDict: A dict containing all information needed to reconstruct the desired BountyBoard
        :return: The new BountyBoard object
        :rtype: BountyBoard
        """
        return BountyBoard(bountyBoardDict["msgID"])