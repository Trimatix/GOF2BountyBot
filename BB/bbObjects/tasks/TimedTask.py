from datetime import datetime, timedelta

class TimedTask:
    issueTime = None
    expiryTime = None
    expiryDelta = None
    expiryFunction = None
    expiryFunctionArgs = {}
    hasExpiryFunction = False

    def __init__(self, issueTime=None, expiryTime=None, expiryDelta=None, expiryFunction=None, expiryFunctionArgs={}):
        if expiryTime is None:
            if expiryDelta is None:
                raise ValueError("No expiry time given, both expiryTime and expiryDelta are None")
        self.issueTime = datetime.utcnow() if issueTime is None else issueTime
        self.expiryTime = issueTime + expiryDelta if expiryTime is None else expiryTime
        self.expiryDelta = expiryTime - issueTime if expiryDelta is None else expiryDelta
        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs

    
    def isExpired(self, now=None):
        return self.expiryTime <= self.expiryTime if now is None else now


    def doExpiryCheck(self, now=None, callExpiryFunction=True):
        if self.isExpired(now=now) and callExpiryFunction and self.hasExpiryFunction:
            self.expiryFunction(self.expiryFunctionArgs)
        return self.isExpired(now=now)

    
    def reschedule(self, now=None, expiryTime=None, expiryDelta=None):
        self.issueTime = datetime.utcnow() if now is None else now
        self.expiryTime = self.issueTime + (self.expiryDelta if expiryDelta is None else expiryDelta) if expiryTime is None else expiryTime
