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
    expressions = {
        p["name"]: p["value"] for p in schema.expressions
    }  # XXX: Expression type needs revision
    # TODO: Check recursion of expressions
    variables = [p.name for p in schema.params]
    variables_with_expr = variables + list(expressions)
    compartments = {var.name: i for i, var in enumerate(schema.compartments)}
    formulas = {x: "" for x in compartments}

    for reaction in schema.reactions:  # XXX: Reaction type needs revision
        expr = eval_function_expr(
            compartments, variables_with_expr, reaction["function"]
        )
        formulas[reaction["from"]] += f"-{expr}"
        formulas[reaction["to"]] += f"+{expr}"

    modelstr = f"def ode_model(z, t, {', '.join(variables)}):\n"

    for exp_name, exp_func in expressions.items():
        expr = eval_function_expr({}, variables_with_expr, exp_func)
        modelstr += f"    {exp_name} = {expr}\n"

    modelstr += f"    dz = [0]*{len(compartments)}\n"

    for model, formula in formulas.items():
        modelstr += f"    dz[{compartments[model]}] = {formula}\n"

    modelstr += "    return dz"
    print(modelstr)
    modelcode = compile(modelstr, f"<{schema.name}>", "exec")

    return FunctionType(modelcode.co_consts[0], globals(), "ode_model")

