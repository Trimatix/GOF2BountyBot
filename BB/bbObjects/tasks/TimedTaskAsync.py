from datetime import datetime, timedelta

class TimedTaskAsync:
    issueTime = None
    expiryTime = None
    expiryDelta = None
    expiryFunction = None
    expiryFunctionArgs = {}
    hasExpiryFunction = False
    hasExpiryFunctionArgs = False
    asyncExpiryFunction = False
    autoReschedule = False
    gravestone = False

    def __init__(self, issueTime=None, expiryTime=None, expiryDelta=None, expiryFunction=None, expiryFunctionArgs={}, autoReschedule=False, asyncExpiryFunction=False):
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
        self.asyncExpiryFunction = asyncExpiryFunction
        self.autoReschedule = autoReschedule

    
    def isExpired(self):
        self.gravestone = self.gravestone or self.expiryTime <= datetime.utcnow()
        return self.gravestone


    async def callExpiryFunction(self):
        if self.asyncExpiryFunction:
            if self.hasExpiryFunctionArgs:
                return await self.expiryFunction(self.expiryFunctionArgs)
            else:
                return await self.expiryFunction()
        else:
            if self.hasExpiryFunctionArgs:
                return self.expiryFunction(self.expiryFunctionArgs)
            else:
                return self.expiryFunction()


    async def doExpiryCheck(self, callExpiryFunc=True):
        expired = self.isExpired()
        if expired:
            if callExpiryFunc and self.hasExpiryFunction:
                await self.callExpiryFunction()
            if self.autoReschedule:
                await self.reschedule()
        return expired

    
    async def reschedule(self, expiryTime=None, expiryDelta=None):
        self.issueTime = datetime.utcnow()
        self.expiryTime = self.issueTime + (self.expiryDelta if expiryDelta is None else expiryDelta) if expiryTime is None else expiryTime
        self.gravestone = False


    async def forceExpire(self, callExpiryFunc=True):
        self.expiryTime = datetime.utcnow()
        if callExpiryFunc and self.hasExpiryFunction:
            await self.callExpiryFunction()
        if self.autoReschedule:
            await self.reschedule()
        else:
            self.gravestone = True


class DynamicRescheduleTaskAsync(TimedTaskAsync):
    delayTimeGenerator = None
    delayTimeGeneratorArgs = {}
    hasDelayTimeGeneratorArgs = False

    def __init__(self, delayTimeGenerator, delayTimeGeneratorArgs={}, issueTime=None, expiryTime=None, expiryFunction=None, expiryFunctionArgs={}, asyncDelayTimeGenerator=False, asyncExpiryFunction=False, autoReschedule=False):
        super(DynamicRescheduleTaskAsync, self).__init__(expiryDelta=delayTimeGenerator(delayTimeGeneratorArgs), issueTime=issueTime, expiryTime=expiryTime, expiryFunction=expiryFunction, expiryFunctionArgs=expiryFunctionArgs, asyncExpiryFunction=asyncExpiryFunction, autoReschedule=autoReschedule)
        self.delayTimeGenerator = delayTimeGenerator
        self.delayTimeGeneratorArgs = delayTimeGeneratorArgs
        self.hasDelayTimeGeneratorArgs = delayTimeGeneratorArgs != {}
        self.asyncDelayTimeGenerator = asyncDelayTimeGenerator


    async def callDelayTimeGenerator(self):
        if self.asyncDelayTimeGenerator:
            if self.hasDelayTimeGeneratorArgs:
                return await self.delayTimeGenerator(self.delayTimeGeneratorArgs)
            else:
                return await self.delayTimeGenerator()
        else:
            if self.hasDelayTimeGeneratorArgs:
                return self.delayTimeGenerator(self.delayTimeGeneratorArgs)
            else:
                return self.delayTimeGenerator()


    # @Override
    async def reschedule(self):
        self.issueTime = datetime.utcnow()
        self.expiryTime = self.issueTime + await self.callDelayTimeGenerator()
        self.gravestone = False
