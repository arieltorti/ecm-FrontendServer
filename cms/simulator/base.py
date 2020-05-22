from sympy import sympify, Symbol
from cms.schemas import Model

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
