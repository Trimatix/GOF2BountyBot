# import inspect

"""
class funcRef:
    def __init__(self, func):
        self.func = func
        self.isCoroutine = inspect.iscoroutinefunction(func)
        self.params = inspect.signature(addFunc).parameters


    async def call(self, args):
        if self.isCoroutine:
            await self.func(args)
        else:
            self.func(args)


class funcArgs:
    def __init__(self, args{}):
"""