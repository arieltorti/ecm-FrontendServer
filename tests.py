import pytest
import numpy as np

from app import app as application
from models import SIR, SplittedSEIR
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
    return application


def test_simulate_endpoint(client):
    mimetype = "application/json"

    data = {
        "initial_conditions": [initS, initI, initR],
        "params": [beta, gamma, N],
        "tspan": np.arange(0, days, 1).tolist(),
    }
    url = "/simulate/sir"
    response = client.post(url, json=data, content_type=mimetype)
    assert response.status_code == 200


def test_simulate_sir():

    data = {
        "initial_conditions": [initS, initI, initR],
        "params": [beta, gamma, N],
        "tspan": np.arange(0, days, 1)
    }
    model = SIR(**data)
    res = model.solve()
    assert not res.empty



def test_simulate_seir():
    data = {
        "initial_conditions": [initSl, initSf, initEl, initEf, initIl, initIf, initRl, initRf],
        "params": [beta, gamma, sigma, F, L, Nof, Nol],
        "tspan": np.arange(0, days, 1)
    }
    model = SplittedSEIR(**data)
    res = model.solve()
    assert not res.empty
