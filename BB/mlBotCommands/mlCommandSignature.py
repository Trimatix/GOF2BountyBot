from . import mlCommandParamTerminators, mlCommandExceptions

class mlCommandSignature:
    def __init__(self, positional=[], keyword={}, stripSpaces=True):
        self.requiredParams = 0
        # TODO: Handle the cases where arg 1 has no end terminator but is matched, arg 2 has a start terminator but is not matched but is optional so its fine, arg 3 has no start terminator
        parsingOptional = False
        for paramNum in range(len(positional)):
            if paramNum != 0 and \
                positional[paramNum].startTerminator is mlCommandParamTerminators.NO_START_TERMINATOR and \
                positional[paramNum - 1].endTerminator is mlCommandParamTerminators.NO_END_TERMINATOR:
                    raise mlCommandExceptions.NoTerminationPossible("Argument " + str(paramNum-1) + " has no end terminator and argument " + str(paramNum) + " has no start terminator, so splitting of these arguments is not possible.")
            if not positional[paramNum].optional:
                self.requiredParams += 1

        self.positional = positional
        self.keyword = keyword
        self.numPositional = len(positional)
        self.numKeyword = len(keyword)
        self.stripSpaces = stripSpaces
        

    def fromStrNew(self, strParams):
        potentialSigs = []

        positional = []
        keyword = {}
        argNum = 0
        unterminatedArg = -1
        requiredParamsFound = 0
        # attempt to match args, assuming all optional args are present
        # then attempt for optional args - 1
        # then -2, etc
        # for i in range(self.optionalArgs):

        # First pass: Check all required arguments can be matched
        for paramType in self.positional:
            if paramType.optional:
                continue

            if strParams == "":
                if not paramType.optional:
                    raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(argNum + 1) + " required, but no further arguments passed.")
                continue

            if unterminatedArg != -1 and not self.positional[unterminatedArg].startTerminator.isEmpty():
                workingArgs = strParams[self.positional[unterminatedArg].startTerminator.matchEnd(strParams):]
            else:
                workingArgs = strParams

            if argNum == 2:
                print("working:",workingArgs)

            # If param has a start terminator
            if paramType.startTerminator is not mlCommandParamTerminators.NO_START_TERMINATOR:
                # if start terminator does not match
                if not paramType.startTerminator.matches(workingArgs):
                    # throw an exception if this parameter is required, skip the parameter otherwise
                    if not paramType.optional:
                        # return positional
                        raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(argNum + 1) + " start terminator not matched.")
                    continue
                
            # if start terminator matches (or no start terminator needed for param)
            # and a previous param is awaiting termination
            if unterminatedArg != -1:
                # find and instance unterminated param type
                prevParamType = self.positional[unterminatedArg]
                positional.append(prevParamType.fromStr(strParams[prevParamType.startTerminator.matchEnd(strParams):paramType.startTerminator.matchStart(workingArgs) + len(strParams) - len(workingArgs)]))
                strParams = workingArgs[paramType.startTerminator.matchStart(workingArgs):]
                requiredParamsFound += 1
                print("A: '" + strParams + "'")
                """if self.stripSpaces:
                    strParams = strParams.lstrip()"""
                unterminatedArg = -1
            
            # if start matches (or no start terminator needed for param)
            # and has end terminator
            if paramType.endTerminator is not mlCommandParamTerminators.NO_END_TERMINATOR:
                # if end terminator doesnt match
                if not paramType.endTerminator.matches(workingArgs):
                    # throw an exception if this parameter is required, skip the parameter otherwise
                    if not paramType.optional:
                        raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(argNum + 1) + " end terminator not matched.")
                    continue
            # if has no end terminator
            else:
                # If this is the last param
                if argNum == self.numPositional - 1:
                    # If an arg is awaiting termination
                    if unterminatedArg != -1:
                        prevParamType = self.positional[unterminatedArg]
                        # If both this arg and the unterminated one are required, throw an error
                        if not paramType.optional:
                            raise mlCommandExceptions.RequiredArgumentNotFound("Required argument " + str(unterminatedArg + 1) + " not found.")
                        # If neither this arg nor the unterminated one are optional, prioritise the unterminated one.
                        # If just one is required, discard the optional one
                        else:
                            positional.append(prevParamType.fromStr(strParams[prevParamType.startTerminator.matchEnd(strParams):]))
                            requiredParamsFound += 1
                            print("B: '" + strParams + "'")
                            strParams = ""
                            unterminatedArg = -1
                            break
                # If this is not the last param
                else:
                    # if another arg is currently unterminated
                    if unterminatedArg != -1:
                        prevParamType = self.positional[unterminatedArg]
                        # if neither this arg nor the unterminated one is required, prioritise the unterminated one by ignoring the current arg
                        # if just one is required, ignore the optional arg
                        # if both args are required, throw an error
                        if not paramType.optional:
                            raise mlCommandExceptions.RequiredArgumentNotFound("Required argument " + str(unterminatedArg + 1) + " has no terminator and was not terminated before reaching another required argument with no terminator: " + str(argNum))
                        continue
                    # If no arg is currently awaiting termination, set this arg to await termination
                    else:
                        unterminatedArg = argNum
                        argNum += 1
                        continue

            # If terminators match, save this arg
            positional.append(paramType.fromStr(strParams[paramType.startTerminator.matchEnd(strParams):paramType.endTerminator.matchEnd(strParams) + 1]))
            requiredParamsFound += 1
            print("C matchend:",paramType.endTerminator.matchEnd(strParams),"paramStr:",strParams,"matchStart:",paramType.endTerminator.matchStart(strParams))#,"substr:",paramType.endTerminator.substr)
            try:
                strParams = strParams[paramType.endTerminator.matchEnd(strParams) + (0 if paramType.endTerminator.isEmpty() else 1):]
                """if self.stripSpaces:
                    strParams = strParams.lstrip()"""
            except IndexError:
                strParams = ""
            print("C: '" + strParams + "'")
            argNum = min(argNum + 1, self.numPositional - 1)

        if unterminatedArg != -1:
            prevParamType = self.positional[unterminatedArg]
            if strParams == "":
                if not prevParamType.optional:
                    raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(unterminatedArg + 1) + " has no end terminator, but no further parameters were passed.")
            else:
                positional.append(prevParamType.fromStr(strParams[prevParamType.startTerminator.matchEnd(strParams):]))
                if not prevParamType.optional:
                    requiredParamsFound += 1
                print("B: '" + strParams + "'")
                strParams = ""
                unterminatedArg = -1

        return positional
    


    def fromStrOld(self, strParams):
        positional = []
        keyword = {}
        argNum = 0
        unterminatedArg = -1
        requiredParamsFound = 0

        for paramType in self.positional:
            if strParams == "":
                if not paramType.optional:
                    raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(argNum + 1) + " required, but no further arguments passed.")
                continue

            if unterminatedArg != -1 and not self.positional[unterminatedArg].startTerminator.isEmpty():
                workingArgs = strParams[self.positional[unterminatedArg].startTerminator.matchEnd(strParams):]
            else:
                workingArgs = strParams

            if argNum == 2:
                print("working:",workingArgs)

            # If param has a start terminator
            if paramType.startTerminator is not mlCommandParamTerminators.NO_START_TERMINATOR:
                # if start terminator does not match
                if not paramType.startTerminator.matches(workingArgs):
                    # throw an exception if this parameter is required, skip the parameter otherwise
                    if not paramType.optional:
                        return positional
                        raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(argNum + 1) + " start terminator not matched.")
                    continue
                
            # if start terminator matches (or no start terminator needed for param)
            # and a previous param is awaiting termination
            if unterminatedArg != -1:
                # find and instance unterminated param type
                prevParamType = self.positional[unterminatedArg]
                if prevParamType.optional:
                    if prevParamType.endTerminator is not mlCommandParamTerminators.NO_END_TERMINATOR:
                        endPoint = prevParamType.endTerminator.matchEnd(strParams)
                    else:
                        endPoint = paramType.endTerminator.matchEnd(workingArgs) + len(strParams) - len(workingArgs)
                    
                    if strParams[endPoint:] == "":
                        unterminatedArg = -1
                positional.append(prevParamType.fromStr(strParams[prevParamType.startTerminator.matchEnd(strParams):paramType.startTerminator.matchStart(workingArgs) + len(strParams) - len(workingArgs)]))
                strParams = workingArgs[paramType.startTerminator.matchStart(workingArgs):]
                if not prevParamType.optional:
                    requiredParamsFound += 1
                print("A: '" + strParams + "'")
                """if self.stripSpaces:
                    strParams = strParams.lstrip()"""
                unterminatedArg = -1
            
            # if start matches (or no start terminator needed for param)
            # and has end terminator
            if paramType.endTerminator is not mlCommandParamTerminators.NO_END_TERMINATOR:
                # if end terminator doesnt match
                if not paramType.endTerminator.matches(workingArgs):
                    # throw an exception if this parameter is required, skip the parameter otherwise
                    if not paramType.optional:
                        raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(argNum + 1) + " end terminator not matched.")
                    continue
            # if has no end terminator
            else:
                # If this is the last param
                if argNum == self.numPositional - 1:
                    # If an arg is awaiting termination
                    if unterminatedArg != -1:
                        prevParamType = self.positional[unterminatedArg]
                        # If both this arg and the unterminated one are required, throw an error
                        if not prevParamType.optional and not paramType.optional:
                            raise mlCommandExceptions.RequiredArgumentNotFound("Required argument " + str(unterminatedArg + 1) + " not found.")
                        # If neither this arg nor the unterminated one are optional, prioritise the unterminated one.
                        # If just one is required, discard the optional one
                        elif paramType.optional:
                            positional.append(prevParamType.fromStr(strParams[prevParamType.startTerminator.matchEnd(strParams):]))
                            if not prevParamType.optional:
                                requiredParamsFound += 1
                            print("B: '" + strParams + "'")
                            strParams = ""
                            unterminatedArg = -1
                            break
                # If this is not the last param
                else:
                    # if another arg is currently unterminated
                    if unterminatedArg != -1:
                        prevParamType = self.positional[unterminatedArg]
                        # if neither this arg nor the unterminated one is required, prioritise the unterminated one by ignoring the current arg
                        # if just one is required, ignore the optional arg
                        if prevParamType.optional:
                            unterminatedArg = argNum
                        # if both args are required, throw an error
                        elif not paramType.optional:
                            raise mlCommandExceptions.RequiredArgumentNotFound("Required argument " + str(unterminatedArg + 1) + " has no terminator and was not terminated before reaching another required argument with no terminator: " + str(argNum))
                        continue
                    # If no arg is currently awaiting termination, set this arg to await termination
                    else:
                        unterminatedArg = argNum
                        argNum += 1
                        continue

            # If terminators match, save this arg
            positional.append(paramType.fromStr(strParams[paramType.startTerminator.matchEnd(strParams):paramType.endTerminator.matchEnd(strParams) + 1]))
            if not paramType.optional:
                requiredParamsFound += 1
            print("C matchend:",paramType.endTerminator.matchEnd(strParams),"paramStr:",strParams,"matchStart:",paramType.endTerminator.matchStart(strParams))#,"substr:",paramType.endTerminator.substr)
            try:
                strParams = strParams[paramType.endTerminator.matchEnd(strParams) + (0 if paramType.endTerminator.isEmpty() else 1):]
                """if self.stripSpaces:
                    strParams = strParams.lstrip()"""
            except IndexError:
                strParams = ""
            print("C: '" + strParams + "'")
            argNum = min(argNum + 1, self.numPositional - 1)

        if unterminatedArg != -1:
            prevParamType = self.positional[unterminatedArg]
            if strParams == "":
                if not prevParamType.optional:
                    raise mlCommandExceptions.RequiredArgumentNotFound("Argument " + str(unterminatedArg + 1) + " has no end terminator, but no further parameters were passed.")
            else:
                positional.append(prevParamType.fromStr(strParams[prevParamType.startTerminator.matchEnd(strParams):]))
                if not prevParamType.optional:
                    requiredParamsFound += 1
                print("B: '" + strParams + "'")
                strParams = ""
                unterminatedArg = -1

        return positional
