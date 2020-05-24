from types import FunctionType
import numpy as np
from .base import ModelContext, SimulationResult

def __buildFunctionObservable(compartments, name, expr):
    # todo: support other environment variables. Only compartments are allowed in this version.
    fstr = "def observable(row):\n"
    fstr += f"    {', '.join(str(s) for s in compartments)}, *others = row\n"
    fstr += f"    return {expr}"
    fstrcode = compile(fstr, f"<{name}>", "exec")
    return FunctionType(fstrcode.co_consts[0], globals(), name)

def computeExtraColumns(context: ModelContext, result: SimulationResult):
    if len(context.observables) > 0:
        functions = [__buildFunctionObservable(result.compartments, n, o) for n,o in context.observables.items()]
        obsSize = len(context.observables)
        compSize = len(result.compartments)
        for findex, frame in enumerate(result.frames):
            shape = list(frame.shape)
            shape[1] += obsSize
            newFrame = np.zeros(tuple(shape))
            newFrame[:,:-obsSize] = frame
            for idx, function in enumerate(functions):
                newFrame[:, compSize + idx] = np.apply_along_axis(function, 1, newFrame)
            result.frames[findex] = newFrame
        result.compartments += list(context.observables.keys())