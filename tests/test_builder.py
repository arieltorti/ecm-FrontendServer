from models.builder import build_model, build_ode_model_function
from pathlib import Path
from matplotlib import pyplot as plt
import schemas

BASE_PATH = Path(__file__).parent / ".."
STATIC_PATH = BASE_PATH / "static"


def test_sir_splitted_build(simulation_schema):
    filepath = STATIC_PATH / "simulations" / f"sir-splitted-builder.png"
    sir_splitted_schema = simulation_schema("SplittedSEIR.json")
    model_schema = schemas.Model(**sir_splitted_schema["model"])
    model = build_model("SplittedSIR", model_schema)
    simulation = model(**sir_splitted_schema["simulation"])

    results = simulation.solve()
    results.plot()
    plt.grid(True)
    plt.savefig(filepath)
    assert not results.empty
    # assert results[:0] == [599800.000000, 399800.000000, 2.000000e+02, 2.000000e+02, 0.000000, 0.000000]


def test_build_ode_model_function(simulation_schema):
    sir_splitted_schema = simulation_schema("SplittedSEIR.json")
    model_schema = schemas.Model(**sir_splitted_schema["model"])
    model = build_ode_model_function(model_schema)

    assert model
