
from typing import List, Optional, Dict
from pydantic import BaseModel
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
    observables: List[Expression] = []
    expressions: List[Expression] = []
    params: List[Param]
    reactions: List[Reaction]
    preconditions: List[Precondition] = []
    template: Optional[Dict]

    class Config:
        orm_mode = True