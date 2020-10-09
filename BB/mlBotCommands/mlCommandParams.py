from abc import abstractmethod
from .. import bbUtil

class mlCommandParam():
    @abstractmethod
    def fromStr(self, paramStr, **kwargs):
        pass
    

class mlIntParam(mlCommandParam):
    def fromStr(self, paramStr, **kwargs):
        if bbUtil.isInt(paramStr):
            return mlIntParam(int(paramStr))
        raise TypeError("Given a non int-castable string: " + paramStr)
    

class mlBoolParam(mlCommandParam):
    trueAliases = ["true", "on", "yes", "enable", "enabled"]
    falseAliases = ["false", "off", "no", "disable", "disabled"]

    def fromStr(self, paramStr, **kwargs):
        paramStr = paramStr.lower().strip()
        if paramStr in self.trueAliases:
            return mlBoolParam(True)
        elif paramStr in self.falseAliases:
            return mlBoolParam(False)
        raise TypeError("Given a non bool-castable string: " + paramStr)
    

class testParamInst:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "<" + __class__.__name__ + " - '" + self.value + "'>"


class mlStringParam(mlCommandParam):
    def __init__(self, optional, startTerminator, endTernminator):
        self.optional = optional
        self.startTerminator = startTerminator
        self.endTerminator = endTernminator

    def fromStr(self, paramStr, **kwargs):
        return testParamInst(paramStr)
    

class mlUserRefParam(mlCommandParam):
    def fromStr(self, paramStr, **kwargs):
        if "dcGuild" in kwargs:
            return mlUserRefParam(bbUtil.getMemberFromRef, isMember=True)
        raise KeyError("dcGuild is a required kwarg for mlUserRefParamType.fromStr")
    

class mlGuildRefParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class mlChannelRefParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class mlRoleRefParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class mlUserAlertRefParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class mlDateTimeParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class mlTimeDeltaParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class mlPageNumParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class mlURLParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class bbItemDictParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class bbItemNameParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class bbItemTypeParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class bbSystemParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class bbRouteParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
    

class bbDuelActionParam(mlCommandParam):
    def fromStr(self, strParam, **kwargs):
        self.param = strParam
