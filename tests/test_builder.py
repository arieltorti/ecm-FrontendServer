from cms.schemas import Model, Simulation
from cms.builder import Simulator, SimulatorError
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
    sim = Simulator(model)
    columns, tspan, data = sim.simulate(simulation)

    assert columns == ["S","I","R"]
    assert len(tspan) == 10
    assert any(lambda t: expectedt[t] == approx(tspan[t], 0.001) for t in range(10))
    assert len(data[0]) == 3
    assert any(lambda t: expectedData[0][t] == approx(data[0][t], 0.001) for t in range(10))
    assert any(lambda t: expectedData[1][t] == approx(data[1][t], 0.001) for t in range(10))
    assert any(lambda t: expectedData[2][t] == approx(data[2][t], 0.001) for t in range(10))


    #assert e.value.args[1] == "Missing initialization for compartment 'R'"

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
    sim = Simulator(model)
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
    sim = Simulator(model)
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
    sim = Simulator(model)
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Cannot solve symbols: [N + 2]"

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
    sim = Simulator(model)
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
    sim = Simulator(model)
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Precondition not satisisfied: (beta <= 1) & (beta > 0)"

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
            "start": 0.2,
            "end": 10
        }
    }
    simulation = Simulation(**simSIR)
    sim = Simulator(model)
    with raises(SimulatorError) as e:
        sim.simulate(simulation)
    assert e.value.args[1] == "Precondition not satisisfied: (beta <= 1) & (beta > 0)"