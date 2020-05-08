import pandas as pd
from scipy.integrate import odeint
from .base import Model
from types import FunctionType
from numbers import Number

operators = ["+", "-", "*", "/"]


class ParsingError(Exception):
    pass


def eval_function_expr(compartments, variables, farray):
    out = ""
    if type(farray) == list:
        if len(farray) == 0:
            raise ParsingError(
                "eval_function_expr", f"Error parsing {farray}: empty array"
            )
        if farray[0] in operators:
            if len(farray) > 1:
                values = [
                    eval_function_expr(compartments, variables, x) for x in farray[1:]
                ]
                out = f"({farray[0].join(values)})"
            else:
                raise ParsingError(
                    "eval_function_expr", f"Error parsing {farray}: mising parameters"
                )
        else:
            raise ParsingError(
                "eval_function_expr", f"Error parsing {farray}: invalid expression"
            )
    elif type(farray) == str:
        if farray in variables:
            out = farray
        elif farray in compartments.keys():
            out = f"z[{compartments[farray]}]"
        else:
            raise ParsingError(
                "eval_function_expr", f"Error parsing {farray}: variable doesn't exist"
            )
    elif isinstance(farray, Number):
        out = str(farray)
    else:
        raise ParsingError(
            "eval_function_expr", f"Error parsing {farray}: invalid type"
        )

    return out


def build_ode_model_function(schema):
    expressions = {p["name"]: p["value"] for p in schema.get("expressions", [])}
    # TODO: Check recursion of expressions
    variables = [p["name"] for p in schema["params"]]
    variables_with_expr = variables + list(expressions.keys())
    compartments = {x[1]["name"]: x[0] for x in enumerate(schema["compartments"])}
    formulas = {x: "" for x in compartments}

    for reaction in schema["reactions"]:
        expr = eval_function_expr(
            compartments, variables_with_expr, reaction["function"]
        )
        formulas[reaction["from"]] += f"-{expr}"
        formulas[reaction["to"]] += f"+{expr}"

    modelstr = f"def ode_model(z, t, {', '.join(variables)}):\n"

    for exp_name, exp_func in expressions.items():
        expr = eval_function_expr([], variables_with_expr, exp_func)
        modelstr += f"    {exp_name} = {expr}\n"

    modelstr += f"    dz = [0]*{len(compartments)}\n"

    for model, formula in formulas.items():
        modelstr += f"    dz[{compartments[model]}] = {formula}\n"

    modelstr += "    return dz"

    modelcode = compile(modelstr, f"<{schema['name']}>", "exec")

    return FunctionType(modelcode.co_consts[0], globals(), "ode_model")


def build_model(name, schema):
    ode_model = build_ode_model_function(schema)

    def _solve(self):
        res = odeint(
            self.__ode_model, self.initial_conditions, self.tspan, args=self.params,
        )

        res = pd.DataFrame(data=res, columns=self.columns, index=self.tspan)
        return res

    def __ode_model(self, *args):
        return ode_model(*args)

    generated_model = type(
        name,
        (Model, object),
        {
            "columns": [c["name"] for c in schema["compartments"]],
            "param_names": [p["name"] for p in schema["params"]],
            "solve": _solve,
            "__ode_model": __ode_model,
        },
    )
    return generated_model
