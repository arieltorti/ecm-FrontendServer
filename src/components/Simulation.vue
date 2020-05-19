<template>
  <div style="position: relative">
    <div class="progress" v-if="simState === SIM_STATE.INPROGRESS">Simulating</div>
    <div class="errorMsg" v-if="simState === SIM_STATE.FAILED">Error: {{ errMsg }}</div>
    <div v-bind:class="{ hidden: isNotDone }">
      <div id="plotDiv" v-once></div>
      <button id="downloadCSV" @click="downloadCSV">Download CSV</button>
    </div>
    <div v-if="simState === SIM_STATE.DONE && isMultiple" id="plotAnimDiv">
      <button @click="handleAnimClick">{{ playing ? "| |" : "▶" }}</button>
    </div>
  </div>
</template>
<script>
import { SIM_STATE, graphLayout } from "../constants.js";
import * as Plotly from "plotly.js";

export default {
  props: ["sim", "simCancel", "simState"],
  data: function() {
    return {
      SIM_STATE: SIM_STATE,
      graphHistoricData: [],
      stats: {
        totalSteps: null,
        currentStep: null
      },
      errMsg: "",
      abortSignal: null, // Stores the signal to abort the current request
      playing: false
    };
  },
  computed: {
    isMultiple: function() {
      return this.sim && this.sim.simulation.iterate.key != null;
    },
    isNotDone: function() {
      return this.simState !== SIM_STATE.DONE;
    }
  },
  watch: {
    sim: function(_sim) {
      _sim != null && this.simulate();
    },
    simCancel: function(stop) {
      if (stop) {
        this.abortSignal.abort();
        this.$emit("sim-cancel");
      }
    }
  },
  methods: {
    downloadCSV: function() {
      generateCSV(this.graphHistoricData, this.isMultiple);
    },
    handleError: function(err) {
      if (err.ABORT_ERR && err.code === err.ABORT_ERR) {
        console.log("Request aborted");
        this.$emit("sim-cancel");
      } else {
        err.json().then(e => {
          this.errMsg = e.error;
        });
        this.$emit("sim-error");
      }
    },

    stop: function() {},

    _play: function() {
      Plotly.animate("plotDiv", null, {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: 300 },
        frame: { duration: 500, redraw: false }
      }).then(() => (this.playing = false));
    },
    _pause: function() {
      Plotly.animate("plotDiv", [null], {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: 0 },
        frame: { duration: 0, redraw: false }
      });
    },

    handleAnimClick: function() {
      if (this.playing) {
        this._pause();
      } else {
        this._play();
      }
      this.playing = !this.playing;
    },

    simulate: function() {
      if (this.sim == null) {
        return;
      }

      console.log("Simulating", this.sim);
      this.$emit("sim-start");
      this.graphHistoricData = [];

      const simulation = JSON.parse(JSON.stringify(this.sim.simulation));
      if (this.isMultiple) {
        if (this.sim.simulation.iterate.intervals === 0) {
          return;
        }
      } else {
        delete simulation.iterate;
      }
      this._simulate(simulation, this.sim.model.id)
        .then(() => this.dataFetchingDone())
        .catch(err => this.handleError(err));
    },
    _simulate: function(simulation, modelId) {
      const controller = new AbortController();
      const signal = controller.signal;
      this.abortSignal = controller;

      const req = fetch(`/simulate/${modelId}`, {
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json"
        },
        method: "POST",
        body: JSON.stringify(simulation),
        signal
      });

      return req
        .then(resp => {
          if (resp.status >= 400 && resp.status < 600) {
            throw resp;
          }
          return resp.json();
        })
        .then(response => {
          if (response.type === "multiple") {
            response.frames.forEach((d, i) => {
              const graphData = makeGraphData(d);
              graphData._iterVal = response.param.values[i];
              this.graphHistoricData.push(graphData);
            });
          } else {
            const graphData = makeGraphData(response.frame);
            graphData._iterVal = 0;
            this.graphHistoricData.push(graphData);
          }
        });
    },

    /** Precisely rounds number based on the number of significant decimal places */
    _preciseRound: function(number, presicion = 7) {
      return (
        Math.round((number + Number.EPSILON) * Math.pow(10, presicion)) /
        Math.pow(10, presicion)
      );
    },
    _getIndexAsString: function(i) {
      return `${this.graphHistoricData[i]._iterVal || i}`;
    },
    dataFetchingDone: function() {
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
              frame: { duration: 800, redraw: true }
            }
          ]
        });
      }

      const slider = [
        {
          pad: { l: 130, t: 55 },
          steps: sliderSteps
        }
      ];

      var frames = [];
      for (let i = 0; i < this.graphHistoricData.length; i++) {
        frames.push({
          name: this._getIndexAsString(i),
          data: this.graphHistoricData[i]
        });
      }

      // Plotly mutates the initial data given, hence not allowing us to animate back
      // to the initial frame. We deeply copy the initial data object to avoid this issue.
      const data = JSON.parse(JSON.stringify(this.graphHistoricData[0]));

      Plotly.newPlot("plotDiv", {
        data: data,
        layout: { ...graphLayout, sliders: slider },
        frames: frames,
        config: plotConfig
      });
    }
  }
  // We use v-once on the #plotDiv element to avoid vue re-rendering it and disrupting plotly
};

/**
 * Returns current date formatted as YYYYmmdd-HHMMss
 */
function getCurrentDate() {
  function pad(string) {
    return (`0${string}`).slice(0, 2);
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
 * @param {*} isMultiple
 */
function generateCSV(plotData, isMultiple = false) {
  let csv = `sampletimes,${plotData[0].map((x) => x.name).join(',')}\n`;
  if (isMultiple) {
    csv = `iteration,${csv}`;
  }

  plotData.forEach(frame => {
    const sampleTimes = frame[0].x;
    const data = frame.map((x) => x.y);
    sampleTimes.forEach((sample, i) => {
      let row = `${sample},${data.map((x) => x[i]).join(',')}\n`;
      if (isMultiple) {
        row =`${frame._iterVal},${row}`;
      }
      csv += row;
    });
  });
  const CSVBlob = new Blob([csv], { type: "text/csv" });
  downloadLink(window.URL.createObjectURL(CSVBlob));
}

const plotConfig = {
  displaylogo: false,
  modeBarButtons: [
    [
      "toImage",
      "zoom2d",
      "zoomIn2d",
      "zoomOut2d",
      "autoScale2d",
      "hoverClosestCartesian",
      "hoverCompareCartesian"
    ]
  ],
  modeBarButtonsToRemove: ["pan2d", "resetScale2d", "sendDataToCloud"]
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
      name: data.index[i]
    });
  }

  return graphData;
}
</script>
