from .. import bbUtil
from abc import ABC, abstractmethod
from .mlCommandParams import *


# class StringTerminator:



class mlCommandParamType:
    def __init__(self, descriptor):
        self.descriptor = descriptor


class mlIntParamType(mlCommandParamType):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class mlBoolParamType(mlCommandParamType):
    def __init__(self, descriptor):
        super().__init__(descriptor)
    

class mlStringParamType(mlCommandParamType):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class mlUserRefParamType(mlCommandParamType):
    def __init__(self, descriptor):
        super().__init__(descriptor)


# class mlGuildRefParamType

# class mlChannelRefParamType

# class mlRoleRefParamType

# class mlUserAlertRefParamType

# class mlDateTimeParamType

# class mlTimeDeltaParamType

# class mlPageNumParamType(mlIntParamType)

# class mlURLParamType(mlStringParamType)



# class bbItemDictParamType
# class bbItemNameParamType
# class bbItemTypeParamType
# class bbSystemParamType
# class bbRouteParamType
# class bbDuelActionParamType(mlStringParamType)