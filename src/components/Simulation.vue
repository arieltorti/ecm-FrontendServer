<template>
  <div style="position: relative">
    <div class="progress" v-if="simState === SIM_STATE.INPROGRESS">
      Simulating
    </div>
    <div class="errorMsg" v-if="simState === SIM_STATE.FAILED">
      Error: {{ errMsg }}
    </div>
    <div v-bind:class="{ hidden: isNotDone }">
      <button id="downloadCSV" @click="downloadCSV">Download CSV</button>
      <GroupControls
        :model="sim.model"
        @changeGroupVisibility="changeGroupVisibility"
      />
      <div id="imageDiv">
        <div id="plotDiv" ref="plotlyInstance" v-once></div>
        <div id="simulationInfo" v-katex:display="simulationInfo"></div>
      </div>
    </div>
    <div
      v-if="simState === SIM_STATE.DONE && isMultiple"
      id="plotAnimDiv"
      class="data-html2canvas-ignore"
    >
      <button @click="handleAnimClick">{{ playing ? "| |" : "▶" }}</button>
    </div>
  </div>
</template>
<script>
import GroupControls from "./GroupControls.vue";
import { SIM_STATE, graphLayout } from "../constants";
import {
  getImageButton,
  extractSimulationInfo,
} from "../plotlyExtras/toImageButton";
import html2canvas from "html2canvas";

import { preciseRound } from "../utils";

import * as Plotly from "plotly.js";

export default {
  components: { GroupControls },
  props: ["sim", "simCancel", "simState"],
  data: function() {
    return {
      SIM_STATE: SIM_STATE,
      graphHistoricData: [],
      stats: {
        totalSteps: null,
        currentStep: null,
      },
      errMsg: "",
      abortSignal: null, // Stores the signal to abort the current request
      playing: false,
      simulationInfo: "",
    };
  },
  mounted: function() {
    this.plotConfig = plotConfig(this.saveToImage);
  },
  computed: {
    isMultiple: function() {
      return this.sim && this.sim.simulation.iterate.key != null;
    },
    isNotDone: function() {
      return this.simState !== SIM_STATE.DONE;
    },
  },
  watch: {
    sim: function(_sim) {
      if (_sim != null) {
        this.simulate();
      }
    },
    simCancel: function(stop) {
      if (stop) {
        this.abortSignal.abort();
        this.$emit("sim-cancel");
      }
    },
  },
  methods: {
    downloadCSV: function() {
      generateCSV(this.graphHistoricData, this.isMultiple);
    },
    handleError: function(err) {
      if (err.ABORT_ERR && err.code === err.ABORT_ERR) {
        this.$emit("sim-cancel");
      } else {
        err.json().then((e) => {
          this.errMsg = e.error;
        });
        this.$emit("sim-error");
      }
    },

    stop: function() {},

    saveToImage: function() {
      this.simulationInfo = extractSimulationInfo(
        this.sim,
        this.$refs.plotlyInstance
      );
      const imageDiv = document.getElementById("imageDiv");
      const simulationInfo = document.getElementById("simulationInfo");

      this.$nextTick(() => {
        html2canvas(imageDiv, {
          scrollX: -window.scrollX,
          scrollY: -window.scrollY,
          height: imageDiv.offsetHeight + simulationInfo.offsetHeight,
          onclone: (document) => {
            const simulationInfo = document.getElementById("simulationInfo");
            simulationInfo.style.position = "initial";
            simulationInfo.style.display = "block";

            const sliderContainer = document.getElementsByClassName(
              "slider-container"
            );
            if (sliderContainer.length !== 0) {
              const sliderHeight = sliderContainer[0].getBoundingClientRect()
                .height;
              sliderContainer[0].style.display = "none";

              simulationInfo.style.marginTop = `-${sliderHeight}px`;
            }
          },
        }).then((canvas) => {
          const imgString = canvas.toDataURL("image/png", 1);
          this.simulationInfo = "";
          downloadLink(imgString, "png");
        });
      });
    },

    _play: function() {
      Plotly.animate("plotDiv", null, {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: 300 },
        frame: { duration: 500, redraw: false },
      }).then(() => (this.playing = false));
    },
    _pause: function() {
      Plotly.animate("plotDiv", [null], {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: 0 },
        frame: { duration: 0, redraw: false },
      });
    },

    changeGroupVisibility(idx, visible) {
      const group = this.sim.model.groups[idx];
      if (group != null) {
        group.visible = visible;
      }
      this.updateGraphLayout();
    },

    removeHiddenGroups(data) {
      const hiddenVariables = [];
      this.sim.model.groups.map((group) => {
        if (!group.visible) {
          for (const compartment of group.compartments) {
            hiddenVariables.push(compartment.name);
          }

          for (const param of group.params) {
            hiddenVariables.push(param.name);
          }
        }
      });

      const filteredData = [];
      for (let frameIdx = 0; frameIdx < data.length; frameIdx++) {
        filteredData.push([]);
        for (const variable of data[frameIdx]) {
          if (hiddenVariables.indexOf(variable._originalName) == -1) {
            filteredData[frameIdx].push(variable);
          }
        }
      }
      return filteredData;
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

      this.$emit("sim-start");
      this.graphHistoricData = [];
      this.simulationInfo = "";

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
        .catch((err) => this.handleError(err));
    },
    _simulate: function(simulation, modelId) {
      const controller = new AbortController();
      const signal = controller.signal;
      this.abortSignal = controller;

      const req = fetch(`/simulate/${modelId}`, {
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify(simulation),
        signal,
      });

      return req
        .then((resp) => {
          if (resp.status >= 400 && resp.status < 600) {
            throw resp;
          }
          return resp.json();
        })
        .then((response) => {
          if (response.type === "multiple") {
            response.frames.forEach((d, i) => {
              const graphData = this.makeGraphData(d);
              graphData._iterVal = preciseRound(response.param.values[i], 2);
              this.graphHistoricData.push(graphData);
            });
          } else {
            const graphData = this.makeGraphData(response.frame);

            graphData._iterVal = 0;
            this.graphHistoricData.push(graphData);
          }
        });
    },
    /**
     * Extract graph data from JSON request output
     * @param {*} data
     */
    makeGraphData(data) {
      data._originalIndex = data.index.slice();
      this.sim.model.compartments.forEach(function(c) {
        const idx = data.index.findIndex((e) => e == c.name);
        if (idx >= 0) data.index[idx] = `$${c.nameLatex}$`;
      });
      this.sim.model.observables.forEach(function(c) {
        const idx = data.index.findIndex((e) => e == c.name);
        if (idx >= 0) data.index[idx] = `$${c.nameLatex}$`;
      });

      const xAxis = data.columns;
      const graphData = [];

      for (let i = 0; i < data.data.length; i++) {
        graphData.push({
          x: xAxis,
          y: data.data[i],
          name: data.index[i],
          hoverinfo: "x+y",
          _originalName: data._originalIndex[i],
        });
      }

      return graphData;
    },
    _getIndexAsString: function(i) {
      return `${this.graphHistoricData[i]._iterVal || i}`;
    },
    dataFetchingDone: function(drawingFn = "newPlot", initialFrame = 0) {
      /**
       * We have a ton of boilerplate here just to configure the slider and animations
       * as we have to rebuild them all everytime the data changes. In the future we could
       * migrate to using addFrames and resize/relayout instead.
       */

      this.$emit("sim-done");

      const filteredData = this.removeHiddenGroups(this.graphHistoricData);

      // Configure the number and style of the slider steps
      var sliderSteps = [];
      for (let i = 0; i < filteredData.length; i++) {
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
          active: initialFrame,
          pad: { l: 130, t: 55 },
          steps: sliderSteps,
        },
      ];

      var frames = [];
      for (let i = 0; i < filteredData.length; i++) {
        frames.push({
          name: this._getIndexAsString(i),
          data: filteredData[i],
        });
      }

      // Plotly mutates the initial data given, hence not allowing us to animate back
      // to the initial frame. We deeply copy the initial data object to avoid this issue.
      const data = JSON.parse(JSON.stringify(filteredData[initialFrame]));

      Plotly[drawingFn]("plotDiv", {
        data: data,
        layout: {
          ...graphLayout,
          sliders: slider,
        },
        frames: frames,
        config: this.plotConfig,
      });
    },

    updateGraphLayout() {
      const slidersArray = this.$refs.plotlyInstance.layout.sliders;
      const slider = slidersArray[0];
      const initialFrame = slider.active || 0;

      this.dataFetchingDone("react", initialFrame);
    },
  },
};

/**
 * Returns current date formatted as YYYYmmdd-HHMMss
 */
function getCurrentDate() {
  function pad(string) {
    return `0${string}`.slice(0, 2);
  }

  const now = new Date();
  const month = pad(now.getMonth() + 1);
  const day = pad(now.getDate());
  const hours = pad(now.getHours());
  const minutes = pad(now.getMinutes());
  const seconds = pad(now.getSeconds());
  return `${now.getUTCFullYear()}${month}${day}-${hours}${minutes}${seconds}`;
}

function downloadLink(href, type = "csv") {
  const linkEl = document.createElement("a");
  linkEl.setAttribute("href", href);
  linkEl.setAttribute("download", `sim-${getCurrentDate()}.${type}`);

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
  let csv = `sampletimes,${plotData[0].map((x) => x.name).join(",")}\n`;
  if (isMultiple) {
    csv = `iteration,${csv}`;
  }

  plotData.forEach((frame) => {
    const sampleTimes = frame[0].x;
    const data = frame.map((x) => x.y);
    sampleTimes.forEach((sample, i) => {
      let row = `${sample},${data.map((x) => x[i]).join(",")}\n`;
      if (isMultiple) {
        row = `${frame._iterVal},${row}`;
      }
      csv += row;
    });
  });
  const CSVBlob = new Blob([csv], { type: "text/csv" });
  downloadLink(window.URL.createObjectURL(CSVBlob));
}

function plotConfig(toImageButton) {
  return {
    displaylogo: false,
    modeBarButtons: [
      [
        getImageButton(toImageButton),
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
}
</script>

<style lang="sass" scoped>

#imageDiv
  position: relative
  #simulationInfo
    position: absolute
    left: -10000px
    top: -10000px
</style>
