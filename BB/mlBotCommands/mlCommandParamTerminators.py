from abc import abstractmethod

class mlCommandParamTerminator:
    @abstractmethod
    def matches(self, strParam):
        pass

    @abstractmethod
    def matchStart(self, strParam):
        pass

    @abstractmethod
    def matchEnd(self, strParam):
        pass

    @abstractmethod
    def isEmpty(self):
        pass


class strTerminator(mlCommandParamTerminator):
    def __init__(self, substr):
        if not bool(substr):
            raise ValueError("Given empty substr for terminator")
        self.substr = substr

    
    def matches(self, strParam):
        return self.substr in strParam


    def matchStart(self, strParam):
        return strParam.index(self.substr)


    def matchEnd(self, strParam):
        return self.matchStart(strParam) + len(self.substr)


    def isEmpty(self):
        return not bool(self.substr)

"""
class strEndTerminator(mlCommandParamTerminator):
    def __init__(self, substr):
        if not bool(substr):
            raise ValueError("Given empty substr for end terminator")
        self.substr = substr


    def matchesEnd(self, strParam):
        return self.substr in strParam


    def matchIndex(self, strParam):
        return strParam.index(self.substr)# if self.matchesEnd(strParam) else -1"""
        

class nullStartTerminator(mlCommandParamTerminator):
    def matches(self, strParam):
        return True

    def matchStart(self, strParam):
        return 0

    def matchEnd(self, strParam):
        return self.matchStart(strParam)

    def isEmpty(self):
        return True


class nullEndTerminator(mlCommandParamTerminator):
    def matchesEnd(self, strParam):
        return True

    def matchStart(self, strParam):
        return len(strParam) - (1 if bool(strParam) else 0)

    def matchEnd(self, strParam):
        return self.matchStart(strParam)

    def isEmpty(self):
        return True


NO_START_TERMINATOR = nullStartTerminator()
NO_END_TERMINATOR = nullEndTerminator()