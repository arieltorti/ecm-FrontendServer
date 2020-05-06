from models.builder import build_model, build_ode_model_function
from pathlib import Path
from matplotlib import pyplot as plt

BASE_PATH = Path(".")
STATIC_PATH = BASE_PATH / "static"


def test_sir_splitted_build(sir_splitted_schema):
    filepath = STATIC_PATH / "simulations" / f"sir-splitted-builder.png"

    model = build_model('SplittedSIR', sir_splitted_schema["model"])
    simulation = model(**sir_splitted_schema["simulation"])
    results = simulation.solve()
    results.plot()
    plt.grid(True)
    plt.savefig(filepath)
    assert not results.empty
    # assert results[:0] == [599800.000000, 399800.000000, 2.000000e+02, 2.000000e+02, 0.000000, 0.000000]


def test_build_ode_model_function(sir_splitted_schema):

    model = build_ode_model_function(sir_splitted_schema["model"])

    assert model