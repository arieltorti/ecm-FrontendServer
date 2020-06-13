from ecm.schemas import Model, Simulation
from ecm.simulator import ModelContext, Simulator, SimulatorError, modelExtendedLatex, computeExtraColumns
import json
from pytest import approx, raises

def test_sim_basic(client, simulation_schema):
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
    context = ModelContext(model)
    sim = Simulator(ModelContext(model))
    result = sim.simulate(simulation)

    assert result.compartments == ["S","I","R"]
    assert len(result.timeline) == 10
    assert any(lambda t: expectedt[t] == approx(result.timeline[t], 0.001) for t in range(10))
    assert len(result.frames) == 1
    assert len(result.frames[0][0]) == 3
    assert any(lambda t: expectedData[0][t] == approx(result.frames[0][0][t], 0.001) for t in range(10))
    assert any(lambda t: expectedData[1][t] == approx(result.frames[0][1][t], 0.001) for t in range(10))
    assert any(lambda t: expectedData[2][t] == approx(result.frames[0][2][t], 0.001) for t in range(10))

def test_sim_missing_compartment(client, simulation_schema):
    model = Model(**simulation_schema("models/SIR.json"))

    simSIR = {
        "step":5,
        "days":50,
        "initial_conditions": {
            "S":999600,
            "I":400
        },
        "params": {
            "beta":1,
            "gamma":0.0714
        }
    }
    simulation = Simulation(**simSIR)
    sim = Simulator(ModelContext(model))
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Missing initialization for compartment 'R'"

def test_sim_missing_parameter(client, simulation_schema):
    model = Model(**simulation_schema("models/SIR.json"))

    simSIR = {
        "step":5,
        "days":50,
        "initial_conditions": {
            "S":999600,
            "I":400,
            "R":0
        },
        "params": {
            "beta":1
        }
    }
    simulation = Simulation(**simSIR)
    sim = Simulator(ModelContext(model))
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Missing parameter 'gamma'"

def test_sim_model_cannot_solve_symbols(client, simulation_schema):
    modelData = simulation_schema("models/SIR.json")
    modelData["expressions"] = [
        { "name": "N", "value": "S+1" },
        { "name": "S", "value": "N+1" }
    ]

    model = Model(**modelData)
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
    context = ModelContext(model)
    sim = Simulator(context)
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Deep recursion exceeded unfolding expressions."

def test_sim_model_cannot_solve_preconditions(client, simulation_schema):
    modelData = simulation_schema("models/SIR.json")
    modelData["preconditions"] = [
        { "predicate": "(omega + N) > 2" }
    ]

    model = Model(**modelData)
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
    sim = Simulator(ModelContext(model))
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Cannot solve precondition [(omega + N) > 2]: omega + 1000000.0 > 2"

def test_sim_precondition_error_1(client, simulation_schema):
    model = Model(**simulation_schema("models/SIR.json"))
    simSIR = {
        "step":5,
        "days":50,
        "initial_conditions": {
            "S":999600,
            "I":400,
            "R":0
        },
        "params": {
            "beta":-1,
            "gamma":0.0714
        }
    }
    simulation = Simulation(**simSIR)
    sim = Simulator(ModelContext(model))
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Precondition not satisisfied: beta >= 0"

def test_sim_precondition_error_animate(client, simulation_schema):
    model = Model(**simulation_schema("models/SIR.json"))
    simSIR = {
        "step":5,
        "days":50,
        "initial_conditions": {
            "S":999600,
            "I":400,
            "R":0
        },
        "params": {
            "beta":0,
            "gamma":0.0714
        },
        "iterate": {
            "key": "beta",
            "intervals": 10,
            "start": 10,
            "end": -10
        }
    }
    simulation = Simulation(**simSIR)
    sim = Simulator(ModelContext(model))
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Precondition not satisisfied: beta >= 0"

def test_sim_to_latex(client, simulation_schema):
    model = Model(**simulation_schema("models/SIR-HL.json"))
    modelDict = modelExtendedLatex(model)
    
    assert modelDict["compartments"][0]["nameLatex"] == "S_{l}"
    assert modelDict["compartments"][0]["initLatex"] == "S_{l0}"
    assert modelDict["params"][1]["nameLatex"] == "\\gamma"
    assert modelDict["equations"][0] == {
        'nameLatex': '\\frac{d S_l}{d t}', 
        'valueLatex': '- \\frac{L S_l p \\left(H I_h + I_l L\\right)}{T}'
    }

def test_process_observables(client, simulation_schema):
    model = Model(**simulation_schema("models/SIR-HL.json"))
    simSIR = {
        "step":1,
        "days":365,
        "initial_conditions": {
            "Sl":599800,
            "Sh":399800,
            "Il":200,
            "Ih":200,
            "Rl":0,
            "Rh":0
        },
        "params": {
            "p":0.1818,
            "gamma":0.0714,
            "H":10,
            "L":1,
            "Noh":400000,
            "Nol":600000
        }
    }
    simulation = Simulation(**simSIR)
    context = ModelContext(model)
    sim = Simulator(context)
    result = sim.simulate(simulation)
    computeExtraColumns(context, result)
    assert True
