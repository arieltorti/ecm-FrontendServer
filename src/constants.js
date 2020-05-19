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
  FAILED: 3,
  NONE: 4
};

/** Name of the LocalStorage keys */
export const SIMULATION_MODEL_KEY = "simulationModel";
export const SIMULATION_CONFIG_KEY = "simulationConfig";

export const graphLayout = {
  yaxis: { fixedrange: true }, // Dont allow rectangle zooming
  xaxis: {
    title: "Days",
  },
};
