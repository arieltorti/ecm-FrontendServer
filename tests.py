import pytest
import json
import numpy as np

from app import create_app

initSl = 599800
initSf = 399800
initS = initSl + initSf

initEl = 0
initEf = 0
initE = initEf + initEl

initIl = 200
initIf = 200
initI = initIf + initIl

initRl = 0
initRf = 0
initR = initRf + initRl

beta = 0.3
gamma = 0.2
sigma = 0.14

Nof = 400000
Nol = 600000
N = Nof + Nol

F = 8
L = 1
D = 0

days = 365


@pytest.fixture
def app():
    return create_app()


def test_animate(client):
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {
        "initial_conditions": [initS, initI, initR],
        "params": [beta, gamma, N],
        "tspan": np.arange(0, days, 1).tolist(),
    }
    url = "/animate/sir/"
    breakpoint()
    response = client.post("/animat", data=json.dumps(data), content_type=mimetype)
    print(response)
    assert response
