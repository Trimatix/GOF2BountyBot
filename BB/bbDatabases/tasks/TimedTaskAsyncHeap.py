from ...bbObjects.tasks import TimedTaskAsync
from heapq import heappop, heappush

class TimedTaskAsyncHeap:
    # taskType = None
    tasksHeap = []
    expiryFunction = None
    expiryFunctionArgs = {}
    hasExpiryFunction = False
    hasExpiryFunctionArgs = False
    asyncExpiryFunction = False

    def __init__(self, expiryFunction=None, expiryFunctionArgs={}, asyncExpiryFunction=False):
        # self.taskType = taskType
        self.tasksHeap = []
        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs
        self.hasExpiryFunctionArgs = expiryFunctionArgs != {}
        self.asyncExpiryFunction = asyncExpiryFunction


    def cleanHead(self):
        while len(self.tasks) > 0 and self.tasksHeap[0].gravestone:
            heappop(self.tasksHeap)

    
    def scheduleTask(self, task):
        heappush(self.tasksHeap, task)

    
    # overrides task autoRescheduling
    def unscheduleTask(self, task):
        task.gravestone = True
        self.cleanHead()

    
    async def callExpiryFunction(self):
        if self.asyncExpiryFunction:
            if self.hasExpiryFunctionArgs:
                await self.expiryFunction(self.expiryFunctionArgs)
            else:
                await self.expiryFunction()
        else:
            if self.hasExpiryFunctionArgs:
                self.expiryFunction(self.expiryFunctionArgs)
            else:
                self.expiryFunction()

    
    async def doTaskChecking(self):
        while len(self.tasksHeap) > 0 and (self.tasksHeap[0].gravestone or await self.tasksHeap[0].doExpiryCheck()):
            if self.hasExpiryFunction:
                await self.callExpiryFunction()
            task = heappop(self.tasksHeap)
            # push autorescheduling tasks back onto the heap
            if not task.gravestone:
                heappush(self.tasksHeap, task)
