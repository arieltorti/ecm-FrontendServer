Vue.component("simulation", {
  props: ["sim", "simCancel", "simState"],
  data: function () {
    return {
      SIM_STATE: SIM_STATE,
      graphHistoricData: [],
      stats: {
        totalSteps: null,
        currentStep: null,
      },

      abortSignal: null, // Stores the signal to abort the current request
      playing: false,
    };
  },
  computed: {
    isMultiple: function() {
      return this.sim.simulation.iterate.key != null;
    }
  },
  watch: {
    sim: function (_sim) {
      _sim != null && this.simulate();
    },
    simCancel: function (stop) {
      if (stop) {
        this.abortSignal.abort();
        this.$emit("sim-cancel");
      }
    },
  },
  methods: {
    handleError: function (err) {
      if (err.ABORT_ERR && err.code === err.ABORT_ERR) {
        console.log("Request aborted");
      } else {
        console.error(err);
      }
    },

    stop: function () {},

    _play: function () {
      Plotly.animate("plotDiv", null, {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: 300 },
        frame: { duration: 500, redraw: false },
      }).then(() => (this.playing = false));
    },
    _pause: function () {
      Plotly.animate("plotDiv", [null], {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: 0 },
        frame: { duration: 0, redraw: false },
      });
    },

    handleAnimClick: function () {
      if (this.playing) {
        this._pause();
      } else {
        this._play();
      }
      this.playing = !this.playing;
    },

    simulate: function () {
      if (this.sim == null) {
        return;
      }

      console.log("Simulating", this.sim);
      this.$emit("sim-start");
      this.graphHistoricData = [];

      const simulation = JSON.parse(JSON.stringify(this.sim.simulation));
      if (this.isMultiple) {
        if (this.sim.simulation.iterate.step === 0) {
          return;
        }
      } else {
        delete simulation.iterate;
      }
      //this.stats.totalSteps = this.stats.currentStep = 1;
      this._simulate({simulation: simulation, model: this.sim.model})
        .then(() => this.dataFetchingDone())
        .catch((err) => this.handleError(err));

    },
    _simulate: function (model) {
      const controller = new AbortController();
      const signal = controller.signal;
      this.abortSignal = controller;

      const req = fetch("/simulate/"+model.model.id, {
        headers: {
          'Accept': 'application/json, text/plain, */*',
          'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(model),
        signal,
      });

      return req
        .then((resp) => {
          if (resp.status >= 400 && resp.status < 600) {
            throw resp;
          }
          return resp.json();
        })
        .then((data) => {
          if (this.isMultiple) {
            data.forEach((d, i) => {
              const graphData = makeGraphData(d);
              graphData._iterVal = i;
              this.graphHistoricData.push(graphData);
            });
          } else {
            const graphData = makeGraphData(data);
            graphData._iterVal = 0;
            this.graphHistoricData.push(graphData);
          }
        });
    },

    /** Precisely rounds number based on the number of significant decimal places */
    _preciseRound: function (number, presicion = 7) {
      return Math.round((number + Number.EPSILON) * Math.pow(10, presicion)) / Math.pow(10, presicion);
    },
    _getIndexAsString: function (i) {
      return "" + this.graphHistoricData[i]._iterVal || i;
    },
    dataFetchingDone: function () {
      /**
       * We have a ton of boilerplate here just to configure the slider and animations
       * as we have to rebuild them all everytime the data changes. In the future we could
       * migrate to using addFrames and resize/relayout instead.
       */

      this.$emit("sim-done");

      // Configure the number and style of the slider steps
      var sliderSteps = [];
      for (let i = 0; i < this.graphHistoricData.length; i++) {
        sliderSteps.push({
          method: "animate",
          label: this._getIndexAsString(i), // Convert to string, plotly behaves weird
          // when using floats.
          args: [
            [this._getIndexAsString(i)],
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
          steps: sliderSteps,
        },
      ];

      var frames = [];
      for (let i = 0; i < this.graphHistoricData.length; i++) {
        frames.push({
          name: this._getIndexAsString(i),
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
      });
    },
  },
  // We use v-once on the #plotDiv element to avoid vue re-rendering it and disrupting plotly   
  template: `<div style="position: relative">
    <div class="progress" v-if="simState === SIM_STATE.INPROGRESS">
        Simulating
    </div>
    <div id="plotDiv" v-once></div>
    <div v-if="simState === SIM_STATE.DONE && isMultiple" id="plotAnimDiv">
        <button @click="handleAnimClick">{{ playing ? "| |" : "▶" }}</button>
    </div>
  </div>`,
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
  model.simulation.params[variable] = value;
  return model;
}

/**
 * Returns a list of the names of all declared variables on the model
 *
 * @param {*} model Simulation model string
 */
function _extractModelVariables(model) {
  let out = [];
  try {
    out = JSON.parse(model).model.params.map(x => x.name);
  } catch (e) {
    console.error(e);
  }
  return out;
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
  const xAxis = data.columns;
  const graphData = [];

  for (let i = 0; i < data.data.length; i++) {
    graphData.push({
      x: xAxis,
      y: data.data[i],
      name: data.index[i],
    });
  }

  return graphData;
}