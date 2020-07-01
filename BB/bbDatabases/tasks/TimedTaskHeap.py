from ...bbObjects.tasks import TimedTask
from heapq import heappop, heappush
import inspect

"""
A min-heap of TimedTasks, sorted by task expiration time.

@param expiryFunction -- function reference to call upon the expiry of any TimedTask managed by this heap. Default: None
@param expiryFunctionArgs -- the data to pass to expiryFunction when calling. There is no type requirement, but a dictionary is recommended as a close representation of KWArgs. Default: {}
"""
class TimedTaskHeap:
    def __init__(self, expiryFunction=None, expiryFunctionArgs={}):
        # self.taskType = taskType
        self.tasksHeap = []
        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs
        self.hasExpiryFunctionArgs = expiryFunctionArgs != {}
        self.asyncExpiryFunction = inspect.iscoroutinefunction(expiryFunction)


    """
    Remove expired tasks from the head of the heap.
    A task's 'gravestone' represents the task no longer being able to be called.
    I.e, it is expired (whether manually or through timeout) and does not auto-reschedule.

    """
    def cleanHead(self):
        while len(self.tasks) > 0 and self.tasksHeap[0].gravestone:
            heappop(self.tasksHeap)

    
    """
    Schedule a new task onto this heap.

    @param task -- the task to schedule
    """
    def scheduleTask(self, task):
        heappush(self.tasksHeap, task)

    
    """
    Forcebly remove a task from the heap without 'expiring' it - no expiry functions or auto-rescheduling are called. 

    @param task -- the task to remove from the heap
    """
    # overrides task autoRescheduling
    def unscheduleTask(self, task):
        task.gravestone = True
        self.cleanHead()

    
    """
    Call the HEAP's expiry function - not a task expiry function.
    Accounts for expiry function arguments (if specified) and asynchronous expiry functions

    """
    async def callExpiryFunction(self):
        # Await coroutine asynchronous functions
        if self.asyncExpiryFunction:
            # Pass args to the expiry function, if they are specified
            if self.hasExpiryFunctionArgs:
                await self.expiryFunction(self.expiryFunctionArgs)
            else:
                await self.expiryFunction()
        # Do not await synchronous functions
        else:
            # Pass args to the expiry function, if they are specified
            if self.hasExpiryFunctionArgs:
                self.expiryFunction(self.expiryFunctionArgs)
            else:
                self.expiryFunction()

    
    """
    Function to be called regularly, that handles the expiring of tasks.
    Tasks are checked against their expiry times and manual expiry.
    Task and heap-level expiry functions are called upon task expiry, if they are defined.
    Tasks are rescheduled if they are marked for auto-rescheduling.
    Expired, non-rescheduling tasks are removed from the heap.

    """
    async def doTaskChecking(self):
        # Is the task at the head of the heap expired?
        while len(self.tasksHeap) > 0 and (self.tasksHeap[0].gravestone or await self.tasksHeap[0].doExpiryCheck()):
            # Call the heap's expiry function
            if self.hasExpiryFunction:
                await self.callExpiryFunction()
            # Remove the expired task from the heap
            task = heappop(self.tasksHeap)
            # push autorescheduling tasks back onto the heap
            if not task.gravestone:
                heappush(self.tasksHeap, task)
