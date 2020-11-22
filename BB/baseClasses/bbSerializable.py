from abc import ABC, abstractmethod, abstractclassmethod
from __future__ import annotations


class bbSerializable(ABC):

    @abstractmethod
    def toDict(self, saveType : bool = False) -> dict:
        """Serialize this object into dictionary format, to be recreated completely.

        :param bool saveType: When true, include the string name of the object type in the output. (Default False)
        :return: A dictionary containing all information needed to recreate this object
        :rtype: dict
        """
        return {"type": type(self).__name__} if saveType else {}


    @abstractclassmethod
    def fromDict(cls, data : dict) -> bbSerializable:
        """Recreate a dictionary-serialized bbSerializable object 
        
        :param dict data: A dictionary containing all information needed to recreate the serialized object
        :return: A new object as specified by the attributes in data
        :rtype: bbSerializable
        """
        pass