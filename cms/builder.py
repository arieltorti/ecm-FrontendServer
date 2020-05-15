from types import FunctionType
from sympy import (
    sympify,
    Symbol
)
from sympy.core.numbers import Float as FloatT
from .schemas import Model, Simulation
from scipy.integrate import odeint
import numpy as np

class Simulator:

    def __init__(self, model: Model):
        self.params = {p.name: Symbol(p.name) for p in model.params}
        
        # initialize expression environment variables
        self.expressionEnv = self.params.copy()
        compartmentsInit = {f"{c.name}_0": Symbol(f"{c.name}_0") for c in model.compartments}
        self.expressionEnv = dict(self.expressionEnv, **compartmentsInit)
        expressionsVars = {e.name: Symbol(e.name) for e in model.expressions}
        self.expressionEnv = dict(self.expressionEnv, **expressionsVars)

        # TODO: Check recursion of expressions
        self.expressions = {e.name: sympify(e.value, self.expressionEnv) for e in model.expressions}
        self.compartments = {c.name: Symbol(c.name) for c in model.compartments}

        # initialize reaction environment variables
        self.reactionEnv = self.expressionEnv.copy()
        self.reactionEnv = dict(self.expressionEnv, **self.compartments) 
        self.reactionEnv["t"] = Symbol("t")

        self.__initializeFormulas(model.reactions)

    def simulate(self, simulation: Simulation):
        tspan = np.arange(0, simulation.days, simulation.step)
        odeModel = self.__buildOdeModelFunction()
        initialConditions, variables = self.__preprocessVariables(simulation)

        print(self.odeVariables)

        if simulation.iterate:
            it = simulation.iterate
            tsimulation = simulation.copy()
            result = []
            for value in np.linspace(it.start, it.end, it.intervals):
                tsimulation.params[it.key] = value
                tvariables = variables[:]
                result.append(self.__singleSimulate(odeModel, initialConditions, tvariables, tsimulation.params, tspan))
        else:
            result = self.__singleSimulate(odeModel, initialConditions, variables, simulation.params, tspan)
        return self.compartments.keys(), tspan, result

    def __preprocessVariables(self, simulation):
        initialConditions = {Symbol(f"{c}_0"): simulation.initial_conditions[c] for c in self.compartments}
        variables = list(self.odeVariables)

        # Replace variable to expression
        for i in range(len(variables)):
            variables[i] = variables[i].subs(self.expressions)

        # Replace initial condition and param values
        for i in range(len(variables)):
            variables[i] = variables[i].subs(initialConditions)

        return list(initialConditions.values()), variables

    def __singleSimulate(self, odeModel, initialConditions, variables, params, tspan):
        varParams = {Symbol(c): params[c] for c in self.params}

        # Replace initial condition and param values
        for i in range(len(variables)):
            variables[i] = variables[i].subs(varParams)

        # TODO: Validate that all values replaced
        if (not any(isinstance(x, FloatT) for x in variables)):
            missingVariables = tuple(r for r in variables if not isinstance(r, float))
            raise ParsingError("simulate", f"Cannot solve symbols: {missingVariables}")

        print(variables)

        return odeint(odeModel, initialConditions, tspan, args=tuple(float(v) for v in variables))

    def __initializeFormulas(self, reactions):
        self.formulas = {x: 0 for x in self.compartments}
        self.odeVariables = set({})
        for reaction in reactions:
            funcExpr = sympify(reaction.function, self.reactionEnv)
            self.odeVariables = self.odeVariables.union(funcExpr.free_symbols)
            self.formulas[reaction.sfrom] -= funcExpr
            self.formulas[reaction.sto] += funcExpr
        self.odeVariables = tuple(self.odeVariables.difference(set(self.compartments.values())))

    def __buildOdeModelFunction(self):
        modelstr = f"def ode_model(z, t, {', '.join(str(s) for s in self.odeVariables)}):\n"
        modelstr += f"    dz = [0]*{len(self.compartments)}\n"
        modelstr += f"    {', '.join(self.compartments.keys())} = z\n"
        for idx, (compartment, formula) in enumerate(self.formulas.items()):
            modelstr += f"    dz[{idx}] = {formula} # {compartment}\n"
        modelstr += "    return dz"

        print(modelstr)
        modelcode = compile(modelstr, f"<odeModel>", "exec")
        return FunctionType(modelcode.co_consts[0], globals(), "ode_model")
