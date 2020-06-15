from datetime import datetime, timedelta

class TimedTask:
    issueTime = None
    expiryTime = None
    expiryDelta = None
    expiryFunction = None
    expiryFunctionArgs = {}
    hasExpiryFunction = False
    hasExpiryFunctionArgs = False
    autoReschedule = False

    def __init__(self, issueTime=None, expiryTime=None, expiryDelta=None, expiryFunction=None, expiryFunctionArgs={}, autoReschedule=False):
        if expiryTime is None:
            if expiryDelta is None:
                raise ValueError("No expiry time given, both expiryTime and expiryDelta are None")
        self.issueTime = datetime.utcnow() if issueTime is None else issueTime
        self.expiryTime = self.issueTime + expiryDelta if expiryTime is None else expiryTime
        self.expiryDelta = self.expiryTime - self.issueTime if expiryDelta is None else expiryDelta
        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs
        self.hasExpiryFunctionArgs = expiryFunctionArgs != {}
        self.autoReschedule = autoReschedule

    
    def isExpired(self):
        return self.expiryTime <= datetime.utcnow()


    def callExpiryFunction(self):
        if self.hasExpiryFunctionArgs:
            return self.expiryFunction(self.expiryFunctionArgs)
        else:
            return self.expiryFunction()


    def doExpiryCheck(self, callExpiryFunc=True):
        expired = self.isExpired()
        if expired:
            if callExpiryFunc and self.hasExpiryFunction:
                self.callExpiryFunction()
            if self.autoReschedule:
                self.reschedule()
        return expired

    
    def reschedule(self, expiryTime=None, expiryDelta=None):
        self.issueTime = datetime.utcnow()
        self.expiryTime = self.issueTime + (self.expiryDelta if expiryDelta is None else expiryDelta) if expiryTime is None else expiryTime


    def forceExpire(self, callExpiryFunc=True):
        self.expiryTime = datetime.utcnow()
        if callExpiryFunc and self.hasExpiryFunction:
            self.callExpiryFunction()
        if self.autoReschedule:
            self.reschedule()


class DynamicRescheduleTask(TimedTask):
    delayTimeGenerator = None
    delayTimeGeneratorArgs = {}
    hasDelayTimeGeneratorArgs = False

    def __init__(self, delayTimeGenerator, delayTimeGeneratorArgs={}, issueTime=None, expiryTime=None, expiryFunction=None, expiryFunctionArgs={}, autoReschedule=False):
        super(DynamicRescheduleTask, self).__init__(expiryDelta=delayTimeGenerator(delayTimeGeneratorArgs), issueTime=issueTime, expiryTime=expiryTime, expiryFunction=expiryFunction, expiryFunctionArgs=expiryFunctionArgs, autoReschedule=autoReschedule)
        self.delayTimeGenerator = delayTimeGenerator
        self.delayTimeGeneratorArgs = delayTimeGeneratorArgs
        self.hasDelayTimeGeneratorArgs = delayTimeGeneratorArgs != {}

    
    def callDelayTimeGenerator(self):
        if self.hasDelayTimeGeneratorArgs:
            return self.delayTimeGenerator(self.delayTimeGeneratorArgs)
        else:
            return self.delayTimeGenerator()


    # @Override
    def reschedule(self):
        self.issueTime = datetime.utcnow()
        self.expiryTime = self.issueTime + self.callDelayTimeGenerator()
