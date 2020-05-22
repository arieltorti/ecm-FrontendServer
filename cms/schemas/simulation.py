from typing import List, Dict, Iterable, Optional
from pydantic import BaseModel, Field, Json, validator, root_validator
from sympy import Symbol, sympify

class Var(BaseModel):
    name: str
    latex: Optional[str]
    default: float
    description: str = ""

class Param(Var):
    iterable: bool

class Precondition(BaseModel):
    predicate: str
    description: str = ""

class Expression(BaseModel):
    """
    {
        "name": "T",
        "value": "Noh * H + Nol * L",
        "description": ""
    }
    """
    name: str
    latex: Optional[str]
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

    @validator('intervals')
    def intervals_positive(cls, intervals):
        assert intervals > 0, "intervals must be greather than zero"
        return intervals

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
    preconditions: List[Precondition] = []

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
        },
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

    @validator('days')
    def days_gt_1(cls, days):
        assert days > 0, "must be greather than zero"
        return days

    @validator('step')
    def step_gt_1(cls, step):
        assert step > 0, "must be greather than zero"
        return step

    @validator('initial_conditions')
    def initial_conditions_gte_0(cls, initial_conditions):
        for k, v in initial_conditions.items():
            assert v >= 0, f"{k} can't be negative"
        return initial_conditions

    @root_validator(skip_on_failure=True)
    def check_passwords_match(cls, values):
        days, step = values.get('days'), values.get('step')
        assert step <= days, "steps <= days"
        return values

    class Config:
        orm_mode = True

