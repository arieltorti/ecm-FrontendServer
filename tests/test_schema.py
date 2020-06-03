from ecm.schemas import Simulation

from pytest import raises
from pydantic import ValidationError


def test_schema_simulation_invalid_step(client, simulation_schema):
    simSIR = {
        "step": -5,
        "days": 50,
        "initial_conditions": {"S": 999600, "I": 400, "R": 0},
        "params": {"beta": 1, "gamma": 0.0714},
    }
    with raises(ValidationError):
        Simulation(**simSIR)


def test_schema_simulation_invalid_days(client, simulation_schema):
    simSIR = {
        "step": 5,
        "days": -1,
        "initial_conditions": {"S": 999600, "I": 400, "R": 0},
        "params": {"beta": 1, "gamma": 0.0714},
    }
    with raises(ValidationError):
        Simulation(**simSIR)


def test_schema_simulation_invalid_step_gt_days(client, simulation_schema):
    simSIR = {
        "step": 500,
        "days": 50,
        "initial_conditions": {"S": 999600, "I": 400, "R": 0},
        "params": {"beta": 1, "gamma": 0.0714},
    }
    with raises(ValidationError):
        Simulation(**simSIR)


def test_schema_simulation_invalid_initial_conditions(client, simulation_schema):
    simSIR = {
        "step": 5,
        "days": 50,
        "initial_conditions": {"S": -999600, "I": 400, "R": 0},
        "params": {"beta": 1, "gamma": 0.0714},
    }
    with raises(ValidationError):
        Simulation(**simSIR)


def test_schema_simulation_iterate_interval_negative(client, simulation_schema):
    simSIR = {
        "step": 5,
        "days": 50,
        "initial_conditions": {"S": -999600, "I": 400, "R": 0},
        "params": {"beta": 1, "gamma": 0.0714},
        "iterate": {"key": "beta", "intervals": -10, "start": 0, "end": 10},
    }
    with raises(ValidationError):
        Simulation(**simSIR)
