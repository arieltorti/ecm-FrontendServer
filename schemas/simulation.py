from marshmallow import Schema, fields


class Var(Schema):
    name = fields.String()
    description = fields.String(default="")


class Reaction(Schema):
    """
    { 
        "from": "Sf",
        "to": "If",
        "function": 
            ["/", ["*", "beta", "F", "Sf", ["+", ["*", "If", "F"], ["*", "Il", "L"]]], "T"],
        "description": ""
    },
    """

    _from = fields.String(data_key="from")
    to = fields.String()
    # ((beta * F * Sf * ((If * F) + ( Il * L) / T)
    function = fields.List(fields.List)


class Model(Schema):
    name = fields.String()
    compartments = fields.List(Var)
    params = fields.List(Var)
    reactions = fields.List(Reaction)


class Simulation(Schema):
    """
    "simulation" : {
        "step" : 1,
        "days" : 365,
        "initial_conditions": {
            "Sl": 599800,
            "Sf": 399800,
            "Il": 200,
            "If": 200,
            "Rl": 0,
            "Rf": 0
        },
        "params" : {
            "beta": 0.05,
            "gamma": 0.2,
            "F": 8,
            "L": 1,
            "T": 3800000
        }
    }
    """

    step = fields.Integer(default=1)
    days = fields.Integer(default=365)
    initial_conditions = fields.Dict(
        keys=fields.String, values=fields.Integer, required=True
    )
    params = fields.Dict(keys=fields.String, values=fields.Number, required=True)
