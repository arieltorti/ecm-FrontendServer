"use strict";

export const defaultIterConfig = {
  from: 0,
  to: 1,
  step: 0.05,
  iteratingVariable: null,
};

export const SIM_STATE = {
  DONE: 0,
  INPROGRESS: 1,
  CANCELED: 2,
  FAILED: 3
};

/** Name of the LocalStorage keys */
export const SIMULATION_MODEL_KEY = "simulationModel";
export const SIMULATION_CONFIG_KEY = "simulationConfig";

/**
 * Finds the name of declared variables in the model.
 * The declarations must be of the form (param <VAR> <VALUE>), ignoring additional whitespaces
 *
 * TODO: Implement a parser and unparser instead of using Regex.
 */
export const VARIABLES_REGEX = new RegExp(/^(?!;).*\(\s*param\s+(\w+)\s+.*\)/, "gm");
