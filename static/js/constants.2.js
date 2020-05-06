"use strict";

const defaultSimulationModel = `{
  "schemaVersion" : 1,
  "simulation" : {
      "step" : 1,
      "days" : 10,
      "initial_conditions": {
          "S": 999600,
          "I": 400,
          "R": 0
      },
      "params" : {
          "beta": 0.3,
          "gamma": 0.2,
          "N": 1000000
      }
  },
  "model" : {
      "name" : "SIR",
      "compartments" :
      [
          {
              "name": "S",
              "description": ""
          },
          {
              "name": "I",
              "description": ""
          },
          {
              "name": "R",
              "description": ""
          }
      ],
      "params" : [
          {
              "name": "beta",
              "description": ""
          },
          {
              "name": "gamma",
              "description": ""
          },
          {
              "name": "N",
              "description": ""
          }
      ],
      "reactions": [
          {
              "from": "S",
              "to": "I",
              "function": ["/", ["*", "beta", "S", "I"], "N"],
              "description": ""
          },
          {
              "from": "I",
              "to": "R",
              "function": ["*", "gamma", "I"],
              "description": ""
          }
      ]
  }
}`;

const defaultIterConfig = {
  from: 0,
  to: 1,
  step: 0.05,
  iteratingVariable: null,
};

const SIM_STATE = {
  DONE: 0,
  INPROGRESS: 1,
  CANCELED: 2,
};

/** Name of the LocalStorage keys */
const SIMULATION_MODEL_KEY = "simulationModel";
const SIMULATION_CONFIG_KEY = "simulationConfig";
const SIMULATION_ITER_CONFIG_KEY = "simulationIterConfig";

/**
 * Finds the name of declared variables in the model.
 * The declarations must be of the form (param <VAR> <VALUE>), ignoring additional whitespaces
 *
 * TODO: Implement a parser and unparser instead of using Regex.
 */
const VARIABLES_REGEX = new RegExp(/^(?!;).*\(\s*param\s+(\w+)\s+.*\)/, "gm");

const graphLayout = {
  yaxis: { fixedrange: true }, // Dont allow rectangle zooming
  xaxis: {
    title: "Days",
  },
};
