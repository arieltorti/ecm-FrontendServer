"use strict";
import * as Plotly from "plotly.js";

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
  NONE: 4,
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

export const toImageButton = {
  name: "toImage",
  title: "Download plot as a png",
  icon: Plotly.Icons.camera,
  click: function(gd) {
    // Remove slider before creating the image
    const oldSlider = gd.layout.sliders;
    gd.layout.sliders = null;

    var toImageButtonOptions = gd._context.toImageButtonOptions;
    var opts = { format: toImageButtonOptions.format || "png" };

    ["filename", "width", "height", "scale"].forEach(function(key) {
      if (key in toImageButtonOptions) {
        opts[key] = toImageButtonOptions[key];
      }
    });

    Plotly.downloadImage(gd, opts).then(() => {
      gd.layout.sliders = oldSlider;
    });
  },
};
