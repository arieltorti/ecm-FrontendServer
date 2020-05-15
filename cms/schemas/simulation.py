from typing import List, Dict, Iterable, Optional
from pydantic import BaseModel, Field, Json

class Var(BaseModel):
    name: str
    default: float
    description: str = ""

class Param(Var):
    iterable: bool

class Expression(BaseModel):
    """
    {
        "name": "T",
        "value": "Noh * H + Nol * L",
        "description": ""
    }
    """
    name: str
    value: str
    description: str = ""

class Iterate(BaseModel):
    """
    {
        "key": "",
        "intervals": 10,
        "start": 0,
        "end": 1
    }
    """

    key: str
    intervals: int
    start: float
    end: float

class Reaction(BaseModel):
    """
    {
        "from": "Sh",
        "to": "Eh",
        "function": "(p * H * Sh * (Ih * H + Il * L)) / T",
        "description": ""
    }
    """

    sfrom: str
    sto: str
    function: str
    description: str = ""

    class Config:
        fields = {
        'sfrom': 'from',
        'sto':'to'
        }

class Model(BaseModel):
    id: Optional[int]
    name: str
    compartments: List[Var]
    expressions: List[Expression] = []
    params: List[Param]
    reactions: List[Reaction]
    preconditions: List[Dict] = []

    class Config:
        orm_mode = True

class Simulation(BaseModel):
    """
    "simulation" : {
        "step" : 10,
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
            "intervals": 10,
            "start": 0,
            "end": 1
        }
    }
    """

    step: float = 1.
    days: float = 365.
    initial_conditions: Dict[str, float]
    params: Dict[str, float]
    iterate: Optional[Iterate]

    class Config:
        orm_mode = True

