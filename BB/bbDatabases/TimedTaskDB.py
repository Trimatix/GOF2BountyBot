from ..bbObjects.tasks import TimedTask

class TimedTaskTB:
    # This may be changed to a dict of expiry/issueTime:task later
    tasks = []
    taskType = None
    expiryFunction = None
    expiryFunctionArgs = {}
    hasExpiryFunction = False

    def __init__(self, taskType=TimedTask, expiryFunction=None, expiryFunctionArgs={}):
        self.taskType = taskType
        self.expiryFunction = expiryFunction
        self.hasExpiryFunction = expiryFunction is not None
        self.expiryFunctionArgs = expiryFunctionArgs

    
    def scheduleTask(self, task):
        self.tasks += task

    
    def unscheduleTask(self, task):
        self.tasks.remove(task)

    
    def doTaskChecking(self):
        for task in self.tasks:
            if task.doExpiryCheck() and self.hasExpiryFunction:
                self.expiryFunction(self.expiryFunctionArgs)
