"use strict";

const app = new Vue({
  el: "#app",
  data: {
    simulationModel: localStorage.getItem(SIMULATION_MODEL_KEY) || defaultSimulationModel,
    simulationConfig: localStorage.getItem(SIMULATION_CONFIG_KEY) || defaultConfigText,
    errorMsg: null,
    statusMsg: null,

    preciseDecimalPlaces: 6,

    intervalConfig: {
      from: 0,
      to: 1,
      step: 0.05,
      iteratingVariable: null,

      totalSteps: null,
      currentStep: null,
    },
    graphHistoricData: [],
  },

  computed: {
    modelVariables: function () {
      return _extractModelVariables(this.simulationModel);
    },
  },

  watch: {
    simulationModel: function (val) {
      localStorage.setItem(SIMULATION_MODEL_KEY, val);
    },
    simulationConfig: function (val) {
      localStorage.setItem(SIMULATION_CONFIG_KEY, val);
    },
  },

  methods: {
    handleError: function (error) {
      console.error(error);
      this.setError(error.message);
    },
    setError: function (message) {
      this.errorMsg = "[ERROR]: " + message;
      this.statusMsg = null;
    },
    setStatus: function (message) {
      this.errorMsg = null;
      this.statusMsg = message;
    },

    selectVariable: function (event) {
      this.intervalConfig.iteratingVariable = event.target.value;
    },

    reset: function (event) {
      this.simulationModel = defaultSimulationModel;
      this.simulationConfig = defaultConfigText;
    },

    simulate: function () {
      {
        if (this.intervalConfig.iteratingVariable != null) {
          // If we selected an interating variable send as many request as needed chaining them
          // to avoid overloading the server.
          let promiseChain = Promise.resolve();

          this.intervalConfig.totalSteps =
            1 +
            this._preciseRound(this.intervalConfig.to - this.intervalConfig.from, 2) /
              this.intervalConfig.step;
          this.intervalConfig.currentStep = 0;

          for (
            let from = this.intervalConfig.from;
            from <= this.intervalConfig.to;
            from = this._preciseRound(from + this.intervalConfig.step)
          ) {
            this.graphHistoricData = [];
            promiseChain = promiseChain.then(() => {
              this.intervalConfig.currentStep += 1;
              return this._simulate(
                this.simulationConfig,
                _replaceModelVariableValue(this.simulationModel, this.intervalConfig.iteratingVariable, from),
                from
              );
            });
          }

          promiseChain.then(() => this.dataFetchingDone()).catch((err) => this.handleError(err));
        } else {
          this.intervalConfig.totalSteps = this.intervalConfig.currentStep = 1;
          this._simulate(this.simulationConfig, this.simulationModel)
            .then(() => this.dataFetchingDone())
            .catch((err) => this.handleError(err));
        }
      }
    },
    _simulate: function (config, model, iterVarValue) {
      const formData = new FormData();
      this.setStatus(`Simulating... ${this.intervalConfig.currentStep}/${this.intervalConfig.totalSteps}`);

      formData.append("config", config);
      formData.append("model", model);

      const req = fetch("/api/compute", {
        method: "POST",
        body: formData,
      });

      return req
        .then((resp) => {
          if (resp.status >= 400 && resp.status < 600) {
            resp.text().then((data) => this.setError(data));
            throw resp;
          }
          return resp.json();
        })
        .then((data) => {
          const graphData = makeGraphData(data);
          graphData._iterVal = iterVarValue;
          this.graphHistoricData.push(graphData);
          this.setStatus(null);
        });
    },

    /** Precisely rounds number based on the number of significant decimal places */
    _preciseRound: function (number, presicion = this.preciseDecimalPlaces) {
      return Math.round((number + Number.EPSILON) * Math.pow(10, presicion)) / Math.pow(10, presicion);
    },
    dataFetchingDone: function () {
      /**
       * We have a ton of boilerplate here just to configure the slider and animations
       * as we have to rebuild them all everytime the data changes. In the future we could
       * migrate to using addFrames and resize/relayout instead.
       */

      // Configure the number and style of the slider steps
      var sliderSteps = [];
      for (let i = 0; i < this.graphHistoricData.length; i++) {
        sliderSteps.push({
          method: "animate",
          label: this.graphHistoricData[i]._iterVal || i,
          args: [
            [i],
            {
              mode: "next",
              transition: { duration: 400, easing: "linear" },
              frame: { duration: 800, redraw: true },
            },
          ],
        });
      }

      const slider = [
        {
          pad: { l: 130, t: 55 },
          active: this.graphHistoricData.length - 1,
          steps: sliderSteps,
        },
      ];

      var frames = [];
      for (let i = 0; i < this.graphHistoricData.length; i++) {
        frames.push({
          name: i,
          data: this.graphHistoricData[i],
        });
      }

      // Plotly mutates the initial data given, hence not allowing us to animate back
      // to the initial frame. We deeply copy the initial data object to avoid this issue.
      const data = JSON.parse(JSON.stringify(this.graphHistoricData[0]));

      Plotly.newPlot("plotDiv", {
        data: data,
        layout: { ...graphLayout, sliders: slider },
        frames: frames,
        config: plotConfig,
      }).then(() => {
        Plotly.animate("plotDiv", [this.graphHistoricData.length - 1]); // Animate to last frame.
      });
    },
  },
});

function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Returns a new simulation model where the selected variable value is replaced
 * by the new value.
 *
 * @param {*} model Simulation model string
 * @param {*} variable Variable name
 * @param {*} value New value
 */
function _replaceModelVariableValue(model, variable, value) {
  const singleVariableRegex = new RegExp(
    `^(?!;)(.*\\(\\s*param\\s+${escapeRegExp(variable)}\\s+)(.*)\s*(\\))`,
    "gm"
  );
  return model.replace(singleVariableRegex, `$1${value}$3`);
}

/**
 * Returns a list of the names of all declared variables on the model
 *
 * @param {*} model Simulation model string
 */
function _extractModelVariables(model) {
  // We could use matchAll, but as we're not using a transpiler and someone may use this on IE11
  // we'll do it the old way instead.
  let match;
  const variables = [];
  while ((match = VARIABLES_REGEX.exec(model)) != null) {
    variables.push(match[1]);
  }
  return variables;
}

/**
 * Returns current date formatted as YYYYmmdd-HHMMss
 */
function getCurrentDate() {
  function pad(string) {
    return ("0" + string).slice(0, 2);
  }

  const now = new Date();
  const month = pad(now.getMonth() + 1);
  const day = pad(now.getDate());
  const hours = pad(now.getHours());
  const minutes = pad(now.getMinutes());
  const seconds = pad(now.getSeconds());
  return `${now.getUTCFullYear()}${month}${day}-${hours}${minutes}${seconds}`;
}

function downloadLink(href) {
  const linkEl = document.createElement("a");
  linkEl.setAttribute("href", href);
  linkEl.setAttribute("download", `sim-${getCurrentDate()}.csv`);

  document.body.appendChild(linkEl);
  linkEl.click();
  linkEl.remove();
}

/**
 * Generates transposed CSV content
 *
 * @param {*} plotData
 */
function generateCSV(plotData) {
  const csvHeader = "sampletimes," + plotData.data.map((x) => x.name).join(",");
  const sampleTimes = plotData.data[0].x;
  const data = plotData.data.map((x) => x.y);

  let csv = csvHeader + "\r\n";
  for (let i = 0; i < sampleTimes.length; i++) {
    csv += sampleTimes[i] + "," + data.map((x) => x[i]).join(",") + "\n";
  }

  const CSVBlob = new Blob([csv], { type: "text/csv" });
  downloadLink(window.URL.createObjectURL(CSVBlob));
}

const exportAsCSVBtn = {
  name: "Export as CSV",
  icon: Plotly.Icons.disk,
  click: function (gd) {
    generateCSV(gd);
  },
};

const plotConfig = {
  displaylogo: false,
  modeBarButtons: [
    [exportAsCSVBtn],
    [
      "toImage",
      "zoom2d",
      "zoomIn2d",
      "zoomOut2d",
      "autoScale2d",
      "hoverClosestCartesian",
      "hoverCompareCartesian",
    ],
  ],
  modeBarButtonsToRemove: ["pan2d", "resetScale2d", "sendDataToCloud"],
};

/**
 * Extract graph data from JSON request output
 *
 * @param {*} data
 */
function makeGraphData(data) {
  const xAxis = data.SampleTimes;
  const graphData = [];

  for (let i = 0; i < data.ChannelData.length; i++) {
    graphData.push({
      x: xAxis,
      y: data.ChannelData[i],
      name: data.ObservableNames[i],
    });
  }

  return graphData;
}
