from .. import bbUtil
from abc import ABC, abstractclassmethod, abstractmethod


# class StringTerminator:



class mlCommandParam:
    descriptor = ""

    @classmethod
    @abstractclassmethod
    def fromStr(cls, paramStr, **kwargs):
        pass


class mlIntParam(mlCommandParam):
    descriptor = ""
    def __init__(self, intParam):
        self.intParam = intParam

    @classmethod
    def fromStr(cls, paramStr, **kwargs):
        if bbUtil.isInt(paramStr):
            return mlIntParam(int(paramStr))
        raise TypeError("Given a non int-castable string: " + paramStr)


class mlBoolParam(mlCommandParam):
    descriptor = ""
    trueAliases = ["true", "on", "yes", "enable", "enabled"]
    falseAliases = ["false", "off", "no", "disable", "disabled"]

    def __init__(self, boolParam):
        self.boolParam = boolParam

    @classmethod
    def fromStr(cls, paramStr, **kwargs):
        paramStr = paramStr.lower().strip()
        if paramStr in cls.trueAliases:
            return mlBoolParam(True)
        elif paramStr in cls.falseAliases:
            return mlBoolParam(False)
        raise TypeError("Given a non bool-castable string: " + paramStr)


class mlStringParam(mlCommandParam):
    descriptor = ""
    def __init__(self, strParam):
        self.strParam = strParam

    @classmethod
    def fromStr(cls, paramStr, **kwargs):
        return mlStringParam(paramStr)


class mlUserRefParam(mlCommandParam):
    descriptor = ""
    def __init__(self, userObj, isMember=False):
        self.userObj = userObj

    @classmethod
    def fromStr(cls, paramStr, **kwargs):
        if "dcGuild" in kwargs:
            return mlUserRefParam(bbUtil.getMemberFromRef, isMember=True)
        raise KeyError("dcGuild is a required kwarg for mlUserRefParam.fromStr")


# class mlGuildRefParam

# class mlChannelRefParam

# class mlRoleRefParam

# class mlUserAlertRefParam

# class mlDateTimeParam

# class mlTimeDeltaParam

# class mlPageNumParam(mlIntParam)

# class mlURLParam(mlStringParam)



# class bbItemDictParam
# class bbItemNameParam
# class bbItemTypeParam
# class bbSystemParam
# class bbRouteParam
# class bbDuelActionParam(mlStringParam)