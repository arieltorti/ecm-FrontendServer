from types import FunctionType
from sympy import (
    sympify,
    Symbol,
    true as BTrue,
    false as BFalse
)
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.numbers import Float as FloatT
from cms.schemas import Model, Simulation
from scipy.integrate import odeint
import numpy as np

class SimulatorError(Exception):
    pass

class SimulationResult:
    def __init__(self, compartments, timeline, frames, param = None, paramValues = []):
        self.compartments = compartments
        self.timeline = timeline
        self.frames = frames
        self.param = param
        self.paramValues = paramValues

    @property
    def isIterated(self):
        return self.param is not None

class ModelContext:
    def __init__(self, model: Model):
        self.params = {p.name: Symbol(p.name) for p in model.params}
        
        # initialize expression environment variables
        self.expressionEnv = self.params.copy()
        compartmentsInit = {f"{c.name}_0": Symbol(f"{c.name}_0") for c in model.compartments}
        self.expressionEnv.update(compartmentsInit)
        expressionsVars = {e.name: Symbol(e.name) for e in model.expressions}
        self.expressionEnv.update(expressionsVars)

        # TODO: Check recursion of expressions
        self.expressions = {e.name: sympify(e.value, self.expressionEnv) for e in model.expressions}
        self.compartments = {c.name: Symbol(c.name) for c in model.compartments}
        self.preconditions = {p.predicate: sympify(p.predicate, self.expressionEnv) for p in model.preconditions}

        # initialize reaction environment variables
        self.reactionEnv = self.expressionEnv.copy()
        self.reactionEnv.update(self.compartments)
        self.reactionEnv["t"] = Symbol("t")
        self.observables = {o.name: sympify(o.value, self.reactionEnv) for o in model.observables}

        self.__initializeFormulas(model.reactions)

    def __initializeFormulas(self, reactions):
        self.formulas = {x: 0 for x in self.compartments}
        self.odeVariables = set({})
        for reaction in reactions:
            funcExpr = sympify(reaction.function, self.reactionEnv)
            self.odeVariables = self.odeVariables.union(funcExpr.free_symbols)
            self.formulas[reaction.sfrom] -= funcExpr
            self.formulas[reaction.sto] += funcExpr
        self.odeVariables = tuple(self.odeVariables.difference(set(self.compartments.values())))

class Simulator:
    def __init__(self, context: ModelContext):
        self.context = context

    def simulate(self, simulation: Simulation):
        timeline = np.arange(0, simulation.days, simulation.step)
        odeModel = self.__buildOdeModelFunction()
        preconditions, initialConditions, variables = self.__preprocessVariables(simulation)
        result = SimulationResult(list(self.context.compartments.keys()), timeline, [])
        if simulation.iterate:
            it = simulation.iterate
            result.paramValues = np.linspace(it.start, it.end, it.intervals)
            result.param = it.key
            tsimulation = simulation.copy()
            for value in result.paramValues:
                tsimulation.params[it.key] = value
                tvariables = variables[:]
                tpreconditions = preconditions.copy()
                self.__validatePreconditions(tpreconditions, tsimulation.params)
                result.frames.append(self.__singleSimulate(odeModel, initialConditions, tvariables, tsimulation.params, timeline))
        else:
            self.__validatePreconditions(preconditions, simulation.params)
            result.frames.append(self.__singleSimulate(odeModel, initialConditions, variables, simulation.params, timeline))
        return result

    def __preprocessVariables(self, simulation):
        initialConditions = self.__initialConditions(simulation.initial_conditions)

        preconditions = self.context.preconditions.copy()
        variables = list(self.context.odeVariables)

        # Replace variable to expression and initial conditions
        for i in range(len(variables)):
            variables[i] = variables[i].subs(self.context.expressions) \
                                       .subs(initialConditions)

        for name, predExpr in preconditions.items():
            preconditions[name] = preconditions[name].subs(self.context.expressions) \
                                                     .subs(initialConditions)

        return preconditions, list(initialConditions.values()), variables

    def __validatePreconditions(self, preconditions, params):
        varParams = self.__varParams(params)
        # Replace param values
        for name in preconditions:
            preconditions[name] = preconditions[name].subs(varParams)
            if (preconditions[name] not in [BTrue, BFalse]):
                raise SimulatorError("simulate", f"Cannot solve precondition [{name}]: {preconditions[name]}")
            if (preconditions[name] == BFalse):
                raise SimulatorError("simulate", f"Precondition not satisisfied: {name}")

    def __initialConditions(self, initial_conditions):
        initialConditions = {}
        try:
            initialConditions = {Symbol(f"{c}_0"): initial_conditions[c] for c in self.context.compartments}
        except KeyError as e:
            raise SimulatorError("simulate", f"Missing initialization for compartment {e}")
        return initialConditions

    def __varParams(self, params):
        varParams = {}
        try:
            varParams = {Symbol(c): params[c] for c in self.context.params}
        except KeyError as e:
            raise SimulatorError("simulate", f"Missing parameter {e}")
        return varParams

    def __singleSimulate(self, odeModel, initialConditions, variables, params, tspan):
        varParams = self.__varParams(params)

        # Replace param values
        for i in range(len(variables)):
            variables[i] = variables[i].subs(varParams)

        # Validates that all values were replaced
        if (not all(x.is_number for x in variables)):
            missingVariables = list(r for r in variables if not isinstance(r, FloatT))
            raise SimulatorError("simulate", f"Cannot solve symbols: {missingVariables}")
        return odeint(odeModel, initialConditions, tspan, args=tuple(float(v) for v in variables))

    def __buildOdeModelFunction(self):
        modelstr = f"def ode_model(z, t, {', '.join(str(s) for s in self.context.odeVariables)}):\n"
        modelstr += f"    dz = [0]*{len(self.context.compartments)}\n"
        modelstr += f"    {', '.join(self.context.compartments.keys())} = z\n"
        for idx, (compartment, formula) in enumerate(self.context.formulas.items()):
            modelstr += f"    dz[{idx}] = {formula} # {compartment}\n"
        modelstr += "    return dz"
        modelcode = compile(modelstr, f"<odeModel>", "exec")
        return FunctionType(modelcode.co_consts[0], globals(), "ode_model")


def __buildFunctionNP(compartments, name, expr):
    # todo: support other environment variables. Only compartments are allowed in this version.
    fstr = "def observable(row):\n"
    fstr += f"    {', '.join(str(s) for s in compartments)}, *others = row\n"
    fstr += f"    return {expr}"
    fstrcode = compile(fstr, f"<{name}>", "exec")
    return FunctionType(fstrcode.co_consts[0], globals(), name)

def computeExtraColumns(context: ModelContext, result: SimulationResult):
    if len(context.observables) > 0:
        functions = [__buildFunctionNP(result.compartments, n, o) for n,o in context.observables.items()]
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