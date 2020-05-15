from pathlib import Path
from cms.schemas import Model, Simulation
from cms.builder import Simulator
import json
from pytest import approx

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
    model = Model(**simulation_schema("models/SIR.json"))
    expectedt = [0.0,5.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0]
    expectedData = [
        [999600.0,957254.704,193974.687,5789.445,408.662, 63.507,17.250,6.928,3.659,2.341],
        [400.0,39654.697,688955.907,626406.400,442512.697, 309930.717,216918.056,151801.651,106229.290,74337.418],
        [0.0,3090.598,117069.405,367804.154,557078.640,690005.774,783064.692,848191.419,893767.049,925660.240]
    ]

    simSIR = {
        "step":5,
        "days":50,
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
    columns, tspan, data = sim.simulate(simulation)

    assert columns == ["S","I","R"]
    assert len(tspan) == 10
    assert any(lambda t: expectedt[t] == approx(tspan[t], 0.001) for t in range(10))
    assert len(data[0]) == 3
    assert any(lambda t: expectedData[0][t] == approx(data[0][t], 0.001) for t in range(10))
    assert any(lambda t: expectedData[1][t] == approx(data[1][t], 0.001) for t in range(10))
    assert any(lambda t: expectedData[2][t] == approx(data[2][t], 0.001) for t in range(10))

