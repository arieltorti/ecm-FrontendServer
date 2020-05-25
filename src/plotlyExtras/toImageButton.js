"use strict";
import * as Plotly from "plotly.js";

export function extractSimulationInfo(sim) {
  function getLatexValue(name) {
    const matchingVar = variablePool.find((el) => el.name === name);

    if (matchingVar == null) {
      return null;
    }

    return `${matchingVar.nameLatex}`;
  }

  const { model, simulation } = sim;
  const variablePool = [
    ...model.compartments,
    ...model.expressions,
    ...model.observables,
    ...model.params,
  ];

  let text = String.raw`\text{Model: ${model.name} - Days: ${simulation.days}} \\
\begin{array}{c}`;

  text += String.raw`\begin{array}{cc}`;
  for (const [key, value] of Object.entries(simulation.params || {})) {
    const latexName = getLatexValue(key);
    if (latexName != null) {
      text += String.raw`${latexName} & ${value} \\`;
    }
  }
  text += String.raw`\end{array}
  &`;

  text += String.raw`\begin{array}{cc} \\`;
  for (const [key, value] of Object.entries(
    simulation.initial_conditions || {}
  )) {
    const latexName = getLatexValue(key);
    if (latexName != null) {
      text += String.raw`${latexName} & ${value} \\`;
    }
  }
  text += String.raw`\end{array} \end{array}`;

  return text;
}

export function getImageButton(callback) {
  return {
    name: "toImage",
    title: "Download plot as a png",
    icon: Plotly.Icons.camera,
    click: callback,
  };
}
