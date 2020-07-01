from datetime import datetime, timedelta

"""
A fairly generic class that, at its core, tracks when a requested amount of time has passed.
Using an expiryFunction, a function call may be delayed by a given amount of time.
Using autoRescheduling, this class can also be used to easily schedule reoccurring tasks.
At least one of expiryTime or expiryDelta must be given.

@param issueTime -- The datetime when this task was created. Default: now
@param expiryTime -- The datetime when this task should expire. Default: None
@param expiryDelta -- The timedelta to add to issueTime, to find the expiryTime. Default: None
@param expiryFunction -- The function to call once expiryTime has been reached/surpassed. Default: None
@param expiryFunctionArgs -- The data to pass to the expiryFunction. There is no type requirement, but a dictionary is recommended as a close representation of KWArgs. Default: {}
@param autoReschedule -- Whether or not this task should automatically reschedule itself by the same timedelta. Default: False
"""
class TimedTask:
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
        self.gravestone = False


    """
    < Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is < other's expiryTime, False otherwise. 
    """
    def __lt__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError("< error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime < other.expiryTime


    """
    > Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is > other's expiryTime, False otherwise. 
    """
    def __gt__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError("> error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime > other.expiryTime


    """
    <= Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is <= other's expiryTime, False otherwise. 
    """
    def __lte__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError("<= error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime <= other.expiryTime


    """
    >= Overload, to be used in TimedTask heaps.
    The other object must be a TimedTask. Compares only the expiryTimes of the two tasks.

    @param -- other TimedTask to compare against.
    @return -- True if this TimedTask's expiryTime is >= other's expiryTime, False otherwise. 
    """
    def __gte__(self, other):
        if not isinstance(other, TimedTask):
            raise TypeError(">= error: TimedTask can only be compared to other TimedTasks")
        return self.expiryTime >= other.expiryTime

    
    """
    Decide whether or not this task has expired.
    This can be due to reaching the task's expiryTime, or due to manual expiry.

    @return -- True if this timedTask has been manually expired, or has reached its expiryTime. False otherwise
    """
    def isExpired(self):
        self.gravestone = self.gravestone or self.expiryTime <= datetime.utcnow()
        return self.gravestone


    """
    Call the task's expiryFunction, if one is specified.
    Handles passing of arguments to the expiryFunction, if specified.

    @return -- the results of the expiryFunction
    """
    def callExpiryFunction(self):
        # Pass args to expiryFunction if specified
        if self.hasExpiryFunctionArgs:
            return self.expiryFunction(self.expiryFunctionArgs)
        else:
            return self.expiryFunction()


    """
    Function to be called regularly, that handles the expiry of this task.
    Handles calling of the task's expiry function if specified, and rescheduling of the task if specified.

    @param callExpiryFunc -- Whether or not to call this task's expiryFunction if it is expired. Default: True
    @return -- True if this task is expired in this check, False otherwise. Regardless of autorescheduling.
    """
    def doExpiryCheck(self, callExpiryFunc=True):
        expired = self.isExpired()
        if expired:
            if callExpiryFunc and self.hasExpiryFunction:
                self.callExpiryFunction()
            if self.autoReschedule:
                self.reschedule()
        return expired

    
    """
    Reschedule this task, with the timedelta given/calculated on the task's creation, or to a given expiryTime/Delta.
    Rescheduling does not update the task's issueTime. TODO: A currentReissueTime tracker may be useful in the future.
    Giving an expiryTime or expiryDelta will not update the task's stored expiryDelta. I.e, if the task is rescheduled again without giving an expiryDelta,
    The expiryDelta given/calculated on the task's creation will be used.
    If both an expiryTime and an expiryDelta is given, the expiryTime takes precedence.

    @param expiryTime -- The new expiry time for the task. Default: now + expiryTime if expiryTime is specified, now + self.expiryTime otherwise
    @param expiryDelta -- The amount of time to wait until the task's next expiry. Default: now + self.expiryTime
    """
    def reschedule(self, expiryTime=None, expiryDelta=None):
        self.issueTime = datetime.utcnow()
        self.expiryTime = datetime.utcnow() + (self.expiryDelta if expiryDelta is None else expiryDelta) if expiryTime is None else expiryTime
        self.gravestone = False


    """
    Force the expiry of this task.
    Handles calling of this task's expiryFunction, and rescheduling if specified.
    TODO: Return the results of the expiry function

    @param callExpiryFunction -- Whether or not to call the task's expiryFunction if the task expires. Default: True
    """
    def forceExpire(self, callExpiryFunc=True):
        self.expiryTime = datetime.utcnow()
        if callExpiryFunc and self.hasExpiryFunction:
            self.callExpiryFunction()
        if self.autoReschedule:
            self.reschedule()
        else:
            self.gravestone = True


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
        self.gravestone = False
