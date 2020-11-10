from BB.mlBotCommands import mlCommandParams, mlCommandParamTerminators, mlCommandSignature

posArgs = []
posArgs.append(mlCommandParams.mlStringParam(False, mlCommandParamTerminators.NO_START_TERMINATOR, mlCommandParamTerminators.NO_END_TERMINATOR))
posArgs.append(mlCommandParams.mlStringParam(True, mlCommandParamTerminators.strTerminator(" ,"), mlCommandParamTerminators.NO_END_TERMINATOR))
posArgs.append(mlCommandParams.mlStringParam(False, mlCommandParamTerminators.strTerminator(" ,"), mlCommandParamTerminators.NO_END_TERMINATOR))

cmdSig = mlCommandSignature.mlCommandSignature(positional=posArgs)

inputparams = "param 1 ,param 2"
outparams = cmdSig.fromStr(inputparams)

print("generated:")
for param in outparams:
    print("-",str(param))