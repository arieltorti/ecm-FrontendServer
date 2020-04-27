Vue.component("simulation", {
  props: ["sim", "simCancel", "simPlay", "simState"],
  data: function () {
    return {
      SIM_STATE: SIM_STATE,
      graphHistoricData: [],
      stats: {
        totalSteps: null,
        currentStep: null,
      },

      simSpeed: 600,
      eventsRegistered: false,
      abortSignal: null, // Stores the signal to abort the current request
      playing: false,
      recording: false,
    };
  },
  created: function () {
    this.videoCreationService = videoCreationService;
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
    simPlay: function (play) {
      if (play) {
        this._play();
        this.$emit("sim-play");
      }
    },
  },
  methods: {
    handleError: function (err) {
      if (err.ABORT_ERR && err.code === err.ABORT_ERR) {
        console.debug("Request aborted");
      } else {
        this.$emit("sim-error", err);
        console.error(err);
      }
    },

    handleAnimEvent: function (ev) {
      if (ev === "done") {
        this.$refs.videoControls.stop();
      }
    },

    createVideo() {
      this.simSpeed = 3000;

      this._goToFirstFrame().then(() => {
        // NOTE: This will emit an `sim-anim-done` event, we may want to avoid it.
        this.recording = true;
        this._play();
        this.$refs.videoControls.record(this.$refs.plotDivRef);
      });
    },

    videoDone() {
      this.recording = false;
      this.simSpeed = 600;
    },

    stop: function () {},

    _goToFirstFrame: function () {
      return Plotly.animate("plotDiv", [this._getIndexAsString(0)], {
        mode: "immediate",
        transition: { duration: 0 },
        frame: { duration: 0, redraw: true },
      });
    },

    _play: function () {
      this.playing = true;
      Plotly.animate("plotDiv", null, {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: this.simSpeed },
        frame: { duration: this.simSpeed + 200, redraw: false },
      }).then(() => (this.playing = false));
    },
    _pause: function () {
      this.playing = false;
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
    },

    simulate: function () {
      if (this.sim == null) {
        return;
      }

      console.log("Simulating", this.sim);
      this.$emit("sim-start");

      this.graphHistoricData = [];

      if (this.sim.intervalConfig.iteratingVariable != null) {
        if (this.sim.intervalConfig.step === 0) {
          return;
        }

        // If we selected an interating variable send as many request as needed chaining them
        // to avoid overloading the server.
        let promiseChain = Promise.resolve();

        this.stats.totalSteps = Math.floor(
          1 +
            Math.floor(
              (this.sim.intervalConfig.to - this.sim.intervalConfig.from) /
                this.sim.intervalConfig.step +
                EPSILON
            )
        );
        this.stats.currentStep = 0;

        for (
          let from = this.sim.intervalConfig.from;
          from <= this.sim.intervalConfig.to;
          from = this._preciseRound(from + this.sim.intervalConfig.step)
        ) {
          promiseChain = promiseChain.then(() => {
            this.stats.currentStep += 1;
            return this._simulate(
              this.sim.config,
              _replaceModelVariableValue(
                this.sim.model,
                this.sim.intervalConfig.iteratingVariable,
                from
              ),
              from
            );
          });
        }

        promiseChain
          .then(() => this.dataFetchingDone())
          .catch((err) => this.handleError(err));
      } else {
        this.stats.totalSteps = this.stats.currentStep = 1;
        this._simulate(this.sim.config, this.sim.model)
          .then(() => this.dataFetchingDone())
          .catch((err) => this.handleError(err));
      }
    },
    _simulate: function (config, model, iterVarValue) {
      const formData = new FormData();

      formData.append("config", config);
      formData.append("model", model);

      const controller = new AbortController();
      const signal = controller.signal;
      this.abortSignal = controller;

      const req = fetch("/api/compute", {
        method: "POST",
        body: formData,
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
          const graphData = makeGraphData(data);
          graphData._iterVal = iterVarValue;
          this.graphHistoricData.push(graphData);
        });
    },

    /** Precisely rounds number based on the number of significant decimal places */
    _preciseRound: function (number, presicion = 7) {
      return (
        Math.round((number + Number.EPSILON) * Math.pow(10, presicion)) /
        Math.pow(10, presicion)
      );
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
              transition: { duration: this.simSpeed, easing: "linear" },
              frame: { duration: this.simSpeed + 200, redraw: true },
            },
          ],
        });
      }

      const slider = [
        {
          pad: { l: 130, t: 55 },
          steps: sliderSteps,
          gripbgcolor: "red",
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

      if (!this.eventsRegistered) {
        this.eventsRegistered = true;
        const plotDiv = document.getElementById("plotDiv");
        plotDiv.on("plotly_animating", () => this.$emit("sim-anim-start"));
        plotDiv.on("plotly_animationinterrupted", () => {
          this.handleAnimEvent("interrupted");
          this.$emit("sim-anim-stop");
        });
        plotDiv.on("plotly_animated", () => {
          this.handleAnimEvent("done");
          this.$emit("sim-anim-done");
        });
      }
    },
  },
  // We use v-once on the #plotDiv element to avoid vue re-rendering it and disrupting plotly
  template: `<div style="position: relative">
    <div class="progress" v-if="simState === SIM_STATE.INPROGRESS">
        Simulating {{ stats.currentStep }} / {{ stats.totalSteps }}
    </div>
    <div v-if="simState === SIM_STATE.DONE && (sim && sim.intervalConfig.iteratingVariable)">
      <button @click="createVideo">Record Video</button>
      <video-record-controls ref="videoControls" @video-done="videoDone">
      </video-record-controls>
    </div>
    <div :class="{'event-cover': recording}">
      <div id="plotDiv" ref="plotDivRef" v-once></div>
    </div>
    <div v-if="simState === SIM_STATE.DONE && (sim && sim.intervalConfig.iteratingVariable)" id="plotAnimDiv">
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

function downloadLink(href, extension="csv") {
  const linkEl = document.createElement("a");
  linkEl.setAttribute("href", href);
  linkEl.setAttribute("download", `sim-${getCurrentDate()}.${extension}`);

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
