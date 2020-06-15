from ...bbObjects.tasks import TimedTask
from heapq import heappop, heappush, heap

class TimedTaskHeap:
    # taskType = None
    expiryFunction = None
    expiryFunctionArgs = {}
    hasExpiryFunction = False
    hasExpiryFunctionArgs = False

    def __init__(self, expiryFunction=None, expiryFunctionArgs={}):
        # self.taskType = taskType
        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs
        self.hasExpiryFunctionArgs = expiryFunctionArgs != {}


    def cleanHead(self):
        while heap[0].gravestone:
            heappop()

    
    def scheduleTask(self, task):
        heappush(task)

    
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
        while heap[0].gravestone or heap[0].doExpiryCheck():
            if self.hasExpiryFunction:
                self.callExpiryFunction()
            task = heappop()
            # push autorescheduling tasks back onto the heap
            if not task.gravestone:
                heappush(task)
