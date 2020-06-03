from types import FunctionType
from sympy import Symbol, true as BTrue, false as BFalse, Float as FloatT
from ecm.schemas import Simulation
from scipy.integrate import odeint
import numpy as np
from .base import ModelContext, SimulationResult, SimulatorError


class Simulator:
    def __init__(self, context: ModelContext):
        self.context = context

    def simulate(self, simulation: Simulation):
        timeline = np.arange(0, simulation.days, simulation.step)
        odeModel = self.__buildOdeModelFunction()
        preconditions, initialConditions, variables = self.__preprocessVariables(
            simulation
        )
        result = SimulationResult(list(self.context.compartments.keys()), timeline)
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
                result.frames.append(
                    self.__singleSimulate(
                        odeModel,
                        initialConditions,
                        tvariables,
                        tsimulation.params,
                        timeline,
                    )
                )
        else:
            self.__validatePreconditions(preconditions, simulation.params)
            result.frames.append(
                self.__singleSimulate(
                    odeModel, initialConditions, variables, simulation.params, timeline
                )
            )
        return result

    def __preprocessVariables(self, simulation):
        #TODO: refactor this, is ugly
        ModelContext.unfoldExpression(self.context.expressions)

        initialConditions = self.__initialConditions(simulation.initial_conditions)

        preconditions = self.context.preconditions.copy()
        variables = list(self.context.odeVariables)

        # Replace variable to expression and initial conditions
        for i in range(len(variables)):
            variables[i] = (
                variables[i].subs(self.context.expressions).subs(initialConditions)
            )

        for name, predExpr in preconditions.items():
            preconditions[name] = (
                preconditions[name]
                .subs(self.context.expressions)
                .subs(initialConditions)
            )

        return preconditions, list(initialConditions.values()), variables

    def __validatePreconditions(self, preconditions, params):
        varParams = self.__varParams(params)
        # Replace param values
        for name in preconditions:
            preconditions[name] = preconditions[name].subs(varParams)
            if preconditions[name] not in [BTrue, BFalse]:
                raise SimulatorError(
                    "simulate",
                    f"Cannot solve precondition [{name}]: {preconditions[name]}",
                )
            if preconditions[name] == BFalse:
                raise SimulatorError(
                    "simulate", f"Precondition not satisisfied: {name}"
                )

    def __initialConditions(self, initial_conditions):
        initialConditions = {}
        try:
            initialConditions = {
                Symbol(f"{c}_0"): initial_conditions[c]
                for c in self.context.compartments
            }
        except KeyError as e:
            raise SimulatorError(
                "simulate", f"Missing initialization for compartment {e}"
            )
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
        if not all(x.is_number for x in variables):
            missingVariables = list(r for r in variables if not isinstance(r, FloatT))
            raise SimulatorError(
                "simulate", f"Cannot solve symbols: {missingVariables}"
            )
        return odeint(
            odeModel, initialConditions, tspan, args=tuple(float(v) for v in variables)
        )

    def __buildOdeModelFunction(self):
        modelstr = f"def ode_model(z, t, {', '.join(str(s) for s in self.context.odeVariables)}):\n"
        modelstr += f"    dz = [0]*{len(self.context.compartments)}\n"
        modelstr += f"    {', '.join(self.context.compartments.keys())} = z\n"
        for idx, (compartment, formula) in enumerate(self.context.formulas.items()):
            modelstr += f"    dz[{idx}] = {formula} # {compartment}\n"
        modelstr += "    return dz"
        modelcode = compile(modelstr, f"<odeModel>", "exec")
        return FunctionType(modelcode.co_consts[0], globals(), "ode_model")
