from ecm.schemas import Model
from .simulator import ModelContext
import re
from sympy import Symbol
from sympy.printing.latex import latex


def normZero(var):
    out = f"{var}_0"
    expr = re.compile(r"(?P<start>.*)_(?P<suffix>\w|\{\w+\})$")
    match = expr.match(var)
    if match:
        out = f"{match.group('start')}_{{{match.group('suffix')}0}}"
    return out


def modelExtendedLatex(model: Model):
    simulator = ModelContext(model)
    out = model.dict()

    symbols = {Symbol(x.name): x.latex for x in model.compartments if x.latex}
    symbols.update({Symbol(x.name): x.latex for x in model.params if x.latex})
    symbols.update({Symbol(x.name): x.latex for x in model.expressions if x.latex})
    symbols.update(
        {
            Symbol(f"{c.name}_0"): normZero(c.latex)
            for c in model.compartments
            if c.latex
        }
    )

    # generate equations latex
    out["equations"] = []
    for compartment, formula in simulator.formulas.items():
        out["equations"].append(
            {
                "nameLatex": "\\frac{d %s}{d t}"
                % latex(Symbol(compartment), symbol_names=symbols),
                "valueLatex": latex(formula, symbol_names=symbols),
            }
        )

    # update params latex
    for idx, param in enumerate(model.params):
        out["params"][idx]["nameLatex"] = latex(Symbol(param.latex or param.name))

    # update compartments latex
    for idx, compartment in enumerate(model.compartments):
        out["compartments"][idx]["nameLatex"] = latex(
            Symbol(compartment.latex or compartment.name)
        )
        out["compartments"][idx]["initLatex"] = latex(
            Symbol(normZero(compartment.latex or compartment.name))
        )

    # update observables latex
    if simulator.observables:
        for idx, (name, observable) in enumerate(simulator.observables.items()):
            out["observables"][idx]["nameLatex"] = "%s" % latex(
                Symbol(name), symbol_names=symbols
            )
            out["observables"][idx]["valueLatex"] = latex(
                observable, symbol_names=symbols
            )

    # update expressions latex
    if simulator.expressions:
        for idx, (name, expression) in enumerate(simulator.expressions.items()):
            out["expressions"][idx]["nameLatex"] = "%s" % latex(
                Symbol(name), symbol_names=symbols
            )
            out["expressions"][idx]["valueLatex"] = latex(
                expression, symbol_names=symbols
            )

    return out
