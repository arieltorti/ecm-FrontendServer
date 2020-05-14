from pathlib import Path
from cms.schemas import Model, Simulation
from cms.builder import Simulator
import json

BASE_PATH = Path(__file__).parent / ".."
STATIC_PATH = BASE_PATH / "static"


sirModel = """{
    "name": "SIR",
    "compartments": [
        {
            "name": "S",
            "default": 999600.0,
            "description": ""
        },
        {
            "name": "I",
            "default": 400.0,
            "description": ""
        },
        {
            "name": "R",
            "default": 0.0,
            "description": ""
        }
    ],
    "expressions": [
        {
            "name": "N",
            "value": "S_0 + I_0 + R_0"
        }
    ],
    "params": [
        {
            "name": "beta",
            "default": 1,
            "description": "",
            "iterable": true
        },
        {
            "name": "gamma",
            "default": 0.0714,
            "description": "",
            "iterable": true
        }
    ],
    "reactions": [
        {
            "from": "S",
            "to": "I",
            "function": "(beta*S*I)/N",
            "description": ""
        },
        {
            "from": "I",
            "to": "R",
            "function": "gamma*I",
            "description": ""
        }
    ],
    "preconditions": []
}"""

simSIR =""""""

def test_simulator(client, simulation_schema):
    breakpoint()
    model = Model(**json.loads(simulation_schema("SIR.json")))

    simSIR = {
        "step":1,
        "days":365,
        "initial_conditions": {
            "S":999600,
            "I":400,
            "R":0
        },
        "params": {
            "beta":1,
            "gamma":0.0714
        }
    }
    simulation = Simulation(**simSIR)
    sim = Simulator(model)
    result = sim.simulate(simulation)
    assert len(result) > 0
