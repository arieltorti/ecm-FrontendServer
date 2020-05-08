from typing import List, Dict, Iterable, Optional
from pydantic import BaseModel, Field, Json


class Var(BaseModel):
    name: str
    description: str = ""


class Expression(BaseModel):
    name: str
    value: List[Iterable]
    description: str = ""


class Reaction(BaseModel):
    """
    { 
        "from": "Sf",
        "to": "If",
        "function": 
            ["/", ["*", "beta", "F", "Sf", ["+", ["*", "If", "F"], ["*", "Il", "L"]]], "T"],
        "description": ""
    },
    """

    _from = Field(alias="from")
    to: str
    # ((beta * F * Sf * ((If * F) + ( Il * L) / T)
    function: List[Iterable]
    description: str = ""


class Model(BaseModel):
    name: str
    compartments: List[Var]
    expressions: Optional[Json]  # List[Expression]
    params: List[Var]
    reactions: List[Json]  # List[Reaction]


class Simulation(BaseModel):
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
        "iterate": {
            "key": "",
            "step": 1,
            "start": 0,
            "stop": 1
        }
    }
    """

    step: int = 1
    days: int = 365
    initial_conditions: Dict[str, int]
    params: Dict[str, int]


class Payload(BaseModel):
    schemaVersion: int
    simulation: Simulation
    model: Model
