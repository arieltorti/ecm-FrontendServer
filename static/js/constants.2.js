"use strict";

const defaultSimulationModel = `; simplemodel

(import (rnrs) (emodl cmslib))

(start-model "seir.emodl")

(species S 990)
(species E)
(species I 10)
(species R)

(observe susceptible S)
(observe exposed     E)
(observe infectious  I)
(observe recovered   R)

(param Ki 0.0005)
(param Kl 0.2)
(param Kr (/ 1 7))

(reaction exposure   (S I) (E I) (* Ki S I))
(reaction infection  (E)   (I)   (* Kl E))
(reaction recovery   (I)   (R)   (* Kr I))

(end-model)`;

const defaultConfigText = `{
    "duration" : 365,
    "runs" : 1,
    "samples" : 365,
    "solver" : "R",
    "output" : {
        "headers" : true
    },
    "tau-leaping" : {
        "epsilon" : 0.01
    },
    "r-leaping" : {}
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

const EPSILON = 0.0000001;

const VCStates = {
  IDLE: 1,
  INPROGRESS: 2,
  STOP: 3,
  DONE: 4,
};

const requestAnimationFrame =
  window.requestAnimationFrame ||
  window.mozRequestAnimationFrame ||
  window.webkitRequestAnimationFrame ||
  window.msRequestAnimationFrame;
window.requestAnimationFrame = requestAnimationFrame;
