import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt

from models import SIR, SplittedSEIR


BASE_PATH = Path(".")
STATIC_PATH = BASE_PATH / "static"

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


def test_simulate_sir():
    filepath = STATIC_PATH / "simulations" / f"sir-model-test.png"

    data = {
        "initial_conditions": [initS, initI, initR],
        "params": [beta, gamma, N],
        "tspan": np.arange(0, days, 1),
    }
    model = SIR(**data)
    results = model.solve()
    results.plot()
    plt.grid(True)
    plt.savefig(filepath)
    assert not results.empty


def test_simulate_seir():
    filepath = STATIC_PATH / "simulations" / f"seir-model-test.png"

    data = {
        "initial_conditions": [
            initSl,
            initSf,
            initEl,
            initEf,
            initIl,
            initIf,
            initRl,
            initRf,
        ],
        "params": [beta, gamma, sigma, F, L, Nof, Nol],
        "tspan": np.arange(0, days, 1),
    }
    model = SplittedSEIR(**data)
    results = model.solve()
    results.plot()
    plt.grid(True)
    plt.savefig(filepath)
    assert not results.empty
