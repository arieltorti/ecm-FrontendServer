<template>
  <div>
    <form @submit.prevent="onSubmit">
      <div class="controls" :class="{ 'disabled-interaction': simulating }">
        <SimulationControls
          :modelVariables="modelVariables"
          :iterVar.sync="iterationConfig.iterVar"
          :from.sync="iterationConfig.from"
          :to.sync="iterationConfig.to"
          :step.sync="iterationConfig.step"
        />
      </div>
      <button :disabled="notChanged && simState < SIM_STATE.CANCELED">
        {{ formBtnText }}
      </button>
    </form>

    <VideoControls
      :record-when-done.sync="recordWhenDone"
      :sim-state="simState"
      :video-duration.sync="videoDuration"
    />
    <SimulationPreview
      :sim-state.sync="simState"
      :plotRef.sync="plotRef"
      :video-duration="videoDuration"
      :recordWhenDone="recordWhenDone"
    />
  </div>
</template>

<script lang="ts">
import { Emit, Watch, Component, Prop, Vue } from "vue-property-decorator";
import SimulationControls from "./SimulationControls.vue";
import SimulationPreview from "./SimulationPreview.vue";
import VideoControls from "./VideoControls.vue";

import { calculateTotalSteps } from "../utils/graph-data";

import {
  SimulationConfig,
  SimulationService,
  SimEventBus,
  IterationConfig
} from "../services/simulation-service";

export const SIM_STATE = {
  IDLE: 0,
  DONE: 1,
  ERROR: 2,
  CANCELED: 3,
  INPROGRESS: 4
};

@Component({
  components: {
    SimulationControls,
    SimulationPreview,
    VideoControls
  }
})
export default class Simulation extends Vue {
  @Prop() modelVariables!: string[];
  @Prop() model!: string;
  @Prop() config!: string;

  private SIM_STATE = SIM_STATE;
  private simulating = false;
  private notChanged = false;

  private formBtnText = "Simulate";
  private iterationConfig: IterationConfig = {
    from: 0,
    to: 1,
    step: 0.05,
    iterVar: null
  };

  private simulationService = SimulationService;
  private plotRef = null;
  private simState = SIM_STATE.IDLE;

  private recordWhenDone = false;
  private videoDuration = 1;

  @Watch("model")
  @Watch("config")
  @Watch("iterationConfig", { deep: true })
  onSimulationConfigChange() {
    this.notChanged = false;
  }

  onSubmit() {
    if (this.simulating) {
      this.simulationService.cancel();
      return;
    }

    this.notChanged = true;
    const simulationConfig: SimulationConfig = {
      model: this.model,
      config: this.config,
      iterationConfig: this.iterationConfig
    };

    this.simulationService.simulate(simulationConfig);
    this.videoDuration =
      this.iterationConfig.iterVar == null
        ? 1
        : calculateTotalSteps(
            this.iterationConfig.to!,
            this.iterationConfig.from!,
            this.iterationConfig.step!
          );
  }

  simulatingOn(
    model: string,
    config: string,
    iterationConfig: IterationConfig
  ) {
    this.simulating = true;
    this.formBtnText = "Stop Simulation";
  }

  simulatingOff() {
    this.simulating = false;
    this.formBtnText = "Simulate";
  }

  created() {
    SimEventBus.$on("sim-processing", this.simulatingOn);
    SimEventBus.$on("sim-error", this.simulatingOff);
    SimEventBus.$on("sim-done", this.simulatingOff);
    SimEventBus.$on("sim-canceled", this.simulatingOff);
  }
}
</script>

<style lang="scss" scoped>
.controls {
  position: relative;
  display: inline-block;
}

form {
  button {
    display: block;
  }
}

.disabled-interaction:before {
  content: "";
  height: 100%;
  width: 100%;
  left: 0;
  top: 0;
  opacity: 0.5;
  background-color: #fff;
  position: absolute;
}
</style>
