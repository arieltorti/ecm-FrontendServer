"use strict";

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
  FAILED: 3
};

/** Name of the LocalStorage keys */
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
