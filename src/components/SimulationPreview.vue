<template>
  <div>
    <span v-if="state === SIM_STATE.INPROGRESS">Status: Simulating {{ currentStep }}/{{ totalSteps }}</span>
    <pre class="errorMsg" v-if="error">{{ error }}</pre>

    <div class="plotContainer">
      <VideoPreview v-if="canAnimate && state > SIM_STATE.IDLE" :video-duration="videoDuration" />

      <div v-once id="plotDiv"></div>

      <div id="plotAnimDiv" v-if="canAnimate && state > SIM_STATE.IDLE">
        <button @click="animate">{{ playing ? "| |" : "▶" }}</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, PropSync, Vue } from "vue-property-decorator";
import { SIM_STATE } from "../components/Simulation.vue";
import VideoPreview from "../components/VideoPreview.vue";

import { SimEventBus, IterationConfig } from "../services/simulation-service";
import { PlotData, calculateTotalSteps, GraphData } from "../utils/graph-data";
import { generateCSV } from "../utils/file-download";
import Plotly from "plotly.js-dist";

const graphLayout = {
  yaxis: { fixedrange: true }, // Dont allow rectangle zooming
  xaxis: {
    title: "Days",
  },
};

const exportAsCSVBtn = {
  name: "Export as CSV",
  icon: Plotly.Icons.disk,
  click: function(gd) {
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

@Component({
  components: {
    VideoPreview,
  },
})
export default class SimulationPreview extends Vue {
  @Prop() videoDuration!: number;
  @Prop() recordWhenDone: boolean;
  @PropSync("simState") state!: number;

  private error: string | null = null;
  private SIM_STATE = SIM_STATE; // For template use

  private totalSteps = 1;
  private currentStep = 0;
  private canAnimate = false;

  private playing = false;
  private eventsRegistered = false;

  private currentGraphData: PlotData[] = []; // Stored so that we can move to the first frame when needed.

  created() {
    SimEventBus.$on("sim-update", this.simulationUpdate);
    SimEventBus.$on("sim-processing", this.handleProcessing);
    SimEventBus.$on("sim-error", this.handleError);
    SimEventBus.$on("sim-done", this.handleDone);
    SimEventBus.$on("sim-canceled", this.handleCanceled);

    SimEventBus.$on("sim-anim-play", this._play);
    SimEventBus.$on("sim-anim-pause", this._pause);
  }

  _getIndexAsString(i: number, graphHistoricData: PlotData[]) {
    return "" + graphHistoricData[i].metadata?.iterationValue || i;
  }

  handleProcessing(model: string, config: string, iterationConfig: IterationConfig) {
    this.error = null;
    this.state = SIM_STATE.INPROGRESS;

    this.totalSteps =
      iterationConfig.iterVar == null
        ? 1
        : calculateTotalSteps(iterationConfig.to!, iterationConfig.from!, iterationConfig.step!);
    this.currentStep = 0;
  }

  handleError(error: any) {
    if (error.status === 500) {
      this.error = "A server error ocurred while running the simulation";
    } else if (error.status === 400) {
      error.text().then((msg) => {
        if (msg && msg.indexOf("The given key was not present in the dictionary.") !== -1) {
          // Most probably we encountered a variable that's not defined
          let errorMsg = "There is an error on the model definition";

          const variable = msg.match(/'\w+'/); // Naive regex to match possible undefined variable
          errorMsg += `\nCould it be that ${variable[0]} is not defined?`;
          this.error = errorMsg;
        } else {
          this.error = "There was an error while running the simulation";
        }
      });
    } else {
      this.error = `${error}`;
    }
    this.state = SIM_STATE.ERROR;
  }

  handleDone(graphHistoricData: PlotData[]) {
    /**
     * We have a ton of boilerplate here just to configure the slider and animations
     * as we have to rebuild them all everytime the data changes. In the future we could
     * migrate to using addFrames and resize/relayout instead.
     */
    this.currentGraphData = graphHistoricData;
    this.canAnimate = graphHistoricData.length > 1;

    // Configure the number and style of the slider steps
    const sliderSteps = [];
    for (let i = 0; i < graphHistoricData.length; i++) {
      sliderSteps.push({
        method: "animate",
        label: this._getIndexAsString(i, graphHistoricData), // Convert to string, plotly behaves weird
        // when using floats.
        args: [
          [this._getIndexAsString(i, graphHistoricData)],
          {
            mode: "immediate",
            transition: { duration: 300 },
            frame: { duration: 300, redraw: false },
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

    const frames = [];
    for (let i = 0; i < graphHistoricData.length; i++) {
      frames.push({
        name: this._getIndexAsString(i, graphHistoricData),
        data: graphHistoricData[i],
      });
    }

    // Plotly mutates the initial data given, hence not allowing us to animate back
    // to the initial frame. We deeply copy the initial data object to avoid this issue.
    const data = JSON.parse(JSON.stringify(graphHistoricData[0]));

    Plotly.newPlot("plotDiv", {
      data: data,
      layout: { ...graphLayout, sliders: slider },
      frames: frames,
      config: plotConfig,
    }).then(() => {
      this.$emit("sim-done");
      this.state = SIM_STATE.DONE;

      if (!this.eventsRegistered) {
        this.eventsRegistered = true;
        const plotDiv = document.getElementById("plotDiv");
        plotDiv.on("plotly_animationinterrupted", () => {
          this.playing = false;
        });
        plotDiv.on("plotly_animated", () => {
          this.playing = false;
        });
      }
    });
  }

  handleCanceled() {
    this.state = SIM_STATE.CANCELED;
  }

  simulationUpdate() {
    this.currentStep += 1;
  }

  _goToFirstFrame() {
    return Plotly.animate("plotDiv", [this._getIndexAsString(0, this.currentGraphData)], {
      mode: "immediate",
      transition: { duration: 0 },
      frame: { duration: 0, redraw: false },
    });
  }

  _play(redraw = false, fromStart = false) {
    const doPlay = () => {
      this.playing = true;
      Plotly.animate("plotDiv", null, {
        mode: "immediate",
        fromcurrent: true,
        transition: { duration: 300 },
        frame: { duration: 500, redraw: redraw }, // NOTE: There seems to be a bug on plotly that doesn't move the slides when redraw is false.
      }).then(() => (this.playing = false));
    };

    if (fromStart) {
      this._goToFirstFrame().then(doPlay.bind(this)());
    } else {
      doPlay();
    }
  }
  _pause() {
    this.playing = false;
    Plotly.animate("plotDiv", [null], {
      mode: "immediate",
      fromcurrent: true,
      transition: { duration: 0 },
      frame: { duration: 0, redraw: false },
    });
  }

  animate() {
    if (this.playing) {
      this._pause();
    } else {
      this._play();
    }
  }
}
</script>

<style lang="scss" scoped>
.errorMsg {
  color: red;
}

.plotContainer {
  position: relative;
}

#plotAnimDiv {
  /* This is a hack, TODO: look on plotly doc is there's a way to insert a DOM element as button for a better way to position this */
  position: absolute;
  bottom: 28px;
  left: 120px;

  button {
    padding: 0.6em 0.8em;
  }
}
</style>
