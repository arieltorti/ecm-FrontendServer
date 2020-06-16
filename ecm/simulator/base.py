from sympy import sympify, Symbol
from ecm.schemas import Model

RECURSION_DEPTH = 5


class SimulatorError(Exception):
    pass


class SimulationResult:
    def __init__(
        self, compartments, timeline, frames=None, param=None, paramValues=None
    ):
        self.compartments = compartments
        self.timeline = timeline
        self.frames = frames is not None or []
        self.param = param is not None or []
        self.paramValues = paramValues is not None or []

    @property
    def isIterated(self):
        return self.param is not None


class ModelContext:
    @staticmethod
    def unfoldExpression(expressions):
        expressionSymbols = {Symbol(e) for e in expressions.keys()}
        notReduced = {
            e: v
            for e, v in expressions.items()
            if len(v.free_symbols.intersection(expressionSymbols)) > 0
        }
        steps = RECURSION_DEPTH
        while len(notReduced) > 0 and steps >= 0:
            for e in notReduced:
                expressions[e] = expressions[e].subs(expressions)
            notReduced = {
                e: v
                for e, v in notReduced.items()
                if len(expressions[e].free_symbols.intersection(expressionSymbols)) > 0
            }
            steps -= 1
        if len(notReduced) > 0:
            raise SimulatorError(
                "context", "Deep recursion exceeded unfolding expressions."
            )

    def __init__(self, model: Model):
        self.params = {p.name: Symbol(p.name) for p in model.params}

        # initialize expression environment variables
        self.expressionEnv = self.params.copy()
        compartmentsInit = {
            f"{c.name}_0": Symbol(f"{c.name}_0") for c in model.compartments
        }
        self.expressionEnv.update(compartmentsInit)
        expressionsVars = {e.name: Symbol(e.name) for e in model.expressions}
        self.expressionEnv.update(expressionsVars)

        self.expressions = {
            e.name: sympify(e.value, self.expressionEnv) for e in model.expressions
        }
        self.compartments = {c.name: Symbol(c.name) for c in model.compartments}
        self.preconditions = {
            p.predicate: sympify(p.predicate, self.expressionEnv)
            for p in model.preconditions
        }

        # initialize reaction environment variables
        self.reactionEnv = self.expressionEnv.copy()
        self.reactionEnv.update(self.compartments)
        self.reactionEnv["t"] = Symbol("t")
        self.observables = {
            o.name: sympify(o.value, self.reactionEnv) for o in model.observables
        }

        self.__initializeFormulas(model.reactions)

    def __initializeFormulas(self, reactions):
        self.formulas = {x: 0 for x in self.compartments}
        self.odeVariables = set({})
        for reaction in reactions:
            funcExpr = sympify(reaction.function, self.reactionEnv)
            self.odeVariables = self.odeVariables.union(funcExpr.free_symbols)
            self.formulas[reaction.sfrom] -= funcExpr
            self.formulas[reaction.sto] += funcExpr
        self.odeVariables = tuple(
            self.odeVariables.difference(set(self.compartments.values()))
        )
