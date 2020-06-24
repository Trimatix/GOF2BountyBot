from ...bbObjects.tasks import TimedTask
from heapq import heappop, heappush

class TimedTaskHeap:
    # taskType = None
    tasksHeap = []
    expiryFunction = None
    expiryFunctionArgs = {}
    hasExpiryFunction = False
    hasExpiryFunctionArgs = False

    def __init__(self, expiryFunction=None, expiryFunctionArgs={}):
        # self.taskType = taskType
        self.tasksHeap = []
        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs
        self.hasExpiryFunctionArgs = expiryFunctionArgs != {}


    def cleanHead(self):
        while len(self.tasksHeap) > 0 and self.tasksHeap[0].gravestone:
            heappop(self.tasksHeap)

    
    def scheduleTask(self, task):
        heappush(self.tasksHeap, task)

    
    # overrides task autoRescheduling
    def unscheduleTask(self, task):
        task.gravestone = True
        self.cleanHead()

    
    def callExpiryFunction(self):
        if self.hasExpiryFunctionArgs:
            self.expiryFunction(self.expiryFunctionArgs)
        else:
            self.expiryFunction()

    
    def doTaskChecking(self):
        while len(self.tasksHeap) > 0 and (self.tasksHeap[0].gravestone or self.tasksHeap[0].doExpiryCheck()):
            if self.hasExpiryFunction:
                self.callExpiryFunction()
            task = heappop(self.tasksHeap)
            # push autorescheduling tasks back onto the heap
            if not task.gravestone:
                heappush(self.tasksHeap, task)
